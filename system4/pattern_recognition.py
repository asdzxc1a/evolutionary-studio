"""Pattern Recognition Module — System 4, Phase 1

Replaces heuristic keyword-matching critics with real structural analysis.
Analyzes concepts and prototypes against established story patterns to produce
scores, specific issues, and actionable suggestions.

Patterns are drawn from:
- Save the Cat beat sheet (Snyder)
- Three-act structure (Field)
- Hero's Journey (Campbell/Vogler)
- Character arc theory (Truby, McKee)
- Emotional arc research (Reagan et al., University of Vermont)
- Pacing formulas from animated features
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import — these are only needed for type hints
    from system3.evolution_engine import Concept, Prototype, ScenePrototype, CriticScore

# Lazy imports from System 3 to avoid circular dependency
# These are imported inside methods that need them


# =============================================================================
# Pattern Data Structures
# =============================================================================

@dataclass
class BeatDefinition:
    """A single story beat with structural requirements."""
    name: str
    target_position: float  # 0.0 to 1.0 (percent through story)
    tolerance: float = 0.05  # +/- acceptable deviation
    required: bool = True
    description: str = ""
    what_it_does: str = ""  # Narrative function


@dataclass
class StoryStructurePattern:
    """A complete story structure template (Save the Cat, 3-Act, etc.)."""
    name: str
    description: str
    beats: list[BeatDefinition]
    act_breaks: list[float] = field(default_factory=list)  # e.g., [0.25, 0.75]


@dataclass
class CharacterArcPattern:
    """A character transformation pattern."""
    name: str
    description: str
    starting_state_type: str  # "ignorant", "corrupt", "wounded", etc.
    ending_state_type: str    # "enlightened", "redeemed", "healed", etc.
    required_stages: list[str] = field(default_factory=list)
    midpoint_flip: bool = True  # Does the midpoint reverse the arc direction?


@dataclass
class EmotionalArcPattern:
    """An ideal emotional curve for a genre."""
    name: str
    genre: str
    description: str
    key_beats: list[tuple[float, float, str]]  # (position, target_valence, label)
    min_range: float = 1.0  # Max - Min valence required
    recovery_time_after_negative: float = 90.0  # seconds
    climax_target_valence: float = 0.8


@dataclass
class PacingFormula:
    """Genre-specific pacing rules."""
    name: str
    genre: str
    target_duration_minutes: float
    target_scene_count: tuple[int, int]  # (min, max)
    act_ratios: list[float]  # e.g., [0.25, 0.50, 0.25]
    hook_max_seconds: float = 120.0
    climax_min_seconds: float = 180.0
    action_to_dialogue_ratio: tuple[float, float] = (1.0, 2.0)  # min, max action:dialogue
    avg_scene_duration_seconds: float = 90.0


@dataclass
class ThemePattern:
    """Thematic consistency requirements."""
    name: str
    description: str
    social_metaphor_required: bool = True
    show_dont_tell_ratio: float = 0.7  # action beats / total beats
    max_preachiness_score: float = 3.0  # 0-10, lower is less preachy
    thematic_keyword_density_max: float = 0.15  # max % of lines with theme words


@dataclass
class PatternScore:
    """Score output from pattern analysis — compatible with CriticScore."""
    analyzer_name: str
    category: str
    score: float  # 0.0 to 10.0
    confidence: float  # 0.0 to 1.0
    notes: str
    specific_issues: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    pattern_matches: dict[str, float] = field(default_factory=dict)  # pattern_name -> match_score

    def to_critic_score(self) -> "CriticScore":
        """Convert to System 3 CriticScore for backward compatibility."""
        from system3.evolution_engine import CriticScore
        return CriticScore(
            critic_name=self.analyzer_name,
            category=self.category,
            score=self.score,
            notes=self.notes,
            specific_issues=self.specific_issues,
            strengths=self.strengths,
        )


# =============================================================================
# Pattern Library
# =============================================================================

class PatternLibrary:
    """Loads and provides access to all story patterns."""

    # Save the Cat 15-beat structure (simplified to key beats for concept analysis)
    SAVE_THE_CAT = StoryStructurePattern(
        name="Save the Cat",
        description="Blake Snyder's 15-beat structure for commercial storytelling",
        act_breaks=[0.25, 0.75],
        beats=[
            BeatDefinition("Opening Image", 0.00, 0.02, True,
                          "First impression of the hero's world",
                          "Establishes the 'before' state thematically and visually"),
            BeatDefinition("Theme Stated", 0.05, 0.03, False,
                          "Someone states the theme aloud",
                          "Thematic thesis of the entire story"),
            BeatDefinition("Setup", 0.10, 0.05, True,
                          "Introduce hero, their flaw, their world",
                          "Build empathy; show what's missing in their life"),
            BeatDefinition("Catalyst", 0.10, 0.03, True,
                          "Life-changing event kicks off the journey",
                          "The inciting incident; no turning back"),
            BeatDefinition("Debate", 0.15, 0.03, True,
                          "Hero questions whether to go on the journey",
                          "The last chance to turn back; fear vs. desire"),
            BeatDefinition("Break into Two", 0.25, 0.03, True,
                          "Hero makes the choice; enters the upside-down world",
                          "The point of no return"),
            BeatDefinition("B-Story", 0.30, 0.05, False,
                          "Secondary plot/relationship begins",
                          "Often the 'love story' that carries the theme"),
            BeatDefinition("Fun & Games", 0.35, 0.05, True,
                          "The promise of the premise; trailer moments",
                          "Hero explores the new world; successes and failures"),
            BeatDefinition("Midpoint", 0.50, 0.03, True,
                          "False victory OR false defeat; stakes raised",
                          "The turning point; everything changes"),
            BeatDefinition("Bad Guys Close In", 0.60, 0.05, True,
                          "Internal and external opposition mounts",
                          "Complications pile up; team fractures"),
            BeatDefinition("All Is Lost", 0.75, 0.03, True,
                          "The lowest point; death/rebirth moment",
                          "The 'whiff of death'; everything seems hopeless"),
            BeatDefinition("Dark Night of the Soul", 0.78, 0.03, True,
                          "Hero processes the loss; the rock bottom",
                          "The emotional nadir before the climb"),
            BeatDefinition("Break into Three", 0.80, 0.03, True,
                          "Hero synthesizes old world + new world lessons",
                          "The solution emerges from combining both worlds"),
            BeatDefinition("Finale", 0.90, 0.05, True,
                          "Hero applies the lesson; climax and resolution",
                          "The theme is proved; the arc completes"),
            BeatDefinition("Final Image", 0.98, 0.02, True,
                          "Opposite of Opening Image; shows the transformation",
                          "Thematic bookend; proof of change"),
        ]
    )

    THREE_ACT = StoryStructurePattern(
        name="Three-Act Structure",
        description="Classic setup-confrontation-resolution structure",
        act_breaks=[0.25, 0.75],
        beats=[
            BeatDefinition("Act 1 Setup", 0.15, 0.10, True,
                          "Establish world, characters, status quo, what's wrong",
                          "Build empathy; define the ordinary world"),
            BeatDefinition("Inciting Incident", 0.10, 0.05, True,
                          "Event that disrupts the status quo",
                          "The call to adventure"),
            BeatDefinition("First Plot Point", 0.25, 0.03, True,
                          "Hero commits to the journey; enters Act 2",
                          "Point of no return"),
            BeatDefinition("Midpoint", 0.50, 0.03, True,
                          "Stakes raise; direction changes",
                          "The fulcrum of the story"),
            BeatDefinition("Second Plot Point", 0.75, 0.03, True,
                          "All Is Lost; hero hits bottom",
                          "The darkness before dawn"),
            BeatDefinition("Climax", 0.90, 0.05, True,
                          "Final confrontation; hero applies what they learned",
                          "Thematic and emotional peak"),
            BeatDefinition("Resolution", 0.95, 0.05, True,
                          "New normal established; arc completes",
                          "Proof of transformation"),
        ]
    )

    # Character arc patterns
    POSITIVE_CHANGE_ARC = CharacterArcPattern(
        name="Positive Change Arc",
        description="Hero believes a Lie, learns the Truth, transforms",
        starting_state_type="wounded_or_limited",
        ending_state_type="healed_or_enlightened",
        required_stages=[
            "starts with a Lie they believe",
            "Acts on the Lie in Act 1",
            "Midpoint glimpses the Truth",
            "Lie is tested in Act 2B",
            "Chooses Truth at climax",
            "Transformed in resolution",
        ],
        midpoint_flip=True,
    )

    FLAT_ARC = CharacterArcPattern(
        name="Flat Arc",
        description="Hero already knows the Truth; changes the world around them",
        starting_state_type="steadfast",
        ending_state_type="steadfast",
        required_stages=[
            "starts with the Truth",
            "Acts on Truth in Act 1",
            "Midpoint tests their resolve",
            "World resists Truth in Act 2B",
            "Truth wins at climax",
            "World is transformed",
        ],
        midpoint_flip=False,
    )

    NEGATIVE_CHANGE_ARC = CharacterArcPattern(
        name="Negative Change Arc (Fall)",
        description="Hero believes a Lie, rejects the Truth, descends",
        starting_state_type="has_chance_at_redemption",
        ending_state_type="deeper_in_lie",
        required_stages=[
            "starts with opportunity for Truth",
            "Chooses Lie at key moments",
            "Midpoint commits to Lie",
            "Act 2B doubles down",
            "Climax reveals cost of Lie",
            "Tragic resolution",
        ],
        midpoint_flip=True,
    )

    # Emotional arc patterns (based on Reagan et al. "The emotional arcs of stories are dominated by six basic shapes")
    RAGS_TO_RICHES = EmotionalArcPattern(
        name="Rags to Riches",
        genre="animated_comedy_drama",
        description="Steady rise with a deep valley in the middle (Zootopia, Finding Nemo)",
        key_beats=[
            (0.05, 0.2, "Opening"),
            (0.15, 0.4, "Setup"),
            (0.25, 0.3, "Debate"),
            (0.50, -0.6, "Midpoint fall"),
            (0.60, -0.3, "Bad Guys Close In"),
            (0.75, -0.8, "All Is Lost"),
            (0.85, 0.3, "Break into Three"),
            (0.95, 0.9, "Climax"),
        ],
        min_range=1.5,
        recovery_time_after_negative=90.0,
        climax_target_valence=0.8,
    )

    COMEDY_ARC = EmotionalArcPattern(
        name="Comedy Arc",
        genre="comedy",
        description="Mostly positive with sharp negative dips (The Hangover, Zootopia's lighter beats)",
        key_beats=[
            (0.10, 0.5, "Setup"),
            (0.30, 0.7, "Fun & Games"),
            (0.50, -0.2, "Midpoint complication"),
            (0.75, -0.4, "All Is Lost"),
            (0.95, 0.8, "Resolution"),
        ],
        min_range=1.0,
        recovery_time_after_negative=60.0,
        climax_target_valence=0.7,
    )

    TRAGEDY_ARC = EmotionalArcPattern(
        name="Tragedy Arc",
        genre="tragedy",
        description="Rise then devastating fall (Breaking Bad, Requiem for a Dream)",
        key_beats=[
            (0.20, 0.6, "Rising"),
            (0.50, 0.8, "Peak"),
            (0.65, 0.2, "Turning"),
            (0.80, -0.6, "Falling"),
            (0.95, -0.9, "Catastrophe"),
        ],
        min_range=1.5,
        recovery_time_after_negative=30.0,
        climax_target_valence=-0.8,
    )

    # Pacing formulas
    ANIMATED_FEATURE_PACING = PacingFormula(
        name="Animated Feature",
        genre="animated_comedy_drama",
        target_duration_minutes=90.0,
        target_scene_count=(45, 65),
        act_ratios=[0.25, 0.50, 0.25],
        hook_max_seconds=120.0,
        climax_min_seconds=180.0,
        action_to_dialogue_ratio=(1.0, 2.5),
        avg_scene_duration_seconds=90.0,
    )

    # Theme patterns
    SOCIAL_METAPHOR_THEME = ThemePattern(
        name="Social Metaphor Theme",
        description="Theme is explored through a social metaphor (prejudice, class, etc.)",
        social_metaphor_required=True,
        show_dont_tell_ratio=0.65,
        max_preachiness_score=4.0,
        thematic_keyword_density_max=0.12,
    )

    def __init__(self):
        self.structures = [
            self.SAVE_THE_CAT,
            self.THREE_ACT,
        ]
        self.character_arcs = [
            self.POSITIVE_CHANGE_ARC,
            self.FLAT_ARC,
            self.NEGATIVE_CHANGE_ARC,
        ]
        self.emotional_arcs = [
            self.RAGS_TO_RICHES,
            self.COMEDY_ARC,
            self.TRAGEDY_ARC,
        ]
        self.pacing_formulas = [
            self.ANIMATED_FEATURE_PACING,
        ]
        self.theme_patterns = [
            self.SOCIAL_METAPHOR_THEME,
        ]

    def get_structure_for_genre(self, genre: str) -> list[StoryStructurePattern]:
        """Get structure patterns matching a genre."""
        # For now, return all structures; future: filter by genre
        return self.structures

    def get_emotional_arc_for_genre(self, genre: str) -> Optional[EmotionalArcPattern]:
        """Get the ideal emotional arc for a genre."""
        genre_lower = genre.lower().replace(" ", "_")
        for arc in self.emotional_arcs:
            if arc.genre == genre_lower:
                return arc
        # Default to rags-to-riches for animated features
        return self.RAGS_TO_RICHES

    def get_pacing_for_genre(self, genre: str) -> Optional[PacingFormula]:
        """Get pacing formula for a genre."""
        genre_lower = genre.lower().replace(" ", "_")
        for formula in self.pacing_formulas:
            if formula.genre == genre_lower:
                return formula
        return self.ANIMATED_FEATURE_PACING


# =============================================================================
# Analyzers
# =============================================================================

class StructureAnalyzer:
    """Analyzes story structure against established patterns."""

    def __init__(self, library: Optional[PatternLibrary] = None):
        self.library = library or PatternLibrary()

    def analyze(self, concept: "Concept", prototype: "Prototype") -> PatternScore:
        """Analyze concept + prototype structure against all patterns."""
        from system3.evolution_engine import Concept, Prototype
        issues = []
        strengths = []
        suggestions = []
        pattern_matches = {}
        total_score = 0.0

        for pattern in self.library.structures:
            match_score, pattern_issues, pattern_strengths, pattern_suggestions = \
                self._analyze_against_pattern(concept, prototype, pattern)
            pattern_matches[pattern.name] = match_score
            total_score += match_score
            issues.extend(pattern_issues)
            strengths.extend(pattern_strengths)
            suggestions.extend(pattern_suggestions)

        # Average across patterns
        avg_score = total_score / len(self.library.structures) if self.library.structures else 5.0

        # Normalize to 0-10
        final_score = max(0.0, min(10.0, avg_score * 10))

        notes = f"Structure score: {final_score:.1f}/10. "
        notes += f"Best match: {max(pattern_matches, key=pattern_matches.get)} ({max(pattern_matches.values()):.0%}). "
        notes += f"{len(strengths)} strengths, {len(issues)} issues."

        return PatternScore(
            analyzer_name="Structure Analyzer",
            category="structure",
            score=final_score,
            confidence=0.75 + (0.05 * len(pattern_matches)),
            notes=notes,
            specific_issues=list(set(issues)),
            strengths=list(set(strengths)),
            suggestions=list(set(suggestions)),
            pattern_matches=pattern_matches,
        )

    def _analyze_against_pattern(
        self, concept: "Concept", prototype: "Prototype", pattern: StoryStructurePattern
    ) -> tuple[float, list[str], list[str], list[str]]:
        from system3.evolution_engine import Concept, Prototype
        """Analyze against a single structure pattern. Returns (match_score 0-1, issues, strengths, suggestions)."""
        issues = []
        strengths = []
        suggestions = []
        checks_passed = 0
        checks_total = 0

        # Check act structure presence in concept
        if concept.act1_summary:
            checks_passed += 1
            strengths.append(f"Act 1 is defined")
        else:
            issues.append("Act 1 is missing or undefined")
            suggestions.append("Define Act 1: establish the hero's world and what's wrong with it")
        checks_total += 1

        if concept.act2a_summary and concept.act2b_summary:
            checks_passed += 1
            strengths.append("Act 2 is split into 2A and 2B (good structural awareness)")
        elif concept.act2a_summary or concept.act2b_summary:
            issues.append("Act 2 is only partially defined (needs both 2A and 2B)")
            suggestions.append("Split Act 2: 2A = hero explores new world; 2B = things fall apart")
        else:
            issues.append("Act 2 is missing")
            suggestions.append("Define Act 2: the confrontation, comprising 2A and 2B")
        checks_total += 1

        if concept.act3_summary:
            checks_passed += 1
            strengths.append("Act 3 is defined")
        else:
            issues.append("Act 3 is missing")
            suggestions.append("Define Act 3: climax and resolution")
        checks_total += 1

        # Check midpoint quality
        midpoint_scene = prototype.get_scene_by_type("midpoint")
        if midpoint_scene:
            checks_passed += 1
            desc_lower = midpoint_scene.description.lower()
            has_turn = any(word in desc_lower for word in [
                "false victory", "all is lost", "everything changes",
                "stakes raise", "discovery", "revelation", "secret revealed",
                "truth", "betrayal", "captured", "escapes"
            ])
            if has_turn:
                checks_passed += 1
                strengths.append(f"Midpoint has clear dramatic turn")
            else:
                issues.append("Midpoint scene lacks a clear dramatic turn (false victory or false defeat)")
                suggestions.append("Make the midpoint a turning point: either a false victory that sets up a fall, or a false defeat that forces reinvention")

            if concept.midpoint:
                checks_passed += 1
                mp_lower = concept.midpoint.lower()
                if any(word in mp_lower for word in ["discovers", "realizes", "learns", "revealed", "truth"]):
                    strengths.append("Midpoint involves a discovery or revelation")
                else:
                    issues.append("Midpoint should involve a key discovery or revelation")
                    suggestions.append("The midpoint should be where the protagonist discovers a crucial truth or faces an unexpected reversal")
            else:
                issues.append("Midpoint is not defined in concept summary")
                suggestions.append("Write a midpoint summary: the moment everything changes")
        else:
            issues.append("No midpoint scene found in prototype")
            suggestions.append("Add a midpoint scene that raises stakes and changes direction")
        checks_total += 3

        # Check climax quality
        climax_scene = prototype.get_scene_by_type("climax")
        if climax_scene:
            checks_passed += 1
            desc_lower = climax_scene.description.lower()
            has_confrontation = any(word in desc_lower for word in [
                "confront", "battle", "fight", "showdown", "final",
                "sacrifice", "choice", "saves", "stops", "defeats"
            ])
            if has_confrontation:
                checks_passed += 1
                strengths.append("Climax has active confrontation or resolution")
            else:
                issues.append("Climax lacks active confrontation or resolution")
                suggestions.append("The climax should feature the protagonist actively confronting the antagonist or core problem")
        else:
            issues.append("No climax scene found in prototype")
            suggestions.append("Add a climax scene with active confrontation")
        checks_total += 2

        # Check hook quality
        hook_scene = prototype.get_scene_by_type("hook")
        if hook_scene:
            checks_passed += 1
            strengths.append("Hook scene present")
        else:
            issues.append("No hook scene found")
            suggestions.append("Add a hook scene that grabs attention and establishes tone")
        checks_total += 1

        # Check B-story hint
        b_story_indicators = ["partner", "friend", "relationship", "love", "trust", "learns to"]
        has_b_story = any(
            indicator in (concept.act2a_summary or "").lower() or
            indicator in (concept.act2b_summary or "").lower()
            for indicator in b_story_indicators
        )
        if has_b_story:
            checks_passed += 1
            strengths.append("B-story or relationship subplot hinted in Act 2")
        else:
            issues.append("No clear B-story or relationship subplot in Act 2")
            suggestions.append("Consider adding a relationship subplot in Act 2 that carries the theme")
        checks_total += 1

        # Check character arcs support structure
        if concept.protagonist:
            arc_complete = (
                concept.protagonist.starting_state and
                concept.protagonist.ending_state and
                concept.protagonist.starting_state != concept.protagonist.ending_state
            )
            if arc_complete:
                checks_passed += 1
                strengths.append("Protagonist has complete transformation arc")
            else:
                issues.append("Protagonist arc is incomplete (missing start/end state or no change)")
                suggestions.append("Define clear starting and ending states for the protagonist that show transformation")
        checks_total += 1

        match_score = checks_passed / checks_total if checks_total > 0 else 0.5
        return match_score, issues, strengths, suggestions


class CharacterArcAnalyzer:
    """Analyzes character arcs against transformation patterns."""

    def __init__(self, library: Optional[PatternLibrary] = None):
        self.library = library or PatternLibrary()

    def analyze(self, concept: "Concept", prototype: "Prototype") -> PatternScore:
        """Analyze character arcs in the concept."""
        from system3.evolution_engine import Concept, Prototype
        issues = []
        strengths = []
        suggestions = []
        total_score = 0.0
        character_count = 0

        characters = []
        if concept.protagonist:
            characters.append(("protagonist", concept.protagonist))
        if concept.deuteragonist:
            characters.append(("deuteragonist", concept.deuteragonist))
        if concept.antagonist:
            characters.append(("antagonist", concept.antagonist))

        for role, char in characters:
            char_score, char_issues, char_strengths, char_suggestions = \
                self._analyze_character(char, role, concept, prototype)
            total_score += char_score
            character_count += 1
            issues.extend(char_issues)
            strengths.extend(char_strengths)
            suggestions.extend(char_suggestions)

        if character_count == 0:
            return PatternScore(
                analyzer_name="Character Arc Analyzer",
                category="character",
                score=0.0,
                confidence=0.9,
                notes="No main characters defined.",
                specific_issues=["No protagonist, deuteragonist, or antagonist defined"],
                suggestions=["Define at least a protagonist with a clear arc"],
            )

        avg_score = total_score / character_count
        final_score = max(0.0, min(10.0, avg_score * 10))

        notes = f"Character arc score: {final_score:.1f}/10 across {character_count} main characters. "
        notes += f"{len(strengths)} strengths, {len(issues)} issues."

        return PatternScore(
            analyzer_name="Character Arc Analyzer",
            category="character",
            score=final_score,
            confidence=0.70,
            notes=notes,
            specific_issues=list(set(issues)),
            strengths=list(set(strengths)),
            suggestions=list(set(suggestions)),
        )

    def _analyze_character(
        self, char, role: str, concept: "Concept", prototype: "Prototype"
    ) -> tuple[float, list[str], list[str], list[str]]:
        from system3.evolution_engine import Concept, Prototype
        issues = []
        strengths = []
        suggestions = []
        checks_passed = 0
        checks_total = 0

        # Check arc completeness
        if char.starting_state:
            checks_passed += 1
        else:
            issues.append(f"{char.name} ({role}) has no starting state")
            suggestions.append(f"Define {char.name}'s starting state: what Lie do they believe? What wound do they carry?")
        checks_total += 1

        if char.ending_state:
            checks_passed += 1
        else:
            issues.append(f"{char.name} ({role}) has no ending state")
            suggestions.append(f"Define {char.name}'s ending state: how have they transformed?")
        checks_total += 1

        if char.key_transformation:
            checks_passed += 1
        else:
            issues.append(f"{char.name} ({role}) has no defined transformation")
            suggestions.append(f"Define the specific transformation {char.name} undergoes")
        checks_total += 1

        # Check for change (arc, not flat line)
        if char.starting_state and char.ending_state:
            if char.starting_state.lower() != char.ending_state.lower():
                checks_passed += 1
                strengths.append(f"{char.name} has meaningful transformation ({char.starting_state} → {char.ending_state})")
            else:
                issues.append(f"{char.name}'s starting and ending states are identical (no transformation)")
                suggestions.append(f"Give {char.name} a transformation: what do they learn or how do they change?")
            checks_total += 1

        # Check for core wound (depth indicator)
        if char.core_wound:
            checks_passed += 1
            strengths.append(f"{char.name} has a core wound (emotional depth)")
        else:
            issues.append(f"{char.name} lacks a core wound (may feel shallow)")
            suggestions.append(f"Give {char.name} a core wound: what past trauma drives their behavior?")
        checks_total += 1

        # Check archetype fit
        if char.archetype:
            checks_passed += 1
            strengths.append(f"{char.name} has defined archetype: {char.archetype}")
        else:
            issues.append(f"{char.name} has no archetype")
            suggestions.append(f"Assign an archetype to {char.name} (e.g., optimistic underdog, cynical trickster)")
        checks_total += 1

        # Check if arc is reflected in prototype scenes
        arc_in_scenes = False
        for scene in prototype.scenes:
            if char.name.lower() in scene.description.lower():
                arc_in_scenes = True
                break
        if arc_in_scenes:
            checks_passed += 1
            strengths.append(f"{char.name} appears in prototype scenes")
        else:
            issues.append(f"{char.name} does not appear in any prototype scene")
            suggestions.append(f"Include {char.name} in at least one prototype scene to test their voice and arc")
        checks_total += 1

        match_score = checks_passed / checks_total if checks_total > 0 else 0.5
        return match_score, issues, strengths, suggestions


class EmotionalArcAnalyzer:
    """Analyzes emotional curves against ideal patterns for the genre."""

    def __init__(self, library: Optional[PatternLibrary] = None):
        self.library = library or PatternLibrary()

    def analyze(self, concept: "Concept", prototype: "Prototype") -> PatternScore:
        """Analyze emotional arc of prototype scenes."""
        from system3.evolution_engine import Concept, Prototype
        issues = []
        strengths = []
        suggestions = []

        scenes = prototype.scenes
        if not scenes:
            return PatternScore(
                analyzer_name="Emotional Arc Analyzer",
                category="emotion",
                score=0.0,
                confidence=0.9,
                notes="No scenes to analyze.",
                specific_issues=["Prototype contains no scenes"],
                suggestions=["Generate hook, midpoint, and climax scenes"],
            )

        valences = [s.emotional_valence for s in scenes]
        min_val = min(valences)
        max_val = max(valences)
        range_val = max_val - min_val

        # Get ideal arc for genre
        ideal_arc = self.library.get_emotional_arc_for_genre(concept.genre or "animated_comedy_drama")

        checks_passed = 0
        checks_total = 0

        # Check emotional range
        if range_val >= ideal_arc.min_range:
            checks_passed += 1
            strengths.append(f"Strong emotional range ({min_val:+.1f} to {max_val:+.1f})")
        else:
            issues.append(f"Emotional range is narrow ({min_val:+.1f} to {max_val:+.1f}, need {ideal_arc.min_range:.1f}+)")
            suggestions.append("Vary emotional valence more: include deeper lows and higher highs")
        checks_total += 1

        # Check for negative beat
        if min_val < -0.5:
            checks_passed += 1
            strengths.append("Contains effective negative emotional beat")
        else:
            issues.append("Missing strong negative emotional beat (story may feel flat)")
            suggestions.append("Add a scene with negative valence (-0.5 or lower) for emotional contrast")
        checks_total += 1

        # Check climax resolution
        climax = prototype.get_scene_by_type("climax")
        if climax:
            if climax.emotional_valence >= ideal_arc.climax_target_valence - 0.2:
                checks_passed += 1
                strengths.append(f"Climax resolves emotionally ({climax.emotional_valence:+.1f})")
            else:
                issues.append(f"Climax emotional resolution is weak ({climax.emotional_valence:+.1f}, target {ideal_arc.climax_target_valence:+.1f})")
                suggestions.append(f"Strengthen climax emotional payoff (target valence {ideal_arc.climax_target_valence:+.1f})")
        else:
            issues.append("No climax scene to evaluate emotional resolution")
        checks_total += 1

        # Check recovery time (simulated — we only have 3 scenes, so approximate)
        # For a full 60-scene production, this would check actual scene durations
        negative_scenes = [s for s in scenes if s.emotional_valence < -0.5]
        positive_scenes = [s for s in scenes if s.emotional_valence > 0.3]
        if negative_scenes and positive_scenes:
            # Check that negative scenes are followed by less negative or positive
            checks_passed += 1
            strengths.append("Negative beats are contrasted with positive moments")
        elif negative_scenes and not positive_scenes:
            issues.append("All scenes are negative (no emotional recovery)")
            suggestions.append("Add a scene with positive valence to provide emotional relief")
        checks_total += 1

        # Check dialogue emotional authenticity
        total_lines = sum(len(s.dialogue) for s in scenes)
        if total_lines >= 3:
            checks_passed += 1
            strengths.append("Dialogue present in key scenes")
        else:
            issues.append("Sparse dialogue limits emotional expression")
            suggestions.append("Add more dialogue to key scenes to convey emotional subtext")
        checks_total += 1

        # Compare to ideal arc pattern
        pattern_match = self._match_against_ideal(scenes, ideal_arc)
        if pattern_match > 0.6:
            checks_passed += 1
            strengths.append(f"Emotional arc matches {ideal_arc.name} pattern ({pattern_match:.0%})")
        else:
            issues.append(f"Emotional arc deviates from {ideal_arc.name} pattern ({pattern_match:.0%} match)")
            suggestions.append(f"Adjust scene emotional valences to better match {ideal_arc.name} arc")
        checks_total += 1

        match_score = checks_passed / checks_total if checks_total > 0 else 0.5
        final_score = max(0.0, min(10.0, match_score * 10))

        notes = f"Emotion score: {final_score:.1f}/10. Range: {min_val:+.1f} to {max_val:+.1f}. "
        notes += f"Pattern match: {ideal_arc.name} ({pattern_match:.0%})."

        return PatternScore(
            analyzer_name="Emotional Arc Analyzer",
            category="emotion",
            score=final_score,
            confidence=0.70 + (0.05 * len(scenes)),
            notes=notes,
            specific_issues=list(set(issues)),
            strengths=list(set(strengths)),
            suggestions=list(set(suggestions)),
        )

    def _match_against_ideal(self, scenes: list["ScenePrototype"], ideal: EmotionalArcPattern) -> float:
        from system3.evolution_engine import ScenePrototype
        """Match prototype scenes against ideal emotional curve. Returns 0.0-1.0."""
        if not scenes:
            return 0.0

        # Map scenes to approximate positions (0.0 to 1.0)
        scene_positions = []
        for i, scene in enumerate(scenes):
            pos = (i + 1) / (len(scenes) + 1)  # Distribute evenly
            scene_positions.append((pos, scene.emotional_valence))

        # Compare each scene to nearest ideal beat
        total_deviation = 0.0
        for pos, valence in scene_positions:
            # Find nearest ideal beat
            nearest_dev = min(abs(valence - beat_val) for _, beat_val, _ in ideal.key_beats)
            total_deviation += nearest_dev

        avg_deviation = total_deviation / len(scenes)
        # Convert to match score (0 deviation = 1.0, 2.0 deviation = 0.0)
        match = max(0.0, 1.0 - (avg_deviation / 2.0))
        return match


class PacingAnalyzer:
    """Analyzes pacing against genre-specific formulas."""

    def __init__(self, library: Optional[PatternLibrary] = None):
        self.library = library or PatternLibrary()

    def analyze(self, concept: "Concept", prototype: "Prototype") -> PatternScore:
        """Analyze pacing of prototype scenes."""
        from system3.evolution_engine import Concept, Prototype
        issues = []
        strengths = []
        suggestions = []

        scenes = prototype.scenes
        if not scenes:
            return PatternScore(
                analyzer_name="Pacing Analyzer",
                category="pacing",
                score=0.0,
                confidence=0.9,
                notes="No scenes to analyze.",
                specific_issues=["Prototype contains no scenes"],
                suggestions=["Generate scenes to evaluate pacing"],
            )

        formula = self.library.get_pacing_for_genre(concept.genre or "animated_comedy_drama")
        checks_passed = 0
        checks_total = 0

        # Check hook duration
        hook = prototype.get_scene_by_type("hook")
        if hook:
            if hook.estimated_duration_seconds <= formula.hook_max_seconds:
                checks_passed += 1
                strengths.append(f"Hook is concise ({hook.estimated_duration_seconds}s)")
            else:
                issues.append(f"Hook may be too long ({hook.estimated_duration_seconds}s, target ≤{formula.hook_max_seconds}s)")
                suggestions.append("Shorten hook to under 2 minutes to maintain audience engagement")
        else:
            issues.append("No hook scene to evaluate pacing")
        checks_total += 1

        # Check climax duration
        climax = prototype.get_scene_by_type("climax")
        if climax:
            if climax.estimated_duration_seconds >= formula.climax_min_seconds:
                checks_passed += 1
                strengths.append(f"Climax has adequate duration ({climax.estimated_duration_seconds}s)")
            else:
                issues.append(f"Climax may be too brief ({climax.estimated_duration_seconds}s, target ≥{formula.climax_min_seconds}s)")
                suggestions.append("Extend climax to at least 3 minutes for emotional impact")
        else:
            issues.append("No climax scene to evaluate pacing")
        checks_total += 1

        # Check action-to-dialogue ratio
        total_dialogue_lines = sum(len(s.dialogue) for s in scenes)
        total_action_beats = sum(len(s.action_beats) for s in scenes)

        if total_dialogue_lines > 0:
            ratio = total_action_beats / total_dialogue_lines
            min_ratio, max_ratio = formula.action_to_dialogue_ratio
            if min_ratio <= ratio <= max_ratio:
                checks_passed += 1
                strengths.append(f"Action-to-dialogue ratio is balanced ({ratio:.1f}:1)")
            elif ratio < min_ratio:
                issues.append(f"Dialogue-heavy ({ratio:.1f}:1 action/dialogue, target {min_ratio:.1f}-{max_ratio:.1f}:1)")
                suggestions.append("Add more visual action beats — animation thrives on visual storytelling")
            else:
                strengths.append(f"Action-heavy ({ratio:.1f}:1) — dynamic pacing")
        else:
            issues.append("No dialogue in prototype (cannot evaluate dialogue pacing)")
            suggestions.append("Add dialogue to evaluate pacing balance")
        checks_total += 1

        # Check scene count for prototype
        if len(scenes) == 3:
            checks_passed += 1
            strengths.append("Exactly 3 key scenes prototyped (hook, midpoint, climax)")
        else:
            issues.append(f"Prototype has {len(scenes)} scenes (expected 3 key scenes)")
        checks_total += 1

        # Check total prototype duration is reasonable
        total_duration = sum(s.estimated_duration_seconds for s in scenes)
        expected_min = 3 * 60  # 3 min minimum for 3 key scenes
        expected_max = 3 * 300  # 15 min maximum
        if expected_min <= total_duration <= expected_max:
            checks_passed += 1
            strengths.append(f"Total prototype duration is reasonable ({total_duration}s)")
        elif total_duration < expected_min:
            issues.append(f"Scenes feel rushed ({total_duration}s total)")
            suggestions.append("Extend scene durations to allow emotional beats to land")
        else:
            issues.append(f"Scenes may be too long ({total_duration}s total)")
            suggestions.append("Tighten scene durations to maintain momentum")
        checks_total += 1

        match_score = checks_passed / checks_total if checks_total > 0 else 0.5
        final_score = max(0.0, min(10.0, match_score * 10))

        notes = f"Pacing score: {final_score:.1f}/10. Total duration: {total_duration}s. "
        notes += f"Action/dialogue: {total_action_beats}/{total_dialogue_lines}."

        return PatternScore(
            analyzer_name="Pacing Analyzer",
            category="pacing",
            score=final_score,
            confidence=0.75,
            notes=notes,
            specific_issues=list(set(issues)),
            strengths=list(set(strengths)),
            suggestions=list(set(suggestions)),
        )


class ThemeAnalyzer:
    """Analyzes thematic consistency and social metaphor quality."""

    def __init__(self, library: Optional[PatternLibrary] = None):
        self.library = library or PatternLibrary()

    def analyze(self, concept: "Concept", prototype: "Prototype") -> PatternScore:
        """Analyze theme across concept and prototype."""
        from system3.evolution_engine import Concept, Prototype
        issues = []
        strengths = []
        suggestions = []

        checks_passed = 0
        checks_total = 0

        # Check theme presence
        if concept.theme:
            checks_passed += 1
            strengths.append(f"Theme is defined: '{concept.theme}'")
        else:
            issues.append("No theme defined")
            suggestions.append("Define a central theme (e.g., 'trust requires vulnerability')")
        checks_total += 1

        # Check social metaphor
        if concept.social_metaphor:
            checks_passed += 1
            strengths.append(f"Social metaphor is defined: '{concept.social_metaphor}'")

            # Check metaphor specificity (good metaphors are specific)
            metaphor_words = concept.social_metaphor.split()
            if len(metaphor_words) >= 3:
                checks_passed += 1
                strengths.append("Social metaphor is specific and concrete")
            else:
                issues.append("Social metaphor is vague or too abstract")
                suggestions.append("Make the social metaphor specific: 'prejudice between predators and prey' not just 'prejudice'")
        else:
            issues.append("No social metaphor defined")
            suggestions.append("Define a social metaphor that carries the theme (e.g., species = social class)")
        checks_total += 1

        # Check theme integration in scenes (show, don't tell)
        theme_words = set()
        if concept.theme:
            theme_words.update(w.lower() for w in concept.theme.split() if len(w) > 3)
        if concept.social_metaphor:
            theme_words.update(w.lower() for w in concept.social_metaphor.split() if len(w) > 3)

        all_dialogue = []
        all_descriptions = []
        for scene in prototype.scenes:
            # Dialogue is list[dict] with "line" key
            for d in scene.dialogue:
                if isinstance(d, dict):
                    all_dialogue.append(d.get("line", ""))
                else:
                    all_dialogue.append(str(d))
            all_descriptions.append(scene.description)

        # Preachiness check: theme words in dialogue
        preachy_lines = 0
        for line in all_dialogue:
            line_lower = line.lower()
            if any(tw in line_lower for tw in theme_words):
                preachy_lines += 1

        total_lines = len(all_dialogue)
        if total_lines > 0:
            preachiness_ratio = preachy_lines / total_lines
            if preachiness_ratio <= 0.15:  # Max 15% of lines mention theme directly
                checks_passed += 1
                strengths.append(f"Theme is shown, not preached ({preachiness_ratio:.0%} direct mentions)")
            else:
                issues.append(f"Theme is too explicit in dialogue ({preachiness_ratio:.0%} direct mentions, target ≤15%)")
                suggestions.append("Show theme through action and subtext, not characters stating it aloud")
        checks_total += 1

        # Check that theme is present in descriptions (visual storytelling)
        theme_in_descriptions = 0
        for desc in all_descriptions:
            desc_lower = desc.lower()
            if any(tw in desc_lower for tw in theme_words):
                theme_in_descriptions += 1

        if theme_in_descriptions > 0:
            checks_passed += 1
            strengths.append("Theme is reflected in scene descriptions (visual storytelling)")
        else:
            issues.append("Theme is absent from scene descriptions")
            suggestions.append("Embed theme in visual details: setting, costumes, lighting, action")
        checks_total += 1

        # Check concept summaries carry theme
        summaries = [concept.act1_summary, concept.act2a_summary, concept.act2b_summary, concept.act3_summary]
        theme_in_acts = sum(1 for s in summaries if s and any(tw in s.lower() for tw in theme_words))
        if theme_in_acts >= 2:
            checks_passed += 1
            strengths.append("Theme carries across multiple acts")
        else:
            issues.append("Theme may not be sustained across acts")
            suggestions.append("Ensure each act summary reflects the theme's progression")
        checks_total += 1

        # Check for two-way theme (like Zootopia's prejudice-goes-both-ways)
        if concept.theme and concept.social_metaphor:
            theme_lower = concept.theme.lower()
            has_complexity = any(word in theme_lower for word in [
                "both", "two", "mutual", "reciprocal", "cycle", "system",
                "everyone", "all sides", "not just", "also"
            ])
            if has_complexity:
                checks_passed += 1
                strengths.append("Theme has nuance/complexity (not one-sided)")
            else:
                issues.append("Theme may be one-sided or simplistic")
                suggestions.append("Consider adding nuance: the theme should challenge BOTH sides, not just one")
        checks_total += 1

        match_score = checks_passed / checks_total if checks_total > 0 else 0.5
        final_score = max(0.0, min(10.0, match_score * 10))

        notes = f"Theme score: {final_score:.1f}/10. "
        preachiness_str = f"{preachiness_ratio:.0%}" if total_lines > 0 else "N/A"
        notes += f"Theme: '{concept.theme or 'N/A'}'. Metaphor: '{concept.social_metaphor or 'N/A'}'. "
        notes += f"Preachiness: {preachiness_str}."

        return PatternScore(
            analyzer_name="Theme Analyzer",
            category="theme",
            score=final_score,
            confidence=0.75,
            notes=notes,
            specific_issues=list(set(issues)),
            strengths=list(set(strengths)),
            suggestions=list(set(suggestions)),
        )


# =============================================================================
# Unified Pattern Recognizer
# =============================================================================

class PatternRecognizer:
    """Unified interface that runs all analyzers and returns scores."""

    def __init__(self, library: Optional[PatternLibrary] = None, use_memory: bool = True):
        self.library = library or PatternLibrary()
        self.structure = StructureAnalyzer(self.library)
        self.character = CharacterArcAnalyzer(self.library)
        self.emotion = EmotionalArcAnalyzer(self.library)
        self.pacing = PacingAnalyzer(self.library)
        self.theme = ThemeAnalyzer(self.library)
        self.use_memory = use_memory
        self._ltm = None

    def _get_ltm(self):
        """Lazy-load long-term memory."""
        if self._ltm is None and self.use_memory:
            try:
                from system4.long_term_memory import LongTermMemory
                self._ltm = LongTermMemory()
            except Exception:
                self.use_memory = False
        return self._ltm

    def _query_memory_context(self, concept: "Concept") -> list[str]:
        """Query LTM for similar past evaluations to enrich analysis."""
        ltm = self._get_ltm()
        if not ltm:
            return []
        
        try:
            # Search for similar themes and character arcs
            query_parts = [getattr(concept, 'theme', ''), getattr(concept, 'logline', '')]
            query = " ".join(p for p in query_parts if p)
            if not query:
                query = getattr(concept, 'title', '')
            
            results = ltm.search(query, doc_types=["evaluation", "post_mortem"], n_results=3)
            
            context = []
            for r in results:
                # Include top results regardless of absolute threshold
                # (relative ranking matters more with small datasets)
                snippet = r.text[:150].replace("\n", " ")
                context.append(f"[Past {r.doc_type} — {r.score:.0%} match] {snippet}...")
            
            return context
        except Exception:
            return []

    def analyze(self, concept: "Concept", prototype: "Prototype") -> dict[str, PatternScore]:
        from system3.evolution_engine import Concept, Prototype
        """Run all analyzers and return scores by category."""
        
        results = {
            "structure": self.structure.analyze(concept, prototype),
            "character": self.character.analyze(concept, prototype),
            "emotion": self.emotion.analyze(concept, prototype),
            "pacing": self.pacing.analyze(concept, prototype),
            "theme": self.theme.analyze(concept, prototype),
        }
        
        # Enrich with memory context if available
        if self.use_memory:
            memory_context = self._query_memory_context(concept)
            if memory_context:
                for category, score in results.items():
                    # Append memory hints to notes (don't change scores)
                    memory_hint = " | ".join(memory_context[:2])
                    score.notes += f"\n[Memory] Similar past evaluations: {memory_hint}"
        
        return results

    def get_combined_score(self, results: dict[str, PatternScore]) -> float:
        """Calculate weighted combined score from all analyzers."""
        weights = {
            "structure": 0.25,
            "character": 0.15,
            "emotion": 0.25,
            "pacing": 0.15,
            "theme": 0.20,
        }
        total = sum(
            results[cat].score * weight
            for cat, weight in weights.items()
            if cat in results
        )
        return total

    def get_all_issues(self, results: dict[str, PatternScore]) -> list[str]:
        """Collect all issues across analyzers."""
        issues = []
        for score in results.values():
            issues.extend(score.specific_issues)
        return issues

    def get_all_suggestions(self, results: dict[str, PatternScore]) -> list[str]:
        """Collect all suggestions across analyzers."""
        suggestions = []
        for score in results.values():
            suggestions.extend(score.suggestions)
        return suggestions
