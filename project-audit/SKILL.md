---
name: project-audit
description: >-
  Audits a project against professional standards (branch protection, CI/CD,
  lint, formatter, tests, pre-commit, security) and optionally fixes the items
  that fail. Use this skill whenever the user asks to "audit", "review
  standards", "project health check", "initialize project", "professional
  setup", "prepare repo", "configure CI", "add lint", "protect branch",
  "quality gates", "best practices", "hardening the repo", "setup profesional",
  "check standards", "poner en producción", or "revisar configuración". Also
  triggers when the user wants to "ensure code quality", "setup pre-commit",
  "add license", "conventional commits setup", or "dependabot config". Handles
  JS/TS, Python, Go, and generic projects.
---

# project-audit

This skill audits a project against professional standards and optionally fixes failing items. It has two modes:

- **[1] audit** — runs all checks, produces a scored report with priorities per project context
- **[2] fix <item(s)>** — applies fixes for specific check IDs from the audit report (only deterministic fixes)

---

## Workflow

### 1. Analyze the Repository

Do not ask the user. Figure it out:

- **Git**: `git rev-parse --is-inside-work-tree`, default branch, remote URL
- **Language stack**: read `package.json`, `tsconfig.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `composer.json`
- **Framework**: Next.js, React, Vue, FastAPI, Django, etc.
- **Existing configs**: lint, formatter, CI, pre-commit, editorconfig
- **Remote provider**: detect GitHub/GitLab/Bitbucket from `git remote -v`
- **Public or private**: `gh repo view --json isPrivate` if GitHub
- **Audit Exclusions**: read `AGENTS.md` (if it exists) and search for a section like `## Exclusiones de Auditoría` or `## Audit Exclusions`. Parse any bullet points containing a check ID and its justification (e.g., `- **TESTS**: Justification` or `- TESTS: Justification`).

### 2. Determine Scope

From the analysis, determine which checks apply:

- **🔴 Critical**: apply to ALL repos (branch protection, CI/CD, .gitignore)
- **🟡 High**: apply based on stack (lint if JS/TS/Python/Go, tests if src/ exists)
- **🟢 Medium**: apply based on team/project maturity
- **🔵 Low**: universal but optional

### 3. Present the Menu

```
Project-audit — jackaranaram/agile-harness
Stack: Next.js (TypeScript) | GitHub | Private

[1] Audit — revisar todos los estándares
[2] Fix <items> — corregir items específicos del reporte

Ej: "fix branch-protection,ci,pre-commit"
```

### 4. Execute by Mode

#### 4a. Audit Mode

Load `references/audit-checks.md` for the complete check list.

Before running the checks, check if any check ID is in the parsed exclusions from `AGENTS.md`.

For each applicable check (filtered by stack/scope in step 2):

1. If the check ID is excluded:
   - Do NOT run the detection command.
   - Assign status: `➖ Excluido` and note the justification.
   - Do not count it in the score (exclude it from both numerator and denominator).
2. Otherwise:
   - Run the detection command and capture output.
   - Assign status: `✅ Pass` | `⚠️ Warning` | `❌ Fail`.
   - Score as 1 (pass) or 0 (fail/warning).

Present results as a formatted report:

```
Audit Report — jackaranaram/agile-harness
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Critical (must have)
  [❌] BRANCH-PROTECTION — main no está protegida
  [❌] CI-CD — Sin workflows en .github/workflows/
  [✅] GITIGNORE — .gitignore presente

🟡 High (stack-specific)
  [✅] LINT — ESLint configurado (eslint.config.js)
  [⚠️] FORMATTER — Prettier configurado pero sin script en package.json
  [➖] TESTS — Excluido: Test runner no configurado
  [➖] TEST-FILES — Excluido: Test runner no configurado
  [⚠️] TS-STRICT — TypeScript strict mode NO habilitado
  [✅] LOCKFILE — package-lock.json presente

🟢 Medium (team maturity)
  [✅] PRE-COMMIT — Husky configurado
  [✅] COMMITLINT — Commitlint configurado
  [✅] ENV-EXAMPLE — .env.example existe

🔵 Low (optional)
  [✅] EDITORCONFIG — .editorconfig presente
  [➖] LICENSE — Excluido: Proyecto privado (temporalmente público)
  [✅] README — README.md existe

Score: 9/10 (90%) [3 Excluidos] — Professional Baseline: 10/13 ⚠️
```

Save the full report as `{project-root}/.audit-report.md` for reference.

#### 4b. Fix Mode

The user specifies which check IDs to fix (from the audit report):

```
fix branch-protection, ci-cd, pre-commit, editorconfig
```

For each requested item:

1. **Load the corresponding reference file** for the fix procedure
2. **Execute deterministically** — no creative generation for infrastructure code
3. **Show diff** — what changed before/after
4. **Mark as fixed** in the summary

Fixable items (deterministic):

| Check ID            | Fix Action                                        | Reference                             |
| ------------------- | ------------------------------------------------- | ------------------------------------- |
| `BRANCH-PROTECTION` | Configure branch protection via `gh api`          | `references/branch-protection.md`     |
| `CI-CD`             | Scaffold `.github/workflows/ci.yml` from template | `references/ci-templates/{stack}.yml` |
| `LINT`              | Create config file + npm/pip script               | `references/lint-formatter.md`        |
| `FORMATTER`         | Create config file + npm/pip script               | `references/lint-formatter.md`        |
| `PRE-COMMIT`        | Install husky + configure hooks                   | `references/pre-commit.md`            |
| `COMMITLINT`        | Install commitlint + husky hook                   | `references/pre-commit.md`            |
| `ENV-EXAMPLE`       | Extract keys from source, create `.env.example`   | inline in SKILL.md                    |
| `EDITORCONFIG`      | Create `.editorconfig` with universal values      | inline in SKILL.md                    |
| `LICENSE`           | Download and create LICENSE file (ask type)       | inline in SKILL.md                    |
| `GITIGNORE`         | Generate `.gitignore` for detected stack          | inline in SKILL.md                    |
| `TS-STRICT`         | Enable strict mode in `tsconfig.json`             | inline in SKILL.md                    |

Items NOT fixable by this skill (require human judgment):

- Test framework selection (user decides Jest vs Vitest vs Playwright)
- CI/CD pipeline logic (templates exist but workflow content is project-specific)
- Code architecture decisions

### 5. Summary

**Audit** output: report saved to `.audit-report.md`

```
Audit complete: 6/13 (46%). Items to fix: BRANCH-PROTECTION, CI-CD, TESTS, PRE-COMMIT, COMMITLINT, EDITORCONFIG, LICENSE
```

**Fix** output: summary of applied changes

```
✓ BRANCH-PROTECTION — main protegida (PR reviews + linear history + no force push)
✓ CI-CD — .github/workflows/ci.yml creado (Next.js template)
✓ PRE-COMMIT — husky instalado, pre-commit hook configurado
✓ EDITORCONFIG — .editorconfig creado
✗ LICENSE — saltado (preguntar tipo: MIT/Apache 2.0/GPL)
```

---

## Inline Fix Procedures

### ENV-EXAMPLE

1. Search source files for `process.env.`, `import.meta.env.`, `os.getenv()`, `os.environ`
2. Extract unique variable names
3. Create `.env.example` with vars in UPPER_SNAKE_CASE, empty values
4. Add comments for each var explaining its purpose

### EDITORCONFIG

```ini
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false
```

### LICENSE

Ask the user which license (MIT / Apache-2.0 / GPL-3.0). Download from:
`https://raw.githubusercontent.com/github/choosealicense.com/gh-pages/_licenses/{license}.txt`

### GITIGNORE

Generate `.gitignore` based on detected stack. Use `npx gitignore {stack}` if available, otherwise compose from templates for the detected language.

### TS-STRICT

If `tsconfig.json` exists:

- Enable `strict: true`
- Enable `noUncheckedIndexedAccess: true`
- Enable `noImplicitReturns: true`
- Keep existing `compilerOptions` intact, only add missing ones
