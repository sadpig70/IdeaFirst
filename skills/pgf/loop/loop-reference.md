# pgf-loop Execution Engine Specification

## 1. Overview

pgf-loop is a self-contained loop engine that automatically traverses and executes nodes in WORKPLAN-{Name}.md, leveraging Claude Code's Stop Hook platform feature.

### Execution Modes

| Mode | DESIGN-{Name}.md | Execution Spec Source | Purpose |
|------|-----------|---------------|------|
| **Standard** | Required | PPR def blocks in DESIGN-{Name}.md | Complex system implementation |
| **Lightweight** | Not required | Inline `#` comments in WORKPLAN-{Name}.md | Simple tasks, documentation, refactoring |

In Lightweight mode, `#` comments written under WORKPLAN nodes serve as the PPR equivalent.

### Core Principle

```
Claude completes current node work → attempts session termination
    ↓
Stop Hook (stop-hook.py) intercepts
    ↓
Selects next executable node from status-{Name}.json
    ↓
Extracts execution spec (Strategy 1: DESIGN PPR → Strategy 2: WORKPLAN inline)
    ↓
Constructs dynamic prompt → re-injects into Claude → executes next node
    ↓
... repeats until all nodes complete ...
```

---

## 2. File Structure

### Standard Mode

```
<project-root>/
    .claude/
        hooks.json              ← Stop Hook registration (auto-configured by init-loop.py)
        pgf-loop-state.json     ← Loop runtime state (exists only when active)
    .pgf/
        DESIGN-{Name}.md              ← System design (Gantree + PPR)
        WORKPLAN-{Name}.md            ← Execution plan
        status-{Name}.json             ← Per-node execution status
```

### Lightweight Mode

```
<project-root>/
    .claude/
        hooks.json
        pgf-loop-state.json
    .pgf/
        WORKPLAN-{Name}.md            ← Execution plan + inline task specs
        status-{Name}.json             ← Per-node execution status
```

---

## 3. Commands

### `/PGF loop start`

Initializes the loop and starts executing the first node.

**Prerequisites**: `.pgf/WORKPLAN-{Name}.md` must exist. `.pgf/DESIGN-{Name}.md` is optional.

**Behavior**:
1. Creates `.claude/pgf-loop-state.json` (state initialization + mode determination)
2. Registers Stop Hook in `.claude/hooks.json`
3. Checks `status-{Name}.json` — applies the following rules:
   - If already created by `plan` mode → use as-is (authoritative copy)
   - If missing → AI auto-generates from WORKPLAN-{Name}.md
   - If exists but inconsistent with WORKPLAN-{Name}.md → sync to WORKPLAN-{Name}.md
4. Selects first executable node → outputs prompt → Claude starts execution

**Automatic Mode Determination**:
- `--design PATH` specified + file exists → Standard mode
- `--design PATH` specified + file missing → warning output, falls back to Lightweight mode
- `--design` not specified → Lightweight mode

> **status-{Name}.json Creation Authority Rule**: `plan` mode's `convert_design_to_workplan()` is the primary creator. `loop start` is the fallback creator when missing. No conflict even if both run — `loop start` does not touch an existing file.

**Options**:
- `--max-iterations N`: Maximum iteration count (0 = unlimited, default)
- `--workplan PATH`: WORKPLAN path (default: `.pgf/WORKPLAN-{Name}.md`)
- `--design PATH`: DESIGN path (omit for Lightweight mode)

### `/PGF loop cancel`

Cancels the active loop.

**Behavior**:
1. Deletes `.claude/pgf-loop-state.json`
2. Reports current iteration and last node

### `/PGF loop status`

Reports loop progress status.

**Behavior**:
1. Reads `pgf-loop-state.json`
2. Reads `status-{Name}.json`
3. Reports progress, current node, iteration, mode (standard/lightweight)

---

## 4. Stop Hook Protocol

### Input (stdin)

```json
{
    "session_id": "unique session ID",
    "transcript_path": "conversation transcript file path"
}
```

### Output (stdout)

**Loop continues** (execute next node):
```json
{
    "decision": "block",
    "reason": "next node execution prompt",
    "systemMessage": "[pgf-loop] iteration N | node: NodeName | done/total done"
}
```

**Loop terminates** (all nodes complete or error):
```
(exit 0 with no output)
```

---

## 5. Node Selection Algorithm (select_next_node)

```
1. If a node with "in-progress" status exists → return that node (retry incomplete)
2. Among nodes with "designing" status where all @dep: are "done" → return first in tree order
3. If no candidates → None (triggers loop termination)
```

---

## 6. Execution Spec Extraction (extract-ppr.py)

### Epigenetic PPR (v2.4)

Context-adaptive PPR execution. When pgf-loop activates a node, `extract-ppr` reads the node's PPR `def` block from `DESIGN-{Name}.md` and injects it into the Stop Hook prompt. The PPR (the "gene") is fixed in DESIGN, but its expression at runtime varies with the surrounding context — available tools, prior node outputs, and current session patterns — so the same PPR can yield different execution behavior across sessions. The name mirrors biological epigenetics: fixed gene, environment-dependent expression.

### 2-Stage Fallback Strategy

```
Strategy 1: Extract PPR def block from DESIGN-{Name}.md
    ├─ "### [PPR] NodeName" header → child ```python code block
    └─ "def snake_name(" pattern → corresponding code block
    ↓ (empty result)
Strategy 2: Extract inline # comments from WORKPLAN-{Name}.md
    ├─ Search for "NodeName // description (status)" line
    └─ Collect # comment lines with deeper indentation → return as task spec
    ↓ (empty result)
Atomic node prompt ("Read node description from WORKPLAN and implement directly")
```

### WORKPLAN Inline Task Spec Format

```
NodeName // node description (status)
    # task: work to perform
    # target: file path or module
    # output: result file
    # criteria: completion criteria
```

`#` comments are free-form. No enforced structure — sufficient as long as AI can understand the intent.

---

## 7. Prompt Construction Rules

Prompt constructed by stop-hook at each iteration:

### Standard Mode

```
[pgf-loop] Node Execution Directive

Project: {project}
Current node: {node_name}
Progress: {done}/{total} nodes done
WORKPLAN: {workplan_path}
DESIGN: {design_path}
status-{Name}.json: {status_path}

## PPR Implementation Spec for This Node
{ppr_block}

## Required Post-Completion Tasks
1. Change this node's status to (done) in WORKPLAN-{Name}.md
2. Update status-{Name}.json
3. Progress report
```

### Lightweight Mode

```
[pgf-loop] [Lightweight] Node Execution Directive

Project: {project}
Current node: {node_name}
Progress: {done}/{total} nodes done
WORKPLAN: {workplan_path}
status-{Name}.json: {status_path}

## Task Spec for This Node (WORKPLAN Inline)
{inline_spec}

## Required Post-Completion Tasks
...
```

---

## 8. Session Isolation

- `session_id` recorded in `pgf-loop-state.json`
- Stop Hook compares hook input's `session_id` at execution time
- On mismatch, loop is ignored (protects other sessions)

---

## 9. Termination Conditions

| Condition | Action |
|------|------|
| All nodes "done" or "blocked" (see POLICY.completion) | Normal termination |
| `max_iterations` reached | Forced termination |
| `pgf-loop-state.json` deleted (`/PGF loop cancel`) | Immediate termination |
| `status-{Name}.json` parse failure | Error termination + state file cleanup |

---

## 10. Error Recovery

### On Node Execution Failure
- Claude attempts session termination without completing the node
- stop-hook detects the node is still "in-progress" in status-{Name}.json
- Re-injects the same node (retry)
- retry_count tracked in pgf-loop-state.json
- When max_retry exhausted, POLICY.on_blocked policy applies

### On State File Corruption
- JSON parse failure → delete state file → terminate loop
- User can restart with `/PGF loop start`

---

## 11. Compaction Resilience (PostCompact Hook)

### Problem
Long-running pgf-loop sessions may trigger context window compaction. Without protection, the loop state (current node, iteration, progress) can be lost after compaction.

### Solution: PostCompact + SessionStart Hook Chain

```
[Context full] → Compaction triggers
    ↓
[PostCompact Hook] post-compact-hook.py
    Saves pgf-loop-state.json → pgf-loop-state.backup.json
    Logs compaction event
    ↓
[Session resumes after compact]
    ↓
[SessionStart Hook] restore-pgf-state.py (matcher: "compact")
    Restores state from backup
    Outputs recovery info to stdout → auto-injected into Claude context
    ↓
[Stop Hook continues loop normally]
```

### Scripts
- `post-compact-hook.py` — Snapshots pgf-loop state on compaction
- `restore-pgf-state.py` — Restores state and injects context after compaction

### Hook Configuration (add to settings.json)

```json
{
  "hooks": {
    "PostCompact": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$HOME/.claude/skills/PGF/loop/post-compact-hook.py\""
          }
        ]
      }
    ]
  }
}
```

Note: SessionStart restore hook is optional — the Stop Hook can also detect and recover from backup files.
