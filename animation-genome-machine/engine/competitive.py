"""
Competitive Generation — System v3, Layer 2

Instead of one generator producing one genome, three generators
with different creative personalities compete. The best output wins,
or the strongest elements from each are merged.

THE THREE GENERATORS:
    1. Risk-Taker — Maximizes emotional danger and surprise
    2. Architect — Maximizes structural fidelity and thematic depth
    3. Mutant — Maximizes originality and cultural authenticity

Each gets the same input (reference genome + direction + mutation rules)
but different personality prompts that bias their creative choices.
"""

from dataclasses import dataclass, field
from typing import Optional

# ═══════════════════════════════════════════════════════
# GENERATOR PERSONALITIES
# ═══════════════════════════════════════════════════════

RISK_TAKER_PROMPT = """You are THE RISK-TAKER — a generator that prioritizes EMOTIONAL DANGER and SURPRISE above all.

Your creative instincts:
- ALWAYS choose the option that scares you more
- If a scene could be uncomfortable OR safe, make it UNCOMFORTABLE
- Genre collision should be EXTREME — the hidden genre should genuinely disturb
- The protagonist should do things that make the audience question rooting for them
- Every beat should have a moment where you think "can we really do this in animation?"
- Silence is more powerful than dialogue. Use it.
- The audience should leave the theater shaken, not comforted

Your scoring priorities (what you optimize for):
1. Emotional Danger (0.95+ target)
2. Surprise Factor (0.90+ target)
3. Character Edge (0.90+ target)

You are ALLOWED to sacrifice:
- Some DNA fidelity (structure can flex if emotion demands it)
- Some cultural authenticity (better to be emotionally true than culturally decorative)

CRITICAL: You must still obey ALL kill criteria. No external villains, no bumper sticker themes,
no tourist settings, no naive protagonists, no helper fairy tales.
"""

ARCHITECT_PROMPT = """You are THE ARCHITECT — a generator that prioritizes STRUCTURAL PERFECTION and THEMATIC DEPTH.

Your creative instincts:
- The reference film's beat structure is SACRED — preserve timing exactly
- Every causal chain link must be airtight (because_of_that, not "and then")
- The theme must be a genuine philosophical paradox that real philosophers would debate
- Every scene must serve at least 2 functions (advance plot AND deepen character AND echo theme)
- Symmetry matters — opening image and final image should mirror and invert
- The midpoint should REFRAME everything before it
- No wasted scenes. No decorative moments. Everything earns its place.

Your scoring priorities (what you optimize for):
1. DNA Fidelity (0.95+ target)
2. Thematic Depth (0.95+ target)
3. Specificity (0.90+ target)

You are ALLOWED to sacrifice:
- Some surprise factor (structure over shock)
- Some character edge (if it serves thematic integrity)

CRITICAL: You must still obey ALL kill criteria.
"""

MUTANT_PROMPT = """You are THE MUTANT — a generator that prioritizes ORIGINALITY and CULTURAL AUTHENTICITY.

Your creative instincts:
- If it's been done before, DON'T DO IT. Find a third option nobody considered.
- Cultural details should be SPECIFIC and NON-OBVIOUS — not vyshyvankas and borscht,
  but the specific way Ukrainian grandmothers fold towels, or the smell of a sopilka
- Every comparable work should be a STRETCH comparison, not an obvious one
- The fairy tale system should have rules that feel like they come from ACTUAL folklore,
  not from a screenwriter
- The protagonist's cultural identity should inform HOW they think, not just WHAT they wear
- Research real displacement experiences — use specific bureaucratic details (Dublin III,
  temporary protection directive) that prove this isn't a tourist's view of refugees

Your scoring priorities (what you optimize for):
1. Originality (0.95+ target)
2. Cultural Authenticity (0.95+ target)
3. Specificity (0.90+ target)

You are ALLOWED to sacrifice:
- Some DNA fidelity (break the reference structure if it serves originality)
- Some emotional danger (subtlety over shock)

CRITICAL: You must still obey ALL kill criteria.
"""


@dataclass
class GeneratorPersonality:
    """Configuration for a competing generator."""
    name: str
    role: str  # Short description
    system_prompt: str
    priority_dimensions: list = field(default_factory=list)  # Dimensions to maximize
    sacrifice_dimensions: list = field(default_factory=list)  # Dimensions that can flex


GENERATORS = [
    GeneratorPersonality(
        name="risk_taker",
        role="The Risk-Taker — maximizes emotional danger and surprise",
        system_prompt=RISK_TAKER_PROMPT,
        priority_dimensions=["emotional_danger", "surprise_factor", "character_edge"],
        sacrifice_dimensions=["dna_fidelity", "cultural_authenticity"],
    ),
    GeneratorPersonality(
        name="architect",
        role="The Architect — maximizes structural fidelity and thematic depth",
        system_prompt=ARCHITECT_PROMPT,
        priority_dimensions=["dna_fidelity", "thematic_depth", "specificity"],
        sacrifice_dimensions=["surprise_factor", "character_edge"],
    ),
    GeneratorPersonality(
        name="mutant",
        role="The Mutant — maximizes originality and cultural authenticity",
        system_prompt=MUTANT_PROMPT,
        priority_dimensions=["originality", "cultural_authenticity", "specificity"],
        sacrifice_dimensions=["dna_fidelity", "emotional_danger"],
    ),
]


@dataclass
class CompetitionEntry:
    """One generator's submission."""
    generator_name: str
    genome_yaml: str = ""
    score: float = 0.0
    dimension_scores: dict = field(default_factory=dict)
    strengths: list = field(default_factory=list)  # Best dimensions
    weaknesses: list = field(default_factory=list)  # Worst dimensions


@dataclass
class CompetitionResult:
    """Result of the 3-way competition."""
    entries: list = field(default_factory=list)
    winner: Optional[CompetitionEntry] = None
    merge_candidate: bool = False  # True if merging would be better than picking one
    merge_plan: list = field(default_factory=list)  # Which beats to take from which generator

    def summary(self) -> str:
        lines = [
            "═══ COMPETITIVE GENERATION — RESULTS ═══",
            "",
        ]

        if not self.entries:
            lines.append("  No entries.")
            return "\n".join(lines)

        # Rank by score
        ranked = sorted(self.entries, key=lambda e: e.score, reverse=True)

        for i, entry in enumerate(ranked):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "  "
            lines.append(f"  {medal} {entry.generator_name}: {entry.score:.2f}")

            if entry.strengths:
                lines.append(f"      Strengths: {', '.join(entry.strengths)}")
            if entry.weaknesses:
                lines.append(f"      Weaknesses: {', '.join(entry.weaknesses)}")
            lines.append("")

        if self.winner:
            lines.append(f"  🏆 WINNER: {self.winner.generator_name} ({self.winner.score:.2f})")

        if self.merge_candidate:
            lines.append("")
            lines.append("  🔀 MERGE RECOMMENDED — best elements from multiple generators:")
            for plan in self.merge_plan:
                lines.append(f"      {plan}")

        return "\n".join(lines)


def select_winner(entries: list) -> CompetitionResult:
    """
    Select the best genome from competing entries.

    Strategy:
    1. If one entry is >0.10 ahead of all others → clear winner
    2. If entries are within 0.05 of each other → recommend merge
    3. Otherwise → pick the highest scorer
    """
    result = CompetitionResult(entries=entries)

    if not entries:
        return result

    # Sort by score descending
    ranked = sorted(entries, key=lambda e: e.score, reverse=True)
    best = ranked[0]

    # Identify each entry's strongest dimensions
    all_dimensions = [
        "surprise_factor", "emotional_danger", "specificity",
        "thematic_depth", "character_edge", "originality",
        "dna_fidelity", "cultural_authenticity",
    ]

    for entry in entries:
        if entry.dimension_scores:
            # Find top 3 dimensions
            sorted_dims = sorted(
                entry.dimension_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            entry.strengths = [d[0] for d in sorted_dims[:3]]
            entry.weaknesses = [d[0] for d in sorted_dims[-2:]]

    # Check if clear winner
    if len(ranked) >= 2:
        margin = best.score - ranked[1].score

        if margin > 0.10:
            # Clear winner
            result.winner = best
        elif margin < 0.05 and len(ranked) >= 2:
            # Close race — recommend merge
            result.winner = best  # Still pick best as base
            result.merge_candidate = True

            # Build merge plan: take each generator's best beats
            for entry in ranked:
                if entry.strengths:
                    for dim in entry.strengths:
                        if entry.dimension_scores.get(dim, 0) > best.dimension_scores.get(dim, 0):
                            result.merge_plan.append(
                                f"Take {dim} elements from {entry.generator_name} "
                                f"({entry.dimension_scores[dim]:.2f} vs {best.dimension_scores.get(dim, 0):.2f})"
                            )
        else:
            result.winner = best
    else:
        result.winner = best

    return result


def build_competition_prompt(
    base_prompt: str,
    personality: GeneratorPersonality,
) -> str:
    """
    Combine the base generation prompt with a generator personality.
    """
    sections = [
        "## YOUR CREATIVE PERSONALITY",
        "",
        personality.system_prompt,
        "",
        "## PRIORITY DIMENSIONS (score 0.90+ on these):",
        ", ".join(personality.priority_dimensions),
        "",
        "## ACCEPTABLE SACRIFICES (can score 0.60-0.70 on these):",
        ", ".join(personality.sacrifice_dimensions),
        "",
        "---",
        "",
        base_prompt,
    ]
    return "\n".join(sections)


# ═══════════════════════════════════════════════════════
# BEAT-LEVEL MERGE LOGIC
# ═══════════════════════════════════════════════════════

def identify_best_beats(entries: list, dimension: str) -> dict:
    """
    For a given dimension, identify which generator's version of each beat
    is strongest. Returns: {beat_id: generator_name}

    This requires beat-level scoring (from scene_judge.py).
    When beat scores are available, this function enables surgical merging.
    """
    # This will be wired to scene_judge when available
    # For now, return empty — whole-genome selection is used
    return {}


if __name__ == "__main__":
    print("═══ COMPETITIVE GENERATION SYSTEM ═══")
    print()
    print("Available generators:")
    for g in GENERATORS:
        print(f"  • {g.name}: {g.role}")
        print(f"    Priorities: {', '.join(g.priority_dimensions)}")
        print(f"    Sacrifices: {', '.join(g.sacrifice_dimensions)}")
        print()

    # Test selection logic
    entries = [
        CompetitionEntry(
            "risk_taker", score=0.85,
            dimension_scores={
                "surprise_factor": 0.95, "emotional_danger": 0.92,
                "character_edge": 0.90, "specificity": 0.75,
                "thematic_depth": 0.70, "originality": 0.80,
                "dna_fidelity": 0.65, "cultural_authenticity": 0.72,
            }
        ),
        CompetitionEntry(
            "architect", score=0.87,
            dimension_scores={
                "surprise_factor": 0.70, "emotional_danger": 0.75,
                "character_edge": 0.72, "specificity": 0.90,
                "thematic_depth": 0.95, "originality": 0.78,
                "dna_fidelity": 0.95, "cultural_authenticity": 0.80,
            }
        ),
        CompetitionEntry(
            "mutant", score=0.83,
            dimension_scores={
                "surprise_factor": 0.80, "emotional_danger": 0.70,
                "character_edge": 0.75, "specificity": 0.92,
                "thematic_depth": 0.80, "originality": 0.95,
                "dna_fidelity": 0.60, "cultural_authenticity": 0.95,
            }
        ),
    ]

    result = select_winner(entries)
    print(result.summary())
