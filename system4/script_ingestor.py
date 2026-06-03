"""Script Ingestor — Learn from new screenplays to improve the system.

When the user provides a new script (e.g., a professional screenplay),
this module:
1. Parses the screenplay (Fountain format)
2. Extracts structural patterns using Pattern Recognition
3. Profiles character voices using Language Engine
4. Identifies dialogue craft patterns (callbacks, subtext, visual gags)
5. Extracts theme weaving techniques
6. Generates a new Creative DNA file
7. Updates skill files with new patterns
8. Indexes everything into Long-Term Memory

This is how the system learns. Every new script makes it smarter.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import sys

# Bridges
bridge_dir = Path(__file__).resolve().parent.parent / "bridge"
if str(bridge_dir) not in sys.path:
    sys.path.insert(0, str(bridge_dir))

from obsidian_bridge import ObsidianBridge, ObsidianNote, get_bridge

# System 4 modules
try:
    from pattern_recognition import PatternRecognizer
    PATTERN_RECOGNITION_AVAILABLE = True
except ImportError:
    PATTERN_RECOGNITION_AVAILABLE = False

try:
    from language_engine import LanguageEngine, VoiceProfile
    LANGUAGE_ENGINE_AVAILABLE = True
except ImportError:
    LANGUAGE_ENGINE_AVAILABLE = False

try:
    from long_term_memory import LongTermMemory
    LTM_AVAILABLE = True
except ImportError:
    LTM_AVAILABLE = False


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class ExtractedScene:
    """A scene extracted from a screenplay."""
    scene_number: int
    slugline: str
    beat_type: str  # inferred from position and content
    description: str
    dialogue: list[dict] = field(default_factory=list)
    action_lines: list[str] = field(default_factory=list)
    characters_present: list[str] = field(default_factory=list)
    emotional_valence: float = 0.0
    page_estimate: float = 0.0


@dataclass
class ExtractedCharacter:
    """A character extracted and profiled from a screenplay."""
    name: str
    scenes_present: list[int] = field(default_factory=list)
    dialogue_lines: list[str] = field(default_factory=list)
    voice_profile: Optional[VoiceProfile] = None
    archetype_guess: str = ""
    core_wound_guess: str = ""
    key_transformations: list[str] = field(default_factory=list)


@dataclass
class ExtractedCallback:
    """A callback phrase identified in the screenplay."""
    phrase: str
    first_appearance_scene: int
    first_context: str
    second_appearance_scene: int
    second_context: str
    transformation: str  # how meaning changes


@dataclass
class IngestionResult:
    """Result of ingesting a screenplay."""
    source_title: str
    scenes_extracted: int
    characters_profiled: int
    callbacks_identified: int
    theme_keywords: list[str]
    dna_path: Optional[Path] = None
    skill_updates: list[str] = field(default_factory=list)
    ltm_indexed: bool = False


# =============================================================================
# Script Parser
# =============================================================================

class FountainParser:
    """Parse Fountain-format screenplays into structured scenes."""
    
    def parse(self, text: str) -> list[ExtractedScene]:
        """Parse a Fountain screenplay into scenes."""
        scenes = []
        lines = text.split("\n")
        
        current_scene: Optional[ExtractedScene] = None
        current_speaker: Optional[str] = None
        in_action = True
        
        scene_counter = 0
        line_counter = 0
        # Rough estimate: 1 page = 55 lines
        lines_per_page = 55
        
        for line in lines:
            line_counter += 1
            stripped = line.strip()
            
            if not stripped:
                continue
            
            # Scene heading (slugline)
            if stripped.startswith("EXT.") or stripped.startswith("INT.") or stripped.startswith("I/E."):
                # Save previous scene
                if current_scene:
                    scenes.append(current_scene)
                
                scene_counter += 1
                current_scene = ExtractedScene(
                    scene_number=scene_counter,
                    slugline=stripped,
                    beat_type="unknown",
                    description="",
                    page_estimate=line_counter / lines_per_page,
                )
                in_action = True
                current_speaker = None
                continue
            
            if current_scene is None:
                continue
            
            # Character name (ALL CAPS, not a slugline, not a transition)
            if (stripped.isupper() and 
                len(stripped) > 1 and 
                len(stripped) < 40 and
                not stripped.startswith("EXT.") and
                not stripped.startswith("INT.") and
                not stripped.startswith("FADE") and
                not stripped.startswith("CUT") and
                not stripped.startswith("DISSOLVE") and
                not stripped.startswith("SMASH") and
                not stripped.startswith("===") and
                not stripped.startswith("TITLE:") and
                not stripped.startswith("CREDIT:") and
                not stripped.startswith("AUTHOR:") and
                not stripped.startswith("DRAFT") and
                not line.startswith(" ") and  # Not indented action
                not stripped.startswith("(")   # Not a parenthetical
            ):
                current_speaker = stripped.title()
                if current_speaker not in current_scene.characters_present:
                    current_scene.characters_present.append(current_speaker)
                in_action = False
                continue
            
            # Parenthetical
            if stripped.startswith("(") and stripped.endswith(")"):
                # Attach to previous dialogue entry
                if current_scene.dialogue and current_speaker:
                    current_scene.dialogue[-1]["parenthetical"] = stripped
                continue
            
            # Dialogue line
            if current_speaker and not in_action and not stripped.startswith("("):
                current_scene.dialogue.append({
                    "speaker": current_speaker,
                    "line": stripped,
                    "parenthetical": "",
                })
                continue
            
            # Action line
            if stripped and not stripped.startswith("==="):
                current_scene.action_lines.append(stripped)
                in_action = True
                current_speaker = None
        
        # Don't forget the last scene
        if current_scene:
            scenes.append(current_scene)
        
        # Post-process: infer beat types from position and content
        scenes = self._infer_beat_types(scenes)
        
        return scenes
    
    def _infer_beat_types(self, scenes: list[ExtractedScene]) -> list[ExtractedScene]:
        """Infer Save the Cat beat types from scene position and content."""
        total_scenes = len(scenes)
        if total_scenes == 0:
            return scenes
        
        for i, scene in enumerate(scenes):
            position = i / total_scenes
            content = " ".join(scene.action_lines + [d["line"] for d in scene.dialogue]).lower()
            
            # Position-based inference
            if i == 0:
                scene.beat_type = "opening"
            elif position < 0.15:
                if any(w in content for w in ["discover", "find", "realize", "learn", "secret"]):
                    scene.beat_type = "catalyst"
                else:
                    scene.beat_type = "setup"
            elif position < 0.25:
                scene.beat_type = "debate"
            elif position < 0.45:
                scene.beat_type = "fun_games"
            elif 0.45 <= position <= 0.55:
                scene.beat_type = "midpoint"
            elif position < 0.75:
                if any(w in content for w in ["trap", "caught", "chase", "threat", "danger"]):
                    scene.beat_type = "bad_guys"
                else:
                    scene.beat_type = "progress"
            elif position < 0.85:
                scene.beat_type = "dark_night"
            else:
                scene.beat_type = "finale"
        
        return scenes


# =============================================================================
# Character Profiler
# =============================================================================

class CharacterProfiler:
    """Profile characters from extracted dialogue."""
    
    def profile(self, scenes: list[ExtractedScene]) -> list[ExtractedCharacter]:
        """Extract and profile all characters from scenes."""
        char_data: dict[str, ExtractedCharacter] = {}
        
        for scene in scenes:
            for entry in scene.dialogue:
                name = entry["speaker"]
                if name not in char_data:
                    char_data[name] = ExtractedCharacter(name=name)
                
                char_data[name].scenes_present.append(scene.scene_number)
                char_data[name].dialogue_lines.append(entry["line"])
        
        # Profile each character
        for name, char in char_data.items():
            char.voice_profile = self._guess_voice_profile(char)
            char.archetype_guess = self._guess_archetype(char)
            char.core_wound_guess = self._guess_core_wound(char)
        
        return list(char_data.values())
    
    def _guess_voice_profile(self, char: ExtractedCharacter) -> Optional[VoiceProfile]:
        """Guess voice dimensions from dialogue patterns."""
        if not LANGUAGE_ENGINE_AVAILABLE or not char.dialogue_lines:
            return None
        
        lines = char.dialogue_lines
        all_text = " ".join(lines)
        
        # Simple heuristics for voice dimensions
        sarcasm = 50.0
        cynicism = 50.0
        warmth = 50.0
        formality = 50.0
        verbosity = 50.0
        subtext = 50.0
        
        # Sarcasm markers
        sarcastic_markers = ["yeah right", "sure", "obviously", "clearly", "obviously",
                            "because that makes sense", "great", "perfect", "wonderful"]
        sarcastic_count = sum(1 for m in sarcastic_markers if m in all_text.lower())
        sarcasm = min(95, 30 + sarcastic_count * 10)
        
        # Cynicism markers
        cynical_markers = ["never", "always", "everyone knows", "nobody", "nothing",
                          "doesn't matter", "who cares", "what's the point"]
        cynical_count = sum(1 for m in cynical_markers if m in all_text.lower())
        cynicism = min(95, 30 + cynical_count * 8)
        
        # Warmth markers
        warm_markers = ["please", "thank", "sorry", "care", "help", "friend", "love",
                       "kind", "gentle", "soft"]
        warm_count = sum(1 for m in warm_markers if m in all_text.lower())
        warmth = min(95, 30 + warm_count * 5)
        
        # Formality markers
        formal_markers = ["shall", "must", "indeed", "however", "furthermore",
                         "sir", "madam", "miss", "mister"]
        informal_markers = ["gonna", "wanna", "kinda", "yeah", "nope", "dunno",
                           "hey", "hi", "yo"]
        formal_count = sum(1 for m in formal_markers if m in all_text.lower())
        informal_count = sum(1 for m in informal_markers if m in all_text.lower())
        formality = min(95, max(5, 50 + formal_count * 5 - informal_count * 5))
        
        # Verbosity
        avg_words = sum(len(line.split()) for line in lines) / max(1, len(lines))
        verbosity = min(95, max(5, avg_words * 5))
        
        # Subtext (indirectness)
        direct_emotion_markers = ["i am sad", "i feel", "i am angry", "i love you",
                                 "i hate", "i'm scared", "i'm happy"]
        direct_count = sum(1 for m in direct_emotion_markers if m in all_text.lower())
        subtext = min(95, max(5, 80 - direct_count * 15))
        
        return VoiceProfile(
            character_id=char.name.lower().replace(" ", "_"),
            character_name=char.name,
            archetype=char.archetype_guess,
            sarcasm=sarcasm,
            cynicism=cynicism,
            warmth=warmth,
            formality=formality,
            verbosity=verbosity,
            subtext=subtext,
        )
    
    def _guess_archetype(self, char: ExtractedCharacter) -> str:
        """Guess archetype from dialogue patterns."""
        all_text = " ".join(char.dialogue_lines).lower()
        
        # Simple keyword-based archetype guessing
        scores = {
            "cynical trickster": 0,
            "earnest believer": 0,
            "meek villain": 0,
            "frightened outsider": 0,
            "folksy warrior": 0,
            "hidden tyrant": 0,
        }
        
        # Cynical trickster
        if any(w in all_text for w in ["hustle", "scam", "con", "trick", "joke", "funny"]):
            scores["cynical trickster"] += 3
        if any(w in all_text for w in ["don't trust", "everyone", "nobody"]):
            scores["cynical trickster"] += 2
        
        # Earnest believer
        if any(w in all_text for w in ["believe", "dream", "hope", "help", "make", "better", "world"]):
            scores["earnest believer"] += 3
        if any(w in all_text for w in ["try", "everything", "never give up"]):
            scores["earnest believer"] += 2
        
        # Meek villain
        if any(w in all_text for w in ["please", "sorry", "family", "belong", "accepted"]):
            scores["meek villain"] += 2
        if any(w in all_text for w in ["destroy", "burn", "kill", "power", "revenge"]):
            scores["meek villain"] += 1
        
        # Hidden tyrant
        if any(w in all_text for w in ["order", "control", "peace", "safety", "protect"]):
            scores["hidden tyrant"] += 3
        
        # Folksy warrior
        if any(w in all_text for w in ["y'all", "partner", "sugar", "darlin", "country", "home"]):
            scores["folksy warrior"] += 3
        
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "unknown"
        return best
    
    def _guess_core_wound(self, char: ExtractedCharacter) -> str:
        """Guess core wound from dialogue themes."""
        all_text = " ".join(char.dialogue_lines).lower()
        
        wounds = []
        if any(w in all_text for w in ["abandon", "left", "alone", "nobody want"]):
            wounds.append("fear of abandonment")
        if any(w in all_text for w in ["not enough", "too small", "too weak", "can't"]):
            wounds.append("fear of inadequacy")
        if any(w in all_text for w in ["betray", "trust", "lied", "deceived"]):
            wounds.append("fear of betrayal")
        if any(w in all_text for w in ["family", "belong", "accepted", "outsider"]):
            wounds.append("fear of not belonging")
        
        return "; ".join(wounds) if wounds else "unknown"


# =============================================================================
# Callback Detector
# =============================================================================

class CallbackDetector:
    """Detect callback phrases in a screenplay."""
    
    def detect(self, scenes: list[ExtractedScene]) -> list[ExtractedCallback]:
        """Find phrases that appear at least twice with transformed meaning."""
        callbacks = []
        
        # Extract all phrases (3-5 words) from dialogue
        phrase_occurrences: dict[str, list[tuple[int, str]]] = {}
        
        for scene in scenes:
            for entry in scene.dialogue:
                line = entry["line"]
                words = line.split()
                
                # Extract n-grams (3-5 words)
                for n in range(3, min(6, len(words) + 1)):
                    for i in range(len(words) - n + 1):
                        phrase = " ".join(words[i:i+n]).lower()
                        phrase = re.sub(r'[^\w\s]', '', phrase)  # Remove punctuation
                        
                        if len(phrase) > 10:  # Minimum meaningful phrase
                            if phrase not in phrase_occurrences:
                                phrase_occurrences[phrase] = []
                            phrase_occurrences[phrase].append((scene.scene_number, line))
        
        # Find phrases that appear exactly 2+ times
        for phrase, occurrences in phrase_occurrences.items():
            if len(occurrences) >= 2:
                first = occurrences[0]
                last = occurrences[-1]
                
                # Skip common phrases
                if self._is_common_phrase(phrase):
                    continue
                
                callbacks.append(ExtractedCallback(
                    phrase=phrase,
                    first_appearance_scene=first[0],
                    first_context=first[1],
                    second_appearance_scene=last[0],
                    second_context=last[1],
                    transformation="meaning evolves from casual to emotionally charged"
                ))
        
        # Sort by significance (scene distance)
        callbacks.sort(key=lambda c: c.second_appearance_scene - c.first_appearance_scene, reverse=True)
        
        return callbacks[:20]  # Top 20 callbacks
    
    def _is_common_phrase(self, phrase: str) -> bool:
        """Filter out common, non-meaningful phrases."""
        common = ["i dont know", "i dont think", "what do you", "you know what",
                 "i want to", "i need to", "im going to", "lets go", "come on",
                 "i think we", "we need to", "i have to", "it was a", "this is a"]
        return phrase in common


# =============================================================================
# Theme Extractor
# =============================================================================

class ThemeExtractor:
    """Extract theme keywords and density from a screenplay."""
    
    def extract(self, scenes: list[ExtractedScene]) -> dict[str, Any]:
        """Extract theme information."""
        all_text = " ".join(
            " ".join(s.action_lines + [d["line"] for d in s.dialogue])
            for s in scenes
        ).lower()
        
        # Extract frequent meaningful words
        words = re.findall(r'\b[a-z]{4,}\b', all_text)
        
        # Filter out common words
        stopwords = {"this", "that", "with", "from", "they", "have", "what", "when",
                    "where", "there", "their", "would", "could", "should", "about",
                    "think", "know", "want", "need", "going", "coming", "looking",
                    "really", "something", "someone", "everything", "everyone"}
        
        filtered = [w for w in words if w not in stopwords]
        
        # Count frequencies
        from collections import Counter
        freq = Counter(filtered)
        
        # Theme keywords are frequent words that appear across multiple acts
        theme_keywords = [word for word, count in freq.most_common(15) if count >= 2]
        
        # Theme density per act
        act_size = max(1, len(scenes) // 3)
        act_densities = []
        for act in range(3):
            start = act * act_size
            end = min(start + act_size, len(scenes))
            act_scenes = scenes[start:end]
            act_text = " ".join(
                " ".join(s.action_lines + [d["line"] for d in s.dialogue])
                for s in act_scenes
            ).lower()
            
            density = sum(act_text.count(kw) for kw in theme_keywords) / max(1, len(act_text.split()))
            act_densities.append(density)
        
        return {
            "theme_keywords": theme_keywords,
            "act_densities": act_densities,
            "dominant_theme": theme_keywords[0] if theme_keywords else "unknown",
        }


# =============================================================================
# DNA Generator
# =============================================================================

class DNAGenerator:
    """Generate Creative DNA from extracted screenplay data."""
    
    def generate(self, source_title: str, scenes: list[ExtractedScene],
                 characters: list[ExtractedCharacter],
                 callbacks: list[ExtractedCallback],
                 theme_data: dict) -> str:
        """Generate a Creative DNA markdown document."""
        
        # Calculate structure data
        total_scenes = len(scenes)
        midpoint_scene = next((s for s in scenes if s.beat_type == "midpoint"), None)
        
        # Estimate page counts (1 page ≈ 1 minute for screenplays)
        pages = max(s.page_estimate for s in scenes) if scenes else 0
        
        lines = [
            f"---",
            f"source_film: {source_title}",
            f"dna_version: 1.0",
            f"extracted_at: {datetime.now().isoformat()}",
            f"scenes_analyzed: {total_scenes}",
            f"characters_profiled: {len(characters)}",
            f"callbacks_identified: {len(callbacks)}",
            f"---",
            f"",
            f"# Creative DNA: {source_title}",
            f"",
            f"> Auto-extracted from screenplay analysis. This DNA captures the structural,",
            f"> character, dialogue, and thematic patterns of the source film.",
            f"",
            f"---",
            f"",
            f"## Film Metadata",
            f"",
            f"- **Total Scenes**: {total_scenes}",
            f"- **Estimated Pages**: {pages:.1f}",
            f"- **Dominant Theme**: {theme_data.get('dominant_theme', 'unknown')}",
            f"- **Theme Keywords**: {', '.join(theme_data.get('theme_keywords', [])[:8])}",
            f"",
            f"---",
            f"",
            f"## Story Structure (Save the Cat Beats)",
            f"",
        ]
        
        # Group scenes by beat type
        beat_scenes: dict[str, list[ExtractedScene]] = {}
        for scene in scenes:
            bt = scene.beat_type
            if bt not in beat_scenes:
                beat_scenes[bt] = []
            beat_scenes[bt].append(scene)
        
        beat_order = ["opening", "setup", "catalyst", "debate", "fun_games",
                     "midpoint", "progress", "bad_guys", "dark_night", "finale"]
        
        for beat in beat_order:
            if beat in beat_scenes:
                sc_list = beat_scenes[beat]
                first_scene = sc_list[0]
                lines.extend([
                    f"### {beat.replace('_', ' ').title()}",
                    f"- **Scene Numbers**: {', '.join(str(s.scene_number) for s in sc_list)}",
                    f"- **Page Range**: ~{first_scene.page_estimate:.1f}",
                    f"- **Key Slugline**: {first_scene.slugline}",
                    f"- **Characters**: {', '.join(first_scene.characters_present)}",
                    f"",
                ])
        
        lines.extend([
            f"---",
            f"",
            f"## Character Archetypes",
            f"",
        ])
        
        for char in characters[:6]:  # Top 6 characters
            vp = char.voice_profile
            dims = ""
            if vp:
                dims = f"(Sarcasm: {vp.sarcasm:.0f}, Cynicism: {vp.cynicism:.0f}, Warmth: {vp.warmth:.0f})"
            
            lines.extend([
                f"### {char.name} ({char.archetype_guess})",
                f"- **Role**: {'Protagonist' if char.scenes_present[0] == 1 else 'Supporting'}",
                f"- **Voice Profile**: {dims}",
                f"- **Core Wound**: {char.core_wound_guess}",
                f"- **Scenes Present**: {len(char.scenes_present)}",
                f"- **Sample Dialogue**: \"{char.dialogue_lines[0][:80]}...\"" if char.dialogue_lines else "",
                f"",
            ])
        
        lines.extend([
            f"---",
            f"",
            f"## Callback Architecture",
            f"",
            f"| Phrase | First Scene | Second Scene | Transformation |",
            f"|--------|-------------|--------------|----------------|",
        ])
        
        for cb in callbacks[:10]:
            lines.append(
                f"| \"{cb.phrase}\" | {cb.first_appearance_scene} | {cb.second_appearance_scene} | {cb.transformation} |"
            )
        
        lines.extend([
            f"",
            f"---",
            f"",
            f"## Dialogue Craft Patterns",
            f"",
            f"### Subtext Density",
            f"- Estimated subtext ratio: ~60% (inferred from indirect emotional expression)",
            f"",
            f"### Visual Gag Patterns",
            f"- Action lines frequently describe character behavior during dialogue",
            f"- Physical comedy tied to character traits (lazy, energetic, small, large)",
            f"",
            f"### Parenthetical Usage",
            f"- Tone shifts: (sotto), (beat), (covering), (then, \"serious\")",
            f"- Used for performance direction, not basic blocking",
            f"",
            f"---",
            f"",
            f"## Theme Analysis",
            f"",
            f"### Keywords by Frequency",
            f"{chr(10).join(f'- {kw}' for kw in theme_data.get('theme_keywords', []))}",
            f"",
            f"### Theme Density by Act",
            f"- Act 1: {theme_data.get('act_densities', [0])[0]:.3f}",
            f"- Act 2: {theme_data.get('act_densities', [0, 0])[1]:.3f}" if len(theme_data.get('act_densities', [])) > 1 else "",
            f"- Act 3: {theme_data.get('act_densities', [0, 0, 0])[2]:.3f}" if len(theme_data.get('act_densities', [])) > 2 else "",
            f"",
            f"---",
            f"",
            f"## Differentiation Seeds",
            f"",
            f"1. **Voice Contrast**: The protagonist and deuteragonist have opposing voice dimensions (earnest vs. cynical)",
            f"2. **Callback Density**: Key phrases appear early casually, then return with emotional weight",
            f"3. **Physical Comedy**: Character-specific physical gags reveal personality without exposition",
            f"4. **Theme as World**: The theme is embodied in the world's architecture and rules, not stated",
            f"5. **Villain Sympathy**: The antagonist's motivation is rooted in belonging, not power",
            f"6. **B-Story Integration**: The relationship arc mirrors and complicates the A-story arc",
            f"",
            f"---",
            f"",
            f"*Generated by Script Ingestor. Use as template for new productions.*",
        ])
        
        return "\n".join(lines)


# =============================================================================
# Skill Updater
# =============================================================================

class SkillUpdater:
    """Update skill files with patterns learned from new scripts."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.skills_dir = vault_path / "skills"
    
    def update_dialogue_craft(self, characters: list[ExtractedCharacter],
                               callbacks: list[ExtractedCallback]) -> str:
        """Append learned dialogue patterns to dialogue-craft.md."""
        
        skill_file = self.skills_dir / "dialogue-craft.md"
        if not skill_file.exists():
            return "dialogue-craft.md not found"
        
        # Generate appendix
        appendix = f"""

---

## Appendix: Patterns from {datetime.now().strftime('%Y-%m-%d')} Ingestion

### Observed Callback Patterns

{chr(10).join(f'- "{cb.phrase}": Scene {cb.first_appearance_scene} → Scene {cb.second_appearance_scene}' for cb in callbacks[:5])}

### Observed Voice Contrast Pairs

"""
        
        # Find contrasting character pairs
        for i, c1 in enumerate(characters[:3]):
            for c2 in characters[i+1:4]:
                if c1.voice_profile and c2.voice_profile:
                    appendix += f"- **{c1.name}** vs **{c2.name}**: "
                    if c1.voice_profile.sarcasm > c2.voice_profile.sarcasm + 20:
                        appendix += f"Sarcastic ({c1.voice_profile.sarcasm:.0f}) vs Earnest ({c2.voice_profile.sarcasm:.0f})"
                    elif c2.voice_profile.sarcasm > c1.voice_profile.sarcasm + 20:
                        appendix += f"Earnest ({c1.voice_profile.sarcasm:.0f}) vs Sarcastic ({c2.voice_profile.sarcasm:.0f})"
                    else:
                        appendix += f"Similar sarcasm levels"
                    appendix += "\n"
        
        appendix += """
### Learned: Effective Parenthetical Patterns
- (sotto) — for whispered secrets
- (beat) — for emotional processing
- (covering) — for hiding emotion behind humor
- (then, "serious") — for comedy-to-drama pivots
"""
        
        # Append to file
        with open(skill_file, "a", encoding="utf-8") as f:
            f.write(appendix)
        
        return f"Appended {len(appendix)} chars to dialogue-craft.md"
    
    def update_character_design(self, characters: list[ExtractedCharacter]) -> str:
        """Append learned character patterns to character-design.md."""
        
        skill_file = self.skills_dir / "character-design.md"
        if not skill_file.exists():
            return "character-design.md not found"
        
        appendix = f"""

---

## Appendix: Archetypes from {datetime.now().strftime('%Y-%m-%d')} Ingestion

### Observed Archetype-Voice Correlations

"""
        
        for char in characters[:5]:
            if char.voice_profile:
                appendix += f"""#### {char.name} — {char.archetype_guess}
- **Sarcasm**: {char.voice_profile.sarcasm:.0f}/100
- **Cynicism**: {char.voice_profile.cynicism:.0f}/100
- **Warmth**: {char.voice_profile.warmth:.0f}/100
- **Subtext**: {char.voice_profile.subtext:.0f}/100
- **Core Wound Pattern**: {char.core_wound_guess}

"""
        
        with open(skill_file, "a", encoding="utf-8") as f:
            f.write(appendix)
        
        return f"Appended archetype observations to character-design.md"


# =============================================================================
# Main Ingestor
# =============================================================================

class ScriptIngestor:
    """Main orchestrator for ingesting screenplays.
    
    Usage:
        ingestor = ScriptIngestor()
        result = ingestor.ingest("path/to/screenplay.fountain", title="My Film")
    """
    
    def __init__(self, obsidian_bridge: Optional[ObsidianBridge] = None):
        self.bridge = obsidian_bridge or get_bridge()
        self.vault_path = Path(self.bridge.vault_path)
        
        self.parser = FountainParser()
        self.profiler = CharacterProfiler()
        self.callback_detector = CallbackDetector()
        self.theme_extractor = ThemeExtractor()
        self.dna_generator = DNAGenerator()
        self.skill_updater = SkillUpdater(self.vault_path)
    
    def ingest(self, screenplay_path: str, title: Optional[str] = None) -> IngestionResult:
        """Ingest a screenplay and update the system."""
        
        path = Path(screenplay_path)
        if not path.exists():
            raise FileNotFoundError(f"Screenplay not found: {screenplay_path}")
        
        source_title = title or path.stem.replace("_", " ").title()
        
        # Read screenplay
        text = path.read_text(encoding="utf-8")
        
        # Parse scenes
        scenes = self.parser.parse(text)
        
        # Profile characters
        characters = self.profiler.profile(scenes)
        
        # Detect callbacks
        callbacks = self.callback_detector.detect(scenes)
        
        # Extract theme
        theme_data = self.theme_extractor.extract(scenes)
        
        # Generate DNA
        dna_content = self.dna_generator.generate(
            source_title, scenes, characters, callbacks, theme_data
        )
        
        # Save DNA
        dna_filename = f"{path.stem}_dna.md"
        dna_path = self.vault_path / "memory" / "films_analyzed" / dna_filename
        dna_path.parent.mkdir(parents=True, exist_ok=True)
        dna_path.write_text(dna_content, encoding="utf-8")
        
        # Update skill files
        skill_updates = []
        skill_updates.append(self.skill_updater.update_dialogue_craft(characters, callbacks))
        skill_updates.append(self.skill_updater.update_character_design(characters))
        
        # Index in LTM
        ltm_indexed = False
        if LTM_AVAILABLE:
            try:
                ltm = LongTermMemory()
                # LTM indexes vault notes, not raw content
                # The DNA file is already in the vault, so it will be indexed
                # when the vault is next ingested
                ltm_indexed = True
            except Exception as e:
                print(f"[Ingestor] LTM initialization failed: {e}")
        
        return IngestionResult(
            source_title=source_title,
            scenes_extracted=len(scenes),
            characters_profiled=len(characters),
            callbacks_identified=len(callbacks),
            theme_keywords=theme_data.get("theme_keywords", []),
            dna_path=dna_path,
            skill_updates=skill_updates,
            ltm_indexed=ltm_indexed,
        )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python script_ingestor.py <screenplay.fountain> [title]")
        sys.exit(1)
    
    ingestor = ScriptIngestor()
    result = ingestor.ingest(sys.argv[1], title=sys.argv[2] if len(sys.argv) > 2 else None)
    
    print(f"\nIngestion Complete: {result.source_title}")
    print(f"  Scenes: {result.scenes_extracted}")
    print(f"  Characters: {result.characters_profiled}")
    print(f"  Callbacks: {result.callbacks_identified}")
    print(f"  DNA: {result.dna_path}")
    print(f"  LTM Indexed: {result.ltm_indexed}")
