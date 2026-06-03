"""
Progressive Refinement Loop — System v3, Layer 5

Instead of regenerating the ENTIRE genome when it fails:
    Pass 1: Generate full genome → score → identify weakest 3 beats
    Pass 2: Regenerate ONLY the 3 weakest beats → re-score
    Pass 3: Regenerate ONLY the weakest 1 beat → final score

This is surgical. A 0.88 genome doesn't need full regeneration —
it needs 3 beats fixed.
"""

import yaml
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional


@dataclass
class BeatFix:
    """A targeted fix for a single beat."""
    beat_id: str
    beat_name: str
    current_score: float
    target_score: float
    weakest_dimensions: list = field(default_factory=list)  # (dimension, score)
    fix_instructions: str = ""
    fixed_text: str = ""  # The regenerated beat text
    new_score: float = 0.0


@dataclass
class RefinementPass:
    """Record of one refinement pass."""
    pass_number: int
    beats_targeted: list = field(default_factory=list)  # beat_ids
    score_before: float = 0.0
    score_after: float = 0.0
    fixes_applied: list = field(default_factory=list)  # BeatFix objects
    timestamp: str = ""


@dataclass
class RefinementResult:
    """Final result of progressive refinement."""
    success: bool = False
    initial_score: float = 0.0
    final_score: float = 0.0
    passes: list = field(default_factory=list)  # RefinementPass objects
    total_beats_fixed: int = 0
    final_genome_yaml: str = ""
    improvement: float = 0.0  # final - initial

    def summary(self) -> str:
        lines = [
            "═══ PROGRESSIVE REFINEMENT — REPORT ═══",
            "",
            f"  Initial Score: {self.initial_score:.2f}",
            f"  Final Score:   {self.final_score:.2f}",
            f"  Improvement:   +{self.improvement:.2f} ({self.improvement/max(self.initial_score, 0.01)*100:.0f}%)",
            f"  Beats Fixed:   {self.total_beats_fixed}",
            "",
            "─── Pass History ───",
        ]

        for p in self.passes:
            lines.append(
                f"  Pass {p.pass_number}: {len(p.beats_targeted)} beats → "
                f"{p.score_before:.2f} → {p.score_after:.2f} "
                f"(+{p.score_after - p.score_before:.2f})"
            )
            for fix in p.fixes_applied:
                status = "✅" if fix.new_score >= fix.target_score else "⚠️"
                lines.append(
                    f"    {status} {fix.beat_id} ({fix.beat_name}): "
                    f"{fix.current_score:.2f} → {fix.new_score:.2f}"
                )

        if self.success:
            lines.append(f"\n  🟢 REFINEMENT SUCCESSFUL")
        else:
            lines.append(f"\n  🔴 REFINEMENT INCOMPLETE — further passes needed")

        return "\n".join(lines)


def extract_beats_from_yaml(genome_yaml: str) -> list:
    """Extract beat sections from a genome YAML string."""
    try:
        data = yaml.safe_load(genome_yaml)
    except Exception:
        return []

    beats = []
    narrative = data.get('narrative_dna', {})

    if isinstance(narrative, dict):
        beat_list = narrative.get('beats', [])
        for beat in beat_list:
            if isinstance(beat, dict):
                beats.append({
                    'id': beat.get('id', ''),
                    'name': beat.get('name', ''),
                    'type': beat.get('type', ''),
                    'description': beat.get('description', ''),
                    'timestamp_pct': beat.get('timestamp_pct', 0),
                    'emotional_valence': beat.get('emotional_valence', 0),
                    'emotional_arousal': beat.get('emotional_arousal', 0),
                    'duration_pct': beat.get('duration_pct', 0),
                })

    return beats


def score_single_beat(beat: dict) -> dict:
    """
    Heuristic score for a single beat.
    Returns dict with 8 dimension scores and overall.
    """
    text = beat.get('description', '').lower()

    # Specificity: sensory details
    sensory = ["smell", "sound", "taste", "feel", "fluorescent", "antiseptic",
               "concrete", "linoleum", "bleach", "coffee", "rain", "silence",
               "2am", "3am", "11 pm", "morning", "evening", "night",
               "basement", "hallway", "bathroom", "kitchen", "apartment"]
    specificity = min(0.15 + sum(1 for s in sensory if s in text) * 0.06, 1.0)

    # Emotional danger
    danger = ["cruel", "angry", "cry", "scream", "hurt", "break", "destroy",
              "shame", "guilt", "can't", "won't", "lost", "gone", "dead",
              "afraid", "fear", "pain", "wound", "scar", "blood", "silence"]
    emotional_danger = min(0.10 + sum(1 for d in danger if d in text) * 0.05, 1.0)

    # Character edge
    edge = ["cruel", "cold", "flat", "pushes away", "refuses", "can't apologize",
            "selfish", "bitter", "resentful", "deliberately", "worst",
            "villain", "wrong", "ugly"]
    character_edge = min(0.10 + sum(1 for e in edge if e in text) * 0.07, 1.0)

    # Thematic depth
    theme = ["paradox", "both", "neither", "dilemma", "contradiction",
             "remember", "forget", "heal", "wound", "cost", "price",
             "carry", "burden"]
    thematic_depth = min(0.15 + sum(1 for t in theme if t in text) * 0.07, 1.0)

    # Surprise factor
    surprise = ["but", "however", "instead", "actually", "twist",
                "ironic", "unexpected", "false", "reversed", "inverted",
                "not what", "wrong about"]
    surprise_factor = min(0.15 + sum(1 for s in surprise if s in text) * 0.06, 1.0)

    # Originality (harder to score heuristically)
    originality = 0.70  # Default moderate

    # DNA fidelity (check for structural markers)
    dna = ["maps to", "preserved", "save_the_cat", "because_of_that",
           "zootopia", "reference"]
    dna_fidelity = min(0.30 + sum(1 for d in dna if d in text) * 0.10, 1.0)

    # Cultural authenticity
    culture = ["ukrainian", "vyshyvanka", "babusya", "halyna", "kherson",
               "sopilka", "bandura", "kazka", "olenka"]
    cultural_authenticity = min(0.20 + sum(1 for c in culture if c in text) * 0.08, 1.0)

    scores = {
        'specificity': specificity,
        'emotional_danger': emotional_danger,
        'character_edge': character_edge,
        'thematic_depth': thematic_depth,
        'surprise_factor': surprise_factor,
        'originality': originality,
        'dna_fidelity': dna_fidelity,
        'cultural_authenticity': cultural_authenticity,
    }

    scores['overall'] = sum(scores.values()) / len(scores)
    return scores


def identify_weakest_beats(genome_yaml: str, n: int = 3) -> list:
    """
    Score all beats and return the N weakest.

    Returns: list of (beat_id, beat_name, overall_score, weak_dimensions)
    """
    beats = extract_beats_from_yaml(genome_yaml)
    scored = []

    for beat in beats:
        scores = score_single_beat(beat)
        # Find weakest 2 dimensions
        dims = [(k, v) for k, v in scores.items() if k != 'overall']
        dims.sort(key=lambda x: x[1])
        weak_dims = dims[:2]

        scored.append({
            'beat_id': beat['id'],
            'beat_name': beat['name'],
            'overall': scores['overall'],
            'weak_dimensions': weak_dims,
            'all_scores': scores,
        })

    # Sort by overall score ascending (weakest first)
    scored.sort(key=lambda x: x['overall'])

    return scored[:n]


def build_beat_fix_prompt(
    beat: dict,
    weak_dimensions: list,
    genome_yaml: str,
    reference_yaml: str = "",
) -> str:
    """
    Build a targeted prompt to regenerate a specific beat.
    """
    sections = [
        "## SURGICAL BEAT REGENERATION",
        "",
        f"You are fixing ONE specific beat: **{beat.get('name', '')}** ({beat.get('id', '')})",
        "",
        "### CURRENT VERSION (what needs improvement):",
        "```",
        beat.get('description', ''),
        "```",
        "",
        "### WEAK DIMENSIONS TO FIX:",
    ]

    for dim, score in weak_dimensions:
        fix_guide = DIMENSION_FIX_GUIDES.get(dim, "Improve this dimension.")
        sections.append(f"- **{dim}** (scored {score:.2f}): {fix_guide}")

    sections.extend([
        "",
        "### RULES:",
        "1. Preserve the beat's FUNCTION in the story (its role in the causal chain)",
        "2. Preserve the timestamp_pct and emotional_valence/arousal",
        "3. Preserve key character interactions",
        "4. IMPROVE the weak dimensions WITHOUT damaging the strong ones",
        "5. The replacement must be a DROP-IN — it replaces only this beat's description",
        "",
        "### OUTPUT:",
        "Return ONLY the new description text for this beat.",
        "No YAML formatting, no metadata — just the description content.",
    ])

    return "\n".join(sections)


DIMENSION_FIX_GUIDES = {
    "specificity": (
        "Add SPECIFIC sensory details: exact time of day, weather, smells, "
        "sounds, textures. Not 'a room' but 'a room with fluorescent lights "
        "that buzz at 50Hz, linoleum that smells like yesterday's cleaning, "
        "and a clock that's 3 minutes fast.'"
    ),
    "emotional_danger": (
        "Raise the emotional stakes. The character should risk something "
        "SOUL-LEVEL, not just plot-level. What's the worst that could happen "
        "to their IDENTITY, not just their situation?"
    ),
    "character_edge": (
        "The protagonist should do or say something in this beat that makes "
        "the audience UNCOMFORTABLE. Not a cute flaw — something genuinely "
        "selfish, cruel, or destructive."
    ),
    "thematic_depth": (
        "Connect this beat to the central paradox. Both sides of the paradox "
        "should be PRESENT in this moment. The character should be caught "
        "between two valid choices."
    ),
    "surprise_factor": (
        "Subvert the expected outcome. What would the audience expect to "
        "happen? Do something ELSE that's more interesting and still organic."
    ),
    "originality": (
        "Has this exact scene been done before? If yes, mutate it. Find an "
        "angle that's specific to THIS story and couldn't exist in any other."
    ),
    "dna_fidelity": (
        "Check the reference film's equivalent beat. Preserve the FUNCTION "
        "(what it does in the story) while mutating the CONTENT."
    ),
    "cultural_authenticity": (
        "Add a cultural detail that only someone from this culture would know. "
        "Not decorative — structural. How does the character's cultural "
        "background change HOW they experience this moment?"
    ),
}


def replace_beat_in_yaml(genome_yaml: str, beat_id: str, new_description: str) -> str:
    """
    Replace a beat's description in the genome YAML.
    Uses string manipulation to preserve YAML formatting and comments.
    """
    lines = genome_yaml.split('\n')
    result_lines = []
    in_target_beat = False
    in_description = False
    description_indent = 0
    skip_until_next_field = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect beat start
        if f"id: {beat_id}" in line:
            in_target_beat = True

        # Detect next beat (exit current)
        if in_target_beat and "- id: beat_" in line and f"id: {beat_id}" not in line:
            in_target_beat = False
            skip_until_next_field = False

        # Detect description field in target beat
        if in_target_beat and not in_description and "description:" in line:
            # Check if it's a block scalar (> or |)
            if ">" in line or "|" in line:
                in_description = True
                description_indent = len(line) - len(line.lstrip()) + 2
                result_lines.append(line)  # Keep the "description: >" line

                # Insert new description
                for desc_line in new_description.split('\n'):
                    result_lines.append(' ' * description_indent + desc_line)

                skip_until_next_field = True
                i += 1
                continue

        # Skip old description lines
        if skip_until_next_field:
            stripped = line.strip()
            # Check if this line is a new field (less indented or a new key)
            if stripped and not stripped.startswith('#'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent < description_indent:
                    skip_until_next_field = False
                    result_lines.append(line)
                    i += 1
                    continue
            # Skip old description lines
            i += 1
            continue

        result_lines.append(line)
        i += 1

    return '\n'.join(result_lines)


class ProgressiveRefinementLoop:
    """
    Run progressive refinement: full → 3 beats → 1 beat.

    Usage:
        loop = ProgressiveRefinementLoop()
        result = loop.run(
            genome_yaml=genome_text,
            reference_yaml=reference_text,
            beat_regenerator_fn=my_llm_call,
            quality_threshold=0.90,
        )
    """

    def __init__(self, quality_threshold: float = 0.90, max_passes: int = 3):
        self.quality_threshold = quality_threshold
        self.max_passes = max_passes

    def run(
        self,
        genome_yaml: str,
        reference_yaml: str = "",
        beat_regenerator_fn: Callable = None,
        verbose: bool = True,
    ) -> RefinementResult:
        """
        Run the progressive refinement loop.

        beat_regenerator_fn: Takes (prompt: str) -> str, returns new beat description
        """
        result = RefinementResult()

        # Initial scoring
        beats = extract_beats_from_yaml(genome_yaml)
        all_scores = [score_single_beat(b) for b in beats]
        initial_avg = sum(s['overall'] for s in all_scores) / max(len(all_scores), 1)
        result.initial_score = initial_avg

        if verbose:
            print(f"  Initial beat-average score: {initial_avg:.2f}")
            print(f"  Target: {self.quality_threshold:.2f}")

        current_yaml = genome_yaml

        # Pass schedule: 3 beats, then 2, then 1
        pass_sizes = [3, 2, 1]

        for pass_num, n_beats in enumerate(pass_sizes[:self.max_passes]):
            if verbose:
                print(f"\n  ═══ PASS {pass_num + 1}: Fix {n_beats} weakest beat(s) ═══")

            weakest = identify_weakest_beats(current_yaml, n=n_beats)

            if not weakest:
                break

            refinement_pass = RefinementPass(
                pass_number=pass_num + 1,
                beats_targeted=[w['beat_id'] for w in weakest],
                score_before=initial_avg if pass_num == 0 else result.passes[-1].score_after,
                timestamp=datetime.now().isoformat(),
            )

            for weak_beat_info in weakest:
                beat_id = weak_beat_info['beat_id']
                beat_name = weak_beat_info['beat_name']
                current_score = weak_beat_info['overall']
                weak_dims = weak_beat_info['weak_dimensions']

                if verbose:
                    print(f"    🔧 Fixing {beat_id} ({beat_name}): {current_score:.2f}")
                    for dim, score in weak_dims:
                        print(f"       {dim}: {score:.2f}")

                # Build fix prompt
                beat_data = None
                for b in beats:
                    if b['id'] == beat_id:
                        beat_data = b
                        break

                if not beat_data:
                    continue

                fix = BeatFix(
                    beat_id=beat_id,
                    beat_name=beat_name,
                    current_score=current_score,
                    target_score=self.quality_threshold,
                    weakest_dimensions=weak_dims,
                )

                if beat_regenerator_fn:
                    prompt = build_beat_fix_prompt(
                        beat_data, weak_dims, current_yaml, reference_yaml
                    )
                    try:
                        new_description = beat_regenerator_fn(prompt)
                        fix.fixed_text = new_description

                        # Replace beat in YAML
                        current_yaml = replace_beat_in_yaml(
                            current_yaml, beat_id, new_description
                        )

                        # Re-score
                        beat_data['description'] = new_description
                        new_scores = score_single_beat(beat_data)
                        fix.new_score = new_scores['overall']

                        if verbose:
                            print(f"    ✅ {beat_id}: {current_score:.2f} → {fix.new_score:.2f}")

                    except Exception as e:
                        if verbose:
                            print(f"    ❌ Failed to fix {beat_id}: {e}")
                        fix.new_score = current_score
                else:
                    fix.fix_instructions = build_beat_fix_prompt(
                        beat_data, weak_dims, current_yaml, reference_yaml
                    )
                    if verbose:
                        print(f"    📝 Fix instructions generated (no regenerator provided)")

                refinement_pass.fixes_applied.append(fix)
                result.total_beats_fixed += 1

            # Re-score full genome after this pass
            new_beats = extract_beats_from_yaml(current_yaml)
            new_all_scores = [score_single_beat(b) for b in new_beats]
            new_avg = sum(s['overall'] for s in new_all_scores) / max(len(new_all_scores), 1)
            refinement_pass.score_after = new_avg

            result.passes.append(refinement_pass)

            if new_avg >= self.quality_threshold:
                result.success = True
                break

        result.final_score = result.passes[-1].score_after if result.passes else initial_avg
        result.final_genome_yaml = current_yaml
        result.improvement = result.final_score - result.initial_score

        return result


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

    print("═══ PROGRESSIVE REFINEMENT — TEST ═══")
    print()

    genome_path = "vault/00-film-dna/kazka_v2_genome.yaml"
    if os.path.exists(genome_path):
        with open(genome_path) as f:
            genome_yaml = f.read()

        # Score all beats
        weakest = identify_weakest_beats(genome_yaml, n=14)
        print("Beat scores (weakest to strongest):")
        for w in weakest:
            dims_str = ", ".join(f"{d}={s:.2f}" for d, s in w['weak_dimensions'])
            print(f"  {w['overall']:.2f}  {w['beat_id']}: {w['beat_name']}")
            print(f"         Weak: {dims_str}")
        print()

        # Run refinement without regenerator (just generates instructions)
        loop = ProgressiveRefinementLoop(quality_threshold=0.85)
        result = loop.run(genome_yaml, verbose=True)
        print()
        print(result.summary())
    else:
        print(f"  File not found: {genome_path}")
