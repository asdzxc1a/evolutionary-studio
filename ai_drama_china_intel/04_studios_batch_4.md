# Batch 4: AI Drama Studios — Full Pipeline Intelligence

> **Companies 16–20** | Research Date: 2026-05-24 | Sources: 36kr, GeekPark, ifeng, Hugging Face, GitHub, company sites

---

## Table of Contents

1. [16. 快手/可灵AI (Kuaishou / Kling AI)](#16-快手可灵ai-kuaishou--kling-ai)
2. [17. 昆仑万维 (Kunlun Tech) — SkyReels Deep Dive](#17-昆仑万维-kunlun-tech--skyreels-deep-dive)
3. [18. 中文在线 (Chinese Online / COL)](#18-中文在线-chinese-online--col)
4. [19. 风平智能/有戏AI (Youxi AI)](#19-风平智能有戏ai-youxi-ai)
5. [20. 创壹科技 (OneStory / CreativeFitting)](#20-创壹科技-onestory--creativefitting)
6. [Cross-Company Comparison Matrix](#cross-company-comparison-matrix)
7. [Strategic Insights](#strategic-insights)

---

## 16. 快手/可灵AI (Kuaishou / Kling AI)

**HQ:** Beijing | **Listed:** HK: 1024 | **Role:** Platform + Foundation Model Provider

### Company Overview

Kuaishou is China's second-largest short-video platform, now positioning itself as the AI infrastructure layer for short drama creation. Through **Kling AI** (可灵AI) — its foundation video generation model — and **Starlight Short Drama** (星芒短剧) — its content label — Kuaishou has built a vertically integrated ecosystem spanning AI tools, content production, creator incentives, and distribution.

**Key Milestone:** 《新世界加载中》(New World Loading) — the world's first AI unit story anthology (7 independent episodes, 180 minutes total), co-produced with the Outliers (异类) team. Achieved **13.7 billion impressions** and **197 million global plays**.

### 7-Layer Pipeline

#### Layer 1: Script (剧本)
- **No proprietary script model** — relies on external LLMs (Claude, Gemini, etc.) for detailed shot-by-shot scripts
- Scripts include camera language (shot types, camera movement, lighting), dialogue, and action descriptions
- Visual style cards and character concept art generated during pre-production to lock aesthetic direction
- Emphasis on **human-written scripts enhanced by AI**, not fully automated generation

#### Layer 2: Storyboard / Shot Planning (分镜)
- **Kling 3.0 "Director Mode"** — the breakthrough feature:
  - **Auto-storyboarding:** AI automatically plans up to **6 connected shots** from a single narrative prompt, including camera transitions, angles, composition, and pacing
  - **Custom Multi-Shot:** Frame-by-frame manual control — set duration, content, camera motion (pan, zoom), and transition logic per shot; single generation up to **15 seconds**
- **First/Last Frame Lock:** Pin start and end poses for complex action continuity between consecutive shots

#### Layer 3: Visual Generation (画面生成)
- **Kling 3.0 / Kling O3 (Omni)** — unified multimodal architecture:
  - Merged Video 2.6 and O1/O3 consistency models into single architecture
  - **3D Spacetime Joint Attention** + physics simulation engine (gravity, inertia, deformation)
  - Max **4K resolution**, up to **15-second** single-take generation
- **Element Reference System (全能参考):**
  - Upload multi-angle character reference images (turnaround sheets, facial close-ups) or 3-8 second reference videos
  - Character features "bound" to the model — maintains appearance/costume consistency across all shots
  - Personal character library with named personas and saved feature tags
- **Model branches:**
  - **Kling Video 3.0 (V3):** Prompt-driven cinematic generation, automatic visual language scheduling
  - **Kling O3 (Omni):** Heavy-reference narrative workflows, stronger multi-character consistency and character-driven performance

#### Layer 4: Audio / Voice (音频/配音)
- **Native multimodal audio-visual generation** — video and audio (dialogue, ambient sound, BGM) generated simultaneously in the same framework
- **Lip-sync engine:** Precise visual character-to-speech alignment
  - Supports Chinese, English, Japanese, Korean, Spanish + dialects
  - Handles multi-person scenes without speaker confusion
- **Voice asset extraction:** Extract unique voice signatures from reference clips, bind to specific characters for cross-scene consistency
- Fallback: Export video → professional dubbing in ElevenLabs for voice consistency fine-tuning

#### Layer 5: Editing / Post-Production (后期制作)
- **Hybrid workflow** (AI生成 + 人工后期):
  - After Effects / Premiere Pro for color grading (fix AI over-saturation), grain overlay, anamorphic glow effects, artifact masking
  - Audio supplementation for scenes where native audio is unsatisfactory
- No proprietary editing tool — Kuaishou positions Kling as the **generation engine**, not the editing suite

#### Layer 6: Quality Control (质控)
- Human review remains primary QC mechanism
- Kling's multi-shot mode reduces inter-shot inconsistency (the main QC failure mode)
- No automated QC pipeline disclosed

#### Layer 7: Distribution / Monetization (分发/变现)
- **Magnetic Engine (磁力引擎) 2026 Program** (announced May 19, 2026):
  - **¥800M** (8亿) dedicated revenue-sharing fund for short dramas
  - **¥200M** (2亿) cash for incubating premium dramas and manga-dramas
  - **1 billion+ dedicated traffic** for content cold-start and quality incentives
  - **Business model shift:** From ad-ROI bidding → **GMV sharing model** (content creators' earnings tied directly to commercial contribution)
- **Three Support Plans:**
  - **磁力新剧计划:** Target 2,000+ dramas, up to ¥1M investment per drama
  - **IP漫改掘金计划:** Novel IP owners + manga-drama producers — matchmaking, tools, resources
  - **全民AI制作人计划:** Individual creators — lower barriers via AI, talent scouting
- Distribution on Kuaishou app + "AI创想剧场" (AI Imagination Theater) initiative for global creator submissions

### Production Economics
| Metric | Value |
|---|---|
| Traditional drama cost | ¥500K–¥1M+ per drama |
| AI drama cost (Kling-based) | ¥50K–¥100K per drama |
| Per-minute cost | ¥500–¥1,000 (down from ¥3,000–¥5,000 in 2024) |
| Direct compute cost | ~¥3,000 per drama |
| Production cycle | ~7 days (from ~2 months traditional) |
| Team size | 3–6 people for full production |
| Weekly output | 3–5 dramas per team |
| Global creators | 60M+ (Kling platform) |
| ARR (2025 EOY) | $240M |

---

## 17. 昆仑万维 (Kunlun Tech) — SkyReels Deep Dive

**HQ:** Beijing | **Listed:** SZ: 300418 | **Role:** Full-Stack AI Drama Platform (Most Vertically Integrated)

> ⚠️ **MOST IMPORTANT COMPANY IN THIS BATCH** — Kunlun Tech has built the most comprehensive open-source AI drama production pipeline in the world.

### Company Overview

Kunlun Tech ("All in AGI & AIGC" strategy) has constructed the **only end-to-end AI drama production system** that spans from script generation to overseas distribution, with most core models **open-sourced**. Their SkyReels ecosystem is the industry's closest approximation to a fully automated AI film studio.

### 7-Layer Pipeline

#### Layer 1: Script (剧本) — SkyScript
- **SkyScript** — proprietary script generation large model
- **SkyScript-100M dataset:** 100M+ high-quality annotated data points covering:
  - Dramatic conflict patterns and "爽点" (satisfaction triggers)
  - Plot pacing and rhythm markers
  - Highlight/climax identification
  - Emotional arc modeling
- Designed specifically for short-drama format — not a general writing LLM
- Generates structured scripts with dramatic tension optimized for mobile-first consumption

#### Layer 2: Storyboard / Shot Planning (分镜) — StoryboardGen
- **StoryboardGen** — world's first **DiT-MoE** (Diffusion Transformer + Mixture-of-Experts) architecture for storyboard generation
- Technical approach:
  - Decomposes script into **global descriptions** (scene, composition) and **subject descriptions** (character, action)
  - Ensures character-to-scene consistency through dual-track encoding
  - Generates industrial-grade storyboard frames with professional cinematographic language
- Achieves controllability that traditional T2I/T2V pipelines cannot match

#### Layer 3: Visual Generation (画面生成) — SkyReels V1/V2/V3 + A1/A2

##### SkyReels Model Evolution

| Model | Architecture | Key Innovation | Status |
|---|---|---|---|
| **SkyReels-V1** | Early DiT | Human-centric video generation | Open-sourced |
| **SkyReels-A1** | Performance-driven | Expression control (33 expressions), body motion (400+ actions), micro-expression fidelity | Open-sourced |
| **SkyReels-A2** | Elements-to-Video (E2V) | Multi-element composition with dual-branch architecture (spatial + semantic) | Open-sourced |
| **SkyReels-V2** | **Diffusion Forcing** | First infinite-length video model; non-decreasing noise schedule; rolling window denoising | Open-sourced |
| **SkyReels-V3** | Based on **Wan2.1** | Text-to-Video + Image-to-Video; lip-sync; long video generation | Open-sourced |

##### SkyReels-A1 (Expression & Motion Control)
- **Video-to-Video human driving:** Transfer expressions and body performance from a driving video onto a target character
- 33 distinct expression types, 400+ action primitives
- High-fidelity micro-expression reproduction (eyebrow details, skin texture)
- Supports arbitrary body proportions (portrait, half-body, full-body)
- Identity (ID) consistency maintained throughout driving

##### SkyReels-A2 (Elements-to-Video Framework)
- **E2V breakthrough:** Moves beyond single-reference I2V to **multi-element composition**
  - Combine multiple independent visual elements (specific character + specific prop + specific background) into coherent video
  - **Dual-branch architecture:** Spatial feature branch + semantic feature branch
  - Maintains strict visual consistency for each element against its reference
- Solves the "style fragmentation" problem when combining multiple AI-generated assets

##### SkyReels-V2 (Diffusion Forcing — Infinite Length)
- First open-source model using **Diffusion Forcing** framework
- Each frame gets independent noise scheduling with non-decreasing constraint
- Search space reduction: O(10^48) → O(10^32)
- **Rolling-window denoising** enables theoretically infinite-length generation
- Supports complex camera movements in long sequences

##### SkyReels-V3 (Production-Ready)
- Built on **Wan2.1** architecture (from Alibaba)
- Native lip-sync support
- Long-video generation with strong temporal consistency
- Integrated with HuggingFace `diffusers` (WanPipeline / WanImageToVideoPipeline)
- ComfyUI wrapper available (`ComfyUI-WanVideoWrapper`)

#### Layer 4: Audio / Voice (音频/配音)
- Integrated dialogue and BGM generation within SkyReels platform
- Character voice matching during "one-click drama" creation flow
- Lip-sync capability native in V3
- Auto-generated background music aligned to scene mood

#### Layer 5: Editing / Post-Production (后期制作) — SkyProduction
- **SkyProduction** — automated editing and compositing engine
- Full pipeline: Script → Character customization → Storyboard → Dialogue/BGM → Final composite
- **Auto-conversion to vertical format** (9:16) for mobile platforms
- Handles scene transitions, pacing, and audio-visual sync automatically

#### Layer 6: Quality Control (质控)
- **WorldEngine** — the QC backbone:
  - **AI 3D Engine + Video Model Fusion Platform** (industry first)
  - Uses **"Layer Fusion" technology** to combine:
    - 3D engine precision (physics simulation, lighting, spatial relationships) via **Unreal Engine 5**
    - Video model creative generation capabilities
  - Eliminates "clipping" and physics-violating artifacts
  - **Unreal-Gen** data production engine: auto-outputs Video + Pose + Action data with tick-level synchronization (millisecond alignment)
- **Sky3DGen** — 3D generation model for scene and character assets
- **3D Gaussian Splatting (3DGS)** for interactive simulation and enhanced physical fidelity
- Multi-level constraint encoding: script, character appearance, storyboard, and environment jointly encoded to ensure semantic + visual consistency

#### Layer 7: Distribution / Monetization (分发/变现)
- **DramaWave** — premium paid subscription platform
  - Launched October 2024
  - Topped Korean entertainment charts
  - Focus: Southeast Asia, Latin America, South Korea
- **FreeReels** — free ad-supported platform
  - Broader audience reach
  - Revenue via ads
  - Traffic complement to DramaWave
- **Combined metrics (as of early 2026):**
  - 100,000+ dramas on platform
  - 80M+ global MAU
  - Strong ARR performance
- **Global Creator Support Program:** Multi-million dollar fund + open creation tools
- **SkyAnime** — AI dynamic manga mass-production tool for manga-drama format

### Open-Source Ecosystem

| Repository | Platform | Description |
|---|---|---|
| `Skywork/SkyReels-V1` | HuggingFace | Base video generation weights |
| `Skywork/SkyReels-A2` | GitHub + HuggingFace | Elements-to-Video framework |
| `Skywork/SkyReels-V3` | HuggingFace | Wan2.1-based production model |
| `SkyReels-V2` | GitHub | Diffusion Forcing infinite-length model |
| ComfyUI wrappers | Community | Visual workflow integration |
| Technical papers | arXiv | Full architecture documentation |

### Production Economics
| Metric | Value |
|---|---|
| AI manga-drama cost | < $20,000 USD |
| Revenue potential | $1M+ per drama |
| Production cycle | Hours (from weeks) |
| Platform coverage | 170+ countries |

---

## 18. 中文在线 (Chinese Online / COL)

**HQ:** Beijing | **Listed:** SZ: 300364 | **Chairman:** 童之磊 (Tong Zhilei) | **Role:** IP Giant → AI Drama Producer

### Company Overview

Chinese Online is China's largest digital content library (5.5M+ titles), now pivoting from pure IP licensing to end-to-end AI drama production and global distribution. Their strategic thesis: **"Human power + Compute power" (人力 + 算力)** is the new content production paradigm.

### 7-Layer Pipeline

#### Layer 1: Script (剧本) — 逍遥AI (XiaoyaoAI)
- **中文逍遥 (Chinese Xiaoyao)** — proprietary content creation LLM
- **"Three Ones" capability:**
  - One-click generation of 10,000+ word novels
  - One image → generates a complete novel
  - One-pass comprehension of 1,000,000+ character novels
- Full creative lifecycle coverage: story conception → world-building → plot architecture → content writing → dialogue → illustration → content evaluation
- Massive training advantage: 5.5M+ proprietary digital content resources as training data
- **Hybrid strategy:** "Self-developed core + external integration" — integrates XiaoyaoAI with external models (e.g., Kuaishou Kling AI) for text-to-visual pipeline

#### Layer 2: Storyboard / Shot Planning (分镜)
- **次元神笔 (Ciyuan Shenbi / Dimension Magic Pen)** handles automated storyboard generation
- Script → automatic storyboard outline conversion using integrated LLM + vision models
- Supports multiple visual styles: 国风 (traditional Chinese), sci-fi, 二次元 (anime), etc.

#### Layer 3: Visual Generation (画面生成)
- **Dimension Magic Pen** full-stack creation:
  - Character generation from reference images or text descriptions
  - **Character lock** — AI generates and locks character appearance for full-drama consistency
  - One-click batch video generation from storyboard content
  - Style switching between visual aesthetics
- Integrates external video generation models (Kling AI, etc.) for high-fidelity output

#### Layer 4: Audio / Voice (音频/配音)
- Built-in AI voice synthesis
- Character-specific voice matching based on persona attributes
- Emotional voice injection
- Auto-matched background music for scene-audio synchronization

#### Layer 5: Editing / Post-Production (后期制作)
- Browser-based preview and fine-tuning interface
- Manual adjustment of: composition, subtitles, voice sync
- No standalone professional editing tool — editing happens within the Dimension Magic Pen web interface

#### Layer 6: Quality Control (质控)
- Creator preview + manual fine-tuning loop
- Character consistency validation (anti-"崩坏" / anti-collapse checks)
- No automated QC pipeline disclosed

#### Layer 7: Distribution / Monetization (分发/变现)
- **FlareFlow** — proprietary international short drama platform
  - Launched March 2025
  - 170+ countries, 11 languages
  - Revenue: ads + user payments + merchandise
  - Focus markets: US, Germany, Japan, UK
- **Cross-platform distribution:** TikTok, YouTube
- **Hengqin International Film City** (横琴国际影视城):
  - China's first short-drama-export-focused production base
  - 30% cost reduction vs. US production
  - Multi-project parallel shooting
  - "Domestic shooting, overseas distribution" model
- **Matrix operations:** Multi-language ad deployment, AI-generated ad creative, precision targeting
- **Ecosystem loop:** Content creation → distribution → user feedback → re-creation

### Production Economics
| Metric | Value |
|---|---|
| IP library | 5.5M+ digital content titles |
| Platform coverage | 170+ countries, 11 languages |
| Cost advantage (Hengqin) | ~30% lower than US production |
| Strategy | AI tech + physical production base + global distribution |

### CEO Vision (童之磊)
- "AI creation models don't replace writers — they lower barriers and boost efficiency"
- "Let writers focus on ideas and themes, while AI handles the mechanical production"
- Content production has entered the "human power + compute power" era

---

## 19. 风平智能/有戏AI (Youxi AI)

**HQ:** Beijing | **Founded:** 2019 | **Role:** Dedicated AI Drama Production Engine

### Company Overview

Fullpeace Intelligence (风平智能) is a pure-play AI drama production company that launched **Youxi AI (有戏AI)** in January 2026 — a purpose-built one-stop AI short drama creation platform. The company was founded by veterans from Huawei, Baidu, Tencent, IBM, Alibaba, and Tsinghua/Peking universities.

**Funding:** Completed ~¥100M (cumulative) A-round series financing in September 2024. Investors: Cuican Capital, Huawei-affiliated Huakun Capital Fund (co-lead), Huicai Capital, Peking University AI Innovation Center director Lei Ming, Tsinghua alumni fund.

### 7-Layer Pipeline

#### Layer 1: Script (剧本)
- **Long script parsing:** Supports up to **50,000 characters** (5万字) — the highest disclosed capacity in this batch
- Multi-Agent collaborative system handles intelligent episode splitting
- Automatic dramatic structure analysis and scene decomposition
- Not a script generation model — focuses on **parsing and structuring** existing scripts

#### Layer 2: Storyboard / Shot Planning (分镜)
- **AI Director Agent** — professional cinematographic logic:
  - Auto-matches camera language to scene emotion: dialogue → close-up, emotional climax → extreme close-up
  - Supports human fine-tuning and rollback at any stage
  - Script-to-storyboard conversion with professional shot types, angles, and transitions
- **Multi-Agent architecture:**
  - Writer Agent → Director Agent → Actor Agent
  - Shared memory, workflow orchestration, and state feedback
  - Real-time communication via WebSocket/message queue

#### Layer 3: Visual Generation (画面生成)
- **Persona Library (人设库):**
  - Core asset database: name, facial features, costume, temperament
  - Serves as "stable context" for model inference
- **Cross-episode character consistency:** 95%+ accuracy (claimed)
  - Proprietary vertical model with LoRA/ControlNet-type fine-tuning
  - Solves the "face collapse" (崩脸) problem across episodes
- **Multi-angle character view generation** for 3D-consistent reference
- Supports multiple visual styles

#### Layer 4: Audio / Voice (音频/配音)
- Integrated AI voice synthesis with **emotional control**
- Character-matched voice assignment
- Sound effects auto-adaptation
- One-click full automation: voiceover + SFX + background music

#### Layer 5: Editing / Post-Production (后期制作)
- **Automated shot concatenation** — system auto-assembles scenes into final cut
- One-click generation: complete episode from script input
- Export-ready output

#### Layer 6: Quality Control (质控)
- Multi-Agent consensus mechanism — agents cross-validate outputs
- 95%+ cross-episode character consistency as primary QC metric
- Human review supported but not required for standard output

#### Layer 7: Distribution / Monetization (分发/变现)
- **Interactive drama engine** (剧游引擎) — unique differentiator:
  - Supports branching narrative with viewer choice
  - Positioned as "next-generation intelligent drama production and interactive experience engine"
- Platform-agnostic output — creators distribute on their own channels
- Not a distribution platform — pure production tool

### Production Economics
| Metric | Value |
|---|---|
| Video generation cost | **¥0.10/second** (lowest in batch) |
| Per-episode cost | < ¥10 |
| Production speed | "1 person, 1 day, 1 drama" |
| Script capacity | 50,000 characters |
| Cross-episode consistency | 95%+ |
| Architecture | Multi-Agent (Writer/Director/Actor) |
| Team background | Huawei, Baidu, Tencent, IBM, Alibaba veterans |
| Funding | ~¥100M cumulative A-round |

---

## 20. 创壹科技 (OneStory / CreativeFitting)

**HQ:** Shenzhen | **Founded:** 2021 | **Role:** Digital Human + Virtual Production Studio

### Company Overview

CreativeFitting is the creator of **柳夜熙 (Liu Yexi)** — China's most famous virtual influencer/digital human, who went viral in 2021 with cinema-grade VFX short-form content. The company has since pivoted from pure digital human IP creation toward **AI-augmented virtual production** and is building the **OneStory AIGC platform**.

**Digital Human IP Matrix:** 柳夜熙 (Liu Yexi), 慧慧周, 宇航员小五, 犹卡塔娜 — multiple high-profile virtual characters.

**Notable Productions:**
- 《柳夜熙：地支迷阵》— world's first digital human short drama
- 《柒两人生》— China's first virtual production web micro-drama (used LED volumes/virtual sets to replace location shooting)

### 7-Layer Pipeline

#### Layer 1: Script (剧本)
- **OneStory AIGC Platform** — AI-driven story generation
- Transforms text concepts into structured scripts
- Focuses on sci-fi and fantasy genres (aligned with their digital human IP DNA)
- Not a standalone script model — integrated into the broader creation flow

#### Layer 2: Storyboard / Shot Planning (分镜)
- OneStory generates professional storyboard scripts from narrative input
- Integrates character consistency maintenance into storyboard phase
- Cinematographic planning informed by team's film/TV production background

#### Layer 3: Visual Generation (画面生成)
- **Hybrid approach: AIGC + Virtual Production + Digital Humans**
  - XR (Extended Reality) production with LED volumes
  - High-fidelity digital human rendering
  - AI-generated backgrounds and environments
  - Motion capture integration
- **IP + XR + AIGC fusion** — their core technical identity
- OneStory tool enables rapid image/video generation from storyboard frames

#### Layer 4: Audio / Voice (音频/配音)
- Professional voice acting (traditional approach for premium content)
- AI voice synthesis for rapid iteration
- Sound design leveraging film production expertise

#### Layer 5: Editing / Post-Production (后期制作)
- Professional VFX post-production pipeline (After Effects, Nuke-class workflows)
- Digital human compositing and integration
- Virtual production removes need for extensive location-based post work

#### Layer 6: Quality Control (质控)
- Film-grade QC standards (team has strong traditional film/TV DNA)
- Director-led creative quality control
- Digital human fidelity checks

#### Layer 7: Distribution / Monetization (分发/变现)
- Platform distribution: Douyin (TikTok China), Bilibili, YouTube
- IP licensing and merchandise
- Brand collaboration and sponsored content
- Building creator ecosystem for global distribution
- Vision: "New Marvel" — building interconnected virtual character universe

### Team & Funding
| Metric | Detail |
|---|---|
| Co-founder/CEO | 梁子康 (Liang Zikang) |
| Co-founder/Chairman | 谢多盛 (Xie Duosheng) — film directing background |
| Team origin | "拍照自修室" (Photo Studio) — VFX short video creators |
| Team size | ~150–200 people |
| Composition | Balanced tech + content; cross-disciplinary (art, algorithm, modeling, mocap) |
| Total funding | ¥100M+ RMB across multiple rounds |
| 2025 Jan | Tens of millions RMB — Lingguang Optics + Wuhu Jingxin |
| 2023 Aug | Jingxin Fund strategic investment |
| 2022 Sep | Dachen Caizhi Pre-A round |
| 2021 Feb | Zhongying Holdings angel round |

### Production Economics
| Metric | Value |
|---|---|
| Traditional cycle | Months per production |
| Current target | 3 people × 3 days = 1 AI story video |
| Ultimate goal | 1 person × 1 day = full production |
| Genre focus | Sci-fi, fantasy, suspense |
| Core differentiator | Digital human IP + Virtual production + AIGC |

---

## Cross-Company Comparison Matrix

### Pipeline Coverage

| Layer | Kuaishou/Kling | Kunlun/SkyReels | COL/次元神笔 | Youxi AI | CreativeFitting |
|---|:---:|:---:|:---:|:---:|:---:|
| **1. Script** | ❌ External LLMs | ✅ SkyScript (proprietary) | ✅ 逍遥AI (proprietary) | ⚡ Parser only (50K chars) | ⚡ OneStory (basic) |
| **2. Storyboard** | ✅ Director Mode (6-shot) | ✅ StoryboardGen (DiT-MoE) | ✅ Auto-storyboard | ✅ AI Director Agent | ⚡ Integrated |
| **3. Visual Gen** | ✅ Kling 3.0/O3 (4K, 15s) | ✅ SkyReels V1/V2/V3/A1/A2 | ✅ Dimension Magic Pen | ✅ 95% consistency | ✅ XR + Digital Human |
| **4. Audio** | ✅ Native multimodal | ✅ Integrated | ✅ AI voice + BGM | ✅ Emotional voice | ⚡ Professional + AI |
| **5. Editing** | ❌ External (AE/Premiere) | ✅ SkyProduction (auto) | ⚡ Browser-based | ✅ Auto-assembly | ✅ Professional VFX |
| **6. QC** | ⚡ Manual | ✅ WorldEngine (physics) | ⚡ Manual preview | ✅ Multi-Agent consensus | ✅ Director-led |
| **7. Distribution** | ✅ Kuaishou + Magnetic Engine | ✅ DramaWave + FreeReels | ✅ FlareFlow + TikTok/YT | ❌ Tool only | ⚡ Platform distribution |

**Legend:** ✅ Full capability | ⚡ Partial/basic | ❌ Not provided

### Business Model Comparison

| Dimension | Kuaishou/Kling | Kunlun/SkyReels | COL/次元神笔 | Youxi AI | CreativeFitting |
|---|---|---|---|---|---|
| **Type** | Platform + Model | Full-stack platform | IP + Platform | Pure SaaS tool | Studio + Tool |
| **Listing** | HK: 1024 | SZ: 300418 | SZ: 300364 | Private (~¥100M) | Private (¥100M+) |
| **Revenue Model** | Creator rev-share, ads | Subscription, ads | Subscription, IP licensing | Per-second pricing | IP, brand deals |
| **Open Source** | ❌ Closed | ✅ Extensive (GitHub/HF) | ❌ Closed | ❌ Closed | ❌ Closed |
| **Global Reach** | 60M+ creators | 80M+ MAU, 170+ countries | 170+ countries, 11 languages | N/A (tool only) | Building |
| **IP Assets** | Content platform | 100K+ dramas | 5.5M+ digital titles | None | 柳夜熙 + IP matrix |

### Cost & Speed Comparison

| Metric | Kuaishou/Kling | Kunlun/SkyReels | COL/次元神笔 | Youxi AI | CreativeFitting |
|---|---|---|---|---|---|
| **Per-drama cost** | ¥50K–100K | < $20K USD | Undisclosed | < ¥10/episode | Undisclosed |
| **Per-second cost** | ~¥10–20 | Undisclosed | Undisclosed | **¥0.10** | Undisclosed |
| **Production cycle** | ~7 days | Hours | Undisclosed | 1 day (1 person) | 3 days (3 people) |
| **Min team size** | 3–6 people | 1 person (platform) | 1 person (platform) | 1 person | 3 people |

### Technical Architecture

| Component | Kuaishou/Kling | Kunlun/SkyReels | COL/次元神笔 | Youxi AI | CreativeFitting |
|---|---|---|---|---|---|
| **Base Architecture** | Unified Omni (proprietary) | DiT-MoE + Diffusion Forcing + Wan2.1 | XiaoyaoAI + external models | Multi-Agent system | XR + Digital Human + AIGC |
| **Character Consistency** | Element Reference System | E2V dual-branch | Character lock | Persona Library (95%+) | Digital human models |
| **Physics/3D** | 3D Spacetime Attention | WorldEngine (UE5 + AI) | None disclosed | None disclosed | Virtual production (LED) |
| **Max Resolution** | 4K | Undisclosed | Undisclosed | Undisclosed | Film-grade |
| **Key Innovation** | Multi-shot Director Mode | Open-source full pipeline | IP-to-drama automation | ¥0.10/sec cost floor | Virtual human IP universe |

---

## Strategic Insights

### 1. The Open-Source Moat: Kunlun Tech's Asymmetric Strategy
Kunlun Tech is the **only company in this batch** (and arguably in all of China's AI drama space) that has open-sourced its core models. This creates a powerful flywheel:
- **Developer adoption** → community contributions → model improvements → more adoption
- **De-risking for enterprises** who fear vendor lock-in
- **Talent acquisition** — top researchers want to work on open models
- The SkyReels V2 Diffusion Forcing paper alone represents a genuine architectural innovation (non-decreasing noise scheduling)
- **Risk:** Open-source commoditizes the generation layer, forcing Kunlun to compete on platform (DramaWave/FreeReels) rather than model

### 2. The "¥0.10/second" Price War
Youxi AI's ¥0.10/second pricing is a strategic weapon designed to:
- **Kill the margin** for competitors who charge per-generation
- **Force consolidation** — only companies with scale compute procurement survive
- **Establish the price floor** for AI video generation as a commodity utility
- Implication: The value layer shifts from "generation" to "script quality" and "distribution"

### 3. Platform vs. Tool vs. Studio — Three Business Models Diverge

| Model | Companies | Advantage | Risk |
|---|---|---|---|
| **Platform** (distribution + tools) | Kuaishou, Kunlun, COL | Network effects, creator lock-in | Content commoditization |
| **Pure Tool** (SaaS) | Youxi AI | Low overhead, pure tech play | Zero switching costs |
| **Studio** (IP + production) | CreativeFitting | IP moat, brand value | Doesn't scale like platforms |

### 4. The IP Advantage: COL's Unique Position
With **5.5 million digital content titles**, COL has the largest IP reservoir. The combination of:
- IP library → XiaoyaoAI script generation → Dimension Magic Pen visual production → FlareFlow global distribution
- Plus the **Hengqin physical production base** for hybrid (AI + live-action) content
- Creates a **vertically integrated content factory** that is uniquely difficult to replicate

### 5. Kuaishou's "GMV Sharing" — The Distribution Power Play
The shift from ad-ROI bidding to **GMV sharing** is the most significant business model innovation in this batch:
- **Old model:** Creator pays for traffic → hopes for ad revenue
- **New model:** Creator's earnings tied directly to commercial value generated
- This aligns incentives and could attract higher-quality creators
- Combined with ¥2B in direct investment, Kuaishou is buying the best content pipeline

### 6. CreativeFitting's "New Marvel" Ambition
The digital human IP strategy is unique in this batch:
- Other companies treat characters as disposable (generated per-drama)
- CreativeFitting builds **persistent IP characters** (柳夜熙) that transcend individual productions
- If successful, this creates compounding IP value — but it's the slowest-scaling model

### 7. The 2026 Inflection Point
The data reveals a structural shift happening in real-time:
- **AI manga-dramas** now account for **~95%** of micro-drama production in China (Q1 2026)
- Content lifecycle has collapsed to **3-4 weeks** (from months)
- **Supply/demand mismatch:** Production is so cheap and fast that content is becoming worthless
- Winners will be those who control **distribution** (Kuaishou, Kunlun) or **IP** (COL, CreativeFitting), not generation

### 8. Technology Convergence Pattern
All 5 companies are converging on the same target architecture:
```
Script LLM → Storyboard Model → Video DiT → Voice TTS → Auto-Editor → Distribution Platform
```
The differentiation is in:
- **Kunlun:** Open-source models + physics engine (WorldEngine)
- **Kuaishou:** Foundation model quality (Kling O3) + distribution scale
- **COL:** IP library depth + physical production base
- **Youxi AI:** Cost leadership + interactive drama engine
- **CreativeFitting:** Digital human IP + virtual production expertise

---

*Research compiled from 20+ web searches across Chinese tech media (36kr, GeekPark, ifeng, chinanews, yicai, pandaily), company sites, GitHub, and HuggingFace. Data current as of May 2026.*
