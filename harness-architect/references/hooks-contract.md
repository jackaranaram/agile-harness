# Antigravity `hooks.json` Contract & Guardrail Patterns

## Discovery & Execution Environment

* **Location:** `<workspace>/.agents/hooks.json` (recommended script folder: `<workspace>/.agents/hooks/`).
* **Execution Shell:** Antigravity executes each command hook synchronously via:
  * Windows: `cmd /c <command>`
  * Linux / macOS: `sh -c <command>`
* **Working Directory:** The hook process **always starts in the directory containing `hooks.json`** (`<workspace>/.agents/`), **NOT** the repository root (`cwd` field in stdin gives the agent's workspace CWD). Refer to scripts relative to `.agents/`, e.g. `"python hooks/guardrails.py"`.
* **Timeout:** Default `30`s; keep `PreToolUse` guardrail scripts fast (`"timeout": 5`).
* **Windows Interpreter Note:** Verify whether `python` or `python3` resolves cleanly under `cmd /c` before writing `"command"`. On Windows Python installs (`python.org`), `python` works reliably while `python3` may hit an empty Windows Store alias.

## `hooks.json` Schema (`PreToolUse`)

Use separate matcher entries per tool (`"write_file"`, `"edit_file"`, `"run_command"`) rather than regex pipe alternation to avoid cross-platform regex escaping discrepancies:

```json
{
  "project-guardrails": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "write_file",
        "hooks": [
          { "type": "command", "command": "python hooks/guardrails.py", "timeout": 5 }
        ]
      },
      {
        "matcher": "edit_file",
        "hooks": [
          { "type": "command", "command": "python hooks/guardrails.py", "timeout": 5 }
        ]
      },
      {
        "matcher": "run_command",
        "hooks": [
          { "type": "command", "command": "python hooks/guardrails.py", "timeout": 5 }
        ]
      }
    ]
  }
}
```

## Input / Output Contract (`stdin` -> `stdout`, camelCase)

**`PreToolUse` stdin payload:**
```json
{
  "conversationId": "...",
  "workspacePaths": ["..."],
  "hookEventName": "PreToolUse",
  "cwd": "...",
  "stepIdx": 19,
  "toolCall": {
    "id": "toolu_01",
    "name": "run_command",
    "args": { "CommandLine": "npm test" }
  }
}
```

**`PreToolUse` stdout payload:**
* `{"decision": "allow"}` — permit tool call silently.
* `{"decision": "deny", "reason": "..."}` — hard block immediately (best for `.env` secrets, temporary lockfiles, frozen backups).
* `{"decision": "ask", "reason": "..."}` — ask user confirmation, respecting "Always Allow" cache (best for off-standard package managers like `npm` in a `pnpm` repo).
* `{"decision": "force_ask", "reason": "..."}` — always ask user confirmation, ignoring cached approvals (best for destructive commands: `git reset --hard`, `git push --force` without `--force-with-lease`, `rm -rf`, `Remove-Item -Recurse -Force`, production DB migrations).

## Mandatory Fail-Open & Anti-False-Positive Rules

1. **Always fail open:** Wrap `main()` in `try/except Exception` and return `{"decision": "allow"}` on malformed JSON or runtime errors so a bug in a hook never freezes the workspace.
2. **Segment shell commands:** Split `CommandLine` on `\r?\n|&&|\|\||[;|&]` and evaluate each segment independently so `--force-with-lease` in segment A does not mask `--force` in segment B.
3. **Never false-positive package manager checks:** Anchor disallowed package manager detection to the start of a command segment (e.g., `^(?:npm|yarn)(?:\.cmd|\.ps1)?(?:\s+|$)`). Never use substring search for `npm`—that breaks `npx`, `pnpm`, and Windows paths containing `AppData\Roaming\npm\pnpm.ps1`.

## Other Lifecycle Events (When Needed)

| Event | Structure | Typical Use |
| :--- | :--- | :--- |
| `SessionStart` | Flat list | Inject one-time session banner or startup context (`injectSteps`) |
| `PostToolUse` | Matcher + `hooks` | Audit tool failures or trigger fast post-edit checks (`{}` stdout) |
| `PreInvocation` | Flat list | Inject reminders before model invocation |
| `PostInvocation` | Flat list | Inspect turn finish state; optionally `force_continue` |
| `Stop` | Flat list | Enforce completion checks (`decision: "continue"`, check `continuationActive` to prevent loops) |
