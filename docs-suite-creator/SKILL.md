---
name: docs-suite-creator
description: Act as an Expert Software Architect and Tech Lead to analyze a project context and generate or update a complete technical documentation suite of 6 core architecture files (ARCHITECTURE.md, CONTRACTS.md, DATABASE.md, MODEL.md/LOGIC.md, ROADMAP.md, SCOPE.md) in docs/. Use whenever the user requests technical documentation, wants to document architecture, contracts, database models, business logic, roadmap, or MVP scope.
---

# 🏗️ Documentation Suite Creator

This skill enables the agent to act as an Expert Software Architect and Tech Lead to structure, analyze, and generate a cohesive, production-grade technical documentation suite of exactly 6 Markdown (`.md`) files in `docs/`.

---

## 🚀 Workflow

### Step 1: Context Discovery & Architecture Analysis
Do not ask the user basic questions that can be derived from code. Inspect the repository directly:
1. Read manifest files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.) to identify libraries, frameworks, ORMs, and runtimes.
2. Inspect directory structure, API routes, database models, and business logic.
3. If critical domain decisions or business requirements are ambiguous, ask concise, targeted questions.

### Step 2: Generation or Update of the 6 Documentation Files
Load the reference templates from `references/` and generate the documentation in `docs/`:

| File | Template Reference | Content Focus |
|---|---|---|
| `docs/ARCHITECTURE.md` | `references/architecture.md` | System topology (Mermaid), E2E data flows, components, deployment |
| `docs/CONTRACTS.md` | `references/contracts.md` | Auth mechanisms, HTTP endpoints, payloads, status codes, security/RLS |
| `docs/DATABASE.md` | `references/database.md` | Entity-Relationship diagram (Mermaid `erDiagram`), data dictionary |
| `docs/MODEL.md` (or `LOGIC.md`) | `references/model.md` | Core business logic, mathematical algorithms, inference flows |
| `docs/ROADMAP.md` | `references/roadmap.md` | Visual timeline (Mermaid `gantt`), phases (MVP, Beta, Scale) |
| `docs/SCOPE.md` | `references/scope.md` | Feature control matrix, strict exclusions, Definition of Done (DoD) |

*Language: Write in technical Spanish by default unless the user requests English.*

### Step 3: Verification & Version Control
1. **Verify relative links:** Ensure cross-references in `## 🔗 Referencias` link correctly between files in `docs/` using relative paths (never absolute `file:///`).
2. **Commit safely:** Stage modified or created docs files:
   ```powershell
   git add docs/
   git commit -m "docs(architecture): update technical documentation suite"
   ```
3. **Push via `dev-flow`:** Delegate pushing to the `dev-flow` skill (`push`) to enforce health gates and respect branch policies. Never push directly to protected branches.

---

## 📋 Strict Style and Terminology Rules

1. **Cero Ambiguidad (MVP vs Post-MVP):**
   - Do NOT use the word "Beta" in `ARCHITECTURE.md`, `CONTRACTS.md`, `DATABASE.md`, `MODEL.md`/`LOGIC.md`, or `SCOPE.md`.
   - Classify all features, code, and tables using a strict binary classification: **"MVP"** (current development scope) or **"Alcance Futuro / Post-MVP"** (excluded scope).
2. **The "Beta" Exception:**
   - The word "Beta" (Private or Public) is ONLY allowed in `ROADMAP.md` to describe the release strategy to users. It must never be used to define code sprints or MVP deliverables.
3. **Language & Aesthetics:**
   - Direct, technical language.
   - Start the main heading (`#`) of each document with a single representative emoji (e.g., `# 🏗️ Arquitectura Técnica`).
4. **Diagrams and Tables:**
   - Use `mermaid` blocks for system architectures, flowcharts, Gantt charts, and ERDs. No external static image links.
   - Use Markdown tables for data dictionaries and feature scope matrices.
5. **Cross References:**
   - Every file must end with a `## 🔗 Referencias` section containing relative links to the other files in the suite.
6. **Architectural Decisions:**
   - Use blockquotes (`> **Decisión:** ...`) to explain critical technical decisions, trade-offs, and justifications.
