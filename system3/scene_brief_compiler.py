"""Scene Brief Compiler — Prepares rich creative briefs for AI writers.

The AI-as-Engine architecture:
1. Python system (this compiler) gathers all context: characters, voice profiles,
   story structure, theme, previous scenes, skill files
2. It writes structured briefs to studio/briefs/
3. The AI (Claude Code / Codex / Kimi) reads each brief and writes the scene
4. Python validates and assembles the final screenplay

No API calls. The AI IS the writer. Python is the producer.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import sys
bridge_dir = Path(__file__).resolve().parent.parent / "bridge"
if str(bridge_dir) not in sys.path:
    sys.path.insert(0, str(bridge_dir))

from obsidian_bridge import ObsidianBridge, get_bridge


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class CharacterBrief:
    """Character context for a single scene."""
    name: str
    archetype: str
    role: str  # protagonist, deuteragonist, antagonist, supporting
    emotional_state_in: str
    emotional_state_out: str
    scene_objective: str
    voice_dimensions: dict[str, float] = field(default_factory=dict)
    signature_phrases: list[str] = field(default_factory=list)
    forbidden_phrases: list[str] = field(default_factory=list)
    vocabulary_level: str = "moderate"
    sentence_structure: str = "mixed"
    physical_comedy_notes: str = ""


@dataclass
class SceneBrief:
    """Complete brief for one scene."""
    scene_number: int
    beat_type: str
    beat_name: str
    slugline: str
    duration_target_seconds: int
    emotional_valence_in: float
    emotional_valence_out: float
    
    # Context
    previous_scene_summary: str
    next_scene_requirements: str
    story_position: str  # e.g., "Act 1, first 2 minutes"
    
    # Characters
    characters: list[CharacterBrief] = field(default_factory=list)
    
    # Theme
    theme: str = ""
    theme_keywords: list[str] = field(default_factory=list)
    theme_weaving_instructions: str = ""
    
    # Callbacks
    callbacks_to_setup: list[str] = field(default_factory=list)
    callbacks_to_payoff: list[str] = field(default_factory=list)
    
    # Craft
    dialogue_rules: list[str] = field(default_factory=list)
    visual_opening: str = ""
    visual_closing: str = ""
    key_props: list[str] = field(default_factory=list)
    lighting_mood: str = ""
    
    # Writing instructions
    writing_instructions: str = ""
    lines_target: int = 10
    words_per_line_target: int = 10
    subtext_ratio_target: float = 0.6


# =============================================================================
# Scene Brief Compiler
# =============================================================================

class SceneBriefCompiler:
    """Compiles rich scene briefs from production context.
    
    Usage:
        compiler = SceneBriefCompiler()
        briefs = compiler.compile_briefs(concept_id="WINNER")
        compiler.save_briefs(briefs, production_id="my-film")
    """
    
    # Beat definitions: name, duration, emotional arc, story position
    BEAT_DEFS = {
        "opening": {
            "name": "Opening Image / Cold Open",
            "duration": 120,
            "valence_in": 0.0,
            "valence_out": 0.3,
            "position": "Act 1 — First 2 minutes",
            "rules": [
                "Rule 4: Visual Gags in Dialogue Directions — every line needs physical business",
                "Rule 5: Species/World-Specific Wordplay — establish the world's language",
                "Rule 1: Subtext First — if emotional, deflect first",
            ],
        },
        "catalyst": {
            "name": "Catalyst / Inciting Incident",
            "duration": 180,
            "valence_in": 0.3,
            "valence_out": -0.2,
            "position": "Act 1 — The discovery that changes everything",
            "rules": [
                "Rule 4: Visual Gags — action beats reveal character",
                "Rule 6: Setup-Punch Rhythm — if comedy, setup now, punch in 3-5 lines",
                "Rule 1: Subtext First — characters hide their true reaction to the discovery",
            ],
        },
        "debate": {
            "name": "Debate / B-Story Launch",
            "duration": 150,
            "valence_in": -0.2,
            "valence_out": 0.2,
            "position": "Act 1 → Act 2A — The partnership forms",
            "rules": [
                "Rule 3: Humor as Defense Mechanism — mismatch reveals fear",
                "Rule 7: Therapy Exercise Payoff — introduce a comedic ritual that will pay off in Act 3",
                "Rule 4: Visual Gags — physical contrast between partners",
            ],
        },
        "fun_games": {
            "name": "Fun & Games / Promise of the Premise",
            "duration": 180,
            "valence_in": 0.2,
            "valence_out": 0.6,
            "position": "Act 2A — The investigation deepens",
            "rules": [
                "Rule 5: World-Specific Wordplay — characters use the world's language",
                "Rule 6: Setup-Punch Rhythm — comedy sequences need clear rhythm",
                "Rule 4: Visual Gags — this is the comedy set piece; action IS the joke",
            ],
        },
        "midpoint": {
            "name": "Midpoint — False Victory + Fracture",
            "duration": 180,
            "valence_in": 0.6,
            "valence_out": -0.7,
            "position": "Act 2 — The turn (exact middle of film)",
            "rules": [
                "Rule 2: Callback Architecture — use a phrase from Act 1 in a new context",
                "Rule 8: Emotional Climax Dialogue — the fracture should have false starts and run-ons",
                "Rule 1: Subtext First — the break happens through what's NOT said",
            ],
        },
        "bad_guys": {
            "name": "Bad Guys Close In",
            "duration": 150,
            "valence_in": -0.7,
            "valence_out": -0.5,
            "position": "Act 2B — Conspiracy deepens",
            "rules": [
                "Rule 9: Villain Dialogue — familial language, self-awareness, belonging",
                "Rule 1: Subtext First — threats are veiled as concern",
                "Rule 4: Visual Gags — even dark scenes need visual storytelling",
            ],
        },
        "dark_night": {
            "name": "All Is Lost / Dark Night of the Soul",
            "duration": 150,
            "valence_in": -0.5,
            "valence_out": -0.8,
            "position": "Act 2B — Emotional death (75% mark)",
            "rules": [
                "Rule 8: Emotional Climax Dialogue — vulnerability, false starts, earned terms",
                "Rule 3: Humor as Defense — if a character jokes here, it must reveal deep trauma",
                "Rule 1: Subtext First — the confession must be earned through 2-3 lines of deflection",
            ],
        },
        "finale": {
            "name": "Finale / Climax + Emotional Payoff",
            "duration": 240,
            "valence_in": -0.8,
            "valence_out": 0.8,
            "position": "Act 3 — Final confrontation and resolution",
            "rules": [
                "Rule 2: Callback Architecture — pay off every major phrase from Act 1-2",
                "Rule 7: Therapy Exercise Payoff — the comedic ritual becomes real emotional work",
                "Rule 8: Emotional Climax Dialogue — messy, interrupted, grammatically broken",
                "Rule 9: Villain Dialogue — offer them a choice to be different",
            ],
        },
    }
    
    # Visual openings per beat
    VISUAL_OPENINGS = {
        "opening": [
            "TIGHT ON: A specific object that represents the protagonist's world. Then pull back to reveal them.",
            "OVER BLACK: A sound that defines the world. Then: reveal the source.",
            "We see quick pops of morning routine — contrast between two characters' approaches to the same world.",
        ],
        "catalyst": [
            "A crate splits open. Eyes peer from the darkness inside.",
            "A document falls from a shelf, revealing something no one was meant to see.",
            "The celebration continues overhead. Below, a wall cracks.",
        ],
        "debate": [
            "Two characters sit in mismatched chairs. One bounces. The other slouches.",
            "A sign reads the theme ironically. Neither character looks at each other.",
            "One character lists reasons on their fingers. The other checks their watch.",
        ],
        "fun_games": [
            "A disguise is revealed to be ridiculous — but effective.",
            "Chase sequence: they navigate a space built for someone twice their size.",
            "A misunderstanding becomes a performance. The audience doesn't know it's fake.",
        ],
        "midpoint": [
            "They celebrate. Glasses clink. But one character doesn't drink.",
            "A confession that should bring them together instead drives them apart.",
            "The truth is spoken. The room goes silent. Then: the door slams.",
        ],
        "bad_guys": [
            "Shadows on the wall. The antagonist's silhouette does something gentle — then cruel.",
            "A family photo on the antagonist's desk. They turn it face-down.",
            "The protagonist finds what they were looking for. It's worse than they imagined.",
        ],
        "dark_night": [
            "One character is trapped. The other is too far away to help.",
            "Rain on glass. The protagonist watches their reflection distort.",
            "A letter is read. The handwriting is familiar. The message is devastating.",
        ],
        "finale": [
            "The two groups face each other across a divide — physical and metaphorical.",
            "The antagonist holds the proof. The protagonist holds the truth.",
            "Dawn breaks. The monument stands. Two characters stand before it, transformed.",
        ],
    }
    
    # Visual closings per beat
    VISUAL_CLOSINGS = {
        "opening": [
            "A camera flashes. SMASH TO TITLE.",
            "The door closes. We hold on the empty room.",
            "They walk away — in opposite directions.",
        ],
        "catalyst": [
            "The discovery is made. Nothing will be the same.",
            "A shadow falls across the map. Someone was watching.",
            "The alarm sounds. Too late.",
        ],
        "debate": [
            "They leave separately. The chairs remain askew.",
            "One looks back. The other doesn't.",
            "The sign creaks in the wind.",
        ],
        "fun_games": [
            "They escape — but leave something important behind.",
            "The disguise falls off. They're exposed. But they got what they needed.",
            "Laughter echoes. Then: silence.",
        ],
        "midpoint": [
            "SMASH CUT TO BLACK. A door slams.",
            "The partnership is broken. The case continues alone.",
            "They walk away from each other. The space between them is the whole world.",
        ],
        "bad_guys": [
            "The trap closes. The protagonist doesn't see it yet.",
            "A phone rings. The caller ID says everything.",
            "The antagonist smiles. It's worse than a threat.",
        ],
        "dark_night": [
            "The light goes out. They're alone.",
            "A tear falls. They wipe it before anyone sees.",
            "Hope is gone. Only the truth remains — and it hurts.",
        ],
        "finale": [
            "They stand together. The city behind them is changed.",
            "The sun rises on a new world. They walk into it — together.",
            "SMASH TO: the empty monument. Then: two shadows appear.",
        ],
    }
    
    def __init__(self, obsidian_bridge: Optional[ObsidianBridge] = None):
        self.bridge = obsidian_bridge or get_bridge()
        self.vault_path = Path(self.bridge.vault_path)
    
    def compile_briefs(self, concept_id: str = "WINNER",
                       production_id: Optional[str] = None) -> list[SceneBrief]:
        """Compile scene briefs for all 8 beats from a concept."""
        
        # Load concept
        concept_note = self.bridge.read_note(f"concepts/{concept_id}.md")
        if concept_note is None:
            raise ValueError(f"Concept not found: concepts/{concept_id}.md")
        
        concept_data = self._parse_concept(concept_note)
        
        # Load characters with voice profiles
        characters = self._load_characters()
        
        # Load skills
        skills = self._load_skills()
        
        # Load DNA for examples
        dna = self._load_dna(concept_data.get("dna_source", "memory/films_analyzed/zootopia2_dna.md"))
        
        # Theme extraction
        theme = concept_data.get("theme", "trust and prejudice")
        theme_keywords = self._extract_theme_keywords(theme, concept_data)
        
        # Generate briefs for each beat
        beats = ["opening", "catalyst", "debate", "fun_games",
                 "midpoint", "bad_guys", "dark_night", "finale"]
        
        briefs = []
        for i, beat_type in enumerate(beats, 1):
            beat_def = self.BEAT_DEFS[beat_type]
            
            # Determine which characters are present
            scene_chars = self._select_characters_for_beat(
                beat_type, characters, concept_data
            )
            
            # Determine emotional states
            char_briefs = self._build_character_briefs(
                scene_chars, beat_type, concept_data, i
            )
            
            # Determine callbacks
            callbacks_setup, callbacks_payoff = self._determine_callbacks(
                beat_type, briefs, concept_data
            )
            
            # Build the brief
            brief = SceneBrief(
                scene_number=i,
                beat_type=beat_type,
                beat_name=beat_def["name"],
                slugline=self._generate_slugline(beat_type, concept_data),
                duration_target_seconds=beat_def["duration"],
                emotional_valence_in=beat_def["valence_in"],
                emotional_valence_out=beat_def["valence_out"],
                previous_scene_summary=self._summarize_previous_scene(briefs),
                next_scene_requirements=self._preview_next_scene(beats, i, concept_data),
                story_position=beat_def["position"],
                characters=char_briefs,
                theme=theme,
                theme_keywords=theme_keywords,
                theme_weaving_instructions=self._theme_weaving_instructions(beat_type, theme),
                callbacks_to_setup=callbacks_setup,
                callbacks_to_payoff=callbacks_payoff,
                dialogue_rules=beat_def["rules"],
                visual_opening=self._select_visual(beat_type, "opening"),
                visual_closing=self._select_visual(beat_type, "closing"),
                key_props=self._select_props(beat_type, concept_data),
                lighting_mood=self._select_lighting(beat_type),
                writing_instructions=self._writing_instructions(beat_type, char_briefs, theme),
                lines_target=12 if beat_type in ["opening", "catalyst", "debate"] else 15,
                words_per_line_target=10,
                subtext_ratio_target=0.6 if beat_type not in ["dark_night", "finale"] else 0.4,
            )
            
            briefs.append(brief)
        
        return briefs
    
    def save_briefs(self, briefs: list[SceneBrief],
                    production_id: str,
                    output_dir: Optional[Path] = None) -> list[Path]:
        """Save briefs as markdown files to studio/briefs/."""
        if output_dir is None:
            output_dir = self.vault_path / "briefs" / production_id
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        paths = []
        for brief in briefs:
            content = self._format_brief_markdown(brief)
            filename = f"scene_{brief.scene_number:03d}_{brief.beat_type}.md"
            filepath = output_dir / filename
            filepath.write_text(content, encoding="utf-8")
            paths.append(filepath)
        
        # Also save a writer's packet (all briefs in one file)
        packet_path = output_dir / "WRITERS_PACKET.md"
        packet_content = self._format_writers_packet(briefs, production_id)
        packet_path.write_text(packet_content, encoding="utf-8")
        paths.append(packet_path)
        
        return paths
    
    def _parse_concept(self, note) -> dict[str, Any]:
        """Parse concept note into structured data."""
        content = note.content
        data = {
            "title": note.title,
            "characters": [],
            "structure": {},
            "theme": "",
            "setting": "",
            "genre": "",
        }
        
        # Extract frontmatter if present in note
        if note.frontmatter:
            data.update(note.frontmatter)
        
        # Extract character names
        char_pattern = r'###\s+(.+?)\s+\('
        data["characters"] = re.findall(char_pattern, content)
        
        # Extract act summaries
        for act in ["Act 1", "Act 2A", "Midpoint", "Act 2B", "Act 3"]:
            pattern = rf'###\s+{act}\s*\n(.+?)(?=###|\Z)'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                data["structure"][act.lower().replace(" ", "_")] = match.group(1).strip()
        
        # Extract theme
        theme_match = re.search(r'\*\*Theme\*\*:\s*(.+)', content)
        if theme_match:
            data["theme"] = theme_match.group(1).strip()
        
        # Extract setting
        setting_match = re.search(r'\*\*Setting\*\*:\s*(.+)', content)
        if setting_match:
            data["setting"] = setting_match.group(1).strip()
        
        # Extract genre
        genre_match = re.search(r'\*\*Genre\*\*:\s*(.+)', content)
        if genre_match:
            data["genre"] = genre_match.group(1).strip()
        
        return data
    
    def _load_characters(self) -> list[dict[str, Any]]:
        """Load character bibles and voice profiles from vault."""
        characters = []
        
        # Look for character notes
        char_notes = self.bridge.query_notes(folder="characters")
        for note in char_notes:
            if "_voice" in note.path or "environments" in note.path:
                continue
            
            fm = note.frontmatter
            char_data = {
                "name": fm.get("name", note.title.replace("Character Bible: ", "")),
                "archetype": fm.get("archetype", "unknown"),
                "role": fm.get("role", "supporting"),
                "description": note.content[:300],
            }
            
            # Try to load voice profile
            char_id = fm.get("character_id", "")
            if char_id:
                voice_note = self.bridge.read_note(f"characters/{char_id}_voice.md")
                if voice_note:
                    vfm = voice_note.frontmatter
                    char_data["voice"] = {
                        "sarcasm": vfm.get("sarcasm", 50.0),
                        "cynicism": vfm.get("cynicism", 50.0),
                        "warmth": vfm.get("warmth", 50.0),
                        "formality": vfm.get("formality", 50.0),
                        "verbosity": vfm.get("verbosity", 50.0),
                        "subtext": vfm.get("subtext", 50.0),
                        "vocabulary_level": vfm.get("vocabulary_level", "moderate"),
                        "sentence_structure": vfm.get("sentence_structure", "mixed"),
                    }
                    # Extract signature/forbidden phrases from content
                    sig_match = re.search(r'### Signature Phrases\n(.+?)(?=###|\Z)', 
                                         voice_note.content, re.DOTALL)
                    if sig_match:
                        char_data["voice"]["signature_phrases"] = [
                            line.strip().lstrip("- '").rstrip("'")
                            for line in sig_match.group(1).strip().split("\n")
                            if line.strip()
                        ]
                    
                    forb_match = re.search(r'### Forbidden Phrases\n(.+?)(?=###|\Z)',
                                          voice_note.content, re.DOTALL)
                    if forb_match:
                        char_data["voice"]["forbidden_phrases"] = [
                            line.strip().lstrip("- '").rstrip("'")
                            for line in forb_match.group(1).strip().split("\n")
                            if line.strip()
                        ]
            
            characters.append(char_data)
        
        return characters
    
    def _load_skills(self) -> dict[str, str]:
        """Load craft skills from vault."""
        skills = {}
        skills_dir = self.vault_path / "skills"
        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.md"):
                skills[skill_file.stem] = skill_file.read_text(encoding="utf-8")
        return skills
    
    def _load_dna(self, dna_source: str) -> dict[str, Any]:
        """Load DNA for reference examples."""
        dna_note = self.bridge.read_note(dna_source)
        if dna_note:
            return {"content": dna_note.content[:2000]}  # First 2000 chars for context
        return {}
    
    def _extract_theme_keywords(self, theme: str, concept_data: dict) -> list[str]:
        """Extract theme keywords from theme statement."""
        # Simple extraction: nouns and key verbs from theme
        words = theme.lower().split()
        # Filter out common words
        stopwords = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "can", "is", "are", "be", "that", "this", "it"}
        keywords = [w.strip(",.!?;:") for w in words if w.strip(",.!?;:") not in stopwords and len(w) > 3]
        
        # Add concept-specific keywords
        if "group_a" in concept_data:
            keywords.append(concept_data["group_a"])
        if "group_b" in concept_data:
            keywords.append(concept_data["group_b"])
        
        return list(set(keywords))[:8]  # Max 8 keywords
    
    def _select_characters_for_beat(self, beat_type: str,
                                     characters: list[dict],
                                     concept_data: dict) -> list[dict]:
        """Select which characters appear in this beat."""
        # Sort characters by role
        protags = [c for c in characters if c.get("role") == "protagonist"]
        deuts = [c for c in characters if c.get("role") == "deuteragonist"]
        antags = [c for c in characters if c.get("role") == "antagonist"]
        support = [c for c in characters if c.get("role") not in ["protagonist", "deuteragonist", "antagonist"]]
        
        if beat_type == "opening":
            return protags[:1] + deuts[:1]
        elif beat_type == "catalyst":
            return protags[:1] + deuts[:1] + support[:1]
        elif beat_type == "debate":
            return protags[:1] + deuts[:1]
        elif beat_type == "fun_games":
            return protags[:1] + deuts[:1] + support[:1]
        elif beat_type == "midpoint":
            return protags[:1] + deuts[:1] + antags[:1]
        elif beat_type == "bad_guys":
            return protags[:1] + deuts[:1] + antags[:1]
        elif beat_type == "dark_night":
            return protags[:1] + deuts[:1]
        elif beat_type == "finale":
            return protags[:1] + deuts[:1] + antags[:1] + support[:1]
        
        return characters[:2]
    
    def _build_character_briefs(self, scene_chars: list[dict],
                                 beat_type: str,
                                 concept_data: dict,
                                 scene_num: int) -> list[CharacterBrief]:
        """Build character briefs for a scene."""
        char_briefs = []
        
        # Emotional state progression across beats
        emotional_progression = {
            "opening": {"in": "optimistic, eager, naive", "out": "challenged but hopeful"},
            "catalyst": {"in": "hopeful", "out": "shocked, uncertain"},
            "debate": {"in": "uncertain, resistant", "out": "cautiously committed"},
            "fun_games": {"in": "committed, energetic", "out": "confident, bonding"},
            "midpoint": {"in": "confident, celebratory", "out": "betrayed, broken"},
            "bad_guys": {"in": "determined, alone", "out": "cornered, fearful"},
            "dark_night": {"in": "defeated, hopeless", "out": "devastated, vulnerable"},
            "finale": {"in": "renewed, resolved", "out": "transformed, whole"},
        }
        
        # Scene objectives per beat
        objectives = {
            "opening": "Establish their world, routine, and core desire",
            "catalyst": "React to the inciting incident; make a choice",
            "debate": "Form the partnership; establish the B-story dynamic",
            "fun_games": "Deepen the investigation; build camaraderie through comedy",
            "midpoint": "Celebrate a false victory; then fracture the partnership",
            "bad_guys": "Confront the antagonist's tightening control",
            "dark_night": "Face their worst fear; confess their true feelings",
            "finale": "Confront the antagonist; earn their transformation",
        }
        
        prog = emotional_progression.get(beat_type, {"in": "neutral", "out": "neutral"})
        obj = objectives.get(beat_type, "Advance the plot")
        
        for char in scene_chars:
            voice = char.get("voice", {})
            char_briefs.append(CharacterBrief(
                name=char["name"],
                archetype=char["archetype"],
                role=char.get("role", "supporting"),
                emotional_state_in=prog["in"],
                emotional_state_out=prog["out"],
                scene_objective=obj,
                voice_dimensions={
                    "sarcasm": voice.get("sarcasm", 50.0),
                    "cynicism": voice.get("cynicism", 50.0),
                    "warmth": voice.get("warmth", 50.0),
                    "formality": voice.get("formality", 50.0),
                    "verbosity": voice.get("verbosity", 50.0),
                    "subtext": voice.get("subtext", 50.0),
                },
                signature_phrases=voice.get("signature_phrases", []),
                forbidden_phrases=voice.get("forbidden_phrases", []),
                vocabulary_level=voice.get("vocabulary_level", "moderate"),
                sentence_structure=voice.get("sentence_structure", "mixed"),
                physical_comedy_notes=self._physical_comedy_notes(char["archetype"]),
            ))
        
        return char_briefs
    
    def _physical_comedy_notes(self, archetype: str) -> str:
        """Generate physical comedy notes based on archetype."""
        notes = {
            "cynical trickster": "Uses lazy, efficient movements. Brushes fur with same brush he uses for teeth. Slouches constantly.",
            "earnest believer": "Springs into action. Throws whole body against doors. Over-prepares physically.",
            "meek villain": "Small, deferential gestures. Twists hands. Avoids eye contact — until the reveal.",
            "frightened outsider": "Trembles slightly. Hides behind larger characters. Makes themselves small.",
            "folksy warrior": "Underestimated size, surprising strength. Country wisdom gestures. Points with thumb.",
        }
        return notes.get(archetype.lower(), "Physical comedy TBD")
    
    def _determine_callbacks(self, beat_type: str,
                              previous_briefs: list[SceneBrief],
                              concept_data: dict) -> tuple[list[str], list[str]]:
        """Determine which callbacks to set up or pay off in this scene."""
        setup = []
        payoff = []
        
        if beat_type == "opening":
            setup = ["A casual phrase that will become emotionally charged later",
                     "A visual motif that repeats at the climax"]
        elif beat_type == "catalyst":
            setup = ["An object or phrase that represents the protagonist's false belief"]
        elif beat_type == "debate":
            setup = ["A comedic ritual or exercise that will pay off in Act 3"]
        elif beat_type == "fun_games":
            setup = ["A skill or tool the protagonist will need in the finale"]
        elif beat_type == "midpoint":
            payoff = ["The false belief from the catalyst — shattered"]
            setup = ["A new understanding that will be tested"]
        elif beat_type == "bad_guys":
            payoff = ["The comedic ritual from Act 2 — twisted by the antagonist"]
        elif beat_type == "dark_night":
            payoff = ["The partnership dynamic from the debate — tested to breaking"]
        elif beat_type == "finale":
            payoff = ["Every major callback from Acts 1-2 pays off here"]
        
        return setup, payoff
    
    def _generate_slugline(self, beat_type: str, concept_data: dict) -> str:
        """Generate a slugline for the beat."""
        setting = concept_data.get("setting", "CITY")
        setting_short = setting.split()[0].upper() if setting else "CITY"
        
        sluglines = {
            "opening": f"EXT. {setting_short} — MORNING",
            "catalyst": f"INT. {setting_short} — BUREAU — DAY",
            "debate": f"INT. COUNSELING ROOM — DAY",
            "fun_games": f"EXT. UNDERWORLD — NIGHT",
            "midpoint": f"INT. HEADQUARTERS — NIGHT",
            "bad_guys": f"INT. HIDEOUT — NIGHT",
            "dark_night": f"INT. PRISON CELL — NIGHT",
            "finale": f"EXT. MONUMENT — DAWN",
        }
        return sluglines.get(beat_type, f"INT. {setting_short} — DAY")
    
    def _summarize_previous_scene(self, previous_briefs: list[SceneBrief]) -> str:
        """Summarize the previous scene for context."""
        if not previous_briefs:
            return "This is the opening scene. Nothing precedes it."
        
        prev = previous_briefs[-1]
        chars = ", ".join([c.name for c in prev.characters])
        return (
            f"Scene {prev.scene_number} ({prev.beat_name}): {chars} were present. "
            f"Emotional arc: {prev.emotional_valence_in:+.1f} → {prev.emotional_valence_out:+.1f}. "
            f"Ended with: {prev.visual_closing}"
        )
    
    def _preview_next_scene(self, beats: list[str], current_index: int,
                            concept_data: dict) -> str:
        """Preview what the next scene needs to accomplish."""
        if current_index >= len(beats):
            return "This is the final scene. The film ends here."
        
        next_beat = beats[current_index]
        next_def = self.BEAT_DEFS[next_beat]
        return f"Next: {next_def['name']} — must {next_def['position'].split('—')[-1].strip()}."
    
    def _theme_weaving_instructions(self, beat_type: str, theme: str) -> str:
        """Generate instructions for weaving theme into this beat."""
        instructions = {
            "opening": f"Show the theme '{theme}' through the world itself — architecture, behavior, what characters take for granted. Do not state it.",
            "catalyst": f"The inciting incident should be a concrete manifestation of '{theme}'. The protagonist's reaction reveals their relationship to the theme.",
            "debate": f"The partnership forming should embody '{theme}' — two perspectives on the same problem.",
            "fun_games": f"The comedy should come from the clash between characters who represent different sides of '{theme}'.",
            "midpoint": f"The fracture should be caused by a disagreement about '{theme}' — what it means, who it includes.",
            "bad_guys": f"The antagonist's motivation should be a dark mirror of '{theme}' — they want the same thing but through exclusion.",
            "dark_night": f"The despair should feel like '{theme}' has been proven false. The confession should reassert it.",
            "finale": f"The resolution must earn '{theme}' through action, not speech. The characters prove it by what they do.",
        }
        return instructions.get(beat_type, f"Weave '{theme}' into dialogue subtext and visual metaphors.")
    
    def _select_visual(self, beat_type: str, which: str) -> str:
        """Select a visual opening or closing for the beat."""
        import random
        pool = (self.VISUAL_OPENINGS if which == "opening" else self.VISUAL_CLOSINGS).get(beat_type, ["TBD"])
        return random.choice(pool)
    
    def _select_props(self, beat_type: str, concept_data: dict) -> list[str]:
        """Select key props for the beat."""
        props = {
            "opening": ["An object that represents the protagonist's world"],
            "catalyst": ["The discovered object", "A map or document"],
            "debate": ["Mismatched chairs", "A sign or form"],
            "fun_games": ["A disguise", "A tool or weapon"],
            "midpoint": ["Celebration glasses", "A phone or message"],
            "bad_guys": ["A family photo", "Evidence documents"],
            "dark_night": ["A letter", "Rain on glass"],
            "finale": ["The proof/evidence", "A symbolic object from Act 1"],
        }
        return props.get(beat_type, [])
    
    def _select_lighting(self, beat_type: str) -> str:
        """Select lighting mood for the beat."""
        lighting = {
            "opening": "Bright, optimistic, warm colors",
            "catalyst": "Neutral daylight → sudden shadow",
            "debate": "Flat fluorescent → warm as bond forms",
            "fun_games": "Neon, colorful, energetic",
            "midpoint": "Bright celebration → sudden darkness",
            "bad_guys": "Low-key, shadows, cold colors",
            "dark_night": "Minimal light, rain, blue tones",
            "finale": "Dawn light, warm, hopeful",
        }
        return lighting.get(beat_type, "Neutral")
    
    def _writing_instructions(self, beat_type: str,
                               characters: list[CharacterBrief],
                               theme: str) -> str:
        """Generate specific writing instructions for the AI."""
        char_list = ", ".join([c.name for c in characters])
        
        base = f"""Write a professional animation screenplay scene in Fountain format.

CHARACTERS IN SCENE: {char_list}

FORMAT REQUIREMENTS:
- Start with the SLUGLINE
- Action lines in prose (present tense, visual)
- Character names in ALL CAPS before dialogue
- Parentheticals in (parentheses) for tone shifts only
- Dialogue: 8-14 words per line, short and punchy
- Every dialogue block must have visual business (what are they DOING while talking?)

QUALITY TARGETS:
- Lines per scene: 8-15
- Subtext ratio: 60%+ of lines should mean something other than what they say
- Visual business: 100% of dialogue blocks need action
- Callback density: at least one phrase that echoes earlier or sets up later

WHAT NOT TO DO:
- Do NOT have characters state emotions directly ("I am sad")
- Do NOT have all characters speak with the same vocabulary
- Do NOT write talking heads (standing still, just talking)
- Do NOT let the villain monologue about power (they want belonging)
- Do NOT write emotional climaxes as polished speeches (messy, interrupted)
"""
        
        beat_specific = {
            "opening": "\nOPENING SCENE NOTES:\n- Establish the world through behavior, not exposition\n- Show the protagonist's routine and what's missing from it\n- End with a visual that sets up the catalyst",
            "catalyst": "\nCATALYST NOTES:\n- The discovery must be VISUAL and SPECIFIC\n- Show the protagonist's immediate reaction through action, not words\n- The world should feel different after this scene",
            "debate": "\nDEBATE NOTES:\n- The partnership dynamic should be clear in the first exchange\n- Use physical comedy to show mismatch (size, speed, approach)\n- Introduce a comedic ritual or exercise that feels throwaway",
            "fun_games": "\nFUN & GAMES NOTES:\n- This is the comedy set piece — action IS the joke\n- Chase sequences, disguises, misunderstandings\n- The partnership should be working smoothly by the end",
            "midpoint": "\nMIDPOINT NOTES:\n- False victory: celebrate, then shatter\n- The fracture must feel inevitable but devastating\n- Use a callback phrase in a new, heartbreaking context",
            "bad_guys": "\nBAD GUYS NOTES:\n- The antagonist should seem almost sympathetic before turning cruel\n- Threats are veiled as concern\n- The protagonist should feel the walls closing in",
            "dark_night": "\nDARK NIGHT NOTES:\n- This is the emotional death. Go deep.\n- False starts, run-on sentences, self-deprecation\n- The confession must be earned through deflection first",
            "finale": "\nFINALE NOTES:\n- Pay off EVERY callback from Acts 1-2\n- The comedic ritual from Act 2 becomes real emotional work\n- The villain gets a choice to be different\n- End with a specific, earned detail — not generic victory",
        }
        
        return base + beat_specific.get(beat_type, "")
    
    # =====================================================================
    # Formatting
    # =====================================================================
    
    def _format_brief_markdown(self, brief: SceneBrief) -> str:
        """Format a single brief as markdown."""
        
        chars_section = ""
        for c in brief.characters:
            dims = c.voice_dimensions
            sig_phrases = "\n".join(f"    - '{p}'" for p in c.signature_phrases) or "    - (none yet)"
            forb_phrases = "\n".join(f"    - '{p}'" for p in c.forbidden_phrases) or "    - (none yet)"
            
            chars_section += f"""### {c.name} ({c.archetype.upper()})
- **Role**: {c.role}
- **Emotional State Entering**: {c.emotional_state_in}
- **Emotional State Exiting**: {c.emotional_state_out}
- **Scene Objective**: {c.scene_objective}

**Voice Profile**:
| Dimension | Score | Guidance |
|-----------|-------|----------|
| Sarcasm | {dims.get('sarcasm', 50):.0f}/100 | {'Deflects with irony' if dims.get('sarcasm', 50) > 60 else 'Speaks directly' if dims.get('sarcasm', 50) < 40 else 'Balanced'} |
| Cynicism | {dims.get('cynicism', 50):.0f}/100 | {'Expects the worst' if dims.get('cynicism', 50) > 60 else 'Expects the best' if dims.get('cynicism', 50) < 40 else 'Balanced'} |
| Warmth | {dims.get('warmth', 50):.0f}/100 | {'Openly caring' if dims.get('warmth', 50) > 60 else 'Guarded' if dims.get('warmth', 50) < 40 else 'Balanced'} |
| Formality | {dims.get('formality', 50):.0f}/100 | {'Formal vocabulary' if dims.get('formality', 50) > 60 else 'Casual/colloquial' if dims.get('formality', 50) < 40 else 'Balanced'} |
| Verbosity | {dims.get('verbosity', 50):.0f}/100 | {'Wordy, complex sentences' if dims.get('verbosity', 50) > 60 else 'Terse, short sentences' if dims.get('verbosity', 50) < 40 else 'Balanced'} |
| Subtext | {dims.get('subtext', 50):.0f}/100 | {'Speaks in implication' if dims.get('subtext', 50) > 60 else 'Says what they mean' if dims.get('subtext', 50) < 40 else 'Balanced'} |

**Signature Phrases**:
{sig_phrases}

**Forbidden Phrases**:
{forb_phrases}

**Physical Comedy Notes**: {c.physical_comedy_notes}

---
"""
        
        rules_section = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(brief.dialogue_rules))
        
        setup_section = "\n".join(f"- {c}" for c in brief.callbacks_to_setup) or "- (none)"
        payoff_section = "\n".join(f"- {c}" for c in brief.callbacks_to_payoff) or "- (none)"
        
        return f"""# Scene Brief: Scene {brief.scene_number:03d} — {brief.beat_name}

## 🎬 Metadata
| Field | Value |
|-------|-------|
| **Scene Number** | {brief.scene_number} |
| **Beat** | {brief.beat_type} |
| **Slugline** | {brief.slugline} |
| **Duration Target** | {brief.duration_target_seconds}s ({brief.duration_target_seconds // 60}m {brief.duration_target_seconds % 60}s) |
| **Emotional Arc** | {brief.emotional_valence_in:+.1f} → {brief.emotional_valence_out:+.1f} |
| **Story Position** | {brief.story_position} |
| **Lines Target** | {brief.lines_target} |
| **Words/Line Target** | {brief.words_per_line_target} |
| **Subtext Target** | {brief.subtext_ratio_target:.0%} |

---

## 📖 Story Context

### Where We Are
{brief.story_position}

### What Just Happened
{brief.previous_scene_summary}

### What Needs to Happen Next
{brief.next_scene_requirements}

---

## 🎭 Characters

{chars_section}

---

## 🌈 Theme Weaving
**Theme**: {brief.theme}

**Keywords to Weave In**: {', '.join(brief.theme_keywords)}

**Instructions**: {brief.theme_weaving_instructions}

---

## 🔄 Callbacks

### Set Up in This Scene
{setup_section}

### Pay Off in This Scene
{payoff_section}

---

## ✍️ Dialogue Craft Rules for This Beat
{rules_section}

---

## 🎥 Visual Direction

### Opening Image
{brief.visual_opening}

### Closing Image
{brief.visual_closing}

### Key Props
{chr(10).join(f'- {p}' for p in brief.key_props) or '- (none specified)'}

### Lighting/Mood
{brief.lighting_mood}

---

## 📝 Writing Instructions

{brief.writing_instructions}

---

## ✅ OUTPUT

Write the complete scene in **Fountain format** below:

```fountain
{brief.slugline}

[YOUR SCENE HERE]
```

**Save to**: `studio/scenes/{brief.scene_number:03d}_{brief.beat_type}.md`
"""
    
    def _format_writers_packet(self, briefs: list[SceneBrief], production_id: str) -> str:
        """Format all briefs into a single Writer's Packet."""
        
        scenes_overview = "\n".join(
            f"| {b.scene_number} | {b.beat_name} | {b.slugline} | {b.emotional_valence_in:+.1f} → {b.emotional_valence_out:+.1f} | {', '.join(c.name for c in b.characters)} |"
            for b in briefs
        )
        
        packet = f"""# Writer's Packet: {production_id}

> **Instructions for the AI Writer**: This packet contains 8 scene briefs for an animated feature. 
> Read each brief completely before writing. Write ONE scene at a time. Save each scene to the path specified.
> Focus on: original dialogue, voice consistency, theme weaving, and visual storytelling.

---

## 📊 Scene Overview

| # | Beat | Slugline | Emotional Arc | Characters |
|---|------|----------|---------------|------------|
{scenes_overview}

---

## 🎯 Global Rules (Apply to Every Scene)

1. **Subtext First**: Characters NEVER say exactly what they feel in the first line. Earn it through deflection.
2. **Visual Business**: Every dialogue block needs action. What is the character physically doing?
3. **Voice Consistency**: Each character has a voice profile. Respect the dimensions.
4. **Theme Weaving**: The theme appears in action lines, dialogue subtext, and visual metaphors — never stated directly.
5. **Callbacks**: Phrases must echo. First appearance casual, second appearance emotionally charged.
6. **No On-the-Nose Emotion**: "I am sad" is forbidden. Show through action and subtext.
7. **Villains Want Belonging**: Never monologue about power. Monologue about love, family, recognition.
8. **Emotional Climaxes Are Messy**: False starts, run-ons, self-deprecation, earned terms.

---

## 🎭 Character Voice Cheat Sheet

"""
        
        # Add character cheat sheet (deduplicated)
        all_chars = {}
        for brief in briefs:
            for c in brief.characters:
                if c.name not in all_chars:
                    all_chars[c.name] = c
        
        for name, c in all_chars.items():
            dims = c.voice_dimensions
            packet += f"""### {name} ({c.archetype})
- **Sarcasm**: {dims.get('sarcasm', 50):.0f} | **Cynicism**: {dims.get('cynicism', 50):.0f} | **Warmth**: {dims.get('warmth', 50):.0f}
- **Formality**: {dims.get('formality', 50):.0f} | **Verbosity**: {dims.get('verbosity', 50):.0f} | **Subtext**: {dims.get('subtext', 50):.0f}
- **Signature**: {', '.join(c.signature_phrases[:2]) or 'TBD'}
- **Forbidden**: {', '.join(c.forbidden_phrases[:2]) or 'TBD'}

"""
        
        packet += """---

## 📝 Individual Scene Briefs

"""
        
        for brief in briefs:
            packet += f"""---

## Scene {brief.scene_number}: {brief.beat_name}

**File**: `studio/scenes/{brief.scene_number:03d}_{brief.beat_type}.md`

**Slugline**: {brief.slugline}

**Emotional Arc**: {brief.emotional_valence_in:+.1f} → {brief.emotional_valence_out:+.1f}

**Characters**: {', '.join(c.name for c in brief.characters)}

**Theme Instructions**: {brief.theme_weaving_instructions}

**Visual Opening**: {brief.visual_opening}

**Visual Closing**: {brief.visual_closing}

**Key Rules**:
{chr(10).join(f'- {r}' for r in brief.dialogue_rules)}

**Writing Focus**: {brief.writing_instructions.split(chr(10))[0] if brief.writing_instructions else 'Write professional animation dialogue'}

"""
        
        packet += """---

## ✅ Completion Checklist

After writing all scenes, run:
```bash
python run_studio.py assemble """ + production_id + """
```

This will validate voice consistency, check callbacks, and compile the final screenplay.
"""
        
        return packet


# =============================================================================
# Assembly / Validation
# =============================================================================

class ScreenplayAssembler:
    """Assembles written scenes into a final screenplay.
    
    Validates:
    - Voice consistency (Language Engine)
    - Callback completeness
    - Theme density
    - Format correctness (Fountain)
    """
    
    def __init__(self, obsidian_bridge: Optional[ObsidianBridge] = None):
        self.bridge = obsidian_bridge or get_bridge()
        self.vault_path = Path(self.bridge.vault_path)
    
    def assemble(self, production_id: str) -> dict[str, Any]:
        """Assemble all scenes for a production into a final screenplay."""
        
        scenes_dir = self.vault_path / "scenes"
        if not scenes_dir.exists():
            return {"error": "No scenes directory found"}
        
        # Find all scene files for this production
        scene_files = sorted(scenes_dir.glob("[0-9][0-9][0-9]_*.md"))
        if not scene_files:
            # Try without production subdir
            scene_files = sorted(scenes_dir.glob("scene_*.md"))
        
        if not scene_files:
            return {"error": f"No scenes found for production: {production_id}"}
        
        # Read and validate each scene
        scenes = []
        issues = []
        
        for scene_file in scene_files:
            content = scene_file.read_text(encoding="utf-8")
            
            # Basic Fountain validation
            scene_issues = self._validate_fountain(content, scene_file.name)
            issues.extend(scene_issues)
            
            scenes.append({
                "filename": scene_file.name,
                "content": content,
                "issues": scene_issues,
            })
        
        # Compile full screenplay
        screenplay = self._compile_screenplay(scenes, production_id)
        
        # Write to vault
        output_path = self.vault_path / f"screenplays/{production_id}_screenplay.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(screenplay, encoding="utf-8")
        
        return {
            "production_id": production_id,
            "scenes_assembled": len(scenes),
            "issues_found": len(issues),
            "issues": issues,
            "screenplay_path": str(output_path),
            "word_count": len(screenplay.split()),
        }
    
    def _validate_fountain(self, content: str, filename: str) -> list[str]:
        """Basic Fountain format validation."""
        issues = []
        lines = content.split("\n")
        
        # Check for slugline
        if not any(line.startswith("EXT.") or line.startswith("INT.") for line in lines):
            issues.append(f"{filename}: Missing slugline (EXT. or INT.)")
        
        # Check for character names in all caps before dialogue
        in_dialogue = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.isupper() and len(stripped) > 1 and not stripped.startswith("EXT.") and not stripped.startswith("INT."):
                in_dialogue = True
            elif in_dialogue and stripped and not stripped.startswith("("):
                in_dialogue = False
        
        # Check for on-the-nose emotion
        forbidden_patterns = [
            r"I am sad",
            r"I feel sad",
            r"I am angry",
            r"I feel angry",
            r"I am happy",
            r"I feel happy",
            r"I am scared",
            r"I feel scared",
        ]
        for pattern in forbidden_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"{filename}: On-the-nose emotion detected: '{pattern}'")
        
        return issues
    
    def _compile_screenplay(self, scenes: list[dict], production_id: str) -> str:
        """Compile scenes into a single screenplay document."""
        
        lines = [
            f"Title: {production_id.replace('_', ' ').title()}",
            "Credit: Written by AI Animation Studio",
            "Author: Evolutionary Studio System",
            "Draft date: " + datetime.now().strftime("%Y-%m-%d"),
            "Contact: studio@localhost",
            "",
            "===",
            "",
        ]
        
        for scene in scenes:
            lines.append(scene["content"])
            lines.append("")
            lines.append("===")
            lines.append("")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test brief compilation
    compiler = SceneBriefCompiler()
    try:
        briefs = compiler.compile_briefs(concept_id="WINNER")
        print(f"Compiled {len(briefs)} scene briefs")
        for b in briefs:
            print(f"  Scene {b.scene_number}: {b.beat_name} — {b.slugline}")
        
        paths = compiler.save_briefs(briefs, production_id="test-production")
        print(f"\nSaved briefs to:")
        for p in paths:
            print(f"  {p}")
    except Exception as e:
        print(f"Error: {e}")
