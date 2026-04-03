#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


KNOWN_GEMINI_STDERR_PATTERNS = [
    re.compile(r"^Loaded cached credentials\.$"),
    re.compile(r"^Registering notification handlers for server "),
    re.compile(r"^Server .+ did not declare .+ capability\..*$"),
    re.compile(r"^Scheduling MCP context refresh\.\.\.$"),
    re.compile(r"^Executing MCP context refresh\.\.\.$"),
    re.compile(r"^MCP context refresh complete\.$"),
]

TRAILING_DIRECTIVES_RE = re.compile(r"(?s)(?P<body>.*?)(?:\s*(?P<directives>(?:<<[^<>]+>>\s*)+))$")
DIRECTIVE_RE = re.compile(r"<<([^<>]+)>>")
CONTEXT_SELECTION_START = "<<<MEMO_SELECTION_START>>>"
CONTEXT_SELECTION_END = "<<<MEMO_SELECTION_END>>>"
CONTEXT_NOTE_START = "<<<MEMO_NOTE_START>>>"
CONTEXT_NOTE_END = "<<<MEMO_NOTE_END>>>"
MEMO_SKILL_PATH = (
    Path(__file__).resolve().parent.parent
    / ".claude"
    / "skills"
    / "memo-rewrite-lite"
    / "SKILL.md"
)


@dataclass
class ProviderResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""
    reason: str = ""


def strip_known_gemini_logs(stderr: str) -> str:
    kept: list[str] = []
    for line in stderr.splitlines():
        if any(pattern.match(line) for pattern in KNOWN_GEMINI_STDERR_PATTERNS):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def parse_input(raw_text: str) -> tuple[str, list[str]]:
    text = raw_text.strip()
    match = TRAILING_DIRECTIVES_RE.match(text)
    if not match:
        return text, []
    directives_block = match.group("directives") or ""
    directives = [item.strip() for item in DIRECTIVE_RE.findall(directives_block) if item.strip()]
    if not directives:
        return text, []
    body = (match.group("body") or "").rstrip()
    return body, directives


def load_memo_skill() -> str:
    try:
        return MEMO_SKILL_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return (
            "우선 규칙:\n"
            "- 중립 어조 유지: 단정형은 `~보임`, `~것 같음`, `~위험해보임`처럼 완곡하게 변환\n"
            "- 단문 메모체: `~함`, `~됨`, `~봄`, `~보임`, `~해봄`, `~적합해보임` 같은 종결 우선 사용"
        )


def parse_memo_context_input(raw_text: str) -> tuple[str, str]:
    selection_match = re.search(
        rf"(?s){re.escape(CONTEXT_SELECTION_START)}\n?(.*?){re.escape(CONTEXT_SELECTION_END)}",
        raw_text,
    )
    note_match = re.search(
        rf"(?s){re.escape(CONTEXT_NOTE_START)}\n?(.*?){re.escape(CONTEXT_NOTE_END)}",
        raw_text,
    )

    if not selection_match or not note_match:
        return raw_text.strip(), ""

    selection = selection_match.group(1).strip()
    note_content = note_match.group(1).strip()
    return selection, note_content


def build_prompt(mode: str, body: str, directives: list[str]) -> str:
    directive_text = ""
    if directives:
        directive_text = (
            "\n추가 스타일/톤 지시:\n- " + "\n- ".join(directives) + "\n"
        )

    if mode == "translate":
        return (
            "아래 한국어 문장을 자연스럽고 세련된 영어로 번역해줘."
            " 부가 설명 없이 결과 문장만 출력해."
            f"{directive_text}\n원문:\n{body}"
        )
    if mode == "shorten":
        return (
            "아래 영어 문장을 의미 손실 없이 조금 더 간결하고 읽기 좋게 다듬어줘."
            " 출력은 반드시 영어로만 하고, 부가 설명 없이 수정된 영어 문장만 출력해."
            f"{directive_text}\n원문:\n{body}"
        )
    if mode == "expand":
        return (
            "아래 영어 문장을 더 구체적이고 설명적으로 다듬어줘."
            " 과장하지 말고 정보량만 조금 늘려서 자연스럽게 써줘."
            " 출력은 반드시 영어로만 하고, 부가 설명 없이 수정된 영어 문장만 출력해."
            f"{directive_text}\n원문:\n{body}"
        )
    if mode == "rewrite":
        return (
            "아래 영어 문장을 핵심 의미는 유지한 채 영어로 자연스럽게 다시 써줘."
            " 길이는 크게 늘리거나 줄이지 말고, 주어진 스타일/톤 지시가 있으면 그에 맞게 반영해."
            " 출력은 반드시 영어로만 하고, 부가 설명 없이 수정된 영어 문장만 출력해."
            f"{directive_text}\n원문:\n{body}"
        )
    if mode == "memo":
        memo_skill = load_memo_skill()
        return (
            "아래 한국어 문장을 핵심 의미는 유지한 채, 더 간단하고 빠르게 읽히는 한국어 메모체로 바꿔줘."
            " 아래 스킬 규칙을 우선 적용하고, 규칙이 충돌하면 더 중립적이고 짧은 메모체를 선택해."
            " 출력은 반드시 한국어로만 하고, 부가 설명 없이 수정된 문장만 출력해."
            f"{directive_text}\n적용할 메모체 스킬:\n{memo_skill}\n\n원문:\n{body}"
        )
    if mode == "memo-fast":
        memo_skill = load_memo_skill()
        return (
            "아래 한국어 선택 문장만 핵심 의미를 유지한 채 짧고 담백한 한국어 메모체로 바꿔줘."
            " 속도가 중요하니 과도한 해석은 하지 말고, 입력 자체에서 읽히는 의미 범위 안에서만 정리해."
            " 아래 스킬 규칙을 우선 적용해."
            " 출력은 반드시 한국어로만 하고, 부가 설명 없이 수정된 문장만 출력해."
            f"{directive_text}\n적용할 메모체 스킬:\n{memo_skill}\n\n선택 문장:\n{body}"
        )
    raise ValueError(f"unsupported mode: {mode}")


def build_memo_context_prompt(selection: str, note_content: str, directives: list[str]) -> str:
    directive_text = ""
    if directives:
        directive_text = (
            "\n추가 스타일/톤 지시:\n- " + "\n- ".join(directives) + "\n"
        )

    memo_skill = load_memo_skill()
    return (
        "아래 한국어 선택 문장만 한국어 메모체로 다시 써줘."
        " 선택 문장만 출력해야 하며, 전체 문서를 다시 쓰면 안 돼."
        " note content는 의미 보존과 지시 대상 해석을 위한 참고 맥락으로만 사용해."
        " 아래 스킬 규칙을 우선 적용하고, 규칙이 충돌하면 더 중립적이고 짧은 메모체를 선택해."
        " 출력은 반드시 한국어로만 하고, 부가 설명 없이 수정된 문장만 출력해."
        f"{directive_text}\n적용할 메모체 스킬:\n{memo_skill}\n\n선택 문장:\n{selection}\n\n참고용 note content:\n{note_content}"
    )


def run_command(
    command: list[str],
    prompt: str,
    timeout_seconds: int,
    extra_env: dict[str, str] | None = None,
    stderr_filter=None,
) -> ProviderResult:
    env = os.environ.copy()
    env["NO_COLOR"] = "1"
    if extra_env:
        env.update(extra_env)
    try:
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ProviderResult(ok=False, reason="timeout")
    except FileNotFoundError:
        return ProviderResult(ok=False, reason="not-installed")
    except Exception as exc:  # pragma: no cover
        return ProviderResult(ok=False, reason=str(exc))

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    if stderr_filter:
        stderr = stderr_filter(stderr)

    if completed.returncode == 0 and stdout:
        return ProviderResult(ok=True, stdout=stdout, stderr=stderr)

    reason = stderr or stdout or f"exit-{completed.returncode}"
    return ProviderResult(ok=False, stdout=stdout, stderr=stderr, reason=reason)


def try_gemini(prompt: str) -> ProviderResult:
    return run_command(
        ["gemini", "--prompt", prompt],
        prompt="",
        timeout_seconds=45,
        stderr_filter=strip_known_gemini_logs,
    )


def try_gemini_flash(prompt: str) -> ProviderResult:
    return run_command(
        ["gemini", "--prompt", prompt],
        prompt="",
        timeout_seconds=45,
        extra_env={"GEMINI_MODEL": "gemini-2.5-flash"},
        stderr_filter=strip_known_gemini_logs,
    )


def try_claude(prompt: str) -> ProviderResult:
    return run_command(
        ["claude", "-p", "--bare", "--tools", ""],
        prompt=prompt,
        timeout_seconds=45,
    )


def get_providers(mode: str, provider_hint: str = "auto"):
    if provider_hint == "gemini":
        return [("gemini", try_gemini)]
    if provider_hint == "flash":
        return [("gemini-flash", try_gemini_flash)]
    if provider_hint == "claude":
        return [("claude", try_claude)]

    if mode == "memo-fast":
        return [
            ("gemini-flash", try_gemini_flash),
            ("gemini", try_gemini),
            ("claude", try_claude),
        ]
    if mode == "memo-context":
        return [
            ("gemini", try_gemini),
            ("gemini-flash", try_gemini_flash),
            ("claude", try_claude),
        ]
    if mode == "translate":
        return [
            ("gemini-flash", try_gemini_flash),
            ("gemini", try_gemini),
            ("claude", try_claude),
        ]
    return [
        ("gemini", try_gemini),
        ("gemini-flash", try_gemini_flash),
        ("claude", try_claude),
    ]


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "translate"
    provider_hint = sys.argv[2] if len(sys.argv) > 2 else "auto"
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        return 0

    if mode == "memo-context":
        selection_raw, note_content = parse_memo_context_input(raw_input)
        body, directives = parse_input(selection_raw)
        if not body.strip():
            return 0
        prompt = build_memo_context_prompt(body, note_content, directives)
    else:
        body, directives = parse_input(raw_input)
        if not body.strip():
            return 0
        prompt = build_prompt(mode, body, directives)

    if not body.strip():
        return 0

    providers = get_providers(mode, provider_hint)

    errors: list[str] = []
    for name, runner in providers:
        result = runner(prompt)
        if result.ok:
            sys.stdout.write(result.stdout.strip() + "\n")
            return 0
        errors.append(f"{name}: {result.reason}")

    sys.stderr.write("All selection transform fallbacks failed.\n")
    sys.stderr.write("\n".join(errors) + "\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
