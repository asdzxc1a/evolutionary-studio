"""
Correction Engine — System 4, Component 5

Takes a ScoreCard (from judgment) + the genome that was judged,
diagnoses WHY it failed, and produces corrected MutationRules
for the next generation attempt.

This is the "doctor" — it reads the diagnosis and prescribes treatment.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CorrectionPrescription:
    """What needs to change in the next generation attempt."""

    iteration: int = 0
    previous_score: float = 0.0
    kill_criteria_triggered: list = field(default_factory=list)
    low_dimensions: list = field(default_factory=list)  # (dimension, score, fix)
    mutation_overrides: dict = field(default_factory=dict)  # field → new value
    prompt_injections: list = field(default_factory=list)  # Extra instructions for LLM
    hard_constraints: list = field(default_factory=list)  # Non-negotiable requirements

    def summary(self) -> str:
        lines = [
            f"═══ CORRECTION PRESCRIPTION (iteration {self.iteration}) ═══",
            f"Previous score: {self.previous_score:.2f}",
            "",
        ]

        if self.kill_criteria_triggered:
            lines.append("💀 Kill Criteria to Fix:")
            for k in self.kill_criteria_triggered:
                lines.append(f"  • {k}")
            lines.append("")

        if self.low_dimensions:
            lines.append("📉 Low Dimensions:")
            for dim, score, fix in self.low_dimensions:
                lines.append(f"  • {dim}: {score:.2f} → Fix: {fix}")
            lines.append("")

        if self.hard_constraints:
            lines.append("🔒 Hard Constraints (non-negotiable):")
            for c in self.hard_constraints:
                lines.append(f"  • {c}")
            lines.append("")

        if self.prompt_injections:
            lines.append("💉 Prompt Injections:")
            for p in self.prompt_injections:
                lines.append(f"  → {p}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# CORRECTION LOGIC
# ═══════════════════════════════════════════════════════

KILL_FIXES = {
    "kill_corporate_villain": {
        "diagnosis": "Villain is a generic corporation or shadowy force",
        "fix": "Eliminate external villain entirely. Make the conflict internal "
               "(protagonist vs self), systemic (protagonist vs an unjust system), "
               "or a genuine dilemma (two valid choices, neither fully right).",
        "hard_constraint": "NO external villain character. The antagonist must be "
                          "a force, a system, or an aspect of the protagonist.",
        "prompt_injection": "CRITICAL: Do NOT create a villain character. The conflict "
                           "must come from within the protagonist or from an impossible "
                           "choice. The most powerful films have no villain — they have "
                           "a DILEMMA.",
    },
    "kill_bumper_sticker_theme": {
        "diagnosis": "Theme is too simple — can be stated as a bumper sticker",
        "fix": "Reframe the theme as a PARADOX. Both sides must be defensible. "
               "The audience should leave the theater still debating.",
        "hard_constraint": "Theme must be a PARADOX with two valid sides, not a statement.",
        "prompt_injection": "CRITICAL: The theme must be expressible as 'X is true, BUT "
                           "ALSO the opposite of X is true.' Example: 'Remembering keeps "
                           "you whole, but remembering keeps the wound open.' The film "
                           "must argue BOTH sides honestly.",
    },
    "kill_naive_protagonist": {
        "diagnosis": "Protagonist is 'good but naive' — a safe Disney template",
        "fix": "Give the protagonist a quality that makes the audience UNCOMFORTABLE. "
               "Not a cute flaw — something that makes you wonder if they're the good guy.",
        "hard_constraint": "Protagonist must do at least ONE thing that makes the audience "
                          "feel bad. Not a mistake — a deliberate choice that hurts someone.",
        "prompt_injection": "CRITICAL: The protagonist must have a DARK quality. They must "
                           "do something cruel, selfish, or destructive at least once. The "
                           "audience must question whether to root for them. This is what "
                           "separates REAL characters from Disney templates.",
    },
    "kill_tourism_setting": {
        "diagnosis": "Settings described like a travel brochure — generic and decorative",
        "fix": "Every location needs a specific address, time of day, weather, and "
               "sensory details. Not 'Paris' — a specific room in a specific building "
               "at a specific hour with specific smells and sounds.",
        "hard_constraint": "Every location must have: specific place name, time, weather, "
                          "at least 3 sensory details, and a reason WHY this specific place.",
        "prompt_injection": "CRITICAL: Do NOT use country names as settings. Use SPECIFIC "
                           "places: 'the basement of a refugee center in Calais at 2AM' "
                           "not 'France'. 'A psychiatric facility near Zurich with white "
                           "walls and the smell of antiseptic' not 'Switzerland'. I want "
                           "to SMELL every location.",
    },
    "kill_helper_fairy_tales": {
        "diagnosis": "Fairy tales are cute helpers — Pagemaster/Inkheart clone",
        "fix": "Fairy tales must be dangerous, uncontrollable, or have a COST. "
               "They are ancient, pre-moral forces — not friends.",
        "hard_constraint": "Fairy tales must have a COST for using them and must be "
                          "capable of HURTING the protagonist or innocent people.",
        "prompt_injection": "CRITICAL: Fairy tales are NOT helpers. They are dangerous, "
                           "ambiguous forces. Every time one manifests, something BAD "
                           "also happens. They are ancient and do not understand modern "
                           "morality. A fairy tale wolf EATS people. A fairy tale fox "
                           "LIES. They do what they do. The protagonist must learn to "
                           "live with them, not control them.",
    },
    "kill_seen_before": {
        "diagnosis": "This story already exists as a film",
        "fix": "Identify all comparable works and articulate what makes this "
               "FUNDAMENTALLY different. If you can't, the concept needs mutation.",
        "hard_constraint": "Must pass the Pagemaster Test — list all comparable works "
                          "and explain why this is not any of them.",
        "prompt_injection": "CRITICAL: Before generating the story, list every existing "
                           "film this could be compared to. Then explain in one sentence "
                           "why this is NONE of those films. If you can't, change the "
                           "concept until you can.",
    },
}

DIMENSION_FIXES = {
    "surprise_factor": {
        "threshold": 0.50,
        "fix": "Add a GENRE COLLISION. The film should be two genres at once — "
               "one visible (what it looks like), one hidden (what it's actually about). "
               "Example: Zootopia looks like a buddy cop movie, is actually about systemic racism.",
    },
    "emotional_danger": {
        "threshold": 0.50,
        "fix": "Raise the stakes to SOUL-LEVEL. The protagonist shouldn't just risk "
               "losing the quest — they should risk becoming someone they hate. "
               "The audience should feel genuine FEAR for the character's soul.",
    },
    "specificity": {
        "threshold": 0.50,
        "fix": "Replace every generic location with a SPECIFIC one. Replace every "
               "generic emotion with a SPECIFIC memory. Replace every generic character "
               "trait with a SPECIFIC behavior.",
    },
    "thematic_depth": {
        "threshold": 0.50,
        "fix": "Make the theme a DEBATE, not a lesson. The villain's position must "
               "be genuinely defensible. The audience should leave uncertain.",
    },
    "character_edge": {
        "threshold": 0.50,
        "fix": "Give the protagonist a moment where THEY are the villain of someone "
               "else's story. Not by accident — by choice.",
    },
    "originality": {
        "threshold": 0.50,
        "fix": "Run the Pagemaster Test. List all comparable works. Mutate the concept "
               "until the comparison list drops below 3 close matches.",
    },
    "dna_fidelity": {
        "threshold": 0.60,
        "fix": "Re-examine the reference film's beat timing, emotional arc shape, and "
               "causal chain. The structure should be FELT even if the content is different.",
    },
    "cultural_authenticity": {
        "threshold": 0.40,
        "fix": "Research the actual cultural context. Use specific cultural details that "
               "only someone from that culture would know. Avoid decorative cultural elements.",
    },
}


def diagnose(scorecard, genome_yaml: str = "", iteration: int = 0) -> CorrectionPrescription:
    """
    Analyze a ScoreCard and produce a CorrectionPrescription.

    Args:
        scorecard: The ScoreCard from the judgment engine
        genome_yaml: The genome that was judged (for context)
        iteration: Which attempt this is (0-indexed)

    Returns:
        CorrectionPrescription with fixes to apply
    """
    prescription = CorrectionPrescription(
        iteration=iteration + 1,
        previous_score=scorecard.overall_score,
    )

    # 1. Address kill criteria first (highest priority)
    kill_map = {
        'kill_corporate_villain': scorecard.kill_corporate_villain,
        'kill_bumper_sticker_theme': scorecard.kill_bumper_sticker_theme,
        'kill_naive_protagonist': scorecard.kill_naive_protagonist,
        'kill_tourism_setting': scorecard.kill_tourism_setting,
        'kill_helper_fairy_tales': scorecard.kill_helper_fairy_tales,
        'kill_seen_before': scorecard.kill_seen_before,
    }

    for kill_name, triggered in kill_map.items():
        if triggered and kill_name in KILL_FIXES:
            fix = KILL_FIXES[kill_name]
            prescription.kill_criteria_triggered.append(
                f"{fix['diagnosis']} → {fix['fix']}"
            )
            prescription.hard_constraints.append(fix['hard_constraint'])
            prescription.prompt_injections.append(fix['prompt_injection'])

    # 2. Address low-scoring dimensions
    dimension_scores = {
        'surprise_factor': scorecard.surprise_factor,
        'emotional_danger': scorecard.emotional_danger,
        'specificity': scorecard.specificity,
        'thematic_depth': scorecard.thematic_depth,
        'character_edge': scorecard.character_edge,
        'originality': scorecard.originality,
        'dna_fidelity': scorecard.dna_fidelity,
        'cultural_authenticity': scorecard.cultural_authenticity,
    }

    for dim, score in dimension_scores.items():
        if dim in DIMENSION_FIXES:
            threshold = DIMENSION_FIXES[dim]['threshold']
            if score < threshold:
                prescription.low_dimensions.append(
                    (dim, score, DIMENSION_FIXES[dim]['fix'])
                )

    # 3. Add iteration-specific escalation
    if iteration >= 2:
        prescription.prompt_injections.append(
            "WARNING: This is attempt #%d. Previous attempts scored %.2f. "
            "You MUST make RADICAL changes, not incremental adjustments. "
            "If the concept isn't working, CHANGE THE CONCEPT." % (
                iteration + 1, scorecard.overall_score
            )
        )

    if iteration >= 4:
        prescription.prompt_injections.append(
            "FINAL ATTEMPT. If this doesn't pass, the concept will be "
            "flagged for human creative direction review. Go BOLD."
        )

    return prescription


def format_correction_prompt(prescription: CorrectionPrescription,
                              original_prompt: str) -> str:
    """
    Take the original generation prompt and inject corrections.

    Returns a new prompt with corrections prepended as hard constraints.
    """
    sections = []

    sections.append("## ⚠️ CORRECTION PASS (Iteration %d)" % prescription.iteration)
    sections.append("Previous score: %.2f / 1.00" % prescription.previous_score)
    sections.append("")

    if prescription.hard_constraints:
        sections.append("## 🔒 HARD CONSTRAINTS — These are NON-NEGOTIABLE:")
        for i, constraint in enumerate(prescription.hard_constraints, 1):
            sections.append(f"{i}. {constraint}")
        sections.append("")

    if prescription.prompt_injections:
        sections.append("## 💉 CRITICAL INSTRUCTIONS:")
        for injection in prescription.prompt_injections:
            sections.append(f"- {injection}")
        sections.append("")

    if prescription.low_dimensions:
        sections.append("## 📉 DIMENSIONS TO IMPROVE:")
        for dim, score, fix in prescription.low_dimensions:
            sections.append(f"- **{dim}** (scored {score:.2f}): {fix}")
        sections.append("")

    correction_header = "\n".join(sections)
    return correction_header + "\n---\n\n" + original_prompt


if __name__ == "__main__":
    # Test: diagnose the Kazka v1 failure
    import sys
    sys.path.insert(0, '.')
    from engine.judgment import SELF_SCORE_KAZKA_V1

    prescription = diagnose(SELF_SCORE_KAZKA_V1, iteration=0)
    print(prescription.summary())
