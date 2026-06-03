# Chinese AI Short Drama Studios — Complete Production Intelligence Report
# Batch 1: 5 Studios Deep Dive

> **Research Date**: May 25, 2026
> **Sources**: 36kr.com, ifeng.com, qq.com, thepaper.cn, iyiou.com, lg.gov.cn, businessinsider.com, techinasia.com, lmtw.com, juduanduan.com, qiniu.com, smzdm.com, segmentfault.com, cnblogs.com, rongyudq.com, yunzhongwenhua.com, volcengine.com, sznews.com, storeel.art, aitop100.cn, peopleapp.com, funnelfox.com, adjust.com, preqin.com, tracxn.com + industry reports

---

## INDUSTRY CONTEXT (2025–2026)

### Market Scale & Growth
- **2025 market size**: AI manga/animation drama market reached ~¥189.8 billion (~276% YoY growth)
- **2030 projection**: Expected to surpass ¥850 billion
- **2025 was dubbed "漫剧元年"** (Year Zero for AI manga drama) — the category exploded from near-zero to massive scale

### Regulatory Landscape
- **April 1, 2026**: NRTA (国家广电总局) enforced **"先备案后上线"** (file before launch) for ALL AI dramas
- **Tiered review system**:
  - **重点类 (Priority)**: Investment ≥¥3M or sensitive topics → NRTA national review, requires 《网络剧片发行许可证》
  - **普通类 (Standard)**: Investment ¥1M–3M → Provincial-level review
  - **其他类 (Other)**: Investment <¥1M, general topics → Platform self-review + provincial filing
- **Mandatory AI labeling**: All AI-generated content must display "AI制作" watermark
- **Existing content purge**: All pre-existing works had to complete retroactive review by March 31, 2026 or face forced removal

### Platform Wars
| Platform | Strategy | Revenue Share | Key Feature |
|---|---|---|---|
| **抖音 (Douyin)** | "辰星计划" + "星光计划" | 90–95% | Short Drama Copyright Center, multi-platform syndication |
| **红果 (Red Fruit/Hongguo)** | Full lifecycle support (script → distribution) | High + subsidies | Cross-platform distribution to Douyin native |
| **快手 (Kuaishou)** | "星芒创想计划" + 可灵AI integration | GMV-sharing model | Deep AI tool integration, shifting from ROI-based buying |
| **阅文集团 (Yuewen/China Literature)** | IP licensing + "漫剧助手" tool | Revenue share + IP fees | Massive web novel IP library, 400+ dramas/year target |

### Cost Revolution
| Metric | Traditional Live-Action | AI Drama |
|---|---|---|
| **Cost per minute** | ~¥10,000+ | ¥100–1,500 |
| **Production cycle (full series)** | 2–6 months | 3 days – 2 weeks |
| **Team size per project** | 30–100+ people | 3–7 people |
| **Cost reduction** | Baseline | **10–100x cheaper** |

### The "抽卡师" (Gacha Artist) Phenomenon
A new profession born from AI drama production. 抽卡师 (literally "card pullers") are AI prompt engineers who:
- Repeatedly generate visuals using AI tools and select the best outputs (like "pulling for SSR cards" in gacha games)
- Require high aesthetic judgment + deep AI tool proficiency
- Are NOT traditional artists, but need superior visual taste
- Typical salary range reflects the demand-supply dynamics of this nascent role

---

## 1. 万像天影 (VisionStar / Wanxiang Tianying)

### Company Overview
| Field | Details |
|---|---|
| **Full Name** | 杭州万像天影影视科技有限公司 |
| **Location** | Hangzhou, Zhejiang |
| **Founded** | ~2023 |
| **Founder / Legal Rep** | **李一介 (Li Yijie)** |
| **Positioning** | "AI Disney" — full-pipeline AI filmmaking company |
| **Funding** | Not publicly disclosed; strategic partner of Alibaba Cloud (通义大模型) |
| **Team Size** | Not publicly disclosed (estimated small-medium) |

### Notable Projects
- **《联通平行宇宙》** — AI全流程 sci-fi short drama, co-produced with China Unicom + 时光坐标 (Suncreate)
- **《The Pickup》** — Hollywood action comedy; provided virtual shooting scenes & AI visual compositing
- **Alibaba Cloud collaboration** — Strategic partner for 通义 (Tongyi) large model; co-produced AI video model promotional films
- **"时光万像" AI Film Creation Plan** — Co-launched with 时光坐标 and Zhejiang Starlight Cinema in May 2026; industry-academia integration platform

### LAYER 1: SCRIPT (剧本)
- **AI-assisted scriptwriting** using large language models: Claude, DeepSeek, 豆包 (Doubao)
- **Structured prompt input**: Story settings → AI generates net-savvy, structurally tight short drama scripts
- **Focus on "网感"** (internet sensibility): fast-paced conflict, emotional hooks, cliffhanger-per-episode structure
- **IP source**: Both original and adapted; partnership ecosystem with IP holders

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)
- **AI-powered storyboard decomposition**: Text scripts → detailed shot scripts including:
  - Camera language (景别/shot types, 运镜/camera movement)
  - Character actions and expressions
  - Dialogue placement and timing
- **This layer is the "command baton"** — the more detailed the storyboard, the higher the success rate of generated footage
- **Typical granularity**: Each shot specifies duration (5–10 seconds recommended), composition, emotional tone

### LAYER 3: VISUAL GENERATION (画面生成)
- **Full-pipeline AI creation system** — unified workbench approach vs. fragmented tool-hopping
- **Character & Scene Asset Library**:
  - Multi-angle character views generated via Stable Diffusion, Midjourney
  - Locked as fixed visual assets for reuse across all shots
  - Asset versioning and management system
- **Video generation**: Seedance 2.0, Vidu, and other models for dynamic video from storyboards
- **Fine control**: ControlNet for precise pose/action control
- **ComfyUI integration**: Node-based workflow connecting multiple AI models:
  - SDXL/Flux for base images → 可灵/即梦 APIs for video → Upscale/Inpainting for refinement
- **Style**: Supports manga/anime, photorealistic, and hybrid approaches
- **Resolution**: 9:16 vertical for short drama platforms; high-res upscaling in pipeline

### LAYER 4: AUDIO & VOICE (音频/配音)
- **Voice cloning**: ElevenLabs, Fish Audio — clone character voices from small samples
- **Emotion injection**: Emotional tags (excited, melancholic, angry) for natural delivery
- **Background music**: AI-generated via Suno and similar tools
- **Sound effects**: Auto-matched to plot points and scene transitions
- **Lip sync**: Advanced lip-sync generation aligned to dialogue

### LAYER 5: EDITING & POST-PRODUCTION (剪辑/后期)
- **AI-powered structured editing**:
  - Face detection, voiceprint matching, audio-visual alignment
  - Automated assembly of scattered raw clips into coherent episodes
- **Post-processing**: AI-driven transitions, color grading, watermark removal, video compression
- **Platform compliance**: Auto-formatting to meet upload standards for Douyin, Red Fruit, etc.
- **"One-click to finished film"** (一键成片) capability for rapid iteration

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)
- **Unified workspace eliminates** the problem of character "drift" (服装、长相 inconsistencies across shots)
- **Asset-first approach**: Pre-built character/scene libraries ensure visual consistency across episodes
- **Version control**: Asset versioning, project progress tracking, team collaboration tools
- **QC benchmarks**: Character consistency, narrative coherence, platform compliance checks

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)
- **Platforms**: Douyin, Red Fruit, and potentially overseas via partnership networks
- **B2B positioning**: Also provides AI filmmaking services/tools to other production companies
- **Revenue model**: Service fees + content distribution revenue
- **Strategic partnerships**: Alibaba Cloud, China Unicom, 时光坐标, Hollywood productions

---

## 2. 灵矩动漫 (Lingju Animation)

### Company Overview
| Field | Details |
|---|---|
| **Full Name** | 灵矩动漫 (under 剧点短剧 / Judian Short Drama / 剧点网络) |
| **Location** | Hangzhou, Zhejiang |
| **Founded** | Originally a live-action short drama company (8+ years in web novel industry); pivoted to AI manga drama in 2025 |
| **Parent Company** | 剧点网络 (Judian Network) |
| **Positioning** | Top-volume AI manga drama factory; industrial-scale production |
| **Funding** | Not publicly detailed; backed by parent company's web novel + live-action revenue |
| **Team Size** | **~700 people** (as of early 2026; grew from <20 in July 2025 → 150 in September 2025 → 700+) |

### Key Metrics
| Metric | Value |
|---|---|
| **Monthly output** | **50–70 dramas/month** (industry-leading) |
| **Hit rate** | **70–80%** (e.g., 8 launched, 7 became hits during one National Day period) |
| **Production cycle** | ~22 days from project launch to online release (100-minute drama) |
| **Per-drama cost** | ~¥100K–150K per 100-minute drama (~¥1,000–1,500/minute) |
| **ROI** | 1.15–2.0x (industry-leading) |
| **2025 Douyin views** | 9.92 billion cumulative views on drama channel |

### Representative Works
- **《收徒万倍返还》** — Cumulative views exceeding 100M+ (signature hit)
- **《年过65 我靠续命红颜修成仙》** — Consecutive 2-week TOP 10 industry ranking
- Multiple male-oriented (男频): fantasy, apocalypse, cultivation genres

### LAYER 1: SCRIPT (剧本)
- **Human editors remain central** for controlling "爽点" (dopamine hooks) and emotional triggers
- **AI models** (豆包, Claude, DeepSeek) used for:
  - Expanding story outlines
  - Storyboard decomposition
  - Dialogue polishing
- **IP source**: Adapted from web novels (8+ years of novel industry experience)
- **Script structure**: Episodes optimized for short drama cadence — strong conflict, fast pace, cliffhanger endings

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)
- **LLM-powered storyboard conversion**: Novel content → shot scripts with "camera language"
- **Prompt engineering as core skill**: Storyboards are translated into precise prompts for AI generation
- **Shot duration**: 5–10 seconds per shot recommended (longer shots cause "logical collapse" in AI generation)
- **Detailed specifications**: Shot type, camera movement, character expressions, dialogue, emotional tone

### LAYER 3: VISUAL GENERATION (画面生成)
- **"Squad + Platform" model (小组制 + 中台模式)**:
  - Each squad: 3–4 抽卡师 (gacha artists) + screenwriter + director
  - Central platform (中台) provides standardized prompts, style guides, QA
- **Character consistency solutions**:
  - **LoRA training**: Dedicated character LoRA models for identity lock
  - **ControlNet**: Precise pose/posture control
  - **IP-Adapter + FaceID**: Face feature extraction as generation constraint
  - **InstantID / PuLID**: High-fidelity face preservation
  - **Fixed seed values**: Reproducibility across generations
- **Asset generation**: Dedicated 抽卡师 batch-generate materials using standardized description words from the central platform
- **Style**: Primarily manga/anime aesthetic

### LAYER 4: AUDIO & VOICE (音频/配音)
- **TTS (Text-to-Speech)** for character voices
- **Tools**: 魔音工坊 (domestic), ElevenLabs (international), Microsoft Azure TTS
- **Voice cloning**: Character-specific voice profiles from small samples
- **BGM**: AI-generated background music matched to scene mood
- **Sound effects**: Auto-synchronized to action beats
- **Lip sync**: ComfyUI workflows with Qwen3-TTS or LTX2.3 for automated mouth-to-speech alignment

### LAYER 5: EDITING & POST-PRODUCTION (剪辑/后期)
- **Central platform (中台) handles post-production** — ensures standardization and quality stability
- **Tool**: 剪映 (CapCut/JianYing) as primary editing platform
- **Automated processes**: Clip assembly, subtitle generation, transition effects
- **Quality standardization**: Templates and style guides maintained by the central platform team

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)
- **Central platform QA**: All output reviewed against platform standards before release
- **Character consistency audits**: Cross-episode visual checks
- **Iteration cycle**: Failed shots are re-generated (re-"抽卡") rather than manually fixed
- **Knowledge accumulation**: Successful prompts and workflows are codified into the central platform for reuse

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)
- **Primary platforms**: 抖音 (Douyin), 红果 (Red Fruit)
- **Monetization model**:
  - **IAP (付费解锁)**: Users pay to unlock episodes — primary revenue driver
  - **IAA (广告变现)**: Ad-supported free viewing
  - **投流 (Traffic buying)**: 80–90% of costs go to user acquisition
- **Revenue per hit**: Top-performing drama with ~¥2M in user spending generates ~¥400K profit
- **Distribution strategy**: Multiple works in market simultaneously; portfolio approach to manage hit rate variance

---

## 3. 酱油文化 (Jiangyou Culture)

### Company Overview
| Field | Details |
|---|---|
| **Full Name** | 南昌优瑞动漫有限公司 (Jiangxi Yourui Animation / "Jiangyou Culture") |
| **Location** | Nanchang, Jiangxi (formerly associated with Hangzhou operations) |
| **Founded** | Transitioned from web novel/live-action to AI manga drama ~2025 |
| **Founder** | **黄浩南 (Huang Haonan)** (b. 1996), alias "酱油"; 10+ years in web novel industry |
| **Positioning** | Industrial-scale "AI manga drama factory" |
| **Funding** | **Angel round from 阅文集团 (China Literature / Yuewen Group)** — Tencent-backed |
| **Team Size** | **1,000–1,200+ people** |

### Key Metrics
| Metric | Value |
|---|---|
| **Monthly revenue** | **~¥50 million** (单月营收5000万) |
| **Monthly output** | **~100 dramas/month** (target: 100+ "精品" dramas) |
| **Production cycle** | **~3 days per drama** (compressed from 30-day traditional cycle) |
| **Per-drama cost** | ¥50K–150K per drama |
| **Douyin dominance** | **8 of top 10** highest-earning dramas on Douyin (August 2025) belonged to Jiangyou |

### Representative Works
- **《洪荒：代管截教，忽悠出一堆圣人》** — 2.7 billion views total; broke 100M in 4 days
- **《魅魔叛主：反手培养十二翼炽天使》** — Broke 100M views in 10 days
- **《再也不当后爸》** — 120M views after adaptation
- **《玩具店卖机甲我震惊全世界》**
- **《国运擂台之妖神镇天》** — ~30M views in 2 days

### LAYER 1: SCRIPT (剧本)
- **Human screenwriters** maintain control of "爽点" (pleasure points) and emotional hooks
- **AI models** (豆包, Claude, DeepSeek) for:
  - Story expansion from outlines
  - Storyboard decomposition
  - Dialogue refinement
- **IP source**: Primarily adapted from web novels; partnership with 阅文集团 for IP licensing
  - Agreement: 400+ dramas/year, 50%+ adapted from Yuewen IP library
- **Hit formula**: "强钩子 + 高情绪 + 快节奏 + 可互动" (strong hooks + high emotion + fast pace + interactivity)
- **Genre focus**: Male-oriented (男频) fantasy, cultivation, apocalypse, "brain-hole" concepts

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)
- **AI-assisted storyboard generation** from script text
- **Detailed prompt engineering**: Scene descriptions, camera angles, character positioning, emotional beats
- **Production-optimized**: Minimizes complex scene count to reduce rendering pressure
- **Platform tools**: 阅文 "漫剧助手" (Manga Drama Assistant) for IP-adapted storyboarding

### LAYER 3: VISUAL GENERATION (画面生成)
- **"AI + Human" fine production model**:
  - Dedicated 抽卡师 teams for batch generation
  - Extensive prompt tuning and aesthetic selection
- **Character consistency**:
  - Fixed seed (Seed) values
  - LoRA model training for character-specific appearances
  - Character library/asset management
- **Tools**: Seedance 2.0, and other video generation models
- **No single tool solves everything**: Head companies use proprietary AI tools + workflow management systems
- **Style**: Manga/anime with strong visual "brain-hole" aesthetics matching the fantastical source material

### LAYER 4: AUDIO & VOICE (音频/配音)
- **AI voice generation** (TTS) for all character dialogue
- **Voice cloning** for character consistency across episodes
- **BGM and sound effects**: AI-generated and manually curated
- **Lip sync**: Integrated into post-production pipeline

### LAYER 5: EDITING & POST-PRODUCTION (剪辑/后期)
- **剪映 (CapCut/JianYing)** as primary editing platform
- **Assembly pipeline**: Clip concatenation, subtitle overlays, transition effects
- **AI-assisted**: Audio-visual synchronization, filter optimization
- **"网感" (internet sensibility)** optimization: Pacing, hooks, scroll-stopping techniques

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)
- **Scale demands rigorous QC**: At 100+ dramas/month, systematic quality checks are essential
- **AI-generated content is treated as "semi-finished"**: Significant human correction for:
  - Character jumping/inconsistency between shots
  - Action logic errors
  - Hand/eye detail issues
- **Massive "抽卡" debugging**: Repeated generation and selection until acceptable quality
- **Precision refinement teams**: Dedicated staff for AI output touch-ups

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)
- **Primary platforms**: 抖音 (Douyin), 快手 (Kuaishou), 红果 (Red Fruit)
- **Red Fruit is key**: Bytedance platform with strong AI drama support, traffic access, guaranteed floor revenue
- **Monetization**:
  - **IAP + IAA hybrid**: Free episodes + ad-unlocked episodes + paid unlock for deep storylines
  - **投流变现** (traffic-buying monetization): Core business model
- **Strategic partnership with 阅文集团**:
  - Future 3-year plan: 400+ dramas/year
  - 50%+ adapted from Yuewen IP
  - Joint content distribution and promotion

---

## 4. StoReel (世哆睿安)

### Company Overview
| Field | Details |
|---|---|
| **Full Name** | 北京世哆睿安科技有限公司 (StoReel) |
| **Location** | HQ: Sunnyvale, CA (USA); Operations: Beijing, China |
| **Founded** | 2024 |
| **Founder / CEO** | **范世鹏 (Eric Fan)** — ex-柠萌影视 (Ningmeng Media) short drama business head |
| **Co-founders** | 张睿 (Janry), Angela Yu |
| **Team background** | PKU, Columbia University grads; blend of internet product, content production, AI tech |
| **Positioning** | AI-native entertainment platform targeting US/global market |
| **Funding** | **$34M raised** |
| **Target market** | North America (primarily), English-speaking countries |

### Business Model: "Platform + Tool" Dual Engine
1. **StoReel App** (Content Platform):
   - AI-generated short drama content for overseas consumers
   - Interactive features: plot voting, multi-modal AI character interaction (text, voice, video)
   - Subscription-based with freemium options
2. **StoReel Canvas** (AI Creation Tool):
   - Self-developed one-stop AI filmmaking tool + creator community
   - Integrates multiple mainstream generation models
   - Full workflow: storyboard → character/scene management → image/video generation → collaboration → publishing

### Key Metrics
| Metric | Value |
|---|---|
| **Cost reduction** | 10–20% of traditional live-action costs (i.e., 80–90% cost savings) |
| **Efficiency gain** | ~3x production efficiency improvement |
| **Subscription pricing (North America)** | $19.9–$29.9/week or $239.99–$269/year |
| **App Store ranking** | Top 14 on US iOS Entertainment chart at peak |
| **Content approach** | AI-native (not retrofitting live-action) |

### LAYER 1: SCRIPT (剧本)
- **AI-assisted scriptwriting** within Canvas platform
- **Creator task matching**: Platform assigns scripts or creators bring their own
- **Genre adaptation**: Optimized for Western audience preferences (action, romance, thriller)
- **Multi-language**: Content created for English-speaking markets

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)
- **Smart storyboard decomposition** built into Canvas
- **Text-to-visual pipeline**: Script → shot sequences with narrative rhythm control
- **Standardized workflow**: Ensures consistent output quality across different creators

### LAYER 3: VISUAL GENERATION (画面生成)
- **Multi-model orchestration**: Canvas integrates multiple mainstream generation models
- **Character consistency**: Core focus area with proprietary solutions
  - Reference anchor system for character identity persistence
  - Multi-modal understanding for consistent character features across shots
- **Asset management**: Character & scene asset library with reuse capability
- **HD/Super-resolution processing**: Upscaling for cinematic quality
- **Lighting style optimization**: AI-driven lighting and mood control

### LAYER 4: AUDIO & VOICE (音频/配音)
- **AI voice generation**: Multiple language support for global markets
- **Lip sync generation**: Automated mouth-to-speech synchronization
- **Multi-modal interaction**: Users can interact with AI characters via voice
- **Sound design**: Integrated into Canvas workflow

### LAYER 5: EDITING & POST-PRODUCTION (剪辑/后期)
- **Canvas handles end-to-end**: Generation → editing → export within unified platform
- **Cinema-grade post-production**: Super-resolution, lighting adjustment, lip-sync refinement
- **Collaborative features**: Multiple creators can work on same project
- **Asset iteration**: Version control and rapid iteration within platform

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)
- **Platform-mediated QC**: StoReel reviews content before distribution
- **Creator feedback loop**: Tools for iterative improvement
- **Character consistency monitoring**: Cross-episode visual coherence checks
- **Technical quality**: Resolution, lip-sync accuracy, audio-visual sync verification

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)
- **StoReel App**: Direct-to-consumer distribution on iOS/Android
- **Target geography**: North America primary, expanding globally
- **Monetization model — hybrid**:
  - **Subscription**: $19.9–$29.9/week, $239.99–$269/year → primary revenue source
  - **Freemium**: Free viewing with ad-unlocking
  - **Pay-per-episode**: Virtual currency for episode unlocking after "suspense points"
  - **Future**: Gamification, virtual gifts, character IP merchandise, interactive plot unlocks, brand partnerships
- **Creator economy**: Creators earn through platform task system + revenue sharing
- **Decentralized content**: Creators own and operate their character/story IPs long-term

---

## 5. 三垣映画 (Sanyuan Yinghua)

### Company Overview
| Field | Details |
|---|---|
| **Full Name** | 三垣映画（深圳）文化科技有限公司 |
| **Location** | Shenzhen, Guangdong (Longgang District — 粤港澳超高清数创产业园) |
| **Founded** | ~2025 |
| **Positioning** | AIGC live-action micro-drama IP investment & industrial operations |
| **Distinction** | Produced **China's first full-process AIGC live-action micro-drama** |
| **Funding** | Backed by 3-party consortium (infrastructure + operations + distribution) |

### Strategic Consortium (三方协同)
| Partner | Role | Capabilities |
|---|---|---|
| **星视达超高清科技** (Starview Ultra HD) | Hardware infrastructure | 6,000 sqm professional studios, **500P compute cluster**, post-production center |
| **青骊影视文化传媒** (Qingli Media) | Operations & ecosystem | Official operator of Longgang micro-drama center; AIGC toolchain building, talent aggregation |
| **百川文化科技** (Baichuan Culture) | Content & distribution | Hit-making expertise; **110-country distribution network**, 8 language support |

### Notable Projects
- **《我家俩萌宝来自地府》** (My Two Cute Babies From the Underworld):
  - **China's first full-process AIGC live-action horizontal micro-drama**
  - Zero real locations, zero live actors
  - All character generation, scene construction, performance driving by AI
  - Entered **Tencent Video AI Creation Competition** (short drama category) national Top 20
  - Content cooperation deal with Tencent Video
  - Launched on Tencent Video January 19, 2026

### LAYER 1: SCRIPT (剧本)
- **AI-driven scriptwriting**: Large language models (Claude, 豆包) for script generation
- **Scene optimization**: Deliberately reduces complex scene count to lower rendering pressure
- **Structure**: Strong conflict, fast pace — optimized for short-form attention spans
- **Genre**: Fantasy/supernatural themes (地府/underworld, supernatural family comedy)

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)
- **Detailed visual decomposition**: Story → shot-by-shot with explicit:
  - Camera angles and movement instructions
  - Character actions and facial expressions
  - Dialogue and emotional markers
- **The "bridge" layer**: Storyboard quality directly determines AI generation success rate
- **Format**: Horizontal (横屏) — differentiating from typical vertical short dramas

### LAYER 3: VISUAL GENERATION (画面生成)
- **Full AIGC pipeline** — NO real photography:
  - AI character generation (photorealistic style, not manga)
  - AI scene/environment construction
  - AI performance driving (expressions, body movement)
- **Character consistency**:
  - Multi-angle character reference sheets (三视图) generated and locked
  - Uploaded to toolchain for identity anchoring across all scenes
- **Tools**: 即梦 (Jimeng/Seedance), 可灵 (Kling) and other video generation models
- **Style**: **Photorealistic live-action** (not manga — key differentiator from Lingju/Jiangyou)
- **Compute**: Leverages 500P intelligent compute cluster from partner 星视达

### LAYER 4: AUDIO & VOICE (音频/配音)
- **AI voice synthesis**: TTS with emotion modeling for all dialogue
- **Voice tools**: 百宝音 (domestic benchmark), ElevenLabs, 冬瓜配音 (CapCut-compatible)
- **Sound design**: AI-generated BGM + sound effects synchronized to plot beats
- **Lip sync**: Automated lip-sync generation for photorealistic characters

### LAYER 5: EDITING & POST-PRODUCTION (剪辑/后期)
- **剪映 (CapCut/JianYing)** for final assembly
- **AI-powered post**: Auto lip-sync correction, audio-visual alignment
- **Quality polish**: Color grading, transition effects, subtitle overlay
- **Format**: Horizontal (横屏) format for Tencent Video platform standards

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)
- **Multi-stage review**: Technical quality + narrative coherence + platform compliance
- **Photorealistic demands higher QC**: Live-action style has lower tolerance for AI artifacts
- **Character consistency is critical**: Any "uncanny valley" issues immediately break immersion
- **Competition validation**: Entry into Tencent Video AI Creation Competition served as external quality benchmark

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)
- **Primary platform**: 腾讯视频 (Tencent Video) — content cooperation deal
- **Distribution network**: Via 百川文化 (Baichuan Culture):
  - **110+ countries** covered
  - **8 major languages** supported
  - Proven hit-making track record: 《何苦相思煮余年》 — 500M views in 24 hours
- **"超清星河·百部AIGC微短剧版权投资计划"**: Plan to produce 100 AIGC micro-dramas through IP investment model
- **Monetization**: Platform revenue sharing + IP licensing + global distribution revenue
- **Government support**: Longgang District "All in AI" strategy with policy incentives for AIGC content production

---

## CROSS-COMPANY COMPARISON TABLE

| Dimension | 万像天影 (VisionStar) | 灵矩动漫 (Lingju) | 酱油文化 (Jiangyou) | StoReel (世哆睿安) | 三垣映画 (Sanyuan) |
|---|---|---|---|---|---|
| **Location** | Hangzhou | Hangzhou | Nanchang | Sunnyvale/Beijing | Shenzhen |
| **Team Size** | Undisclosed (small-med) | ~700 | ~1,200+ | Undisclosed (startup) | Consortium model |
| **Monthly Output** | B2B focused | 50–70 dramas | ~100 dramas | Scaling via creators | Project-based |
| **Visual Style** | Flexible (all styles) | Manga/anime | Manga/anime | AI-native (multiple) | **Photorealistic** |
| **Target Market** | China + Hollywood | China (Douyin/Red Fruit) | China (Douyin/Kuaishou) | **US/North America** | China + Global (110 countries) |
| **Monthly Revenue** | Undisclosed | Profitable (ROI 1.15–2.0x) | **¥50M/month** | Subscription-based | Investment model |
| **Funding** | Alibaba Cloud partnership | Parent company backed | 阅文集团 angel round | **$34M raised** | 3-party consortium |
| **Key Differentiator** | Full-pipeline AI system | Industrial scale + hit rate | Massive volume + Yuewen IP | US market + Canvas tool | First AIGC live-action drama |
| **IP Strategy** | Original + client projects | Web novel adaptation | Yuewen IP library (400+/yr) | Creator-generated | Investment + Baichuan catalog |
| **Per-drama Cost** | Service-based pricing | ¥100K–150K | ¥50K–150K | 10–20% of live-action | Reduced by 10x vs traditional |
| **Production Cycle** | Hours to days | ~22 days | ~3 days | Rapid via Canvas | Project-dependent |
| **Hit/Top Work** | 《联通平行宇宙》 | 《收徒万倍返还》(100M+) | 《洪荒：代管截教》(2.7B) | App peaked #14 US iOS | 《我家俩萌宝来自地府》 |

---

## UNIVERSAL TOOL STACK TABLE

| Pipeline Layer | Tool / Technology | Category | Used By |
|---|---|---|---|
| **Script** | Claude | LLM — Scriptwriting | VisionStar, Lingju, Jiangyou, Sanyuan |
| **Script** | DeepSeek | LLM — Scriptwriting | VisionStar, Lingju, Jiangyou |
| **Script** | 豆包 (Doubao) | LLM — Scriptwriting | VisionStar, Jiangyou, Sanyuan |
| **Script** | ChatGPT / GPT-4 | LLM — Scriptwriting | Industry-wide |
| **Script** | 阅文 漫剧助手 | IP adaptation platform | Jiangyou (partnership) |
| **Storyboard** | LLM-powered decomposition | Script → shot breakdown | All companies |
| **Storyboard** | ComfyUI workflows | Node-based pipeline orchestration | VisionStar, Lingju |
| **Visual Gen** | Stable Diffusion (SDXL, Flux) | Image generation (base) | VisionStar, Lingju |
| **Visual Gen** | Midjourney | Image generation (concepts) | VisionStar, industry-wide |
| **Visual Gen** | 即梦 / Jimeng (Seedance 2.0) | Video generation — ByteDance | Jiangyou, Sanyuan, industry-wide |
| **Visual Gen** | 可灵 / Kling | Video generation — Kuaishou | Sanyuan, industry-wide |
| **Visual Gen** | Vidu | Video generation | VisionStar |
| **Visual Gen** | 海螺AI / MiniMax | Video generation | Industry option |
| **Consistency** | LoRA training (Kohya_ss, LiblibAI) | Character identity lock | Lingju, Jiangyou |
| **Consistency** | ControlNet (OpenPose/Canny) | Pose & composition control | Lingju, VisionStar |
| **Consistency** | IP-Adapter + FaceID | Face feature anchoring | Lingju |
| **Consistency** | InstantID / PuLID | High-fidelity face preservation | Lingju |
| **Consistency** | Fixed Seed values | Reproducibility | Lingju, Jiangyou |
| **Consistency** | StoReel proprietary system | Platform-level consistency | StoReel |
| **Audio** | ElevenLabs | Voice cloning (international) | VisionStar, Lingju, Sanyuan |
| **Audio** | Fish Audio | Voice cloning | VisionStar |
| **Audio** | 魔音工坊 | Voice cloning (domestic) | Lingju |
| **Audio** | 百宝音 | AI dubbing (domestic) | Sanyuan |
| **Audio** | 冬瓜配音 | CapCut-compatible dubbing | Sanyuan |
| **Audio** | Microsoft Azure TTS | Enterprise TTS | Lingju |
| **Audio** | Suno | AI music generation | VisionStar |
| **Editing** | 剪映 / CapCut (JianYing) | Video editing + assembly | Lingju, Jiangyou, Sanyuan |
| **Editing** | StoReel Canvas | Integrated creation tool | StoReel |
| **Pipeline** | ComfyUI | Node-based workflow orchestration | VisionStar, Lingju |
| **Pipeline** | Alibaba Cloud 百炼 | API platform for AI models | VisionStar |
| **Platform** | StoReel Canvas | One-stop creation + community | StoReel |

---

## TEAM ROLES TABLE (INDUSTRY STANDARD)

| Role (中文) | Role (English) | Function | Typical Count per Squad |
|---|---|---|---|
| **编剧** | Screenwriter / Script Engineer | Write scripts + structure AI prompts; control narrative hooks and pacing | 1 |
| **导演** | Director | Oversee visual quality, narrative coherence, shot selection | 1 |
| **抽卡师** | Gacha Artist / AI Visual Generator | Generate visuals via AI tools; select best outputs through repeated generation; tune prompts | 3–4 |
| **精修师** | Refinement Artist | Fix AI artifacts: hands, eyes, character drift, background glitches | 1–2 |
| **后期剪辑** | Post-Production Editor | Assemble clips, add transitions, subtitles, audio sync, final polish | 1–2 |
| **配音/音效** | Voice & Sound Designer | Manage AI voice generation, BGM selection, sound effects | 1 (often shared) |
| **投流运营** | Traffic/Distribution Operator | Manage platform uploads, ad buying, user acquisition, analytics | 1–2 (per portfolio) |
| **中台技术** | Platform/Pipeline Engineer | Maintain AI toolchain, model updates, workflow optimization, asset management | Shared across squads |
| **IP运营** | IP Operations Manager | Source novels, negotiate licensing, manage adaptation pipeline | 1 (per portfolio) |

### Typical Squad Sizes
| Company | Squad Size | Structure |
|---|---|---|
| **灵矩动漫** | 5–7 per squad | 3–4 抽卡师 + screenwriter + director; post-production via central platform |
| **酱油文化** | Similar squad model | Specialized 抽卡师 + refinement + editing teams at scale |
| **万像天影** | Flexible | Adapts to project scope (B2B model) |
| **StoReel** | Creator-centric | Individual creators or small teams using Canvas platform |
| **三垣映画** | Consortium model | Distributed across 3 partner organizations |

---

## INDUSTRY ECONOMICS

### Revenue & Cost Structure
| Metric | Range | Notes |
|---|---|---|
| **Per-drama production cost** | ¥50K–150K | For ~100-minute AI manga drama |
| **Per-minute production cost** | ¥100–1,500 | Mainstream quality range |
| **Top hit drama revenue** | ¥2M+ in user spending | Before platform fees |
| **Profit per hit drama** | ~¥400K | After production + traffic acquisition costs |
| **Traffic acquisition (投流)** | 80–90% of total costs | Dominant cost center has shifted from production to distribution |
| **Platform revenue share** | 90–95% to creator | During platform competition phase; may normalize lower |

### Production Economics by Tier
| Tier | Cost/Min | Cycle | Team | Output Quality |
|---|---|---|---|---|
| **Grassroots/Test** | ¥10–100 | Hours | 1–2 people | MVP quality, rapid testing |
| **Commercial Standard** | ¥100–1,000 | Days | 3–6 people | Platform-acceptable, consistent characters |
| **Premium/Head** | ¥1,000–1,500 | 1–3 weeks | 5–10 people | High production value, IP-backed |

### Key Economic Insights
1. **Production cost is no longer the bottleneck** — traffic acquisition (投流) now dominates total costs at 80–90%
2. **Portfolio strategy beats single-drama bets** — at 70–80% hit rates, companies launch 50–100 dramas/month to ensure consistent revenue
3. **IP licensing is the new moat** — access to web novel IP libraries (阅文, 飞卢) determines content pipeline depth
4. **Regulatory compliance adds cost** — the new filing system (备案) adds time and administrative overhead, favoring larger companies
5. **The "抽卡" efficiency paradox** — while AI dramatically reduces per-unit costs, the volume of generation/selection needed means labor hasn't disappeared, just transformed
6. **Platform subsidies are temporary** — current 90–95% revenue shares and content subsidies will decrease as platforms consolidate market position

### Competitive Moats (What Actually Matters)
| Moat | Description |
|---|---|
| **IP Pipeline** | Exclusive access to web novel libraries (Yuewen partnership = 400+ adaptations/year) |
| **Industrial SOP** | Codified workflows that enable consistent quality at 100+ dramas/month |
| **Hit Rate Intelligence** | Data-driven understanding of what hooks, pacing, and genres convert to revenue |
| **Character Consistency Tech** | Proprietary LoRA libraries + asset management systems |
| **Distribution Expertise** | Traffic buying optimization, platform relationship management, multi-platform syndication |
| **Regulatory Compliance** | Filing infrastructure, content review teams, audit trail documentation |

---

> **End of Batch 1 Report**
> 
> *This report covers 5 studios researched in maximum depth using Chinese-language primary sources. Data reflects industry state as of May 2026. The AI drama industry evolves rapidly — specific tool versions, pricing, and platform policies may change within months.*
