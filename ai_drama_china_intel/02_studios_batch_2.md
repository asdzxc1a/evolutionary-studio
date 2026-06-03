# AI Short Drama Studios — Batch 2 Intelligence Report
## Companies 6–10: Deep Production Pipeline Analysis

> **Research Date**: 2026-05-24
> **Sources**: 36kr, huxiu, tmtpost, Sina, Tencent, 长江日报, 极目新闻, BOSS直聘, cztv.com, wuhan.gov.cn, 163.com, and other Chinese-language authoritative sources
> **Methodology**: Chinese-keyword searches across industry media, founder interviews, job postings, government enterprise registries

---

## 6. 武汉杨涵涵文化传媒 (Yanghanhan Culture Media)

### Company Overview

| Field | Detail |
|---|---|
| **Location** | Wuhan, Qiaokou District, Hanjiangwan AI Industrial Park |
| **Founded** | ~2023 |
| **Team Size** | ~20 people (mostly 90s/00s generation) |
| **Team Composition** | AIGC producers, content planners, music/sound effects dept, business/admin |
| **CEO/Director** | 杨涵涵 (Yang Hanhan) — 90后, NOT film-school trained. BA from Xinghai Conservatory of Music (music performance), MA in Marxist Theory. Former university teacher, former deputy director of Rural Revitalization Academy. Crossed into e-commerce, then AI video in 2023 |
| **Deputy GM** | 李轲 (Li Ke) |
| **Classification** | Independent AI video studio |

### Notable Works

- **《霍去病》** (Huo Qubing) — Viral AI historical drama short film. Two versions: 4-min and 6-min. **NOT 80 episodes as rumored online**. Debunked stats: "3 people / 3,000 RMB" refers only to compute costs, not full production
- **《机械心与狗尾巴》** (Mechanical Heart & Dog Tail) — **1st Prize at Tencent Video's Inaugural AI Short Film Competition** (from 6,000+ global entries). Sci-fi/post-apocalyptic theme exploring AI and human emotions

### LAYER 1: SCRIPT (剧本)

- **AI Models**: Claude (literary quality, nuanced narrative), DeepSeek-R1 (logical structure, storyboard decomposition), 豆包 (Doubao)
- **Method**: LLMs used for plot conception, storyboard decomposition, dialogue creation
- **Key Technique**: Decompose emotions into AI-understandable detail descriptions (expressions, lighting, actions, mood)
- **Script Structure**: Director writes script + text storyboard first (human-led creative direction)
- **IP Source**: Original content — historical themes (Huo Qubing), sci-fi (Mechanical Heart)
- **Prompt Engineering**: Team developed proprietary structured prompt workflows; prompts structured as `[scene description] + [camera language] + [character action] + [lighting style]`

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)

- **Process**: Director personally completes full text storyboard before production
- **Shot Count**: 《霍去病》 contained 90+ storyboard panels with ~20 style-setting reference images
- **Approach**: Storyboarding claims 70%+ of total creative effort — meticulous breakdown into camera angles, character expressions, spatial staging
- **Platform**: Uses 360's "Nanomi Manga Pipeline" (纳米漫剧流水线) for script decomposition → intelligent storyboarding → image generation

### LAYER 3: VISUAL GENERATION (画面生成)

- **Primary Platform**: 360 纳米漫剧流水线 (Nanomi Manga Pipeline) — industrial-grade AI manga agent production platform
- **Image Generation Tools**: Midjourney, 即梦 (Jimeng/Dreamina), 通义万相
- **Video Generation**: 即梦 Seedance, 可灵 (Kling), Vidu
- **Character Consistency**: LoRA models + ControlNet for pose/appearance control; ~20 style-setting anchor images per project
- **Volume**: **~1,700 images generated** for 《霍去病》, with each image averaging **15+ revision rounds**; each video shot generated **~5 times** for quality selection
- **Quality**: First-pass storyboard approval rate raised to **90%+** through proprietary prompt structures
- **Style**: Cinematic historical aesthetic — detailed attention to war horse close-ups, metallic reflections, atmospheric lighting

### LAYER 4: AUDIO / VOICE (音频/配音)

- **TTS Tools**: AI voice synthesis (百宝音, 黑狐配音 for short-drama-optimized multi-character dialogue; ElevenLabs for cinema-grade; 海螺AI/DubbingX for emotional capture)
- **Music/SFX**: Team includes dedicated music/sound effects department; 剪映 (CapCut) built-in BGM/SFX library
- **Lip Sync**: Not explicitly confirmed; focus is on manga/animated style rather than photorealistic

### LAYER 5: EDITING / POST-PRODUCTION (后期制作)

- **Primary Tool**: 剪映 (CapCut/Jianying) — auto-subtitles, scene transitions, audio-visual assembly
- **Process**: Automated subtitle addition, clip stitching, transition effects, voiceover integration, BGM/SFX layering
- **Fine-tuning**: Manual micro-adjustments on each frame for lighting, skin tone, action details to meet "industrial-grade" standards

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)

- **Philosophy**: "AI is not one-click generation" — team explicitly rejects raw AI output
- **Review Process**: Every frame undergoes multiple prompt adjustment rounds; emphasis on light/shadow, skin tone, action coherence
- **Re-generation vs Fix**: Heavy re-generation (15x per image, 5x per video shot) rather than manual fixes
- **Core Insight**: High-quality output depends on narrative grasp, Eastern aesthetic sensibility, and professional camera language judgment — not just AI tools

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)

- **Platforms**: Tencent Video, Douyin (TikTok China), CCTV频道 (央视频)
- **Strategy**: Competition awards + social media virality → industry recognition → B2B contracts
- **Revenue Streams**: B2B production services, competition prizes, platform content distribution, industry speaking/consulting
- **Key Metric**: 《霍去病》 went viral across Chinese social media; team invited to DataEye L!nk industry conference (May 2026) to share production insights
- **Production Speed**: ~48 hours pure working time from script to final cut (for a 4-6 min short)
- **Cost**: 3,000 RMB in pure compute costs (excluding labor)

### Additional Data Points

- **Improvement Loop**: Team builds internal "workflows" with proprietary prompt structures; continuously refines for higher first-pass rates
- **Industry Speaking**: Deputy GM 李轲 presented at DataEye L!nk conference on "Telling Chinese Stories with AI"
- **Key Differentiator**: Music background of director brings unique aesthetic sensibility; cross-disciplinary approach (music → education → e-commerce → AI film)

---

## 7. 元界矩阵 (Vertex Matrix / Fiderma)

### Company Overview

| Field | Detail |
|---|---|
| **Location** | Beijing, Chaoyang District |
| **Founded** | 2021 |
| **Classification** | National High-tech Enterprise (国家高新技术企业) |
| **CEO** | 李伯男 (Li Bonan) |
| **Core Team Background** | IBM, JD.com (京东), Alibaba veterans |
| **Core Business** | AI digital transformation solutions for government & enterprise; cultural tourism digitalization; AI short drama production |
| **Key Platform** | Fiderma — AI content marketing transaction platform |

### Notable Works

- **《沈总，你的西医夫人是终极药引》** — First AI-native short drama produced entirely on Fiderma platform (launched ~May 2026). Full-pipeline AI production
- **《妈妈的秘密》** — Described as first AI full-pipeline health drama, pioneering the health/wellness vertical in AI short dramas

### LAYER 1: SCRIPT (剧本)

- **Method**: Multi-agent collaborative creation system — AI agents auto-generate scripts from concept
- **AI Models**: Proprietary MetrixAI large model engine + general LLMs (豆包, ChatGPT)
- **Key Feature**: Script optimization integrated into Fiderma platform; automated script decomposition into scene/character/action descriptions
- **IP Source**: Original content + adapted popular genres (urban revenge, sweet romance, mystery, health)

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)

- **Process**: Automated storyboard generation through Fiderma platform
- **Method**: "Shot-level production" — system decomposes scripts into individual shot descriptions with camera angles, character positioning, expressions
- **Asset Management**: Pre-built character/scene/costume/lighting asset library to ensure consistency ("visual locking" before production begins)
- **Investment**: Storyboarding consumes 70%+ of total creative effort in the AI pipeline

### LAYER 3: VISUAL GENERATION (画面生成)

- **Platform**: Fiderma integrated pipeline — auto-generates character imagery, scene design
- **Video Models**: Seedance, Vidu, Runway, Pika (platform-agnostic, integrates multiple models)
- **Character Consistency**: LoRA training + ControlNet for precise pose/appearance control; standardized character "anchor points" (clothing, physical features)
- **Quality**: Professional-grade output through iterative refinement; each shot goes through multiple generation cycles

### LAYER 4: AUDIO / VOICE (音频/配音)

- **TTS**: AI voice synthesis integrated into Fiderma platform (魔音工坊, MiniMax语音)
- **Process**: Automated character voiceover generation + BGM + environmental SFX
- **Capability**: Multi-character dialogue with emotional nuance

### LAYER 5: EDITING / POST-PRODUCTION (后期制作)

- **Integration**: Full-pipeline editing within Fiderma — from raw AI clips to finished episode
- **Features**: Auto-subtitle, auto-transition, audio-visual sync
- **Output**: "High-efficiency, high-quality, low-cost" mass production capability

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)

- **Multi-Agent QC**: Automated quality checks through AI agent pipeline
- **Human Review**: Final creative decisions and brand alignment by human team
- **Industry Benchmark**: 70-90% cost reduction vs. traditional live-action; 5-20x efficiency gain

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)

- **Platforms**: Multi-platform distribution through Fiderma marketplace
- **B2B Model**: Enterprise AI solutions — digital human IP cloning, digital human livestreaming, cultural tourism smart guides
- **Products**:
  - **元界获客宝** — Full-domain automated customer acquisition
  - **元界文旅通** — Cultural tourism digitalization
  - **伴游机器人** — Smart tourism service robots
- **Monetization**: Platform transaction fees + enterprise SaaS subscriptions + content production services

### Additional Data Points

- **Digital Human**: Offers digital human IP cloning + 24/7 digital human livestreaming (replacing expensive human livestreamers)
- **"AgriCulturalTourismCommerce" Focus**: AI-powered integration of agriculture, culture, tourism, and commerce sectors
- **Key Differentiator**: Enterprise-grade platform approach vs. individual creator tools; National High-tech Enterprise certification adds credibility

---

## 8. 抽象示界科技 (Abstract Vision Tech)

### Company Overview

| Field | Detail |
|---|---|
| **Location** | Not specified (likely Beijing/online) |
| **Founded** | ~2024 |
| **Co-Founders** | "台台" (TaiTai) + "抽象仔XEIIZO" (Chouxiangzai) |
| **Team Size** | 2-5 core members (indie team) |
| **TaiTai Background** | China Communications University (中国传媒大学) graduate → CCTV documentary director → AI short drama creator. Jimeng (即梦) "Super Creator" (超级创作者) |
| **XEIIZO Background** | AI content creator with massive following on Douyin/Bilibili; known for "abstract" aesthetic |
| **Classification** | Indie AI studio, overseas-focused |

### Notable Works

- **《五个哥哥都宠我》** (Five Brothers All Spoil Me) — AI hyper-realistic short drama, **100M+ views** on overseas platforms (Reel.ai)
- **《亿万富翁回归》** (Billionaire's Return) — AI hyper-realistic short drama, **100M+ views** on overseas platforms
- Multiple viral AI short dramas targeting overseas audiences with sweet romance, family drama, and urban revenge genres

### LAYER 1: SCRIPT (剧本)

- **AI Models**: 豆包 (Doubao), DeepSeek for script creation and storyboard decomposition
- **Method**: Deep localization for target overseas markets (US/Europe, Southeast Asia, Japan/Korea) — not simple translation but cultural adaptation
- **Key Focus**: Reverse-engineering overseas audience preferences (revenge, underdog rise, fantasy, boss romance tropes)
- **IP Source**: Original content adapted for overseas cultural context

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)

- **Process**: Leverages TaiTai's CCTV documentary directing experience for professional narrative structure and camera language
- **Method**: Script decomposition into shot-level descriptions with Seedance 2.0 integrated workflow
- **Asset Management**: Character/scene asset library with "visual locking" for multi-episode consistency
- **Efficiency Evolution**: First AI short drama took ~10 days per episode; dramatically improved with tool iterations

### LAYER 3: VISUAL GENERATION (画面生成)

- **Primary Tool**: 即梦 Seedance 2.0 (core production engine) — ByteDance's video generation model
- **Secondary Tools**: 可灵 AI (Kling) for 4K resolution and single-shot close-ups
- **Style**: "AI hyper-realistic" (仿真人) — photorealistic character generation
- **Character Consistency**: Seedance 2.0's "Omni-Reference" system + asset anchoring; solved the "character drift" problem across dozens of episodes
- **Key Feature**: Seedance 2.0's "director logic" workflow design — multi-shot narrative coherence, audio-visual sync generation

### LAYER 4: AUDIO / VOICE (音频/配音)

- **TTS**: AI text-to-speech (Speechify, CapCut built-in AI voice) — multi-language, multi-tone support
- **Localization**: Multi-language dubbing automated pipeline — audio extraction → AI translation → subtitle embedding → emotional voice dubbing → lip-sync
- **Speed**: Traditional multi-day dubbing compressed to hours

### LAYER 5: EDITING / POST-PRODUCTION (后期制作)

- **Tools**: 剪映 (CapCut/Jianying) for final assembly
- **Process**: Auto lip-sync, voiceover addition, BGM, SFX, subtitle integration
- **Integration**: Seamless pipeline from Seedance generation → CapCut post-production

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)

- **Controlled Generation**: Seedance 2.0 moves from "gacha/lottery" randomness to "controllable directing mode" via reference images/video
- **TaiTai's Edge**: Professional directing background (CCTV) brings film-quality narrative sensibility
- **Iteration**: Rapid AB testing of generated content against audience engagement metrics

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)

- **Primary Platform**: Reel.ai (overseas AI short drama app)
- **Secondary**: TikTok, YouTube for overseas distribution
- **Domestic**: Douyin (抖音), Bilibili (B站) for domestic presence
- **Monetization Model**: Platform revenue sharing from overseas short drama apps; production contracts
- **Cost Advantage**: AI production cost ~1/3 of traditional live-action short dramas
- **Performance**: Multiple titles achieving **100M+ overseas views**
- **AB Testing**: Automated generation of thousands of ad creatives for platform-specific testing; real-time ROI-driven content iteration

### Additional Data Points

- **"Super Creator" Status**: TaiTai holds Jimeng AI's highest creator tier, receiving priority access, traffic, commercial partnerships
- **Efficiency Trajectory**: First drama ~10 days/episode → current speed dramatically faster (specific current number not disclosed)
- **Key Differentiator**: Professional CCTV directing experience + Jimeng/Seedance ecosystem deep integration + overseas-first strategy
- **Production Philosophy**: "AI makes the quantity, directors make the quality" — CCTV narrative training is the irreplaceable moat

---

## 9. 杭州原神文化传媒 (Yuanshen Culture Media)

### Company Overview

| Field | Detail |
|---|---|
| **Location** | Hangzhou, Yuhang District, Liangzhu Street |
| **Founded** | September 15, 2023 |
| **Legal Representative** | 魏天 (Wei Tian) |
| **Registered Capital** | 1,000,000 RMB |
| **CEO** | 卢心舸 (Lu Xinge) — former senior concept artist with 5+ years original art experience, transitioned to AI short drama directing |
| **Team Size** | ~20 people |
| **Monthly Output** | ~5 premium AI short dramas per month |
| **Business Scope** | AI application software development, AI industry system integration, film production, creative arts, internet livestream tech services |

> **Note**: Despite the name "原神", this company has NO relation to miHoYo or the game *Genshin Impact*

### Notable Works

- AI short dramas using "AI Content Factory" model
- Focus on manga-style AI drama production (漫剧)

### LAYER 1: SCRIPT (剧本)

- **Method**: AI-assisted script generation with human creative direction
- **Model Usage**: 360 Nanomi AI agents for script decomposition and intelligent storyboarding
- **Key Process**: Lu Xinge serves as "AI Director" — the chief creative orchestrator of the full pipeline
- **IP Source**: Adapted web novels + original content

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)

- **Core Role**: AI storyboarding (AI分镜) identified as the most critical and challenging step — requires outstanding text comprehension and aesthetic judgment
- **Process**: "Script reading" (围读) → AI storyboard generation → dynamic generation → post-production editing
- **Platform**: 360 Nanomi AI agents used for intelligent storyboard generation
- **Time Investment**: Storyboarding dominates creative effort

### LAYER 3: VISUAL GENERATION (画面生成)

- **AI Agent System**: Uses 360 Nanomi AI agents (纳米AI智能体) — industrial-grade manga production platform
- **Integration**: Multi-agent system where master agent receives requirements and dispatches sub-agents for script, storyboarding, asset generation, editing
- **Style**: Manga/anime aesthetic (漫剧 style)
- **Character Consistency**: Asset library with locked visual definitions; "visual anchoring" for multi-episode consistency

### LAYER 4: AUDIO / VOICE (音频/配音)

- **Method**: AI voice synthesis integrated into production pipeline
- **Music/SFX**: AI-generated background music and sound effects

### LAYER 5: EDITING / POST-PRODUCTION (后期制作)

- **Process**: Automated assembly through AI agent pipeline
- **Integration**: Full-pipeline from script to finished episode within agent workflow

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)

- **AI Director Role**: Lu Xinge as "总指挥" (chief commander) oversees full-pipeline quality
- **Review**: Human aesthetic judgment on AI output; final creative sign-off by director

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)

- **Platforms**: Chinese short drama platforms, short video platforms
- **Model**: Content distribution + production services

### Additional Data Points

- **Production Speed Revolution**: Cut from **4 months (10+ person team)** → **21 days (4-5 person team)** for 60-80 episode anime short dramas
- **CEO Background**: Lu Xinge's 5+ years as concept artist provides deep understanding of visual quality standards
- **"AI Director" as New Profession**: Company exemplifies the emergence of "AI Director" and "AI Storyboard Artist" as formal job roles
- **Key Differentiator**: "AI Content Factory" model — systematic, repeatable production with agent-based automation; concept artist background ensures visual quality
- **Industry Positioning**: Training ground for new "tech + hands-on" composite talent model

---

## 10. 灵境万维 (Lingjing AI / Lingjing Wanwei)

### Company Overview

| Field | Detail |
|---|---|
| **Location** | Hangzhou (HQ) + Wuhan Optics Valley (Central China HQ) |
| **Founded** | August 2023 |
| **Founders** | 许金城 (Xu Jincheng, CEO) + 许文良 (Xu Wenliang, COO/Partner) — brothers |
| **Core Team Background** | Alibaba and other top internet company alumni |
| **Team Size** | **100-499 people** (grew from 5 to 100+ in under 6 months) |
| **Team Demographics** | Average born after 1995 (95后) |
| **Classification** | AI manga drama industrialization platform |
| **Platform** | lingjingai.cn |

### Funding History

| Round | Date | Amount | Investors |
|---|---|---|---|
| Seed | Aug 2024 | Several million RMB | 中科招商 (CSCI) |
| Angel | Jul 2025 | Tens of millions RMB | 柏睿资本, 零以创投 |
| Angel+ | Sep/Oct 2025 | Tens of millions RMB | 国科投资 (lead), 柏睿资本 (follow-on) |

### Notable Works

- **《我在末世开超市》** (I Run a Supermarket in the Apocalypse) — **3 BILLION views in 5 days, 12 MILLION RMB revenue** — industry phenomenon
- Orders booked through **2027**, cumulative order value **exceeding 100 million RMB (亿元)**
- Monthly production capacity: hundreds to potentially thousands of manga dramas

### LAYER 1: SCRIPT (剧本)

- **Big Data Selection**: Proprietary web novel data analytics platform — monitors **millions of works daily** across the entire web using NLP and trend prediction models
- **AI Scriptwriting**: AI auto-generates novel and script drafts based on hot-topic data; professional human editors optimize for "hit potential"
- **Data Signals**: Click-through rates, retention, trending topics, genre heat maps (face-slapping, power fantasy, sweet romance, villain punishment)
- **IP Source**: Primarily adapted from web novels (网文) identified via big data; AI-generated original content

### LAYER 2: STORYBOARD / SHOT PLANNING (分镜)

- **"Storyboard Brain"**: AI automatically decomposes text scripts into cinematic-grade storyboard scripts
- **Emotion-Matched Camera Language**: AI auto-matches camera movements (运镜), shot scales (景别) to script emotional beats
- **Character Sheets**: System generates standardized **three-view character sheets** (正面/侧面/背面) before production begins
- **Scene Design**: Multi-angle environment panoramas generated for each scene setting

### LAYER 3: VISUAL GENERATION (画面生成)

- **Self-Built Pipeline**: Proprietary multi-modal anime production pipeline (多模态动漫管线)
- **Dual-Core Engine**: "Neural Rendering + Cognitive Computing" (神经渲染+认知计算)
- **Tools**: ComfyUI (core workflow management) + LoRA models + ControlNet (Depth, Canny) for character locking
- **Video Generation**: 可灵 AI (Kling) for image-to-video dynamic generation with motion brushes, start/end frame control, video extension
- **3D Digital Studio**: Spatial graph technology (空间图谱) for constructing 3D digital sets — ensures physical laws (light source, positioning) remain consistent
- **Character Consistency**: Three-view character sheets + visual asset library = "digital actors" with locked appearance across hundreds/thousands of shots
- **Production Mode**: AI handles 80% automatically; humans do ~20% fine-tuning ("watering and fertilizing")
- **Efficiency**: **10x+ faster than traditional anime production; costs reduced to ~1/20th (95%+ reduction)**

### LAYER 4: AUDIO / VOICE (音频/配音)

- **Automated Audio Pipeline**: System auto-handles dubbing, **lip-sync** (对口型), sound effects, and background music
- **Platform Feature**: Lip-sync is a core advertised feature of the Lingjing AI platform
- **Process**: Fully integrated into production pipeline — no separate audio production step

### LAYER 5: EDITING / POST-PRODUCTION (后期制作)

- **Auto-Assembly**: System automatically assembles generated clips according to script timeline
- **"Hot Update" Mechanism**: If character appearance needs changing post-production (e.g., costume swap), only the asset library entry needs updating — system **auto-propagates changes across all timeline segments** without starting over
- **Tools**: 剪映 + professional editing (Premiere/After Effects) for final polish

### LAYER 6: QUALITY CONTROL / ITERATION (质控/迭代)

- **Human Roles Redefined**:
  - **Decision Maker**: Decides what content to produce (data-driven)
  - **Trainer**: Feeds AI agents quality assets and parameter adjustments
  - **QC Inspector**: Final 20% fine-tuning and quality control
- **Anti-Collapse**: Three-view character sheets + spatial graph = prevent "axis jumping" (跳轴) and visual "collapse" (崩坏)
- **Scale**: Industrial QC across hundreds-to-thousands of episodes monthly

### LAYER 7: DISTRIBUTION / MONETIZATION (分发/变现)

- **Domestic Platforms**: UC, Zhihu, Yuewen (阅文) and other content platforms
- **Overseas Platforms**: Webnovel, Dreame — global distribution through "cultural adaptation system"
- **Revenue Model**:
  - IP copyright licensing & revenue sharing (content splits with platforms)
  - B2B AI technology solutions (enterprise API access for IP incubation)
  - Creator ecosystem & platform tool subscriptions
- **Performance**: 《我在末世开超市》 = 3B views / 12M RMB revenue in 5 days
- **Order Pipeline**: Booked through 2027, cumulative orders >100M RMB
- **Vision**: "AI Anime DreamWorks" (AI动漫梦工厂) — global-scale content factory

### Additional Data Points

- **"One-Sentence Generation"**: System can take a single sentence and produce a full script + video through multi-agent pipeline
- **Proprietary Platform (lingjingai.cn)**: Offers public-facing tools — AI scriptwriting, novel-to-script conversion, manga creation, live-action creation, free canvas, image/video generation, lip-sync
- **Big Data Moat**: Real-time monitoring of millions of web novels across all platforms; NLP-powered trend prediction for genre selection
- **Hot Update Innovation**: Unique ability to change character attributes post-production with automatic propagation — massive efficiency gain for serialized content
- **Key Differentiator**: Only company in batch with venture funding, 100+ team, industrial-scale operations, and orders exceeding 100M RMB

---

## Comparative Analysis

### Company Comparison Table

| Dimension | 6. 杨涵涵文化传媒 | 7. 元界矩阵 / Fiderma | 8. 抽象示界科技 | 9. 原神文化传媒 | 10. 灵境万维 |
|---|---|---|---|---|---|
| **Location** | Wuhan | Beijing | Undisclosed | Hangzhou | Hangzhou + Wuhan |
| **Team Size** | ~20 | Mid-size (enterprise) | 2-5 core | ~20 | 100-499 |
| **Founding** | ~2023 | 2021 | ~2024 | Sep 2023 | Aug 2023 |
| **Funding** | Self-funded | Self-funded (enterprise) | Self-funded | Self-funded | Multi-round VC (>100M RMB orders) |
| **Founder Background** | Music + education | IBM/JD/Alibaba tech | CCTV documentary | Concept art (5yr) | Alibaba alumni |
| **Primary AI Platform** | 360 Nanomi Pipeline | Fiderma (self-built) | Jimeng Seedance 2.0 | 360 Nanomi Agents | Self-built multi-modal pipeline |
| **Visual Style** | Cinematic historical | Enterprise content | Photorealistic (仿真人) | Manga/anime | Manga/anime |
| **Key Video Models** | Seedance, Kling, Vidu | Seedance, Vidu, Runway | Seedance 2.0, Kling | Via 360 Nanomi agents | Kling + ComfyUI + custom |
| **Scriptwriting AI** | Claude, DeepSeek, Doubao | MetrixAI engine | Doubao, DeepSeek | 360 Nanomi agents | Big data + AI auto-generation |
| **Character Consistency** | LoRA + 20 anchor images | LoRA + ControlNet | Seedance Omni-Reference | Agent asset library | Three-view sheets + spatial graph |
| **Production Speed** | 48hr for 4-6min short | "Daily multi-episode" | First: 10d/ep → faster now | 4mo→21 days (60-80 eps) | Monthly: hundreds of dramas |
| **Cost Structure** | 3,000 RMB compute + labor | 70-90% reduction claimed | ~1/3 of traditional | Not disclosed | 1/20th of traditional (~95% cut) |
| **Primary Market** | Domestic (CN platforms) | Enterprise B2B | Overseas (Reel.ai) | Domestic CN | Domestic + Overseas |
| **Monetization** | Awards + B2B services | Enterprise SaaS + digital human | Overseas platform rev-share | Production services | IP licensing + B2B API + platform |
| **Breakout Metric** | Tencent AI Competition 1st Prize | National High-tech Enterprise | 100M+ overseas views per title | 4mo→21d speed gain | 3B views / 12M RMB in 5 days |

### Production Pipeline Comparison

| Pipeline Layer | 6. 杨涵涵 | 7. 元界矩阵 | 8. 抽象示界 | 9. 原神文化 | 10. 灵境万维 |
|---|---|---|---|---|---|
| **L1: Script** | Claude + DeepSeek (human-led) | Multi-agent auto (MetrixAI) | Doubao + DeepSeek (localized) | 360 Nanomi agents | Big data → AI draft → human polish |
| **L2: Storyboard** | Manual by director (90+ panels) | Auto via Fiderma | Seedance 2.0 workflow | AI storyboard (core step) | "Storyboard Brain" auto-decompose |
| **L3: Visual Gen** | 360 Nanomi + MJ + Jimeng | Fiderma integrated | Seedance 2.0 + Kling | 360 Nanomi agents | Self-built pipeline + ComfyUI + Kling |
| **L4: Audio** | Dedicated audio team + AI TTS | AI TTS (魔音工坊, MiniMax) | AI TTS (Speechify, CapCut) | AI voice in pipeline | Auto dubbing + lip-sync |
| **L5: Editing** | 剪映 (CapCut) | Fiderma integrated | 剪映 (CapCut) | Agent pipeline | Auto-assembly + "hot update" |
| **L6: QC** | 15x/image, 5x/video regen | Multi-agent QC | Seedance controlled + AB test | AI Director review | 80% AI / 20% human fine-tune |
| **L7: Distribution** | Tencent, Douyin, CCTV频道 | Enterprise B2B multi-platform | Reel.ai, TikTok, YouTube | CN drama platforms | UC, Zhihu, Webnovel, Dreame |

### Strategic Positioning Map

```
                    OVERSEAS ←————————————→ DOMESTIC
                         |                    |
    INDIE/              8. 抽象示界           6. 杨涵涵
    CREATOR             (Reel.ai focus)       (Award-winning
    DRIVEN              (Seedance native)      auteur model)
                         |                    |
                         |                    |
                         |         9. 原神文化
                         |         (AI Content Factory)
                         |         (concept art → AI director)
                         |                    |
    PLATFORM/            |                    |
    INDUSTRIAL           |          7. 元界矩阵
                         |          (Enterprise SaaS)
                         |          (B2B digital solutions)
                         |                    |
                         |         10. 灵境万维
                         |         (Industrial-scale factory)
                         |         (VC-funded, 100+ team)
                         |         (3B views, orders to 2027)
```

### Key Insights

1. **Scale Spectrum**: From 2-person indie (抽象示界) to 100-500 person factory (灵境万维) — AI enables both extremes
2. **Platform Dependency**: 360 Nanomi Pipeline powers 2 of 5 companies; Seedance/Jimeng powers the overseas play
3. **Background Matters More Than AI**: The CCTV director (TaiTai), concept artist (Lu Xinge), and music graduate (Yang Hanhan) all leverage non-tech backgrounds as creative moats
4. **Overseas vs Domestic Split**: 抽象示界 is the only overseas-first player; 灵境万维 is building dual-track; others are domestic-focused
5. **Cost Revolution Confirmed**: Across all 5 companies, cost reductions of 70-95% vs. traditional production are consistently reported
6. **"Hot Update" as Innovation**: 灵境万维's ability to change character attributes post-production with automatic propagation is a genuine workflow innovation not seen in others
7. **Big Data as Moat**: 灵境万维's real-time web novel monitoring + NLP trend prediction creates a defensible content selection advantage
8. **Human Role Evolution**: Across all companies, the human role shifts from "maker" to "director/curator/QC inspector" — the 80/20 AI-human split is the emerging standard
