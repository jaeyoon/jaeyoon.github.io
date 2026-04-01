While Generative AI produces strong visuals when given more freedom, the real challenge is figuring out if legacy designs can be tokenized and systematized. I recently ran a test to see if Claude and Codex could handle freeform analysis, using MCP (Model Context Protocol) to run design tests directly on canvases like Figma, Stitch, and Pencil.

> **The Workflow:** 1. Input → 2. Analysis → 3. Design System Gen → 4. Variant Gen → 5. Output

---

### Step 1
>• Figma Designs (Node/Section selection via MCP)  
• Website URLs (HTML-based testing targets)  

*(Input sources)* ![alt text](</notes/assets/Input - sources.png>)  


---

### Step 2  
Converting raw input into structured data (JSON/TSX).

>• Figma Designs (Node/Section selection via MCP → Layout/component/token extraction)  
• Website URLs (HTML → JSON/TSX conversion without screenshots)  

**The Findings:**  
Even with the exact same MCP calls, the extracted data looked different depending on the model's interpretation and strategy. Claude was great at looking deeper, using previous context to map out broader tokens and track internal structures. Codex, however, treated each request independently, focusing purely on identifying lean, core structures. This mostly comes down to keeping context versus working independently.

**Phase 1-2 Speed (Input + Analysis)**

| Case | Claude | Codex |
|--------|--------|--------|
| Node / Sidemenu | input 1m / analysis 5m = 6m | input 2m / analysis 4m = 6m |
| Section / Desktop | input 3m / analysis 1m = 4m | input 3m / analysis 4m = 7m |
| Section / Header | input 3m / analysis 1m = 4m | input 4m / analysis 5m = 9m |
| URL / Warp.dev | input 2m / analysis 1m = 3m | input 3m / analysis 4m = 7m |
| **Total** | **17m** | **29m** |

---

### Step 3 (Design System Generation)
Delegating generation to each agent using only the analysis results.
> layout rules  
token system  
component system  

![alt text](</notes/assets/Claude - DS iteration.png>)
![alt text](</notes/assets/Codex - DS iteration.png>)
**The Findings:**  
Claude scaled the data into ready-to-use specs, detailing component architecture and exact dimensions. Codex chose to keep it brief, summarizing the high-level flow and direction even when it had more data. Since these were zero-shot prompts with no fine-tuning, both models landed in the "Mid-to-Low" quality range—you can expect some overlapping layers, missing parts, and layout shifts.

---

### Step 4 (Design Variant Generation)
Testing "structural integrity vs. recomposition" with A/B variants based on the generated systems.
> • A: Keep the structure, change the styles (Not aiming for a perfect match, just checking performance).  
• B: Improve the component structure (Loosely guided prompt). 

**The Findings:**
Claude builds step-by-step; it treats 'B' as an evolution of 'A,' separating what to keep from what to change and documenting everything down to the code level. Codex treats 'A' and 'B' as two separate concepts, quickly splitting them by mood and direction. Because of this, Claude builds continuous results based on previous definitions, while Codex frames each variant as a completely standalone proposal. In the end, Claude feels more like dev-ready documentation, while Codex is better for quick visual concepting ready to plug into a generation tool.


**Phase 3-4 Speed (System + Variant)**  

| Case | Claude | Codex |
|------|--------|--------|
| Node / Sidemenu | system 5m / variant 4m = 9m | system 3m / variant 2m = 5m |
| Section / Desktop | system 1m / variant 6m = 7m | system 3m / variant 2m = 5m |
| Section / Header | system 1m / variant 4m = 5m | system 3m / variant 2m = 5m |
| URL / Warp.dev | system 1m / variant 4m = 5m | system 4m / variant 2m = 6m |
| **Total** | **26m** | **21m** |


---

### Step 5 (Execution)
Comparing tools during the "Output" phase. This is mainly limited by which tools support writing to the canvas via MCP.
>• `Google Stitch`    
• `Pencil.dev`  
• `Figma (write to canvas)`    
Stitch (Creation) / Pencil (Refinement) / Figma write (Exact Execution)  


#### Google Stitch
*Stitch generated 3 sidemenu variations, but customization outside its templates is limited. It defaults to a full-screen canvas based on `deviceType` (e.g., 2560×2048 even when rendering a single component).*  
<video controls muted loop playsinline width="600">
  <source src="https://pub-b3f343132a0f482d88780d5a9ba50665.r2.dev/stitch-fixed-canvas-2.mp4" type="video/mp4">
</video>

#### Pencil.dev
*Sidemenu component — rendered across 3 agents*
<video controls muted loop playsinline width="600">
  <source src="https://pub-b3f343132a0f482d88780d5a9ba50665.r2.dev/pencil-sidemenu-3-agents.mp4" type="video/mp4">
</video>

*Alert bar component — rendered across 4 agents*
<video controls muted loop playsinline width="600">
  <source src="https://pub-b3f343132a0f482d88780d5a9ba50665.r2.dev/pencil-4-agents-1.mp4" type="video/mp4">
</video>


#### Figma (write to canvas)
*Creating variables via MCP write*
<video controls muted loop playsinline width="600">
  <source src="https://pub-b3f343132a0f482d88780d5a9ba50665.r2.dev/figma-write-variables.mp4" type="video/mp4">
</video>


**The Findings:**  
• All three struggle with fine details. Getting a "pixel-perfect" reproduction right now takes a lot of time and tokens.  
• Corner radii, margins, and typography adjustments start to break down even with fine-tuning (Figma gives the highest quality out of the three).  
• Without exact coordinates, tools often fail to recognize existing elements and just blindly overwrite the canvas (This was reduced by using scripts and `skill.md`).  
• Tiny details like vector icons are frequently left out or altered.  

---
### Takeaways
• Layouts and structural traits are reproduced reasonably well, but exact JSON values for radii, margins, and alignment often shift around in Stitch and Pencil.  
• Figma's "write to canvas" feature is the best performer for overall accuracy and stable variable generation.  
• Stitch shines in the early creative phases—it’s great at taking rough sketches and turning them into clean UI mockups reliably.  
• Custom Font Limitations: Testing non-standard fonts (like Pretendard) led to reading failures. Stitch handled it fine when given a CDN link, but Pencil relies on local font rendering, which broke the output—I eventually had to install the font locally to fix it.  
• At this stage, forcing highly detailed refinement is tough. Because of this, Stitch and Pencil hit the "SaaS Visual Sweet Spot"—they are basically production-ready for generating standard interfaces quickly as long as your branding isn't super specific.  
• Building a setup based on design tokens is expensive. While heavy prompt engineering can improve the details, it is still highly inefficient.  

### Trivia
•``````Pencil.dev`````` produces impressive output for a startup, though the UX can be a bit quirky or non-standard. Their "parallel agents" processing feels like a UI gimmick, but it gives you something nice to look at while you wait (using bio tokens). Unfortunately, it isn't supported via API yet.  
• OpenPencil: I tested this open-source tool for `.fig` analysis. It's useful for structural checks when you don't have full seat permissions, but it felt limited beyond that.  
• The lag across AI generation wasn't just model latency—the real bottleneck was the bridge between unoptimized tool setups (MCPs/scripts) and human review speeds compared to raw computing time.  
• Well-documented design systems will likely fade into being just reference points for humans to check or portfolio pieces, rather than actual blueprints used directly in development.
