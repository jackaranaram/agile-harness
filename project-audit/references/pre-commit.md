# Pre-commit & Commitlint Setup

## Husky + lint-staged (JS/TS)

### Step 1: Install dependencies

```powershell
npm install --save-dev husky lint-staged
```

### Step 2: Enable git hooks

```powershell
npx husky init
```

### Step 3: Configure pre-commit hook

Edit `.husky/pre-commit`:

```bash
npx lint-staged
```

### Step 4: Configure lint-staged in package.json

```json
"lint-staged": {
  "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
  "*.{json,css,md}": ["prettier --write"]
}
```

### Step 5: Verify

```powershell
npx husky run pre-commit
```

---

## Commitlint (Conventional Commits)

### Step 1: Install

```powershell
npm install --save-dev @commitlint/cli @commitlint/config-conventional
```

### Step 2: Create config

Create `commitlint.config.js`:

```js
export default { extends: ['@commitlint/config-conventional'] };
```

### Step 3: Add commit-msg hook

```powershell
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg
```

### Step 4: Verify

```powershell
echo "foo: this will fail" | npx commitlint
echo "chore: this will pass" | npx commitlint
```

---

## pre-commit Framework (Python)

### Step 1: Install

```powershell
pip install pre-commit
```

### Step 2: Create config

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.2.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
```

### Step 3: Install hooks

```powershell
pre-commit install
pre-commit install --hook-type commit-msg
```

### Step 4: Verify

```powershell
pre-commit run --all-files
```
