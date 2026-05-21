# DESIGN-MCO

## PGF Mode

`design -> plan -> execute -> verify`

Durable PGF is used because MCO is a new product track designed to handle complex multi-jurisdictional compliance rules, stablecoin smart-contract attestations, and ISO 20022 message schema parsing.

## Gantree

```text
MCO // Message-Layer Compliance Oracle (status: concrete_mvp)
    ProductThesis // Real-time semantic compliance for ISO 20022 & Stablecoins (status: completed)
        AI_extract_winner_mechanism
        AI_translate_to_attestation_flow
        -> thesis

    ComplianceEngine // Rule evaluator and semantic matcher (status: completed)
        RuleParser
        SanctionDatabaseMock
        SemanticResolver
        AttestationGenerator
        -> evaluation_result

    DataContract // Message structure & rule schemas (status: completed)
        ISO20022MessageFormat
        StablecoinTxFormat
        AttestationTokenFormat
        -> schemas

    Prototype // Executable oracle engine (status: completed)
        OracleEngine
        RuleMatcher
        CryptoSigner
        -> runnable_mvp

    VerificationSystem // Auto-verification tests (status: completed)
        PositiveTestCase
        NegativeTestCase
        SanctionMatchCase
        BypassVerify
        -> MCO_R_V_C
```

## PPR

```text
def AI_evaluate_compliance(transaction_message, compliance_rules, sanctions_db):
    parsed_msg = AI_parse_message(transaction_message)
    sender = parsed_msg.sender
    receiver = parsed_msg.receiver
    amount = parsed_msg.amount
    currency = parsed_msg.currency

    # Check Sanctions List
    sender_sanctioned = AI_check_sanctions(sender, sanctions_db)
    receiver_sanctioned = AI_check_sanctions(receiver, sanctions_db)

    if sender_sanctioned or receiver_sanctioned:
        return compliance_result(
            status="BLOCKED",
            reason="Sanctioned party detected in transaction path",
            attestation_token=null
        )

    # Check Custom Compliance Rules (e.g., AML limits, regional restrictions)
    for rule in compliance_rules:
        if rule.matches(parsed_msg):
            rule_eval = AI_evaluate_rule_semantics(rule, parsed_msg)
            if rule_eval.status == "VIOLATION":
                return compliance_result(
                    status="BLOCKED",
                    reason=rule_eval.reason,
                    attestation_token=null
                )

    # Cryptographic Attestation Generation
    msg_hash = AI_compute_sha256(parsed_msg)
    signature = AI_sign_attestation_hash(msg_hash, oracle_private_key)

    return compliance_result(
        status="APPROVED",
        reason="All compliance checks passed",
        attestation_token=attestation_token(
            oracle_id="MCO-ORACLE-01",
            message_hash=msg_hash,
            signature=signature,
            timestamp=AI_get_timestamp()
        )
    )
```

## Acceptance Criteria

- `MCO/` exists as a self-contained product track.
- ISO 20022 and Stablecoin schema formats are clearly specified.
- Compliance rule definitions are customizable.
- Prototype performs compliance evaluation and generates cryptographic mock attestations.
- Verification script executes sample messages and yields correct block/approve states.
