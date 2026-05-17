# SA-IdeaFirst v0.1 — Standalone Technical Document

## SA-ICX / SA-EVX / SA-AOX standalone execution contract

> Compatibility: IdeaFirst v1.3.1 / CIX v1.5.1 capability handling.
> This English document defines the standalone execution contract of
> `skills/sa-icx`, `skills/sa-evx`, `skills/sa-aox`. It follows the canonical
> engine document's structure but explicitly **separates the boundary** from
> production CIX/EVX/AOX. The Korean `skills/**/SKILL.md` remain canonical.

## 1. Why standalone exists

Production IdeaFirst mandates `cross_model` surprise validation in CIX v1.5.1.
In a single-model environment (e.g. Codex only), that cross-model baseline call
is impossible, so a production round is correctly marked **`(blocked)`**.

SA-IdeaFirst does **not** discard that blocked state as a failure, and does
**not** bypass it with a fallback heuristic. Instead it closes — within the
range possible in a single-model environment — the idea-generation and
evaluation loop, end to end.

### 1.1 Production vs standalone

- **Production IdeaFirst**: cross-model surprise validation is mandatory; a
  single-model environment ⇒ round `(blocked)` + `HANDOFF.md`.
- **Standalone IdeaFirst**: closes the exploratory loop in the single-model
  environment and emits only into `.sa-*/` paths.

### 1.2 The role of SA-IdeaFirst

SA-IdeaFirst does **not** lift the production blocked state. Its final result is
**not** production-certified output, and it must never disguise a `.aox`
production run as `completed`. It is an honest standalone exploratory result,
not a replacement for production IdeaFirst.

## 2. The three standalone skills

| Skill | Standalone role |
|---|---|
| **SA-ICX** | standalone candidate generation/filtering/scoring; can resume from already-preserved CIX phase-1–4 raw seeds (`--from-cix-raw`), preserving `lens_application` / `source_round_chain` / `scores: null` |
| **SA-EVX** | standalone evaluation closing the loop without cross-model consensus |
| **SA-AOX** | Stand-Alone IdeaFirst Orchestrator eXplorer — receives SDX/TCX/IDX outputs, runs SA-ICX then SA-EVX sequentially, and produces a standalone final summary + a production-promotion package; it does not replace AOX production and writes only under `.sa-aox/` |

## 3. Output contract

- All standalone artifacts are written under `.sa-icx/` / `.sa-evx/` /
  `.sa-aox/` only — never under the production `.cix/` / `.evx/` / `.aox/`
  paths.
- Every standalone final summary is explicitly labelled: *"This is a standalone
  IdeaFirst result, not CIX/EVX/AOX production-certified output."*
- A standalone run may emit a **production-promotion package** so that, once a
  cross-model environment is available, the work can be promoted through the
  real production gates — without ever having faked them.

## 4. Boundary summary

SA-IdeaFirst is the honest closure of the loop under a capability constraint.
It preserves provenance, refuses to fake certification, and keeps the
production blocked state intact for later, legitimate promotion.
