# `AGENTS.md` Templates & Discovery Rules

## Antigravity Loading Contract

1. **Hierarchical Discovery:** Antigravity walks upward from the active file/CWD to the repository/workspace root and loads every `AGENTS.md` (or `GEMINI.md`) it encounters, applying them to their folder and all subdirectories. Duplicate paths are deduplicated automatically.
2. **No YAML Frontmatter:** Standalone `AGENTS.md` / `GEMINI.md` files **must NOT contain YAML frontmatter (`---`)**. Frontmatter belongs only in `.agents/rules/*.md` or `SKILL.md`.
3. **Budget Discipline:** Each file is capped at **24,000 bytes**, and always-on/hierarchical rules share a **20,000-token** aggregate rules budget (`defaultRulesBudget`). Keep root `AGENTS.md` under ~4 KB and module `AGENTS.md` files under ~3 KB.
4. **Grounded Facts Only:** Never invent scripts, test flags, or dependencies. Copy exact commands from observed manifests (`package.json`, `pyproject.toml`, `Makefile`, `go.mod`, `Cargo.toml`, CI workflows).
5. **What Rules Do NOT Do:** `AGENTS.md` injects instructions and constraints—it **does not** switch models automatically per directory. Use it to document conventions, quality gates, and safety boundaries cleanly.

---

## Template 1: Root Workspace (`<workspace>/AGENTS.md`)

Adapt `[brackets]` strictly from real discovery outputs.

### Variant A — Multi-Repo Umbrella (no root `.git`; subdirectories each have `.git`)

```markdown
# <Workspace Name> — Agent Harness Rules

`<workspace-path>` is a **multi-repository workspace** containing <N> independent Git repositories (there is no root `.git` directory):

| Directory | Role | Stack & Tooling |
| :--- | :--- | :--- |
| `<web-dir>/` | <Frontend role> | <Framework, package manager> |
| `<api-dir>/` | <Backend API role> | <Framework, runtime, DB> |
| `<ml-dir>/` | <ML/Data role> | <Python/venv, test runner> |

## Workspace-Wide Engineering Rules

1. **Git Operations Inside Subrepositories:**
   Always change into or target the specific `<repo-dir>/` subdirectory before running `git` commands. Never assume a root Git repository.
2. **Package Managers & Runtimes:**
   - JavaScript / TypeScript (`<web-dir>`): strictly use `<pnpm|npm|bun>`.
   - Python (`<api-dir>`, `<ml-dir>`): use `<uv run ... | .venv>`.
3. **Commits & Quality Gates:**
   - Follow Conventional Commits (`type(scope): description`).
   - Run the target subrepository's linter, typechecker, and unit test suite before proposing commits or PRs. Never push with failing checks.
4. **Protected Files & Workspace Hygiene:**
   - Never read, print, or overwrite `.env` or `.env.*` secret files (edit `.env.example` templates only).
   - Never modify frozen backup files or lockfiles (`~$*.docx`, etc.).
   - Place temporary/scratch scripts in the conversation artifact `scratch/` directory, never in the workspace root.
5. **Workspace Skills & Subrepository Rules:**
   - Shared workflow skills live in `.agents/skills/` (if present).
   - Module-specific constraints live in each directory's `AGENTS.md`.
```

### Variant B — True Monorepo (single root `.git`, e.g., `apps/` + `packages/`)

```markdown
# <Project Name> — Monorepo Agent Rules

Single-repository monorepo managed with `<pnpm workspaces / Turborepo / uv / Nx>`.

| Path | Role | Key Commands |
| :--- | :--- | :--- |
| `apps/web/` | <Web app> | `<pnpm --filter web ...>` |
| `apps/api/` | <Backend service> | `<...>` |
| `packages/shared/` | <Shared types/UI> | `<...>` |

## Workspace Rules

1. **Package Manager:** Strictly use `<pnpm|uv|...>`.
2. **Cross-Package Changes:** When modifying shared contracts (`packages/*`), run typechecks and tests across downstream consumers before finishing.
3. **Commits & Verification:** Follow Conventional Commits (`type(scope): description`) and pass lint, typecheck, and unit tests before proposing commits/PRs.
4. **Secrets & Safety:** Never edit `.env` / `.env.*` secret files directly; update `.env.example` instead. Never run destructive DB or infra commands (`migrate deploy`, `push --force`, `reset --hard`) without explicit approval.
```

---

## Template 2: Subrepository / Module `AGENTS.md` Blueprints

Keep each sub-`AGENTS.md` self-contained so it also works when a developer opens that subrepository alone in a separate IDE window.

### Backend API (`<api-dir>/AGENTS.md`)
* **Stack & Architecture:** Framework, DB/ORM, architectural boundaries (e.g., Clean Architecture layers: keep domain decoupled from HTTP/DB adapters).
* **Quality Gates:** Exact lint, format-check, strict typecheck (`mypy`/`pyright`/`tsc`), and fast unit test command (excluding slow/integration markers when applicable).
* **Safety Boundaries:** Never run DB migrations (`alembic upgrade head`, `prisma migrate deploy`) or seed scripts against staging/production targets without explicit user approval; never read or modify `.env`.

### Frontend Web (`<web-dir>/AGENTS.md`)
* **Stack & Package Manager:** Exact framework versions, styling engine (e.g., Tailwind v4 `@theme` tokens without `tailwind.config.js` or arbitrary hex values), strict package manager (`pnpm`).
* **Language Conventions:** Codebase/identifiers/commits language vs. user-facing UI locale (note clearly if UI copy is Spanish/EN/etc.).
* **Quality Gates:** Exact lint, format check, `tsc --noEmit`, and production build commands.

### ML / Evaluation (`<ml-dir>/AGENTS.md`)
* **Runtime:** Virtualenv / `uv` / Conda command conventions and core directories (`src/`, `tests/`, `validation/`).
* **Quality Gates:** Exact linter and `pytest` commands.
* **Reproducibility & Data Integrity:** Never modify ground-truth evaluation datasets or overwrite saved benchmark artifacts without explicit approval; preserve fixed random seeds (`seed=42`) and record commit hashes alongside reported metrics.

### Scrapers / Workers / ETL (`<worker-dir>/AGENTS.md`)
* **Runtime & Safe Local Testing:** Always test locally with dry-run / non-production flags (e.g., `--no-supabase`, `--dry-run`, small batch caps like `--jobs 5`) writing to ignored output paths.
* **Tests & Safety:** Exact test runner command; never ingest into production stores or expose `.env` credentials.

### Docs / Academic Manuscripts (`<docs-dir>/AGENTS.md`)
* **Language Override:** Explicitly state manuscript/spec language (e.g., formal academic English) if other repos enforce a non-English UI language.
* **Formatting & Backup Protection:** Specify frozen backup versions (`v1..vN`), Word lock files (`~$*.docx`), template styles/cross-references preservation, citation verification rules, and GenAI disclosure requirements if applicable.
