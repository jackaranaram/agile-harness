---
name: dev-flow
description: Handles the full Git lifecycle — creating branches and pushing code safely. Integrates with agile-mcp-server MCP to create Historias de Usuario (HU) and branches in one step. Automates branch creation following GitHub Flow (default), TBD, or Git Flow conventions. Also manages safe push with conflict validation (dry-run merge local), toolchain detection (lint/format/test), and optional PR creation. Use this skill whenever the user asks to "crear HU", "crear branch para HU", "empezar a trabajar en una historia", or wants to push code ("push seguro", "validar antes de push", "crear PR"). When talking about features, bugs, or tasks, prefer using this skill to create HUs first and then branches. Handles GitHub Flow (branches cortas, PR + review — default), TBD (Google/Meta/Netflix), and Git Flow (Linux Kernel/Hashicorp).
---

# dev-flow

This skill manages the complete Git lifecycle for the project. It has three modes:

- **Crear HU + branch** — crea una Historia de Usuario via MCP y luego la rama para implementarla
- **Branch desde HU existente** — obtiene los detalles de una HU existente via MCP y crea la rama
- **Listo para Review** — valida conflictos, ejecuta pruebas, pushea cambios y marca el PR como listo para revisión

---

## Workflow

### 1. Analyze the Repository

Do not ask the user. Figure it out:

- Is this a git repo? (`git rev-parse --is-inside-work-tree`)
- Default branch: try `main`, then `master` (`git branch --list main`, `git branch --list master`)
- Does `develop` exist? (`git branch --list develop`)
- Current branch name and naming pattern: issue refs like `42-*`? short kebab like `feat/*`? `feature/*`?
- Remote configured? (`git remote -v`)

### 2. Detect agile-mcp-server MCP

Check if MCP agile-mcp-server tools are available in the environment:

- Look for tools named `create_epic`, `fetch_existing_epics`, `fetch_project_onboarding` or similar
- If available → store as `{mcpAvailable: true}` for use in menu and HU operations
- If not available → fall back to simple branch creation modes

### 3. Ask the User

Present the action menu:

```
¿Qué quieres hacer?

[ ] Crear HU + branch — crea la HU y la rama en un solo paso
[ ] Branch desde HU existente — ej: "HU-42", "issue 42"
[ ] Listo para Review — validar conflictos, testear, push y publicar PR

Describe el contexto o task:
___________________________________________________________
```

If **Crear HU + branch** or **Branch desde HU existente** is selected, present workflow selection:

```
¿Qué workflow de ramas?

[x] GitHub Flow — recomendado (PR + review, squash merge)
[ ] TBD — branches ultra cortas, feature flags
[ ] Git Flow — develop, feature/release/hotfix

Workflow por defecto: GitHub Flow (Enter para confirmar)
```

### 4. Execute by Mode

#### 4a. Crear HU + branch

1. **Descubrir Épicas y Crear HU via MCP:**
   - **IMPORTANTE:** Antes de redactar o aplicar un plan ágil de HUs, ejecutar obligatoriamente `fetch_existing_epics` para listar el roadmap y las épicas (milestones) existentes en el repositorio.
   - Preguntar al usuario si desea asociar las HUs a alguna de estas épicas existentes o si de verdad necesita crear una nueva.
   - Si se asocia a una existente: Configurar el campo `targetMilestone` en el payload de `stage_agile_plan` con el número del milestone de esa épica.
   - Usar el contexto y el plan ágil aprobado para llamar a `apply_agile_plan` (o la herramienta MCP equivalente).
   - Extraer de la respuesta: `{huId}`, `{huTitle}`, `{huType}` (feat/fix/docs/chore).

2. **Crear branch, push inicial y Draft PR:**
   - Cargar la reference del workflow seleccionado.
   - Si GitHub Flow (default):
     - `git checkout -b "{huId}-{huTitle-kebab}"` desde `main`/`master`
     - Stash previo, sync base branch.
     - Crear commit vacío inicial: `git commit --allow-empty -m "chore: start work on {huId}"`
     - Push inicial de la rama: `git push -u origin "{huId}-{huTitle-kebab}"`
     - Crear Draft PR en GitHub usando la herramienta `github/create_pull_request` con `draft: true` (o mediante el CLI local `gh pr create --draft --title "{huType}: {huTitle} ({huId})" --body "Closes #{huId}"`).

3. **Summary:** "HU-42 creada. Branch 42-add-jwt-auth creada y subida. Draft PR #15 abierto para iniciar CI/CD."

#### 4b. Branch desde HU existente

1. **Obtener HU via MCP:**
   - Extraer el ID de HU del contexto (`HU-42`, `#42`, `issue 42`, `AGILE-42` — aceptar formatos flexibles)
   - Llamar a `fetch_existing_epics` o herramienta equivalente para obtener detalles
   - Extraer `{huTitle}`, `{huType}`, `{huDescription}` de la respuesta
   - Si el MCP no encuentra la HU, informar al usuario y preguntar el título manualmente

2. **Crear branch, push inicial y Draft PR:**
   - Cargar la reference del workflow seleccionado.
   - Nombre: `{huId}-{huTitle-kebab}` (o el formato que corresponda al workflow)
   - Stash previo, sync base branch.
   - `git checkout -b "{huId}-{huTitle-kebab}"`
   - Crear commit vacío inicial: `git commit --allow-empty -m "chore: start work on {huId}"`
   - Push inicial de la rama: `git push -u origin "{huId}-{huTitle-kebab}"`
   - Crear Draft PR en GitHub usando la herramienta `github/create_pull_request` con `draft: true` (o mediante el CLI local `gh pr create --draft --title "{huType}: {huTitle} ({huId})" --body "Closes #{huId}"`).

3. **Summary:** "Branch 42-add-jwt-auth creada y subida para HU-42. Draft PR #15 abierto para iniciar CI/CD."

#### 4c. Listo para Review

- `develop` exists + current branch is `feature/*`/`bugfix/*` → target `develop`
- `develop` exists + current branch is `release/*`/`hotfix/*` → target `main`
- Otherwise → target = default branch (main/master)
- Show detected target and ask confirmation
- Load `references/ready-for-review.md` and execute

### 5. Summary

After completion, provide a brief summary:

| Mode              | Example summary                                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| Crear HU + branch | "HU-42 creada. Branch 42-add-jwt-auth creada y subida. Draft PR #15 abierto para iniciar CI/CD."      |
| Branch desde HU   | "Branch 42-add-jwt-auth creada y subida para HU-42. Draft PR #15 abierto para iniciar CI/CD."         |
| Listo para Review | "Validaciones OK. Sin conflictos locales contra main. PR #15 publicado (Ready for review)."          |
