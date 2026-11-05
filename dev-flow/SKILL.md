---
name: dev-flow
description: Manages Git branch creation, safe code pushes with zero bloat, local sync/pruning, isolated parallel worktrees, feature rebasing, and remote CI verification. Automates clean feature/fix branches from updated main, toolchain quality gates (lint/format/typecheck), Draft PR creation, atomic iterative commits via commit --amend and git push --force-with-lease, git worktree isolation for parallel bugfixes/tasks without interrupting active development, clean git rebase workflows against advanced origin/master, active PR lifecycle monitoring (auto-detect open PRs, recommend merge or branch stacking when PR commits/lines exceed limits), GitHub CLI CI watch (`gh pr checks --watch`) to prevent delivering failing builds, and automated transition from Draft to Ready for Review (`gh pr ready`) upon task objective completion while enforcing scope-lock against feature bloat. Enforces professional engineering health gates (atomic commits, lines/files thresholds, Conventional Commits). Use whenever the user asks to create a branch ("crear rama", "nueva feature", "empezar tarea"), push code ("push", "push seguro", "actualizar PR", "hacer force push", "enmendar commit"), synchronize/clean local branches ("sync", "sincronizar", "limpiar ramas", "podar ramas", "actualizar master", "prune"), work in parallel or isolate a task ("worktree", "en paralelo", "tarea aislada", "hotfix sin tocar rama actual", "aislar refactor", "aislar optimizacion", "aislar tests"), bring latest master changes into an active branch ("rebase", "actualizar mi rama con master", "poner al día rama"), or monitor CI checks ("verificar CI", "checks", "vigilar build", "listo para review", "pasar a ready").
---

# dev-flow

Skill de automatización de Git enfocado en máxima productividad, historial limpio y estándares de ingeniería profesional (Google Engineering Practices) en Windows (PowerShell).
100% autocontenido, agnóstico a cualquier lenguaje/stack, sin dependencias de MCPs externos y con **5 acciones fundamentales** y **gestión proactiva del ciclo de vida de Pull Requests**:

1. **`branch` (Crear rama limpia):** Crea ramas estandarizadas (`feat/*`, `fix/*`, `chore/*`, etc.) directamente desde `origin/master` (o `origin/main`), podando ramas locales huérfanas y detectando PRs abiertos en conflicto.
2. **`push` (Push inteligente, seguro y verificado por CI):** Valida localmente, empuja la rama (creando Draft PR o enmendando con `--force-with-lease`), monitorea los límites de commits/líneas recomendando merge cuando madura, vigila con GitHub CLI (`gh pr checks --watch`) y **marca el PR como listo para revisión (`gh pr ready`)** cuando se cumple el objetivo de la tarea.
3. **`sync` (Sincronizar y podar ramas locales):** Cambia a la rama principal (`main`/`master`), actualiza contra `origin` (`git pull`) y elimina todas las ramas locales mergeadas o cuyo remoto fue borrado (`[origin/...: gone]`).
4. **`worktree` (Aislamiento para tareas paralelas e independientes):** Resuelve bugs, hotfixes, optimizaciones de rendimiento (`perf`), mejoras de cobertura de tests (`test`), refactors aislados (`refactor`) o auditorías de UI en una carpeta física paralela sin tocar la rama activa, sin hacer `stash`, sin interrumpir el servidor local de desarrollo (`pnpm start`), abriendo el PR, vigilando su CI y limpiando el worktree al finalizar.
5. **`rebase` (Sincronizar rama activa con master avanzado):** Pone al día la rama de trabajo actual sobre el último `origin/master` manteniendo un historial 100% lineal y actualizando el remoto con `--force-with-lease`.

---

## 🚦 Protocolo Proactivo de Monitoreo de PRs (PR Lifecycle Sentinel)

El agente **SIEMPRE debe inspeccionar el estado de los PRs abiertos** (`gh pr list --state open`) al iniciar una sesión, al crear una rama o al evaluar un push:

### Regla 1: Detección de PR Maduro para Merge (Bloat Prevention)
Si la rama actual ya tiene un PR abierto asociado y se detecta alguna de estas condiciones:
- Acumula **más de 3 a 4 commits lógicos**.
- La suma neta de cambios de autoría supera **250 - 300 líneas de código**.
- El CI remoto ya pasó en verde (✅) y el alcance de la tarea original está cerrado.

➡️ **Acción del Agente:** El agente debe **detenerse y recomendar formalmente el merge antes de seguir agregando más features**:
> *"⚠️ Tu PR #{num} (`{branch}`) ya tiene {n} commits y {lineas} líneas con CI en verde. Para mantener la mantenibilidad y bisectabilidad según Google Engineering Standards, recomiendo mergear este PR a master ahora antes de continuar. ¿Deseas hacer merge o encadenar una nueva rama (Stacked PR) para los siguientes cambios?"*

### Regla 2: Prevención de Ramas Huérfanas con PR Pendiente
Si el usuario pide crear una nueva rama (`branch` o `worktree`) pero ya existe un PR abierto en su rama anterior que está listo y con checks verdes:
➡️ **Acción del Agente:** Advertir amablemente:
> *"💡 Tienes el PR #{num} (`{branch_anterior}`) abierto y con checks pasando. Te sugiero mergearlo a master antes de crear esta nueva rama para que tu nueva feature nazca con los cambios previos integrados. Si prefieres dejarlo abierto, crearemos la nueva rama directamente desde el último origin/master."*

### Regla 3: Transición Automática a "Ready for Review" y Blindaje contra Scope Creep
- **Culminación del objetivo de la tarea:** Una vez que el agente implementa la meta acordada para el PR, pasan todas las pruebas locales y el CI remoto está en verde (✅), el agente **debe ejecutar automáticamente**:
  ```powershell
  gh pr ready {currentBranch}
  ```
- **El Merge es potestad exclusiva del usuario:** El agente **NUNCA ejecuta el merge automáticamente por su cuenta**. Su responsabilidad termina entregando el PR en estado `Ready for review` con el enlace directo para que el usuario (Tech Lead / Revisor) lo inspeccione y apruebe.
- **Distinción estricta entre Feedback de Revisión vs Nueva Feature:**
  - **Feedback de revisión:** Si el usuario encuentra errores, desalineaciones visuales o fallos en el comportamiento pactado para *ese* PR, el agente corrige el código en ese mismo PR vía `commit --amend` o commit específico, empuja con `--force-with-lease` y vigila nuevamente el CI.
  - **Nueva Feature / Idea:** Si el usuario solicita nuevas capacidades, páginas o comportamientos que exceden la meta original del PR, el agente **debe detener el impulso de ensuciar el PR** y responder:
    > *"Esa solicitud es una nueva funcionalidad que expande el alcance de este PR. Como el PR #{num} ya cumplió su objetivo original y tiene los checks en verde, sugiero mergearlo a master ahora para cerrar el ciclo limpiamente y abrir una nueva rama desde master para tu nueva idea."*

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
- Detectar PRs activos: `gh pr list --state open --limit 5`

---

### 2. Acción 1: Crear Rama (`branch`)

Cuando el usuario pide crear una rama o empezar una tarea:

1. **Determinar Nombre Semántico:**
   - Formato estricto: `{tipo}/{descripcion-kebab-case}` (en inglés técnico).
   - Tipos válidos: `feat`, `fix`, `refactor`, `perf`, `test`, `chore`, `docs`, `style`.
   - Ejemplos: `feat/market-compact-view`, `fix/header-sticky-alignment`, `refactor/auth-context`, `perf/memoize-odds-selector`.
   - Si el usuario proporciona un número de issue (ej: #42), puede usarse `feat/42-market-view` o `42-market-view`.
2. **Verificar PRs activos y advertir si corresponde (Regla 2 del Sentinel):**
   - Si la rama actual tiene un PR abierto con checks verdes, sugerir merge antes de abrir una rama no relacionada.
3. **Stash preventivo si hay cambios sucios:**
   - Si `git status -s` tiene cambios: `git stash push -u -m "Auto-stashed before branch creation"` e informar al usuario.
4. **Podar ramas locales huérfanas y sincronizar desde `origin`:**
   - **NUNCA** hacer checkout a `main` local ni crear ramas desde la rama activa actual.
   - Ejecutar:
     ```powershell
     git fetch --prune origin; git branch -vv | Where-Object { $_ -match '\[origin/.*: gone\]' } | ForEach-Object { $b = ($_.Trim() -split '\s+')[0]; if ($b -and $b -ne '*') { git branch -D $b } }; git checkout -B {tipo}/{descripcion-kebab-case} origin/{defaultBranch}
     ```
5. **Confirmación concisa:**
   - "Ramas locales huérfanas podadas y rama `{branch}` creada directamente desde `origin/{defaultBranch}` actualizado."

---

### 3. Acción 2: Push Inteligente y Seguro (`push`)

#### Paso 1: Precondición de Calidad Local (Quality Gate Universal)
- **Nunca empujar código roto:** Verificar que el proyecto compile y pase linter/tests locales según el stack del proyecto (ej: TypeScript, Ruff, Cargo, Go test) antes de tocar el remoto.
- Si alguna validación falla, **detener el push**, reportar el error y corregirlo.

#### Paso 2: Evaluar Health Gates y Estado del PR
- Evaluar archivos modificados (excluyendo lockfiles y tipos generados).
- **Inspeccionar madurez del PR (Regla 1 del Sentinel):** Si agregar este commit sobrepasa los límites de 3-4 commits o 300 líneas, recomendar merge antes de continuar.
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

#### Paso 3: Vigilancia Remota de CI (GitHub Actions CI Watch)
> **Regla de Entrega Verificada:** El agente **NUNCA debe dar por completada una tarea ni entregar un PR como "listo" si el CI remoto falla**.
- Tras el push inicial o iterativo, verificar el estado de los checks remotos con:
  ```powershell
  gh pr checks {currentBranch} --watch
  ```
- Si algún check falla (rojo ❌):
  1. Inspeccionar el log del runner remoto: `gh run view --log-failed`
  2. Identificar el fallo (diferencia de entorno, tests de integración, linters remotos).
  3. Corregir el código localmente, compilar y ejecutar tests de nuevo.
  4. Enmendar el commit y volver a empujar con `git push --force-with-lease origin {currentBranch}`.
  5. Volver a vigilar hasta que todos los checks estén en verde (✅).

#### Paso 4: Cierre de Meta y Transición a "Ready for Review"
- Cuando los checks remotos pasen en verde y el objetivo funcional pactado esté completo:
  ```powershell
  gh pr ready {currentBranch}
  ```
- Entregar el enlace del PR al usuario destacando que está en **Ready for review** para su inspección y aprobación final.

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
   - **Paso C:** Creación del PR en GitHub en modo Draft:
     ```powershell
     gh pr create --repo <owner/repo> --head {tipo}/{descripcion-kebab-case} --base {defaultBranch} --draft --title "{tipo}({scope}): {description}" --body "## Summary\n- ..."
     ```
   - **Paso D (Vigilancia remota):** Verificar checks del PR:
     ```powershell
     gh pr checks {tipo}/{descripcion-kebab-case} --watch
     ```
   - **Paso E (Cierre de Meta):** Marcar como Ready for review:
     ```powershell
     gh pr ready {tipo}/{descripcion-kebab-case}
     ```
4. **Desmantelar y limpiar el Worktree:**
   - Una vez la rama está subida, el PR en Ready for review y los checks en verde:
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
# 1. Detectar PRs activos al inicio
gh pr list --state open --limit 5

# 2. Crear rama limpia con poda automática de huérfanas
git fetch --prune origin; git branch -vv | Where-Object { $_ -match '\[origin/.*: gone\]' } | ForEach-Object { $b = ($_.Trim() -split '\s+')[0]; if ($b -and $b -ne '*') { git branch -D $b } }; git checkout -B feat/nueva-feature origin/master

# 3. Sincronizar master y podar ramas locales huérfanas/mergeadas
git checkout master; git pull origin master; git fetch --prune origin; git branch -vv | Where-Object { $_ -match '\[origin/.*: gone\]' } | ForEach-Object { $b = ($_.Trim() -split '\s+')[0]; if ($b -and $b -ne '*' -and $b -ne 'master' -and $b -ne 'main') { git branch -D $b } }; git branch --merged | Where-Object { $_.Trim() -notmatch '^(\*|master$|main$|dev$|develop$)' } | ForEach-Object { $b = $_.Trim(); if ($b) { git branch -d $b } }

# 4. Trabajo paralelo aislado con Worktree (Bugfix, Perf, Test o Refactor aislado)
git fetch origin; git worktree add -b fix/hotfix-pnl ../fixed-frontend-hotfix origin/master
# ... realizar cambios, test y commit en ../fixed-frontend-hotfix ...
git -C ../fixed-frontend-hotfix add <archivos>; git -C ../fixed-frontend-hotfix commit -m "fix(pnl): correct calculation"
git -C ../fixed-frontend-hotfix push -u origin fix/hotfix-pnl
gh pr create --head fix/hotfix-pnl --base master --draft --title "fix(pnl): correct calculation" --body "..."
gh pr checks fix/hotfix-pnl --watch
gh pr ready fix/hotfix-pnl
git worktree remove ../fixed-frontend-hotfix

# 5. Rebase de rama activa sobre master actualizado
git fetch origin; git rebase origin/master; git push --force-with-lease origin <currentBranch>

# 6. Push Inicial + Draft PR + Vigilancia CI + Ready
git add <archivos>; git commit -m "feat(scope): description"; git push -u origin <branch>
gh pr create --draft --title "feat(scope): description" --body "## Summary`n- ..."
gh pr checks <branch> --watch
gh pr ready <branch>

# 7. Push Iterativo Seguro (amend) + Vigilancia CI
git add <archivos>; git commit --amend --no-edit; git push --force-with-lease origin <branch>
gh pr checks <branch> --watch
```
