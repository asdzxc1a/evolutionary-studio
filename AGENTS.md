# AGENTS.md — Evolutionary Studio Checkpoint

**Created:** 2026-05-31
**Status:** System 3 is BUILT and OPERATIONAL. System 4 Phases 1-5 (Pattern Recognition, Language Engine, Director Agent, Vector Memory, Diffused Attention + Emotional Model) are BUILT and ACTIVE.
**Server:** Running at `http://localhost:8000`
**Python Env:** `openmontage/venv/`

---

## 1. THE VISION

Build an AI animation production studio that does not just generate pixels — it generates **coherent stories** through evolutionary selection pressure, then compiles them into production-ready packages.

The user is a creative director who wants to:
- Deconstruct reference films (like Zootopia) into "Creative DNA"
- Apply that DNA to new settings/characters/concepts
- Generate competing story concepts, prototype key scenes, run critic agents, select winners
- Compile the winning concept into a full production (screenplay, characters, environments, shot lists)
- Do this at ~$50 budget for a 90-minute animated film

**Core insight:** Real studios don't write one script. They write 6 concepts, prototype 2, kill one, iterate the winner. This system implements that loop.

---

## 2. THE ARCHITECTURE (7 Layers)

```
Layer 7: Cognitive OS (System 4)          ← PHASES 1-5 BUILT
         Pattern Recognition ✅ ACTIVE (replaces heuristic critics)
         Language Engine ✅ ACTIVE (voice profiling + dialogue validation)
         Director Agent ✅ ACTIVE (3-tier executive review: ACCEPT/REJECT/ITERATE)
         Vector Memory ✅ ACTIVE (ChromaDB + semantic search)
         Diffused Attention ✅ ACTIVE (background inconsistency scanner)
         Emotional Model ✅ ACTIVE (audience valence simulation)
         Real Generation ← PLANNED

Layer 6: Parallel Production Swarm         ← BUILT (system3/production_swarm.py)
         7 Department Agents: Writer, Visual Planner, Character, World,
         Animation, Sound, Editorial

Layer 5: Evolutionary Engine (System 3)    ← BUILT (system3/evolution_engine.py)
         Generate → Prototype → Critic → Select → Iterate

Layer 4: Creative DNA                      ← BUILT (studio/memory/films_analyzed/)
         Deconstructed reference films into structural templates

Layer 3: OpenMontage                       ← EXISTS (openmontage/)
         57+ tools for video/audio/image generation, tool registry,
         pipeline manifests, checkpoint system, cost tracker

Layer 2: China Open Source                 ← RESEARCHED
         AniSora, Wan 2.2, ComfyUI ecosystem (detailed in 32KB research doc)

Layer 1: Shared Memory (Obsidian Vault)    ← BUILT (studio/)
         Human-readable + machine-readable persistent state
```

**Decision rationale:** Build System 3 first (it produces tangible output), then System 4 on top (it makes System 3 smarter). A compiler without a brain is still useful. A brain without a compiler is just a simulator.

---

## 3. WHAT IS BUILT (System 3)

### 3.1 Backend — FastAPI Server (`api/`)

| File | Purpose | Lines |
|------|---------|-------|
| `api/server.py` | FastAPI app, CORS, static files, all endpoints | ~250 |
| `api/models.py` | Pydantic request/response models | ~80 |

**Endpoints:**
- `POST /api/produce` — Start production (background task)
- `GET /api/status/{id}` — Poll production status
- `GET /api/package/{id}` — Get full production package
- `GET /api/concepts` — List all concepts in vault
- `GET /api/concepts/{id}` — Get specific concept
- `GET /api/reviews` — List all reviews
- `GET /api/vault` — Browse vault notes
- `GET /api/vault/{path}` — Read specific note
- `GET /api/health` — Health check

### 3.2 System 3 Core (`system3/`)

| File | Purpose | Status |
|------|---------|--------|
| `system3/evolution_engine.py` | ConceptGenerator, PrototypeEngine, CriticSwarm, SelectionEngine, StoryEvolutionEngine | ✅ WORKING |
| `system3/production_swarm.py` | TaskQueue, DepartmentAgent base, 7 department agents, ProductionSwarm | ✅ WORKING |
| `system3/evolution_controller.py` | Orchestrates evolve → swarm → compile → save. Main entry point. | ✅ WORKING |
| `system3/__init__.py` | Package exports | ✅ |

**How the evolution loop works:**
1. `ConceptGenerator.load_dna()` reads Creative DNA from vault
2. `ConceptGenerator.generate()` creates N concepts using template pools (settings, conflicts, character archetypes)
3. `PrototypeEngine.prototype_concept()` generates 3 scenes per concept: Hook, Midpoint, Climax
4. `CriticSwarm.evaluate()` runs 4 critics:
   - Structure Critic (3-act breaks, midpoint placement)
   - Emotion Critic (emotional valence curve, range, recovery time)
   - Pacing Critic (dialogue-to-action ratio, scene duration)
   - Theme Critic (theme keywords, preachiness check, climax dialogue)
5. `SelectionEngine.select()` picks top-K, checks convergence criteria
6. If not converged, refined concepts go to Round 2
7. Winner is declared, passed to ProductionSwarm

**How the production swarm works:**
1. `ProductionSwarm.create_production_tasks()` creates 9 tasks with dependencies
2. `WriterAgent` writes 5-scene screenplay in Fountain format
3. `VisualPlannerAgent` plans 6 shots per scene (WS, MS, 2S, CU, OTS, ECU)
4. `CharacterAgent` designs characters, registers with ConsistencyEngine
5. `WorldBuilderAgent` creates 4 environments
6. `AnimationAgent`, `SoundAgent` are scaffolded (need API keys for real generation)
7. `EditorialAgent` assembles final cut
8. All outputs saved to Obsidian vault

### 3.3 Bridge Layer (`bridge/`)

| File | Purpose |
|------|---------|
| `bridge/obsidian_bridge.py` | Python ↔ Obsidian vault. Read/write/query markdown with YAML frontmatter. Canvas support. | ✅ |
| `bridge/openmontage_bridge.py` | Python ↔ OpenMontage tool registry. Tool discovery, execution, cost tracking, fallback resolution. | ✅ |
| `bridge/platform_bridge.py` | Python ↔ platform/ assets. ConsistencyEnginePy, CollaborationHubPy, VideoGenerationRouter. Adapts JS classes to Python. | ✅ |

### 3.4 Frontend (`frontend/`)

| File | Purpose | Lines |
|------|---------|-------|
| `frontend/index.html` | Single-page app with 5 tabs | ~350 |
| `frontend/static/styles.css` | Dark theme, cards, forms, progress bars | ~650 |
| `frontend/static/app.js` | SPA logic: tab switching, API calls, polling, vault browser, package renderer | ~700 |

**5 Tabs:**
1. **New Production** — Form with DNA source, setting, groups, theme, genre, concepts/rounds/budget. Pipeline flow visualization.
2. **Dashboard** — Stats cards, progress bar, swarm progress (total/pending/in-progress/completed/failed), completion celebration.
3. **Evolution** — Concept cards with winner badge, logline, score bars (structure/emotion/pacing/theme). Clickable for detail.
4. **Package** — Winning concept header, sub-tabs (Scenes/Characters/Environments/Shot Lists/Reviews), Fountain screenplay rendering.
5. **Vault** — Two-pane browser with folder filter, search, note list, markdown detail view with tags.

### 3.5 Studio Vault (`studio/`)

**Current contents (40+ notes):**
- `creative_brief.md` — Production brief template
- `decision_log.md` — Append-only decision log
- `concerns.md` — Active quality concerns
- `concepts/` — Generated concepts (concept-1-A through concept-1-D, WINNER)
- `scenes/` — 5 screenplay scenes in Fountain format + 5 shot lists
- `characters/` — Character bibles (6 characters) + environments (4)
- `reviews/` — Prototype reviews + selection reports
- `memory/films_analyzed/zootopia_dna.md` — Zootopia Creative DNA
- `memory/post_mortems/` — Production packages and post-mortems

### 3.6 CLI Entry Point

`run_studio.py` — argparse-based CLI that wraps `EvolutionController`

### 3.7 Configuration

`config/studio.yaml` — Studio configuration (evolution params, critic weights, department settings, memory limits)

---

## 4. HOW TO START THE SYSTEM

```bash
# 1. Activate environment
cd /Users/dmytrnewaimastery/Documents/AI\ Agents\ Test
source openmontage/venv/bin/activate

# 2. Start server
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# 3. Open browser
open http://localhost:8000

# OR use CLI
python run_studio.py --setting "a city of robots" --group-a robot --group-b human \
  --theme "trust between synthetic and organic life"
```

**Dependencies installed in venv:**
- fastapi, uvicorn, python-multipart
- playwright (for testing)
- All OpenMontage deps: pyyaml, pydantic, jsonschema, python-dotenv, Pillow, requests, yt-dlp, youtube-transcript-api, faster-whisper, scenedetect, opencv-python

---

## 5. KNOWN ISSUES AND WORKAROUNDS

| Issue | Workaround | Priority |
|-------|-----------|----------|
| Image/video/audio generation is MOCK | Uses OpenMontage tools but returns mock URLs. Needs API keys (Kling, Vidu, Suno, etc.) to produce real media. | High |
| ConceptGenerator uses templates | Produces somewhat repetitive concepts. Needs LLM integration (Claude/GPT) for true variety. | Medium |
| CriticSwarm uses heuristics | ✅ FIXED — Now uses System 4 Pattern Recognition with Save the Cat, 3-Act, character arc, emotional curve, and pacing formula analysis. | Done |
| No real cost tracking | `cost_tracker.py` exists in OpenMontage but not wired into studio budget enforcement. | Medium |
| EditorInterface.html not integrated | 32KB HTML UI exists in `platform/` but not wired to the new architecture. | Low |
| Vault can accumulate stale data | Multiple test productions create duplicate notes. No cleanup mechanism yet. | Low |

**Critical fix made during build:**
- JS syntax error: `$('#el')?.value = x` is invalid (optional chaining on LHS of assignment). Fixed to explicit null checks.

---

## 6. THE PHILOSOPHY (Co-Evolution, Not Replacement)

**The user asked: "Should the studio run inside you?"**

Answer: **No.** The studio must run independently. I am the conversational layer, not the infrastructure.

**Why:**
- I don't have long-term memory (context window gets compressed)
- I can't run background processes (no diffused attention while you sleep)
- Every reasoning step costs API tokens (expensive for 60-scene productions)
- I hallucinate and forget character names between scenes
- The studio needs to be usable when I'm not in the conversation

**The correct architecture:**
```
User (Creative Director)
    ↓ natural language
Me (Kimi — The Conductor)
    ↓ structured commands
System 4 (Cognitive OS — The Brain)
    ↓ spawns
System 3 (Evolutionary Studio — The Compiler)
    ↓ uses
OpenMontage + Obsidian Vault
```

**How we co-evolve:**
1. I analyze films → write Creative DNA to vault (I get sharper at deconstruction)
2. Studio uses DNA → generates concepts (studio gets better source material)
3. I review output → write critiques to reviews/ (my taste gets encoded)
4. Studio iterates → produces v2 (studio learns from my feedback)
5. We ship → write post-mortem to memory/ (institutional knowledge accumulates)
6. Next film → I query vault for patterns, studio queries embeddings (both sharper)

**My evolution is configurational** (better files in → better reasoning out).
**Studio's evolution is data-driven** (more productions → better embeddings → sharper pattern matching).

Together: a flywheel.

---

## 7. SYSTEM 4 (Cognitive OS) — SPECIFICATION

This is what needs to be built next. System 4 is the brain that makes System 3 smarter.

### 7.1 Director Agent (Executive Function)
- **Input:** User requests, System 3 outputs, Critic reports, Diffused Attention flags
- **Output:** Decisions: ACCEPT / REJECT / ITERATE / ESCALATE / SPAWN
- **State:** `creative_brief.md` (north star), `decision_log.md` (append-only), `concerns.md` (active issues)
- **Protocol:** Every decision includes REASON, ACTION, EVIDENCE

### 7.2 Working Memory Manager
- **Capacity:** ~5 scenes + 3 character bibles + 1 style guide = ~80% context window
- **Eviction:** LRU (Least Recently Used) — scenes not accessed in 3 turns get swapped to Obsidian
- **Prefetch:** When working on Scene N, auto-load Scene N-1 and N+1

### 7.3 Focused Attention
- Loads ONLY context needed for current task
- Excludes: scenes not in current sequence, characters not present, environments not used

### 7.4 Diffused Attention
- Background scanner that checks entire production for inconsistencies
- Checks: character consistency, plot continuity, theme drift, pacing decay, visual consistency, cost creep
- Flags written to `concerns.md`
- Mimics "shower insight" — idea that comes when not focused

### 7.5 Pattern Recognition Module
- Trained on 1,000+ films via embeddings
- Recognizes: story structures (3-act, Save the Cat, Hero's Journey), character archetypes, visual grammar, pacing formulas, genre conventions
- Usage: Scores drafts, suggests improvements

### 7.6 Emotional Model
- Simulates audience emotional valence beat-by-beat
- Rules: after -0.8 beat, need 90s recovery; all-is-lost at 75%; climax resolves to +0.8

### 7.7 Language Engine
- Character voice profiles with sarcasm density, cynicism, warmth, formality, vocabulary, sentence structure
- Scores dialogue lines against profile, flags out-of-voice lines

### 7.8 Long-Term Memory
- Vector DB (ChromaDB) of all films, characters, scenes, scores, costs, post-mortems
- Semantic search: "Show me all con-man protagonists. What worked?"

---

## 8. NEXT PHASES (Exact Spec)

### Phase A: Skill Injection (Priority: HIGH)
**Goal:** Make department agents read skill files before executing tasks.

**Files to create:**
- `studio/skills/screenplay-craft.md` — Story structure, dialogue rules, slugline format
- `studio/skills/visual-grammar.md` — Shot sizes, camera movements, lighting schemes
- `studio/skills/character-design.md` — Archetype patterns, voice profiling, consistency rules
- `studio/skills/critic-criteria.md` — Scoring rubrics for structure/emotion/pacing/theme

**Code change:** In each DepartmentAgent.execute_task(), read relevant skill from vault and inject into prompt context.

**Success criteria:** Writer Agent produces screenplay that follows Save the Cat beats without explicit prompting.

### Phase B: Vector Memory (Priority: HIGH)
**Goal:** Build LongTermMemory module with semantic search.

**Files to create:**
- `system4/long_term_memory.py` — ChromaDB wrapper, embedding generation, semantic query
- `studio/memory/embeddings/` — ChromaDB persistence directory

**Code change:**
1. Chunk all post-mortems into segments
2. Embed with sentence-transformers
3. Store in ChromaDB
4. Pattern Recognition queries DB before scoring

**Success criteria:** Pattern Recognition can answer: "What emotional curves worked for buddy-cop films?" with evidence from previous productions.

### Phase C: Director Agent (Priority: HIGH)
**Goal:** Build the decision-making brain that reviews System 3 outputs.

**Files to create:**
- `system4/director_agent.py` — Decision protocol, state management
- `system4/diffused_attention.py` — Background inconsistency scanner
- `system4/working_memory.py` — Context loading/eviction

**Code change:**
1. Director Agent loads production package
2. Runs Diffused Attention scan
3. Applies decision protocol
4. Writes decision to decision_log.md
5. If ITERATE, sends specific notes back to System 3

**Success criteria:** Director Agent catches character inconsistency ("Judy fears water in Scene 3 but cannonballs in Scene 47") and rejects with specific rewrite instructions.

### Phase D: Real Generation (Priority: MEDIUM)
**Goal:** Wire actual API keys for image/video/audio generation.

**Prerequisites:**
- Kling API key → video generation
- Suno API key → music generation
- CosyVoice/ElevenLabs API key → TTS
- Flux/Stable Diffusion API key → concept art

**Code change:**
1. Add API keys to `.env`
2. Update `api_gateway.py` to use real endpoints instead of mocks
3. Update `AnimationAgent` and `SoundAgent` to use real tools

**Success criteria:** A 5-scene sequence generates actual video clips, not mock URLs.

### Phase E: Feedback Loop (Priority: MEDIUM)
**Goal:** Capture my creative critiques and encode them into the system.

**Workflow:**
1. Studio completes production
2. Presents package via CLI or API
3. I critique in natural language
4. Critique is parsed (manually or via structured prompt) into tagged notes
5. Notes added to post-mortem
6. Pattern Recognition reweights scoring based on my preferences

**Success criteria:** After 10 productions, the studio knows I hate preachy themes and love redemption arcs, and scores accordingly.

---

## 9. FILE INVENTORY

```
/Users/dmytrnewaimastery/Documents/AI Agents Test/
├── AGENTS.md                          ← THIS FILE
├── run_studio.py                      ← CLI entry point
├── config/
│   └── studio.yaml                    ← Studio configuration
├── api/
│   ├── server.py                      ← FastAPI backend
│   └── models.py                      ← Pydantic models
├── frontend/
│   ├── index.html                     ← SPA shell
│   └── static/
│       ├── app.js                     ← Frontend logic (~700 lines)
│       └── styles.css                 ← Dark theme (~650 lines)
├── system3/
│   ├── __init__.py
│   ├── evolution_engine.py            ← Concept→Prototype→Critic→Select (~500 lines)
│   ├── production_swarm.py            ← 7 department agents (~380 lines)
│   └── evolution_controller.py        ← Orchestrator (~140 lines)
├── system4/                           ← BUILT — All 5 phases
│   ├── pattern_recognition.py         ← Structural analysis engine (~1200 lines)
│   ├── language_engine.py             ← Voice profiling + dialogue analysis (~700 lines)
│   ├── director_agent.py              ← Executive decision layer (~500 lines)
│   ├── long_term_memory.py            ← Vector memory + semantic search (~750 lines)
│   ├── emotional_model.py             ← Audience valence simulation (~450 lines)
│   └── diffused_attention.py          ← Background inconsistency scanner (~450 lines)
├── bridge/
│   ├── obsidian_bridge.py             ← Vault I/O (~150 lines)
│   ├── openmontage_bridge.py          ← Tool registry wrapper (~130 lines)
│   └── platform_bridge.py             ← Platform adapters (~200 lines)
├── studio/                            ← Obsidian vault (40+ notes)
│   ├── creative_brief.md
│   ├── decision_log.md
│   ├── concerns.md
│   ├── concepts/
│   ├── scenes/
│   ├── characters/
│   ├── reviews/
│   ├── memory/
│   │   ├── films_analyzed/
│   │   └── post_mortems/
│   └── production.canvas
├── platform/                          ← Pre-existing assets
│   ├── api_gateway.py                 ← Kling/Vidu adapters
│   ├── consistency_engine.js          ← Character consistency
│   ├── collaboration_hub.js           ← Review/feedback system
│   └── editor_interface.html          ← 32KB UI (not integrated)
└── openmontage/                       ← Cloned repo with 57+ tools
```

---

## 10. KEY RESEARCH ASSETS

| File | Size | Contents |
|------|------|----------|
| `animation_ai_foundation_research.md` | 32KB | 47+ open-source repos across China/GitHub (AniSora, Wan 2.2, ComfyUI, etc.) |
| `FOUR_OPINIONS_SYSTEM_DESIGN.md` | 29KB | Strategic analysis: surface assessment → inner mechanism architecture |
| `openmontage/projects/zootopia_combined_reference_analysis.md` | ~15KB | Zootopia Creative DNA extraction, 4 differentiation seeds |
| `beijing_ai_animation_studios_top5.md` | ~17KB | Top 5 Beijing AI animation studios analysis |
| `cannes_research_report.md` | ~22KB | Cannes Film Festival strategy research |

---

## 11. USER PREFERENCES (Inferred)

- **Wants co-evolution**, not replacement. System and agent improve together.
- **Wants deep architecture**, not superficial tools. Thinks in systems, not features.
- **Values institutional memory.** Every production should teach the next one.
- **Wants to use my best capabilities** (analysis, strategy, creative judgment) as structured inputs to the system.
- **Wants the studio to be independent** — usable without my presence.
- **Budget target:** $50 for 90-minute animated film.
- **Reference film:** Zootopia (2016) — used as primary Creative DNA template.
- **Existing assets:** `platform/` code (ConsistencyEngine, CollaborationHub, API gateway) should be integrated, not discarded.

---

## 12. SYSTEM 4 PHASE 1: PATTERN RECOGNITION (BUILT 2026-05-31)

### What Was Built

**`system4/pattern_recognition.py`** (~850 lines) — Replaces heuristic keyword-matching critics with real structural analysis.

### Pattern Library Contents

| Pattern Type | Count | Examples |
|-------------|-------|----------|
| Story Structures | 2 | Save the Cat (15 beats), Three-Act Structure (7 beats) |
| Character Arcs | 3 | Positive Change, Flat Arc, Negative Change (Fall) |
| Emotional Arcs | 3 | Rags to Riches, Comedy Arc, Tragedy Arc |
| Pacing Formulas | 1 | Animated Feature (90 min, 45-65 scenes, 1.5:1 action/dialogue) |
| Theme Patterns | 1 | Social Metaphor (show-don't-tell, preachiness check, two-sided test) |

### Analyzers

| Analyzer | What It Checks |
|----------|---------------|
| **StructureAnalyzer** | Beat completeness, midpoint turn quality, B-story hints, act structure |
| **CharacterArcAnalyzer** | Arc completeness, transformation, core wound, archetype, scene presence |
| **EmotionalArcAnalyzer** | Valence range, recovery timing, climax resolution, pattern match |
| **PacingAnalyzer** | Hook/climax duration, action/dialogue ratio, scene count, total duration |
| **ThemeAnalyzer** | Metaphor specificity, preachiness, show-don't-tell, act sustainability, two-sided nuance |

### Integration

`CriticSwarm` now uses `PatternRecognizer` by default. Falls back to heuristics if unavailable.

New weights:
- structure: 0.20
- character: 0.15 (NEW)
- emotion: 0.25
- pacing: 0.15
- theme: 0.25

### Skill Files Created

- `studio/skills/story-structure.md` — 3-act architecture, Save the Cat, animation-specific notes
- `studio/skills/character-design.md` — Lie-Truth arcs, voice profiling, relationship evolution
- `studio/skills/visual-grammar.md` — Shot sizes, camera movement, lighting, composition, editing
- `studio/skills/critic-criteria.md` — Scoring rubrics for all 5 critic categories

### Impact: Before vs After

| Concept | Heuristic Combined | Pattern Recognition Combined | Key Difference |
|---------|-------------------|------------------------------|----------------|
| "Beyond the Human Wall" | 8.8 | 9.1 | +character category (9.5), theme caught as one-sided (6.7 vs 8.5) |

**Pattern Recognition catches issues heuristics miss:**
- Theme sustainability across acts
- Character core wound absence
- Two-sided theme nuance
- Emotional arc pattern match (93% Rags to Riches)
- B-story presence

---

## 13. SYSTEM 4 PHASE 2: LANGUAGE ENGINE (BUILT 2026-05-31)

### What Was Built

**`system4/language_engine.py`** (~700 lines) — Voice profiling, dialogue consistency analysis, and rewrite suggestions.

### Voice Profile System

**Six voice dimensions (0-100 scale):**
- **Sarcasm** — Irony, understatement, deflection
- **Cynicism** — Negative expectations, distrust
- **Warmth** — Affection, caring, openness
- **Formality** — Vocabulary, grammar, contractions
- **Verbosity** — Word count per sentence
- **Subtext** — Implication vs direct statement

**16 archetype templates:** Optimistic Underdog, Cynical Trickster, Hidden Tyrant, Naive Idealist, Wounded Veteran, Corrupt Bureaucrat, Reluctant Mentor, Charismatic Demagogue, Curious Explorer, Jaded Survivor, Manipulative Advisor, Determined Reformer, Apathetic Con-Artist, Earnest Believer, Sarcastic Realist, Ambitious Schemer.

### Dialogue Analysis

| Capability | What It Does |
|------------|-------------|
| **Voice Consistency Scoring** | Scores each line against speaker's voice profile (0.0-1.0) |
| **On-the-Nose Detection** | Flags lines that state emotions directly ("I feel sad") |
| **Subtext Analysis** | Scores implication vs direct statement |
| **Forbidden Phrase Detection** | Catches lines that violate character voice |
| **Rewrite Suggestions** | Generates alternative lines for low-scoring dialogue |
| **Screenplay Analysis** | Analyzes all dialogue across all scenes, finds worst lines |

### Integration Points

| Component | Change |
|-----------|--------|
| **CharacterAgent** | Generates voice profiles from archetypes → writes `characters/{id}_voice.md` |
| **WriterAgent** | Loads voice profiles → generates voice-aware dialogue → validates with Language Engine |
| **CriticSwarm** | New **Dialogue Critic** category (weight 0.13) using Language Engine |
| **Frontend** | Score bars now show **6 categories** (added Dialogue) |

### Critic Weights (Updated)

- structure: 0.18
- character: 0.12
- emotion: 0.22
- pacing: 0.13
- theme: 0.22
- **dialogue: 0.13** (NEW)

### Example Output

**Voice Profile: Jaded Survivor**
```
Sarcasm: 80, Cynicism: 90, Warmth: 15, Formality: 30, Verbosity: 35, Subtext: 80
Signature: "Seen it all", "Doesn't matter", "Trust no one"
Forbidden: "Everything happens for a reason", "People are good", "I have hope"
```

**Dialogue Validation:**
```
Line: "I feel very sad about this situation."
Speaker: Nick Wilde (Cynical Trickster)
Score: 0.33/1.0
Issues: ["On-the-nose emotional statement", "Too earnest for sarcastic character"]
Rewrite: "[Action: Nick looks away, voice dropping.] 'I shouldn't have...'"
```


---

## 14. SYSTEM 4 PHASE 3: DIRECTOR AGENT (BUILT 2026-05-31)

### What Was Built

**`system4/director_agent.py`** (~400 lines) — Executive decision layer that reviews production packages and gates quality with structured verdicts.

### Decision Protocol

| Verdict | Trigger | Action |
|---------|---------|--------|
| **ACCEPT** | Combined ≥7.5, all categories ≥5.0, no critical issues | Green light to production |
| **REJECT** | Combined <4.0 OR any critical issue OR <3 categories pass | Kill the production, log reason |
| **ITERATE** | Everything else (4.0–7.5) | Send specific improvement notes back to swarm |

### Key Capabilities

| Capability | What It Does |
|------------|-------------|
| **Confidence Scoring** | 0.0-1.0 based on category spread and issue severity |
| **Dimension Analysis** | Per-dimension scores with specific improvement notes |
| **Issue Classification** | `is_iterable()` — determines if an issue is fixable vs fundamental |
| **Vault Integration** | Writes `reviews/director_decision_{production_id}.md` to vault |
| **Decision Logging** | Appends to `studio/decision_log.md` with REASON, ACTION, EVIDENCE |

### Integration Points

| Component | Change |
|-----------|--------|
| **EvolutionController** | New Phase 3.5 between compile and save: `_director_review(package)` |
| **ProductionPackage** | New `director_decision` field |
| **Frontend** | Package tab shows Director verdict badge (green/yellow/red) with confidence % |

### Example Output

```
Director Review: demo-robot-city-001
Verdict: ITERATE
Confidence: 70%

Reason: Combined score 9.0 is close to acceptance but 0 dimension(s) need improvement.

Dimension Scores:
- structure: 9.1
- character: 9.5
- emotion: 10.0
- pacing: 10.0
- theme: 6.7  ← flagged for shallow theme
- dialogue: 8.5

Action: Send specific notes back to production swarm for targeted revision.
```

### Known Issue

ITERATE threshold may be too sensitive for high scores with minor category spread. A combined 9.0 with one weak dimension (theme 6.7) triggers ITERATE rather than ACCEPT. Tuning may be needed.

---

---

## 15. SYSTEM 4 PHASE 5: DIFFUSED ATTENTION + EMOTIONAL MODEL (BUILT 2026-06-01)

### What Was Built

Two modules that add "shower insight" capabilities — catching problems that focused analyzers miss.

**`system4/emotional_model.py`** (~450 lines) — Simulates audience emotional response beat-by-beat.

**`system4/diffused_attention.py`** (~450 lines) — Background scanner for cross-cutting inconsistencies.

### Emotional Model

| Component | Purpose |
|-----------|---------|
| **EmotionalSimulator** | Generates valence/arousal beats from scene content using keyword analysis |
| **ArcLibrary** | 5 built-in patterns: Rags to Riches, Comedy, Tragedy, Man in a Hole, Icarus |
| **RecoveryValidator** | Ensures negative beats (-0.5+) are followed by recovery within 90s |
| **ClimaxValidator** | Checks climax resolves to +0.5, all-is-lost at ~75%, range ≥1.0 |

**Rules enforced:**
- After -0.8 beat → need 90s recovery
- All-is-lost at ~75% of runtime
- Climax resolves to +0.8
- Emotional range ≥ 1.0
- No more than 3 consecutive negative beats

### Diffused Attention

| Scanner | Checks For |
|---------|-----------|
| **ContinuityScanner** | Character disappears too long, contradictory behavior vs archetype, missing protagonist |
| **ThemeDriftScanner** | Theme absence per act, theme decay in Act 3 |
| **PacingDecayScanner** | Action density drop in Act 3 vs Act 1 |
| **ArcCompletenessScanner** | Characters who appear in Act 1 but not finale, late-introduced characters |

### Integration Points

| Component | Change |
|-----------|--------|
| **EvolutionController** | Phase 3.6: Runs after Director Review, before Save |
| **Vault** | Writes `reviews/emotional_analysis_{id}.md` and `reviews/diffused_attention_{id}.md` |
| **PatternRecognizer** | Emotional arc notes enriched with historical context from LTM |
| **API** | New endpoints: `/api/emotional/{id}`, `/api/concerns/{id}` |
| **Frontend** | Package tab shows Emotional Arc badge + Concerns badge; new sub-tabs for both |

### Example Output

```
PHASE 3.6: Diffused Attention + Emotional Model
----------------------------------------
  ⚠ 3 concern(s) flagged:
    🟠 [theme] Theme is nearly absent from Act 2 (0% keyword presence)
    🟠 [theme] Theme decays significantly in Act 3
    🟡 [arc] Character 'Judy' appears in Act 1 but not in final act
  Emotional arc: Rags to Riches (score: 5.0/10)
  Valence range: 0.8
  Issues: 2
```

---

## 16. SYSTEM 4 PHASE 4: VECTOR MEMORY (BUILT 2026-05-31)

### What Was Built

**`system4/long_term_memory.py`** (~500 lines) — ChromaDB-based vector memory with sentence-transformer embeddings and semantic search.

### Architecture

| Component | Purpose |
|-----------|---------|
| **DocumentChunker** | Splits vault notes into semantically meaningful chunks per document type |
| **EmbeddingEngine** | `all-MiniLM-L6-v2` model (384-dim) for text → vector |
| **VectorStore** | ChromaDB with per-type collections (cosine similarity) |
| **LongTermMemory** | High-level API: ingest, search, ask |

### Collections

| Collection | Contents | Count (example) |
|-----------|----------|-----------------|
| `concepts` | Concept descriptions, loglines, themes | 35 |
| `evaluations` | Critic scores, issues, strengths | 57 |
| `post_mortems` | Production summaries, learnings | 66 |
| `voice_profiles` | Character voice dimensions | 5 |
| `scenes` | Scene sluglines, content | 11 |
| `decisions` | Director verdicts, reasons | 4 |

### Integration Points

| Component | Change |
|-----------|--------|
| **EvolutionController** | Phase 5: Auto-indexes production into vector memory after completion |
| **PatternRecognizer** | Queries LTM for similar past evaluations before scoring (enriches notes with historical context) |
| **API** | New endpoints: `/api/memory/search`, `/api/memory/stats`, `/api/memory/ingest` |
| **Frontend** | New **Memory** tab (6th tab) with semantic search, doc-type filters, match scores |

### Example Queries

```
Search: "redemption arc"
→ [evaluation] 37% match: "Protagonist has complete transformation arc..."
→ [concept] 35% match: "Unit-7 (determined reformer) — Start: naive..."

Search: "strong emotional transformation"
→ [concept] 51% match: "Relay has meaningful transformation..."
→ [evaluation] 50% match: "Emotional arc matches Rags to Riches (93%)..."
```

### API Examples

```bash
# Search all memory
curl "http://localhost:8000/api/memory/search?q=emotional+arc&n=5"

# Filter by document type
curl "http://localhost:8000/api/memory/search?q=redemption&doc_type=evaluation"

# Get stats
curl "http://localhost:8000/api/memory/stats"

# Re-ingest vault
curl -X POST "http://localhost:8000/api/memory/ingest"
```

---

## 17. IF YOU READ THIS WITH ZERO CONTEXT

1. The project is an AI animation studio called **Evolutionary Studio** (System 3)
2. It's built on top of **OpenMontage** (Layer 3) with an **Obsidian vault** (Layer 1)
3. The backend is **FastAPI** running on `localhost:8000`
4. The frontend is a vanilla JS SPA at `frontend/index.html`
5. System 3 is DONE. **System 4 Phases 1-5 are DONE and ACTIVE.**
6. The user wants **co-evolution** — my reasoning feeds the studio, studio data feeds my reasoning.
7. Start the server (Section 6), open the browser, test a production.
8. Next: Phase 6 (Real Generation).
9. Read the research assets (Section 10) for domain knowledge.
10. Check `studio/memory/post_mortems/` for what previous productions learned.

---

## 18. SESSION: 2026-06-02 — CLI + QUALITY UPGRADE

### What Was Done

**1. CLI Rewritten (`run_studio.py` v0.1.0 → v0.2.0)**
- Added subcommands: `produce`, `status`, `list`, `package`
- Backward-compatible: legacy usage without subcommand still works
- Configuration hierarchy: CLI args > env vars (`STUDIO_*`) > `config/studio.yaml` > defaults
- Dry-run mode, output formats (pretty/json/markdown), file output
- Resume protection (duplicate ID detection), `--force` overwrite
- Structured logging (`-v`/`-vv`, `--quiet`, `--log-file`)
- Proper exit codes (0/1/2/3) and signal handling

**2. Zootopia 2 Creative DNA Extracted**
- File: `studio/memory/films_analyzed/zootopia2_dna.md` (12.6 KB)
- Extracted from 107-page Jared Bush screenplay
- 15 Save the Cat beats with page ranges, 6 archetypes with voice dimensions, dialogue craft rules

**3. Skill Files Upgraded**
- `studio/skills/story-structure.md` — B-story/C-story mechanics, animation pacing rules
- `studio/skills/character-design.md` — 5 Zootopia 2 archetypes with full voice profiles
- `studio/skills/dialogue-craft.md` — 10 professional dialogue rules (NEW)

**4. ConceptGenerator Rewritten**
- 12 settings, 10 conflicts, 8 archetype trios with relationship mechanics
- Archetype-specific builders: protagonist, deuteragonist, antagonist
- 6 logline templates with emotional stakes, 15 structure variations
- Pluralization fix, hierarchical DNA parsing

**5. WriterAgent Rewritten**
- 8 beat-mapped scenes (Opening, Catalyst, Debate, Fun & Games, Midpoint, Bad Guys, Dark Night, Finale)
- Camera directions, parentheticals, visual gags, beat-specific openings/closings
- Archetype-specific dialogue pools with adapted lines from Zootopia 2

### File Changes
- **Modified:** `run_studio.py`, `system3/evolution_engine.py`, `system3/production_swarm.py`, `studio/skills/story-structure.md`, `studio/skills/character-design.md`
- **New:** `studio/memory/films_analyzed/zootopia2_dna.md`, `studio/skills/dialogue-craft.md`, `studio/memory/checkpoints/CHECKPOINT_2026-06-02.md`

### Known Limitations
- Still template-based (not LLM-generated originality)
- Director Agent flags theme as absent from acts
- Image/video/audio generation is MOCK (needs API keys)

### Next Steps (Priority Order)
1. **Custom DNA for Ukrainian fairy-tale** — Hero's Journey beats, fairy-tale ally archetypes
2. **Theme integration** — weave theme keywords into every scene
3. **LLM integration** — replace templates with Claude/GPT-4 generation
4. **Real generation** — wire Kling/Suno/Flux API keys

### Checkpoint
Full session record: `studio/memory/checkpoints/CHECKPOINT_2026-06-02.md`


---

## 19. SESSION: 2026-06-03 — AI-AS-ENGINE + SELF-IMPROVEMENT SYSTEM

### The Insight

The user clarified: **no API calls**. The AI (Claude Code, Codex, Kimi) IS the writer engine. Python is the producer that creates the brief. This is not a limitation — it is the correct architecture. A real studio doesn't have a robot write the script. It has a producer create a brief, a writer write from the brief, and an editor validate.

### What Was Built

**1. Scene Brief Compiler (`system3/scene_brief_compiler.py`)**
- Compiles rich creative briefs for each of the 8 beats
- Each brief includes: metadata, story context, character voice profiles, theme weaving instructions, callback setup/payoff, dialogue craft rules, visual direction, writing instructions
- Generates a **Writer's Packet** — single markdown file with all briefs + character cheat sheet
- Briefs saved to `studio/briefs/{production_id}/`

**2. AI-as-Engine Workflow**
```
python run_studio.py briefs --production-id "my-film"
# AI reads Writer's Packet, writes scenes to studio/scenes/
python run_studio.py assemble my-film
```

**3. Script Ingestor (`system4/script_ingestor.py`)**
- Parses Fountain screenplays into structured scenes
- Profiles character voices (6 dimensions) using heuristic analysis
- Detects callback phrases (repeated with transformed meaning)
- Extracts theme keywords and density per act
- Generates Creative DNA from any screenplay
- **Updates skill files** with learned patterns (append-only)
- Usage: `python run_studio.py ingest screenplay.fountain --title "Film Name"`

**4. Self-Improvement Engine (`system4/self_improvement.py`)**
- Tracks production history (scores, templates used, director verdicts)
- Identifies weakest category across all productions
- Queries top performers in that category
- Generates improvement proposals (template, skill, code changes)
- Auto-applies safe improvements (skill file appendices)
- Generates evolution reports showing trend over time
- Usage: `python run_studio.py evolve`

**5. CLI Extended (`run_studio.py` v0.2.0 → v0.2.1)**
New subcommands:
| Command | Purpose |
|---------|---------|
| `briefs` | Generate scene briefs for AI writers |
| `assemble` | Compile AI-written scenes into screenplay |
| `ingest` | Learn from a new screenplay |
| `evolve` | Run self-improvement analysis |

### The Self-Improving Flywheel

```
Ingest Script → Extract DNA/Patterns → Update Skill Files
       ↑                                      ↓
       └───── Learn from results ─────────────┘
              (Self-Improvement Engine)

Produce → Director Scores → Identify Weakness
   ↑                            ↓
   └──── Query Memory for solutions ─┘
          (What worked before?)
```

**How it works in practice:**
1. User ingests Zootopia 2 screenplay → system extracts DNA, updates dialogue-craft.md with observed patterns
2. User runs production → Director scores it 6.5 on dialogue
3. Self-Improvement Engine checks history → "Dialogue is consistently weak"
4. Engine queries LTM → "Productions using Zootopia 2 DNA scored 8.2 on dialogue"
5. Engine proposes: "Use Zootopia 2 DNA for dialogue patterns" → auto-appends note to skill file
6. Next production uses improved context → scores higher

### File Changes
- **New:** `system3/scene_brief_compiler.py` — Brief compiler + Screenplay assembler
- **New:** `system4/script_ingestor.py` — Script ingestion + DNA generation
- **New:** `system4/self_improvement.py` — Feedback loop + evolution tracking
- **Modified:** `system3/production_swarm.py` — WriterAgent now supports `generate_briefs` task
- **Modified:** `run_studio.py` — Added `briefs`, `assemble`, `ingest`, `evolve` subcommands
- **Modified:** `studio/skills/dialogue-craft.md` — Auto-appended learned patterns from test ingestion
- **Modified:** `studio/skills/character-design.md` — Auto-appended archetype observations

### Updated Architecture

```
Layer 7: Cognitive OS (System 4)
         Pattern Recognition ✅
         Language Engine ✅
         Director Agent ✅
         Vector Memory ✅
         Diffused Attention ✅
         Emotional Model ✅
         Script Ingestor ← NEW (learns from screenplays)
         Self-Improvement Engine ← NEW (evolves system)

Layer 6: Parallel Production Swarm
         WriterAgent ← NOW generates briefs AND templates

Layer 5: Evolutionary Engine (System 3)
         ConceptGenerator ← Template evolution tracking

Layer 4: Creative DNA
         Zootopia 1 DNA ✅
         Zootopia 2 DNA ✅
         User-ingested DNAs ← NEW (auto-generated)

Layer 3: OpenMontage

Layer 2: China Open Source

Layer 1: Shared Memory (Obsidian Vault)
         studio/briefs/ ← NEW (creative briefs for AI writers)
         studio/memory/production_history.jsonl ← NEW (score tracking)
         studio/memory/evolution_reports/ ← NEW (trend reports)
```

### How to Use the New System

**Generate briefs for AI writer:**
```bash
python run_studio.py briefs --production-id "my-film" --concept-id WINNER
# Read studio/briefs/my-film/WRITERS_PACKET.md
# Write scenes following each brief
# Save to studio/scenes/001_opening.md, etc.
python run_studio.py assemble my-film
```

**Learn from a professional screenplay:**
```bash
python run_studio.py ingest /path/to/zootopia2.fountain --title "Zootopia 2"
# System extracts DNA, profiles characters, detects callbacks
# Skill files are auto-updated with observed patterns
```

**Track system evolution:**
```bash
python run_studio.py evolve
# Shows score trends, weakest category, proposals
```

### Known Limitations
- Brief compiler character detection depends on vault character bibles being present
- Script ingestor callback detection is basic (n-gram matching)
- Self-improvement auto-application is conservative (only skill file appendices)
- LTM integration in ingestor is simplified

### Next Steps
1. **Run a full production with briefs** — test the AI-as-Engine workflow end-to-end
2. **Ingest a real feature screenplay** — extract richer DNA from a 90-page script
3. **Build template evolution** — weight ConceptGenerator templates by historical success
4. **Theme integration** — weave theme keywords into scene briefs more deeply

---

**Status:** System is now self-learning. Every screenplay ingested makes it smarter. Every production recorded improves the next one.
