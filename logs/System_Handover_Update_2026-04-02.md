# 🔄 핸드오버 후속 업데이트 로그 (2026-04-02)

> [!NOTE]
> 본 문서는 기존 [System_Handover_Note.md](/Users/jayden/Workspace/github-page/System_Handover_Note.md)의 원문을 보존한 상태에서, 그 이후 실제로 적용 완료된 수정사항과 운영 상태를 별도 로그로 정리한 후속 문서입니다.

## 1. 요약
- Git 인증 문제는 **저장소 로컬 credential 분리** 방식으로 해결 완료
- Obsidian Git 자동 백업/푸시는 **실동작 검증 완료**
- Shell Commands 번역 명령은 PATH 및 입력 방식이 더 안전한 구조로 수정됨
- 웹에서 안 보이던 Obsidian 이미지 위키 임베드는 **pre-commit hook 기반 자동교정**으로 해결됨
- `.gitignore`를 정리해 `.DS_Store` 및 Obsidian UI 상태 파일 노이즈를 제외함

## 2. Obsidian Git 실제 설정 상태
- 설정 파일: [`.obsidian/plugins/obsidian-git/data.json`](/Users/jayden/Workspace/github-page/.obsidian/plugins/obsidian-git/data.json)
- 반영값:
  - `autoSaveInterval = 15`
  - `autoPullOnBoot = true`
  - `autoPushInterval = 0`
  - `autoPullInterval = 0`
  - `pullBeforePush = true`

### 의미
- 15분 간격으로 자동 커밋/푸시
- Obsidian 시작 시 원격 pull
- 실행 중 자동 pull은 아님

## 3. Git 인증 문제 최종 해결 방식
- 초기 핸드오버 문서에는 PAT를 remote URL에 직접 삽입하는 방향이 제안되어 있었음
- 실제 적용은 그보다 안전한 **로컬 credential helper 분리 방식**으로 진행함

### 현재 적용 상태
- 설정 파일: [`.git/config`](/Users/jayden/Workspace/github-page/.git/config)
- 원격 URL:
  - `https://jaeyoon@github.com/jaeyoon/jaeyoon.github.io.git`
- credential helper:
  - `store --file=.git/credentials`

### 효과
- Mac 전역 Keychain 계정과 충돌하지 않음
- 이 저장소에서만 별도 PAT 사용
- Obsidian Git 자동 push가 안정적으로 동작

### 검증 결과
- PAT 저장 후 `git ls-remote origin HEAD` 성공
- `git push origin main` 성공
- GitHub Pages 사이트 반영 확인

## 4. Shell Commands 번역 환경 개선
- 설정 파일: [`.obsidian/plugins/obsidian-shellcommands/data.json`](/Users/jayden/Workspace/github-page/.obsidian/plugins/obsidian-shellcommands/data.json)

### 변경 전 문제
- 기존 방식은:
  - `export PATH="/opt/homebrew/bin:$PATH" && /opt/homebrew/bin/gemini "... {{selection}}"`
- `{{selection}}`을 직접 명령행 인자로 넣기 때문에 따옴표/줄바꿈/긴 문자열에서 깨질 가능성이 있었음

### 1차 변경
- PATH augmentation:
  - `environment_variable_path_augmentations.darwin = /opt/homebrew/bin`
- alias:
  - `Gemini translate selection (KO to EN)`
- 명령:
  - 래퍼 스크립트 호출 방식으로 전환
- 입력:
  - `stdin = {{selection}}`
- 출력:
  - `current-file-caret`

### 효과
- Obsidian GUI PATH 문제 완화
- 선택 텍스트 escaping 안정성 향상
- 선택 후 실행 시 본문에 번역문 치환되는 구조 유지

### 2차 변경: 래퍼 스크립트 + 다중 명령 구조
- 기존 단일 스크립트는 폐기하고, 현재는 아래 구조로 동작
  - 셸 래퍼: [`scripts/gemini_selection_transform.sh`](/Users/jayden/Workspace/github-page/scripts/gemini_selection_transform.sh)
  - 실제 로직: [`scripts/llm_selection_transform.py`](/Users/jayden/Workspace/github-page/scripts/llm_selection_transform.py)
- Obsidian Shell Commands에는 현재 3개 명령이 등록됨
  - 이후 톤 전용 명령까지 추가되어 현재는 4개 명령 구조
  - `Gemini translate selection (KO to EN)`
  - `Gemini make selection shorter`
  - `Gemini make selection more detailed`
  - `Gemini rewrite selection with tone`

### 실행 피드백 개선
- 사용자가 "실행 중인지 알기 어렵다"는 피드백을 줌
- 이에 따라 각 명령의 `execution_notification_mode`를 `permanent`로 설정
- 실행 중에는 `Executing: ...` 알림이 뜨고, 완료 시 자동으로 사라지게 구성
- 플러그인 전체 기본값은 `if-long`으로 두되, 위 3개 명령은 개별적으로 `permanent` 적용

### 폴백 체인
- 사용자가 `gemini` CLI는 토큰/트래픽/과부하로 중단이 잦다고 피드백
- `codex` CLI는 현 환경에서 번역 단발 호출 시 panic / state db / permission 문제로 불안정해 보였으므로 일단 제외
- 현재 적용된 순차 폴백:
  1. `gemini` 기본 모델
  2. `gemini-2.5-flash`
  3. `claude -p --bare --tools ""`

### 폴백 구현 판단 근거
- `gemini` CLI는 로컬에서 가장 먼저 정상 응답 확인
- `gemini flash`는 더 가벼운 fallback으로 적합
- `claude` CLI는 비대화형 출력 구조는 적합하지만, 테스트 당시 `Not logged in` 상태였음
- 따라서 최종 폴백 체인은 구현해 두되, 실제 마지막 fallback이 동작하려면 사용자 측 Claude 로그인 필요

### stderr 노이즈 처리
- `gemini`는 번역 본문과 별개로 MCP/credential 관련 잡음 로그를 `stderr`에 출력함
- 초기에는 Obsidian notification으로 이 로그가 잠깐 표시됨
- 현재는 `llm_selection_transform.py` 내부에서 알려진 Gemini stderr 패턴을 필터링하여 불필요한 잡음은 숨김
- 실제 오류만 notification으로 전달되도록 조정

### 커스텀 스타일 지시문 문법
- 사용자가 선택 텍스트 끝에 스타일/톤 지시를 붙일 수 있게 추가 구현
- 현재 문법:
  - `<<...>>`
- 예시:
  - `This recording shows four parallel agents generating four Alert Multiselector iterations (v1-v4) via the Figma MCP on pencil.dev. <<너무 딱딱하지 않은 캐주얼한 블로그 톤으로>>`

### 왜 `<<...>>`를 선택했는가
- `[[...]]`는 Obsidian 링크 문법과 충돌
- `{...}`는 코드/템플릿 문맥과 섞이기 쉬움
- `<<...>>`는 Markdown과의 충돌이 상대적으로 적고 육안으로 구분하기 쉬움

### 지시문 처리 규칙
- 현재는 **선택 텍스트 맨 끝에 붙은 `<<...>>` 블록만** 스타일 지시문으로 인식
- 여러 개도 허용:
  - `<<캐주얼하게>> <<너무 장황하지 않게>>`
- 본문 중간의 `<<...>>`는 지시문으로 쓰는 용도가 아님

### 톤 전용 재작성 명령
- 사용자가 "기존 영어 문장 뒤에 `<<...>>`만 붙여 톤을 바꿀 수 있느냐"는 요구를 추가로 제시
- 이에 따라 길이를 크게 바꾸지 않고 의미를 유지한 채 스타일만 재작성하는 전용 모드 `rewrite`를 추가함
- Obsidian 명령명:
  - `Gemini rewrite selection with tone`
- 사용 의도:
  - 이미 영어인 문장에 대해
  - `<<프로페셔널한 톤으로>>`
  - `<<캐주얼한 블로그 톤으로>>`
  같은 지시만 붙여 재작성

### 톤 전용 명령 사용 예시
- 입력:
  - `Even though Claude and Codex started with the exact same MCP calls and inputs, ... <<프로페셔널한 톤으로>>`
- 실행:
  - `Gemini rewrite selection with tone`
- 기대 결과:
  - 길이는 크게 변하지 않음
  - 핵심 의미 유지
  - 선택한 톤만 반영한 영어 문장으로 치환

### 언어 고정 처리
- `translate`는 한국어 원문을 영어로 번역
- `shorten` / `expand`는 입력이 영어 문장이라는 전제
- 한국어 지시문이 붙어도 출력 언어가 흔들리지 않도록:
  - `shorten`
  - `expand`
  에는 "출력은 반드시 영어로만"이라는 제약을 프롬프트에 추가함

### 실제 검증 결과
- 번역 테스트:
  - 입력: `이 기능은 사용자의 반복 작업을 줄여 줍니다.`
  - 출력: `This feature streamlines repetitive tasks for users.`
- 축약 테스트:
  - 출력: `This feature streamlines repetitive user tasks.`
- 상세화 테스트:
  - 설명적인 영어 문장으로 확장 정상
- 스타일 지시문 테스트:
  - `<<너무 딱딱하지 않은 캐주얼한 블로그 톤으로>>` 지시를 붙여 상세화 시도
  - 초기 1회는 출력 언어가 한국어로 흔들렸으나, 이후 프롬프트 보강으로 영어 출력 고정 확인
- 톤 전용 rewrite 테스트:
  - 기존 영어 문단 뒤에 `<<프로페셔널한 톤으로>>`를 붙여 실행
  - 결과가 더 정제된 professional register로 재작성되는 것 확인

## 5. `.gitignore` 정리
- 파일: [`.gitignore`](/Users/jayden/Workspace/github-page/.gitignore)

### 추가 항목
- `.DS_Store`
- `**/.DS_Store`
- `.obsidian/workspace.json`
- `.obsidian/graph.json`

### 의도
- Finder 메타파일과 Obsidian UI 상태 파일은 자동백업 노이즈가 크므로 추적 제외
- 플러그인 설정 자체는 계속 Git으로 관리

## 6. 웹 이미지 미표시 문제와 자동교정
- 문제 원인:
  - Obsidian에서는 `![[image.png]]`가 보이지만
  - GitHub Pages 정적 웹 프리뷰에서는 이 문법을 일반 Markdown 이미지로 처리하지 않음

### 예시 문제
- `![pencil 4 agents 1](</assets/pencil-4-agents-1.png>)`
- `![장비배치](</assets/T2-side/장비배치.png>)`

### 해결 방식
- Hook 파일: [`.githooks/pre-commit`](/Users/jayden/Workspace/github-page/.githooks/pre-commit)
- 변환 스크립트: [`scripts/convert_obsidian_embeds.py`](/Users/jayden/Workspace/github-page/scripts/convert_obsidian_embeds.py)
- Git hook 경로:
  - `.git/config`의 `core.hooksPath = .githooks`

### 동작 방식
- staged 된 `.md` 파일만 검사
- `![[...]]` 중 이미지 임베드만 탐지
- repo 내부 실제 파일 경로를 찾아
  - `![alt](</notes/assets/foo.png>)`
  - `![alt](</assets/bar.png>)`
  형태로 자동 변환
- 변환 후 hook이 다시 `git add`

### 결과
- 사용자는 Obsidian에서 계속 드래그 앤 드롭으로 이미지 삽입 가능
- 작성 시점에는 `![[...]]` 그대로여도 됨
- 커밋 시점에 웹 호환 Markdown으로 자동 교정됨
- 사용자 테스트 결과 정상 동작 확인

## 7. 명령명 혼동 포인트
- Obsidian Git 버전에 따라 명령명이 다르게 보일 수 있음
- 이 환경에서는 `Create backup` 대신 `Git: Commit-and-sync` 계열이 표시되었음
- `Git: Commit-and-sync and then close Obsidian`는 실제로 앱 종료 명령이며, 크래시가 아니라 정상 동작임

## 8. GitHub → 로컬 동기화 주의
- 현재는:
  - Obsidian 시작 시 pull
  - 실행 중 자동 pull 없음
- 따라서 GitHub에서 수정 후 로컬에 반영하려면:
  - Obsidian 재시작
  - 또는 수동 `Git: Pull`

## 9. 실제 검증된 상태
- 신규 노트 작성 후 사이트 반영 확인
- `assets/` 및 `assets/T2-side/` 이미지 반영 확인
- Obsidian 위키 임베드 자동교정 후 웹 표시 확인
- hook 자동교정 테스트 정상

## 10. 향후 추가 개선 후보
- 실행 중 주기적 pull이 필요하면 `autoPullInterval` 설정
- 비디오 임베드까지 자동교정 확장 가능
- 일반 문서 위키링크 `[[...]]` 웹 호환화가 필요하면 별도 변환 로직 추가 가능
- Claude CLI를 실제 fallback으로 쓰려면 사용자 측 로그인 상태를 점검할 필요 있음
- `<<...>>` 지시문을 본문 중간이나 프론트매터 수준까지 확장할지는 별도 정책 필요
