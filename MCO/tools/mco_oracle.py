# -*- coding: utf-8 -*-
"""
Message-Layer Compliance Oracle (MCO) - Prototype Engine
Evaluating ISO 20022 and Stablecoin messages against semantic compliance rules.
"""

import os
import sys
import json
import hashlib
import yaml
from datetime import datetime, timezone

class ComplianceOracle:
    def __init__(self, rules_path, schema_path=None):
        self.rules_path = rules_path
        if not schema_path:
            # Locate schema in the same directory as rules by default
            self.schema_path = os.path.join(os.path.dirname(rules_path), "message_schema.yaml")
        else:
            self.schema_path = schema_path
        
        # Load rules and schemas using PyYAML (C1)
        with open(self.rules_path, 'r', encoding='utf-8') as f:
            self.rules_data = yaml.safe_load(f)
            
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            self.schema_data = yaml.safe_load(f)
            
        sanctions = self.rules_data.get('sanctions_list', {})
        
        # M1: Normalize names and countries using casefold and strip
        self.blocked_names = [n.strip().casefold() for n in sanctions.get('blocked_names', [])]
        self.blocked_countries = [c.strip().casefold() for c in sanctions.get('blocked_countries', [])]
        self.high_risk_countries = [c.strip().casefold() for c in sanctions.get('high_risk_countries', [])]
        
        # H1: Extract threshold limit dynamically from RULE-AML-01 in compliance_rules
        self.threshold_usd = 10000.0
        for rule in self.rules_data.get('compliance_rules', []):
            if rule.get('id') == 'RULE-AML-01':
                self.threshold_usd = float(rule.get('threshold_usd', 10000.0))
                
        self.oracle_id = "MCO-ORACLE-01"
        self.private_key_sig = "mco_secret_key_attestation_signature_v1"

    def check_sanctions(self, entity_name, country_code):
        # M1: Casefold screening for robust matching
        if entity_name:
            norm_name = entity_name.strip().casefold()
            if norm_name in self.blocked_names:
                return True, f"Entity name '{entity_name}' is sanctioned"
        if country_code:
            norm_country = country_code.strip().casefold()
            if norm_country in self.blocked_countries:
                return True, f"Country '{country_code}' is sanctioned/high-risk"
        return False, ""

    def evaluate_compliance(self, tx_data):
        # M3: Enhanced ISO/Stablecoin transaction type detection
        has_payment_type = "payment_type" in tx_data
        has_tx_hash = "tx_hash" in tx_data
        has_iso_entities = "debtor" in tx_data and "creditor" in tx_data
        has_stablecoin_addresses = "from_address" in tx_data and "to_address" in tx_data

        is_iso = has_payment_type or (has_iso_entities and not has_tx_hash)
        is_stablecoin = has_tx_hash or (has_stablecoin_addresses and not has_iso_entities)

        if not is_iso and not is_stablecoin:
            return self._build_result(
                status="BLOCKED",
                reason="Unable to determine transaction message format (neither ISO 20022 nor Stablecoin)",
                tx_data=tx_data,
                score=100.0,
                tier="CRITICAL_VIOLATION",
                factors={"sanction": 0.0, "aml": 0.0, "country": 0.0, "completeness": 1.0}
            )

        # H5: Required field validation based on schema definitions
        required_fields = []
        if is_iso:
            required_fields = self.schema_data.get("required_fields_iso20022", [])
        else:
            required_fields = self.schema_data.get("required_fields_stablecoin", [])

        missing_fields = [f for f in required_fields if f not in tx_data]
        
        # 1. Parse fields based on transaction type
        if is_iso:
            sender_name = tx_data.get("debtor", {}).get("name", "") if isinstance(tx_data.get("debtor"), dict) else ""
            sender_country = tx_data.get("debtor", {}).get("country", "") if isinstance(tx_data.get("debtor"), dict) else ""
            receiver_name = tx_data.get("creditor", {}).get("name", "") if isinstance(tx_data.get("creditor"), dict) else ""
            receiver_country = tx_data.get("creditor", {}).get("country", "") if isinstance(tx_data.get("creditor"), dict) else ""
            
            # H4: Safe float parse, and initialize metadata kyc
            try:
                amount = float(tx_data.get("amount", 0))
            except (ValueError, TypeError):
                amount = 0.0
            currency = tx_data.get("currency", "USD")
            
            # M6: Normalized KYC verified check
            kyc_val = tx_data.get("extensions", {}).get("enhanced_kyc_verified", False) if isinstance(tx_data.get("extensions"), dict) else False
            has_enhanced_kyc = str(kyc_val).strip().lower() in ("true", "1", "yes")
        else:
            metadata = tx_data.get("metadata", {}) if isinstance(tx_data.get("metadata"), dict) else {}
            sender_name = metadata.get("sender_name", "")
            sender_country = metadata.get("sender_country", "")
            receiver_name = metadata.get("receiver_name", "")
            receiver_country = metadata.get("receiver_country", "")
            
            try:
                amount = float(tx_data.get("amount", 0))
            except (ValueError, TypeError):
                amount = 0.0
            currency = tx_data.get("token_symbol", "USDT")
            
            # M6: Normalized KYC verified check
            kyc_val = metadata.get("enhanced_kyc_verified", False)
            has_enhanced_kyc = str(kyc_val).strip().lower() in ("true", "1", "yes")

        # Factor evaluations
        factors = {
            "sanction": 0.0,
            "aml": 0.0,
            "country": 0.0,
            "completeness": 0.0
        }

        # 2. Complete schema check & positive amount check (H4, H5)
        schema_violation = False
        schema_reasons = []
        
        if missing_fields:
            schema_violation = True
            schema_reasons.append(f"Missing required fields: {', '.join(missing_fields)}")
            factors["completeness"] = 1.0
            
        if amount <= 0:
            schema_violation = True
            schema_reasons.append(f"Transaction amount must be positive. Received: {amount}")
            factors["completeness"] = 1.0

        if schema_violation:
            return self._build_result(
                status="BLOCKED",
                reason=f"Schema Validation Failure: {'; '.join(schema_reasons)}",
                tx_data=tx_data,
                score=100.0,
                tier="CRITICAL_VIOLATION",
                factors=factors
            )

        # 3. Sanctions Screening Factor
        sender_sanctioned, reason_s = self.check_sanctions(sender_name, sender_country)
        receiver_sanctioned, reason_r = self.check_sanctions(receiver_name, receiver_country)
        
        if sender_sanctioned or receiver_sanctioned:
            factors["sanction"] = 1.0
            block_reason = reason_s if sender_sanctioned else reason_r
            # Force critical override score = 100.0
            return self._build_result(
                status="BLOCKED",
                reason=block_reason,
                tx_data=tx_data,
                score=100.0,
                tier="CRITICAL_VIOLATION",
                factors=factors
            )

        # 4. AML Limit Screening Factor (using dynamic threshold_usd H1)
        if amount >= self.threshold_usd:
            if has_enhanced_kyc:
                factors["aml"] = 0.2
            else:
                factors["aml"] = 1.0
        else:
            factors["aml"] = 0.0

        # 5. Country Risk Factor (using high_risk_countries L2)
        sender_c_norm = sender_country.strip().casefold()
        receiver_c_norm = receiver_country.strip().casefold()
        
        if sender_c_norm in self.blocked_countries or receiver_c_norm in self.blocked_countries:
            factors["country"] = 1.0
        elif sender_c_norm in self.high_risk_countries or receiver_c_norm in self.high_risk_countries:
            factors["country"] = 0.3
        else:
            factors["country"] = 0.0

        # C2: Compliance Scoring Formula Calculation
        raw_score = 100 * (
            factors["sanction"] * 0.40 +
            factors["aml"] * 0.30 +
            factors["country"] * 0.20 +
            factors["completeness"] * 0.10
        )
        
        # Spec 88 line override: High volume lacking KYC or high country risk triggers ENHANCED_REVIEW (Score >= 40)
        if factors["aml"] == 1.0 or factors["country"] == 1.0:
            raw_score = max(raw_score, 40.0)

        # Clamping to [0, 100]
        compliance_risk_score = float(max(0.0, min(100.0, raw_score)))

        # Tier mapping and status determination
        # >= 70: CRITICAL_VIOLATION
        # >= 40: ENHANCED_REVIEW
        # [15, 40): MONITORED_OK
        # < 15: LOW_RISK
        if compliance_risk_score >= 70.0:
            status = "BLOCKED"
            tier = "CRITICAL_VIOLATION"
            reason = f"Critical risk score ({compliance_risk_score}) exceeding critical safety threshold"
        elif compliance_risk_score >= 40.0:
            status = "BLOCKED"
            tier = "ENHANCED_REVIEW"
            reason = f"Enhanced review required due to high AML/Country risk (Score: {compliance_risk_score})"
        elif compliance_risk_score >= 15.0:
            status = "APPROVED"
            tier = "MONITORED_OK"
            reason = f"Risk score ({compliance_risk_score}) is within acceptable monitored threshold"
        else:
            status = "APPROVED"
            tier = "LOW_RISK"
            reason = "All compliance checks passed successfully"

        return self._build_result(status, reason, tx_data, compliance_risk_score, tier, factors)

    def _build_result(self, status, reason, tx_data, score, tier, factors):
        # M5: Fix datetime deprecation
        timestamp = datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z"
        
        result = {
            "status": status,
            "reason": reason,
            "timestamp": timestamp,
            "compliance_risk_score": score,
            "compliance_tier": tier,
            "factors_breakdown": factors,
            "attestation_token": None
        }

        if status == "APPROVED":
            # For APPROVED, generate deterministic SHA256 signature hash of tx
            tx_serialized = json.dumps(tx_data, sort_keys=True)
            tx_hash = hashlib.sha256(tx_serialized.encode('utf-8')).hexdigest()
            
            # Simulating signature by hashing tx_hash with oracle secret key
            signature_payload = f"{self.private_key_sig}:{tx_hash}:{timestamp}"
            signature = hashlib.sha256(signature_payload.encode('utf-8')).hexdigest()
            
            # M2: Standardize attestation token structure with mock/simulated properties
            result["attestation_token"] = {
                "oracle_id": self.oracle_id,
                "transaction_hash": tx_hash,
                "mock_signature": f"mco_sig_0x{signature[:32]}",
                "certificate_type": "ISO20022_COMPLIANCE_COMPATIBILITY_v1",
                "simulated": True
            }
            
        return result

def main():
    if len(sys.argv) < 4:
        print("Usage: python mco_oracle.py <rules.yaml> <transaction.json> <output.json>")
        sys.exit(1)
        
    rules_file = sys.argv[1]
    tx_file = sys.argv[2]
    out_file = sys.argv[3]
    
    if not os.path.exists(rules_file) or not os.path.exists(tx_file):
        print("Error: Rules or Transaction file not found.")
        sys.exit(1)
        
    with open(tx_file, 'r', encoding='utf-8') as f:
        tx_data = json.load(f)
        
    oracle = ComplianceOracle(rules_file)
    result = oracle.evaluate_compliance(tx_data)
    
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        
    print(f"Compliance check completed. Status: {result['status']}. Output saved to {out_file}")

if __name__ == '__main__':
    main()
