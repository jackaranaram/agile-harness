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

### 3. Run Validations (Local Tests & Lints)
- Detectar toolchain del proyecto automáticamente:
  - **Node.js** (`package.json` existe):
    - Detectar package manager: `pnpm-lock.yaml` → `pnpm`, `yarn.lock` → `yarn`, `package-lock.json` → `npm`
    - Leer scripts de `package.json`: buscar `lint`, `format`, `test`.
    - Ejecutar: `{pm} run lint`, `{pm} run format --check` (o el script correspondiente), `{pm} run test`.
  - **Python** (`pyproject.toml` existe):
    - Ejecutar: `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run pytest`.
  - **Rust** (`Cargo.toml` existe):
    - Ejecutar: `cargo clippy`, `cargo fmt --check`, `cargo test`.
  - **Go** (`go.mod` existe):
    - Ejecutar: `gofmt -l .`, `go vet ./...`, `go test ./...`.
  - **Genérico**: si no se detecta toolchain conocido, preguntar al usuario qué comandos ejecutar.
- Si falla alguna validación:
  - Mostrar errores y abortar para que el usuario los corrija antes de pasar a revisión.

### 4. Push Final
- `git push origin {currentBranch}`
- Si el push falla, resolver mediante pull/rebase según sea necesario.

### 5. Pasar PR a Ready for Review
- Dado que el Draft PR ya está abierto en GitHub (creado en la inicialización de la rama):
  - Ejecutar el comando local de GitHub CLI: `gh pr ready` (o usar la API/MCP de GitHub para marcar el PR como listo para revisión).
  - Actualizar la tarjeta del proyecto (si aplica) a la columna/status **"Ready for review"** usando el ID del campo Status y la opción correspondiente (color: PURPLE).

### 6. Post-Push Cleanup
- Si se stashearon cambios al inicio: preguntar "¿Aplicar stash de vuelta?" (`git stash pop`).

### 7. Summary
"Validaciones OK. Sin conflictos locales con {targetBranch}. Cambios subidos y PR marcado como Listo para Review (Ready for review)."
