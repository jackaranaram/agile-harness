# agile-skills

[![skills.sh](https://skills.sh/b/jackaranaram/agile)](https://skills.sh/jackaranaram/agile)

AI agent skills for the agile-agent-harness ecosystem.

## Skills

| Skill | Description | Install |
|---|---|---|
| [daily-init](./daily-init/SKILL.md) | Single entry point for daily work — health check, session recap, breach detection, action menu | `npx skills add jackaranaram/agile --skill daily-init` |
| [dev-flow](./dev-flow/SKILL.md) | Full Git lifecycle — create HU+branch, safe push with dry-run merge, strictly enforces PR/Issue templates | `npx skills add jackaranaram/agile --skill dev-flow` |
| [technical-writer](./technical-writer/SKILL.md) | Generate/update project context suite (6 docs + AGENTS.md + README.md + DESIGN.md + GitHub Templates) | `npx skills add jackaranaram/agile --skill technical-writer` |

## Install all skills

```bash
npx skills add jackaranaram/agile
```

## Install individual skills

```bash
npx skills add jackaranaram/agile --skill daily-init
npx skills add jackaranaram/agile --skill dev-flow
npx skills add jackaranaram/agile --skill technical-writer
```
