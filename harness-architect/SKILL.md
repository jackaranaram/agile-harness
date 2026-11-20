---
name: harness-architect
description: >-
  Audit, design, generate, and deterministically verify Antigravity agent harnesses
  across multi-repo workspaces, monorepos, and single repositories: hierarchical
  AGENTS.md rules, .agents/hooks.json lifecycle guardrails, safe PreToolUse scripts,
  and Orchestrator (Neon/Argon) guidance. Trigger whenever the user asks to configure
  or improve an agent harness, set up AGENTS.md or hooks.json, standardize rules across
  web/backend/ML repos, or replicate a productivity harness for a new SaaS or monorepo
  project ("armar arnés", "configurar arnés", "agent harness", "AGENTS.md",
  "hooks.json", "guardrails", "configurar reglas del proyecto", "nuevo proyecto SaaS").
---

# Harness Architect

Design and verify project-grounded Antigravity harnesses built from two complementary layers:
1. **Context & Quality Layer (`AGENTS.md` hierarchy):** Grounded stack maps, package manager contracts, quality gates, and domain boundaries scoped per repository/directory.
2. **Enforcement Layer (`.agents/hooks.json` + `.agents/hooks/guardrails.py`):** Fast, fail-open `PreToolUse` guards blocking `.env` leaks, temporary lockfiles, frozen backups, destructive Git/shell commands, and off-standard package managers.

Never guess commands, test runners, or repository structure. Extract every rule directly from observed project files.

## Phase 1 — Read-Only Workspace Discovery

Inspect the workspace before proposing or writing files:
1. **Detect Repository Topology:** Check whether `.git` exists at the workspace root (monorepo or single-repo) or inside child directories (`api/`, `web/`, `ml/`, etc. -> multi-repo umbrella).
2. **Inventory Active Customizations:** Check `<root>/.agents/` (`rules/`, `skills/`, `hooks.json`) and any existing `AGENTS.md` / `GEMINI.md` / `CLAUDE.md` files. Check whether legacy `AGENTS.md` files mistakenly include YAML frontmatter (`---`), which standalone `AGENTS.md` files must not use.
3. **Read Real Manifests & Tooling:** Read only relevant manifests (`package.json`, `pnpm-workspace.yaml`, `pyproject.toml`, `Makefile`, `go.mod`, `Cargo.toml`, `turbo.json`, `.pre-commit-config.yaml`, `README.md`, `.github/workflows/`) to capture exact lint, format, typecheck, build, and test commands.
4. **Check Runtime Commands:** Verify the available shell Python command (`python --version` vs `python3 --version`) inside `<workspace>` so `hooks.json` works reliably on the host OS (`cmd /c` on Windows, `sh -c` on POSIX).

## Phase 2 — Blueprint & Alignment

Before generating files (skip waiting if the user already asked to execute directly):
1. Propose the exact `AGENTS.md` file list (`<root>/AGENTS.md` plus per-repo or per-app/package files for multi-repo/monorepo workspaces).
2. Propose specific guardrail rules (`deny` on `.env*` except `.env.example`, `~$*` lockfiles, frozen datasets/backups; `force_ask` on `git reset --hard`, `git push --force` without `--force-with-lease`, `rm -rf`, `Remove-Item -Recurse -Force`, and high-impact DB migrations; `ask` on off-standard package managers like `npm`/`yarn` when using `pnpm`).
3. Confirm Git tracking preference for generated `AGENTS.md` files (leave untracked, add to `.gitignore`, or open PRs cleanly per repository).
4. Clarify model usage honestly: recommend `Orchestrator (Neon)` as the default daily planner/worker pairing and `Orchestrator (Argon)` for complex cross-service architecture or hard debugging, noting clearly that `AGENTS.md` sets context/rules and **does not** switch models automatically per directory.

## Phase 3 — Author Harness Artifacts

Follow [agents-md-templates.md](./references/agents-md-templates.md) and [hooks-contract.md](./references/hooks-contract.md):

1. **Write `AGENTS.md` Hierarchy:**
   - Start cleanly with a Markdown `# Heading` (**zero YAML frontmatter `---`**).
   - Keep root `AGENTS.md` under ~4 KB and module files under ~3 KB (strict Antigravity cap: `24,000` bytes per file; aggregate rule budget: `20,000` tokens).
   - Make each subrepository `AGENTS.md` self-contained so it also works when opened standalone.
   - Preserve all existing rules in `.agents/rules/*.md` unless fixing an explicit error with user consent.

2. **Install & Customize Guardrail Hook:**
   - Copy/adapt [guardrails_template.py](./scripts/guardrails_template.py) to `<workspace>/.agents/hooks/guardrails.py`.
   - Customize only the top-level `POLICY` dictionary (`protected_filename_regexes`, `protected_path_substrings`, `disallowed_pkg_managers`, `preferred_pkg_manager`, `extra_force_ask_regexes`). Keep fail-open `try/except` in `main()`.
   - Create `<workspace>/.agents/hooks.json` with separate `PreToolUse` matcher entries (`"write_file"`, `"edit_file"`, `"run_command"`), pointing to the verified interpreter (`"python hooks/guardrails.py"` or `"python3 hooks/guardrails.py"`) and `"timeout": 5`.

## Phase 4 — Deterministic Verification

Run [verify_harness.py](./scripts/verify_harness.py) via `run_command` from the workspace:

```bash
python "<path-to-harness-architect>/scripts/verify_harness.py" \
  --workspace "<workspace-root>" \
  --expect-deny-file "<project-specific-protected-file-if-any>" \
  --expect-ask-cmd "<disallowed-pkg-manager-test-if-any>"
```

All checks must pass (`exit code 0`), proving via the real OS shell (`cmd /c` / `sh -c` from `<workspace>/.agents`):
- Every `AGENTS.md` is UTF-8 valid, `< 24,000` bytes, and free of YAML frontmatter.
- `hooks.json` parses cleanly and all referenced hook scripts exist.
- `.env` writes/edits are denied while `.env.example` and normal source files are allowed.
- Destructive commands (`git push --force`, `git reset --hard`, `rm -rf`, `Remove-Item -Force -Recurse`) trigger `force_ask` while `git push --force-with-lease` is allowed.
- `npx` and toolchain install paths (`AppData\Roaming\npm\pnpm.ps1`) never false-positive as disallowed `npm`.
- Malformed JSON fails open with `allow`.

## Phase 5 — Handoff

Report concisely in the user's language:
- Exact paths created/updated with file sizes, policy rules active, and the verified pass summary from `verify_harness.py`.
- Confirm untouched secrets/backups/existing rules.
- State exact Git status (whether files are untracked or committed/PR'd — never claim Git actions that were not run).
