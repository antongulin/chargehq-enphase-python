<!-- FOR AI AGENTS - Human readability is a side effect, not a goal -->
<!-- Managed by agent: keep sections and order; edit content, not structure -->
<!-- Last updated: 2026-09-23 | Last verified: 2026-09-23 -->

# AGENTS.md

**Precedence:** the **closest `AGENTS.md`** to the files you're changing wins. Root holds global defaults only.

## Commands (unverified)
> Source: defaults — CI-sourced commands are most reliable

No Makefile or test suite exists. The script is a single long-running process that pushes data to
the external Charge HQ service; running it is **production operation requiring owner approval**, not
an ordinary local check.

<!-- AGENTS-GENERATED:START commands -->
| Task | Command | ~Time |
|------|---------|-------|
| Syntax check (verified) | `python3 -m py_compile chargehq_enphase.py` | <1s |
<!-- AGENTS-GENERATED:END commands -->

> Only the syntax check above was actually run. The live script was **not** executed and
> `pip install -r requirements.txt` was **not** run during this task. Check `README.md` and
> `requirements.txt` before using other commands.

## File Map

```text
chargehq_enphase.py       -> the integration script (Envoy -> Charge HQ)
requirements.txt          -> runtime deps (requests, python-dotenv)
Dockerfile                -> python:3-slim container image
chargehq-enphase.service  -> systemd unit template for boot/restart
.env.example              -> environment variable template (copy to .env)
.github/workflows/        -> Robin PR review workflow
.mcp.json, opencode.jsonc, .codex/, .cursor/, .vscode/ -> committed CodeGraph MCP wiring per client
.codegraph/               -> machine-local CodeGraph index (untracked, gitignored)
```

## Code intelligence: CodeGraph

- **CodeGraph (`codegraph`) is the approved code-intelligence index for the Python source** (`chargehq_enphase.py`). Project-local MCP configs are committed for Claude-compatible [`.mcp.json`](.mcp.json), Codex [`.codex/config.toml`](.codex/config.toml), OpenCode [`opencode.jsonc`](opencode.jsonc), Cursor [`.cursor/mcp.json`](.cursor/mcp.json), and VS Code [`.vscode/mcp.json`](.vscode/mcp.json). Each launches `codegraph serve --mcp`, sets `CODEGRAPH_TELEMETRY=0`, and passes `--path ${workspaceFolder}` where the client supports a workspace placeholder. Clients without a workspace placeholder (`.mcp.json`, `.codex/config.toml`, `opencode.jsonc`) rely on the MCP client's project root/`rootUri` instead, so start those clients from this checkout and confirm `codegraph status` reports this project — a CLI run from a parent directory targets that parent. `AGENTS.md` stays the only instruction source; do not let an installer create a competing instruction file, and do not add or edit home-directory configs from this repo.
- **Telemetry is off** via the committed `CODEGRAPH_TELEMETRY=0`. Keep it off.
- **The index stays untracked.** `.codegraph/` is gitignored and must never be committed. Build it once per checkout, then check it:

  ```bash
  CODEGRAPH_TELEMETRY=0 codegraph init .
  CODEGRAPH_TELEMETRY=0 codegraph sync .   # after pulls or merges that add files
  CODEGRAPH_TELEMETRY=0 codegraph status   # confirm "Index is up to date"
  ```

  After adding files through Git, run `sync` even if `status` says the index is current.
- **Use CodeGraph for the indexed code.** It gives symbol navigation for `chargehq_enphase.py` (`fetch_envoy_data`, `calculate_values`, `push_to_chargehq`, `main`). For Python, use CodeGraph's returned source; read the file directly when the result flags stale content or omits a needed detail. For non-Python docs and configuration — Markdown (`README.md`, this file), YAML (`.github/workflows/`), JSON/TOML configs (`.mcp.json`, `.codex/config.toml`, `opencode.jsonc`, `.cursor/mcp.json`, `.vscode/mcp.json`), plain pip requirements (`requirements.txt`), the `Dockerfile`, and the systemd unit — treat CodeGraph as a file lister rather than navigation and use ordinary search and read.
- **Canonical source:** `https://github.com/colbymchenry/codegraph`. The global `codegraph` binary is a user-managed, pre-existing install (ask-first to add or update); per-repo setup here is only the wiring plus the local index. Confirm `command -v codegraph` and `codegraph version` before relying on it.
- **Commands:** `codegraph status`, `codegraph query "<symbol>"`, `codegraph node <file-or-symbol>`, `codegraph explore "<area>"`, `codegraph files`.

## Response Style
- Answer first, elaborate only if needed. No sycophantic openers ("Great question!", "Absolutely!").
- For yes/no or status questions, lead with the answer.
- Skip preamble. Match response length to task complexity.

## Workflow

Start every session by inspecting Git status and worktrees, fetching origin with pruning, safely fast-forwarding local main, and verifying main matches origin/main. Only then create a task branch from synchronized main if needed. Preserve existing task branches and unfinished work. Never reset, discard changes, auto-stash, or force-push merely to synchronize. If safe synchronization is blocked, resolve the blocker before editing or branching.

1. **Before coding**: Read nearest `AGENTS.md` + check Golden Samples for the area you're touching
2. **After each change**: Run the smallest relevant check (lint → typecheck → single test)
3. **Before committing**: Run full test suite if changes affect >2 files or touch shared code
4. **Before claiming done**: Run verification and **show output as evidence** — never say "try again", "should work now", "tested", "verified", or "all green" without pasted command output in the same turn

## Heuristics (quick decisions)
<!-- AGENTS-GENERATED:START heuristics -->
| When | Do |
|------|-----|
| Adding env var | Add to `.env.example` first |
| Adding dependency | Ask first - we minimize deps |
| Unsure about pattern | Check Golden Samples above |
<!-- AGENTS-GENERATED:END heuristics -->

## Repository Settings
<!-- AGENTS-GENERATED:START repo-settings -->
- **Default branch:** `main`
- **Merge strategy:** squash, merge, rebase
<!-- AGENTS-GENERATED:END repo-settings -->

<!-- AGENTS-GENERATED:START ci-rules -->

<!-- AGENTS-GENERATED:END ci-rules -->

## Boundaries

### Always Do
- Run pre-commit checks before committing
- Add tests for new code paths
- Use conventional commit format: `type(scope): subject`
- Use **atomic commits** (one logical change per commit); preserve signatures, keep bisection useful
- **Show test output as evidence before claiming work is complete** — never say "try again", "should work now", "tested", "verified", or "all green" without pasted command output
- Before any edit, verify `pwd` resolves inside the intended repo worktree — not `.bare/`, not `~/.claude/skills/…`, not `~/.claude/plugins/cache/…` (those are read-only caches that get clobbered on update)
- For upstream dependency fixes: run **full** test suite, not just affected tests
- Force-push only with `--force-with-lease`

### Ask First
- Adding new dependencies
- Modifying CI/CD configuration
- Changing public API signatures
- Running full e2e test suites
- Repo-wide refactoring or rewrites
- Operations that touch >3 repos (produce a dry-run plan first)

### Never Do
- Commit secrets, credentials, or sensitive data
- Modify vendor/, node_modules/, or generated files
- Push directly to main/master branch — open a PR
- Merge a PR before all review threads are resolved
- Squash commits during merge or rebase unless the user explicitly asked
- Edit installed skill/plugin cache paths (`~/.claude/skills/`, `~/.claude/plugins/cache/`, `**/.bare/**`) — always the source worktree
- Reply to review comments with bare "Addressed" or "Fixed" — cite the resolving commit SHA
- Delete migration files or schema changes
- Use `secrets: inherit` in reusable GitHub Actions workflows (pass secrets explicitly)

## Contributing (for AI agents)
- **Comprehension**: Understand the problem before submitting code. Read the linked issue, understand *why* the change is needed, not just *what* to change.
- **Context**: Every PR must explain the trade-offs considered and link to the issue it addresses. Disclose AI assistance if the project requires it.
- **Continuity**: Respond to review feedback. Drive-by PRs without follow-up will be closed.

<!-- AGENTS-GENERATED:START module-boundaries -->

<!-- AGENTS-GENERATED:END module-boundaries -->

## Scoped AGENTS.md (MUST read when working in these directories)
<!-- AGENTS-GENERATED:START scope-index -->
- `./.github/workflows/AGENTS.md` — GitHub Actions workflows and CI/CD automation
<!-- AGENTS-GENERATED:END scope-index -->

> **Agents**: When you read or edit files in a listed directory, you **must** load its AGENTS.md first. It contains directory-specific conventions that override this root file.

## When instructions conflict
The nearest `AGENTS.md` wins. Explicit user prompts override files.

<!-- DOX:BEGIN (canonical: github.com/agent0ai/dox AGENTS.md — always-latest copy; safe to edit/extend the block below, e.g. fill in Child DOX Index) -->
# DOX framework

- DOX is highly performant AGENTS.md hierarchy installed here
- Agent must follow DOX instructions across any edits

## Core Contract

- AGENTS.md files are binding work contracts for their subtrees
- Work products, source materials, instructions, records, assets, and durable docs must stay understandable from the nearest applicable AGENTS.md plus every parent AGENTS.md above it

## Read Before Editing

1. Read the root AGENTS.md
2. Identify every file or folder you expect to touch
3. Walk from the repository root to each target path
4. Read every AGENTS.md found along each route
5. If a parent AGENTS.md lists a child AGENTS.md whose scope contains the path, read that child and continue from there
6. Use the nearest AGENTS.md as the local contract and parent docs for repo-wide rules
7. If docs conflict, the closer doc controls local work details, but no child doc may weaken DOX

Do not rely on memory. Re-read the applicable DOX chain in the current session before editing.

## Update After Editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning AGENTS.md when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or quality
- AGENTS.md creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child index changes. Update child docs when parent changes alter local rules. Remove stale or contradictory text immediately. Small edits that do not change behavior or contracts may leave docs unchanged, but the DOX pass still must happen.

## Hierarchy

- Root AGENTS.md is the DOX rail: project-wide instructions, global preferences, durable workflow rules, and the top-level Child DOX Index
- Child AGENTS.md files own domain-specific instructions and their own Child DOX Index
- Each parent explains what its direct children cover and what stays owned by the parent
- The closer a doc is to the work, the more specific and practical it must be

## Child Doc Shape

- Create a child AGENTS.md when a folder becomes a durable boundary with its own purpose, rules, responsibilities, workflow, materials, or quality standards
- Work Guidance must reflect the current standards of the project or user instructions; if there are no specific standards or instructions yet, leave it empty
- Verification must reflect an existing check; if no verification framework exists yet, leave it empty and update it when one exists

Default section order:
- Purpose
- Ownership
- Local Contracts
- Work Guidance
- Verification
- Child DOX Index

## Style

- Keep docs concise, current, and operational
- Document stable contracts, not diary entries
- Put broad rules in parent docs and concrete details in child docs
- Prefer direct bullets with explicit names
- Do not duplicate rules across many files unless each scope needs a local version
- Delete stale notes instead of explaining history
- Trim obvious statements, repeated rules, misplaced detail, and warnings for risks that no longer exist

## Closeout

1. Re-check changed paths against the DOX chain
2. Update nearest owning docs and any affected parents or children
3. Refresh every affected Child DOX Index
4. Remove stale or contradictory text
5. Run existing verification when relevant
6. Report any docs intentionally left unchanged and why

## User Preferences

When the user requests a durable behavior change, record it here or in the relevant child AGENTS.md

## Child DOX Index

- [`./.github/workflows/AGENTS.md`](./.github/workflows/AGENTS.md) — GitHub Actions workflows and CI/CD automation (Robin PR review), including runner and secrets conventions. The root AGENTS.md owns repository-wide rules, CodeGraph wiring, and the script contract.
<!-- DOX:END -->

<!-- BASELINE:BEGIN (managed by agents-md-bootstrap) -->
## Engineering baseline

This repo follows the baseline: `~/Code/700 systems/baseline` (https://github.com/antongulin/baseline, private).
Read `baseline/00-laws.md` first; pillars 01–07 hold the law (workspace, agents, project,
stacks, infra, delivery, knowledge). Answer standards questions from those files, not memory.
Anything missing or broken against the baseline is surfaced loudly — never skipped (law 2).
<!-- BASELINE:END -->
