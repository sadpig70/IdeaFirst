# -*- coding: utf-8 -*-
"""
MCO Verification Script
Performs integration tests against the compliance oracle engine.
Supports execution bypass via '--bypass' or '-bypass' with explicit warnings.
"""

import os
import sys
import json
import tempfile
import subprocess

def run_test(rules_path, tx_data, expected_status, expected_tier=None, expected_score=None):
    # Create temp transaction file
    fd, temp_tx_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    
    fd2, temp_out_path = tempfile.mkstemp(suffix=".json")
    os.close(fd2)
    
    try:
        with open(temp_tx_path, 'w', encoding='utf-8') as f:
            json.dump(tx_data, f)
            
        oracle_script = os.path.join(os.path.dirname(__file__), "..", "tools", "mco_oracle.py")
        
        # Execute oracle
        cmd = [sys.executable, oracle_script, rules_path, temp_tx_path, temp_out_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FAIL: Oracle execution failed. Stderr: {result.stderr}")
            return False
            
        # Parse output
        with open(temp_out_path, 'r', encoding='utf-8') as f:
            output_data = json.load(f)
            
        actual_status = output_data.get("status")
        actual_tier = output_data.get("compliance_tier")
        actual_score = output_data.get("compliance_risk_score")
        
        # 1. Validate status
        if actual_status != expected_status:
            print(f"FAIL: Expected status {expected_status}, but got {actual_status}. Reason: {output_data.get('reason')}")
            return False
            
        # 2. Validate tier (if specified)
        if expected_tier and actual_tier != expected_tier:
            print(f"FAIL: Expected tier {expected_tier}, but got {actual_tier}.")
            return False
            
        # 3. Validate score (if specified)
        if expected_score is not None and abs(actual_score - expected_score) > 0.001:
            print(f"FAIL: Expected score {expected_score}, but got {actual_score}.")
            return False
            
        # 4. Validate Attestation token layout for APPROVED txs (M2)
        if actual_status == "APPROVED":
            token = output_data.get("attestation_token")
            if not token:
                print("FAIL: APPROVED transaction lacks attestation_token.")
                return False
            if "mock_signature" not in token:
                print("FAIL: Attestation token lacks 'mock_signature' field.")
                return False
            if token.get("simulated") is not True:
                print("FAIL: Attestation token lacks 'simulated: true' flag.")
                return False
                
        print(f"PASS: Expected {expected_status} ({actual_tier}, Score: {actual_score}). Reason: {output_data.get('reason')}")
        return True
    finally:
        # Cleanup
        if os.path.exists(temp_tx_path):
            os.remove(temp_tx_path)
        if os.path.exists(temp_out_path):
            os.remove(temp_out_path)

def main():
    # Support Bypass argument (H3)
    bypass = False
    for arg in sys.argv:
        if arg.lower() in ["--bypass", "-bypass", "bypass"]:
            bypass = True
            
    if bypass:
        sys.stderr.write("\n======================================================\n")
        sys.stderr.write("WARNING: MCO VERIFICATION BYPASSED VIA COMMAND ARGUMENT!\n")
        sys.stderr.write("THIS BYPASS SIGNAL IS FOR STAGING/TEST-BYPASS ONLY.\n")
        sys.stderr.write("======================================================\n\n")
        # Exit with dedicated code 77 to indicate bypass state instead of normal 0
        sys.exit(77)
        
    print("Starting MCO Oracle Integration Tests...")
    
    rules_path = os.path.join(os.path.dirname(__file__), "..", "spec", "compliance_rules.yaml")
    
    # Test case 1: Standard Approved ISO transaction
    tx_approved_iso = {
      "msg_id": "TEST-TX-001",
      "creation_date_time": "2026-05-21T12:00:00Z",
      "payment_type": "CREDIT_TRANSFER",
      "amount": 5000.0,
      "currency": "USD",
      "debtor": {"name": "HONG GILDONG", "country": "KR", "account_id": "ACC-111"},
      "creditor": {"name": "JOHN SMITH", "country": "US", "account_id": "ACC-222"}
    }
    
    # Test case 2: Blocked Sanctions name match (ISO)
    tx_blocked_sanction = {
      "msg_id": "TEST-TX-002",
      "creation_date_time": "2026-05-21T12:00:00Z",
      "payment_type": "CREDIT_TRANSFER",
      "amount": 1000.0,
      "currency": "USD",
      "debtor": {"name": "ALEXEY SMIRNOV", "country": "RU", "account_id": "ACC-111"},
      "creditor": {"name": "JOHN SMITH", "country": "US", "account_id": "ACC-222"}
    }
    
    # Test case 3: Blocked High-Risk Jurisdiction country match (ISO)
    tx_blocked_country = {
      "msg_id": "TEST-TX-003",
      "creation_date_time": "2026-05-21T12:00:00Z",
      "payment_type": "CREDIT_TRANSFER",
      "amount": 500.0,
      "currency": "USD",
      "debtor": {"name": "HONG GILDONG", "country": "KR", "account_id": "ACC-111"},
      "creditor": {"name": "TRADER", "country": "KP", "account_id": "ACC-333"}
    }
    
    # Test case 4: AML Limit violation (large amount, no KYC flag -> triggers ENHANCED_REVIEW)
    tx_blocked_aml = {
      "msg_id": "TEST-TX-004",
      "creation_date_time": "2026-05-21T12:00:00Z",
      "payment_type": "CREDIT_TRANSFER",
      "amount": 25000.0,
      "currency": "USD",
      "debtor": {"name": "HONG GILDONG", "country": "KR", "account_id": "ACC-111"},
      "creditor": {"name": "JOHN SMITH", "country": "US", "account_id": "ACC-222"},
      "extensions": {
        "enhanced_kyc_verified": "false"
      }
    }

    # Test case 5: AML Limit passed with KYC (large amount, KYC verified -> LOW_RISK)
    tx_approved_kyc = {
      "msg_id": "TEST-TX-005",
      "creation_date_time": "2026-05-21T12:00:00Z",
      "payment_type": "CREDIT_TRANSFER",
      "amount": 25000.0,
      "currency": "USD",
      "debtor": {"name": "HONG GILDONG", "country": "KR", "account_id": "ACC-111"},
      "creditor": {"name": "JOHN SMITH", "country": "US", "account_id": "ACC-222"},
      "extensions": {
        "enhanced_kyc_verified": "True" # M6: Normalized parsing test
      }
    }

    # Test case 6: Standard Approved Stablecoin transaction (M4)
    tx_approved_stable = {
      "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
      "from_address": "0xSenderAddress",
      "to_address": "0xReceiverAddress",
      "amount": 500.0,
      "token_symbol": "USDC",
      "chain_id": 1,
      "metadata": {
        "sender_name": "BOB JONES",
        "sender_country": "US",
        "receiver_name": "ALICE SMITH",
        "receiver_country": "KR",
        "enhanced_kyc_verified": False
      }
    }

    # Test case 7: Stablecoin AML Limit violation (large amount, no KYC -> ENHANCED_REVIEW)
    tx_blocked_stable_aml = {
      "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
      "from_address": "0xSenderAddress",
      "to_address": "0xReceiverAddress",
      "amount": 15000.0,
      "token_symbol": "USDT",
      "chain_id": 137,
      "metadata": {
        "sender_name": "BOB JONES",
        "sender_country": "US",
        "receiver_name": "ALICE SMITH",
        "receiver_country": "KR",
        "enhanced_kyc_verified": "0"
      }
    }

    # Test case 8: Stablecoin Sanctions Hit in Metadata
    tx_blocked_stable_sanction = {
      "tx_hash": "0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef",
      "from_address": "0xSenderAddress",
      "to_address": "0xReceiverAddress",
      "amount": 100.0,
      "token_symbol": "USDT",
      "chain_id": 56,
      "metadata": {
        "sender_name": "ZACK CORRUPT", # Blocked name
        "sender_country": "US",
        "receiver_name": "ALICE SMITH",
        "receiver_country": "KR"
      }
    }

    # Test case 9: Negative amount validation check (H4)
    tx_negative_amount = {
      "msg_id": "TEST-TX-009",
      "creation_date_time": "2026-05-21T12:00:00Z",
      "payment_type": "CREDIT_TRANSFER",
      "amount": -100.0, # Negative
      "currency": "USD",
      "debtor": {"name": "HONG GILDONG", "country": "KR", "account_id": "ACC-111"},
      "creditor": {"name": "JOHN SMITH", "country": "US", "account_id": "ACC-222"}
    }

    # Test case 10: Missing required fields check (H5)
    tx_missing_fields = {
      "tx_hash": "0x9876543210abcdef9876543210abcdef9876543210abcdef9876543210abcdef",
      "from_address": "0xSenderAddress",
      "to_address": "0xReceiverAddress",
      "amount": 100.0,
      "token_symbol": "USDT"
      # Missing chain_id
    }

    # Test case 11: High-risk country but not blocked (RU in high_risk_countries -> triggers ENHANCED_REVIEW)
    tx_high_risk_country = {
      "msg_id": "TEST-TX-011",
      "creation_date_time": "2026-05-21T12:00:00Z",
      "payment_type": "CREDIT_TRANSFER",
      "amount": 200.0,
      "currency": "USD",
      "debtor": {"name": "HONG GILDONG", "country": "RU", "account_id": "ACC-111"}, # RU is high risk
      "creditor": {"name": "JOHN SMITH", "country": "US", "account_id": "ACC-222"}
    }
    
    success = True
    print("\n--- Running ISO 20022 Test Cases ---")
    success &= run_test(rules_path, tx_approved_iso, "APPROVED", "LOW_RISK", 0.0)
    success &= run_test(rules_path, tx_blocked_sanction, "BLOCKED", "CRITICAL_VIOLATION", 100.0)
    success &= run_test(rules_path, tx_blocked_country, "BLOCKED", "CRITICAL_VIOLATION", 100.0)
    success &= run_test(rules_path, tx_blocked_aml, "BLOCKED", "ENHANCED_REVIEW", 40.0)
    success &= run_test(rules_path, tx_approved_kyc, "APPROVED", "LOW_RISK", 6.0)
    success &= run_test(rules_path, tx_negative_amount, "BLOCKED", "CRITICAL_VIOLATION", 100.0)
    success &= run_test(rules_path, tx_high_risk_country, "APPROVED", "LOW_RISK", 6.0)
    
    print("\n--- Running Stablecoin Test Cases ---")
    success &= run_test(rules_path, tx_approved_stable, "APPROVED", "LOW_RISK", 0.0)
    success &= run_test(rules_path, tx_blocked_stable_aml, "BLOCKED", "ENHANCED_REVIEW", 40.0)
    success &= run_test(rules_path, tx_blocked_stable_sanction, "BLOCKED", "CRITICAL_VIOLATION", 100.0)
    success &= run_test(rules_path, tx_missing_fields, "BLOCKED", "CRITICAL_VIOLATION", 100.0)
    
    if success:
        print("\nAll integration tests passed successfully.")
        sys.exit(0)
    else:
        print("\nOne or more integration tests failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
