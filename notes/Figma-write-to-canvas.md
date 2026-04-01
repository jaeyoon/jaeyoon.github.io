자유도가 높은 환경에서는 생성형 AI가 상당히 근사한 디자인을 뽑아내지만, 기존 레거시 디자인의 토큰화 및 시스템화 가능 여부를 확인하기 위해 Codex, Claude로 각각 자유분석을 맡기고 MCP 기반으로 캔버스에 직접 생성(write) 가능한 Figma, Stitch, Pencil로 디자인 테스트를 진행함.

> **순서:** 1. input → 2. 분석 → 3. 디자인시스템 생성 → 4. Variant 생성 → 5. Output

---

### 1단계
>• Figma 디자인 (MCP로 node/section 선택)  
• 웹사이트 URL (HTML 기반 테스트 대상)  

*(Input 소스)*


---

### 2단계  
입력 데이터를 기반으로 구조(JSON/TSX)로 변환  

>• Figma 디자인 (MCP로 node/section 선택 → layout/component/token 추출)  
• 웹사이트 URL (HTML → JSON/TSX 구조 변환, 스크린샷 없이)  

**결과:**
Claude와 Codex는 동일한 MCP 호출을 사용해 입력은 같았지만, 2단계에서 추출된 데이터 구성은 모델이 데이터를 해석하고 정리하는 방식에 따라 달라졌다. Claude는 이전 결과를 이어서 활용하며 더 넓은 토큰과 내부 구조까지 확장해 수집한 반면, Codex는 각 요청을 독립적으로 처리하며 핵심 구조 중심으로 정리했다. 즉 입력은 같았지만, 컨텍스트 활용 여부와 정리 전략을 모델이 어떻게 선택하느냐에 따라 결과 차이 발생.

**1-2단계 소요시간 (input + analysis)**

| 케이스 | Claude | Codex |
|--------|--------|--------|
| node / sidemenu | input 1m / analysis 5m = 6분 | input 2m / analysis 4m = 6분 |
| section / desktop | input 3m / analysis 1m = 4분 | input 3m / analysis 4m = 7분 |
| section / header | input 3m / analysis 1m = 4분 | input 4m / analysis 5m = 9분 |
| url / warp.dev | input 2m / analysis 1m = 3분 | input 3m / analysis 4m = 7분 |
| **합계** | **17분** | **29분** |

---

### 3단계 (디자인시스템)
분석 결과만 전달하여 각 에이전트에 생성 위임
> layout rule  
token system  
component system  

**결과:**  
Claude는 컴포넌트 구조를 세분화하고 위치·크기 등 구체적인 수치까지 포함해 실제 구현에 가까운 수준으로 확장한 반면, Codex는 전체 구조를 중심으로 핵심 흐름과 방향만 간결하게 정리하는 경향을 보임. Claude가 앞 단계에서 추출한 정보를 그대로 확장하는 방식이라면, Codex는 추출량과 무관하게 system 단계 자체를 요약 중심으로 처리하는 전략을 선택함. 미세조정없이 던진 프롬프트라 당연하지만, 양쪽 모델 모두 레이어 겹침, 누락, 레이아웃 이탈 등 퀄리티는 중간-낮음 수준.

---

### 4단계 (디자인 variant 생성)
구성된 시스템을 기반으로 “구조 유지 vs 재구성 능력” 비교 목적의 A/B 시안 생성.   
> • A: 기존 구조 유지, 스타일만 변경 (재현이 목적은 아니지만 성능 점검차원).  
• B: 컴포넌트 구조 개선 (loosely guided prompt). 

**결과:**
Claude는 A에서의 변경을 B로 이어가는 누적 구조로, 변경 사항과 유지 요소를 나누고 코드 수준까지 구체화하는 반면, Codex는 A와 B를 각각 독립된 방향으로 설정해 분위기와 컨셉 중심으로 빠르게 나눈다. 이 때문에 Claude는 이전 단계 정의를 이어받아 연속성이 높은 결과를 만들고, Codex는 각 시안을 하나의 완결된 제안으로 구성한다. 결과적으로 Claude는 바로 구현에 옮길 수 있는 변경 정리에 가깝고, Codex는 생성 툴에 바로 넣기 좋은 디자인 컨셉에 가깝다.


**3-4단계 소요시간 (system + variant)**
| 케이스 | Claude | Codex |
|--------|--------|--------|
| node / sidemenu | system 5m / variant 4m = 9분 | system 3m / variant 2m = 5분 |
| section / desktop | system 1m / variant 6m = 7분 | system 3m / variant 2m = 5분 |
| section / header | system 1m / variant 4m = 5분 | system 3m / variant 2m = 5분 |
| url / warp.dev | system 1m / variant 4m = 5분 | system 4m / variant 2m = 6분 |
| **합계** | **26분** | **21분** |


---

### 5단계 (실행)
각 툴의 주목적이 다르지만, MCP write 가능한 선택지가 제한적이기 때문에 같은 단계(Output)에서 비교함.  
>• Google Stitch  
• Pencil.dev  
• Figma (write to canvas)  
Stitch(생성) / Pencil(보정) / Figma write(정확 실행)  
 

**결과:**  
• 3개 모두 디테일 처리가 부족하며, 재현 수준으로 미세 조정 시 상당한 토큰·시간 소요  
• 캔버스 사이즈, radius, 서체 조정 등은 미세 조정에도 한계 존재 (Figma는 그중 가장 높은 수준으로 생성)  
• 생성 위치를 명시하지 않으면 기존 캔버스 위 요소를 인식하지 못하고 덮어쓰는 문제 반복 발생 (스크립트와 skill.md로 보완)  
• 벡터 아이콘 등 미세 요소 누락 및 변형  

---
### takeaways
• 레이아웃 등 구조적 특징은 비교적 잘 재현되지만, radius, margin, align 등 정확한 JSON 값을 넣어도 Stitch, Pencil에서 구조 이탈 발생  
• Figma write to canvas는 상대적으로 정확도가 높고 variables 생성도 안정적임  
• Stitch는 창의성이 요구되는 초기 시안 생성에 적합해보임, 낙서 수준의 스케치 이미지 입력도 안정적으로 생성됨  
• 한글 서체(Pretendard) 테스트 시 인식 실패 케이스 발생. Stitch는 CDN 입력으로 해결 가능했지만, Pencil은 로컬 폰트 기반 렌더링 제한으로 깨짐 발생 (결국 로컬 설치로 해결)  
• 현 시점에서 미세 조정의 한계로 인해 Stitch & Pencil은 취향/브랜딩이 크게 중요하지 않은 “SaaS형 비주얼”을 빠르게 생성하는 데는 충분히 현업 적용 가능 수준  
• design token 기반 harness 구축 비용이 큼. 프롬프트를 정교하게 다듬으면 높은 재현도는 가능하지만 비효율적  

### trivia
• pencil.dev는 스타트업 제품치고 꽤 완성도가 높은 결과물을 뽑아줌. 다만 매우 상식적인 툴 UX가 적용되지 않는 경우가 많음. parallel agents 효과는 마케팅 장치에 불과하지만, 기다리는 시간(bio token) 동안 은근한 재미와 위로감이 있음. API에서 아직 지원되지 않는 점이 아쉬움  
• .fig 분석을 위해 openpencil이라는 오픈소스 툴을 테스트해봤는데, 구조 분석 수준에서만 의미가 있었음. full seat 권한이 없을 때 구조 파악 용도로는 활용 가능했지만, 그 외에는 실효성이 낮게 느껴짐  
• 테스트 과정에서 모든 AI 생성 output 속도가 느렸는데, AI 자체의 지연이라기보다 연산 속도 대비 툴(MCP 등, 최적화되지 않은 프롬프트와 스크립트)과 인간 검토 속도가 병목으로 느껴짐  
• 잘 정리된 디자인 시스템/가이드라인은 앞으로 (인간의) 중간 검토용 또는 포트폴리오 수단으로 수렴할 듯  
