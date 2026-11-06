# Triage de CI: ¿Fallo de Código o de Infraestructura?

Usa esta reference **cada vez que se vigile el CI de un PR** (push inicial, amend, worktree o paso a Ready for review).

> **Regla de Oro:** Nunca modificar código, reescribir commits ni "adivinar" un fix cuando el CI no llegó a ejecutar jobs. Un `startup_failure`, un workflow que no se dispara o un `log not found` son **falta de evidencia**, no un fallo de código.

---

## 1. Fijar el SHA objetivo

Antes de mirar ningún check, confirmar qué commit se está validando:

```powershell
$sha = git rev-parse HEAD
git rev-parse --abbrev-ref HEAD
gh pr view {currentBranch} --json number,headRefOid,headRefName,url,isDraft
```

- El `headRefOid` del PR **debe coincidir** con `$sha`. Si no coincide, el push aún no se propagó o el PR apunta a otra rama: no vigilar ese run.
- Guardar `$sha` para todas las consultas siguientes. Un run verde de un SHA anterior **no valida** el HEAD actual.

---

## 2. Recolección de evidencia (obligatoria)

### 2.1 Runs reales del repo para ese SHA

```powershell
gh run list --repo {owner}/{repo} --commit $sha --limit 20 `
  --json databaseId,name,workflowName,event,status,conclusion,headSha,createdAt,url
```

- `--commit` filtra por SHA; no confiar en `gh run list` sin filtro (puede devolver runs de otras ramas/SHAs).
- Si la lista está vacía → **el workflow no se disparó**: ir a la sección 4.

### 2.2 Checks publicados en el PR (solo como complemento)

```powershell
gh pr checks {currentBranch} --json name,state,bucket,link
```

- `gh pr checks` **no es fuente de verdad**: puede mostrar solo checks de terceros (Vercel, Netlify, Codecov, bots) y aun así parecer "todo verde".
- `no checks reported` con exit code 1 **no** es un fallo de código.
- Verificar qué workflows pertenecen al repo:

```powershell
gh workflow list --repo {owner}/{repo} --all
```

Solo un check originado por un workflow del propio repo cuenta como verificación de código.

### 2.3 Detalle del run sospechoso

```powershell
gh run view {runId} --repo {owner}/{repo} `
  --json status,conclusion,jobs,event,headSha,createdAt,updatedAt,url
gh api repos/{owner}/{repo}/actions/runs/{runId}/jobs
gh run view {runId} --repo {owner}/{repo} --log-failed
```

Interpretación de los logs:

- **`log not found`** → el run no ejecutó jobs (típico de `startup_failure` o run cancelado antes de arrancar). **No es un error de código.**
- **Logs con stack trace, test fallido, error de lint/compilación** → fallo de código real.

---

## 3. Taxonomía de estados

Clasificar **siempre** en una de estas cuatro clases antes de actuar:

| Clase | Evidencia | Acción |
| :--- | :--- | :--- |
| **VERDE** | Al menos un run de un workflow del repo para `$sha` con `conclusion: success`. Sin runs en `failure`, `cancelled`, `timed_out`, `startup_failure` ni `action_required`. | Continuar: marcar Ready for review. |
| **ROJO_CÓDIGO** | Run del repo que **sí ejecutó jobs** (`jobs > 0`) y falló en un paso real (test, lint, build, typecheck). `--log-failed` muestra el error reproducible. | Diagnosticar con logs, corregir código/tests, repetir quality gate local, `amend` y `--force-with-lease`. |
| **INFRA_DESCONOCIDO** | `startup_failure`, run con **0 jobs**, `log not found`, workflow **no disparado** para `$sha`, run atascado en `queued`/`in_progress` más de ~20-30 min, HTTP 403/429, Actions deshabilitado, límite de spending/billing, error de permisos/OIDC o política de organización. | **No tocar código.** Verificar localmente, reintentar de forma acotada y reportar la evidencia al usuario. |
| **SIN_CI_CONFIGURADO** | `gh workflow list --repo {owner}/{repo} --all` no devuelve ningún workflow: el repo **no tiene CI**, no es un fallo ni un verde. | No tocar código. Ejecutar el quality gate local, entregar el PR como **Draft** y reportar que no existe CI. Marcar Ready solo con confirmación explícita del usuario. |

> **Nunca** clasificar como `ROJO_CÓDIGO` un fallo sin logs de un job ejecutado.
> **Nunca** clasificar como `VERDE` la ausencia de checks.

---

## 4. Casos de infraestructura y cómo confirmarlos

### 4.1 `startup_failure` (0 jobs, ~0-2 s, sin logs)

Síntomas: el run aparece creado y termina casi instantáneamente con `conclusion: startup_failure`, `jobs: []` y `--log-failed` devuelve `log not found`.

Detalle de la API: en este estado los campos `name`/`workflowName` pueden venir **vacíos** y el run puede reportar `path: "BuildFailed"`. Eso **no** significa que el workflow no exista; complementar con `gh api repos/{owner}/{repo}/actions/runs/{runId}` y con `gh workflow list`.

Causas habituales (de más a menos frecuente):

1. **Límite de minutos / spending de GitHub Actions agotado** o método de pago inválido.
2. **Actions deshabilitado** para el repo o para la organización.
3. Workflow inválido a nivel de parseo (YAML, `uses` inexistente, expresión inválida).
4. Runner solicitado no disponible (`runs-on` inválido o sin acceso).
5. Permisos/entitlement: workflow reutilizable, OIDC, environment protection o política de organización.

**Discriminador código vs cuenta:** si un workflow trivial (por ejemplo un `on: workflow_dispatch` con `run: echo ok`) también termina en `startup_failure`, el problema es **de cuenta/organización/infra**, no del código del PR.

```powershell
# Estado del billing (requiere token con scope 'user')
gh auth status
gh api /users/{user}/settings/billing/actions

# Permisos de Actions del repo
gh api repos/{owner}/{repo}/actions/permissions
gh api repos/{owner}/{repo}/actions/permissions/workflow
```

Si la API de billing devuelve 403/404 por falta de scope `user`, **no asumir** la causa: reportar que no se pudo verificar y adjuntar el resto de evidencia.

### 4.2 Workflow no disparado

Si `gh run list --commit $sha` no devuelve ningún run:

- Revisar triggers en `.github/workflows/*.yml`: `on.push.branches`, `paths`, `paths-ignore`, `types` de `pull_request`.
- Confirmar que el push llegó a la rama remota correcta (`git ls-remote origin {currentBranch}` debe devolver `$sha`).
- Revisar si el workflow requiere aprobación (PR desde fork) o si está deshabilitado (`gh workflow list --all` muestra `disabled_manually`).
- Si el workflow no aplica a esa rama/paths, **no hay verificación**: reportarlo; no asumir verde.

### 4.2.1 Repo sin CI configurado

Si `gh workflow list --repo {owner}/{repo} --all` devuelve una lista vacía, el repo **no tiene GitHub Actions configurado**. No es un error de infraestructura ni un CI verde:

- No crear workflows improvisados dentro de un PR de feature (scope creep).
- Ejecutar el quality gate local completo y reportar explícitamente "sin CI configurado".
- Entregar el PR como **Draft**; marcar Ready solo si el usuario lo confirma.

### 4.3 Run atascado o cola infinita

- `queued`/`in_progress` sin cambios durante ~20-30 minutos → tratar como `INFRA_DESCONOCIDO`.
- Reintentar de forma acotada (máximo 2-3 intentos, con espera entre ellos):

```powershell
gh run rerun {runId} --repo {owner}/{repo}
```

- No introducir commits vacíos ni cambios cosméticos solo para "reintentar" el CI.

---

## 5. Reintentos y espera acotada

- `gh pr checks --watch` puede salir de inmediato si no hay checks o quedarse esperando indefinidamente. **No usarlo como única fuente ni sin límite.**
- Espera recomendada: `gh pr checks {currentBranch} --watch --interval 30`, con un máximo de ~20-30 minutos.
- Después de cada iteración, volver a enumerar los runs **por SHA** (sección 2.1) y reclasificar.
- Si el estado no cambia tras el límite → `INFRA_DESCONOCIDO` y escalar al usuario con la evidencia recogida.

---

## 6. Reglas anti-falsos-positivos

- ❌ "Todo verde" basado solo en `gh pr checks` (puede haber únicamente Vercel/bots).
- ❌ "No hay checks" interpretado como éxito.
- ❌ "El PR es `MERGEABLE`" interpretado como CI aprobado.
- ❌ Run verde de un SHA anterior como validación del HEAD actual.
- ❌ `log not found` interpretado como fallo de código.
- ❌ `name`/`workflowName` vacíos + `path: "BuildFailed"` interpretados como "el workflow no existe" (es un `startup_failure`).
- ❌ Modificar código o hacer `amend` para "forzar" que un workflow de infra arranque.
- ❌ Marcar `gh pr ready` cuando la clase es `INFRA_DESCONOCIDO` o `SIN_CI_CONFIGURADO`, salvo autorización explícita del usuario (en ese caso, entregar como **Draft** y adjuntar la evidencia).

---

## 7. Plantilla de reporte al usuario

```text
CI: {VERDE | ROJO_CÓDIGO | INFRA_DESCONOCIDO | SIN_CI_CONFIGURADO}
SHA validado: {sha}
PR headRefOid: {headRefOid} (coincide: {sí/no})
Workflows del repo: {nombres}
Runs para el SHA: {runId} · {workflow} · {status}/{conclusion} · jobs={n}
Checks externos ignorados: {Vercel/Netlify/...}
Evidencia: {log-failed | 0 jobs | log not found | workflow no disparado | billing/permisos}
Acción tomada: {corregir código + amend | reintentar | reportar bloqueo}
```
