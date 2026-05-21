# MCO Engineering Guide

MCO stands for **Message-Layer Compliance Oracle**.

This guide is for an engineer or AI worker seeing the project for the first time. It explains the project architecture, how to run the oracle and validation tests, and the core rules governing the compliance attestation flow.

## 1. What You Are Building

MCO is an automated compliance verification and attestation engine for cross-border transactions (ISO 20022 and stablecoin metadata).

It answers this question:
> Given a payment message transaction payload, does it violate multi-jurisdictional sanctions, exceed AML limits, or lack adequate enhanced KYC verification? If clean, how does the oracle issue a cryptographic proof of compliance?

The current MVP contains:
- input: JSON transaction payloads (ISO 20022 or Stablecoin Tx format)
- computation: Multi-factor risk scoring (0-100), rule matching, sanctions screening, and SHA-256 simulated attestation signature generation
- output: JSON attestation certificate (with risk score, tier, and mock signature) or BLOCK audit trail
- dependencies: Requires Python 3.8+ and PyYAML (defined in requirements.txt)

## 2. End-to-End Flow

```text
JSON Message Payload
  -> tools/mco_oracle.py
  -> parse schema (ISO 20022 or Stablecoin)
  -> verify sanctions lists (names & jurisdictions)
  -> evaluate compliance rules (AML threshold)
  -> generate SHA-256 hash of payload
  -> sign cryptographically
  -> write JSON attestation token or BLOCK report
```

The CLI run command is:

```powershell
python tools/mco_oracle.py `
  spec/compliance_rules.yaml `
  examples/sample_message.json `
  examples/attestation_output.json
```

Full integration test verification is:

```powershell
python verification/verify.py
```

Bypass test run:

```powershell
python verification/verify.py --bypass
```

## 3. Core Terms

| Term | Meaning |
|---|---|
| Attestation | A cryptographic certificate issued by the oracle verifying compliance compatibility. |
| Compliance Score | A risk metric (0 to 100) calculated based on 4-factor scoring specifications. |
| Sanctions List | Blocked lists of names (SDN list equivalents) and high-risk country codes. |
| Rule Match | An automated check that catches AML threshold limits or missing KYC flags. |
| ISO 20022 | The financial messaging standard format used for remittance data payloads. |
| Enhanced KYC | Mandatory additional checks flagged for large transactions (>= $10,000 USD). |

## 4. Rule Configurations

The rules live in `spec/compliance_rules.yaml`. The parameters define block criteria:
- `blocked_names`: List of sanctioned individuals or entities.
- `blocked_countries`: ISO 2-letter codes of prohibited jurisdictions.
- `threshold_usd`: Maximum allowed amount before requiring `enhanced_kyc_verified` extension.

## 5. Required Fields

The data contract is in `spec/message_schema.yaml`. Both ISO 20022 and Stablecoin JSON payloads must match their respective schema attributes. Key fields:
- `amount` and `currency` (or `token_symbol`): Used for USD threshold conversion.
- `debtor` / `creditor` (or metadata sender/receiver name): Screened against the blocked names list.
- `enhanced_kyc_verified`: Required if the transaction amount is >= 10,000 USD.

## 6. Scoring and Logic Changes

If you need to change rules or scoring policies:
1. Update `spec/compliance_rules.yaml` or `spec/compliance_scoring_spec.md`.
2. Update the logic inside `tools/mco_oracle.py`.
3. Run `python verification/verify.py` to confirm no regressions.
4. Document the changes in `.pgf/status-MCO.json`.

## 7. Common Mistakes

- Sending raw strings instead of structural debtor/creditor objects.
- Omitting timezone offsets in `creation_date_time` (UTC / `Z` format preferred).
- Assuming `MCO` verifies legal liability. It issues an *exploratory compliance attestation*, not a final government clearance certificate.
- Forgetting to provide the `enhanced_kyc_verified` flag for high-value transactions, which triggers automatic block status.

## 8. Acceptance Checklist

Before committing/handing off:
- `python verification/verify.py` passes successfully on local test cases.
- Valid JSON schema is maintained.
- Cryptographic transaction_hash is deterministic; signature is timestamp-bound.
- Status updates are reflected in `.pgf/status-MCO.json`.
