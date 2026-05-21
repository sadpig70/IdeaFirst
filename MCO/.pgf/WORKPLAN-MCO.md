# WORKPLAN-MCO

## Policy

- Keep MCO separate from `.sa-*`, `.aox`, `.cix`, and `.evx` production paths.
- Use PGF artifacts for durable design state.
- Prefer executable prototypes over broad concept notes.
- Treat all scores as exploratory until independently validated.

## Nodes

| ID | Task | Status | Output |
|---|---|---|---|
| G1 | Extract selected idea into MCO product thesis | completed | `README.md` |
| G2 | Define schema configurations for ISO 20022 and stablecoins | completed | `spec/message_schema.yaml` |
| G3 | Define compliance rules YAML structure | completed | `spec/compliance_rules.yaml` |
| G4 | Build executable prototype oracle | completed | `tools/mco_oracle.py` |
| G5 | Add sample message and attestation output | completed | `examples/sample_message.json`, `examples/attestation_output.json` |
| G6 | Add auto-verification test suite | completed | `verification/verify.py` |
| G7 | Expand sanctions database size and rule semantics | pending | - |

## Next Executable Node

`G7`: Expand DB and rule parsing once the core prototype passes validation.
