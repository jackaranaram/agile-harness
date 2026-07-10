# Lint & Formatter Setup

Deterministic config files for common stacks.

## ESLint (JS/TS)

Create `eslint.config.js` (flat config for ESLint 9+):

```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    rules: {
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/no-explicit-any": "warn",
    },
  },
  {
    ignores: ["dist/", "node_modules/", ".next/"],
  }
);
```

Add to `package.json`:
```json
"scripts": {
  "lint": "eslint src/ --report-unused-disable-directives --max-warnings 0",
  "lint:fix": "eslint src/ --fix"
}
```

## Prettier (Universal)

Create `.prettierrc`:
```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "arrowParens": "always"
}
```

Add to `package.json`:
```json
"scripts": {
  "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
  "format:check": "prettier --check \"src/**/*.{ts,tsx,js,jsx,json,css,md}\""
}
```

## Ruff (Python)

Add to `pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

Add to scripts or just run: `ruff check . && ruff format .`

## golangci-lint (Go)

Create `.golangci.yml`:
```yaml
linters:
  enable:
    - gofmt
    - govet
    - errcheck
    - staticcheck
    - gosimple
    - ineffassign

run:
  timeout: 5m
```

## Combined Lint+Format Script

Add to `package.json` when both eslint and prettier are configured:
```json
"scripts": {
  "lint": "eslint src/ --report-unused-disable-directives --max-warnings 0",
  "lint:fix": "eslint src/ --fix",
  "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
  "format:check": "prettier --check \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
  "check": "npm run lint && npm run format:check",
  "fix": "npm run lint:fix && npm run format"
}
```
