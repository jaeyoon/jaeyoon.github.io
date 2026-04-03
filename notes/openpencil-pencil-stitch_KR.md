## draft
| 테스트                                              | OpenPencil 결과                                     | Figma MCP 대비 판정                      |
| ------------------------------------------------ | ------------------------------------------------- | ------------------------------------ |
| 1. Alert Overlay                                 | 구조, 텍스트, 상태, 아이콘까지 꽤 잘 읽음                         | 가장 잘 된 케이스. 거의 실사용 가능                |
| 2. local-navigation                              | 구조와 variant 수는 읽지만 실제 라벨은 placeholder로 흔들림        | 구조는 됨, 의미 복원은 약함                     |
| 3. AppLayout                                     | shell hierarchy는 잘 읽지만 내부 메뉴/탭/헤더 의미가 평준화됨        | shell parser로는 유효, truth source로는 부족 |
| 4. Fullwidth-content in AppLayout                | 거의 배경 shell만 남고 내부 content expansion 실패           | 사실상 실패                               |
| 5. Detached-frame-component / detached fullwidth | 3컬럼 구조와 block 반복은 풀리지만 실제 운영 텍스트는 여전히 placeholder | 4번보다 개선됐지만, 의미 복원은 여전히 실패            |
1. Alert Overlay
![Pasted image 20260403102807|313](<assets/Pasted image 20260403102807.png>)

2. local-navigation
![Pasted image 20260403102748](<assets/Pasted image 20260403102748.png>)

3. AppLayout
![Pasted image 20260403102759](<assets/Pasted image 20260403102759.png>)


4. Fullwidth-content in AppLayout
![Pasted image 20260403103053](<assets/Pasted image 20260403103053.png>)

5. Detached-frame-component / detached fullwidth
![Pasted image 20260403104150](<assets/Pasted image 20260403104150.png>)


>전: 

핵심 패턴은 일관적입니다.

- 단순하고 detached된 컴포넌트일수록 OpenPencil이 잘 읽습니다.
- variant와 override가 늘어나면 먼저 텍스트 의미가 흔들립니다.
- nested instance로 들어가면 구조는 남아도 semantic content가 빠집니다.
- full page, settings screen, override-heavy UI에서는 Figma MCP와 격차가 크게 벌어집니다.

한 줄 결론으로 줄이면 이렇습니다.

- Alert Overlay만 보면 OpenPencil도 꽤 강합니다.
- local-navigation, AppLayout부터는 “구조는 읽는데 의미는 못 살린다”가 맞습니다.
- Fullwidth 계열에서는 OpenPencil이 parser 성격을 강하게 드러내고, Figma MCP만이 안정적인 truth source 역할을 합니다.

실무 포지셔닝도 5개 결과를 종합하면 명확합니다.

- Figma MCP: 실제 구현 기준, truth source
- OpenPencil: 구조 추출, skeleton 파악, 전처리용 parser

---
> 후:

핵심 패턴은 일관적으로 보임.

- 단순하고 detached된 컴포넌트일수록 OpenPencil이 잘 읽
- variant와 override가 늘어나면 먼저 텍스트가 혼란스러워짐
- nested instance로 들어가면 구조는 남아도 semantic content는 누락됨.
- full page, settings screen, override-heavy 요소들에서는 Figma MCP와 격차가 크게 벌어집니다.

한 줄 결론,

- 단순 요소 예) Alert Overlay만 보면 OpenPencil 는 쓸만함.
- local-navigation, AppLayout부터는 “구조는 읽는데 의미는 못 살림" 쪽에 가까움.
- Fullwidth 계열에서는 OpenPencil이 parser 성격을 강하게 드러내고, Figma MCP만이 안정적인 truth source 역할을 할수 있어 보임.

실무 포지셔닝은 5개 결과를 종합했을때,
- Figma MCP: 실제 구현 기준, truth source
- OpenPencil: 구조 추출, skeleton 파악, 전처리용 parser

