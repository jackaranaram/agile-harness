# Audit Checks Reference

Complete list of all checks with detection commands, priority, and fixability.

## 🔴 Critical (ALL projects)

| ID | Check | Detection Command | Priority Condition |
|---|---|---|---|
| BRANCH-PROTECTION | Default branch protected | `gh api repos/{owner}/{repo}/branches/{default}/protection 2>&1` | Always |
| CI-CD | CI workflow exists | `Test-Path ".github/workflows/ci.yml"` or `ls .github/workflows/*.yml 2>/dev/null` | Always |
| GITIGNORE | .gitignore exists | `Test-Path ".gitignore"` | Always |
| LOCKFILE | Lock file present | `Test-Path "package-lock.json" -or Test-Path "pnpm-lock.yaml" -or Test-Path "yarn.lock" -or Test-Path "Cargo.lock" -or Test-Path "go.sum"` | Always |
| README | README exists | `Test-Path "README.md"` | Always |

## 🟡 High (stack-specific)

| ID | Check | Detection Command | Applies When |
|---|---|---|---|
| LINT | Linter configured | `Test-Path ".eslintrc*" -or Test-Path "eslint.config.*" -or Test-Path ".eslintrc.*" -or Test-Path "pyproject.toml" | Select-String "ruff" -or Test-Path ".golangci.yml"` | JS/TS/Python/Go |
| FORMATTER | Formatter configured | `Test-Path ".prettierrc*" -or Test-Path ".prettierrc" -or Test-Path "pyproject.toml" | Select-String "ruff" -or Test-Path ".editorconfig"` (partial) | JS/TS/Python/Go |
| FORMATTER-SCRIPT | Format script in package.json | `Get-Content "package.json" | Select-String '"format"'` | JS/TS with package.json |
| TESTS | Test framework detected | `Test-Path "vitest.config.*" -or Test-Path "jest.config.*" -or Test-Path "playwright.config.*" -or (Get-Content "package.json" | Select-String "vitest|jest|playwright|mocha|ava")` | Projects with src/ |
| TEST-FILES | Tests exist | `Get-ChildItem -Recurse "*.test.*","*.spec.*","__tests__","tests/"` | Test framework detected |
| TS-STRICT | TypeScript strict mode | `Get-Content "tsconfig.json" | Select-String '"strict": true'` | TypeScript project |
| DEPENDABOT | Dependabot configured | `Test-Path ".github/dependabot.yml"` | GitHub project |

## 🟢 Medium (team maturity)

| ID | Check | Detection Command | Applies When |
|---|---|---|---|
| PRE-COMMIT | Pre-commit hooks | `Test-Path ".husky/pre-commit" -or Test-Path ".pre-commit-config.yaml"` | >1 contributor or active project |
| COMMITLINT | Commit convention | `Test-Path "commitlint.config.*" -or (Get-Content "package.json" | Select-String "commitlint")` | >1 contributor |
| ENV-EXAMPLE | .env.example exists | `Test-Path ".env.example"` | Project uses env vars |
| DOCKERFILE | Dockerfile exists | `Test-Path "Dockerfile" -or Test-Path "docker-compose.yml"` | Backend or deployable project |
| CODEOWNERS | CODEOWNERS file | `Test-Path ".github/CODEOWNERS"` | >2 contributors |

## 🔵 Low (optional)

| ID | Check | Detection Command | Applies When |
|---|---|---|---|
| EDITORCONFIG | .editorconfig exists | `Test-Path ".editorconfig"` | Always |
| LICENSE | LICENSE file exists | `Test-Path "LICENSE" -or Test-Path "LICENSE.md" -or Test-Path "LICENSE.txt"` | Public repo |
| CONVENTIONAL-COMMITS | Recent commits follow CC | `git log --format="%s" -5 --skip=1 | Select-String "^(feat|fix|docs|chore|refactor|test|ci)(\(.*?\))?: "` | Always |
| PR-TEMPLATE | PR template exists | `Test-Path ".github/PULL_REQUEST_TEMPLATE" -or Test-Path ".github/PULL_REQUEST_TEMPLATE.md"` | >1 contributor |
| ISSUE-TEMPLATE | Issue template exists | `Test-Path ".github/ISSUE_TEMPLATE"` | Public project |
| SECURITY | Security policy | `Test-Path "SECURITY.md"` | Public project |
