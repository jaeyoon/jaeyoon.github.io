• 목적: 생성형 AI가 레거시 디자인을 실무 수준으로 구조화·개선·시스템화 가능한지 Codex / Claude로 검증

자유도가 높은 환경에서는 생성형 AI가 상당히 근사한 디자인을 뽑아내지만,
기존 레거시 디자인의 시스템화·개선 가능 여부를 실무 수준에서 확인하기 위해 Codex, Claude 각각 테스트 진행.

⸻

	1.	input

	•	기존 Figma 디자인 (.fig의 node & section)
	•	URL (HTML) – 테스트 목적의 단순 구조 웹사이트
	
<!-- img width="2032" height="1317" alt="Screenshot 2026-03-31 at 5 27 13 PM" src="https://github.com/user-attachments/assets/33c41dff-5c8d-4ab2-a416-69a0dcc058a0" /-->


	2.	분석 (분해)
입력 데이터를 기반으로 아래 항목을 분리하여 추출

	•	Figma: layout 구조, component 구조, token
	•	URL: 스크린샷 없이 JSON, TSX 추출

	3.	시스템 생성
2의 결과를 기반으로 Figma에 디자인 시스템 생성

	•	token system
	•	component system
	•	layout rule

	4.	Variant 생성
3의 결과 기반, 에이전트에 위임하여 2개 시안 생성

	•	A: 기존 구조 유지, 스타일만 변경
	•	B: 컴포넌트 구조 개선

	5.	Output (실행)

	•	구조 기반 UI 생성
	•	컴포넌트화 결과
	•	최종 UI 결과

출력 경로
	•	Figma (write to canvas)
	•	pencil.dev API
	•	Google Stitch SDK

⸻

	•	3개 모두 현업 적용 기준에서는 디테일 처리 부족, 재현 수준으로 미세조정 시 상당한 토큰·시간 소요
	•	캔버스 사이즈, radius, 서체 조정 등은 미세조정에도 한계 존재
	•	의도적으로 한글 서체(Pretendard) 테스트 시 CDN 적용에도 불구하고 인식 실패 케이스 발생
	•	프롬프트에 생성 위치를 명시하지 않으면 기존 요소를 인식하지 못하고 덮어쓰는 문제 발생
	•	벡터 아이콘 등 미세 요소 누락
	•	생각보다 시간과 토큰 소비가 큼
생성 시작 ~ 종료 타임스탬프 기준 추적
분석 단계 (input → variant 완료)
케이스 / Claude / Codex
	•	node/sidemenu → 15분 / 11분
	•	section/1-desktop → 11분 / 12분
	•	section/2-alarm-list → 9분 / 14분
	•	url/warp → 8분 / 13분
	•	합계 → 43분 / 50분

⸻

takeaways

pros:
	•	google stitch는 창의성이 요구되는 초기 시안 생성에 매우 유용 (러프한 입력도 꽤 잘 정리함)
	•	stitch & pencil: 취향/브랜딩이 크게 중요하지 않은 “적당한 SaaS형 비주얼”은 빠르게 안정적으로 생성
	•	세부 요소 재현은 부족하지만 레이아웃 등 구조적 특징은 비교적 잘 유지됨

cons:
	•	radius, crop area 등 정확한 값을 넣어도 stitch, pencil에서 구조 이탈 발생 → 아직 불안정
	•	figma canvas는 상대적으로 정확도가 높은 편
	•	stitch는 AGNOSTIC deviceType에서 full-screen 캔버스를 기본 생성하는 것으로 보임
(예: “컴포넌트만 렌더링” 지시에도 2560×2048 전체 캔버스 생성)
	•	design token 기반 harness 구축 비용이 큼 → 결국 개발과 유사한 문제 구조

⸻

trivia
	•	pencil.dev는 스타트업 제품치고 꽤 완성도 높음 (a16z 느낌)
→ 기다리는 동안 parallel agents UI는 은근한 재미 + 위로감 있음
→ 단순 eye candy 이긴 하지만 API 호출 시 이 경험이 사라지는 점은 아쉬움

<video controls width="100%" autoplay muted loop playsinline>
  <source src="https://pub-b3f343132a0f482d88780d5a9ba50665.r2.dev/pencil-4-agents-1.mp4" type="video/mp4">
</video>

	•	속도 자체가 느리다기보다, AI 연산속도 대비 툴(MCP 등)과 인간 검토 속도가 병목
	•	잘 정리된 디자인 시스템/가이드라인은 앞으로
→ 실행 도구라기보다 인간의 중간 검토용, 포트폴리오 성격으로 수렴할 가능성



⸻

ai 디자인 활용 기저에 대한 고찰

대략 3가지로 정리 가능
	1.	효율성과 결과 중심 (Utilitarian View)
→ 사람이 하기 싫거나 오래 걸리는 일을 대체하여 생산성 극대화
	2.	상업적 목적 (Capitalist View)
→ 사용자의 체류 시간 증가 + 결제 유도
	3.	증강과 확장 (Augmentation View)
→ 인간이 할 수 없는 영역(초거대 데이터 분석, 대규모 시뮬레이션 등) 수행

다만 3번은 과학/예술 영역을 제외하면 결국 1,2에 종속되는 경우가 많고,
UI/UX는 본질적으로 ‘최적해’가 존재하는 상업 디자인 영역이기 때문에
장기적으로 인간 디자이너의 기여 영역은 점점 제한될 가능성이 높아 보임.
