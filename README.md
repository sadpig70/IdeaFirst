<p align="center">
  <img src="assets/banner.svg" alt="IdeaFirst — implementation cost ≪ idea value" width="100%">
</p>

<h1 align="center">IdeaFirst</h1>

<p align="center">
  <em>An autonomous idea engine where implementation cost ≪ idea value.<br>
  It structurally refuses mundane LLM output via a 6-skill cross-model adversarial pipeline.</em>
</p>

---

> **Scope & honesty note.** IdeaFirst is an *idea-generation methodology and engine*,
> not a guarantee that any particular generated idea is correct, novel, or valuable.
> Its design goal is to make mundane output *structurally hard to produce* and to keep
> every output **auditable** (source, score, and log attached). Outputs are provisional
> until independently validated. See the worked example below, whose own verdict is an
> honest, evidence-blocked provisional — *by design, not a bug*.

## What this is

Running 8 AIs in parallel over fresh news does **not** produce diverse system ideas —
empirically the 24 proposals collapse into ~3 semantic clusters. Parallelism alone does
not create diversity. IdeaFirst decomposes *why* mundane output happens into independent
failure causes, assigns one skill to each, and runs the whole thing autonomously from
discovery to evaluation.

```
failure cause              →  skill
  Input homogenization     →  SDX  (Source Discovery)
  Information asymmetry     →  TCX  (Trend Collection & Analysis)
  Insight shallowness       →  IDX  (Insight Distillation)
  Combination triviality    →  CIX  (Creative Innovation)
  Evaluation self-reference →  EVX  (Evaluation eXplorer)
  Manual orchestration      →  AOX  (IdeaFirst Orchestrator)
```

## The governing principle: cost ≪ value

In the AI era, implementation cost converges toward zero. Therefore all of a system's
value lives in **idea novelty**. Token spend and wall-clock time are *byproducts, not
KPIs* — if a more expensive evaluation produces a newer idea, the expensive evaluation
is the correct one. This single principle re-orders every other design rule (e.g.,
determinism is right only where novelty needs it).

## The pipeline

```
/aox full
  Stage 1  SDX   maintain ~80 orthogonal information channels        → .sdx/catalog/
  Stage 2  TCX   collect + analyze (8 personas, 14/14 cross-check)   → .tcx/latest/
  Stage 3  IDX   distill 20 deep insights (forced deep layers)       → .idx/latest/
  Stage 4  CIX   20 lenses → reject the obvious → 24 seed ideas       → .cix/latest/
  Stage 5  EVX   8 personas × top-3 → cross-AI consensus → final 1    → .evx/latest/
  Stage 6  wrap  measure homogenization → auto-trigger next round
```

| Skill | Role | Output |
|---|---|---|
| **AOX** | Master orchestrator (autonomy only, no domain knowledge) | full run + `summary.md` |
| **SDX** | Discover/maintain orthogonal input channels | 80-channel catalog |
| **TCX** | Collect & first-pass analyze signals | `news.md` + `industry_trend.md` |
| **IDX** | Lift shallow observations into deep insights | 20 layered insights |
| **CIX** | Transform trivial combinations into non-obvious systems | 24 seed ideas |
| **EVX** | Reach consensus on the final pick with a *different* scoring axis | final idea + 5 strengths / 3 risks / 3 expansions |

Standalone variants `sa-icx` / `sa-evx` / `sa-aox` close the loop in single-model
environments (e.g., Codex) without faking production certification. `pg` (PG notation)
and `pgf` (PGF framework) are the AI-native specification dependencies; the
PGF discovery personas P1–P8 are shared cross-skill.

## Innovation KPIs (the only real KPIs)

| KPI | Target |
|---|---|
| Novelty — baseline-LLM prediction failure | ≥ 0.7 |
| Diversity — pairwise embedding distance | ≥ 0.6 |
| Sustained innovation — cross-round winner similarity | ≤ 0.5 |
| Surprise pass — personas failing to predict | ≥ 6 of 8 |
| Post-hoc — follow-ups within 12 months per winner | ≥ 1 |

Round duration and autonomy rate are **recorded but have no target** — they are
constraints/byproducts, never goals.

## Worked example

[**sadpig70/BlindSpotMoat**](https://github.com/sadpig70/BlindSpotMoat) — a full
idea → engine → review → publish cycle produced with this method. Its verdict is
`phantom_moat`: empirically robust **by design**, in an honest *evidence-blocked
provisional* state. That honesty is the point of the methodology, not a defect.

## Lineage

IdeaFirst is the fully advanced, normalized successor of the original **A3IE**
("AI Infinite Idea Engine") seed. The original seed/basic-idea repository
[**sadpig70/A3IE**](https://github.com/sadpig70/A3IE) is preserved as-is; this
repository is the advanced engine and is independent of it.

## Repository layout

```
skills/      the framework (canonical spec; Korean is authoritative — see note)
docs/        English explanatory docs (architecture, onboarding, standalone)
assets/      banner
```

> **On language.** The executable framework under `skills/` is the *canonical
> instrument* and its authoritative form is Korean (`skills/**/SKILL.md`,
> PG/PPR notation). The English material in `docs/` is a faithful explanatory
> layer, not a replacement; per the project's integrity rule, the canonical
> instrument is not machine-translated. Original Korean technical documents are
> preserved internally.

## Quick start

```bash
git clone github.com/sadpig70/IdeaFirst
cd IdeaFirst
ln -s $(pwd)/skills ~/.claude/skills/
/aox dry-run        # print the execution plan, detect missing deps
pip install pyyaml  # EVX script dependency
/aox full           # run the full SDX→AOX pipeline
```

## License

Released under the [MIT License](LICENSE) — © 2025–2026 sadpig70 (Jung Wook Yang).

## Author

Jung Wook Yang (양정욱) 
GitHub [@sadpig70](https://github.com/sadpig70) · ORCID 0009-0004-3646-9684
