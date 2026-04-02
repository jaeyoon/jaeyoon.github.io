# 🔄 옵시디언 동기화 및 AI 번역 환경 세팅 핸드오버 노트

> [!NOTE] 
> 본 문서는 현재까지 진행된 요구사항, 제안 내용, 설치된 플러그인, 그리고 미해결 에러(Git 권한)에 대한 맥락을 다른 에이전트(또는 사용자 님)에게 인계하기 위해 작성되었습니다.

## 1. 초기 요구사항 및 목적
- **목적**: GitHub Pages (`jaeyoon.github.io/notes`)의 마크다운 파일을 로컬에 동기화하여 쉽게 수정하고, 커밋/푸시 과정을 자동화하여 웹 페이지에 편하게 반영.
- **추가 요구사항**: 로컬 Mac에 기설치된 터미널 전용 AI CLI 툴(`gemini`, `claude`, `codex`)을 활용하여 옵시디언 영문 번역 환경 구축.

## 2. 작업된 환경 (워크스페이스)
- **로컬 경로**: `/Users/jayden/Workspace/github-page`
- **현재 상태**: 저장소를 `git clone` (fetch 후 `main` 브랜치 명시적 체크아웃) 하여 로컬과 연동 완료. 구조상 `github-page` 폴더 자체가 옵시디언 Vault로 열려있음.

---

## 3. 적용된 솔루션 1: 자동 동기화 (Obsidian Git)
GitHub 데스크탑 앱이나 터미널 스크립트 대신, 옵시디언 내에서 자동으로 동기화되는 방식을 채택.

- **설치된 플러그인**: `Obsidian Git` (ID: `obsidian-git`, Author: Denis Olehov, Vinzent)
- **적용된 설정 내역**:
  - `Auto commit-and-sync interval (minutes)`: **15분** (15분 주기로 커밋과 Push 병행 처리)
  - `Pull updates on startup`: **ON**
  - `Split timers for automatic commit and sync`: **OFF**
- **🚨 미해결 이슈 (진행 중 상태)**: 
  - 15분 주기로 깃허브로 Push가 실행될 때, Mac Keychain에 전역으로 저장되어 있던 과거/타 계정 정보(`j43y0on`)가 튀어나오면서 `jaeyoon/jaeyoon.github.io.git`에 403 권한 거부 에러가 발생함.
  - **해결을 위해 제안된 Next Step**: GitHub에서 `jaeyoon` 계정의 Personal Access Token(PAT, repo 스코프)을 발급받아, 해당 폴더(`github-page`)의 `.git/config` Remote URL을 `https://jaeyoon:<TOKEN>@github.com/...` 형태로 직접 갱신하는 절차 대기 중.
  - **💡 PAT(토큰 연동) 방식이 현재 유일하고 최적의 해결법이라고 판단하는 근거**:
    1. **Mac 전역 키체인 환경의 독립성 보장**: 기존에 등록된 `j43y0on` 계정의 정보를 억지로 지우거나 덮어씌우면, 사용자님의 다른 폴더라 프로젝트에서 `j43y0on` 계정으로 연동된 작업들이 모조리 망가질 위험이 있습니다. 이 옵시디언 폴더(`.git/config`) 안에만 토큰을 은밀히 심어두면, Mac 전체 환경을 어지럽히지 않고 완벽하게 이 폴더만 격리하여(Isolation) `jaeyoon` 권한을 쓸 수 있습니다.
    2. **백그라운드 무인 자동화의 절대적 안정성**: 15분 간격 자동화가 '옵시디언'이라는 GUI 앱 뒤에서 암묵적으로 돌아가야 합니다. 만약 키체인 충돌로 인해 OS에서 비밀번호를 요구하는 팝업이 뜨면 플러그인의 자동 백업이 그대로 멈춰버립니다. URL 문자열에 토큰을 직결해 버리면 애초에 암호 요구 팝업이 원천 차단되어 가장 안정적인 무인 자동화(Unattended Automation)가 완성됩니다.
    3. **GitHub 보안 정책 순응**: 애초에 GitHub 측에서 HTTPS 주소의 경우 더 이상 일반 로그인 비밀번호를 허용하지 않습니다. PAT(Token) 사용은 보안상 거스를 수 없는 단일 표준 기조입니다.

---

## 4. 적용된 솔루션 2: 자체 CLI 연동 번역기 (Shell commands)
Obsidian Copilot 같은 API 기반 플러그인 대신, 로컬에 컴파일/설치되어 있는 CLI를 옵시디언 에디터 텍스트에 직접 묻게 하는 방식 채택.

- **설치된 플러그인**: `Shell commands` (Author: Jarkko Linnanvirta)
- **발생했던 이슈**: Mac GUI 애플리케이션(옵시디언) 특성상 터미널의 `.zshrc` PATH 변수를 불러오지 못해 `[127] env: node: No such file or directory` 에러가 발생.
- **적용된 설정 및 우회 픽스(Fix)**: 
  - 생성된 커맨드 내용 (가장 직관적인 One-liner 방식 채택):
    ```bash
    export PATH="/opt/homebrew/bin:$PATH" && /opt/homebrew/bin/gemini "다음 텍스트를 자연스럽고 세련된 영어로 번역해줘. 부가 설명 없이 번역 결과만 출력할 것: {{selection}}"
    ```
  - Output 환경 설정: `Output channel for stdout` 값을 **`Current file: caret position` (또는 `Replace selection`)** 으로 지정.
  - 이를 통해 드래그된 부분의 텍스트가 번역된 결과물로 in-place 치환되도록 설정됨.

---

## 5. 다른 에이전트에게 보내는 개선 요구 포인트 (Request for Optimize)
1. **깃허브 Auth (Obsidian Git)**: 에러가 발생하는 `j43y0on` 키체인 이슈를 가장 매끄럽게 우회하거나 권한을 갱신할 수 있는 최단 자동화 루트 제안이 필요함.
2. **CLI 번역 최적화 (Shell commands)**: 인라인 PATH 주입 방식(`export PATH=...`)을 플러그인의 Environments 설정으로 전역 매핑하는 방식이나, 더 빠르고 에러 없는 프롬프트 파이프라인(CLI 아규먼트 탈출 문자 등)으로 개선할 수 있는지 검토 요망.
