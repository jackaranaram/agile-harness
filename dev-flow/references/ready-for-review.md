# Listo para Review (dry-run merge + validaciones + push + publicar PR)

Usa esta reference cuando el usuario quiera pasar su rama/Draft PR al estado "Listo para Review".

Lee el `targetBranch` del workflow reference cargado (tbd.md → `main`, github-flow.md → `main`, git-flow.md → según tipo de rama).

---

## Workflow Steps

### 1. Stash Uncommitted Changes
- `git status -s` para verificar cambios.
- Si hay: `git stash push -u -m "Auto-stashed before ready-for-review"` e informar al usuario.
- Recordar que hay stash para preguntar al final si aplicar de vuelta.

### 2. Fetch and Dry-Run Merge (local, sin commitear)
- `git fetch origin {targetBranch}` — trae lo último del remoto.
- Ejecutar merge local para detectar conflictos:
  ```
  $output = git merge origin/{targetBranch} --no-commit --no-ff 2>&1
  ```
- **Caso A: "Already up to date"** → no hay merge en progreso, continuar.
- **Caso B: Merge limpio** (`$LASTEXITCODE -eq 0`) → abortar merge: `git merge --abort`. Todo OK, continuar.
- **Caso C: Conflictos** (`$LASTEXITCODE -ne 0` y output contiene "CONFLICT" o "conflict") →
  - Mostrar archivos en conflicto al usuario.
  - Preguntar: "Hay conflictos en {archivos}. ¿Los resuelvo automáticamente?"
  - Si sí:
    - Resolver conflictos usando herramientas de edición.
    - `git add -A`
    - `git commit -m "chore: merge {targetBranch} and resolve conflicts"`
    - Informar al usuario que se creó un merge commit.
  - Si no:
    - `git merge --abort`
    - Informar al usuario y abortar: "Merge abortado. Resuelve los conflictos manualmente y vuelve a ejecutar."

### 3. Run Validations (Local Tests, Lints & Build)
- Detectar el toolchain leyendo los **scripts reales** del proyecto, nunca inventar flags.
- **Node.js** (`package.json` existe):
  - Detectar package manager: `pnpm-lock.yaml` → `pnpm`, `yarn.lock` → `yarn`, `package-lock.json` → `npm`.
  - Listar los scripts disponibles antes de ejecutar: `{pm} run` (o leer `package.json`).
  - Ejecutar, si existen, en este orden: **lint → format check → test → build/typecheck**.
  - **Nunca** ejecutar `{pm} run format --check`: eso invoca el script `format` (que **escribe** archivos) y le pasa `--check` como argumento, por lo que no verifica nada. Usar el script de verificación real: `format:check`, `check:format`, `prettier:check`, etc.
  - **Nunca** ejecutar `{pm} run test` a secas si el runner queda en **watch mode** (Karma/Angular, Jest, Vitest). Pasar el flag de CI real del proyecto. Ejemplo Angular con pnpm:
    ```powershell
    pnpm run format:check
    pnpm run lint
    pnpm test --watch=false --browsers=ChromeHeadless
    pnpm run build
    ```
    Con npm, los argumentos requieren `--`: `npm test -- --watch=false --browsers=ChromeHeadless`.
  - Si el proyecto no tiene script de format check, ejecutar el binario directamente (ej: `npx prettier --check .`) o preguntar al usuario.
- **Python** (`pyproject.toml` existe):
  - Ejecutar: `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run pytest`.
- **Rust** (`Cargo.toml` existe):
  - Ejecutar: `cargo clippy`, `cargo fmt --check`, `cargo test`.
- **Go** (`go.mod` existe):
  - Ejecutar: `gofmt -l .`, `go vet ./...`, `go test ./...`.
- **Genérico**: si no se detecta toolchain conocido, preguntar al usuario qué comandos ejecutar.
- Si falla alguna validación:
  - Mostrar errores y abortar para que el usuario los corrija antes de pasar a revisión. **No** continuar al push ni a `gh pr ready`.
- **Paridad local/CI:** ejecutar exactamente los mismos scripts que usa el CI (leer `.github/workflows/*.yml`). Un comando local distinto puede dar un falso verde.

### 4. Push Final
- `git push origin {currentBranch}`
- Si el push falla, resolver mediante pull/rebase según sea necesario.

### 5. Verificar el CI Real (antes de marcar Ready)
- **No** marcar el PR como listo basándose solo en `gh pr checks`: puede contener únicamente checks de terceros (Vercel, Netlify, Codecov, bots) y aun así parecer verde.
- Seguir `references/ci-triage.md`:
  1. Fijar el SHA: `$sha = git rev-parse HEAD` y comprobar que coincide con `gh pr view --json headRefOid`.
  2. Enumerar runs del repo para ese SHA: `gh run list --repo {owner}/{repo} --commit $sha --limit 20`.
  3. Exigir al menos un workflow **del propio repo** en `success` (`gh workflow list --repo {owner}/{repo}`).
- Clasificar:
  - **VERDE** → continuar al paso 6.
  - **ROJO_CÓDIGO** → abortar el Ready, corregir y volver a validar.
  - **INFRA_DESCONOCIDO** (`startup_failure`, 0 jobs, `log not found`, workflow no disparado, timeout, billing/permisos) → **no tocar código y no marcar Ready**; reportar la evidencia al usuario y dejar el PR en Draft.
  - **SIN_CI_CONFIGURADO** (`gh workflow list` vacío) → reportar que el repo no tiene CI y dejar el PR en Draft; marcar Ready solo con confirmación explícita del usuario. No crear workflows improvisados dentro del PR.

### 6. Pasar PR a Ready for Review
- Dado que el Draft PR ya está abierto en GitHub (creado en la inicialización de la rama) **y el CI está clasificado como VERDE**:
  - Ejecutar el comando local de GitHub CLI: `gh pr ready` (si el PR ya estaba listo, ignorar el error de idempotencia).
  - Actualizar la tarjeta del proyecto (si aplica) a la columna/status **"Ready for review"** usando el ID del campo Status y la opción correspondiente (color: PURPLE).

### 7. Post-Push Cleanup
- Si se stashearon cambios al inicio: preguntar "¿Aplicar stash de vuelta?" (`git stash pop`).

### 8. Summary
"Validaciones locales OK con los scripts reales del proyecto. Sin conflictos locales con {targetBranch}. CI del repo clasificado como VERDE para el SHA {sha}. Cambios subidos y PR marcado como Listo para Review (Ready for review)."
