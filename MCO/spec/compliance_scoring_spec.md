# MCO Compliance Scoring Spec

MCO stands for **Message-Layer Compliance Oracle**.

This document represents the scoring and evaluation contract of MCO. Developers and AI workers must align the oracle implementation with these calculations.

## Goal

MCO evaluates transaction metadata to assign a **Compliance Risk Score** and determine whether the transaction can receive a signed attestation token.

The score measures:
> The risk level of regulatory non-compliance or sanctions breach associated with a given remittance or stablecoin message payload.

## Score Formula

The Compliance Risk Score ($S$) is calculated as:

```text
compliance_risk_score = 
  100 * (
    sanction_screening_factor * 0.40 +
    aml_limit_factor * 0.30 +
    country_risk_factor * 0.20 +
    data_completeness_factor * 0.10
  )
```

The final score is clamped to `[0, 100]`. 
- **Higher scores** represent higher risk of non-compliance (leading to `BLOCKED`).
- **Lower scores** represent low risk (leading to `APPROVED` attestation).

---

## Component Definitions

### 1. `sanction_screening_factor`

Captures direct hits or close name matches in Blocked lists (e.g. OFAC SDN equivalents).
- `1.0` if the debtor or creditor name is found on the blocked names list.
- `0.0` if no match is found.

### 2. `aml_limit_factor`

Evaluates transaction volume risk against KYC status.
- `0.0` if the transaction is under $10,000 USD.
- `0.2` if the transaction is over $10,000 USD but has `enhanced_kyc_verified` = `true`.
- `1.0` if the transaction is over $10,000 USD and lacks `enhanced_kyc_verified` (or it is `false`).

### 3. `country_risk_factor`

Assesses high-risk jurisdiction involvement.
- `1.0` if either debtor or creditor country is on the `blocked_countries` list.
- `0.3` if either country is on a high-risk FATF watch list (not blocked but monitored).
- `0.0` if both countries are low risk.

### 4. `data_completeness_factor`

Measures message structural validity.
- `0.0` if all mandatory ISO 20022 fields are fully populated.
- `0.5` if optional fields are missing but structural integrity is intact.
- `1.0` if major fields are missing (e.g., account IDs, missing amount/currency).

---

## Weights

| Component | Weight | Reason |
|---|---:|---|
| `sanction_screening_factor` | 0.40 | Sanction hits carry strict legal liability and must cause an immediate block |
| `aml_limit_factor` | 0.30 | High volume transactions require enhanced due diligence to prevent money laundering |
| `country_risk_factor` | 0.20 | Geographical location is a key vector for capital flight and tax evasion |
| `data_completeness_factor` | 0.10 | Complete telemetry is required to prove compliance audits |

Weights sum to `1.0`.

---

## Compliance Tiers

| Compliance Risk Score | Action Tier | Status | Attestation Issued? |
|---|---|---|---|
| `>= 70` | `CRITICAL_VIOLATION` | `BLOCKED` | No (Rejected) |
| `>= 40` | `ENHANCED_REVIEW` | `BLOCKED` | No (Rejected unless KYC provided) |
| `[15, 40)` | `MONITORED_OK` | `APPROVED` | Yes (Standard Attestation) |
| `< 15` | `LOW_RISK` | `APPROVED` | Yes (Attestation Issued) |

- **CRITICAL_VIOLATION**: Any direct sanction hit immediately forces this tier.
- **ENHANCED_REVIEW**: High volume or high country risk triggers this. Requires enhanced KYC parameters to downgrade the score to `MONITORED_OK`.

---

## Worked Example

### Example A: Sanction Hit
A transaction of $1,000 USD involving `ALEXEY SMIRNOV`.
- `sanction_screening_factor` = 1.0 (Weight 0.40 -> 0.40)
- `aml_limit_factor` = 0.0 (Weight 0.30 -> 0.00)
- `country_risk_factor` = 0.3 (Weight 0.20 -> 0.06)
- `data_completeness_factor` = 0.0 (Weight 0.10 -> 0.00)
- **Score** = `100 * (0.40 + 0.06) = 46`. However, direct sanction hit forces a override to `CRITICAL_VIOLATION (Score 100)` -> `BLOCKED`.

### Example B: Large Amount with Enhanced KYC
A transaction of $15,000 USD between KR and US, with `enhanced_kyc_verified` = `true`.
- `sanction_screening_factor` = 0.0
- `aml_limit_factor` = 0.2 (Large amount, but KYC present)
- `country_risk_factor` = 0.0 (KR and US are low risk)
- `data_completeness_factor` = 0.0
- **Score** = `100 * (0.2 * 0.30) = 6` -> `LOW_RISK` -> `APPROVED`.
