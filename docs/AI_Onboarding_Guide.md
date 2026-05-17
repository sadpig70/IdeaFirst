# IdeaFirst — Onboarding Guide for AI Workers

> Compatibility: IdeaFirst v1.3 (CIX **v1.5.1** / EVX **v1.1** / AOX **v1.3.1**).
> This English guide is the **reading order + role framing**; it is not a
> replacement for the canonical spec. The authoritative specification is the
> Korean `skills/**/SKILL.md` (and the canonical engine document); read those
> for exhaustive policy and schema detail.

This page is designed so that another LLM (Claude / GPT / Gemini / Grok / Kimi /
DeepSeek / Qwen / Mistral …) can do meaningful work in the system after reading
*only this one page* for the first five minutes.

## 1. What IdeaFirst is (in one paragraph)

IdeaFirst is a 6-skill autonomous pipeline that *structurally* blocks mundane
LLM output and produces novel, innovative system ideas. Parallelizing 8 AIs does
not by itself create diversity; IdeaFirst instead decomposes the failure causes
and assigns one independent skill to each:
`SDX → TCX → IDX → CIX → EVX → AOX`. The governing principle is **cost ≪ value**:
implementation cost converges to 0, so all value is idea novelty; token/time are
byproducts, never KPIs.

## 2. Read in this order

1. This guide (the page you are on).
2. The orchestrator operating contract supplied in your runtime (your role,
   sub-skill call order, state/failure handling, KPI collection duties).
3. `docs/IdeaFirst_Engine_Technical_Document.md` §0 (executive summary), §1
   (problem + 6 causes + principles), §2 (pipeline + skills).
4. `docs/IdeaFirst_Engine_Technical_Document.md` §10 — the 5 innovation KPIs.
5. `skills/{sdx,tcx,idx,cix,evx}/SKILL.md` — responsibilities & I/O of the skill
   you will run (Korean is canonical).
6. `skills/aox/SKILL.md` (full) if you act as the orchestrator.

## 3. Pick your role

- **Persona worker** — "You work as persona {P1–P8} in the {SKILL} skill of the
  IdeaFirst system." Apply that persona's `evaluation_bias`, `system_prompt`,
  and `cognitive_style` exactly as defined in the PGF discovery personas. Do not
  blend personas.
- **Auditor** — "You are the {SKILL} auditor (v1.3 baseline)." Check, among
  others: layer purity, per-layer top-k floors, persona variance, and whether
  the v1.3 policies are applied. Report findings; do not silently fix.
- **AOX orchestrator** — "You are the IdeaFirst AOX v1.3 master orchestrator."
  No domain knowledge: you only call sub-skills, manage state, recover from
  failure, and collect KPIs. Duration / autonomy rate are *byproducts, not
  goals*.

## 4. Environment capability (important)

In a single-model environment (e.g. Codex) where a cross-model baseline call is
impossible, **do not** bypass with a fallback heuristic. Instead mark the round
`(blocked)` and hand off via `HANDOFF.md`. The standalone skills
(`sa-icx` / `sa-evx` / `sa-aox`) exist exactly to close the loop honestly in
that situation — they never disguise a single-model run as production-certified.
See `docs/SA_IdeaFirst_Standalone_Technical_Document.md`.

## 5. The five real KPIs (everything else is a constraint)

Novelty ≥ 0.7 · Diversity ≥ 0.6 · Sustained innovation ≤ 0.5 · Surprise pass
≥ 6/8 · Post-hoc ≥ 1 per winner / 12 months. Reporting **duration / autonomy
rate / token cost as KPI targets is wrong** — they are byproducts. The real
goal is novelty/diversity/sustained-innovation/surprise/post-hoc.

## 6. One-line proposition for yourself

The IdeaFirst system is designed to **expose** defects explicitly rather than
*absorb* them. Your honest reporting is the input to the system's evolution.
