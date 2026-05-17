---
name: sa-aox
description: "SA-AOX (Stand-Alone IdeaFirst Orchestrator eXplorer) — Codex 단독 환경에서 SDX/TCX/IDX 산출물을 받아 SA-ICX와 SA-EVX를 순차 실행하고 standalone final summary와 production promotion package를 만드는 오케스트레이터. AOX production을 대체하지 않고 .aox production run을 completed로 위장하지 않으며 .sa-aox/에만 산출한다. Triggers: sa-aox, standalone aox, stand-alone aox, 단독 AOX, 독립 AOX, standalone full cycle, SA IdeaFirst"
user-invocable: true
argument-hint: "full|resume|dry-run|promote-package [--start-from=stage] [--run-id=...]"
version: "0.1"
author: "양정욱 (sadpig70@gmail.com)"
---

# SA-AOX (Stand-Alone IdeaFirst Orchestrator eXplorer) v0.1

SA-AOX는 cross-model capability가 없는 Codex 단독 환경에서 IdeaFirst exploratory loop를 끝까지 닫는 standalone 오케스트레이터다.

## Boundary

SA-AOX는 AOX production 결과가 아니다.

```yaml
result_class: "standalone_single_runtime"
cross_model_certified: false
production_aox_equivalent: false
may_write_aox_completed_summary: false
may_write_cix_latest: false
may_write_evx_latest: false
```

SA-AOX가 만드는 것은 최종 인증 결과가 아니라:
- standalone final idea
- standalone summary
- production promotion package
- CIX/EVX/AOX로 승격하기 위한 trace

## Pipeline

```text
SA_AOX_Full
    Stage0_Init
        create .sa-aox/{run_id}/status.json
        probe file_io and PGF personas
        record cross_model_capability but do not block standalone flow

    Stage1_UpstreamCheck
        verify .sdx/catalog/index.yaml
        verify .tcx/latest/
        verify .idx/latest/insight_layered_traced.yaml

    Stage2_SA_ICX
        invoke or execute SA-ICX forge
        output .sa-icx/rounds/{sa_icx_round_id}/candidate_pool.yaml

    Stage3_SA_EVX
        invoke or execute SA-EVX evaluate
        output .sa-evx/rounds/{sa_evx_round_id}/final_idea.md

    Stage4_WrapUp
        write .sa-aox/{run_id}/summary.md
        write .sa-aox/{run_id}/PROMOTE_TO_PRODUCTION.md
        update .sa-aox/index.yaml
```

## Inputs

```yaml
required:
  sdx_catalog_index: ".sdx/catalog/index.yaml"
  tcx_latest: ".tcx/latest/manifest.yaml"
  idx_latest: ".idx/latest/insight_layered_traced.yaml"
  personas: "skills/pgf/discovery/personas.json"

optional:
  existing_sa_icx_round: ".sa-icx/rounds/{round_id}"
  existing_sa_evx_round: ".sa-evx/rounds/{round_id}"
```

## Outputs

```yaml
output_root: ".sa-aox"
run_id_format: "SA-AOX-{YYYYMMDD}-{NNN}"
files:
  - status.json
  - summary.md
  - standalone_kpis.yaml
  - PROMOTE_TO_PRODUCTION.md
  - run_manifest.yaml
```

## Status Contract

```yaml
status:
  run_id: "SA-AOX-{YYYYMMDD}-{NNN}"
  mode: "full | resume | dry-run"
  result_class: "standalone_single_runtime"
  stages:
    0_init: "completed | failed"
    1_upstream_check: "completed | failed"
    2_sa_icx: "completed | failed | skipped_reused"
    3_sa_evx: "completed | failed | skipped_reused"
    4_wrapup: "completed | failed"
  sub_round_ids:
    sa_icx_round_id: "SA-ICX-{YYYYMMDD}-{NNN}"
    sa_evx_round_id: "SA-EVX-{YYYYMMDD}-{NNN}"
  production_boundary:
    cross_model_certified: false
    cix_promotion_required: true
    evx_production_required: true
    aox_production_wrapup_required: true
```

## Standalone KPIs

SA-AOX may record analogous exploratory metrics, but they must not be confused with AOX v1.3.1 production KPIs.

```yaml
standalone_kpis:
  candidate_diversity_proxy: number
  layer_balance: {L6_Gap, L7_Tension, L9_Counterfactual, L10_Generative}
  persona_vote_breadth: number
  consensus_vs_innovation_split: boolean
  production_certification_status: "not_certified"
```

Forbidden KPI language:
- `novelty baseline failure rate` unless cross-model CIX has run
- `surprise pass rate` unless cross-model CIX has run
- `AOX KPI passed`

## Summary Contract

`summary.md` must include:

```markdown
# SA-AOX Standalone Summary

This is a standalone IdeaFirst result, not CIX/EVX/AOX production-certified output.
Cross-model CIX v1.5.1 promotion is required before production use.

## Outputs
- SA-ICX candidate pool
- SA-EVX final idea
- SA-EVX dual winner block

## Boundary
- cross_model_certified: false
- may_use_for_exploration: true
- may_use_for_final_certification: false

## Production promotion
```

## Promotion Package

`PROMOTE_TO_PRODUCTION.md` must give the exact next production path:

```text
1. Run CIX v1.5.1 cross_model surprise_validation using SA-ICX candidates as evidence.
2. Emit completed .cix/latest only after cross_model validation.
3. Run EVX v1.1 production evaluate.
4. Run AOX v1.3.1 wrap-up and collect production 5 KPIs.
```

If CIX import from `.sa-icx` is not implemented, state manual handoff:

```text
Use .sa-icx/rounds/{id}/candidate_pool.yaml and raw_seed_ideas.yaml as candidate evidence.
Do not copy them into .cix/latest without CIX v1.5.1 validation.
```

## PGF Execution Rule

Use inline PGF for a single run. Create durable `.pgf/` workplans only when changing this skill, running a multi-turn standalone campaign, or handing off to another environment.
