"""
Scene-Level Judgment Engine — Beat-by-beat scoring.

Parses beats from a genome YAML and scores EACH beat independently
on the same 8 dimensions used by the genome-level judgment engine.

KEY CONCEPT: Weakest Link Rule
  effective_score = overall_average * 0.6 + weakest_beat_score * 0.4
  One bad beat drags the whole film down.

DIMENSIONS (per beat):
  1. surprise_factor       — Does this beat subvert expectations?
  2. emotional_danger      — Are the stakes real in THIS moment?
  3. specificity           — Sensory grounding (smell, sound, time, address)
  4. thematic_depth        — Does this beat engage the paradox?
  5. character_edge        — Does the protagonist do something uncomfortable?
  6. originality           — Is this beat's scenario fresh?
  7. dna_fidelity          — Does this beat match reference film structure?
  8. cultural_authenticity  — Are cultural elements genuine, not decorative?
"""

from dataclasses import dataclass, field
from typing import Optional
import re
import yaml


# ═══════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════

DIMENSIONS = [
    'surprise_factor', 'emotional_danger', 'specificity', 'thematic_depth',
    'character_edge', 'originality', 'dna_fidelity', 'cultural_authenticity',
]

WEIGHTS = {
    'surprise_factor': 0.20,
    'emotional_danger': 0.15,
    'specificity': 0.10,
    'thematic_depth': 0.15,
    'character_edge': 0.10,
    'originality': 0.15,
    'dna_fidelity': 0.10,
    'cultural_authenticity': 0.05,
}


@dataclass
class BeatScore:
    """Score for a single narrative beat."""

    beat_id: str = ""
    beat_name: str = ""
    beat_type: str = ""

    # Dimension scores (0.0–1.0)
    surprise_factor: float = 0.0
    emotional_danger: float = 0.0
    specificity: float = 0.0
    thematic_depth: float = 0.0
    character_edge: float = 0.0
    originality: float = 0.0
    dna_fidelity: float = 0.0
    cultural_authenticity: float = 0.0

    weaknesses: list = field(default_factory=list)
    strengths: list = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        total = sum(
            getattr(self, dim) * WEIGHTS[dim]
            for dim in DIMENSIONS
        )
        return round(total, 3)

    def dim_dict(self) -> dict:
        return {d: getattr(self, d) for d in DIMENSIONS}


@dataclass
class BeatReport:
    """Full beat-level analysis of a genome."""

    beats: list = field(default_factory=list)            # list[BeatScore]
    weakest_beats: list = field(default_factory=list)     # 3 lowest
    strongest_beats: list = field(default_factory=list)   # 3 highest
    effective_score: float = 0.0
    beat_ranking: list = field(default_factory=list)      # [(beat_id, score)] ascending
    surgical_prescriptions: dict = field(default_factory=dict)  # beat_id → str
    comparative_deltas: dict = field(default_factory=dict)      # beat_id → {dim: delta}

    def summary(self) -> str:
        """Human-readable beat report."""
        lines = [
            "═══ SCENE-LEVEL JUDGMENT — BEAT REPORT ═══",
            "",
        ]

        # Effective score
        if self.beats:
            avg = sum(b.overall_score for b in self.beats) / len(self.beats)
            lines.append(f"  Overall Average:  {avg:.3f}")
            if self.weakest_beats:
                lines.append(f"  Weakest Beat:     {self.weakest_beats[0].overall_score:.3f}  ({self.weakest_beats[0].beat_id})")
            lines.append(f"  Effective Score:  {self.effective_score:.3f}  (avg×0.6 + weakest×0.4)")
        lines.append("")

        # Beat-by-beat
        lines.append("─── BEAT-BY-BEAT SCORES ───")
        lines.append("")
        for bs in self.beats:
            verdict = _verdict_emoji(bs.overall_score)
            lines.append(f"  {verdict} {bs.beat_id} — {bs.beat_name}")
            lines.append(f"     Type: {bs.beat_type}   Score: {bs.overall_score:.3f}")
            dims = bs.dim_dict()
            dim_strs = [f"{d[:3]}={v:.2f}" for d, v in dims.items()]
            lines.append(f"     {' | '.join(dim_strs)}")
            if bs.strengths:
                lines.append(f"     ✅ {', '.join(bs.strengths[:2])}")
            if bs.weaknesses:
                lines.append(f"     ❌ {', '.join(bs.weaknesses[:2])}")
            lines.append("")

        # Ranking
        lines.append("─── BEAT RANKING (weakest → strongest) ───")
        lines.append("")
        for i, (bid, sc) in enumerate(self.beat_ranking, 1):
            bar = _bar(sc)
            lines.append(f"  {i:2d}. {bar} {sc:.3f}  {bid}")
        lines.append("")

        # Surgical prescriptions
        if self.surgical_prescriptions:
            lines.append("─── SURGICAL PRESCRIPTIONS (3 weakest) ───")
            lines.append("")
            for bid, rx in self.surgical_prescriptions.items():
                lines.append(f"  🔧 {bid}:")
                for line in rx.split('\n'):
                    lines.append(f"     {line}")
                lines.append("")

        # Comparative deltas
        if self.comparative_deltas:
            lines.append("─── COMPARATIVE DELTAS vs REFERENCE ───")
            lines.append("")
            for bid, deltas in self.comparative_deltas.items():
                wins = [d for d, v in deltas.items() if v > 0]
                losses = [d for d, v in deltas.items() if v < 0]
                lines.append(f"  {bid}:")
                if wins:
                    lines.append(f"     ▲ WINS: {', '.join(wins)}")
                if losses:
                    lines.append(f"     ▼ LOSES: {', '.join(losses)}")
                detail = [f"{d}={v:+.2f}" for d, v in deltas.items()]
                lines.append(f"     Δ {' | '.join(detail)}")
                lines.append("")

        return "\n".join(lines)


def _verdict_emoji(score: float) -> str:
    if score >= 0.80:
        return "🟢"
    elif score >= 0.60:
        return "🟡"
    else:
        return "🔴"


def _bar(value: float, width: int = 20) -> str:
    filled = int(value * width)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}]"


# ═══════════════════════════════════════════════════════
# YAML PARSING
# ═══════════════════════════════════════════════════════

def _parse_beats(genome_yaml: str) -> list:
    """Extract beats from a genome YAML string. Returns list of dicts."""
    data = yaml.safe_load(genome_yaml)
    if not data:
        return []
    beats = data.get('narrative_dna', {}).get('beats', [])
    return beats if beats else []


# ═══════════════════════════════════════════════════════
# HEURISTIC SCORING (per-beat)
# ═══════════════════════════════════════════════════════

# Keyword banks — shared across beats
_SURPRISE_KEYWORDS = [
    "genre", "collision", "subvert", "twist", "unexpected", "invert",
    "but actually", "reveals", "reframes", "ironic", "not what it seems",
    "secretly", "reversal", "misdirection",
]

_DANGER_KEYWORDS = [
    "cruel", "angry", "destroy", "betray", "consume", "lose", "hurt",
    "damage", "break", "wound", "scar", "rage", "spite", "resentment",
    "trauma", "scream", "fear", "terror", "kills", "eats", "burns",
    "drowning", "shame", "guilt", "cry", "crumbles", "panic", "cost",
    "dangerous", "violent", "feeding",
]

_SPECIFICITY_KEYWORDS = [
    "2:", "3:", "4:", "am", "pm",  # times
    "rue ", "strasse", "straße", "street", "avenue", "boulevard",
    "basement", "third floor", "room",
    "smell of", "smell like", "sound of", "taste of",
    "fluorescent", "antiseptic", "concrete", "linoleum", "bleach",
    "styrofoam", "cigarette", "lavender",
    "kaliningrad", "neukölln", "berlin", "calais", "zurich", "kherson",
    "ikea", "kallax", "deutsche bahn",
    "clicks", "buzzes", "peeling",
]

_THEMATIC_KEYWORDS = [
    "paradox", "dilemma", "both sides", "both are", "but also",
    "debatable", "tension", "contradiction", "irreconcilable",
    "neither", "two valid", "carries both", "opposing",
    "theme", "remember", "forget", "carry it",
]

_EDGE_KEYWORDS = [
    "cruel", "selfish", "angry", "mean", "cold", "flat",
    "pushes away", "uncomfortable", "dark", "deliberately",
    "villain of someone", "becomes the villain", "hurts someone",
    "ugly", "spite", "resentful", "bitter",
    "doesn't apologize", "can't bring herself",
]

_ORIGINALITY_KEYWORDS = [
    "pagemaster", "inkheart", "neverending story", "coco",
    "strange world", "book of life", "kubo",
    "similar to", "comparable", "clone",
]

_DNA_KEYWORDS = [
    "maps to", "preserved", "save_the_cat", "cinderella",
    "timestamp_pct", "causal chain", "beat_", "emotional_valence",
    "zootopia", "judy", "nick",
]

_CULTURAL_KEYWORDS = [
    "babusya", "казка", "ukrainian", "vyshyvanka", "bandura",
    "sopilka", "petrykivka", "котигорошко", "мавка", "залізний",
    "розкажи", "пам'ятай", "lullaby", "halyna",
    "displaced", "refugee", "displacement", "resettlement",
]


def _count_hits(text: str, keywords: list) -> int:
    return sum(1 for kw in keywords if kw in text)


def _score_beat(beat: dict) -> BeatScore:
    """Score a single beat using keyword/pattern heuristics."""
    desc = beat.get('description', '')
    name = beat.get('name', '')
    text = (desc + ' ' + name).lower()

    bs = BeatScore(
        beat_id=beat.get('id', 'unknown'),
        beat_name=beat.get('name', 'Unnamed'),
        beat_type=beat.get('type', 'unknown'),
    )

    # ── Surprise Factor ──
    hits = _count_hits(text, _SURPRISE_KEYWORDS)
    # Also reward high arousal beats with surprising content
    arousal = beat.get('emotional_arousal', 0.5)
    bs.surprise_factor = min(0.15 + hits * 0.08 + (arousal * 0.1), 1.0)

    # ── Emotional Danger ──
    hits = _count_hits(text, _DANGER_KEYWORDS)
    # Negative valence amplifies danger
    valence = beat.get('emotional_valence', 0.5)
    danger_bonus = max(0, (0.5 - valence) * 0.15)
    bs.emotional_danger = min(0.05 + hits * 0.04 + danger_bonus, 1.0)

    # ── Specificity ──
    hits = _count_hits(text, _SPECIFICITY_KEYWORDS)
    # Longer descriptions tend to be more specific
    length_bonus = min(len(desc) / 2000.0, 0.15)
    bs.specificity = min(0.05 + hits * 0.05 + length_bonus, 1.0)

    # ── Thematic Depth ──
    hits = _count_hits(text, _THEMATIC_KEYWORDS)
    bs.thematic_depth = min(0.10 + hits * 0.10, 1.0)

    # ── Character Edge ──
    hits = _count_hits(text, _EDGE_KEYWORDS)
    bs.character_edge = min(0.05 + hits * 0.08, 1.0)

    # ── Originality ──
    # Fewer clone-markers = more original. Penalize mentions of existing works.
    clone_hits = _count_hits(text, _ORIGINALITY_KEYWORDS)
    # Mutation notes are positive (show awareness), not penalizing
    mutation_notes = text.count("mutation note")
    bs.originality = max(0.15, min(0.75 + mutation_notes * 0.05 - clone_hits * 0.08, 1.0))

    # ── DNA Fidelity ──
    hits = _count_hits(text, _DNA_KEYWORDS)
    has_timestamp = 'timestamp_pct' in str(beat)
    has_valence = 'emotional_valence' in str(beat)
    struct_bonus = 0.15 if has_timestamp else 0.0
    struct_bonus += 0.10 if has_valence else 0.0
    bs.dna_fidelity = min(0.10 + hits * 0.06 + struct_bonus, 1.0)

    # ── Cultural Authenticity ──
    hits = _count_hits(text, _CULTURAL_KEYWORDS)
    bs.cultural_authenticity = min(0.05 + hits * 0.10, 1.0)

    # ── Strengths / Weaknesses ──
    dims = bs.dim_dict()
    for d, v in sorted(dims.items(), key=lambda x: x[1]):
        if v < 0.35:
            bs.weaknesses.append(f"{d} critically low ({v:.2f})")
        elif v < 0.50:
            bs.weaknesses.append(f"{d} below threshold ({v:.2f})")
    for d, v in sorted(dims.items(), key=lambda x: -x[1]):
        if v >= 0.70:
            bs.strengths.append(f"{d} strong ({v:.2f})")

    return bs


# ═══════════════════════════════════════════════════════
# SURGICAL PRESCRIPTIONS
# ═══════════════════════════════════════════════════════

_FIX_TEMPLATES = {
    'surprise_factor': (
        "This beat is predictable. Add a REVERSAL or GENRE COLLISION.\n"
        "Ask: what would the audience NEVER expect at this moment?\n"
        "Inject an element from a different genre into this scene."
    ),
    'emotional_danger': (
        "The stakes feel safe here. The protagonist must RISK something real.\n"
        "What's the WORST thing that could happen in this moment?\n"
        "Make the audience genuinely afraid — not for the body, for the soul."
    ),
    'specificity': (
        "This beat is too generic. Add SENSORY GROUNDING:\n"
        "- What TIME is it? What does the room SMELL like?\n"
        "- Name a specific street, building, object.\n"
        "- Add at least 3 concrete sensory details."
    ),
    'thematic_depth': (
        "This beat doesn't engage the film's central paradox.\n"
        "Every beat should make the audience feel the TENSION between the two sides.\n"
        "How does this moment argue FOR and AGAINST the theme simultaneously?"
    ),
    'character_edge': (
        "The protagonist is too safe here. They need to do something UNCOMFORTABLE.\n"
        "Not a mistake — a CHOICE that makes the audience question them.\n"
        "What would make this character hard to like in this moment?"
    ),
    'originality': (
        "This beat feels derivative. It resembles existing films too closely.\n"
        "What makes THIS moment unique to THIS story?\n"
        "Mutate the scenario until it can't be compared to another film."
    ),
    'dna_fidelity': (
        "This beat drifts from the reference film's structural DNA.\n"
        "Check: does the emotional arc shape match? Does the causal chain hold?\n"
        "The STRUCTURE should be felt even when the CONTENT is different."
    ),
    'cultural_authenticity': (
        "Cultural elements are surface-level or absent here.\n"
        "Add details only someone from this culture would know.\n"
        "Make the cultural elements DRIVE the beat, not decorate it."
    ),
}


def _generate_prescription(beat_score: BeatScore) -> str:
    """Generate surgical fix instructions for a weak beat."""
    dims = beat_score.dim_dict()
    # Sort by score ascending — fix the worst first
    sorted_dims = sorted(dims.items(), key=lambda x: x[1])

    lines = []
    for dim, val in sorted_dims[:3]:  # Top 3 worst dimensions
        if val < 0.60:
            lines.append(f"[{dim} = {val:.2f}]")
            lines.append(_FIX_TEMPLATES.get(dim, "Improve this dimension."))
            lines.append("")

    if not lines:
        lines.append("Beat is borderline. Tighten all dimensions incrementally.")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# COMPARATIVE SCORING
# ═══════════════════════════════════════════════════════

def _compute_deltas(target_beats: list, reference_beats: list) -> dict:
    """Compare each target beat against the reference's equivalent beat.

    Matches by index (position in beat sequence). Returns
    {beat_id: {dimension: delta}} where positive = target wins.
    """
    deltas = {}
    for i, tgt in enumerate(target_beats):
        if i >= len(reference_beats):
            break
        ref = reference_beats[i]
        tgt_dims = tgt.dim_dict()
        ref_dims = ref.dim_dict()
        beat_deltas = {}
        for d in DIMENSIONS:
            beat_deltas[d] = round(tgt_dims[d] - ref_dims[d], 3)
        deltas[tgt.beat_id] = beat_deltas
    return deltas


# ═══════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════

def score_beats(genome_yaml: str, reference_yaml: str = '') -> BeatReport:
    """Score every beat in a genome YAML and produce a BeatReport.

    Args:
        genome_yaml: The genome YAML string to score.
        reference_yaml: Optional reference genome for comparative deltas.

    Returns:
        BeatReport with per-beat scores, ranking, prescriptions, and deltas.
    """
    raw_beats = _parse_beats(genome_yaml)
    if not raw_beats:
        report = BeatReport()
        report.beats = []
        report.effective_score = 0.0
        return report

    # Score each beat
    scored = [_score_beat(b) for b in raw_beats]

    # Rank beats (ascending by overall_score)
    ranking = sorted(
        [(bs.beat_id, bs.overall_score) for bs in scored],
        key=lambda x: x[1],
    )

    # Weakest / strongest
    sorted_by_score = sorted(scored, key=lambda bs: bs.overall_score)
    weakest = sorted_by_score[:3]
    strongest = sorted_by_score[-3:][::-1]

    # Effective score (weakest-link rule)
    avg = sum(bs.overall_score for bs in scored) / len(scored)
    weakest_score = sorted_by_score[0].overall_score
    effective = round(avg * 0.6 + weakest_score * 0.4, 3)

    # Surgical prescriptions for 3 weakest
    prescriptions = {}
    for bs in weakest:
        prescriptions[bs.beat_id] = _generate_prescription(bs)

    # Comparative deltas
    comp_deltas = {}
    if reference_yaml:
        ref_beats = _parse_beats(reference_yaml)
        if ref_beats:
            ref_scored = [_score_beat(b) for b in ref_beats]
            comp_deltas = _compute_deltas(scored, ref_scored)

    return BeatReport(
        beats=scored,
        weakest_beats=weakest,
        strongest_beats=strongest,
        effective_score=effective,
        beat_ranking=ranking,
        surgical_prescriptions=prescriptions,
        comparative_deltas=comp_deltas,
    )


# ═══════════════════════════════════════════════════════
# STANDALONE TEST
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 scene_judge.py <genome.yaml> [reference.yaml]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        genome = f.read()

    ref = ''
    if len(sys.argv) >= 3:
        with open(sys.argv[2]) as f:
            ref = f.read()

    report = score_beats(genome, ref)
    print(report.summary())
