"""
Film DNA Extractor — The Perception + Understanding Engine

This module takes a reference film (or clip) and produces a Film Genome Document.
It orchestrates the full DNA extraction pipeline:

1. Scene Detection (PySceneDetect or manual timestamps)
2. Content Analysis (Gemini 2M context for full-film understanding)
3. Narrative Structure Extraction (beat sheet, character arcs)
4. Visual DNA Extraction (color palettes, shot types)
5. Pacing Analysis (shot lengths, cutting dynamics)
6. Emotional Arc Mapping (valence-arousal over time)
7. Film Genome Document Assembly

Usage:
    extractor = FilmDNAExtractor()
    genome = extractor.extract_from_description(film_analysis_text)
    genome.save("vault/00-film-dna/zootopia_genome.yaml")
"""

import yaml
import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path
from datetime import date


# ═══════════════════════════════════════════════════════
# DATA MODELS — Mirror the Film Genome Document schema
# ═══════════════════════════════════════════════════════

@dataclass
class Beat:
    id: str
    name: str
    type: str  # setup, catalyst, debate, etc.
    timestamp_pct: float  # 0.0 - 1.0
    emotional_valence: float  # -1.0 to 1.0
    emotional_arousal: float  # 0.0 to 1.0
    description: str
    duration_pct: float = 0.0


@dataclass
class CausalLink:
    cause: str  # beat_id
    effect: str  # beat_id
    relationship: str  # because_of_that, until_finally, meanwhile


@dataclass
class NarrativeDNA:
    structure: str = "save_the_cat"
    emotional_arc_shape: str = "cinderella"
    beats: list = field(default_factory=list)
    causal_chain: list = field(default_factory=list)
    themes: list = field(default_factory=list)


@dataclass
class CharacterRelationship:
    target: str  # character_id
    type: str
    evolution: str


@dataclass
class CharacterVisual:
    reference_sheet: str = ""
    turnaround: str = ""
    expression_sheet: str = ""
    color_palette: list = field(default_factory=list)
    description: str = ""


@dataclass
class CharacterVoice:
    style: str = ""
    reference_audio: str = ""
    tts_model: str = ""


@dataclass
class Character:
    id: str
    name: str
    archetype: str
    arc: str
    traits: list = field(default_factory=list)
    introduction_beat: str = ""
    relationships: list = field(default_factory=list)
    visual: CharacterVisual = field(default_factory=CharacterVisual)
    voice: CharacterVoice = field(default_factory=CharacterVoice)


@dataclass
class ColorDNA:
    palette: list = field(default_factory=list)
    mood: str = ""
    saturation_level: str = "natural"
    contrast: str = "medium"


@dataclass
class ShotDistribution:
    wide: float = 0.25
    medium: float = 0.40
    close_up: float = 0.25
    extreme_close_up: float = 0.05
    overhead: float = 0.05


@dataclass
class VisualStyle:
    render_style: str = "3d_stylized"
    lighting_approach: str = "cinematic_three_point"
    reference_films_visual: list = field(default_factory=list)
    art_direction_notes: str = ""


@dataclass
class VisualDNA:
    color_dna: dict = field(default_factory=dict)  # act -> ColorDNA
    shot_distribution: ShotDistribution = field(default_factory=ShotDistribution)
    style: VisualStyle = field(default_factory=VisualStyle)


@dataclass
class PacingDNA:
    average_shot_length_seconds: float = 4.0
    asl_by_act: dict = field(default_factory=dict)
    cutting_dynamics: str = "accelerating"
    tension_curve: list = field(default_factory=list)  # [[pct, value], ...]
    rhythm_pattern: str = ""


@dataclass
class SilenceMoment:
    beat_id: str
    duration_seconds: float
    purpose: str


@dataclass
class MusicStyle:
    genre: str = ""
    reference: str = ""
    emotional_arc_follows: bool = True
    instruments: list = field(default_factory=list)


@dataclass
class AudioDNA:
    dialogue_ratio: float = 0.45
    music_coverage: float = 0.70
    silence_moments: list = field(default_factory=list)
    music_style: MusicStyle = field(default_factory=MusicStyle)
    voice_styles: dict = field(default_factory=dict)


@dataclass
class Shot:
    id: str
    type: str  # wide_establishing, medium, close_up, etc.
    duration_seconds: float
    camera_movement: str = "static"
    description: str = ""
    characters_in_frame: list = field(default_factory=list)
    dialogue: Optional[str] = None
    sfx: list = field(default_factory=list)
    transition_to_next: str = "cut"


@dataclass
class EmotionalTarget:
    valence: float = 0.0
    arousal: float = 0.0


@dataclass
class Scene:
    id: str
    beat_id: str
    act: int
    location: str = ""
    time_of_day: str = "day"
    weather: str = ""
    characters_present: list = field(default_factory=list)
    emotional_target: EmotionalTarget = field(default_factory=EmotionalTarget)
    duration_seconds: float = 0.0
    shots: list = field(default_factory=list)


@dataclass
class RenderingHints:
    preferred_models: dict = field(default_factory=lambda: {
        "character_closeups": "kling_3.0",
        "establishing_shots": "veo_3.1",
        "dialogue_scenes": "seedance_2.0",
        "action_sequences": "hunyuan_video",
        "bulk_transitions": "wan_2.1"
    })
    budget_mode: bool = False
    max_cost_usd: float = 500.0
    quality_threshold: float = 0.85
    target_resolution: str = "1080p"
    target_fps: int = 24


@dataclass
class FilmGenomeDocument:
    """The complete Film Genome Document — the 'source code' of a film."""

    # Metadata
    title: str = "Untitled Film"
    reference_film: str = ""
    genome_version: str = "1.0"
    author: str = "Creative Loop Engine"
    created: str = field(default_factory=lambda: str(date.today()))
    target_duration_minutes: float = 5.0
    target_format: str = "short_film"

    # 7 DNA Strands
    narrative: NarrativeDNA = field(default_factory=NarrativeDNA)
    characters: list = field(default_factory=list)
    visual: VisualDNA = field(default_factory=VisualDNA)
    pacing: PacingDNA = field(default_factory=PacingDNA)
    audio: AudioDNA = field(default_factory=AudioDNA)
    scenes: list = field(default_factory=list)
    rendering: RenderingHints = field(default_factory=RenderingHints)

    def save(self, path: str):
        """Save Film Genome Document as YAML."""
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = self._to_dict()
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False,
                      allow_unicode=True, width=120)
        print(f"Film Genome saved to: {filepath}")

    def save_json(self, path: str):
        """Save Film Genome Document as JSON."""
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        data = self._to_dict()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Film Genome saved to: {filepath}")

    def _to_dict(self):
        """Convert to nested dict for serialization."""
        return _deep_asdict(self)

    @classmethod
    def load(cls, path: str) -> 'FilmGenomeDocument':
        """Load Film Genome Document from YAML."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> 'FilmGenomeDocument':
        """Reconstruct from dict (basic implementation)."""
        genome = cls()
        genome.title = data.get('title', 'Untitled')
        genome.reference_film = data.get('reference_film', '')
        genome.genome_version = data.get('genome_version', '1.0')
        genome.author = data.get('author', '')
        genome.created = data.get('created', str(date.today()))
        genome.target_duration_minutes = data.get('target_duration_minutes', 5.0)
        genome.target_format = data.get('target_format', 'short_film')

        # Parse narrative
        if 'narrative' in data:
            n = data['narrative']
            genome.narrative = NarrativeDNA(
                structure=n.get('structure', 'save_the_cat'),
                emotional_arc_shape=n.get('emotional_arc_shape', 'cinderella'),
                beats=[Beat(**b) for b in n.get('beats', [])],
                causal_chain=[CausalLink(**c) for c in n.get('causal_chain', [])],
                themes=n.get('themes', [])
            )

        # Parse characters
        if 'characters' in data:
            for c in data['characters']:
                visual = CharacterVisual(**c.get('visual', {})) if 'visual' in c else CharacterVisual()
                voice = CharacterVoice(**c.get('voice', {})) if 'voice' in c else CharacterVoice()
                rels = [CharacterRelationship(**r) for r in c.get('relationships', [])]
                char = Character(
                    id=c['id'], name=c['name'], archetype=c.get('archetype', 'custom'),
                    arc=c.get('arc', ''), traits=c.get('traits', []),
                    introduction_beat=c.get('introduction_beat', ''),
                    relationships=rels, visual=visual, voice=voice
                )
                genome.characters.append(char)

        # Parse scenes
        if 'scenes' in data:
            for s in data['scenes']:
                et = EmotionalTarget(**s.get('emotional_target', {})) if 'emotional_target' in s else EmotionalTarget()
                shots = [Shot(**sh) for sh in s.get('shots', [])]
                scene = Scene(
                    id=s['id'], beat_id=s.get('beat_id', ''), act=s.get('act', 1),
                    location=s.get('location', ''), time_of_day=s.get('time_of_day', 'day'),
                    characters_present=s.get('characters_present', []),
                    emotional_target=et, duration_seconds=s.get('duration_seconds', 0),
                    shots=shots
                )
                genome.scenes.append(scene)

        return genome

    def validate(self) -> dict:
        """Run basic validation checks on the genome."""
        errors = []
        warnings = []

        # Check required fields
        if not self.title or self.title == "Untitled Film":
            warnings.append("Film has no title")

        # Check beats exist
        if not self.narrative.beats:
            errors.append("No narrative beats defined")

        # Check characters exist
        if not self.characters:
            errors.append("No characters defined")

        # Check beat references in causal chain
        beat_ids = {b.id for b in self.narrative.beats}
        for link in self.narrative.causal_chain:
            if link.cause not in beat_ids:
                errors.append(f"Causal chain references unknown beat: {link.cause}")
            if link.effect not in beat_ids:
                errors.append(f"Causal chain references unknown beat: {link.effect}")

        # Check character references in scenes
        char_ids = {c.id for c in self.characters}
        for scene in self.scenes:
            for char_id in scene.characters_present:
                if char_id not in char_ids:
                    errors.append(f"Scene {scene.id} references unknown character: {char_id}")

        # Check emotional arc shape
        valid_shapes = ['rags_to_riches', 'tragedy', 'man_in_a_hole',
                        'icarus', 'cinderella', 'oedipus']
        if self.narrative.emotional_arc_shape not in valid_shapes:
            warnings.append(f"Unknown emotional arc shape: {self.narrative.emotional_arc_shape}")

        # Check shot distribution sums to ~1.0
        sd = self.visual.shot_distribution
        total = sd.wide + sd.medium + sd.close_up + sd.extreme_close_up + sd.overhead
        if abs(total - 1.0) > 0.05:
            warnings.append(f"Shot distribution sums to {total:.2f}, expected ~1.0")

        # Check scene durations
        total_scene_duration = sum(s.duration_seconds for s in self.scenes)
        target_seconds = self.target_duration_minutes * 60
        if self.scenes and total_scene_duration > 0:
            ratio = total_scene_duration / target_seconds
            if ratio < 0.5 or ratio > 1.5:
                warnings.append(
                    f"Scene durations total {total_scene_duration:.0f}s "
                    f"vs target {target_seconds:.0f}s (ratio: {ratio:.2f})"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "stats": {
                "beats": len(self.narrative.beats),
                "characters": len(self.characters),
                "scenes": len(self.scenes),
                "total_shots": sum(len(s.shots) for s in self.scenes),
                "total_duration_seconds": total_scene_duration
            }
        }

    def summary(self) -> str:
        """Human-readable summary of the genome."""
        validation = self.validate()
        stats = validation['stats']

        lines = [
            f"═══ Film Genome: {self.title} ═══",
            f"Reference: {self.reference_film or 'None'}",
            f"Format: {self.target_format} ({self.target_duration_minutes} min)",
            f"Structure: {self.narrative.structure}",
            f"Emotional Arc: {self.narrative.emotional_arc_shape}",
            f"",
            f"Stats:",
            f"  Beats: {stats['beats']}",
            f"  Characters: {stats['characters']}",
            f"  Scenes: {stats['scenes']}",
            f"  Shots: {stats['total_shots']}",
            f"  Duration: {stats['total_duration_seconds']:.0f}s",
            f"",
            f"Validation: {'✅ VALID' if validation['valid'] else '❌ ERRORS'}",
        ]

        if validation['errors']:
            lines.append(f"  Errors ({len(validation['errors'])}):")
            for e in validation['errors']:
                lines.append(f"    ❌ {e}")

        if validation['warnings']:
            lines.append(f"  Warnings ({len(validation['warnings'])}):")
            for w in validation['warnings']:
                lines.append(f"    ⚠️  {w}")

        return "\n".join(lines)


def _deep_asdict(obj):
    """Recursively convert dataclass to dict, handling nested structures."""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field_name, field_def in obj.__dataclass_fields__.items():
            value = getattr(obj, field_name)
            result[field_name] = _deep_asdict(value)
        return result
    elif isinstance(obj, list):
        return [_deep_asdict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _deep_asdict(val) for key, val in obj.items()}
    else:
        return obj


# ═══════════════════════════════════════════════════════
# EXTRACTION PROMPTS — Used by the Creative Loop Engine
# ═══════════════════════════════════════════════════════

FILM_DNA_EXTRACTION_PROMPT = """
You are a Film DNA Extractor. Your job is to analyze a reference film and produce
a complete Film Genome Document — a structured specification that captures everything
that makes this film work.

Analyze the film across these 7 DNA strands:

## 1. NARRATIVE DNA
- Identify the structural framework (Save the Cat, Hero's Journey, Story Spine)
- Map all major story beats with timestamps (as % of runtime)
- Classify the emotional arc shape (one of 6: rags_to_riches, tragedy, man_in_a_hole, icarus, cinderella, oedipus)
- Score each beat for emotional valence (-1 to +1) and arousal (0 to 1)
- Map the causal chain (how does each beat cause the next?)
- Identify core themes

## 2. CHARACTER DNA
- List all significant characters
- Classify archetypes (reluctant_hero, charming_trickster, wise_mentor, etc.)
- Map character arcs (how does each character change?)
- Chart relationships and how they evolve
- Note distinctive visual and vocal traits

## 3. VISUAL DNA
- Extract color palettes per act (hex codes)
- Identify the dominant shot types and their distribution
- Describe the visual style (lighting, composition approach)
- Note any signature visual techniques

## 4. PACING DNA
- Estimate average shot length (in seconds) per act
- Identify the cutting dynamics pattern (accelerating, decelerating, wave, etc.)
- Map the tension curve (0-1 values at key points throughout the film)
- Describe the rhythm pattern

## 5. AUDIO DNA
- Estimate dialogue-to-runtime ratio
- Estimate music coverage ratio
- Identify intentional silence moments
- Describe the musical style and instrumentation
- Note distinctive voice characteristics per character

## 6. SCENE MANIFEST (for key scenes)
- Break down at least 3 key scenes into individual shots
- For each shot: type, duration, camera movement, characters, dialogue, SFX

## 7. SECRET SAUCE
- What makes THIS film special vs. others in its genre?
- What are the non-obvious patterns that drive audience engagement?
- What elements would transfer well to a new story?
- What elements are too specific to this film to transfer?

Output your analysis as a structured YAML Film Genome Document.
"""


# ═══════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Create a minimal example genome and validate it
    genome = FilmGenomeDocument(
        title="Test Film",
        reference_film="Zootopia",
        target_duration_minutes=5.0,
    )

    genome.narrative = NarrativeDNA(
        structure="save_the_cat",
        emotional_arc_shape="cinderella",
        beats=[
            Beat("beat_01", "Opening Image", "setup", 0.0, 0.3, 0.2,
                 "Establish the world and protagonist"),
            Beat("beat_02", "Catalyst", "catalyst", 0.10, 0.5, 0.6,
                 "The event that changes everything"),
        ],
        themes=["prejudice", "identity", "perseverance"]
    )

    genome.characters = [
        Character(
            id="char_protagonist",
            name="Judy Hopps",
            archetype="reluctant_hero",
            arc="idealistic outsider → disillusioned realist → empowered agent of change",
            traits=["optimistic", "stubborn", "compassionate", "naive"],
            introduction_beat="beat_01",
        )
    ]

    print(genome.summary())
    print()

    # Save as YAML
    genome.save("/tmp/test_genome.yaml")
    print("Genome saved successfully.")

    # Load and validate
    loaded = FilmGenomeDocument.load("/tmp/test_genome.yaml")
    print(f"\nLoaded genome: {loaded.title}")
    print(loaded.summary())
