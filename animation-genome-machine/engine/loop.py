"""
Creative Loop — The Main Orchestrator

This is the beating heart of the Animation Genome Machine.
It connects: Generation → Judgment → Correction → Regeneration

THE LOOP:
    1. Load reference genome + creative direction + mutation rules
    2. Format transmutation prompt
    3. [LLM CALL] Generate new genome
    4. Parse and validate genome
    5. Run judgment engine (score + kill check)
    6. If PASS: save genome, report success
    7. If FAIL: run correction engine, inject fixes into prompt, goto 3
    8. Max 5 iterations. If all fail, escalate to human.

ARCHITECTURE NOTE:
    The actual LLM calls are abstracted behind a `generate_fn` callable.
    This allows the loop to work with any LLM backend:
    - Gemini (via Antigravity agent calls)
    - Claude (via claude CLI)
    - Local models (via API)
    - Human (via manual input for testing)
"""

import json
import yaml
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from engine.extractor import FilmGenomeDocument
from engine.judgment import ScoreCard, JUDGMENT_PROMPT
from engine.generation import MutationRules, TRANSMUTATION_PROMPT
from engine.correction import diagnose, format_correction_prompt, CorrectionPrescription


@dataclass
class LoopConfig:
    """Configuration for the creative loop."""
    max_iterations: int = 5
    quality_threshold: float = 0.70
    vault_path: str = "vault"
    save_intermediates: bool = True  # Save failed attempts for debugging
    verbose: bool = True


@dataclass
class LoopIteration:
    """Record of one iteration through the loop."""
    iteration: int
    timestamp: str
    genome_yaml: str = ""
    scorecard: Optional[ScoreCard] = None
    prescription: Optional[CorrectionPrescription] = None
    prompt_used: str = ""
    status: str = ""  # "generated", "killed", "below_threshold", "passed", "parse_error"
    error: str = ""


@dataclass
class LoopResult:
    """Final result of the creative loop."""
    success: bool = False
    final_genome: Optional[FilmGenomeDocument] = None
    final_genome_yaml: str = ""
    final_score: float = 0.0
    final_scorecard: Optional[ScoreCard] = None
    iterations: list = field(default_factory=list)
    total_iterations: int = 0
    reference_film: str = ""
    creative_direction: str = ""

    def summary(self) -> str:
        lines = [
            "═══════════════════════════════════════════════════",
            "    CREATIVE LOOP — FINAL REPORT",
            "═══════════════════════════════════════════════════",
            "",
        ]

        if self.success:
            lines.append(f"🟢 STATUS: SUCCESS after {self.total_iterations} iteration(s)")
        else:
            lines.append(f"🔴 STATUS: FAILED after {self.total_iterations} iteration(s)")

        lines.extend([
            f"   Reference: {self.reference_film}",
            f"   Direction: {self.creative_direction[:80]}...",
            f"   Final Score: {self.final_score:.2f} / 1.00",
            "",
            "─── Iteration History ───",
        ])

        for it in self.iterations:
            score_str = f"{it.scorecard.overall_score:.2f}" if it.scorecard else "N/A"
            killed = "💀" if (it.scorecard and it.scorecard.killed) else ""
            status_icon = {
                "passed": "✅",
                "killed": "💀",
                "below_threshold": "⚠️",
                "parse_error": "❌",
                "generated": "📝",
            }.get(it.status, "?")

            lines.append(
                f"  {status_icon} Iteration {it.iteration}: "
                f"score={score_str} {killed} [{it.status}]"
            )

        if self.final_scorecard:
            lines.append("")
            lines.append("─── Final Scorecard ───")
            lines.append(self.final_scorecard.summary())

        return "\n".join(lines)


class CreativeLoop:
    """
    The main orchestrator that runs the generate→judge→correct loop.

    Usage:
        loop = CreativeLoop(config=LoopConfig())
        result = loop.run(
            reference_genome_path="vault/00-film-dna/zootopia_reference_genome.yaml",
            creative_direction="Ukrainian girl, fairy tales, Europe...",
            mutation_rules=my_rules,
            generate_fn=my_llm_call_function,
            judge_fn=my_judgment_function,
        )
    """

    def __init__(self, config: Optional[LoopConfig] = None):
        self.config = config or LoopConfig()
        self.iterations: list = []

    def run(
        self,
        reference_genome_yaml: str,
        creative_direction: str,
        mutation_rules: MutationRules,
        generate_fn: Callable[[str], str],
        judge_fn: Callable[[str, str, str], ScoreCard],
        reference_film: str = "",
    ) -> LoopResult:
        """
        Execute the creative loop.

        Args:
            reference_genome_yaml: YAML string of reference film's genome
            creative_direction: User's creative direction text
            mutation_rules: MutationRules defining originality constraints
            generate_fn: Callable that takes a prompt and returns generated YAML
            judge_fn: Callable that takes (genome_yaml, reference_film, direction)
                     and returns a ScoreCard
            reference_film: Name of reference film for reporting

        Returns:
            LoopResult with success/failure, final genome, and iteration history
        """
        result = LoopResult(
            reference_film=reference_film,
            creative_direction=creative_direction,
        )

        # Validate mutation rules first
        rules_validation = mutation_rules.validate()
        if not rules_validation['valid']:
            if self.config.verbose:
                print("❌ Mutation rules invalid:")
                for err in rules_validation['errors']:
                    print(f"  • {err}")
            result.iterations.append(LoopIteration(
                iteration=0,
                timestamp=datetime.now().isoformat(),
                status="parse_error",
                error="Mutation rules invalid: " + "; ".join(rules_validation['errors']),
            ))
            result.total_iterations = 0
            return result

        # Build the base prompt
        base_prompt = TRANSMUTATION_PROMPT.format(
            reference_genome=reference_genome_yaml,
            creative_direction=creative_direction,
            mutation_rules=mutation_rules.summary(),
        )

        current_prompt = base_prompt

        for i in range(self.config.max_iterations):
            if self.config.verbose:
                print(f"\n{'='*60}")
                print(f"  ITERATION {i + 1} / {self.config.max_iterations}")
                print(f"{'='*60}")

            iteration = LoopIteration(
                iteration=i + 1,
                timestamp=datetime.now().isoformat(),
                prompt_used=current_prompt[:500] + "..." if len(current_prompt) > 500 else current_prompt,
            )

            # STEP 1: Generate
            if self.config.verbose:
                print("  📝 Generating new genome...")

            try:
                generated_yaml = generate_fn(current_prompt)
                iteration.genome_yaml = generated_yaml
                iteration.status = "generated"
            except Exception as e:
                iteration.status = "parse_error"
                iteration.error = str(e)
                self.iterations.append(iteration)
                result.iterations.append(iteration)
                if self.config.verbose:
                    print(f"  ❌ Generation failed: {e}")
                continue

            # STEP 2: Judge
            if self.config.verbose:
                print("  ⚖️ Running judgment...")

            try:
                scorecard = judge_fn(generated_yaml, reference_film, creative_direction)
                iteration.scorecard = scorecard
            except Exception as e:
                iteration.status = "parse_error"
                iteration.error = f"Judgment failed: {e}"
                self.iterations.append(iteration)
                result.iterations.append(iteration)
                if self.config.verbose:
                    print(f"  ❌ Judgment failed: {e}")
                continue

            score = scorecard.overall_score
            killed = scorecard.killed

            if self.config.verbose:
                print(f"  Score: {score:.2f} / 1.00")
                if killed:
                    print(f"  💀 KILLED — {len(scorecard.kill_reasons)} kill criteria triggered")
                    for reason in scorecard.kill_reasons:
                        print(f"     {reason}")

            # STEP 3: Decide
            if not killed and score >= self.config.quality_threshold:
                # SUCCESS
                iteration.status = "passed"
                self.iterations.append(iteration)
                result.iterations.append(iteration)
                result.success = True
                result.final_genome_yaml = generated_yaml
                result.final_score = score
                result.final_scorecard = scorecard
                result.total_iterations = i + 1

                if self.config.verbose:
                    print(f"  ✅ PASSED with score {score:.2f}")

                # Try to parse into FilmGenomeDocument
                try:
                    genome_data = yaml.safe_load(generated_yaml)
                    if genome_data:
                        result.final_genome = FilmGenomeDocument._from_dict(genome_data)
                except Exception:
                    pass  # Keep the YAML even if we can't parse it

                # Save to vault
                if self.config.save_intermediates:
                    self._save_to_vault(generated_yaml, i + 1, "passed", score)

                return result

            elif killed:
                iteration.status = "killed"
            else:
                iteration.status = "below_threshold"

            self.iterations.append(iteration)
            result.iterations.append(iteration)

            # Save intermediate for debugging
            if self.config.save_intermediates:
                self._save_to_vault(generated_yaml, i + 1, iteration.status, score)

            # STEP 4: Correct (if not last iteration)
            if i < self.config.max_iterations - 1:
                if self.config.verbose:
                    print("  🔧 Generating corrections...")

                prescription = diagnose(scorecard, generated_yaml, iteration=i)
                iteration.prescription = prescription

                if self.config.verbose:
                    print(prescription.summary())

                # Inject corrections into prompt for next iteration
                current_prompt = format_correction_prompt(prescription, base_prompt)

        # All iterations exhausted
        result.total_iterations = self.config.max_iterations
        result.success = False

        # Use best attempt as final
        best_iteration = max(
            [it for it in result.iterations if it.scorecard],
            key=lambda it: it.scorecard.overall_score if it.scorecard else 0,
            default=None,
        )
        if best_iteration and best_iteration.scorecard:
            result.final_score = best_iteration.scorecard.overall_score
            result.final_scorecard = best_iteration.scorecard
            result.final_genome_yaml = best_iteration.genome_yaml

        if self.config.verbose:
            print(f"\n{'='*60}")
            print(f"  ⛔ LOOP EXHAUSTED — Best score: {result.final_score:.2f}")
            print(f"  Escalating to human review.")
            print(f"{'='*60}")

        return result

    def _save_to_vault(self, yaml_content: str, iteration: int,
                       status: str, score: float):
        """Save iteration output to vault for debugging."""
        vault_dir = Path(self.config.vault_path) / "05-review"
        vault_dir.mkdir(parents=True, exist_ok=True)

        filename = f"iteration_{iteration:02d}_{status}_{score:.2f}.yaml"
        filepath = vault_dir / filename

        with open(filepath, 'w') as f:
            f.write(f"# Iteration {iteration} — Status: {status} — Score: {score:.2f}\n")
            f.write(f"# Timestamp: {datetime.now().isoformat()}\n\n")
            f.write(yaml_content)

        if self.config.verbose:
            print(f"  💾 Saved to {filepath}")


# ═══════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS FOR TESTING
# ═══════════════════════════════════════════════════════

def mock_generate_fn(prompt: str) -> str:
    """Mock generator that returns a minimal genome for testing the loop."""
    return """
metadata:
  title: "Test Film"
  reference_film: "Zootopia"
  genome_version: "1.0"
  target_duration_minutes: 90
  target_format: feature

narrative_dna:
  structure: save_the_cat
  emotional_arc_shape: cinderella
  beats:
    - id: beat_01
      name: "Opening"
      type: setup
      timestamp_pct: 0.0
      emotional_valence: 0.3
      emotional_arousal: 0.2
      description: "A displaced girl arrives in a foreign city"
      duration_pct: 0.05
  themes:
    - "displacement"
    - "identity"

character_dna:
  characters:
    - id: char_protagonist
      name: "Olenka"
      archetype: reluctant_hero
      arc: "Angry displaced girl learns to carry her heritage without being consumed by it"
"""


def mock_judge_fn(genome_yaml: str, reference_film: str,
                  creative_direction: str) -> ScoreCard:
    """
    Mock judge that scores based on content analysis.
    In production, this would call an LLM with JUDGMENT_PROMPT.
    """
    yaml_lower = genome_yaml.lower()

    # Simple heuristic scoring for testing
    score = ScoreCard()

    # Check for kill criteria
    score.kill_corporate_villain = (
        "corporation" in yaml_lower or
        "shadowy" in yaml_lower or
        "archivist" in yaml_lower
    )
    score.kill_bumper_sticker_theme = (
        "stories matter" in yaml_lower or
        "be yourself" in yaml_lower or
        "believe in" in yaml_lower
    )
    score.kill_naive_protagonist = (
        "good but naive" in yaml_lower or
        "optimistic and kind" in yaml_lower
    )
    score.kill_tourism_setting = (
        "the eiffel tower" in yaml_lower or
        "the louvre" in yaml_lower or
        "big ben" in yaml_lower
    )
    score.kill_helper_fairy_tales = (
        "helps her" in yaml_lower or
        "ally" in yaml_lower or
        "helper" in yaml_lower
    )
    score.kill_seen_before = (
        "pagemaster" in yaml_lower or
        "inkheart" in yaml_lower
    )

    # Dimension scoring (heuristic for testing)
    score.surprise_factor = 0.3 if "genre" not in yaml_lower else 0.6
    score.emotional_danger = 0.3 if "cruel" not in yaml_lower else 0.7
    score.specificity = 0.2 if "paris" in yaml_lower and "rue" not in yaml_lower else 0.6
    score.thematic_depth = 0.3 if "paradox" not in yaml_lower else 0.7
    score.character_edge = 0.3 if "angry" not in yaml_lower else 0.7
    score.originality = 0.4
    score.dna_fidelity = 0.7 if "save_the_cat" in yaml_lower else 0.3
    score.cultural_authenticity = 0.5

    score.diagnosis = "Mock judgment — replace with LLM-powered evaluation"

    return score


# ═══════════════════════════════════════════════════════
# TEST: Run the full loop with mock functions
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    from engine.generation import MutationRules, LocationSpec

    print("═══════════════════════════════════════════════════")
    print("    CREATIVE LOOP — INTEGRATION TEST")
    print("═══════════════════════════════════════════════════")
    print()

    # Load reference genome
    reference_path = "vault/00-film-dna/zootopia_reference_genome.yaml"
    if os.path.exists(reference_path):
        with open(reference_path, 'r') as f:
            reference_yaml = f.read()
    else:
        reference_yaml = "# No reference genome found"

    # Define mutation rules
    rules = MutationRules(
        genre_primary="coming-of-age road movie",
        genre_hidden="psychological horror",
        genre_collision_note="Looks like Pixar, feels like Pan's Labyrinth",
        villain_type="internal",
        villain_note="No villain. Conflict is protagonist vs displacement trauma.",
        protagonist_uncomfortable_quality="Cruel to people who try to help her",
        protagonist_worst_action="Tells a foster child their problems aren't real",
        theme_paradox="To heal you must remember. But remembering keeps the wound open.",
        theme_side_a="Forgetting is freedom",
        theme_side_b="Remembering is identity",
        fairy_tale_role="Involuntary manifestations of emotional state",
        fairy_tale_cost="Every manifestation costs a real memory",
        fairy_tale_danger="They don't distinguish helping from destroying",
        one_sentence_pitch=(
            "A displaced girl's fairy tales escape as dangerous forces "
            "that feed on her trauma — each one costs a real memory."
        ),
        pitch_uniqueness_score=0.80,
        locations=[
            LocationSpec("France", "Refugee center basement, Calais", "2AM Feb"),
            LocationSpec("Switzerland", "Psychiatric facility, Zurich"),
            LocationSpec("Germany", "Empty apartment, Berlin-Neukölln", "Evening"),
        ],
        comparable_works=["Pan's Labyrinth", "Spirited Away", "Wolfwalkers"],
        differentiation="Fantasy isn't escape — it's the PROBLEM.",
    )

    # Create and run the loop
    config = LoopConfig(
        max_iterations=3,
        quality_threshold=0.70,
        vault_path="vault",
        verbose=True,
    )

    loop = CreativeLoop(config=config)

    result = loop.run(
        reference_genome_yaml=reference_yaml,
        creative_direction=(
            "Ukrainian girl displaced to Europe. Fairy tales from grandmother's "
            "book. Travels through France, Switzerland, Germany, England, USA. "
            "Must be unique, NOT generic, NOT a Pagemaster clone."
        ),
        mutation_rules=rules,
        generate_fn=mock_generate_fn,
        judge_fn=mock_judge_fn,
        reference_film="Zootopia (2016)",
    )

    print()
    print(result.summary())
