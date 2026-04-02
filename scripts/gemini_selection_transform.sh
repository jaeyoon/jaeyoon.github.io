#!/bin/sh
set -eu

mode="${1:-translate}"

if ! command -v gemini >/dev/null 2>&1; then
  echo "gemini CLI를 찾을 수 없습니다." >&2
  exit 127
fi

input="$(cat)"

if [ -z "$(printf '%s' "$input" | tr -d '[:space:]')" ]; then
  exit 0
fi

case "$mode" in
  translate)
    prompt='위 한국어 원문을 자연스럽고 세련된 영어로 번역해줘. 부가 설명 없이 번역문만 출력해.'
    ;;
  shorten)
    prompt='위 영어 문장을 의미 손실 없이 조금 더 간결하고 읽기 좋게 다듬어줘. 부가 설명 없이 수정된 문장만 출력해.'
    ;;
  expand)
    prompt='위 영어 문장을 더 구체적이고 설명적으로 다듬어줘. 과장하지 말고 정보량만 조금 늘려서 자연스럽게 써줘. 부가 설명 없이 수정된 문장만 출력해.'
    ;;
  *)
    echo "지원하지 않는 모드입니다: $mode" >&2
    exit 2
    ;;
esac

stderr_file="$(mktemp)"
trap 'rm -f "$stderr_file"' EXIT INT TERM

set +e
printf '%s' "$input" | NO_COLOR=1 gemini --prompt "$prompt" 2>"$stderr_file"
status=$?
set -e

if [ -s "$stderr_file" ]; then
  grep -v -E \
    '^Loaded cached credentials\.$|^Registering notification handlers for server |^Server .+ did not declare .+ capability\..*$|^Scheduling MCP context refresh\.\.\.$|^Executing MCP context refresh\.\.\.$|^MCP context refresh complete\.$' \
    "$stderr_file" >&2 || true
fi

exit "$status"
