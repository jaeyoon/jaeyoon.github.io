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

### 변경 후
- PATH augmentation:
  - `environment_variable_path_augmentations.darwin = /opt/homebrew/bin`
- alias:
  - `Gemini translate selection`
- 명령:
  - `gemini --prompt "위 한국어 원문을 자연스럽고 세련된 영어로 번역해줘. 부가 설명 없이 번역문만 출력해."`
- 입력:
  - `stdin = {{selection}}`
- 출력:
  - `current-file-caret`

### 효과
- Obsidian GUI PATH 문제 완화
- 선택 텍스트 escaping 안정성 향상
- 선택 후 실행 시 본문에 번역문 치환되는 구조 유지

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
