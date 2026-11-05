# agile-skills

[![skills.sh](https://skills.sh/b/jackaranaram/agile)](https://skills.sh/jackaranaram/agile)

AI agent skills for the agile-agent-harness ecosystem, designed for professional engineering practices, full Git lifecycle automation, automated diagnostics, and comprehensive technical context generation.

## 📦 Skills Catalog

| Skill | Description | Install |
|---|---|---|
| [daily-init](./daily-init/SKILL.md) | Single entry point for daily work — non-blocking Scrum Daily Standup reports, Git state & sync analysis, user story detection, preventive breach audit (.env drift, orphaned tests, stashes). | `npx skills add jackaranaram/agile --skill daily-init` |
| [dev-flow](./dev-flow/SKILL.md) | Professional Git lifecycle & health gates — automatic branch creation from updated master/main, isolated parallel worktrees (hotfix, perf, test, refactor), atomic commits & amends with `--force-with-lease`, linear rebase sync, and automated Draft PRs. | `npx skills add jackaranaram/agile --skill dev-flow` |
| [project-audit](./project-audit/SKILL.md) | Professional repo standards auditor & bootstrapper — branch protection, CI/CD, linting, pre-commit, dependency bloat analysis, and full implementation plan generation with human-in-the-loop validation. | `npx skills add jackaranaram/agile --skill project-audit` |
| [docs-suite-creator](./docs-suite-creator/SKILL.md) | Production-grade technical documentation suite architect — generates and updates the 6 core architecture files (`ARCHITECTURE.md`, `CONTRACTS.md`, `DATABASE.md`, `MODEL.md`/`LOGIC.md`, `ROADMAP.md`, `SCOPE.md`) in `docs/` with strict MVP/Post-MVP boundaries and Mermaid diagrams. | `npx skills add jackaranaram/agile --skill docs-suite-creator` |

---

## 🚀 Quick Installation

### Install all skills

```bash
npx skills add jackaranaram/agile
```

### Install individual skills

```bash
npx skills add jackaranaram/agile --skill daily-init
npx skills add jackaranaram/agile --skill dev-flow
npx skills add jackaranaram/agile --skill project-audit
npx skills add jackaranaram/agile --skill docs-suite-creator
```
