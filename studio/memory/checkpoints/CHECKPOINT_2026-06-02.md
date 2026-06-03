# Evolutionary Studio — Session Checkpoint
**Date:** 2026-06-02
**Session Focus:** Rewriting the CLI and core generation pipeline to approach professional screenplay quality
**Status:** System 3 + 4 operational. Major quality upgrade implemented.

---

## 1. PROJECT ARCHITECTURE (What Exists)

```
Layer 7: Cognitive OS (System 4)          ← PHASES 1-5 BUILT
         Pattern Recognition, Language Engine, Director Agent,
         Vector Memory, Diffused Attention, Emotional Model

Layer 6: Parallel Production Swarm         ← BUILT (system3/production_swarm.py)
         7 Department Agents

Layer 5: Evolutionary Engine (System 3)    ← BUILT (system3/evolution_engine.py)
         Generate → Prototype → Critic → Select → Iterate

Layer 4: Creative DNA                      ← UPDATED TODAY
         Zootopia 1 DNA (original)
         Zootopia 2 DNA (NEW — extracted from 107-page script)

Layer 3: OpenMontage                       ← EXISTS
         57+ tools, pipeline manifests, cost tracker

Layer 2: China Open Source                 ← RESEARCHED

Layer 1: Shared Memory (Obsidian Vault)    ← BUILT (studio/)
         Human-readable + machine-readable persistent state
```

**Server:** Running at `http://localhost:8000` (FastAPI + static frontend)
**Python Env:** `openmontage/venv/`

---

## 2. WHAT EXISTED BEFORE THIS SESSION

### System 3 Core (Pre-Session State)
- `system3/evolution_engine.py`: Template-based ConceptGenerator with 6 settings, 5 conflicts, 6 archetype trios
- `system3/production_swarm.py`: WriterAgent producing 5 generic scenes with placeholder dialogue
- `system3/evolution_controller.py`: Orchestrator with Director Review + Diffused Attention + LTM indexing

### System 4 Core (Pre-Session State)
- `system4/pattern_recognition.py`: Structural analysis engine (~1200 lines)
- `system4/language_engine.py`: Voice profiling + dialogue analysis (~700 lines)
- `system4/director_agent.py`: Executive decision layer (~500 lines)
- `system4/long_term_memory.py`: ChromaDB vector memory (~750 lines)
- `system4/emotional_model.py`: Audience valence simulation (~450 lines)
- `system4/diffused_attention.py`: Background inconsistency scanner (~450 lines)

### Frontend / API (Pre-Session State)
- `api/server.py`: FastAPI with all endpoints
- `api/models.py`: Pydantic models
- `frontend/index.html`: SPA with 5 tabs (New Production, Dashboard, Evolution, Package, Vault)
- `frontend/static/app.js`: Frontend logic (~700 lines)
- `frontend/static/styles.css`: Dark theme (~650 lines)

### Skill Files (Pre-Session State)
- `studio/skills/story-structure.md` — basic 3-act + Save the Cat
- `studio/skills/character-design.md` — basic archetype pools
- `studio/skills/visual-grammar.md` — shot sizes, camera movement
- `studio/skills/critic-criteria.md` — scoring rubrics

### DNA Files (Pre-Session State)
- `studio/memory/films_analyzed/zootopia_dna.md` — Zootopia 1 Creative DNA

### CLI (Pre-Session State)
- `run_studio.py` v0.1.0 — basic argparse with top-level args only

---

## 3. WHAT WAS DONE IN THIS SESSION

### 3.1 CLI Completely Rewritten
**File:** `run_studio.py` (upgraded from v0.1.0 → v0.2.0)

**New features:**
- **Subcommands:** `produce`, `status`, `list`, `package`
- **Backward compatibility:** Legacy usage `run_studio.py --setting x --theme y` still works via `_infer_subcommand()`
- **Configuration hierarchy:** CLI args → Environment variables (`STUDIO_SETTING`, `STUDIO_THEME`, etc.) → `config/studio.yaml` → defaults
- **Dry-run mode:** `--dry-run` validates inputs without executing
- **Output formats:** `--format pretty|json|markdown` + `--output <file>`
- **Resume protection:** Warns if `--production-id` already exists; `--force` to overwrite
- **Structured logging:** `--verbose` / `-vv` / `--quiet` / `--log-file`
- **Coloured output:** Auto-detects TTY; `--no-color` to disable
- **Input validation:** Required fields, range checks (1–20 concepts, 1–10 rounds), DNA file existence
- **Proper exit codes:** 0=success, 1=runtime error, 2=interrupted, 3=validation error
- **Signal handling:** Graceful Ctrl+C shutdown

**Tested and working:**
- `run_studio.py --version` → `0.2.0`
- `run_studio.py --help` with examples and environment variables
- `run_studio.py --dry-run --setting "x" --theme "y"`
- `run_studio.py status <production_id>`
- `run_studio.py list`
- `run_studio.py package <production_id> --format json --output file.json`
- Environment variables: `STUDIO_SETTING`, `STUDIO_THEME`, `STUDIO_N_CONCEPTS`, `STUDIO_BUDGET`
- Duplicate ID protection + `--force`

### 3.2 Zootopia 2 Creative DNA Extracted
**File:** `studio/memory/films_analyzed/zootopia2_dna.md` (12.6 KB, 216 lines)

Extracted from a 107-page Zootopia 2 Final Draft screenplay by Jared Bush.

**Contents:**
- All 15 Save the Cat beats with exact page ranges (p.1–107)
- 6 character archetypes with full voice dimensions (Sarcasm/Cynicism/Warmth/Formality/Verbosity/Subtext 0–100)
- Core Mechanism: A-story (mystery) + B-story (partnership therapy) + C-story (systemic erasure)
- Dialogue Craft Rules: callbacks, humor-as-defense, subtext, visual gags, wordplay, setup-punch
- Pacing Formula: minute-by-minute beat map
- Social Metaphor: prejudice as burial/historical erasure (not solved bias)
- Visual Style and Music Integration notes
- 6 Differentiation Seeds for concept generation

### 3.3 Skill Files Rewritten / Created

#### `studio/skills/story-structure.md` (REWRITTEN — 10.4 KB)
- Save the Cat beats with animation-specific notes
- B-Story mechanics (3-act substructure, must climax before A-story)
- C-Story mechanics (systemic/historical world story)
- Animation pacing rules: action every 8–12 min, emotional beat every 12–15 min, visual gag every 2–3 min
- Cold open and end credits as storytelling devices
- Common structure failures checklist

#### `studio/skills/character-design.md` (REWRITTEN — 13.9 KB)
- 5 archetypes from Zootopia 2: Nick (Cynical Trickster), Judy (Earnest Believer), Gary (Frightened Outsider), Pawbert (Meek Villain), Nibbles (Folksy Warrior)
- Each archetype: Surface/Truth, full 6-dimension voice profile, forbidden phrases, signature line patterns, physical comedy
- Relationship evolution rules: catchphrase evolution, midpoint fracture, mutual teaching, physical contrast
- Complete Voice Profile System with 6 dimensions defined at 0/50/100 scale

#### `studio/skills/dialogue-craft.md` (NEW — 11.6 KB)
- 10 professional dialogue rules with screenplay examples
- Subtext First (3-line deflection ladder)
- Callback Architecture (first appearance → second appearance table)
- Humor as Defense Mechanism
- Visual Gags in Directions
- Species/World-Specific Wordplay
- Setup-Punch Rhythm (3–5 line rule)
- Therapy Exercise Payoff (Act 2 comedy → Act 3 emotion)
- Emotional Climax Dialogue (hesitation → run-ons → self-deprecation → earned term)
- Villain Dialogue (familial language + self-awareness + belonging)
- Parenthetical Directions (approved patterns table)
- Dialogue metrics table and common failures checklist

### 3.4 ConceptGenerator Completely Rewritten
**File:** `system3/evolution_engine.py` (key methods replaced)

**Before:** 6 setting templates, 5 conflict templates, 6 archetype trios. Keyword substitution producing output like: *"When [setting] is rocked by a series of attacks, [protagonist] and [deuteragonist] form an unlikely alliance to find the truth."*

**After:**
- 12 setting templates with narrative specificity
- 10 conflict templates with emotional stakes (e.g., "mother's survival depends on proving the truth")
- 8 archetype trios with relationship mechanics (e.g., "humor_as_armor", "innocence_summons_magic")
- Archetype-specific character builders:
  - `_build_protagonist()`: 5 archetype profiles with specific emotional mechanics
  - `_build_deuteragonist()`: 5 archetype profiles that mirror/challenge the protagonist
  - `_build_antagonist()`: 4 archetype profiles for tragic villains
- 6 logline templates with specific stakes
- 3 templates per act (Act 1, Act 2A, Midpoint, Act 2B, Act 3) = 15 structure variations
- Pluralization fix: `_pluralize()` helper prevents "guardianss" / "alliess"
- `load_dna()` upgraded to parse hierarchical markdown (## sections → ### subsections)

### 3.5 WriterAgent Completely Rewritten
**File:** `system3/production_swarm.py` (key methods replaced)

**Before:** 5 generic scenes with hardcoded sluglines. Dialogue: "I must speak with you. It concerns a matter of some importance."

**After:**
- **8 beat-mapped scenes:** Opening Image, Catalyst, Debate/B-Story, Fun & Games, Midpoint, Bad Guys Close In, Dark Night of the Soul, Finale
- Each scene has beat-specific:
  - Visual/action opening (e.g., "OVER BLACK: A typewriter clacks.", "TIGHT ON: A broken toy.")
  - Camera directions and parentheticals
  - Closing visual (e.g., "SMASH CUT TO BLACK. A door slams.")
- `_generate_dialogue_exchange()`: Mini-exchanges (3–6 lines) with visual business, parentheticals, action beats
- `_get_exchange_pool()`: Beat-type + archetype-specific dialogue pools with **adapted lines from Zootopia 2**
- `_generate_dialogue_line()`: Archetype-specific pools (Cynical Trickster, Earnest Believer, Meek Villain, Frightened Outsider, Folksy Warrior) + fallback voice-dimension pools

---

## 4. TEST RESULTS

### 4.1 CLI Tests (All Passed)
| Test | Result |
|------|--------|
| `--version` | `0.2.0` ✅ |
| `--help` / subcommand helps | Clean, with examples ✅ |
| Missing required fields | Exit 3, clear error ✅ |
| Out-of-range values | Exit 3, clear error ✅ |
| Missing DNA file | Exit 3, path shown ✅ |
| Dry-run legacy usage | Works ✅ |
| Dry-run explicit `produce` | Works ✅ |
| JSON output to file | Valid JSON ✅ |
| Environment variables | Applied correctly ✅ |
| Debug verbose (`-vv`) | Dumps effective config ✅ |
| `list` command | Shows all productions ✅ |
| `status` command | Loads from vault ✅ |
| `package` command | Pretty + JSON formats ✅ |
| Duplicate ID protection | Blocks rerun, exit 1 ✅ |
| `--force` overwrite | Re-runs and succeeds ✅ |
| `--log-file` | Structured timestamps ✅ |

### 4.2 Full Pipeline Test: Ukrainian Fairy-Tale Concept
**Command:**
```bash
python run_studio.py \
  --dna "memory/films_analyzed/zootopia2_dna.md" \
  --setting "a Ukrainian borderland where old stories awaken when belief returns" \
  --group-a "Ukrainian guardians" \
  --group-b "Foreign fairy-tale allies" \
  --theme "a child's love can summon stories to shield what war threatens" \
  --metaphor "the girl's quest for her mother mirrors Ukraine's call for European solidarity" \
  --genre "metaphorical animated drama" \
  --n-concepts 2 \
  --production-id "ukraine-z2-test"
```

**Results:**
- Concepts generated: 2 (with specific emotional mechanics)
- Scenes produced: 8 (up from 5)
- Characters produced: 27 (with archetype-specific core wounds)
- Environments: 4
- Director Verdict: ITERATE (9.3/10) — theme flagged as absent from acts (known limitation)

**Sample output quality:**
- Scene 1: `OVER BLACK: A typewriter clacks. A beat. Then silence. TIGHT ON: A broken toy. A child's hand reaches for it.` → Dialogue: *"Blood, blood, blood and death..." / "Alright, you know you're milking it."*
- Midpoint: *"We did it. We actually did it." → "They lied to us. It's all a lie." → "You knew. You knew the whole time and you didn't tell me."* → `SMASH CUT TO BLACK. A door slams.`
- Finale: *"No one will believe you over us. We've always been better than you." → "Well... it matters to him." → "Shall we?"*

---

## 5. KNOWN ISSUES & LIMITATIONS

| Issue | Severity | Notes |
|-------|----------|-------|
| **Template-based generation** | High | Dialogue is adapted from Zootopia 2, not original. Need LLM integration for true originality. |
| **Theme absence in acts** | Medium | Director Agent flags theme as 0% in all acts. The scenes don't explicitly weave theme keywords. Need deeper theme integration in scene generation. |
| **Character name pools** | Low | Some names repeat across productions. Could expand pools further. |
| **LTM indexing fails** | Low | `sentence_transformers` not installed. Vector memory works when dependency is available. |
| **Title generation awkward** | Low | "Ukrainiborderland Calls" — key noun extraction needs polish. |
| **Action lines reuse structure text** | Medium | Some scenes paste the act summary into action lines instead of rewriting as visual direction. |
| **Image/video/audio is MOCK** | High | No real API keys wired. Returns mock URLs. Needs Phase D (Real Generation). |
| **Emotional arc misclassified** | Low | Emotional Model scores "Rags to Riches" for rescue/quest stories. Arc library needs quest pattern. |

---

## 6. FILE INVENTORY (Post-Session)

### Modified Files
```
run_studio.py                              ← COMPLETE REWRITE (v0.1.0 → v0.2.0)
system3/evolution_engine.py                ← ConceptGenerator rewritten
system3/production_swarm.py                ← WriterAgent rewritten
studio/skills/story-structure.md           ← REWRITTEN
studio/skills/character-design.md          ← REWRITTEN
```

### New Files
```
studio/memory/films_analyzed/zootopia2_dna.md   ← NEW (12.6 KB)
studio/skills/dialogue-craft.md                  ← NEW (11.6 KB)
studio/memory/checkpoints/CHECKPOINT_2026-06-02.md  ← THIS FILE
```

### Untouched (Still Working)
```
api/server.py
api/models.py
frontend/index.html
frontend/static/app.js
frontend/static/styles.css
system3/evolution_controller.py
system4/*.py (all 6 modules)
bridge/*.py (all 3 modules)
config/studio.yaml
```

---

## 7. NEXT STEPS (What To Do Tomorrow)

### Option A: LLM Integration (Highest Impact)
Wire Claude/GPT-4 into the WriterAgent and ConceptGenerator so templates become *few-shot examples* rather than content sources.
- Add API key config to `.env`
- Replace `_generate_dialogue_line()` with LLM prompt using voice profile + skill files as system prompt
- Replace `_generate_single_concept()` with LLM prompt using DNA + constraints
- Keep template output as fallback if LLM unavailable

### Option B: Theme Integration (Medium Impact)
Fix the Director Agent's theme flag by weaving theme keywords into every scene:
- Add `theme_keywords` field to Concept
- Modify WriterAgent to inject theme into action lines and dialogue subtext
- Add theme density checker to CriticSwarm

### Option C: Custom DNA for User's Project (Immediate Value)
Create a dedicated Creative DNA for the Ukrainian fairy-tale concept:
- Extract structure from Pan's Labyrinth / Spirited Away (quest films, not buddy-cop)
- Write `ukrainian_quest_dna.md` with Hero's Journey beats
- Add fairy-tale ally archetypes (Swiss gnome, French poodle, German woodsman, English knight, American cowboy)
- Test with this DNA to see if quest structure fits better than Zootopia 2's buddy-cop structure

### Option D: Real Generation (Long-Term)
Wire actual API keys for image/video/audio generation (Phase D from AGENTS.md).
- Kling API key → video generation
- Suno API key → music generation
- Flux/Stable Diffusion API key → concept art

### Recommended Order
1. **C** — Custom DNA for Ukrainian fairy-tale (1 hour, immediate storytelling improvement)
2. **B** — Theme integration (2 hours, fixes Director Agent flags)
3. **A** — LLM integration (half day, transforms quality from 40% → 80%)
4. **D** — Real generation (full day, makes tangible media)

---

## 8. HOW TO ACTIVATE THE ENVIRONMENT

```bash
cd /Users/dmytrnewaimastery/Documents/AI\ Agents\ Test
source openmontage/venv/bin/activate
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

---

## 9. KEY COMMANDS FOR TOMORROW

```bash
# Quick test with new DNA
python run_studio.py --dry-run \
  --dna "memory/films_analyzed/zootopia2_dna.md" \
  --setting "YOUR SETTING" \
  --group-a "GROUP A" --group-b "GROUP B" \
  --theme "YOUR THEME"

# Full production
python run_studio.py \
  --dna "memory/films_analyzed/zootopia2_dna.md" \
  --setting "YOUR SETTING" \
  --theme "YOUR THEME" \
  --n-concepts 4 --n-rounds 1 \
  --production-id "your-film-001"

# Check results
python run_studio.py status your-film-001
python run_studio.py package your-film-001 --format markdown --output result.md
```

---

*End of checkpoint. All systems operational.*
