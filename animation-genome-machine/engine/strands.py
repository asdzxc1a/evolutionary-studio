"""
Extended Film Genome Strands — Dialogue DNA, World Rules, Audience Psychology

This module EXTENDS the Film Genome Document (see extractor.py) with three
new DNA strands and a per-scene scoring system. It does NOT modify extractor.py.

Strands:
    1. DialogueDNA      — Structured dialogue analysis per character
    2. WorldRules       — Formalized physics of the fairy tale system
    3. AudienceBeatPsych — Per-beat emotional engineering

Utility:
    SceneScorecard — Scores a single beat/scene on all 8 genome dimensions

Usage:
    from engine.strands import DialogueDNA, WorldRules, AudienceBeatPsych, SceneScorecard

    dialogue = DialogueDNA.from_yaml("vault/strands/olenka_dialogue.yaml")
    print(dialogue.summary())

    scorecard = SceneScorecard(beat_id="beat_09", beat_name="Olenka Becomes the Villain")
    scorecard.validate()
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _deep_asdict(obj) -> dict | list | object:
    """Recursively convert dataclass → dict, matching extractor.py convention."""
    if hasattr(obj, "__dataclass_fields__"):
        return {
            fname: _deep_asdict(getattr(obj, fname))
            for fname in obj.__dataclass_fields__
        }
    if isinstance(obj, list):
        return [_deep_asdict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _deep_asdict(v) for k, v in obj.items()}
    return obj


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* to [lo, hi]."""
    return max(lo, min(hi, value))


# ═══════════════════════════════════════════════════════════════════════════════
# STRAND 1: Dialogue DNA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VoicePattern:
    """How a character speaks — cadence, vocabulary, sentence structure."""

    cadence: str = ""
    """Rhythmic pattern: 'staccato', 'flowing', 'halting', etc."""

    vocabulary_level: str = "conversational"
    """Register: 'archaic', 'academic', 'street', 'conversational', 'clinical'."""

    average_sentence_length: str = "medium"
    """'terse' (<5 words), 'medium' (5-15), 'verbose' (15+)."""

    signature_constructions: list[str] = field(default_factory=list)
    """Recurring syntactic patterns (e.g., 'rhetorical questions', 'imperatives')."""


@dataclass
class LanguageMixEntry:
    """One language in a character's repertoire, with usage context."""

    language: str = ""
    """ISO-639 name or common name (e.g., 'Ukrainian', 'German')."""

    proficiency: str = "native"
    """'native', 'fluent', 'functional', 'broken', 'few_words'."""

    used_when: str = ""
    """Context trigger (e.g., 'to the book', 'when forced', 'with Elif')."""


@dataclass
class EmotionalRange:
    """What emotions the character's dialogue can express vs. suppress."""

    expressible: list[str] = field(default_factory=list)
    """Emotions this character CAN voice (e.g., 'anger', 'contempt')."""

    suppressed: list[str] = field(default_factory=list)
    """Emotions this character NEVER voices directly (e.g., 'grief', 'love')."""

    leaks_as: dict[str, str] = field(default_factory=dict)
    """Suppressed emotion → how it leaks (e.g., {'grief': 'sarcasm'})."""


@dataclass
class DialogueDNA:
    """Structured dialogue profile for a single character.

    Captures voice patterns, speech tics, forbidden words, emotional range,
    and the character's multilingual code-switching behaviour.
    """

    character_id: str = ""
    """Must match a character id in the genome (e.g., 'char_olenka')."""

    voice_pattern: VoicePattern = field(default_factory=VoicePattern)
    """How they speak: cadence, register, sentence length."""

    speech_tics: list[str] = field(default_factory=list)
    """Recurring verbal habits (e.g., 'archaic Ukrainian constructions',
    'clicking pen pauses', 'code-switches mid-sentence')."""

    dialogue_samples: list[str] = field(default_factory=list)
    """3 example lines that capture the character's voice. Direct quotes."""

    forbidden_words: list[str] = field(default_factory=list)
    """Words this character would NEVER say — violation = out-of-character."""

    emotional_range: EmotionalRange = field(default_factory=EmotionalRange)
    """What emotions their dialogue can express vs. suppress."""

    language_mix: list[LanguageMixEntry] = field(default_factory=list)
    """Languages they use and when. Order = preference order."""

    # ── Validation ───────────────────────────────────────────────────────

    def validate(self) -> dict[str, list[str]]:
        """Return ``{'errors': [...], 'warnings': [...]}``."""
        errors: list[str] = []
        warnings: list[str] = []

        if not self.character_id:
            errors.append("character_id is required")

        if len(self.dialogue_samples) < 3:
            warnings.append(
                f"Expected 3 dialogue_samples, got {len(self.dialogue_samples)}"
            )

        if not self.language_mix:
            warnings.append("No language_mix entries — every character speaks something")

        valid_vocab = {"archaic", "academic", "street", "conversational", "clinical"}
        if self.voice_pattern.vocabulary_level not in valid_vocab:
            warnings.append(
                f"Unknown vocabulary_level '{self.voice_pattern.vocabulary_level}'; "
                f"expected one of {sorted(valid_vocab)}"
            )

        valid_proficiency = {"native", "fluent", "functional", "broken", "few_words"}
        for entry in self.language_mix:
            if entry.proficiency not in valid_proficiency:
                warnings.append(
                    f"Language '{entry.language}' has unknown proficiency "
                    f"'{entry.proficiency}'; expected one of {sorted(valid_proficiency)}"
                )

        return {"errors": errors, "warnings": warnings}

    # ── Serialization ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return _deep_asdict(self)

    def save(self, path: str) -> None:
        """Write as YAML."""
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            yaml.dump(
                self.to_dict(), f,
                default_flow_style=False, sort_keys=False, allow_unicode=True, width=120,
            )

    @classmethod
    def from_dict(cls, data: dict) -> DialogueDNA:
        """Reconstruct from a plain dict (e.g., loaded from YAML)."""
        vp = VoicePattern(**data.get("voice_pattern", {}))
        er_raw = data.get("emotional_range", {})
        er = EmotionalRange(
            expressible=er_raw.get("expressible", []),
            suppressed=er_raw.get("suppressed", []),
            leaks_as=er_raw.get("leaks_as", {}),
        )
        lm = [LanguageMixEntry(**e) for e in data.get("language_mix", [])]
        return cls(
            character_id=data.get("character_id", ""),
            voice_pattern=vp,
            speech_tics=data.get("speech_tics", []),
            dialogue_samples=data.get("dialogue_samples", []),
            forbidden_words=data.get("forbidden_words", []),
            emotional_range=er,
            language_mix=lm,
        )

    @classmethod
    def from_yaml(cls, path: str) -> DialogueDNA:
        with open(path, "r") as f:
            return cls.from_dict(yaml.safe_load(f))

    # ── Display ──────────────────────────────────────────────────────────

    def summary(self) -> str:
        lines = [
            f"═══ Dialogue DNA: {self.character_id} ═══",
            f"Voice: {self.voice_pattern.cadence} / "
            f"{self.voice_pattern.vocabulary_level} / "
            f"sentences {self.voice_pattern.average_sentence_length}",
        ]
        if self.speech_tics:
            lines.append(f"Tics: {', '.join(self.speech_tics)}")
        if self.forbidden_words:
            lines.append(f"Forbidden: {', '.join(self.forbidden_words)}")
        if self.language_mix:
            langs = [f"{e.language} ({e.proficiency})" for e in self.language_mix]
            lines.append(f"Languages: {', '.join(langs)}")
        if self.dialogue_samples:
            lines.append("Samples:")
            for s in self.dialogue_samples:
                lines.append(f"  \"{s}\"")

        v = self.validate()
        status = "✅ VALID" if not v["errors"] else "❌ ERRORS"
        lines.append(f"Validation: {status}")
        for e in v["errors"]:
            lines.append(f"  ❌ {e}")
        for w in v["warnings"]:
            lines.append(f"  ⚠️  {w}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# STRAND 2: World Rules
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ManifestationCost:
    """What a single manifestation type costs."""

    fairy_tale: str = ""
    """Name of the fairy tale creature (e.g., 'Iron Wolf', 'Mavka')."""

    memory_type_consumed: str = ""
    """Category of memory consumed: 'sensory', 'episodic', 'identity', 'procedural'."""

    example: str = ""
    """Concrete example (e.g., 'the smell of Halyna's kitchen')."""


@dataclass
class EscalationCurve:
    """How manifestation costs increase over time."""

    shape: str = "exponential"
    """'linear', 'exponential', 'stepped', 'logarithmic'."""

    description: str = ""
    """Plain-language description of the progression."""

    breakpoints: list[dict[str, object]] = field(default_factory=list)
    """List of ``{'at': <event/pct>, 'cost_multiplier': <float>, 'note': <str>}``."""


@dataclass
class WorldRules:
    """Formalized physics of the fairy tale manifestation system.

    Defines the internally consistent rules of how fairy tales manifest,
    what they cost, how they escalate, and what hard limits exist.
    These rules are the "physics" the film must never violate.
    """

    manifestation_triggers: dict[str, str] = field(default_factory=dict)
    """Maps emotion → which fairy tale appears.
    e.g., ``{'rage': 'Iron Wolf', 'grief': 'Mavka', 'joy_guilt': 'Firebird'}``
    """

    manifestation_costs: list[ManifestationCost] = field(default_factory=list)
    """What each manifestation costs (specific memory types)."""

    escalation_curve: EscalationCurve = field(default_factory=EscalationCurve)
    """How costs increase over the film's runtime."""

    control_rules: dict[str, object] = field(default_factory=dict)
    """Rules about controlling manifestations.
    Expected keys: ``can_be_controlled`` (bool), ``control_method`` (str),
    ``additional_cost`` (str), ``control_reliability`` (str).
    """

    interaction_rules: dict[str, object] = field(default_factory=dict)
    """Rules about fairy tales interacting with each other.
    Expected keys: ``can_interact`` (bool), ``can_conflict`` (bool),
    ``interaction_effects`` (list[str]).
    """

    hard_limits: dict[str, str] = field(default_factory=dict)
    """Endgame rules.
    Expected keys: ``all_memories_gone`` (what happens?),
    ``all_pages_blank`` (what happens to the book?),
    ``endgame`` (the final state).
    """

    world_consistency_checks: list[str] = field(default_factory=list)
    """Rules that must NEVER be violated. Each entry is a plain-language
    invariant, e.g., 'Manifestations are always involuntary unless a story
    is being actively told to another person.'
    """

    # ── Validation ───────────────────────────────────────────────────────

    def validate(self) -> dict[str, list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        if not self.manifestation_triggers:
            errors.append("manifestation_triggers is empty — need at least one emotion→tale mapping")

        if not self.manifestation_costs:
            warnings.append("No manifestation_costs defined")

        valid_shapes = {"linear", "exponential", "stepped", "logarithmic"}
        if self.escalation_curve.shape not in valid_shapes:
            warnings.append(
                f"Unknown escalation shape '{self.escalation_curve.shape}'; "
                f"expected one of {sorted(valid_shapes)}"
            )

        if not self.world_consistency_checks:
            errors.append("world_consistency_checks is empty — the world needs rules to enforce")

        required_hard_limits = {"all_memories_gone", "all_pages_blank", "endgame"}
        missing = required_hard_limits - set(self.hard_limits.keys())
        if missing:
            warnings.append(f"hard_limits missing keys: {sorted(missing)}")

        return {"errors": errors, "warnings": warnings}

    # ── Serialization ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return _deep_asdict(self)

    def save(self, path: str) -> None:
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            yaml.dump(
                self.to_dict(), f,
                default_flow_style=False, sort_keys=False, allow_unicode=True, width=120,
            )

    @classmethod
    def from_dict(cls, data: dict) -> WorldRules:
        costs = [ManifestationCost(**c) for c in data.get("manifestation_costs", [])]
        esc_raw = data.get("escalation_curve", {})
        esc = EscalationCurve(
            shape=esc_raw.get("shape", "exponential"),
            description=esc_raw.get("description", ""),
            breakpoints=esc_raw.get("breakpoints", []),
        )
        return cls(
            manifestation_triggers=data.get("manifestation_triggers", {}),
            manifestation_costs=costs,
            escalation_curve=esc,
            control_rules=data.get("control_rules", {}),
            interaction_rules=data.get("interaction_rules", {}),
            hard_limits=data.get("hard_limits", {}),
            world_consistency_checks=data.get("world_consistency_checks", []),
        )

    @classmethod
    def from_yaml(cls, path: str) -> WorldRules:
        with open(path, "r") as f:
            return cls.from_dict(yaml.safe_load(f))

    # ── Display ──────────────────────────────────────────────────────────

    def summary(self) -> str:
        lines = [
            "═══ World Rules ═══",
            f"Triggers: {len(self.manifestation_triggers)} emotion→tale mappings",
            f"Costs: {len(self.manifestation_costs)} defined",
            f"Escalation: {self.escalation_curve.shape}",
        ]
        if self.manifestation_triggers:
            for emotion, tale in self.manifestation_triggers.items():
                lines.append(f"  {emotion} → {tale}")
        if self.control_rules:
            controllable = self.control_rules.get("can_be_controlled", "unknown")
            lines.append(f"Control: {'yes' if controllable else 'no'}")
        lines.append(f"Consistency checks: {len(self.world_consistency_checks)}")
        for i, rule in enumerate(self.world_consistency_checks, 1):
            lines.append(f"  {i}. {rule}")

        v = self.validate()
        status = "✅ VALID" if not v["errors"] else "❌ ERRORS"
        lines.append(f"Validation: {status}")
        for e in v["errors"]:
            lines.append(f"  ❌ {e}")
        for w in v["warnings"]:
            lines.append(f"  ⚠️  {w}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# STRAND 3: Audience Psychology
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class InformationAsymmetry:
    """What the audience knows vs. what the character knows."""

    audience_knows: list[str] = field(default_factory=list)
    """Facts the audience has that the character does not."""

    character_knows: list[str] = field(default_factory=list)
    """Facts the character has that the audience does not."""

    effect: str = ""
    """The dramatic effect this gap creates (e.g., 'dramatic irony', 'suspense')."""


@dataclass
class AudienceBeatPsych:
    """Per-beat emotional engineering — what the audience should think and feel.

    This strand exists at the BEAT level, not the character level.
    It encodes the filmmaker's intent for audience manipulation at
    every story beat.
    """

    beat_id: str = ""
    """Must match a beat id in the genome (e.g., 'beat_09')."""

    target_emotion: str = ""
    """What the audience should FEEL (e.g., 'uncomfortable empathy', 'dread')."""

    active_question: str = ""
    """The question in the audience's mind right now
    (e.g., 'Will she apologize to Anna?')."""

    tension_source: str = ""
    """Where the tension is coming from at this beat
    (e.g., 'Olenka hearing Anna cry and not knocking')."""

    information_asymmetry: InformationAsymmetry = field(
        default_factory=InformationAsymmetry
    )
    """What does the audience know that the character doesn't, or vice versa."""

    predicted_reaction: str = ""
    """What we expect the audience to do/feel
    (e.g., 'lean forward', 'hold breath', 'look away')."""

    subversion: str = ""
    """How this beat defies what the audience expects
    (e.g., 'no apology comes — the scene ends on the closed door')."""

    # ── Validation ───────────────────────────────────────────────────────

    def validate(self) -> dict[str, list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        if not self.beat_id:
            errors.append("beat_id is required")
        if not self.target_emotion:
            errors.append("target_emotion is required — what should the audience feel?")
        if not self.active_question:
            warnings.append("No active_question — every beat should plant a question")
        if not self.tension_source:
            warnings.append("No tension_source defined")
        if not self.subversion:
            warnings.append(
                "No subversion — beats that meet expectations exactly are forgettable"
            )

        return {"errors": errors, "warnings": warnings}

    # ── Serialization ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return _deep_asdict(self)

    def save(self, path: str) -> None:
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            yaml.dump(
                self.to_dict(), f,
                default_flow_style=False, sort_keys=False, allow_unicode=True, width=120,
            )

    @classmethod
    def from_dict(cls, data: dict) -> AudienceBeatPsych:
        ia_raw = data.get("information_asymmetry", {})
        ia = InformationAsymmetry(
            audience_knows=ia_raw.get("audience_knows", []),
            character_knows=ia_raw.get("character_knows", []),
            effect=ia_raw.get("effect", ""),
        )
        return cls(
            beat_id=data.get("beat_id", ""),
            target_emotion=data.get("target_emotion", ""),
            active_question=data.get("active_question", ""),
            tension_source=data.get("tension_source", ""),
            information_asymmetry=ia,
            predicted_reaction=data.get("predicted_reaction", ""),
            subversion=data.get("subversion", ""),
        )

    @classmethod
    def from_yaml(cls, path: str) -> AudienceBeatPsych:
        with open(path, "r") as f:
            return cls.from_dict(yaml.safe_load(f))

    # ── Display ──────────────────────────────────────────────────────────

    def summary(self) -> str:
        lines = [
            f"═══ Audience Psychology: {self.beat_id} ═══",
            f"Target emotion: {self.target_emotion}",
            f"Active question: {self.active_question}",
            f"Tension source: {self.tension_source}",
        ]
        if self.information_asymmetry.audience_knows:
            lines.append("Audience knows (character doesn't):")
            for item in self.information_asymmetry.audience_knows:
                lines.append(f"  • {item}")
        if self.information_asymmetry.character_knows:
            lines.append("Character knows (audience doesn't):")
            for item in self.information_asymmetry.character_knows:
                lines.append(f"  • {item}")
        if self.information_asymmetry.effect:
            lines.append(f"Asymmetry effect: {self.information_asymmetry.effect}")
        if self.predicted_reaction:
            lines.append(f"Predicted reaction: {self.predicted_reaction}")
        if self.subversion:
            lines.append(f"Subversion: {self.subversion}")

        v = self.validate()
        status = "✅ VALID" if not v["errors"] else "❌ ERRORS"
        lines.append(f"Validation: {status}")
        for e in v["errors"]:
            lines.append(f"  ❌ {e}")
        for w in v["warnings"]:
            lines.append(f"  ⚠️  {w}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# SceneScorecard — Per-beat scoring on all 8 genome dimensions
# ═══════════════════════════════════════════════════════════════════════════════

# The 8 dimensions, matching the genome-level scorecard in kazka_v2_deep_score.json
SCORECARD_DIMENSIONS = (
    "surprise_factor",
    "emotional_danger",
    "specificity",
    "thematic_depth",
    "character_edge",
    "originality",
    "dna_fidelity",
    "cultural_authenticity",
)


@dataclass
class SceneScorecard:
    """Scores a SINGLE beat/scene on all 8 genome dimensions.

    Same dimensions as the genome-level scorecard but applied per-scene,
    letting you pinpoint exactly which beats are dragging the overall score
    down and which are carrying the film.
    """

    beat_id: str = ""
    """Which beat this scorecard evaluates (e.g., 'beat_09')."""

    beat_name: str = ""
    """Human-readable name (e.g., 'Olenka Becomes the Villain')."""

    # ── The 8 dimensions (0.0 – 1.0) ────────────────────────────────────

    surprise_factor: float = 0.0
    """Does this beat defy expectations? 0 = predictable, 1 = genuinely shocking."""

    emotional_danger: float = 0.0
    """Does this beat risk making the audience uncomfortable? 0 = safe, 1 = devastating."""

    specificity: float = 0.0
    """Are the details concrete and sensory? 0 = generic, 1 = you-were-there vivid."""

    thematic_depth: float = 0.0
    """Does this beat advance or complicate the theme? 0 = irrelevant, 1 = thematically essential."""

    character_edge: float = 0.0
    """Do characters behave in ways that are true but unflattering? 0 = sanitized, 1 = raw."""

    originality: float = 0.0
    """Has this exact beat been done before? 0 = cliché, 1 = never seen this."""

    dna_fidelity: float = 0.0
    """Does this beat honor the source DNA (structure, timing, arc)? 0 = drift, 1 = locked."""

    cultural_authenticity: float = 0.0
    """Would someone from this culture recognize it? 0 = tourist, 1 = insider."""

    # ── Analysis fields ──────────────────────────────────────────────────

    weaknesses: list[str] = field(default_factory=list)
    """Specific issues pulling scores down."""

    strengths: list[str] = field(default_factory=list)
    """Specific elements that elevate the beat."""

    is_weakest_link: bool = False
    """True if this beat has the lowest overall_score in the film."""

    # ── Computed ─────────────────────────────────────────────────────────

    @property
    def overall_score(self) -> float:
        """Arithmetic mean of all 8 dimension scores."""
        scores = [
            self.surprise_factor,
            self.emotional_danger,
            self.specificity,
            self.thematic_depth,
            self.character_edge,
            self.originality,
            self.dna_fidelity,
            self.cultural_authenticity,
        ]
        return sum(scores) / len(scores)

    @property
    def dimension_scores(self) -> dict[str, float]:
        """All 8 dimensions as a name→score dict."""
        return {dim: getattr(self, dim) for dim in SCORECARD_DIMENSIONS}

    @property
    def lowest_dimension(self) -> tuple[str, float]:
        """Return ``(dimension_name, score)`` for the weakest dimension."""
        scores = self.dimension_scores
        name = min(scores, key=scores.get)  # type: ignore[arg-type]
        return name, scores[name]

    # ── Validation ───────────────────────────────────────────────────────

    def validate(self) -> dict[str, list[str]]:
        errors: list[str] = []
        warnings: list[str] = []

        if not self.beat_id:
            errors.append("beat_id is required")
        if not self.beat_name:
            warnings.append("beat_name is empty")

        for dim in SCORECARD_DIMENSIONS:
            val = getattr(self, dim)
            if not isinstance(val, (int, float)):
                errors.append(f"{dim} must be a number, got {type(val).__name__}")
            elif val < 0.0 or val > 1.0:
                errors.append(f"{dim} = {val} — must be in [0.0, 1.0]")

        if self.overall_score < 0.5 and not self.weaknesses:
            warnings.append(
                f"overall_score is {self.overall_score:.2f} but no weaknesses listed — "
                "diagnose what's wrong"
            )

        return {"errors": errors, "warnings": warnings}

    # ── Serialization ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        d = _deep_asdict(self)
        # Inject the computed property so it appears in YAML/JSON output.
        d["overall_score"] = round(self.overall_score, 4)
        return d

    def save(self, path: str) -> None:
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            yaml.dump(
                self.to_dict(), f,
                default_flow_style=False, sort_keys=False, allow_unicode=True, width=120,
            )

    @classmethod
    def from_dict(cls, data: dict) -> SceneScorecard:
        return cls(
            beat_id=data.get("beat_id", ""),
            beat_name=data.get("beat_name", ""),
            surprise_factor=float(data.get("surprise_factor", 0)),
            emotional_danger=float(data.get("emotional_danger", 0)),
            specificity=float(data.get("specificity", 0)),
            thematic_depth=float(data.get("thematic_depth", 0)),
            character_edge=float(data.get("character_edge", 0)),
            originality=float(data.get("originality", 0)),
            dna_fidelity=float(data.get("dna_fidelity", 0)),
            cultural_authenticity=float(data.get("cultural_authenticity", 0)),
            weaknesses=data.get("weaknesses", []),
            strengths=data.get("strengths", []),
            is_weakest_link=data.get("is_weakest_link", False),
        )

    @classmethod
    def from_yaml(cls, path: str) -> SceneScorecard:
        with open(path, "r") as f:
            return cls.from_dict(yaml.safe_load(f))

    # ── Display ──────────────────────────────────────────────────────────

    def summary(self) -> str:
        low_dim, low_val = self.lowest_dimension
        lines = [
            f"═══ Scene Scorecard: {self.beat_name} ({self.beat_id}) ═══",
            f"Overall: {self.overall_score:.2f}",
        ]
        for dim in SCORECARD_DIMENSIONS:
            val = getattr(self, dim)
            bar = "█" * int(val * 10) + "░" * (10 - int(val * 10))
            flag = " ← weakest" if dim == low_dim else ""
            lines.append(f"  {dim:<24s} {val:.2f} {bar}{flag}")

        if self.strengths:
            lines.append("Strengths:")
            for s in self.strengths:
                lines.append(f"  ✦ {s}")
        if self.weaknesses:
            lines.append("Weaknesses:")
            for w in self.weaknesses:
                lines.append(f"  ✗ {w}")
        if self.is_weakest_link:
            lines.append("⚠️  THIS IS THE WEAKEST BEAT IN THE FILM")

        v = self.validate()
        if v["errors"]:
            for e in v["errors"]:
                lines.append(f"  ❌ {e}")
        if v["warnings"]:
            for w in v["warnings"]:
                lines.append(f"  ⚠️  {w}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience: load/save all strands for a genome in one shot
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExtendedGenomeStrands:
    """Container for all extended strands — attaches to a Film Genome Document.

    This is the integration point: load your genome from extractor.py,
    then load extended strands from this class. Keeps the modules decoupled.
    """

    dialogue_profiles: list[DialogueDNA] = field(default_factory=list)
    world_rules: Optional[WorldRules] = None
    audience_psychology: list[AudienceBeatPsych] = field(default_factory=list)
    scene_scorecards: list[SceneScorecard] = field(default_factory=list)

    def validate_all(self) -> dict[str, list[str]]:
        """Run validation across all strands, aggregating results."""
        all_errors: list[str] = []
        all_warnings: list[str] = []

        for dp in self.dialogue_profiles:
            v = dp.validate()
            all_errors.extend(
                f"[DialogueDNA/{dp.character_id}] {e}" for e in v["errors"]
            )
            all_warnings.extend(
                f"[DialogueDNA/{dp.character_id}] {w}" for w in v["warnings"]
            )

        if self.world_rules:
            v = self.world_rules.validate()
            all_errors.extend(f"[WorldRules] {e}" for e in v["errors"])
            all_warnings.extend(f"[WorldRules] {w}" for w in v["warnings"])
        else:
            all_warnings.append("[WorldRules] Not defined")

        for ap in self.audience_psychology:
            v = ap.validate()
            all_errors.extend(
                f"[AudiencePsych/{ap.beat_id}] {e}" for e in v["errors"]
            )
            all_warnings.extend(
                f"[AudiencePsych/{ap.beat_id}] {w}" for w in v["warnings"]
            )

        for sc in self.scene_scorecards:
            v = sc.validate()
            all_errors.extend(
                f"[SceneScorecard/{sc.beat_id}] {e}" for e in v["errors"]
            )
            all_warnings.extend(
                f"[SceneScorecard/{sc.beat_id}] {w}" for w in v["warnings"]
            )

        return {"errors": all_errors, "warnings": all_warnings}

    def to_dict(self) -> dict:
        return {
            "dialogue_profiles": [dp.to_dict() for dp in self.dialogue_profiles],
            "world_rules": self.world_rules.to_dict() if self.world_rules else None,
            "audience_psychology": [ap.to_dict() for ap in self.audience_psychology],
            "scene_scorecards": [sc.to_dict() for sc in self.scene_scorecards],
        }

    def save(self, path: str) -> None:
        """Save all extended strands as a single YAML file."""
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            yaml.dump(
                self.to_dict(), f,
                default_flow_style=False, sort_keys=False, allow_unicode=True, width=120,
            )

    @classmethod
    def from_dict(cls, data: dict) -> ExtendedGenomeStrands:
        dps = [DialogueDNA.from_dict(d) for d in data.get("dialogue_profiles", [])]
        wr = (
            WorldRules.from_dict(data["world_rules"])
            if data.get("world_rules")
            else None
        )
        aps = [
            AudienceBeatPsych.from_dict(a)
            for a in data.get("audience_psychology", [])
        ]
        scs = [
            SceneScorecard.from_dict(s)
            for s in data.get("scene_scorecards", [])
        ]
        return cls(
            dialogue_profiles=dps,
            world_rules=wr,
            audience_psychology=aps,
            scene_scorecards=scs,
        )

    @classmethod
    def from_yaml(cls, path: str) -> ExtendedGenomeStrands:
        with open(path, "r") as f:
            return cls.from_dict(yaml.safe_load(f))

    def summary(self) -> str:
        v = self.validate_all()
        status = "✅ ALL VALID" if not v["errors"] else "❌ ERRORS"
        lines = [
            "═══ Extended Genome Strands ═══",
            f"Dialogue profiles: {len(self.dialogue_profiles)}",
            f"World rules: {'defined' if self.world_rules else 'NOT defined'}",
            f"Audience psychology beats: {len(self.audience_psychology)}",
            f"Scene scorecards: {len(self.scene_scorecards)}",
            f"Validation: {status}",
        ]
        for e in v["errors"]:
            lines.append(f"  ❌ {e}")
        for w in v["warnings"]:
            lines.append(f"  ⚠️  {w}")
        return "\n".join(lines)
