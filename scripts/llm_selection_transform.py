#!/usr/bin/env python3

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass


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
    raise ValueError(f"unsupported mode: {mode}")


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


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "translate"
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        return 0

    body, directives = parse_input(raw_input)
    if not body.strip():
        return 0

    prompt = build_prompt(mode, body, directives)

    providers = [
        ("gemini", try_gemini),
        ("gemini-flash", try_gemini_flash),
        ("claude", try_claude),
    ]

    errors: list[str] = []
    for name, runner in providers:
        result = runner(prompt)
        if result.ok:
            sys.stdout.write(result.stdout.strip() + "\n")
            return 0
        errors.append(f"{name}: {result.reason}")

    sys.stderr.write("All translation fallbacks failed.\n")
    sys.stderr.write("\n".join(errors) + "\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
