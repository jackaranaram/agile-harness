---
name: dev-flow
description: Manages Git branch creation, safe code pushes with zero bloat, local sync/pruning, isolated parallel worktrees, and feature rebasing. Automates clean feature/fix branches from updated main, toolchain quality gates (lint/format/typecheck), Draft PR creation, atomic iterative commits via commit --amend and git push --force-with-lease, git worktree isolation for parallel bugfixes/tasks without interrupting active development, and clean git rebase workflows against advanced origin/master. Enforces professional engineering health gates (atomic commits, lines/files thresholds, Conventional Commits). Use whenever the user asks to create a branch ("crear rama", "nueva feature", "empezar tarea"), push code ("push", "push seguro", "actualizar PR", "hacer force push", "enmendar commit"), synchronize/clean local branches ("sync", "sincronizar", "limpiar ramas", "podar ramas", "actualizar master", "prune"), work in parallel or isolate a task ("worktree", "en paralelo", "tarea aislada", "hotfix sin tocar rama actual", "aislar refactor", "aislar optimizacion", "aislar tests"), or bring latest master changes into an active branch ("rebase", "actualizar mi rama con master", "poner al día rama").
---

# dev-flow

Skill de automatización de Git enfocado en máxima productividad, historial limpio y estándares de ingeniería profesional (Google Engineering Practices) en Windows (PowerShell).
100% autocontenido, agnóstico a cualquier lenguaje/stack, sin dependencias de MCPs externos y con **5 acciones fundamentales**:

1. **`branch` (Crear rama limpia):** Crea ramas estandarizadas (`feat/*`, `fix/*`, `chore/*`, etc.) directamente desde `origin/master` (o `origin/main`), podando ramas locales huérfanas.
2. **`push` (Push inteligente y seguro):** Valida que el proyecto compile y pase pruebas/linting localmente, y ejecuta push normal creando Draft PR o push iterativo (`commit --amend` + `push --force-with-lease`) sin ensuciar el historial de commits.
3. **`sync` (Sincronizar y podar ramas locales):** Cambia a la rama principal (`main`/`master`), actualiza contra `origin` (`git pull`) y elimina todas las ramas locales mergeadas o cuyo remoto fue borrado (`[origin/...: gone]`).
4. **`worktree` (Aislamiento para tareas paralelas e independientes):** Resuelve bugs, hotfixes, optimizaciones de rendimiento (`perf`), mejoras de cobertura de tests (`test`), refactors aislados (`refactor`) o auditorías de UI en una carpeta física paralela sin tocar la rama activa, sin hacer `stash`, sin interrumpir el servidor local de desarrollo (`pnpm start`), abriendo el PR y limpiando el worktree al finalizar.
5. **`rebase` (Sincronizar rama activa con master avanzado):** Pone al día la rama de trabajo actual sobre el último `origin/master` manteniendo un historial 100% lineal y actualizando el remoto con `--force-with-lease`.

---

## Estándares de Ingeniería y Health Gates (Google Engineering Practices)

Para garantizar un código mantenible, atómico y fácilmente auditable:

### 1. Límites de Tamaño y Atomicidad (Google CL Guidelines)
* **Tamaño del PR:** **Techo estricto de máximo 300 líneas netas de cambio** de autoría (sin límite mínimo; PRs de 1 a 50 líneas son óptimos para fixes y mejoras puntuales).
* **PRs Encadenados Dinámicos (Stacked PRs):** Si una funcionalidad proyecta superar las 300 líneas de lógica densa, el agente debe sugerir dividirla en ramas encadenadas. El agente infiere la cantidad de capas y su separación según la arquitectura real del proyecto (ej: 2 capas en refactors simples, 3 o más en features fullstack).
* **Atomicidad por commit:** Máximo **8 a 10 archivos de autoría** por commit. Cada commit debe representar un cambio lógico cohesivo.
* **Límite de commits:** Máximo **3 a 4 commits lógicos** por PR.
* **Bisectabilidad:** Cada commit individual debe compilar y pasar pruebas por separado.
* **Conventional Commits estricto:** `tipo(alcance): descripción en inglés imperativo` (ej: `feat(market): add compact cluster cards`). Tipos válidos: `feat`, `fix`, `refactor`, `perf`, `test`, `chore`, `docs`, `style`.

### 2. Exclusiones Automáticas (Inferencia de Código No-Autoría)
El agente debe inferir del contexto del repositorio y excluir de las métricas de líneas/archivos:
* **Lockfiles de dependencias** de cualquier gestor de paquetes.
* **Código autogenerado** (schemas, stubs, bindings, tipos autogenerados o archivos con avisos tipo `DO NOT EDIT`).
* **Assets estáticos y fixtures masivos** (imágenes, SVGs, datasets JSON de mock).
* **Migraciones declarativas** de base de datos o esquemas iniciales de infraestructura.

---

## Heurística de Decisión: ¿Cuándo `commit --amend` vs `Nuevo Commit`?

| Escenario | Acción | Comando |
| :--- | :--- | :--- |
| **Corrección de estilo, padding, typos o feedback de review en PR abierto** | **`AMEND`** | `git commit --amend --no-edit`<br>`git push --force-with-lease origin <branch>` |
| **Fix de linter, compilación o tests sobre el commit que se está construyendo** | **`AMEND`** | `git commit --amend --no-edit`<br>`git push --force-with-lease origin <branch>` |
| **Ajustes iterativos para probar en previews remotas (Vercel, Koyeb, CI)** | **`AMEND`** | `git commit --amend --no-edit`<br>`git push --force-with-lease origin <branch>` |
| **Capa arquitectónica independiente y testeable** (ej: tipos/esquema primero, luego UI/consumo) | **`NUEVO COMMIT`** | `git commit -m "..."`<br>`git push origin <branch>` |
| **El commit anterior ya compila, pasa tests y tiene alcance cerrado** | **`NUEVO COMMIT`** | `git commit -m "..."`<br>`git push origin <branch>` |

---

## Reglas Críticas de Seguridad y Entorno

1. **Sintaxis PowerShell (Windows):**
   - **NUNCA** usar operadores `&&` para encadenar comandos de Git. En PowerShell 5.1 falla con `ParserError`.
   - Ejecutar comandos secuenciales con `;` o como comandos separados (ej: `git add <files>; git commit -m "..."`).
2. **Regla de Oro de `--force-with-lease`:**
   - **NUNCA** hacer `push -f` a secas (ciego). Siempre usar `--force-with-lease`.
   - **NUNCA** hacer force push sobre ramas principales (`main`, `master`, `develop`).
   - Solo usar `--force-with-lease` sobre ramas de feature/fix personales activas para mantener commits atómicos en PRs abiertos.

---

## Workflow y Acciones

### 1. Detectar Repositorio y Estado
- Verificar si es git repo: `git rev-parse --is-inside-work-tree`
- Detectar rama default: `main` o `master`
- Rama actual y estado: `git status -s`

---

### 2. Acción 1: Crear Rama (`branch`)

Cuando el usuario pide crear una rama o empezar una tarea:

1. **Determinar Nombre Semántico:**
   - Formato estricto: `{tipo}/{descripcion-kebab-case}` (en inglés técnico).
   - Tipos válidos: `feat`, `fix`, `refactor`, `perf`, `test`, `chore`, `docs`, `style`.
   - Ejemplos: `feat/market-compact-view`, `fix/header-sticky-alignment`, `refactor/auth-context`, `perf/memoize-odds-selector`.
   - Si el usuario proporciona un número de issue (ej: #42), puede usarse `feat/42-market-view` o `42-market-view`.
2. **Stash preventivo si hay cambios sucios:**
   - Si `git status -s` tiene cambios: `git stash push -u -m "Auto-stashed before branch creation"` e informar al usuario.
3. **Podar ramas locales huérfanas y sincronizar desde `origin`:**
   - **NUNCA** hacer checkout a `main` local ni crear ramas desde la rama activa actual.
   - Ejecutar:
     ```powershell
     git fetch --prune origin; git branch -vv | Where-Object { $_ -match '\[origin/.*: gone\]' } | ForEach-Object { $b = ($_.Trim() -split '\s+')[0]; if ($b -and $b -ne '*') { git branch -D $b } }; git checkout -B {tipo}/{descripcion-kebab-case} origin/{defaultBranch}
     ```
   - Esto limpia automáticamente cualquier rama local cuyo remoto fue eliminado (post Squash & Merge) y garantiza que la nueva rama nace exactamente sobre el último commit de remoto sin heredar commits huérfanos.
4. **Confirmación concisa:**
   - "Ramas locales huérfanas podadas y rama `{branch}` creada directamente desde `origin/{defaultBranch}` actualizado."

---

### 3. Acción 2: Push Inteligente y Seguro (`push`)

#### Paso 1: Precondición de Calidad (Quality Gate Universal)
- **Nunca empujar código roto:** Verificar que el proyecto compile y pase linter/tests locales según el stack del proyecto (ej: TypeScript, Ruff, Cargo, Go test) antes de tocar el remoto.
- Si alguna validación falla, **detener el push**, reportar el error y corregirlo.

#### Paso 2: Evaluar Health Gates y Determinar Modo de Push
- Evaluar archivos modificados (excluyendo lockfiles y tipos generados).
- Si es una corrección o ajuste iterativo del commit anterior: **Modo B (Amend)**.
- Si es una capa modular nueva y el PR tiene < 4 commits: **Modo A (Nuevo Commit)**.

- **Modo A: Push Normal / Inicial (Nueva rama o commit nuevo explícito)**
  - Agregar archivos y commitear: `git add <archivos>; git commit -m "{tipo}({alcance}): {descripcion}"`
  - Empujar la rama a remoto: `git push -u origin {currentBranch}`
  - **Crear siempre el Draft PR inmediatamente tras el primer push**:
    `gh pr create --draft --title "{commit_type}({scope}): {desc}" --body "## Summary\n- ..."`
  - **Retornar el enlace directo al PR en la respuesta al usuario**.

- **Modo B: Push Iterativo / Amend (`--force-with-lease`)**
  - Verificar que la rama actual NO sea `main` ni `master`.
  - Agregar archivos modificados: `git add <rutas>`
  - Enmendar el último commit: `git commit --amend --no-edit` (o con mensaje actualizado si cambió el alcance).
  - Empujar con seguridad: `git push --force-with-lease origin {currentBranch}`
  - Confirmar: "Commit enmendado y actualizado en remoto con --force-with-lease."

---

### 4. Acción 3: Sincronizar y Podar Ramas Locales (`sync`)

Cuando el usuario pide sincronizar, podar ramas huérfanas, o actualizar la rama base ("sync", "sincronizar", "limpiar ramas", "podar ramas", "actualizar master/main"):

1. **Prevenir pérdida de trabajo:**
   - Si `git status -s` tiene cambios sucios: `git stash push -u -m "Auto-stashed before sync"`.
2. **Posicionar en la rama default y actualizar:**
   - Detectar si es `main` o `master`.
   - `git checkout {defaultBranch}; git pull origin {defaultBranch}`
3. **Poda integral de ramas huérfanas y mergeadas:**
   - Ejecutar:
     ```powershell
     git fetch --prune origin; git branch -vv | Where-Object { $_ -match '\[origin/.*: gone\]' } | ForEach-Object { $b = ($_.Trim() -split '\s+')[0]; if ($b -and $b -ne '*' -and $b -ne 'master' -and $b -ne 'main') { git branch -D $b } }; git branch --merged | Where-Object { $_.Trim() -notmatch '^(\*|master$|main$|dev$|develop$)' } | ForEach-Object { $b = $_.Trim(); if ($b) { git branch -d $b } }
     ```
4. **Confirmación concisa:**
   - Informar ramas podadas y estado actual: "`{defaultBranch}` local actualizado con `origin/{defaultBranch}` y ramas locales huérfanas/mergeadas eliminadas."

---

### 5. Acción 4: Trabajo Aislado en Worktree (`worktree`)

#### Heurística Proactiva de Inferencia de Alcance Ampliado:
> **Regla de Aislamiento Universal:** Si el usuario está trabajando en una rama activa (`feat/*`, `refactor/*`) con cambios locales activos o servidor de desarrollo corriendo, y ocurre cualquiera de los siguientes eventos:
> 1. Se detecta o solicita la resolución de un **bug o hotfix** ajeno a la tarea en curso (`fix/*`).
> 2. Se identifica un cuello de botella o mejora crítica de **rendimiento / optimización** (`perf/*`).
> 3. Se requiere implementar o corregir una suite de **pruebas unitarias o de integración** (`test/*`).
> 4. Se propone un ajuste puntual de **diseño/UI/accesibilidad** o refactor de un módulo no relacionado (`refactor/*`, `style/*`).
> 
> En todos estos casos, el agente **NUNCA debe hacer stash ni cambiar de rama en el directorio activo**. Debe proponer o crear automáticamente un **Worktree** aislado.

#### Flujo de Ejecución Riguroso:
1. **Crear Worktree vinculado a nueva rama limpia:**
   - Determinar directorio hermano: `../<repo>-<tipo>-<sufijo>` (ej: `../fixed-frontend-perf-odds` o `../fixed-frontend-fix-calc`).
   - Sincronizar referencias y crear worktree desde `origin/{defaultBranch}`:
     ```powershell
     git fetch origin; git worktree add -b {tipo}/{descripcion-kebab-case} ../{repo}-{tipo}-{sufijo} origin/{defaultBranch}
     ```
2. **Ejecutar la tarea en el Worktree:**
   - Realizar modificaciones (código, tests, optimizaciones).
   - Validar que compile y pasen las pruebas dentro del directorio del worktree.
3. **Commit, Push Inicial y Apertura de PR (Draft o Ready):**
   - **Paso A:** Primer commit con Conventional Commits:
     ```powershell
     git -C ../{repo}-{tipo}-{sufijo} add <archivos>; git -C ../{repo}-{tipo}-{sufijo} commit -m "{tipo}({scope}): {description}"
     ```
   - **Paso B:** Push de la rama a GitHub:
     ```powershell
     git -C ../{repo}-{tipo}-{sufijo} push -u origin {tipo}/{descripcion-kebab-case}
     ```
   - **Paso C:** Creación del PR en GitHub (Draft si es iterativo, normal si ya está listo):
     ```powershell
     gh pr create --repo <owner/repo> --head {tipo}/{descripcion-kebab-case} --base {defaultBranch} --title "{tipo}({scope}): {description}" --body "## Summary\n- ..."
     ```
4. **Desmantelar y limpiar el Worktree:**
   - Una vez la rama está subida y el PR abierto en GitHub:
     ```powershell
     git worktree remove ../{repo}-{tipo}-{sufijo}
     ```
5. **Reportar al usuario:**
   - Entregar el enlace al PR listo para revisión/merge y confirmar que su espacio de trabajo original se mantuvo 100% inalterado.

---

### 6. Acción 5: Sincronizar Rama Activa (`rebase`)

Cuando la rama principal remota (`origin/master` o `origin/main`) ha recibido nuevos merges (bugfixes, tests o mejoras de agentes o compañeros) y se requiere poner al día la rama activa actual:

1. **Asegurar cambios locales:**
   - Si existen cambios sin commitear en la rama actual, realizar un commit semántico antes de rebasear:
     ```powershell
     git add <archivos>; git commit -m "feat(scope): intermediate progress"
     ```
2. **Ejecutar Rebase contra el remoto actualizado:**
   ```powershell
   git fetch origin; git rebase origin/{defaultBranch}
   ```
3. **Resolución de conflictos (si ocurren):**
   - El agente analiza los conflictos, preserva la lógica de ambos lados, agrega los archivos resueltos (`git add`) y continúa con `git rebase --continue`.
4. **Actualizar el remoto de forma segura:**
   - Como el rebase reescribe los hashes de los commits sobre la nueva base, sincronizar la rama remota con `--force-with-lease`:
     ```powershell
     git push --force-with-lease origin {currentBranch}
     ```
5. **Confirmar:**
   - "Rama `{currentBranch}` rebaseada exitosamente sobre el último `origin/{defaultBranch}` y actualizada en remoto."

---

## Resumen de Comandos PowerShell

```powershell
# 1. Crear rama limpia con poda automática de huérfanas
git fetch --prune origin; git branch -vv | Where-Object { $_ -match '\[origin/.*: gone\]' } | ForEach-Object { $b = ($_.Trim() -split '\s+')[0]; if ($b -and $b -ne '*') { git branch -D $b } }; git checkout -B feat/nueva-feature origin/master

# 2. Sincronizar master y podar ramas locales huérfanas/mergeadas
git checkout master; git pull origin master; git fetch --prune origin; git branch -vv | Where-Object { $_ -match '\[origin/.*: gone\]' } | ForEach-Object { $b = ($_.Trim() -split '\s+')[0]; if ($b -and $b -ne '*' -and $b -ne 'master' -and $b -ne 'main') { git branch -D $b } }; git branch --merged | Where-Object { $_.Trim() -notmatch '^(\*|master$|main$|dev$|develop$)' } | ForEach-Object { $b = $_.Trim(); if ($b) { git branch -d $b } }

# 3. Trabajo paralelo aislado con Worktree (Bugfix, Perf, Test o Refactor aislado)
git fetch origin; git worktree add -b fix/hotfix-pnl ../fixed-frontend-hotfix origin/master
# ... realizar cambios, test y commit en ../fixed-frontend-hotfix ...
git -C ../fixed-frontend-hotfix add <archivos>; git -C ../fixed-frontend-hotfix commit -m "fix(pnl): correct calculation"
git -C ../fixed-frontend-hotfix push -u origin fix/hotfix-pnl
gh pr create --head fix/hotfix-pnl --base master --title "fix(pnl): correct calculation" --body "..."
git worktree remove ../fixed-frontend-hotfix

# 4. Rebase de rama activa sobre master actualizado
git fetch origin; git rebase origin/master; git push --force-with-lease origin <currentBranch>

# 5. Push Inicial + Draft PR
git add <archivos>; git commit -m "feat(scope): description"; git push -u origin <branch>
gh pr create --draft --title "feat(scope): description" --body "## Summary`n- ..."

# 6. Push Iterativo Seguro (amend)
git add <archivos>; git commit --amend --no-edit; git push --force-with-lease origin <branch>
```
