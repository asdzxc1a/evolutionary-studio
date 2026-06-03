# 🎬 MASTER INTELLIGENCE REPORT: Chinese AI Short Drama Industry

> **25 Studios · 7-Layer Pipeline Analysis · Replicable Blueprint**
> Research Date: 2026-05-25 | Sources: 36kr, huxiu, volcengine, eastmoney, thepaper, sina, geekpark, huggingface, github, + 50 Chinese-language primary sources

---

## Executive Summary

This report synthesizes deep intelligence on **25 Chinese AI short drama studios** across the full production stack. The Chinese AI drama market reached **¥189.8B in 2025** (276% YoY growth) and is undergoing a paradigm shift: from human-intensive production to **"1 person + AI agents"** workflows that produce 60-episode series in 8 days for under ¥10K.

### The 5 Key Findings

1. **ByteDance owns the stack** — Seedance 2.0 → Xiaoyunque Agent → 火山剧创 → Douyin/红果 is the dominant end-to-end pipeline
2. **"5 people, 8 days, 60 episodes, 100M views"** is the new benchmark (《万兽独尊》by 创翊传媒)
3. **Kunlun Tech SkyReels** is the most complete open-source pipeline — fully replicable from HuggingFace
4. **Character consistency is solved** at model level (Seedance 2.0 dual-branch, SkyReels E2V, Kling O3 element binding)
5. **Cost collapsed to ¥0.10/second** of video — the bottleneck is now creative differentiation, not production cost

---

## Table of Contents

1. [All 25 Studios — Master Index](#master-index)
2. [Comparative Intelligence Matrices](#comparative-matrices)
3. [Technology Stack Breakdown](#tech-stack)
4. [The Ideal Replicable Pipeline](#ideal-pipeline)
5. [Cost & Speed Benchmarks](#cost-benchmarks)
6. [Distribution & Monetization Playbook](#distribution)
7. [Strategic Recommendations](#recommendations)

---

## 1. All 25 Studios — Master Index {#master-index}

### Tier 1: Platform Giants & Tech Providers (Control the ecosystem)

| # | Company | Location | Type | Core Product | Batch |
|---|---------|----------|------|-------------|-------|
| 15 | **字节跳动 (ByteDance)** | Beijing | Platform + Model | Seedance 2.0, Xiaoyunque Agent, 火山剧创 | [Batch 3](./03_studios_batch_3.md) |
| 16 | **快手/可灵AI (Kuaishou/Kling)** | Beijing | Platform + Model | Kling 3.0/O3, 磁力引擎, 星芒短剧 | [Batch 4](./04_studios_batch_4.md) |
| 17 | **昆仑万维 (Kunlun Tech)** | Beijing | Full Stack + Open Source | SkyReels V1-V4, SkyScript, DramaWave | [Batch 4](./04_studios_batch_4.md) |

### Tier 2: Traditional Studios with AI Centers (IP + Distribution leverage)

| # | Company | Location | Type | Core Product | Batch |
|---|---------|----------|------|-------------|-------|
| 11 | **博纳影业 (Bona Film)** | Beijing | Film Studio → AI | AIGMS Center, 三星堆 IP | [Batch 3](./03_studios_batch_3.md) |
| 12 | **华策影视 (Huace)** | Hangzhou | Largest Drama Co. | 有风/国色 models, IP library | [Batch 3](./03_studios_batch_3.md) |
| 13 | **芒果超媒 (Mango)** | Changsha | State Broadcaster | 芒果灵创, 芒果大模型 | [Batch 3](./03_studios_batch_3.md) |
| 14 | **耀客传媒 (Yaoker)** | Shanghai | Drama Studio | AI digital actors, 帧赞 platform | [Batch 3](./03_studios_batch_3.md) |
| 18 | **中文在线 (COL)** | Beijing | IP Giant | 次元神笔, 逍遥AI, FlareFlow | [Batch 4](./04_studios_batch_4.md) |

### Tier 3: Pure AI Studios (AI-native production)

| # | Company | Location | Type | Core Product | Batch |
|---|---------|----------|------|-------------|-------|
| 1 | **万像天影 (VisionStar)** | Beijing | AI Disney | Full-pipeline AI filmmaking | [Batch 1](./01_studios_batch_1.md) |
| 2 | **灵矩动漫 (Lingju)** | Hangzhou | Volume Factory | 50-70 dramas/month, 700 staff | [Batch 1](./01_studios_batch_1.md) |
| 3 | **酱油文化 (Jiangyou)** | Hangzhou | Industrial Scale | 1,200+ staff, ¥50M monthly revenue | [Batch 1](./01_studios_batch_1.md) |
| 4 | **StoReel (世哆睿安)** | Beijing | US Market | Canvas tool, $34M funding | [Batch 1](./01_studios_batch_1.md) |
| 5 | **三垣映画 (Sanyuan)** | Shenzhen | First AIGC Live-Action | 500P compute, 110 countries | [Batch 1](./01_studios_batch_1.md) |
| 9 | **原神文化 (Yuanshen)** | Hangzhou | AI Content Factory | 360 Nanomi agents, 21-day cycle | [Batch 2](./02_studios_batch_2.md) |
| 10 | **灵境万维 (Lingjing AI)** | Hangzhou+Wuhan | AI Manga Industrial | Orders booked through 2027 | [Batch 2](./02_studios_batch_2.md) |
| 22 | **创翊传媒 (Chuangyi)** | — | Benchmark Producer | 万兽独尊 (100M views) | [Batch 5](./05_studios_batch_5.md) |

### Tier 4: Tool/Engine Companies (B2B SaaS)

| # | Company | Location | Type | Core Product | Batch |
|---|---------|----------|------|-------------|-------|
| 7 | **元界矩阵 (Vertex Matrix)** | Beijing | Platform Builder | Fiderma platform | [Batch 2](./02_studios_batch_2.md) |
| 19 | **有戏AI (Youxi AI)** | Beijing | Pure Tool | Multi-Agent engine, ¥0.1/sec | [Batch 4](./04_studios_batch_4.md) |
| 23 | **绘映网 (Huiying Net)** | — | One-Stop Factory | AI Visual Bible, 5-step workflow | [Batch 5](./05_studios_batch_5.md) |

### Tier 5: Indie / Creator-Led Studios (Viral hits, tiny teams)

| # | Company | Location | Type | Core Product | Batch |
|---|---------|----------|------|-------------|-------|
| 6 | **杨涵涵文化 (Yanghanhan)** | Wuhan | Director-Led | 霍去病 AI drama, ~20 people | [Batch 2](./02_studios_batch_2.md) |
| 8 | **抽象示界 (Abstract Vision)** | — | Indie Team | 2-5 core, viral overseas hits | [Batch 2](./02_studios_batch_2.md) |
| 20 | **创壹科技 (CreativeFitting)** | Shenzhen | Digital Humans + XR | 柳夜熙 IP, OneStory platform | [Batch 4](./04_studios_batch_4.md) |
| 21 | **海看股份 (Haikan)** | — | Self-Built Compute | Octopus AI editing, audit platform | [Batch 5](./05_studios_batch_5.md) |
| 24 | **剧小白 (JuXiaobai)** | Nanning | ASEAN-Facing | Government-backed, regional focus | [Batch 5](./05_studios_batch_5.md) |
| 25 | **捷成股份 (Jetsen)** | — | Hybrid Pipeline | Lingxi AI, 200K-hour library | [Batch 5](./05_studios_batch_5.md) |

---

## 2. Comparative Intelligence Matrices {#comparative-matrices}

### Matrix A: Production Speed & Cost

| Company | Team Size | Production Speed | Cost/Episode | Cost/Minute | Views (Flagship) |
|---------|-----------|-----------------|-------------|-------------|------------------|
| **创翊传媒** | 5 | 60 eps / 8 days | ~¥167 | ~¥100 | 100M+ (万兽独尊) |
| **有戏AI** | 1 | 1 drama / 1 day | <¥10 | ¥0.1/sec | N/A (tool) |
| **灵矩动漫** | 700 | 50-70 dramas/month | ¥5K-15K | ¥500-1,500 | Multiple hits |
| **酱油文化** | 1,200+ | Industrial scale | — | — | 8/10 top Douyin |
| **快手/Kling** | 3-6 | ~7 days/drama | ¥50K-100K | ¥500-1,000 | 1.37B impressions |
| **原神文化** | Small | 4 months→21 days | — | — | — |
| **华策影视** | Institute | — | — | ¥350-1,200 | 3.96B topic views |
| **昆仑万维** | Corp | Hours/drama | <$20K total | — | 80M MAU platform |
| **三垣映画** | — | 500P compute | — | — | 110 countries |
| **博纳影业** | Subsidiary | Months (pioneering) | — | — | 200M+ (三星堆) |

### Matrix B: Technology Stack per Layer

| Layer | ByteDance | Kuaishou | Kunlun | Youxi AI | Others |
|-------|-----------|----------|--------|----------|--------|
| **Script** | Xiaoyunque (100K chars) | Third-party LLMs | SkyScript (100M dataset) | Multi-Agent (50K chars) | 逍遥AI (COL), 有风 (Huace) |
| **Storyboard** | Auto from script | Kling multi-shot (6) | StoryboardGen (DiT-MoE) | Director Agent | 帧赞 (Yaoker) |
| **Video Gen** | Seedance 2.0 | Kling 3.0/O3 | SkyReels V1-V4 | External + optimize | Jimeng, MJ, SD |
| **Consistency** | Dual-branch diffusion | Element binding | E2V dual-branch | Persona Library + RAG | LoRA, IP-Adapter |
| **Audio** | Native AV sync | Native multimodal | Integrated V3/V4 | One-click + emotion | 火山TTS, ElevenLabs |
| **Editing** | Auto-assembly | Manual (AE/Premiere) | SkyProduction | Auto + CapCut export | 剪映/CapCut |
| **QC** | Strategic Review Agent | Human dominant | A/B testing via platform | Multi-Agent QC | Human review |
| **Distribution** | Douyin + 红果 | Kuaishou (700M users) | DramaWave + FreeReels | B2B (no platform) | Various |

### Matrix C: Character Consistency Methods (The #1 Technical Challenge)

| Method | Companies | How It Works | Reliability |
|--------|-----------|-------------|-------------|
| **Dual-Branch Diffusion Transformer** | ByteDance (Seedance 2.0) | Visual + audio features coupled from training inception; 12 simultaneous reference files | ★★★★★ Highest |
| **Elements-to-Video (E2V)** | Kunlun (SkyReels A2) | Separate spatial + semantic feature branches compose multi-element scenes | ★★★★★ |
| **Element Binding** | Kuaishou (Kling O3) | Multi-angle refs bound to named character library with feature tags | ★★★★☆ |
| **Persona Library + RAG** | Youxi AI | Stable context store with retrieval-augmented generation per frame | ★★★★☆ (95%+) |
| **Visual Bible** |绘映网, Industry SOP | Comprehensive character sheets (front/side/back, expressions, costumes) fed as static reference | ★★★★☆ |
| **LoRA Fine-Tuning** | Indie studios | Train character-specific LoRA on 20-50 images | ★★★☆☆ |
| **IP-Adapter** | Various | CLIP-based style/identity injection without fine-tuning | ★★★☆☆ |
| **Digital Human Rigs** | CreativeFitting | Full 3D character models with motion capture — permanent identity | ★★★★★ Highest |

### Matrix D: Strategic Archetype Map

| Archetype | Companies | Moat | Risk |
|-----------|-----------|------|------|
| **Platform Ecosystem** | ByteDance, Kuaishou | Distribution + creator lock-in + model | Regulatory, model commoditization |
| **Full Vertical Stack** | Kunlun Tech | Open-source community + distribution | Thin margins, model catch-up by rivals |
| **IP Factory** | COL, Huace, 酱油文化 | Content library, adaptation rights | IP exhaustion, quality floor |
| **State-Backed Platform** | Mango, 海看 | Regulatory compliance, funding | Bureaucratic speed, creative constraints |
| **Pure SaaS Tool** | Youxi AI, 绘映网 | Cost leadership, agent architecture | No distribution moat, commoditization |
| **Premium Studio** | CreativeFitting, Bona, VisionStar | Brand equity, visual quality | High cost, low volume |
| **Volume Factory** | 灵矩, 酱油, 灵境万维 | Scale, speed, process | Race to bottom, quality ceiling |
| **Indie Creator** | 杨涵涵, 抽象示界 | Agility, viral instinct, low overhead | No moat, single-person risk |

---

## 3. Technology Stack Breakdown {#tech-stack}

### The Universal Tool Stack (2026 Q2 Industry Standard)

| Pipeline Layer | Tier 1 Tools (Dominant) | Tier 2 Tools (Common) | Emerging |
|---------------|------------------------|----------------------|----------|
| **Script** | Xiaoyunque Agent, SkyScript, 逍遥AI | GPT-4/Claude, 豆包(Doubao), 通义千问 | Youxi AI Writer Agent |
| **Storyboard** | Xiaoyunque auto-storyboard, StoryboardGen | Manual prompt engineering, ComfyUI | Kling multi-shot auto |
| **Image Gen** | Seedream, Jimeng AI | Midjourney v6, FLUX, SD 3.5 | — |
| **Video Gen** | Seedance 2.0, Kling 3.0/O3 | SkyReels V4, Runway Gen-4 | Pika 2.0, Hailuo |
| **Character Lock** | Dual-branch (Seedance), E2V (SkyReels) | LoRA, IP-Adapter, Reference Images | Visual Bible protocol |
| **TTS/Voice** | Native AV sync (Seedance, Kling) | 火山TTS, ElevenLabs, 讯飞 | Voice cloning |
| **Music/SFX** | Platform-integrated, Suno | AI music generators, stock libraries | — |
| **Editing** | 剪映/CapCut, SkyProduction | Premiere, DaVinci, After Effects | Auto-assembly agents |
| **QC** | Multi-Agent QC (火山剧创) | Human review teams | AI审核 platforms |
| **Distribution** | Douyin, 红果, Kuaishou | TikTok, YouTube, ReelShort | DramaWave, FlareFlow |

### The 3 Dominant Production Architectures

#### Architecture 1: ByteDance Closed Loop (Most Adopted)
```
Script → Xiaoyunque Agent (100K chars, auto-parse)
  → Auto-Storyboard (camera directions, shot planning)
    → Seedance 2.0 (dual-branch, 12 refs, native AV sync)
      → Auto-Assembly (剪映 for final polish)
        → Douyin/红果 Distribution
```
**Who uses it:** 创翊传媒, 博纳影业, most indie creators
**Strength:** Lowest friction, fastest to production
**Weakness:** Platform dependency, closed ecosystem

#### Architecture 2: Kunlun Open-Source Stack (Most Replicable)
```
SkyScript (100M annotations) → script with dramatic structure
  → StoryboardGen (DiT-MoE) → industrial-grade storyboards
    → SkyReels A2 (E2V multi-element) → video with character consistency
      → SkyProduction → auto-editing and assembly
        → DramaWave/FreeReels → global distribution
```
**Who uses it:** Kunlun internal, open-source community
**Strength:** Fully open-source on HuggingFace, self-hostable
**Weakness:** Requires GPU infrastructure (RTX 4090+), less polished than ByteDance

#### Architecture 3: Multi-Agent Engine (Most Flexible)
```
Writer Agent → script comprehension + structure
  → Director Agent → cinematography-logic storyboards
    → Actor Agent → character performance direction
      → External Models (Jimeng, Kling, etc.) → video generation
        → Auto-Assembly → CapCut project export
          → Creator chooses platform
```
**Who uses it:** Youxi AI, 火山剧创 enterprise users
**Strength:** Model-agnostic, lowest cost (¥0.1/sec), best flexibility
**Weakness:** Depends on external model quality, no distribution

---

## 4. The Ideal Replicable Pipeline {#ideal-pipeline}

Based on best practices extracted from all 25 studios, here is the **recommended pipeline for replication**:

### Phase 0: Setup (One-Time)

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 0.1 | Define art style | — | Style guide document |
| 0.2 | Create Visual Bible | Seedream / Midjourney | Character sheets: front/side/back, 10+ expressions, 3+ costumes, props |
| 0.3 | Train LoRA (optional) | Kohya / ComfyUI | Character-specific LoRA weights for SD/FLUX |
| 0.4 | Set voice profiles | 火山TTS / ElevenLabs | Voice clones for each character |
| 0.5 | Build prompt templates | Manual | Reusable shot templates with style/character locks |

### Phase 1: Script (Day 1, Morning)

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 1.1 | Source IP or write original | Claude/GPT-4/豆包 | Story outline with hooks |
| 1.2 | Generate full script | Xiaoyunque Agent OR SkyScript | 30-60 episode scripts, 40K-100K chars |
| 1.3 | Structure validation | Human review | Hook-conflict-resolution per episode verified |
| 1.4 | Episode breakdown | Auto (Xiaoyunque) or manual | Scene list with shot counts per episode |

**Key Principle:** Every episode must end on a cliffhanger. Every 15 seconds must have a "dopamine hook."

### Phase 2: Storyboard (Day 1, Afternoon)

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 2.1 | Auto-generate storyboards | Xiaoyunque / StoryboardGen | Shot-by-shot visual plan |
| 2.2 | Specify camera language | Manual refinement | 景别 (shot size), 运镜 (camera move), 光影 (lighting) per shot |
| 2.3 | Lock character references | Visual Bible | Reference images bound to each character in each scene |
| 2.4 | Human review + adjust | Director review | Final storyboard approved |

**Key Principle:** Use "Fixed + Variable Layer" prompt strategy (from Youxi AI) — lock character core description, only vary action/expression/shot.

### Phase 3: Visual Generation (Day 2-4)

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 3.1 | Generate key frames | Seedream / Jimeng / MJ | Reference stills for each scene |
| 3.2 | Generate video clips | Seedance 2.0 / Kling O3 / SkyReels | 6-10 second clips per shot |
| 3.3 | Character consistency check | Visual comparison + AI | Verify face/costume consistency across shots |
| 3.4 | Re-generate failed shots | Same tool, adjusted prompts | Replace any shots with consistency breaks |
| 3.5 | Batch processing | Parallel generation | Multiple episodes generated simultaneously |

**Key Principle:** Generate 6-10 second clips (not longer) for maximum quality control. Typical ratio: generate 5-10x more clips than needed, select best.

### Phase 4: Audio (Day 4-5)

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 4.1 | Generate dialogue | 火山TTS / ElevenLabs | Character voice lines with emotion |
| 4.2 | Generate narration | Same tools | Narrator track |
| 4.3 | Add BGM | Suno / stock libraries | Background music per scene mood |
| 4.4 | Add SFX | Auto-matched or manual | Environmental sounds, action effects |
| 4.5 | Lip sync verification | Built-in (Seedance) or manual | Dialogue matches mouth movements |

**Key Principle:** If using Seedance 2.0, audio is generated natively with video (skip steps 4.1-4.4 for dialogue). Otherwise, post-hoc dubbing workflow.

### Phase 5: Editing & Assembly (Day 5-6)

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 5.1 | Auto-assemble clips | SkyProduction / 剪映 | Rough cut per episode |
| 5.2 | Add subtitles | 剪映/CapCut | Styled subtitles (大字报 style for impact) |
| 5.3 | Color grading | 剪映/DaVinci | Consistent color across scenes |
| 5.4 | Add transitions | Manual | Scene transitions, effects |
| 5.5 | Final review | Human | Pacing, emotional arc, hook verification |

**Key Principle:** Pacing target = 2-3 cuts per minute. Each episode 1-3 minutes. Vertical format (9:16) mandatory.

### Phase 6: Quality Control (Day 6-7)

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 6.1 | Character consistency audit | Frame-by-frame comparison | Flag any identity breaks |
| 6.2 | Narrative continuity check | Human review | Story logic verification |
| 6.3 | Technical quality check | Visual inspection | Resolution, artifacts, lip sync |
| 6.4 | Re-generate & fix | Targeted regeneration | Only fix flagged shots (not full redo) |
| 6.5 | Final approval | Director sign-off | Ready for distribution |

### Phase 7: Distribution (Day 7+)

| Step | Action | Tool | Output |
|------|--------|------|--------|
| 7.1 | Platform optimization | Format adaptation | Platform-specific versions |
| 7.2 | Upload batch | Platform tools | Episodes live on target platforms |
| 7.3 | Monitor performance | Analytics dashboards | Views, completion rate, revenue |
| 7.4 | Iterate on data | Content optimization | Adjust future episodes based on audience data |

### Pipeline Summary: 7 Days, 1-5 People, 30-60 Episodes

```
┌──────────────────────────────────────────────────────────────────────┐
│                    THE IDEAL AI DRAMA PIPELINE                       │
│                                                                      │
│  Day 1          Day 2-4        Day 4-5       Day 5-6      Day 7     │
│  ┌──────┐      ┌──────┐      ┌──────┐      ┌──────┐    ┌──────┐   │
│  │Script│─────▶│Video │─────▶│Audio │─────▶│Edit  │───▶│QC &  │   │
│  │  +   │      │ Gen  │      │      │      │  +   │    │Ship  │   │
│  │Story │      │      │      │      │      │Polish│    │      │   │
│  │board │      │      │      │      │      │      │    │      │   │
│  └──────┘      └──────┘      └──────┘      └──────┘    └──────┘   │
│                                                                      │
│  Tools: Xiaoyunque  Seedance 2.0  火山TTS    剪映/CapCut  Platform  │
│         OR SkyScript Kling O3     ElevenLabs SkyProd     Douyin     │
│         OR Claude    SkyReels V4  Suno       DaVinci     ReelShort  │
│                                                                      │
│  Cost: ¥5,000 – ¥50,000 total for 30-60 episode series             │
│  Team: 1-5 people                                                    │
│  Output: 30-60 episodes × 1-3 min each                              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 5. Cost & Speed Benchmarks {#cost-benchmarks}

### Cost Evolution (2024 → 2026)

| Metric | Early 2024 | Late 2024 | Mid 2025 | Q2 2026 |
|--------|-----------|-----------|----------|---------|
| Cost/minute (漫剧) | ¥3,000-5,000 | ¥2,000-3,000 | ¥800-1,500 | **¥100-500** |
| Cost/minute (仿真人) | ¥10,000+ | ¥5,000-8,000 | ¥2,000-3,000 | **¥500-1,500** |
| Production cycle (60 eps) | 3-6 months | 1-2 months | 2-4 weeks | **5-8 days** |
| Minimum team | 20-30 | 10-15 | 5-8 | **1-5** |
| Character consistency | Manual fix | LoRA/IP-Adapter | Visual Bible | **Model-native** |

### Lowest Cost Achievers

| Rank | Company/Tool | Cost/Second | Cost/Episode (2 min) | Method |
|------|-------------|-------------|---------------------|--------|
| 1 | **有戏AI (Youxi AI)** | ¥0.10 | <¥10 | Multi-Agent + external models |
| 2 | **Xiaoyunque Agent** | ~¥0.50 | ~¥60 | Seedance 2.0 pipeline |
| 3 | **Kunlun SkyReels** | ~¥1-2 | ~¥150 | Self-hosted open-source |
| 4 | **Kling AI** | ~¥3-5 | ~¥500 | API credits |
| 5 | **Industry average** | ~¥5-10 | ~¥800 | Mixed tools |

### Speed Records

| Record | Company | Details |
|--------|---------|---------|
| **Fastest full series** | 创翊传媒 | 60 episodes in 8 days (万兽独尊) |
| **Fastest viral hit** | 气运三角洲 creator | 200M views in 29 hours |
| **Lowest cost viral** | 李世民魂穿阿斗 creator | 100M views, total cost ¥10K |
| **Fastest to #1 chart** | 耀客传媒 | 秦岭青铜诡事录 → Tencent Video #1 in 12 hours |
| **Most efficient cycle** | 有戏AI | "1 person, 1 day, 1 drama" |

---

## 6. Distribution & Monetization Playbook {#distribution}

### Platform Landscape

| Platform | Owner | Model | Reach | Best For |
|----------|-------|-------|-------|----------|
| **抖音 (Douyin)** | ByteDance | Ad revenue + CPS | 700M+ DAU | Mass reach, viral potential |
| **红果短剧 (Hongguo)** | ByteDance | Free + ads | 100M+ users | Dedicated drama audience |
| **快手 (Kuaishou)** | Kuaishou | GMV sharing + ads | 700M+ MAU | Creator incentives |
| **微信视频号** | Tencent | Social distribution | 800M+ users | Organic social spread |
| **芒果TV** | Mango | Platform + grants | 50M+ users | State-backed content |
| **腾讯视频** | Tencent | Premium content | 120M+ subscribers | High-quality dramas |
| **ReelShort** | 枫叶互动 | IAP (episode unlock) | 50M+ downloads | US market |
| **DramaWave** | Kunlun Tech | Subscription | 80M MAU | Southeast Asia, Latin America |
| **FlareFlow** | COL | Ads + payments | 170+ countries | Global English markets |
| **TikTok** | ByteDance | Ad-supported | 1B+ global | Global viral distribution |

### Revenue Models Ranked by Profitability

| Model | Revenue/Drama | Scalability | Control |
|-------|--------------|-------------|---------|
| **Mini-program CPS** | ¥100K-1M+ | ★★★★★ | Medium |
| **Platform ad sharing** | ¥10K-100K | ★★★★☆ | Low |
| **IAP episode unlock** | $50K-500K+ | ★★★★☆ | High |
| **Subscription** | Recurring | ★★★★★ | High |
| **Brand integration** | ¥50K-500K | ★★★☆☆ | Medium |
| **IP licensing** | Variable | ★★★☆☆ | High |

### Platform Creator Incentive Programs (2026)

| Platform | Program | Value |
|----------|---------|-------|
| **Kuaishou** | 磁力引擎 | ¥8B revenue sharing + ¥2B cash + 1B traffic |
| **Mango TV** | Creator Ecosystem | ¥100K-1M/project + 120 scripts + millions in points |
| **Douyin** | Various | Traffic allocation + creator funds |
| **Kuaishou** | 全民AI制作人 | AI tools + talent incubation |

---

## 7. Strategic Recommendations {#recommendations}

### For Building a Competing AI Drama Production System

#### Recommended Stack (Fastest Path)

| Layer | Primary Choice | Fallback | Why |
|-------|---------------|----------|-----|
| **Script** | Claude/GPT-4 + human writer | Xiaoyunque Agent | More creative control; Agent for speed |
| **Storyboard** | Xiaoyunque auto-storyboard | Manual + StoryboardGen | Fastest; StoryboardGen for self-hosted |
| **Video** | Seedance 2.0 (via Xiaoyunque) | SkyReels V4 (open-source) | Best quality; SkyReels for independence |
| **Consistency** | Seedance dual-branch + Visual Bible | LoRA + reference images | Model-native is superior |
| **Audio** | Native (Seedance) + 剪映 polish | ElevenLabs + Suno | Native AV sync saves days |
| **Editing** | 剪映/CapCut | SkyProduction | Universal tool, export flexibility |
| **QC** | Human review (1 person) | Multi-Agent QC (Youxi AI) | Quality judgment still human-led |
| **Distribution** | Douyin + ReelShort (dual-market) | FlareFlow + TikTok | China + US simultaneously |

#### Recommended Stack (Full Independence — No Platform Lock-in)

| Layer | Choice | Source |
|-------|--------|--------|
| **Script** | SkyScript | HuggingFace `Skywork` org |
| **Storyboard** | StoryboardGen | HuggingFace `Skywork` org |
| **Video** | SkyReels A2 + V3 | HuggingFace `Skywork` org |
| **3D Assets** | Sky3DGen + WorldEngine | HuggingFace `Skywork` org |
| **Editing** | SkyProduction | Kunlun internal (API access) |
| **Distribution** | Self-hosted / multi-platform | DramaWave partnership or direct |
| **Hardware** | RTX 4090 cluster (24GB+) | Cloud or self-hosted |

### Critical Success Factors (Extracted from 25 Studios)

1. **Hook density** — Every 15 seconds must deliver a dopamine hit. Every episode ends on a cliffhanger. This is non-negotiable for retention.

2. **Character Visual Bible** — Before generating a single frame, create comprehensive character reference sheets. This is the single highest-ROI investment in the pipeline.

3. **Batch, don't iterate** — Generate 5-10x more clips than needed, then select. This is faster than iterating on individual shots.

4. **6-10 second clips** — Never generate clips longer than 10 seconds. Quality degrades rapidly with length. Stitch shorter clips in post.

5. **Fixed + Variable prompting** — Lock character descriptors (fixed layer), only modify action/expression/shot (variable layer). Prevents face collapse.

6. **Distribution-first thinking** — Choose your platform before you choose your story. Platform algorithm preferences shape content decisions.

7. **Vertical format (9:16)** — This is non-negotiable. 99% of consumption is mobile vertical.

8. **Speed over perfection** — The market rewards volume and iteration speed. A good drama released today beats a perfect drama released next month.

### The 2026 Industry Meta

> **"The era of 'one person + AI agents' has arrived. The competitive advantage is no longer production capability — it's storytelling instinct and distribution intelligence."**

The technology stack is commoditizing rapidly. Every tool converges toward similar capabilities. The differentiators are:

1. **Story selection** — Which IPs/genres resonate? Data-driven selection is critical.
2. **Platform algorithm mastery** — Understanding what Douyin/ReelShort/TikTok promote.
3. **Character design** — Memorable, distinctive characters that audiences bond with.
4. **Speed of iteration** — Release → measure → adjust → release cycle should be weekly.
5. **Multi-market strategy** — Simultaneously serving China (Douyin/红果) + overseas (ReelShort/TikTok) doubles addressable market.

---

## Appendix: File Index

| File | Contents | Size |
|------|----------|------|
| [discovery_list.md](./discovery_list.md) | Initial 25-studio identification list | 3.6KB |
| [01_studios_batch_1.md](./01_studios_batch_1.md) | Companies 1-5: VisionStar, Lingju, Jiangyou, StoReel, Sanyuan | 36.8KB |
| [02_studios_batch_2.md](./02_studios_batch_2.md) | Companies 6-10: Yanghanhan, Vertex Matrix, Abstract Vision, Yuanshen, Lingjing | 31.7KB |
| [03_studios_batch_3.md](./03_studios_batch_3.md) | Companies 11-15: Bona, Huace, Mango, Yaoker, ByteDance/Xiaoyunque | 33.9KB |
| [04_studios_batch_4.md](./04_studios_batch_4.md) | Companies 16-20: Kuaishou/Kling, Kunlun/SkyReels, COL, Youxi AI, CreativeFitting | 32.8KB |
| [05_studios_batch_5.md](./05_studios_batch_5.md) | Companies 21-25: Haikan, Chuangyi, Huiying, JuXiaobai, Jetsen + Case Studies + 2026 SOP | 27.5KB |
| [00_master_report.md](./00_master_report.md) | This file — synthesis, matrices, ideal pipeline, recommendations | — |

**Total intelligence corpus: ~166KB+ across 7 files.**

---

*Research conducted by 7-agent parallel research team. 2026-05-25.*
*Sources: 50+ Chinese-language primary sources including 36kr, huxiu, volcengine, eastmoney, thepaper, sina, geekpark, huggingface, github, BOSS直聘, and company-direct publications.*
