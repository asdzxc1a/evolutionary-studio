# AI Animation Production System — Foundation Research

> **Research Goal**: Build a foundation for an AI system that analyzes blockbuster animated films (e.g., *Zootopia 2*), extracts their creative DNA (script, interviews, scene-by-scene breakdown), and generates entirely new animated stories with the same cinematic quality.
> 
> **Research Date**: May 31, 2026
> **Scope**: China-focused open-source projects + global tools for video generation, animation pipelines, movie analysis, script extraction, and agentic production systems.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Vision](#2-system-architecture-vision)
3. [Layer 1: Video Generation Engines (China + Global)](#3-layer-1-video-generation-engines)
4. [Layer 2: Animation-Specific Open Models](#4-layer-2-animation-specific-open-models)
5. [Layer 3: Movie Analysis & Scene Breakdown](#5-layer-3-movie-analysis--scene-breakdown)
6. [Layer 4: Script Extraction & Story Analysis](#6-layer-4-script-extraction--story-analysis)
7. [Layer 5: Agentic Production Pipelines](#7-layer-5-agentic-production-pipelines)
8. [Layer 6: ComfyUI Workflows & Chinese Community](#8-layer-6-comfyui-workflows--chinese-community)
9. [Layer 7: Chinese AI Animation Studios (Existing Research)](#9-layer-7-chinese-ai-animation-studios)
10. [Recommended Build Architecture](#10-recommended-build-architecture)
11. [Immediate Next Steps](#11-immediate-next-steps)

---

## 1. Executive Summary

This research identifies **47+ open-source repositories, 12 production pipelines, and 6 categories of tools** that can serve as the foundation for your AI animation production system. The ecosystem is mature enough to build a working prototype today.

**Key Finding**: The most advanced approach is not a single model — it is a **multi-agent pipeline** that combines:
- **Video understanding agents** (to deconstruct reference films)
- **Script/scene analysis agents** (to extract story structure)
- **Animation generation models** (to produce new content)
- **Production orchestration agents** (to assemble the final film)

China is uniquely positioned in this space: Bilibili open-sourced **AniSora** (the world's best open-source anime video model), Alibaba open-sourced **Wan 2.2** (a cinematic MoE video model with character animation), and Chinese ComfyUI communities have built thousands of animation workflows.

---

## 2. System Architecture Vision

Your target system needs **7 subsystems**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI ANIMATION PRODUCTION SYSTEM                        │
├─────────────────────────────────────────────────────────────────────────┤
│  INPUT: Reference Film (e.g., Zootopia 2)                               │
│                    ↓                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  SUBSYSTEM 1    │  │  SUBSYSTEM 2    │  │  SUBSYSTEM 3    │         │
│  │  Video Analyzer │  │  Script Finder  │  │  Interview      │         │
│  │  (Scene/Shot/   │  │  & Parser       │  │  Aggregator     │         │
│  │  Motion/Style)  │  │  (FDX/PDF/TXT)  │  │  (YouTube/Web)  │         │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘         │
│           ↓                    ↓                    ↓                  │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │              SUBSYSTEM 4: CREATIVE DNA EXTRACTOR             │      │
│  │  • Story structure (3-act, hero's journey, Save the Cat)     │      │
│  │  • Character archetypes & emotional beats                   │      │
│  │  • Visual style guide (color, lighting, composition)        │      │
│  │  • Pacing & rhythm analysis                                  │      │
│  │  • "Secret sauce" — what makes it popular                    │      │
│  └──────────────────────────┬──────────────────────────────────┘      │
│                             ↓                                          │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │              SUBSYSTEM 5: NEW STORY GENERATOR                │      │
│  │  • Same DNA, different environment/characters/plot           │      │
│  │  • Scene-by-scene script with visual descriptions            │      │
│  └──────────────────────────┬──────────────────────────────────┘      │
│                             ↓                                          │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │              SUBSYSTEM 6: ANIMATION PIPELINE                 │      │
│  │  • Character design → Consistent generation (LoRA/IPAdapter) │      │
│  │  • Storyboard → Keyframes → Video clips (I2V / T2V)         │      │
│  │  • Lip-sync, SFX, music, voice (native audio generation)    │      │
│  └──────────────────────────┬──────────────────────────────────┘      │
│                             ↓                                          │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │              SUBSYSTEM 7: POST-PRODUCTION & EDIT             │      │
│  │  • Scene assembly, transitions, color grading               │      │
│  │  • Final render with cinematic quality                      │      │
│  └─────────────────────────────────────────────────────────────┘      │
│                                                                         │
│  OUTPUT: Complete animated film in new setting with proven DNA          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1: Video Generation Engines

### 3.1 Chinese Closed-Source APIs (Best Quality)

| Model | Company | Open Source? | Key Strength | Access |
|-------|---------|-------------|--------------|--------|
| **Seedance 2.0** | ByteDance | ❌ No | Native audio + lip-sync, multi-shot directing, 2K, character consistency | API via Jimeng/Dreamina |
| **Kling 3.0** | Kuaishou | ❌ No | Cinematic motion realism, physics | API |
| **Wan 2.6** | Alibaba | ⚠️ Weights only | Multi-shot 1080p, native audio, video roleplay | HuggingFace / Alibaba Cloud |
| **Hailuo 2.3** | MiniMax | ❌ No | Dynamic motion, emotional animation | API |
| **PixVerse V6** | AIsphere (Beijing) | ❌ No | 100M+ users, VFX, multi-shot audio-visual | pixverse.ai |
| **Vidu** | Tsinghua/ShengShu | ❌ No | 1080p short clips | API |

### 3.2 Fully Open-Source Chinese Video Models (Weights + Code)

| Model | Repo | Params | Best For | VRAM |
|-------|------|--------|----------|------|
| **Wan 2.2** | [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) | 14B MoE | Cinematic T2V/I2V, 720P@24fps, character animation/replacement | 24GB |
| **Wan 2.1** | [Wan-Video/Wan2.1](https://github.com/Wan-Video/Wan2.1) | 14B | SOTA open T2V, I2V, editing, T2I, V2A | 8GB+ (1.3B variant) |
| **HunyuanVideo** | Tencent | 13B+ | Strong motion, I2V, Avatar, Foley variants | Consumer GPU (v1.5 = 8.3B) |
| **CogVideoX** | Zhipu AI / Z.AI | 5B | 10s videos, commercial product "Ying" | Consumer GPU |
| **SkyReels** | SkyworkAI | V1-V3 | Human-centric video, infinite-length V2 | ComfyUI compatible |

### 3.3 Global Open-Source Video Models

| Model | Repo | Notes |
|-------|------|-------|
| **LTX-Video / LTX-2** | Lightricks | Real-time DiT-based, 4K@50fps + native audio |
| **MAGI-1** | Sand AI | 24B autoregressive, chunk-by-chunk generation, outperforms Wan 2.1 |
| **Step-Video-T2V** | StepFun | 300B params, up to 204 frames, bilingual EN/ZH |
| **Open-Sora** | Open-source reproduction | 2s–15s at 144p–720p, T2V/I2V/V2V |
| **Pyramid Flow** | Open-source | Up to 10s at 768p, efficient autoregressive |

---

## 4. Layer 2: Animation-Specific Open Models

### 4.1 Bilibili AniSora (The Crown Jewel for Animation)

> **GitHub**: [bilibili/Index-anisora](https://github.com/bilibili/Index-anisora)  
> **Paper**: IJCAI 2025 accepted  
> **License**: Apache 2.0 (V2+)  
> **ComfyUI**: [Yuan-ManX/ComfyUI-AniSora](https://github.com/Yuan-ManX/ComfyUI-AniSora)

**What it does**: The most powerful open-source **animated video generation model** specifically designed for anime/animation (not natural video). Trained on 10M+ high-quality animation frames.

**Capabilities**:
- Image-to-video with spatiotemporal masks
- Frame interpolation for smooth animation
- Localized image-guided animation (paint-over regions)
- Character 3D video generation (360° rotation from front-facing illustration)
- Arbitrary-frame inference (first + mid + last frame → full video)
- Video style transfer (any style via line art + first/last frames)
- Multimodal guidance (pose, depth, line art, audio)
- Ultra-Low-Res Super-Resolution (90p → 720p/1080p)

**Versions**:
- V3.2 (latest): Trained on Wan2.2, 8 inference steps, arbitrary-frame inference
- V3.1: 12GB VRAM version, enhanced motion range
- V3: Apache 2.0, 5 sec 360p in 8 sec generation

**Why this matters for you**: This is the ONLY open-source model specifically built for animation (not live-action). If you want Zootopia-quality character animation, this is your starting point.

### 4.2 Wan Animate (Character Animation & Replacement)

> **GitHub**: [wan-animate/wananimate](https://github.com/wan-animate/wananimate)  
> **Docs**: [wananimate.top](https://wananimate.top)

**Capabilities**:
- **Animation mode**: Static character image + reference video motion → animated character
- **Replacement mode**: Swap character in existing video while preserving lighting/background
- Facial expression transfer + body motion replication
- Environmental matching (auto-relighting)
- 720P @ 24fps output

### 4.3 Face Animation & Lip Sync (Chinese + Global)

| Tool | Repo | Function |
|------|------|----------|
| **AniPortrait** | Tencent | Audio/video-driven portrait animation |
| **MusePose** | Tencent | Pose-driven character animation |
| **EchoMimic** | Alibaba | Audio-driven portrait animation |
| **LivePortrait** | Community | Expression transfer, lip sync |
| **FollowYourEmoji** | [mayuelala/FollowYourEmoji](https://github.com/mayuelala/FollowYourEmoji) | Fine-controllable portrait animation (SIGGRAPH Asia 2024) |
| **FantasyTalking** | [Fantasy-AMAP/fantasy-talking](https://github.com/Fantasy-AMAP/fantasy-talking) | Audio-driven character video |
| **Wav2Lip** | Open-source | Lip-sync for any face |

### 4.4 3D Character Reconstruction (For Consistent Characters)

| Tool | Repo | Function |
|------|------|----------|
| **IDOL** | [yiyuzhuang/IDOL](https://github.com/yiyuzhuang/IDOL) | Instant photorealistic 3D human from single image (CVPR 2025) |
| **LHM** | [aigc3d/LHM](https://github.com/aigc3d/LHM) | 3D human animation, 8GB VRAM, ComfyUI nodes |
| **HuMo** | [Phantom-video/HuMo](https://github.com/Phantom-video/HuMo) | Controllable identity transfer for video generation |

---

## 5. Layer 3: Movie Analysis & Scene Breakdown

### 5.1 Reference Video Analysis (Your "Zootopia Deconstructor")

| Tool | Repo | What It Does |
|------|------|-------------|
| **OpenMontage** | [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | **THE most advanced agentic video production system**. Analyzes reference videos (transcript, pacing, scenes, keyframes, style) and turns them into grounded production plans. 12 pipelines, 52 tools, 500+ agent skills. |
| **Video Expert Analyzer** | [ALBEDO-TABAI/video-expert-analyzer](https://github.com/ALBEDO-TABAI/video-expert-analyzer) | Chinese/English bilingual video analysis based on Walter Murch's Six Rules of Editing. AI vision scoring (Gemini/Kimi/Claude), scene detection, subtitle extraction, 5D scoring (Aesthetic/Credibility/Impact/Memorability/Fun). |
| **VideoHighlighter** | [Aseiel/VideoHighlighter](https://github.com/Aseiel/VideoHighlighter) | Open-source local AI video analyzer (Ollama). Scene detection, motion detection, object/action detection, audio peaks, transcript via Whisper. |
| **Film Breakdown Assistant** | [ggvfx/film-breakdown-assistant](https://github.com/ggvfx/film-breakdown-assistant) | Multi-agent pipeline for script breakdown: 7-pass agentic pipeline (Harvester + Continuity Agent + Review Flag Agent). Local processing via Ollama. |
| **VideoClaw** | [HITsz-TMG/VideoClaw](https://github.com/HITsz-TMG/VideoClaw) | "AI全自动化视频生成员工" — Chinese automated video generation coworker. Chat an idea, get a film. Includes 文学短视频, 动作迁移, 数字人口播 pipelines. |

### 5.2 Scene Detection Libraries (Building Blocks)

| Library | Language | Function |
|---------|----------|----------|
| **PySceneDetect** | Python | Adaptive scene/shot detection (used by OpenMontage, Video Expert Analyzer) |
| **TransNetV2** | Python | Shot detection via deep learning |
| **scenedetect (ContentDetector)** | Python | HSV-based fast cut detection |

### 5.3 Video Captioning & Understanding

| Tool | Repo | Function |
|------|------|----------|
| **LLM-Timestamps-Video-Analyzer** | [Nizier193/LLM-Timestamps-Video-Analyzer](https://github.com/Nizier193/LLM-Timestamps-Video-Analyzer) | GPT-4V analyzes video frames + subtitle extraction → scene descriptions |
| **TranscriptAI** | [ErikBahena/transcript-ai](https://github.com/ErikBahena/transcript-ai) | Topic segmentation for VTT transcripts via local LLMs (Ollama) + DeepTiling |
| **Gemini MCP** | [Tommertom/gemini-mcp](https://github.com/Tommertom/gemini-mcp) | Media analysis via Gemini: scene breakdown, cinematography analysis, composition scoring |

---

## 6. Layer 4: Script Extraction & Story Analysis

### 6.1 Subtitle/Script Extraction Tools

| Tool | Repo | Languages | Features |
|------|------|-----------|----------|
| **Video Subtitle Extractor** | [YaoFANGUK/video-subtitle-extractor](https://github.com/YaoFANGUK/video-subtitle-extractor) | 87 languages | Hardcoded subtitle extraction via OCR. GPU accelerated. Batch processing. No API needed. |
| **biliSub** | [lvusyy/biliSub](https://github.com/lvusyy/biliSub) | Chinese/English | Bilibili subtitle downloader + Whisper ASR fallback |
| **Hardcoded-Subtitle-Extraction** | [HuuHuy227/Hardcoded-Subtitle-Extraction](https://github.com/HuuHuy227/Hardcoded-Subtitle-Extraction) | EN/CN/JP/KR/AR | Desktop app + web UI. PaddleOCR backend. GPU accelerated. |
| **YouTube Transcript API** | Various | Many | Extract official subtitles from YouTube |

### 6.2 Script Analysis & Story Structure

| Tool | Repo | Function |
|------|------|----------|
| **Claude Screenplay Plugin** | [aslanSuleimenov/claude-screenplay-plugin](https://github.com/aslanSuleimenov/claude-screenplay-plugin) | 14 specialized agents in 6 phases: foundation → macro → continuity → characters → craft → synthesis. Full screenplay audit. |
| **How-to-Make-Script** | [Roundwhitefishdrop407/how-to-make-script](https://github.com/Roundwhitefishdrop407/how-to-make-script) | Multi-agent AI pipeline: one line of text → finished short-form drama with script, storyboards, character-consistent video. |
| **NoverWriter** | GitHub Topic | Novel writing app with built-in AI analysis tools and side-panel AI agent |
| **Screenplay Analysis Tools** | Various | Save the Cat beat sheets, 3-act structure analyzers, Hero's Journey mappers |

### 6.3 Script Breakdown for Production

| Tool | Type | Function |
|------|------|----------|
| **Dramatify AI Script Breakdown** | Commercial | Creates fully tagged production-ready breakdown from any screenplay. Cast, props, wardrobe, vehicles, stunts, locations, VFX. |
| **Studiovity** | Commercial | AI auto-tags cast, props, locations, wardrobe. Mobile app. Used by Netflix, Disney+, HBO. |
| **Filmustage** | Commercial | Complete script breakdown, shooting schedules, DOOD reports, automatic film budget. |
| **OpenMontage Transcriber** | Open-source | WhisperX speech-to-text with word-level timestamps |

---

## 7. Layer 5: Agentic Production Pipelines

### 7.1 OpenMontage (The Production Operating System)

> **GitHub**: [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)

**Architecture**: Agent-first. Your AI coding assistant IS the orchestrator. Python provides tools and persistence. All creative decisions live in readable YAML manifests + Markdown skills.

**12 Production Pipelines**:
1. Animated Explainer
2. Animation (anime/Ghibli style via FLUX + Remotion)
3. Avatar Spokesperson
4. Cinematic (trailers, teasers)
5. Clip Factory (batch short-form clips)
6. Documentary Montage
7. Hybrid (source + AI visuals)
8. Localization & Dub
9. Podcast Repurpose
10. Screen Demo
11. Talking Head
12. Reference-Driven (paste a video → get a production plan)

**52 Production Tools**:
- Video: 13 video gen tools + compose, stitch, trim
- Audio: 4 TTS providers + Suno/ElevenLabs music + mixing
- Graphics: 9 image gen tools + diagrams
- Enhancement: Upscale (Real-ESRGAN), bg remove, face enhance
- Analysis: Transcription (WhisperX), scene detect, frame sampling, video understand (CLIP/BLIP-2)
- Avatar: SadTalker / MuseTalk talking head, Wav2Lip lip sync

**Why this matters**: This is the closest existing system to what you want. It already does reference video analysis → production plan → script → assets → render. You would extend it with animation-specific tools and story-DNA extraction.

### 7.2 GuarDVark (Self-Hosted AI Workstation)

> **GitHub**: [guaardvark/guaardvark](https://github.com/guaardvark/guaardvark)

**Film Crew Feature**: Five specialized agents collaborate:
| Role | Function |
|------|----------|
| Screenwriter | Generates script + scene breakdown from logline |
| Casting | Assigns characters to LoRAs or stock characters |
| Cinematographer | Shot list with camera moves, framing, lens choices |
| Storyboard | Generates keyframe images for every shot |
| Editor | Assembles clips into finished video |

**Plus**: LoRA Trainer plugin for character/environment/prop training (~46MB per LoRA).

### 7.3 Koda (Agentic Video Ad Platform)

> **GitHub**: [realaman90/koda](https://github.com/realaman90/koda)

**Animation Plugin**: Multi-phase AI pipeline:
1. Enhance Prompt (Gemini Pro rewrites → detailed spec)
2. Generate Plan (Scene breakdown → user approval gate)
3. Execute (Create sandbox → generate code → render)
4. Deliver (Video URL + snapshot)

### 7.4 Cinemanga (Script → Comic → Animation)

> **GitHub**: [joewhaley/cinemanga](https://github.com/joewhaley/cinemanga)

- Script-to-Comic via FAL AI nano-banana
- Synchronized audio (music, SFX, voice-over via ElevenLabs)
- Intelligent script understanding + scene breakdown (Google Gemini)
- Video analysis + scene extraction (FAL AI video understanding)
- Panel animation (smooth transitions between states)

---

## 8. Layer 6: ComfyUI Workflows & Chinese Community

### 8.1 Why ComfyUI Is the Foundation

ComfyUI is the **standard workflow platform** for Chinese AI animation creators. It exposes every component of diffusion models as nodes, enabling:
- Frame-by-frame animation with seed control
- ControlNet (OpenPose, Canny, Depth) for consistent character motion
- IP-Adapter for character consistency across frames
- AnimateDiff for motion modules
- WanVideoWrapper for video generation

### 8.2 Key ComfyUI Repositories (Chinese Community)

| Repo | Author | Contents |
|------|--------|----------|
| **ComfyUI Workflows ZHO** | [ZHO-ZHO-ZHO](https://github.com/ZHO-ZHO-ZHO) | 22 categories, 54 workflows. ArtGallery, Portrait Master, Qwen-2, Gemini, QWen-VL. |
| **ComfyUI-- (Everything)** | [xiaowuzicode](https://github.com/xiaowuzicode/ComfyUI--) | AIGC前沿技术合集. InstantID, PuLID, IP-Adapter, SUPIR, AniPortrait, MusePose, etc. |
| **ComfyUI-WanVideoWrapper** | [kijai](https://github.com/kijai/ComfyUI-WanVideoWrapper) | Professional Wan video generation in ComfyUI. Supports SkyReels, ReCamMaster, VACE, Phantom, ATI, FantasyTalking, etc. |
| **ComfyUI-AnimateDiff-Evolved** | [Kosinkadink](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved) | Improved AnimateDiff with advanced sampling, context windows, CameraCtrl, PIA. |
| **ComfyUi-Ares-Workflows** | [AresWei](https://github.com/AresWei/ComfyUi-Ares-Workflows) | Animation & digital human resources. EchoMimic, etc. |
| **awesome-ai-painting** | [hua1995116](https://github.com/hua1995116/awesome-ai-painting) | Comprehensive Chinese AI painting/video resource collection. AnimateDiff, SVD, workflows. |

### 8.3 Chinese Workflow Resources (Bilibili + Blogs)

| Resource | Type | Link / Search |
|----------|------|--------------|
| **ComfyUI-WanVideoWrapper Tutorial** | Blog | CSDN: "深度解析ComfyUI-WanVideoWrapper" |
| **ComfyUI Animation Workflows** | Blog | CSDN: "ComfyUI动画生成工作流：制作连续帧AI视频的完整流程" |
| **ComfyUI Video Nodes Guide** | Blog | GitCode: "ComfyUI视频工作流：AI视频生成节点完全掌握指南" |
| **Bilibili ComfyUI Tutorials** | Video | Search "ComfyUI 动画工作流" on Bilibili |
| **OpenArt Flow** | Online | [openart.ai/workflows](https://openart.ai/workflows) — Web-based ComfyUI workflow sharing |
| **RunComfy / ViewComfy** | Cloud | Cloud ComfyUI with 100+ preloaded workflows |
| **Civitai Workflows** | Community | [civitai.com](https://civitai.com) — Models + workflows |

### 8.4 Animation-Specific ComfyUI Techniques

From the Chinese community research:

**Batch Rendering for Animation**:
```python
# Seed strategy for frame consistency
class IncrementalSeedGenerator:
    def generate(self, base_seed, frame_index):
        return (base_seed + frame_index,)  # +1 per frame for micro-variation
```

**ControlNet Stack for Character Animation**:
- OpenPose (body pose control)
- Canny (edge/shape consistency)
- Depth (spatial layering)
- All extracted from reference video frames via Python scripts

**Long Animation Pipeline**:
1. Preprocess: Extract frames from reference video → Canny/OpenPose/Depth
2. Build ComfyUI workflow with IncrementalSeedGenerator
3. Batch render via API: `POST http://127.0.0.1:8188/prompt`
4. Post-process: `ffmpeg -framerate 30 -i anim_%04d.png -c:v libx264 output.mp4`

---

## 9. Layer 7: Chinese AI Animation Studios (Existing Research)

Your project already contains extensive research:

| Document | Contents |
|----------|----------|
| `beijing_ai_animation_studios_top5.md` | Qimen Power, iQiyi Nadou Pro, CreateAI/Animon.ai, CMG/CCTV, PixVerse |
| `ai_drama_china_intel/` | 5 batches of Chinese AI drama studios |
| `ai_media_competitive_intel/` | Video (West + East), image, audio/3D, platform companies |

**Key Insight from Qimen Power**: They built the world's first AI-native theatrical animated film (*First Prototype*, 85 minutes) with ~10 people in 4 months. Their "Four AI Black Boxes" — Director AI, Art AI, Screenwriter AI, Cinematography AI — are exactly the architecture you need.

---

## 10. Recommended Build Architecture

Based on all research, here is the **recommended foundation stack** for your system:

### Phase 1: Reference Film Deconstruction (Weeks 1-2)

```
INPUT: Zootopia 2 video file
│
├─→ Video Expert Analyzer (Chinese/English, Walter Murch rules)
│   └─→ Scene boundaries, shot types, pacing, 5D scores
│
├─→ Video Subtitle Extractor (87 languages, hardcoded OCR)
│   └─→ Full dialogue transcript with timestamps
│
├─→ OpenMontage Reference Analysis
│   └─→ Transcript, pacing, scenes, keyframes, style summary
│
├─→ Gemini MCP / Qwen-VL (multimodal analysis)
│   └─→ Cinematography analysis, composition, lighting, color
│
└─→ LLM Synthesis (Claude/GPT-4o/Qwen-2-72B)
    └─→ Story structure (Save the Cat beats)
    └─→ Character archetypes & arcs
    └─→ Emotional beat mapping
    └─→ "Secret sauce" extraction (why it works)
```

### Phase 2: Creative DNA + New Story (Weeks 3-4)

```
INPUT: Deconstructed Zootopia 2 data
│
├─→ Story Structure Analyzer (Claude Screenplay Plugin)
│   └─→ 14-agent audit: foundation → macro → continuity → characters → craft
│
├─→ DNA Extractor (custom agent)
│   └─→ Theme, tone, pacing formula, visual style guide, character dynamics
│
└─→ New Story Generator (custom agent)
    └─→ Same DNA, new environment/characters/plot
    └─→ Scene-by-scene script with visual descriptions
    └─→ Shot list with camera direction
```

### Phase 3: Asset Generation (Weeks 5-8)

```
Character Design:
├─→ FLUX / SDXL for character concept art
├─→ IP-Adapter / PuLID for character consistency
├─→ LoRA training (GuarDVark plugin or Kohya_ss) for main characters
└─→ IDOL / LHM for 3D character models (optional)

Environment/Background:
├─→ FLUX for concept art
├─→ ControlNet (Depth/Canny) for consistency
└─→ SkyReels / Wan 2.2 for environmental video

Storyboard:
├─→ Keyframe generation per scene
└─→ GuarDVark Storyboard agent

Animation:
├─→ Bilibili AniSora V3.2 (primary animation engine)
│   └─→ I2V with spatiotemporal masks
│   └─→ Arbitrary-frame inference for key scene transitions
├─→ Wan Animate (character motion from reference)
├─→ Wan 2.2 (cinematic shots, 720P)
└─→ EchoMimic / FantasyTalking (lip sync for dialogue scenes)

Audio:
├─→ CosyVoice (Alibaba, speech synthesis, Chinese/English)
├─→ Suno / ElevenLabs Music (soundtrack)
├─→ ElevenLabs SFX (sound effects)
└─→ Wan 2.2 S2V (speech-to-video for talking scenes)
```

### Phase 4: Post-Production (Weeks 9-10)

```
├─→ ComfyUI / FFmpeg for scene assembly
├─→ OpenMontage Editor for transitions, pacing
├─→ Color grading via ComfyUI nodes
├─→ Audio mixing (OpenMontage Audio Mixer)
└─→ Final render with quality gates
```

### Technology Stack Summary

| Layer | Primary Tool | Backup |
|-------|-------------|--------|
| Video Analysis | OpenMontage + Video Expert Analyzer | VideoHighlighter + PySceneDetect |
| Script Extraction | Video Subtitle Extractor (87 languages) | biliSub + Whisper |
| Story Analysis | Claude Screenplay Plugin | Custom LLM prompts |
| Animation Engine | Bilibili AniSora V3.2 | Wan 2.2 + ComfyUI |
| Character Consistency | IP-Adapter + LoRA | PuLID + InstantID |
| Lip Sync / Talking | EchoMimic + Wan S2V | Wav2Lip + LivePortrait |
| Motion Transfer | Wan Animate | FollowYourEmoji |
| Video Editing | ComfyUI + FFmpeg | OpenMontage pipelines |
| Audio | CosyVoice + Suno | ElevenLabs + Piper (free) |
| Orchestration | OpenMontage agent system | GuarDVark Film Crew |

---

## 11. Immediate Next Steps

### Step 1: Validate the Foundation (This Week)
1. Clone and run **Bilibili AniSora V3.2** locally or on cloud GPU
2. Test **OpenMontage** with a reference YouTube video
3. Run **Video Expert Analyzer** on a Zootopia clip
4. Extract subtitles from a Zootopia trailer using **Video Subtitle Extractor**

### Step 2: Build the Deconstructor (Weeks 1-2)
1. Create a unified pipeline that combines:
   - PySceneDetect for scene boundaries
   - Gemini/Qwen-VL for frame-by-frame cinematography analysis
   - WhisperX for transcript with word-level timestamps
   - Custom LLM agent for "DNA extraction" (story structure, character arcs, visual style)

### Step 3: Build the Reconstructor (Weeks 3-4)
1. Extend OpenMontage's pipeline system with animation-specific stages
2. Add AniSora/Wan generation nodes to the ComfyUI workflow
3. Create character consistency system (LoRA + IP-Adapter pipeline)

### Step 4: Generate First Proof of Concept (Weeks 5-6)
1. Pick a 2-minute scene from Zootopia
2. Deconstruct it fully (script, shots, pacing, style)
3. Generate a new 2-minute scene with the same DNA but different characters/setting

---

## Appendix A: Complete GitHub Repository List

### Chinese Open-Source Animation/Video
- [bilibili/Index-anisora](https://github.com/bilibili/Index-anisora) — Animation video generation
- [Wan-Video/Wan2.2](https://github.com/Wan-Video/Wan2.2) — Cinematic video generation
- [wan-animate/wananimate](https://github.com/wan-animate/wananimate) — Character animation
- [aigc3d/LHM](https://github.com/aigc3d/LHM) — 3D human animation
- [yiyuzhuang/IDOL](https://github.com/yiyuzhuang/IDOL) — 3D human reconstruction
- [HITsz-TMG/VideoClaw](https://github.com/HITsz-TMG/VideoClaw) — Automated video generation

### Global Open-Source Animation/Video
- [mayuelala/FollowYourEmoji](https://github.com/mayuelala/FollowYourEmoji) — Portrait animation
- [Fantasy-AMAP/fantasy-talking](https://github.com/Fantasy-AMAP/fantasy-talking) — Talking characters

### Analysis & Production
- [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) — Agentic video production
- [ALBEDO-TABAI/video-expert-analyzer](https://github.com/ALBEDO-TABAI/video-expert-analyzer) — Video analysis (CN/EN)
- [ggvfx/film-breakdown-assistant](https://github.com/ggvfx/film-breakdown-assistant) — Script breakdown
- [Aseiel/VideoHighlighter](https://github.com/Aseiel/VideoHighlighter) — Local video analysis
- [joewhaley/cinemanga](https://github.com/joewhaley/cinemanga) — Script-to-comic-to-animation
- [realaman90/koda](https://github.com/realaman90/koda) — Agentic video ads
- [guaardvark/guaardvark](https://github.com/guaardvark/guaardvark) — Self-hosted AI workstation

### Script & Story
- [aslanSuleimenov/claude-screenplay-plugin](https://github.com/aslanSuleimenov/claude-screenplay-plugin) — Screenplay audit
- [Roundwhitefishdrop407/how-to-make-script](https://github.com/Roundwhitefishdrop407/how-to-make-script) — Script generation pipeline

### Subtitle Extraction
- [YaoFANGUK/video-subtitle-extractor](https://github.com/YaoFANGUK/video-subtitle-extractor) — 87-language OCR
- [lvusyy/biliSub](https://github.com/lvusyy/biliSub) — Bilibili subtitles
- [HuuHuy227/Hardcoded-Subtitle-Extraction](https://github.com/HuuHuy227/Hardcoded-Subtitle-Extraction) — Desktop subtitle extractor

### ComfyUI Ecosystem
- [kijai/ComfyUI-WanVideoWrapper](https://github.com/kijai/ComfyUI-WanVideoWrapper)
- [Kosinkadink/ComfyUI-AnimateDiff-Evolved](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved)
- [Yuan-ManX/ComfyUI-AniSora](https://github.com/Yuan-ManX/ComfyUI-AniSora)
- [xiaowuzicode/ComfyUI--](https://github.com/xiaowuzicode/ComfyUI--)
- [ZHO-ZHO-ZHO/ZHO-ZHO-ZHO](https://github.com/ZHO-ZHO-ZHO/ZHO-ZHO-ZHO)

---

> **End of Foundation Research**. This document should be treated as the starting blueprint. The next step is to pick one component (recommended: OpenMontage + AniSora) and build a working proof of concept.
