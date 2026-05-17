# IdeaFirst v1.3 — Engine Technical Document

## Integrated technical specification of SDX / TCX / IDX / CIX / EVX / AOX

> **Structurally blocks the three major biases of AI-based system-idea
> generation, and autonomously runs the complete pipeline from discovery to
> evaluation.**

> This English document is a faithful **explanatory** rendering. The exhaustive
> canonical specification is the Korean engine document (preserved internally)
> together with the Korean `skills/**/SKILL.md`. Section numbers mirror the
> canonical document so cross-references (e.g. "§10 — KPIs") stay valid.

| Item | Value |
|---|---|
| System version | v1.3 (2026-05-13) |
| Component skills | SDX v1.3 / TCX v1.5 / IDX v1.4 / CIX v1.4 / **EVX v1.0** / AOX v1.2 |
| Author | Jung Wook Yang (양정욱) — sadpig70@gmail.com |
| Affiliation | AR Gducation / SeAAI · ORCID 0009-0004-3646-9684 · github.com/sadpig70 |
| Depends on | PG (PPR/Gantree notation), PGF (framework) — PGF discovery personas P1–P8 shared by all 6 skills |

---

## 0. Executive summary

**What it solves.** In an LLM-based idea-generation system, running 8 AIs in
parallel still makes the **results converge into ~3 clusters**, and the
remedy historically stayed a *manual-invocation workflow* that **cannot run
autonomously**.

**How it solves it.** Decompose the failure causes stage by stage, add an
autonomous-execution layer, and separate the evaluation layer:

```
failure cause                →  responding skill
  Input homogenization       →  SDX  (Source Discovery)
  Information asymmetry       →  TCX  (Trend Collection & Analysis)
  Insight shallowness         →  IDX  (Insight Distillation)
  Combination triviality      →  CIX  (Creative Innovation)
  Evaluation self-reference   →  EVX  (Evaluation eXplorer)   ⭐ new in v1.3
  Manual orchestration        →  AOX  (IdeaFirst Orchestrator)
```

**Outcome (same 8-AI resource budget):** diversity index 0.2 → ~0.7, execution
manual → autonomous, evaluation ~2 min → ~30 s (deterministic).

---

## 1. Problem definition

### 1.1 Observed failure pattern

Empirically running the workflow (8 AIs over 21 domains of fresh news):

```
8 AI × 3 system proposals = 24
→ semantically converge into 3 clusters
   Cluster 1: PQC × bio × regulation
   Cluster 2: LEO × power grid × data centers
   Cluster 3: humanoids × regulatory fragmentation × insurance
```

The 8-AI parallelism introduced *for* diversity **fails to create diversity**.

### 1.2 Cause diagnosis (6 stages)

- **Input homogenization** — every AI is exposed to the same Anglo-American tech
  media, forced into the same 24-hour window, with shared LLM training data
  prioritizing the same keywords. → SDX.
- **Information asymmetry** — even with channels discovered, there is no standard
  for *how* to collect; 21-domain × 4-criterion analysis runs differently each
  time; cross-domain synthesis is missing. → TCX (v1.5 `canonical_mapping`
  guarantees persona cross-check 14/14).
- **Insight shallowness** — only a quantitative instruction ("10 insights"), no
  depth criterion. → IDX (v1.4 `layer_pure_assertion` + hybrid layers).
- **Combination triviality** — LLMs naturally select only obvious variations
  within the training distribution; naive score-summing makes a layer dead. →
  CIX (v1.4 per-layer z-score + `layer_min_top_k=4` + persona-bias filter-only).
- **Evaluation self-reference** *(new in v1.3)* — reusing CIX's own 6-axis score
  makes evaluation a self-assessment; an idea popular with one cognitive-style
  cohort can win; the 5S/3R/3X writeup is ad-hoc and irreproducible. → EVX
  (CIX 6-axis → PGF 4-axis remap, vote → cog-style-breadth → mean tiebreak,
  5 quality gates).
- **Manual orchestration** — each stage is invoked by hand, no failure recovery,
  outputs never feed input refresh. → AOX (6-skill standard contract).

### 1.3 Resolution principles

| Principle | Application |
|---|---|
| Bias-blocking at the mechanism level | structural enforcement, not "be more diverse" |
| One independent skill per stage | no skill solves two problems |
| Guaranteed autonomous execution | the master orchestrator calls every stage |
| Self-evolution | output monitoring auto-refreshes input |
| Reproducibility & verifiability | every artifact carries source, score, log |
| AI-native notation | PG (PPR/Gantree) |
| **★ cost ≪ value** (v1.3) | implementation cost converges to 0; all value is idea novelty; token/time are byproducts, not constraints; a costlier evaluation that yields a newer idea is correct |

**Implication.** The last principle re-orders the others: determinism is correct
only where the pursuit of novelty requires it. If a more expensive evaluation
(LLM-augmented qualitative, cross-model surprise validation) discriminates
novelty better, it becomes the new default. Every CIX v1.5 / EVX v1.1 / AOX v1.3
policy change derives from this principle.

---

## 2. System overview

### 2.1 Full pipeline (v1.3)

```
[AOX] /aox full
  Stage 0  Init                 run_id = …
  Stage 1  SDX (conditional)    bootstrap if no catalog; refresh on homogenization;
                                else reuse → .sdx/catalog/index.yaml + channels/*.yaml (80)
  Stage 2  TCX                  /tcx full → .tcx/latest/{news,industry_trend,manifest}
                                v1.5 canonical_mapping (14 domains × 2 personas, 14/14)
  Stage 3  IDX                  /idx distill → .idx/latest/insight_layered_traced.yaml
                                (20 insights, 5/5/5/5; v1.4 audit_mode + layer purity)
  Stage 4  CIX                  /cix innovate → .cix/latest/idea_pool.yaml (24, layer-balanced)
                                v1.4 per-layer z-score + layer_min_top_k=4 + bias filter-only
  Stage 5  EVX ⭐ (was inline)   /evx evaluate → .evx/latest/{stage5,stage6,final_idea,manifest}
                                STEP5 8 personas × top3 · STEP6 cross-AI consensus
                                (vote→cog_style_breadth→mean) · STEP7 5S/3R/3X
  Stage 6  Wrap-up              measure homogenization (next-round trigger) + summary.md
```

vs v1.2: Stage 5 moved from AOX-inline to a first-class **EVX** skill call,
completing the 6-skill (SDX→TCX→IDX→CIX→EVX→AOX) standard-contract chain.

### 2.2 The six skills

| Skill | Role | Input | Output |
|---|---|---|---|
| **AOX** v1.2 | master orchestrator | mode/args | full run + `summary.md` |
| **SDX** v1.3 | discover/maintain orthogonal channels | (self-discovers) | `.sdx/catalog/index.yaml` + `channels/*.yaml` (80) |
| **TCX** v1.5 | collect & per-domain analysis | `.sdx/catalog/index.yaml` | `.tcx/latest/news.md` + `industry_trend.md` |
| **IDX** v1.4 | deep insight distillation | `.tcx/latest/industry_trend.md` | `.idx/latest/insight_layered_traced.yaml` (20) |
| **CIX** v1.4 | innovative seed-idea generation | `.idx/latest/insight_layered_traced.yaml` | `.cix/latest/idea_pool.yaml` (24) |
| **EVX** v1.0 ⭐ | evaluation & final selection | `.cix/latest/idea_pool.yaml` | `.evx/latest/final_idea.md` (final 1 + 5S/3R/3X) |

### 2.3 Responsibility boundaries

- **AOX** — autonomy only (no domain knowledge): call order (6-skill standard
  contract), artifact versioning (`.{skill}/latest` fixed paths), failure
  recovery/retry, homogenization detection + next-round trigger. All domain
  analysis/insight/evaluation is delegated.
- **SDX** — input diversity only: channel-quality scoring (8 axes); does *not*
  analyze channel content (TCX's job).
- **TCX** — collection + first-pass analysis only; does not analyze the channel
  catalog itself (SDX's job).
- **IDX / CIX / EVX** — depth / non-trivial transformation / consensus
  evaluation respectively, each strictly scoped.

---

## 10. Quality gates & KPIs

### 10.1 Quality gates (excerpt)

- **CIX**: obvious-rejection rate 40–60% (threshold=1, v1.4 strict); mean
  total_score ≥ 7.5; Generativity·Compounding mean ≥ 7.0; surprise validation
  ≥ 2 methods; `layer_min_top_k` ≥ 4 per layer (L6/L7/L9/L10); persona variance
  ≤ 4 (filter-direction-only).
- **EVX** (5 gates, new in v1.3): g1 input top_k = 24 (matches CIX); g2 all 8
  personas top-3 voted; g3 `final_1.votes` ≥ 2 (single-vote round invalid);
  g4 5 strengths + 3 risks + 3 expansions; g5 axis_mapping (4 formulas) cited
  in manifest.

### 10.2 System-level KPIs (v1.3 redefinition)

Per principle §1.3 ("cost ≪ value"), v1.2's cost KPIs (autonomy rate, mean
duration) are demoted to *constraints*, and **five innovation KPIs** become
canonical.

| KPI | Target | Measurement |
|---|---|---|
| **Novelty** | baseline-LLM prediction-failure ≥ 0.7 | fraction of other models (GPT/Gemini/…) failing to predict an idea similar to the winner from the same insight (1 − similarity) |
| **Diversity** | mean pairwise embedding distance ≥ 0.6 | mean cosine distance over all pairs of the round's 24 ideas |
| **Sustained innovation** | cross-round winner cosine ≤ 0.5 | winner-embedding similarity between rounds N and N−1, 5 rounds running |
| **Surprise pass** | ≥ 6 of 8 personas fail to predict | CIX cross-model surprise validation (fallback abolished from v1.5) |
| **Post-hoc** | ≥ 1 follow-up per winner within 12 months | external tracking — follow-on idea/product/research/paper/patent |

**Constraints (not KPIs — recorded only):** round duration and autonomy rate
are measured but have *no target value*. If a costlier evaluation or manual
intervention discriminates novelty better, that is the correct choice.

**Enforcement (AOX Stage 6):** all 5 KPIs written to `summary.md`; if any KPI
misses target, the next round auto-triggers an SDX refresh.

### 10.3 Measured comparison (v1.3)

- Manual baseline: 24 ideas → 3 clusters, diversity ~0.2, hours of manual stage
  switching.
- Engine v1.3 `/aox full`: 80 channels → 20 deep insights → 114 pass → 24
  selected (≥4 per layer) → consensus → final 1 + 5S/3R/3X; diversity ~0.7;
  ~15 min (Stage 5 deterministic, −2 min).
- EVX-20260513-001 actuals: Stage 5 duration 30 s (−75% vs inline), Stage 5 AI
  calls 0 (−100%), byte-identical reproducibility.

---

## 14. Conclusion

Engine v1.3 completes a **full 6-skill autonomous system** by adding **EVX
(evaluation separation)** on top of v1.2 (SDX/TCX/IDX/CIX/AOX), unifying the
**PGF discovery 8 personas cross-skill**, and applying **CIX v1.4 audit-driven**
policy reinforcement.

Core insights:

1. Diversity is a *mechanism*, not an intention (v1.1).
2. Autonomous execution is a *standard interface*, not an automation script (v1.2).
3. Self-evolution starts from output monitoring (v1.2).
4. Evaluation self-reference must also be blocked by mechanism (★ v1.3).
5. The audit → fix → validate loop evolves the policy itself (★ v1.3).

```
Final position v1.3
  AOX  master that flows every stage autonomously via the 6-skill contract
  SDX  information-channel engine that blocks input bias
  TCX  collection engine converting channels via persona cross-check analysis
  IDX  distillation engine lifting shallow insights into deep ones
  CIX  creation engine transforming trivial combinations into non-obvious systems
  EVX  evaluation engine reaching consensus on final-1 with a different scoring axis ⭐
  Together  deterministic, reproducible, 6-skill autonomous run from input to evaluation
```

v1.3 is an operational stage with one completed empirical run
(EVX-20260513-001); next is multi-round regression analysis.

---

*For exhaustive detail (every policy, schema, and PG/PPR definition), the Korean
`skills/**/SKILL.md` is canonical and authoritative.*
