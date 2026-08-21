#!/usr/bin/env python3
"""Flag likely audience-boundary and task-process leakage in text artifacts.

The audit is profile-aware and deliberately conservative. It ignores fenced
code and reports contextual warnings rather than trying to rewrite prose.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


PROFILES = ("state", "change", "decision", "direct")
LEVELS = {"ignore": 0, "warning": 1, "error": 2}


@dataclass(frozen=True)
class Finding:
    line: int
    severity: str
    rule_id: str
    message: str
    snippet: str = ""


@dataclass(frozen=True)
class Rule:
    rule_id: str
    message: str
    patterns: tuple[re.Pattern[str], ...]
    levels: dict[str, str]
    allow_in_history_section: bool = False


def _compile(*patterns: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)


RULES: tuple[Rule, ...] = (
    Rule(
        "REQUESTER_REFERENCE",
        "Refers to a requester or their feedback; confirm that the intended reader shares this context.",
        _compile(
            r"(?:根据|按照|按)(?:你|用户|审阅者|评审者)(?:的)?(?:要求|反馈|意见)",
            r"为了回应(?:你|用户|审阅者|评审者)(?:的)?(?:要求|反馈|意见)",
            r"\b(?:as|per) (?:you|the user|the reviewer)(?:'s)? (?:requested|request|feedback)\b",
            r"\bbased on (?:your|the user's|the reviewer's) (?:request|feedback)\b",
            r"\bthe user asked\b",
        ),
        {"state": "error", "change": "warning", "decision": "warning", "direct": "ignore"},
    ),
    Rule(
        "AUTHORING_ACTION",
        "Narrates an authoring action; express the subject result unless the recipient needs a work update.",
        _compile(
            r"(?:我|我们|模型|助手|AI|Codex|Claude)(?:已经|已|刚刚|在本次(?:任务|修改)中)?(?:删除|移除|修改|调整|重写|更新|添加)",
            r"\b(?:I|we|the (?:assistant|model|agent)|Codex|Claude) (?:have )?(?:removed|deleted|changed|updated|added|rewritten|adjusted)\b",
        ),
        {"state": "error", "change": "warning", "decision": "warning", "direct": "ignore"},
        allow_in_history_section=True,
    ),
    Rule(
        "REVISION_FRAME",
        "Frames the artifact around the current editing process rather than its audience purpose.",
        _compile(
            r"(?:本次|此次)(?:修改|调整|更新|修订|任务|工作)",
            r"(?:原方案|此前方案|之前的方案)",
            r"\b(?:this|the current) (?:revision|editing task|edit|update)\b",
            r"\b(?:the|our) previous (?:draft|approach)\b",
        ),
        {"state": "error", "change": "ignore", "decision": "ignore", "direct": "ignore"},
        allow_in_history_section=True,
    ),
    Rule(
        "HIDDEN_CONVERSATION",
        "Depends on conversation context that may be unavailable to the intended reader.",
        _compile(
            r"(?:正如|就像)(?:我们)?(?:刚才|之前|上面)(?:讨论|提到|说过)",
            r"(?:在|根据)(?:我们的)?(?:聊天|对话)中",
            r"\b(?:as|like) (?:we )?(?:discussed|mentioned) (?:above|earlier|in (?:our|the) (?:chat|conversation))\b",
            r"\bin (?:our|the) (?:chat|conversation)\b",
        ),
        {"state": "error", "change": "error", "decision": "warning", "direct": "ignore"},
    ),
    Rule(
        "PAST_STATE",
        "Mentions an earlier state; retain it only when history changes a reader decision.",
        _compile(
            r"(?:原先|此前|以前|之前)(?:采用|使用|包含|支持|依赖|提供|是)",
            r"(?:不再|现已)(?:使用|包含|支持|依赖|提供)",
            r"\b(?:previously|formerly|no longer|used to|has been removed|was removed|was replaced)\b",
        ),
        {"state": "warning", "change": "ignore", "decision": "ignore", "direct": "ignore"},
        allow_in_history_section=True,
    ),
    Rule(
        "INTERNAL_AGENT_MECHANICS",
        "Mentions internal agent mechanics; verify that disclosure is useful and authorized for this reader.",
        _compile(
            r"(?:系统提示词|思维链|工具调用|上下文窗口|令牌预算|token预算|子代理)",
            r"\b(?:system prompt|chain[- ]of[- ]thought|tool call|context window|token budget|subagent)\b",
        ),
        {"state": "warning", "change": "warning", "decision": "warning", "direct": "warning"},
    ),
)


PROCESS_HEADING = re.compile(
    r"^(?:what (?:i|we) changed|changes made|editing summary|revision summary|"
    r"本次修改|此次修改|修改说明|调整说明|完成内容)$",
    re.IGNORECASE,
)
HISTORY_HEADING = re.compile(
    r"^(?:migration|upgrade|upgrading|changelog|history|release notes?|"
    r"breaking changes?|deprecations?|迁移|升级|变更记录|历史|发布说明|破坏性变更|废弃)",
    re.IGNORECASE,
)
NEGATIVE_IDENTITY_HEADING = re.compile(
    r"^(?:without|no |not |无|不含|不使用|不依赖)", re.IGNORECASE
)


def _heading_text(line: str) -> str | None:
    match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
    return match.group(1).strip() if match else None


def _strip_inline_code(line: str) -> str:
    return re.sub(r"`[^`]*`", "", line)


def audit_text(text: str, profile: str = "state", verbose: bool = False) -> list[Finding]:
    if profile not in PROFILES:
        raise ValueError(f"unsupported profile: {profile}")

    findings: list[Finding] = []
    in_fence = False
    in_history_section = profile in {"change", "decision"}

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if re.match(r"^\s*(```|~~~)", raw_line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        heading = _heading_text(raw_line)
        heading_handled = False
        if heading is not None:
            in_history_section = profile in {"change", "decision"} or bool(
                HISTORY_HEADING.match(heading)
            )
            if profile == "state" and PROCESS_HEADING.match(heading):
                findings.append(
                    Finding(
                        line_number,
                        "error",
                        "PROCESS_HEADING",
                        "Uses a task-report heading in a current-state artifact.",
                        raw_line.strip() if verbose else "",
                    )
                )
                heading_handled = True
            elif profile == "state" and NEGATIVE_IDENTITY_HEADING.match(heading):
                findings.append(
                    Finding(
                        line_number,
                        "warning",
                        "NEGATIVE_IDENTITY_HEADING",
                        "Defines a section by absence; confirm that the distinction helps this reader.",
                        raw_line.strip() if verbose else "",
                    )
                )

        if heading_handled:
            continue

        prose = _strip_inline_code(raw_line)
        if not prose.strip():
            continue

        for rule in RULES:
            severity = rule.levels[profile]
            if severity == "ignore" or (in_history_section and rule.allow_in_history_section):
                continue
            if any(pattern.search(prose) for pattern in rule.patterns):
                findings.append(
                    Finding(
                        line_number,
                        severity,
                        rule.rule_id,
                        rule.message,
                        raw_line.strip() if verbose else "",
                    )
                )

    return findings


def _should_fail(findings: Iterable[Finding], fail_on: str) -> bool:
    if fail_on == "none":
        return False
    threshold = LEVELS[fail_on]
    return any(LEVELS[finding.severity] >= threshold for finding in findings)


def _print_findings(path: Path, findings: Sequence[Finding]) -> None:
    if not findings:
        print(f"PASS {path}: no audience-boundary leakage detected")
        return

    for finding in findings:
        print(f"{finding.severity.upper()} {path}:{finding.line} {finding.rule_id}: {finding.message}")
        if finding.snippet:
            print(f"  {finding.snippet}")
    errors = sum(finding.severity == "error" for finding in findings)
    warnings = sum(finding.severity == "warning" for finding in findings)
    print(f"SUMMARY {path}: {errors} error(s), {warnings} warning(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit outward-facing text for audience-boundary and task-process leakage."
    )
    parser.add_argument("artifact", type=Path, help="Markdown or text artifact to audit")
    parser.add_argument(
        "--profile", choices=PROFILES, default="state", help="Audience writing mode"
    )
    parser.add_argument(
        "--fail-on",
        choices=("error", "warning", "none"),
        default="error",
        help="Lowest severity that produces exit code 1",
    )
    parser.add_argument("--verbose", action="store_true", help="Show each flagged source line")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = args.artifact.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR {args.artifact}: {exc}", file=sys.stderr)
        return 2

    findings = audit_text(text, args.profile, args.verbose)
    _print_findings(args.artifact, findings)
    return 1 if _should_fail(findings, args.fail_on) else 0


if __name__ == "__main__":
    raise SystemExit(main())
