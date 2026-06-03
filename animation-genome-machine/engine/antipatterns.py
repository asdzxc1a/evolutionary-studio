"""
Anti-Pattern Database — System v3, Layer 4

Cataloged failures from v1 and the judgment engine,
with specific fixes and example injections.
Every failure we've seen gets recorded so the system
never repeats the same mistake.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AntiPattern:
    """A cataloged creative failure with its fix."""
    id: str
    name: str
    description: str
    kill_criterion: str  # Which kill criterion it triggers
    dimension_affected: str  # Which dimension it damages
    severity: str  # "kill" or "degrade"
    detection_keywords: list = field(default_factory=list)
    fix_strategy: str = ""
    fix_example: str = ""
    source: str = ""  # Where this was first observed (e.g., "kazka_v1")


# ═══════════════════════════════════════════════════════
# THE DATABASE — Every failure we've seen
# ═══════════════════════════════════════════════════════

ANTI_PATTERNS = [
    # ─── KILL-LEVEL PATTERNS ───

    AntiPattern(
        id="AP001",
        name="Corporate Villain",
        description="The antagonist is a generic corporation, shadowy organization, or faceless institution.",
        kill_criterion="kill_corporate_villain",
        dimension_affected="originality",
        severity="kill",
        detection_keywords=["corporation", "shadowy", "the archivist", "dark lord",
                            "evil organization", "secret society", "dark force"],
        fix_strategy="Remove all external villains. The conflict must be INTERNAL — protagonist vs. their own trauma, identity, or choices. The most dangerous person in the story should be the protagonist.",
        fix_example="Pan's Labyrinth: No corporate villain. The real monster is Captain Vidal, but the deeper antagonist is Ofelia's refusal to accept reality. Kazka v2: No villain at all — Olenka IS the antagonist of Anna's story.",
        source="kazka_v1",
    ),

    AntiPattern(
        id="AP002",
        name="Bumper Sticker Theme",
        description="The theme can be summarized as a greeting card platitude.",
        kill_criterion="kill_bumper_sticker_theme",
        dimension_affected="thematic_depth",
        severity="kill",
        detection_keywords=["stories matter", "be yourself", "believe in yourself",
                            "follow your dream", "anyone can be anything",
                            "love conquers all", "the power of friendship"],
        fix_strategy="Replace the theme with a genuine PARADOX — two valid, contradictory positions that the film argues simultaneously. The audience should leave debating, not nodding.",
        fix_example="Kazka v2: 'To heal, you must remember. But remembering is what keeps the wound open.' Side A (therapist): forget and move forward. Side B (grandmother): remember everything. The film argues BOTH honestly.",
        source="kazka_v1",
    ),

    AntiPattern(
        id="AP003",
        name="Naive Protagonist",
        description="The main character is good-hearted, optimistic, pure, and never does anything genuinely wrong.",
        kill_criterion="kill_naive_protagonist",
        dimension_affected="character_edge",
        severity="kill",
        detection_keywords=["good but naive", "innocent and kind", "pure of heart",
                            "wide-eyed wonder", "innocent girl"],
        fix_strategy="Give the protagonist a GENUINE flaw that causes real harm to an innocent person. They should be the villain of someone else's story for at least one scene. The audience should be uncomfortable rooting for them.",
        fix_example="Kazka v2: Olenka tells a 10-year-old that her problems aren't real. The child cries in the bathroom. Olenka hears it and can't bring herself to apologize. She is CRUEL — and the cruelty comes from real pain.",
        source="kazka_v1",
    ),

    AntiPattern(
        id="AP004",
        name="Tourist Settings",
        description="Locations are famous landmarks or postcard views rather than specific, lived-in places.",
        kill_criterion="kill_tourism_setting",
        dimension_affected="specificity",
        severity="kill",
        detection_keywords=["the eiffel tower", "the louvre", "big ben",
                            "times square", "the alps were majestic",
                            "beautiful countryside", "picturesque village"],
        fix_strategy="Replace every landmark with a SPECIFIC, unglamorous, sensory-rich location. Name the street. Describe the smell. What time is it? What's the weather? What sounds do you hear?",
        fix_example="Kazka v2: NOT 'France' but 'A refugee processing center basement in Calais, 2AM, February. Fluorescent lights that buzz at 50Hz. Bleach on concrete. Instant coffee in styrofoam.'",
        source="kazka_v1",
    ),

    AntiPattern(
        id="AP005",
        name="Helper Fairy Tales",
        description="Fairy tale creatures are cute, helpful allies who guide the protagonist.",
        kill_criterion="kill_helper_fairy_tales",
        dimension_affected="surprise_factor",
        severity="kill",
        detection_keywords=["helps her", "comes to her aid", "friendly fairy",
                            "magical helper", "guides her"],
        fix_strategy="Fairy tales should be DANGEROUS, involuntary, pre-moral. They don't understand modern ethics. Every manifestation has a COST. The protagonist doesn't control them — they're panic attacks in narrative form.",
        fix_example="Kazka v2: When Olenka lies, Lys makes EVERYONE lie. The neighbor tells his wife he doesn't love her. Consequences are real. Every manifestation costs a memory.",
        source="kazka_v1",
    ),

    AntiPattern(
        id="AP006",
        name="Seen-Before Story",
        description="The story is recognizably close to an existing film or book.",
        kill_criterion="kill_seen_before",
        dimension_affected="originality",
        severity="kill",
        detection_keywords=["pagemaster", "inkheart", "neverending story",
                            "the book of life", "strange world"],
        fix_strategy="Identify the closest comparable work. Name exactly what's similar. Then MUTATE the similar elements until the comparison breaks. The goal: 7 comparables, none a close match.",
        fix_example="Deep judge comparables for Kazka v2: Pan's Labyrinth, A Monster Calls, The Breadwinner, Inside Out, Flee, Persepolis, Spirited Away — 7 comparables, none a close match because the specific combination is original.",
        source="kazka_v1",
    ),

    # ─── DEGRADATION PATTERNS (not kills, but score damage) ───

    AntiPattern(
        id="AP007",
        name="Invisible Mother",
        description="A parent figure exists in the story but has no arc, no agency, no confrontation with the protagonist.",
        kill_criterion="",
        dimension_affected="character_edge",
        severity="degrade",
        detection_keywords=[],
        fix_strategy="Give the parent their own paradox. They should confront the protagonist at least once. They should say something the protagonist doesn't want to hear. They are living the same displacement — their silence isn't passive, it's a survival strategy.",
        fix_example="Add a scene: Mother says 'I'm doing everything I can and you're making it impossible.' Olenka says something she can't take back.",
        source="kazka_v2_deep_review",
    ),

    AntiPattern(
        id="AP008",
        name="Convenience Character",
        description="A supporting character exists only to serve plot functions — helping, explaining, or connecting scenes — without their own desires or pain.",
        kill_criterion="",
        dimension_affected="character_edge",
        severity="degrade",
        detection_keywords=[],
        fix_strategy="Give them ONE scene where they push back, reveal their own pain, or refuse to help. A character who only serves the protagonist isn't a character — they're a prop.",
        fix_example="Elif (Turkish-German friend): Instead of just helping organize the community center, she tells Olenka about her own displacement — her parents' Turkey stories, the things she's lost.",
        source="kazka_v2_deep_review",
    ),

    AntiPattern(
        id="AP009",
        name="Vague Ending Location",
        description="The final scene is set in a deliberately unspecified location ('a city', 'somewhere').",
        kill_criterion="",
        dimension_affected="specificity",
        severity="degrade",
        detection_keywords=["somewhere", "it doesn't matter which", "a city",
                            "any city", "an unnamed"],
        fix_strategy="Name it. The story's geographic arc should complete — the final location should echo or invert the opening. If the opening was Kherson, the ending shouldn't escape to a generic 'somewhere.'",
        fix_example="Keep her in Berlin. The story started in Ukraine, traveled through Europe, and should land where she chose to stay — not drift to the US as a Hollywood reflex.",
        source="kazka_v2_deep_review",
    ),

    AntiPattern(
        id="AP010",
        name="Repetitive Manifestation Pattern",
        description="Multiple fairy tale manifestations follow the same pattern: emotion → manifestation → cost. The pattern becomes predictable.",
        kill_criterion="",
        dimension_affected="surprise_factor",
        severity="degrade",
        detection_keywords=[],
        fix_strategy="Break the pattern on the 3rd or 4th manifestation. Change WHAT gets lost — not a memory of grandmother, but a memory of SELF. Change WHO's affected. Change the timing — make one happen when she's NOT emotional.",
        fix_example="Third manifestation costs Olenka a memory of herself — her own middle name, or what her bedroom looked like. This signals the escalation is non-linear.",
        source="kazka_v2_deep_review",
    ),

    AntiPattern(
        id="AP011",
        name="Hand-Waved Displacement",
        description="The bureaucratic reality of displacement is glossed over. The character 'just ends up' in different countries without explanation.",
        kill_criterion="",
        dimension_affected="cultural_authenticity",
        severity="degrade",
        detection_keywords=[],
        fix_strategy="Add ONE line about legal status — temporary protection directive, Dublin III regulation, asylum claim transfer. The displacement route needs a single sentence justifying each transfer.",
        fix_example="'Their TPD placement in Calais collapsed after the processing center incident. The asylum claim was transferred under Dublin III to Switzerland, then to Germany when the Swiss system flagged her case as requiring specialized child services.'",
        source="kazka_v2_deep_review",
    ),
]


def find_patterns_in_text(text: str) -> list:
    """
    Scan text for anti-patterns.
    Returns list of (AntiPattern, matched_keyword).
    """
    text_lower = text.lower()
    found = []

    for ap in ANTI_PATTERNS:
        for kw in ap.detection_keywords:
            if kw in text_lower:
                found.append((ap, kw))
                break  # One match per pattern is enough

    return found


def get_fixes_for_dimensions(weak_dimensions: list) -> list:
    """
    Given a list of weak dimensions, return relevant anti-patterns
    and their fixes.
    """
    fixes = []
    for dim in weak_dimensions:
        for ap in ANTI_PATTERNS:
            if ap.dimension_affected == dim:
                fixes.append(ap)
    return fixes


def get_fix_for_pattern(pattern_id: str) -> Optional[AntiPattern]:
    """Look up a specific anti-pattern by ID."""
    for ap in ANTI_PATTERNS:
        if ap.id == pattern_id:
            return ap
    return None


def summary() -> str:
    """Display the full anti-pattern database."""
    lines = [
        "═══ ANTI-PATTERN DATABASE ═══",
        f"  Total patterns: {len(ANTI_PATTERNS)}",
        f"  Kill-level: {sum(1 for ap in ANTI_PATTERNS if ap.severity == 'kill')}",
        f"  Degradation: {sum(1 for ap in ANTI_PATTERNS if ap.severity == 'degrade')}",
        "",
    ]

    for ap in ANTI_PATTERNS:
        icon = "💀" if ap.severity == "kill" else "⚠️"
        lines.append(f"  {icon} {ap.id}: {ap.name}")
        lines.append(f"     Affects: {ap.dimension_affected}")
        lines.append(f"     Fix: {ap.fix_strategy[:100]}...")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
