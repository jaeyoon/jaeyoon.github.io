# 2026-03-23 Integrated Design Pipeline Final Report

Date: 2026-03-23
Workspace: `/Workspace/uimorph`

## Executive Summary

이번 테스트는 Stitch만 따로 본 실험이 아니었다.

실제로는 아래 세 단계를 하나의 파이프라인으로 검증한 셈에 가깝다.

1. OpenPencil로 기존 `.fig` 구조를 읽고 분석한다
2. Pencil로 그 구조를 재현하고 controlled variation을 만든다
3. Stitch로 같은 구조를 바탕으로 더 넓은 생성형 variation과 MCP 자동화 가능성을 검증한다

이번 시점의 종합 결론은 다음과 같다.

- OpenPencil은 구조 분석 엔진으로 유의미했다
- Pencil은 구조를 붙잡고 재현 fidelity를 높이는 쪽에서 가장 안정적이었다
- Stitch는 구조를 바탕으로 시안을 빠르게 넓히는 데는 강점이 있었다
- 하지만 타이트한 UI/UX 재현 툴로 바로 쓰기에는 아직 한계가 있었다

즉 이번 테스트의 핵심 성과는 "AI가 기존 UI를 완벽히 대체했다"가 아니라, "기존 구조를 분석하고, 사람 기준으로 정리한 뒤, 그 위에서 AI variation을 설계하는 파이프라인이 실제로 가능하다"는 점을 확인한 데 있다.

## Scope Of This Final Report

이 문서는 아래 실험들을 통합해 최종 평가를 내린다.

- OpenPencil의 `.fig` 구조 분석 테스트
- Pencil 재현 테스트 1차 / 2차 / 3.5 variation 테스트
- Stitch SDK reproduction / variation 테스트
- Stitch MCP 연결 및 생성/편집/저장 검증

주요 근거 문서:

- [openpencil-isms-sidemenu-note.md](/Workspace/uimorph/task-logs/openpencil-isms-sidemenu-note.md)
- [pencil-test01-review.md](/Workspace/uimorph/task-logs/pencil-test01-review.md)
- [pencil-test02-review.md](/Workspace/uimorph/task-logs/pencil-test02-review.md)
- [pencil-test035-review.md](/Workspace/uimorph/task-logs/pencil-test035-review.md)
- [ai-design-generation-flow-comparison.md](/Workspace/uimorph/task-logs/ai-design-generation-flow-comparison.md)
- [2026-03-23-stitch-session-log.md](/Workspace/uimorph/task-logs/2026-03-23-stitch-session-log.md)
- [stitch-sdk-reproduction-review.md](/Workspace/uimorph/task-logs/stitch-sdk-reproduction-review.md)
- [stitch-sdk-variation-review.md](/Workspace/uimorph/task-logs/stitch-sdk-variation-review.md)
- [2026-03-23-stitch-mcp-validation.md](/Workspace/uimorph/task-logs/2026-03-23-stitch-mcp-validation.md)

## What We Actually Learned

### 1. Structure Transfer Was The Real Success

이번 실험에서 가장 잘 된 것은 "구조 전달"이었다.

OpenPencil로 읽은 구조 정보를 바탕으로 Pencil과 Stitch 모두 아래 요소를 비교적 안정적으로 유지했다.

- 메뉴 개수
- 메뉴 순서
- 한국어 라벨
- 선택 상태
- 비활성 상태
- 하단 프로필 블록

즉 AI 생성 결과가 픽셀 퍼펙트 복제는 아니어도, "이 UI가 어떤 의미 구조를 가진 navigation shell인가"는 꽤 잘 전달되었다.

이건 단순한 부수 효과가 아니라, 이번 테스트의 본질적인 성과다.

왜냐하면 실무적으로 더 중요한 건 "기존 UI를 그대로 베끼는 것"보다, "기존 구조를 분석 가능하고 재사용 가능한 형태로 모델에 전달하는 것"이기 때문이다.

### 2. Visual Fidelity Was The Weak Point

반대로 시각 fidelity는 세 도구 모두 한계가 있었다.

공통적으로 문제였던 지점:

- 서체 크기와 폭 감각
- 컬러 톤의 미세한 인상 차이
- 상태 표현의 밀도
- 아이콘 fidelity
- preview framing 일관성

특히 "구조는 맞는데 느낌이 다르다"는 문제가 반복됐다.

실무적으로는 이 부분이 크다.

UI/UX는 정보 구조만 맞는다고 같은 제품처럼 보이지 않는다. 상태, 리듬, 타이포, 그림자, 아이콘의 질감까지 맞아야 비로소 같은 제품으로 읽힌다.

## Tool-By-Tool Evaluation

## OpenPencil

### What It Did Well

OpenPencil은 `.fig` 직접 분석 도구로서 의미 있는 역할을 했다.

확인된 강점:

- `.fig` 파일 파싱 성공
- page / node 구조 파악 가능
- 반복 메뉴 버튼 패턴 탐지 가능
- 특정 노드 단위 조회 가능
- SVG / JSX export 가능
- AI 입력용 전처리 데이터 생성에 유리

이 관점에서 OpenPencil은 "분석 엔진"으로 충분히 가치가 있었다.

### Limits

하지만 시각 재현 도구로는 분명한 한계가 있었다.

주요 한계:

- 인스턴스 텍스트 override 복원 부정확
- 메뉴 텍스트가 기본값으로 읽히는 문제
- 상태별 색상 override 복원 부정확
- 변수 값 해석이 `undefined`로 남는 경우 다수
- PNG 렌더 결과의 텍스트 fidelity 부족

따라서 OpenPencil은 이번 파일에서 다음 용도로 보는 게 맞다.

- 구조 분석
- 상태 점검
- 부분 추출
- AI 입력 전처리

반대로 아래 용도로는 보수적으로 보는 편이 맞다.

- 픽셀 퍼펙트 복제
- override가 많은 컴포넌트의 완전 복원
- 변수 기반 스타일의 정확한 렌더

## Pencil

### Reproduction Quality

이번 테스트에서 재현 fidelity가 가장 좋았던 쪽은 Pencil이었다.

특히 1차에서 2차로 갈수록 아래가 눈에 띄게 개선됐다.

- 메뉴 라벨 9개와 순서 정확도
- 선택/비활성 상태 유지
- 아이콘이 generic icon font에서 path 기반 벡터로 개선
- 메뉴/프로필 텍스트를 `Pretendard`로 정리
- 아바타가 원본과 유사한 그룹/패스 구조로 개선

즉 Pencil은 단순한 "의미 복제"를 넘어서, 실제 원본에 가까운 fidelity pass를 꽤 반영할 수 있었다.

### Remaining Gaps

그럼에도 완전한 재현은 아니었다.

끝까지 남았던 문제:

- 버튼 내부 `icon 위 / label 아래` 구조 보정 이슈
- selected button shadow가 `inset`이 아니라 `outer`로 남는 문제
- 일부 아이콘이 여전히 icon font 기반
- 메뉴와 프로필 사이 간격이 원본보다 느슨한 경우

하지만 이건 "구조는 맞고, 세밀한 시각 디테일이 남아 있는 상태"에 가까웠다.

즉 Pencil은 세 도구 중 가장 실무적인 reproduction 기준점으로 쓸 수 있었다.

### Variation Quality

Pencil 3.5 variation 테스트도 의미가 있었다.

확인된 점:

- variation 보드 형태로 여러 방향을 유지할 수 있었다
- 구조 오류를 줄이면서 variation 차이를 만들 수 있었다
- state preview와 버튼 구조를 더 정교하게 보정할 수 있었다

즉 Pencil은 variation 생성도 가능하지만, 그 강점은 Stitch처럼 폭발적 생성력보다는 "구조와 규칙을 유지하는 controlled variation"에 있다.

## Stitch

### Reproduction

Stitch는 reproduction에서 구조는 생각보다 잘 따라왔다.

유지된 요소:

- 메뉴 개수와 순서
- 선택 상태
- 비활성 상태
- 프로필 블록

하지만 reproduction 품질 자체는 기대보다 약했다.

아쉬웠던 점:

- typography가 섬세하지 못함
- 컬러/상태 인상이 generic하게 흐름
- legacy operator-console 무드 fidelity 부족
- preview framing inconsistency

즉 Stitch는 "구조 이해"는 괜찮았지만, "정교한 재현"은 부족했다.

### Variation

반대로 Stitch의 진짜 강점은 variation 생성에서 더 잘 드러났다.

좋았던 점:

- 시각 방향을 빠르게 3안 이상으로 전개할 수 있었다
- dark / alternate / polished / terminal-like 등 mood 분기가 빨랐다
- SDK / MCP 기반 자동화 파이프라인에 붙이기 좋았다

하지만 variation 품질도 완벽하진 않았다.

아쉬웠던 점:

- typography와 spacing 감각이 기대보다 평범함
- 일부 안은 generic SaaS 스타일로 미끄러짐
- framing consistency가 약함
- screenshot PNG와 실제 HTML framing이 어긋남

즉 Stitch는 "creative breadth"는 강하지만, "controlled fidelity"는 약하다.

### MCP Validation

Stitch MCP는 이번에 실제로 연결과 쓰기까지 검증됐다.

확인된 점:

- `create_project`, `generate_screen_from_text`, `generate_variants`, `edit_screens`, `get_screen` 모두 동작
- HTML / screenshot URL 회수 가능
- 결과를 로컬 파일로 다시 저장 가능

하지만 운영상 중요한 제약도 확인됐다.

- Stitch 웹은 MCP 결과를 현재 열린 프로젝트 화면에 즉시 live-refresh 하지 않는 것으로 보임
- 프로젝트 재진입 또는 브라우저 리프레시 후 결과가 보이는 경우가 있었음
- HTML은 sidebar-only에 가깝지만 PNG는 넓은 preview canvas를 유지했음

즉 Stitch MCP는 "기능적으로는 가능"하지만, 웹 UI 반영 경험까지 매끄러운 상태는 아니었다.

## Relative Assessment

세 도구를 한 문장씩 요약하면 이렇다.

- OpenPencil: 구조를 읽는 도구
- Pencil: 구조를 붙잡고 다듬는 도구
- Stitch: 구조를 바탕으로 상상력을 넓히는 도구

좀 더 직설적으로 말하면:

- 분석: OpenPencil이 가장 유용했다
- 재현: Pencil이 가장 낫다
- 폭넓은 variation: Stitch가 가장 빠르다

이번 테스트를 통해 처음 세웠던 가설, 즉 "기존 디자인 규칙을 유지하는 variation은 Pencil이 더 유리하고, 탐색형 variation은 Stitch가 더 유리하다"는 가설은 대체로 맞았다고 본다.

## My Opinion

내 평가는 당신이 느낀 것과 거의 같다.

재현 품질만 놓고 보면, 이번 결과에서는 Pencil 쪽이 더 나았다.

정확히 말하면:

- Stitch가 구조를 이해하는 능력은 생각보다 괜찮았다
- 하지만 UI를 설계물로서 완성시키는 감각은 아직 아쉬웠다
- 특히 서체, 컬러, 상태 밀도, 전체 무드의 정교함은 Pencil 쪽이 더 믿을 만했다

그래서 지금 단계의 Stitch를 "UI/UX 대체 생성기"로 보는 건 과장이다.

반면 Stitch를 "정의된 구조를 받아 다양한 방향의 시안을 빠르게 확장하는 보조 엔진"으로 보는 건 충분히 현실적이다.

즉 현재 기준의 판단은 아래와 같다.

- reproduction engine로서의 Stitch: 아직 부족
- structured ideation engine로서의 Stitch: 충분히 유망
- controlled refinement tool로서의 Pencil: 가장 실무적
- structural analysis tool로서의 OpenPencil: 충분히 의미 있음

## Practical Product Interpretation

지금 단계에서 Stitch 같은 생성형 도구의 강점은, 정형화된 UI를 그대로 복제하는 데 있지 않다.

오히려 아래 같은 프로젝트에서 더 강점이 있을 가능성이 높다.

- 자유도가 높은 시안 탐색
- creative direction experimentation
- visual language exploration
- 빠른 mood variation 생성
- 이미지를 포함한 넓은 표현 자유도를 가진 프로젝트

반대로 아래 같은 프로젝트에서는 한계가 더 빨리 드러난다.

- 구조적으로 매우 타이트한 admin / ops / enterprise UI
- 상태 표현이 엄격한 UI shell
- typography / spacing / color precision이 중요한 작업
- 기존 제품과의 시각 continuity가 중요한 프로젝트

즉 Stitch는 "자유로운 디자인 시안 생성기"로는 상당히 강력할 수 있지만, 지금 단계에서 바로 구조적으로 엄격한 UI/UX를 대체하는 실무 툴로 보기에는 한계가 있다.

## Recommended Direction

이번 결과를 종합하면, 앞으로의 가장 설득력 있는 방향은 아래라고 본다.

1. OpenPencil을 더 적극적으로 활용해 기존 디자인의 구조를 최대한 정확히 읽고 정리한다
2. Pencil에서 그 구조를 사람이 검증 가능한 수준까지 정밀하게 구성한다
3. 그 다음 Stitch에는 "구조를 깨지 않는 범위 안에서의 새로운 UX / visual option 제안"만 맡긴다
4. 즉 AI가 원본을 직접 대체하게 하기보다, 구조적으로 정리된 기반 위에서 파생안을 제안하도록 만든다

이 방향이 좋은 이유는 분명하다.

- 구조 fidelity는 사람이 통제할 수 있다
- AI는 creativity와 option generation에 집중할 수 있다
- 각 도구의 강점을 분리해서 쓸 수 있다

이건 단순한 타협이 아니라, 현재 기술 상태에 맞는 더 현실적인 제품 전략에 가깝다.

## Final Conclusion

이번 통합 테스트의 최종 결론은 아래처럼 정리할 수 있다.

OpenPencil, Pencil, Stitch는 서로 경쟁하는 단일 대체재라기보다, 서로 다른 위치에서 강점을 가진 보완재에 가깝다.

현재 가장 현실적인 역할 분담은 다음과 같다.

- OpenPencil: 기존 디자인 분석
- Pencil: 구조적 재현과 controlled refinement
- Stitch: exploratory variation과 creative expansion

즉 앞으로의 발전 방향은 "AI에게 기존 UI/UX를 통째로 맡기는 것"보다, "구조는 단단히 고정하고 그 위에서 파생 UX와 visual variation을 AI가 제안하게 만드는 것"이 더 적절해 보인다.

이번 시점의 한 줄 결론:

OpenPencil은 구조를 읽고, Pencil은 구조를 붙잡고, Stitch는 구조 위에서 넓게 상상하는 도구다.
