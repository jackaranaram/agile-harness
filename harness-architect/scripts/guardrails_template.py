"""Reusable Antigravity PreToolUse guardrail hook template.

Customize POLICY below for your workspace, save as `<workspace>/.agents/hooks/guardrails.py`,
and reference it from `<workspace>/.agents/hooks.json`.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

# ==============================================================================
# Project Policy Configuration (Customize per workspace)
# ==============================================================================
POLICY: dict[str, Any] = {
    "allowed_env_names": frozenset({".env.example", ".env.sample", ".env.template"}),
    "block_word_lockfiles": True,
    # Add lowercase filename regexes for frozen backups or read-only artifacts, e.g.:
    # r"^devalign_full_paper_computers_en_v[1-6]\.docx$"
    "protected_filename_regexes": (),
    # Add normalized lowercase path substrings to protect fixtures/datasets, e.g.:
    # "/validation/ground_truth_cvs.json"
    "protected_path_substrings": (),
    # Set to ["npm", "yarn"] when enforcing pnpm, ["pnpm", "yarn"] for npm, or [] to disable:
    "disallowed_pkg_managers": ("npm", "yarn"),
    "preferred_pkg_manager": "pnpm",
    # Add project-specific destructive CLI regexes requiring explicit user approval:
    # r"\bprisma\s+migrate\s+deploy\b", r"\balembic\s+upgrade\s+head\b"
    "extra_force_ask_regexes": (),
}

# ==============================================================================
# Core Evaluators (Fail-open by design)
# ==============================================================================
_SEGMENT_SPLIT_RE = re.compile(r"\r?\n|&&|\|\||[;|&]")
_GIT_RESET_HARD_RE = re.compile(r"\bgit\s+reset\s+--hard\b")
_GIT_PUSH_FORCE_RE = re.compile(r"\bgit\s+push\b.*(?:\s--force\b|\s-f\b)")
_RM_RF_RE = re.compile(r"(?:^|\s)rm\s+(?:-rf|-fr)(?:\s|$)")
_REMOVE_ITEM_FORCE_RE = re.compile(
    r"\bRemove-Item\b(?=.*-Recurse\b)(?=.*-Force\b)", re.IGNORECASE
)

_PROTECTED_FILE_RES = tuple(
    re.compile(pat, re.IGNORECASE) for pat in POLICY["protected_filename_regexes"]
)
_EXTRA_FORCE_ASK_RES = tuple(
    re.compile(pat, re.IGNORECASE) for pat in POLICY["extra_force_ask_regexes"]
)


def _build_pkg_manager_regex() -> re.Pattern[str] | None:
    """Compile anchored regex for disallowed JS package manager commands."""
    disallowed = POLICY["disallowed_pkg_managers"]
    if not disallowed:
        return None
    escaped = "|".join(re.escape(name) for name in disallowed)
    return re.compile(rf"^(?:{escaped})(?:\.cmd|\.ps1)?(?:\s+|$)", re.IGNORECASE)


_DISALLOWED_PKG_RE = _build_pkg_manager_regex()


def _allow() -> dict[str, Any]:
    """Return the default allow decision payload."""
    return {"decision": "allow"}


def _evaluate_file_path(raw_path: str) -> dict[str, Any]:
    """Evaluate write_file/edit_file target paths against protected file rules."""
    if not raw_path:
        return _allow()

    normalized = raw_path.replace("\\", "/").rstrip("/")
    normalized_lower = normalized.lower()
    basename = normalized_lower.split("/")[-1]

    if POLICY["block_word_lockfiles"] and basename.startswith("~$"):
        return {
            "decision": "deny",
            "reason": "Blocked edit to Word temporary lock file (~$*.docx).",
        }

    if (basename == ".env" or basename.startswith(".env.")) and (
        basename not in POLICY["allowed_env_names"]
    ):
        return {
            "decision": "deny",
            "reason": "Blocked modification of secret .env file; update .env.example instead.",
        }

    for pattern in _PROTECTED_FILE_RES:
        if pattern.match(basename):
            return {
                "decision": "deny",
                "reason": f"Blocked modification of protected file '{basename}'.",
            }

    for substring in POLICY["protected_path_substrings"]:
        if substring.lower() in normalized_lower:
            return {
                "decision": "deny",
                "reason": f"Blocked modification of protected path matching '{substring}'.",
            }

    return _allow()


def _evaluate_command(command_line: str) -> dict[str, Any]:
    """Evaluate run_command shell strings for destructive or off-standard commands."""
    if not command_line:
        return _allow()

    segments = [seg.strip() for seg in _SEGMENT_SPLIT_RE.split(command_line) if seg.strip()]

    for segment in segments:
        if _GIT_RESET_HARD_RE.search(segment):
            return {
                "decision": "force_ask",
                "reason": "Destructive command detected (git reset --hard). Confirm before running.",
            }

        if _GIT_PUSH_FORCE_RE.search(segment) and not re.search(
            r"--force-with-lease\b", segment
        ):
            return {
                "decision": "force_ask",
                "reason": (
                    "Force push without --force-with-lease detected. "
                    "Confirm before overwriting remote history."
                ),
            }

        if _RM_RF_RE.search(segment) or _REMOVE_ITEM_FORCE_RE.search(segment):
            return {
                "decision": "force_ask",
                "reason": "Recursive forced deletion detected. Confirm before running.",
            }

        for extra_re in _EXTRA_FORCE_ASK_RES:
            if extra_re.search(segment):
                return {
                    "decision": "force_ask",
                    "reason": "High-impact workspace command detected. Confirm before running.",
                }

    if _DISALLOWED_PKG_RE is not None:
        preferred = POLICY["preferred_pkg_manager"]
        disallowed_label = "/".join(POLICY["disallowed_pkg_managers"])
        for segment in segments:
            if _DISALLOWED_PKG_RE.match(segment):
                return {
                    "decision": "ask",
                    "reason": (
                        f"Workspace standard uses {preferred} instead of {disallowed_label}. "
                        "Confirm if intentional."
                    ),
                }

    return _allow()


def evaluate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a PreToolUse hook payload to the matching policy evaluator."""
    tool_call = payload.get("toolCall") or {}
    tool_name = str(tool_call.get("name", ""))
    args = tool_call.get("args") or {}

    if tool_name in {"write_file", "edit_file"}:
        path = str(args.get("Path") or args.get("path") or "")
        return _evaluate_file_path(path)

    if tool_name == "run_command":
        cmd = str(args.get("CommandLine") or args.get("commandLine") or "")
        return _evaluate_command(cmd)

    return _allow()


def main() -> None:
    """Read PreToolUse JSON from stdin and emit a decision JSON object on stdout."""
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
        decision = evaluate_payload(payload if isinstance(payload, dict) else {})
    except Exception:
        decision = _allow()

    sys.stdout.write(json.dumps(decision))


if __name__ == "__main__":
    main()
