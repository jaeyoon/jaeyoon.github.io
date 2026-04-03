---
layout: page
title: "OpenPencil.dev 테스트"
permalink: /notes/openpencil-pencil-stitch_KR/
---

### OpenPencil.dev  (www.openpencil.dev)

| 테스트 요소                | OpenPencil 결과                                     | Figma MCP 대비 판정                      |
| --------------------- | ------------------------------------------------- | ------------------------------------ |
| 1. Alert Overlay      | 구조, 텍스트, 상태, 아이콘까지 꽤 잘 읽음                         | 가장 잘 된 케이스. 거의 실사용 가능                |
| 2. local-navigation   | 구조와 variant 수는 읽지만 실제 라벨은 placeholder로 흔들림        | 구조는 됨, 의미 복원은 약함                     |
| 3. AppLayout          | shell hierarchy는 잘 읽지만 내부 메뉴/탭/헤더 의미가 평준화됨        | shell parser로는 유효, truth source로는 부족 |
| 4. Fullwidth content  | 거의 배경 shell만 남고 내부 content expansion 실패           | 사실상 실패                               |
| 5. Detached component | 3컬럼 구조와 block 반복은 풀리지만 실제 운영 텍스트는 여전히 placeholder | 4번보다 개선됐지만, 의미 복원은 여전히 실패            |

> 테스트용 샘플들..  

1. Auto Layout frame
- 단순한 프레임 Auto Layout 구조, 각 행은 텍스트와 아이콘 인스턴스.
- A simple Auto Layout frame structure, with each row comprising text and icon instances.

<img src="/notes/assets/Pasted image 20260403102807.png" alt="Pasted image 20260403102807" width="198">

2. Variable Components
- 6개 Variables 로 분류된 디자인. (swap용)
- Design categorized by 6 variables (for swapping).

![Pasted image 20260403102748](</notes/assets/Pasted image 20260403102748.png>)

3. Shell component
- 인스턴스 swap 으로 각 화면별 디자인을 담을수 있는 Shell 디자인 프레임.
- A Shell design framework capable of accommodating screen-specific designs through instance swapping.

![Pasted image 20260403102759](</notes/assets/Pasted image 20260403102759.png>)


4. 3의 디자인에 swap 으로 배치될 풀스크린 디자인
![Pasted image 20260403103053](</notes/assets/Pasted image 20260403103053.png>)

5. 4의 디자인 구조 분석에 어려움이 있어 detach 인스턴스로 재시도. (구조는 좌측 레이어 참조)
![Pasted image 20260403104150](</notes/assets/Pasted image 20260403104150.png>)


---
**패턴**  

- 단순하고 detached된 컴포넌트일수록 OpenPencil이 잘 읽음.
- variant와 override 늘어나면 텍스트 의미 혼란스러워짐.
- nested instance로 들어가면 구조는 남아도 semantic content 누락됨.
- full page, settings screen, override-heavy UI에서는 Figma MCP와 격차 크게 벌어짐.

**결론**

- 1과 같은 단순구조의 인스턴스 분석용으로는 OpenPencil도 꽤 쓸만함.
- 2-3. 과 같은 정도의 복잡도 있는 요소부터는 “구조는 읽는데 의미는 못 살림” 쪽에 가까움.
- 4-5 Fullwidth 계열에서는 OpenPencil이 parser 성격 강하게 드러냄, Figma MCP만이 안정적인 truth source 역할 할 수 있어 보임.