"""Deterministic verification script for Antigravity workspace harnesses.

Validates:
1. All workspace/module AGENTS.md files exist, are non-empty UTF-8, < 24,000 bytes,
   and contain no leading YAML frontmatter ('---').
2. .agents/hooks.json schema, referenced local script paths, and OS-shell execution
   of PreToolUse guardrails against safety & fail-open test vectors.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_SKIP_DIRS = frozenset(
    {
        ".agent",
        ".agents",
        ".git",
        ".mypy_cache",
        ".next",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "htmlcov",
        "node_modules",
        "venv",
    }
)
_MAX_RULE_BYTES = 24_000
_SCRIPT_TOKEN_RE = re.compile(r"[^\s\"']+\.(?:py|sh|ps1|js|mjs|cjs|bat|cmd)")


def find_agents_md_files(workspace: Path) -> list[Path]:
    """Walk workspace recursively to locate project/module AGENTS.md files."""
    found: list[Path] = []
    for root, dirs, files in os.walk(workspace):
        dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
        if "AGENTS.md" in files:
            found.append(Path(root) / "AGENTS.md")
    return sorted(found)


def validate_agents_md(workspace: Path) -> tuple[bool, list[str]]:
    """Validate AGENTS.md presence, size limits, encoding, and absence of frontmatter."""
    messages: list[str] = []
    files = find_agents_md_files(workspace)
    if not files:
        return False, ["FAIL agents_md: No AGENTS.md files found under workspace."]

    ok = True
    for md_path in files:
        raw = md_path.read_bytes()
        rel = md_path.relative_to(workspace)
        if not raw.strip():
            messages.append(f"FAIL {rel}: File is empty.")
            ok = False
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            messages.append(f"FAIL {rel}: Invalid UTF-8 ({exc}).")
            ok = False
            continue
        if len(raw) >= _MAX_RULE_BYTES:
            messages.append(f"FAIL {rel}: {len(raw)} bytes exceeds {_MAX_RULE_BYTES}-byte limit.")
            ok = False
            continue
        if text.lstrip().startswith("---"):
            messages.append(f"FAIL {rel}: Contains leading YAML frontmatter ('---').")
            ok = False
            continue
        messages.append(f"PASS {rel}: {len(raw)} bytes, valid UTF-8, no frontmatter.")

    return ok, messages


def _find_matching_commands(hooks_data: dict[str, Any], tool_name: str) -> list[str]:
    """Return PreToolUse commands in hooks.json matching a given tool name."""
    commands: list[str] = []
    for hook_spec in hooks_data.values():
        if not isinstance(hook_spec, dict) or hook_spec.get("enabled") is False:
            continue
        for group in hook_spec.get("PreToolUse", []):
            if not isinstance(group, dict):
                continue
            matcher = str(group.get("matcher", "") or "").strip()
            if matcher and matcher != "*":
                if not re.fullmatch(matcher, tool_name):
                    continue
            for handler in group.get("hooks", []):
                if isinstance(handler, dict) and handler.get("command"):
                    commands.append(str(handler["command"]))
    return commands


def _run_hook_command(command: str, cwd: Path, stdin_text: str) -> dict[str, Any]:
    """Invoke a hook command through the OS shell exactly as Antigravity does."""
    shell_cmd = ["cmd", "/c", command] if os.name == "nt" else ["sh", "-c", command]
    proc = subprocess.run(
        shell_cmd,
        cwd=str(cwd),
        input=stdin_text,
        text=True,
        capture_output=True,
        timeout=5,
        check=True,
    )
    return json.loads(proc.stdout.strip())


def validate_hooks(
    workspace: Path,
    extra_deny_files: list[str],
    extra_ask_cmds: list[str],
    extra_force_ask_cmds: list[str],
) -> tuple[bool, list[str]]:
    """Validate .agents/hooks.json structure, scripts, and PreToolUse behavior."""
    messages: list[str] = []
    agents_dir = workspace / ".agents"
    hooks_json_path = agents_dir / "hooks.json"

    if not hooks_json_path.exists():
        return False, [f"FAIL hooks.json: Missing {hooks_json_path}."]

    try:
        hooks_data = json.loads(hooks_json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, [f"FAIL hooks.json: Invalid JSON ({exc})."]

    if not isinstance(hooks_data, dict) or not hooks_data:
        return False, ["FAIL hooks.json: Top-level JSON object is empty."]

    ok = True
    checked_scripts: set[str] = set()
    for hook_name, hook_spec in hooks_data.items():
        if not isinstance(hook_spec, dict):
            messages.append(f"FAIL hooks.json[{hook_name}]: Spec must be an object.")
            ok = False
            continue
        for event_name in ("PreToolUse", "PostToolUse"):
            for group in hook_spec.get(event_name, []):
                for handler in group.get("hooks", []):
                    cmd = str(handler.get("command", ""))
                    for token in _SCRIPT_TOKEN_RE.findall(cmd):
                        if token in checked_scripts:
                            continue
                        checked_scripts.add(token)
                        script_path = agents_dir / token
                        if not script_path.exists():
                            messages.append(
                                f"FAIL hooks.json: Referenced script not found: {script_path}"
                            )
                            ok = False

    if not ok:
        return False, messages

    test_cases: list[tuple[str, str, dict[str, Any] | str, str]] = [
        (
            "env_edit_deny",
            "edit_file",
            {"toolCall": {"name": "edit_file", "args": {"Path": str(workspace / ".env")}}},
            "deny",
        ),
        (
            "env_example_allow",
            "write_file",
            {
                "toolCall": {
                    "name": "write_file",
                    "args": {"Path": str(workspace / ".env.example")},
                }
            },
            "allow",
        ),
        (
            "normal_file_allow",
            "write_file",
            {
                "toolCall": {
                    "name": "write_file",
                    "args": {"Path": str(workspace / "src" / "example_module.py")},
                }
            },
            "allow",
        ),
        (
            "git_push_force",
            "run_command",
            {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": "git push --force origin main"},
                }
            },
            "force_ask",
        ),
        (
            "git_push_lease",
            "run_command",
            {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": "git push --force-with-lease origin feat/test"},
                }
            },
            "allow",
        ),
        (
            "git_reset_hard",
            "run_command",
            {"toolCall": {"name": "run_command", "args": {"CommandLine": "git reset --hard HEAD~1"}}},
            "force_ask",
        ),
        (
            "rm_rf",
            "run_command",
            {"toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf ./tmp"}}},
            "force_ask",
        ),
        (
            "pwsh_remove_item",
            "run_command",
            {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": "Remove-Item -Force -Recurse ./build"},
                }
            },
            "force_ask",
        ),
        (
            "npx_allow",
            "run_command",
            {"toolCall": {"name": "run_command", "args": {"CommandLine": "npx -y skills add foo"}}},
            "allow",
        ),
        ("malformed_json_fail_open", "write_file", "{bad json", "allow"),
    ]

    for idx, fpath in enumerate(extra_deny_files, 1):
        test_cases.append(
            (
                f"custom_deny_file_{idx}",
                "write_file",
                {"toolCall": {"name": "write_file", "args": {"Path": fpath}}},
                "deny",
            )
        )
    for idx, cmd_text in enumerate(extra_ask_cmds, 1):
        test_cases.append(
            (
                f"custom_ask_cmd_{idx}",
                "run_command",
                {"toolCall": {"name": "run_command", "args": {"CommandLine": cmd_text}}},
                "ask",
            )
        )
    for idx, cmd_text in enumerate(extra_force_ask_cmds, 1):
        test_cases.append(
            (
                f"custom_force_ask_cmd_{idx}",
                "run_command",
                {"toolCall": {"name": "run_command", "args": {"CommandLine": cmd_text}}},
                "force_ask",
            )
        )

    for case_name, tool_name, payload, expected in test_cases:
        cmds = _find_matching_commands(hooks_data, tool_name)
        if not cmds:
            messages.append(f"FAIL {case_name}: No enabled PreToolUse matcher for {tool_name}.")
            ok = False
            continue
        stdin_text = payload if isinstance(payload, str) else json.dumps(payload)
        for cmd in cmds:
            try:
                out = _run_hook_command(cmd, agents_dir, stdin_text)
                actual = out.get("decision")
                if actual == expected:
                    messages.append(f"PASS {case_name}: {actual}")
                else:
                    messages.append(
                        f"FAIL {case_name}: expected '{expected}', got {out!r}"
                    )
                    ok = False
            except Exception as exc:
                messages.append(f"FAIL {case_name}: hook execution error ({exc})")
                ok = False

    return ok, messages


def main() -> int:
    """CLI entry point for harness verification."""
    parser = argparse.ArgumentParser(
        description="Verify Antigravity AGENTS.md hierarchy and .agents/hooks.json guardrails."
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Path to the workspace root directory (default: current directory).",
    )
    parser.add_argument(
        "--expect-deny-file",
        action="append",
        default=[],
        help="Additional file path expected to produce decision='deny'.",
    )
    parser.add_argument(
        "--expect-ask-cmd",
        action="append",
        default=[],
        help="Additional run_command string expected to produce decision='ask'.",
    )
    parser.add_argument(
        "--expect-force-ask-cmd",
        action="append",
        default=[],
        help="Additional run_command string expected to produce decision='force_ask'.",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    if not workspace.is_dir():
        print(f"FAIL: Workspace directory not found: {workspace}", file=sys.stderr)
        return 1

    print(f"=== Harness Verification: {workspace} ===")
    md_ok, md_msgs = validate_agents_md(workspace)
    for line in md_msgs:
        print(line)

    hooks_ok, hook_msgs = validate_hooks(
        workspace,
        extra_deny_files=args.expect_deny_file,
        extra_ask_cmds=args.expect_ask_cmd,
        extra_force_ask_cmds=args.expect_force_ask_cmd,
    )
    for line in hook_msgs:
        print(line)

    passed = md_ok and hooks_ok
    print("=== RESULT:", "ALL CHECKS PASSED ===" if passed else "FAILED ===")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
