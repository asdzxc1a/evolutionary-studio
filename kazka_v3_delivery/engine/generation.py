"""
Generation Engine — System 4, Component 3

The transmutation engine that takes reference DNA + creative direction
and produces a NEW Film Genome Document.

KEY LESSON FROM KAZKA v1 FAILURE:
    Literal DNA transfer produces generic output.
    The structure must be preserved, but the CONTENT must be MUTATED
    through creative constraints that force uniqueness.

This module defines MUTATION RULES — constraints that the generation
engine must satisfy before producing output. These rules are derived
from the Judgment Engine's kill criteria and scoring dimensions.

ARCHITECTURE:
    Input:  Reference Film Genome + Creative Direction + Mutation Rules
    Process: Multi-pass generation with judgment checkpoints
    Output: New Film Genome Document that passes judgment (score >= 0.70)

THE GENERATION LOOP:
    1. Extract DNA strands from reference
    2. Apply creative direction as mutation vector
    3. Apply mutation rules (force originality constraints)
    4. Generate candidate genome
    5. Run judgment engine
    6. If killed or below threshold: diagnose + mutate + regenerate
    7. If passes: output to human review
"""

from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════
# MUTATION RULES — Force originality in transmutation
# ═══════════════════════════════════════════════════════

@dataclass
class MutationRules:
    """
    Constraints applied during transmutation to force the output
    past the Judgment Engine's kill criteria.

    Each rule is a constraint the generation engine MUST satisfy.
    If a rule is violated, the genome is rejected before reaching judgment.
    """

    # RULE 1: GENRE COLLISION
    # The transmuted film must combine at least 2 genres that don't
    # normally go together. This is what made Zootopia work — it's a
    # buddy cop movie that's secretly about systemic racism.
    genre_primary: str = ""        # What it LOOKS like
    genre_hidden: str = ""         # What it ACTUALLY IS
    genre_collision_note: str = "" # Why these two genres collide

    # RULE 2: NO EXTERNAL VILLAIN
    # If the reference film has an external villain, the transmuted film
    # must internalize the conflict. The most interesting antagonists are
    # aspects of the protagonist themselves, or systems, or impossible
    # dilemmas — not people in suits.
    villain_type: str = "internal"  # internal, systemic, dilemma, absent
    villain_note: str = ""

    # RULE 3: SETTING SPECIFICITY
    # Every location must be a SPECIFIC place with a SPECIFIC address,
    # smell, sound, and time. Not "Paris" — a specific bakery on Rue de
    # Rivoli at 6am when the croissants come out and the street is wet.
    locations: list = field(default_factory=list)  # List of LocationSpec

    # RULE 4: PROTAGONIST EDGE
    # The protagonist must have at least one quality that makes the
    # audience UNCOMFORTABLE. Not a cute flaw — a real one. Something
    # that makes you wonder if they're actually the good guy.
    protagonist_uncomfortable_quality: str = ""
    protagonist_worst_action: str = ""  # The worst thing they DO in the film

    # RULE 5: THEMATIC PARADOX
    # The theme must be expressible as a PARADOX, not a statement.
    # "Stories matter" is a statement. "Remembering can be a prison
    # and forgetting can be freedom" is a paradox.
    theme_paradox: str = ""
    theme_side_a: str = ""  # One valid position
    theme_side_b: str = ""  # The opposing valid position

    # RULE 6: FAIRY TALE MUTATION (specific to this project)
    # Fairy tales must NOT be helpers. They must be one of:
    # - Uncontrollable forces
    # - Manifestations of the protagonist's psyche
    # - Unreliable narrators with their own agenda
    # - Dangerous, with a cost for using them
    fairy_tale_role: str = ""  # What role do fairy tales play?
    fairy_tale_cost: str = ""  # What's the COST of using them?
    fairy_tale_danger: str = "" # How can they HURT the protagonist?

    # RULE 7: THE PAGEMASTER TEST
    # List every existing film this could be compared to.
    # If more than 3 are closely similar, the concept must be mutated.
    comparable_works: list = field(default_factory=list)
    differentiation: str = ""  # How this is DIFFERENT from all of them

    # RULE 8: THE PITCH TEST
    # The story must be describable in one sentence that makes someone
    # say "I've never heard THAT before." If the pitch sounds familiar,
    # mutate until it doesn't.
    one_sentence_pitch: str = ""
    pitch_uniqueness_score: float = 0.0  # Self-assessed 0-1

    def validate(self) -> dict:
        """Check that all mutation rules are specified."""
        errors = []

        if not self.genre_primary or not self.genre_hidden:
            errors.append("RULE 1: Genre collision not defined")
        if self.genre_primary == self.genre_hidden:
            errors.append("RULE 1: Genres must be DIFFERENT")

        if self.villain_type == "external_person":
            errors.append("RULE 2: External person villain not allowed — internalize the conflict")

        if len(self.locations) < 3:
            errors.append(f"RULE 3: Only {len(self.locations)} specific locations — need at least 3")

        if not self.protagonist_uncomfortable_quality:
            errors.append("RULE 4: Protagonist uncomfortable quality not defined")
        if not self.protagonist_worst_action:
            errors.append("RULE 4: Protagonist worst action not defined")

        if not self.theme_paradox:
            errors.append("RULE 5: Thematic paradox not defined")
        if self.theme_side_a and not self.theme_side_b:
            errors.append("RULE 5: Theme must have TWO valid sides")

        if not self.fairy_tale_cost:
            errors.append("RULE 6: Fairy tale cost not defined")
        if not self.fairy_tale_danger:
            errors.append("RULE 6: Fairy tale danger not defined")

        if len(self.comparable_works) > 3 and not self.differentiation:
            errors.append("RULE 7: Too many comparable works without clear differentiation")

        if not self.one_sentence_pitch:
            errors.append("RULE 8: One-sentence pitch not defined")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "rules_defined": 8 - len(errors),
        }

    def summary(self) -> str:
        """Human-readable summary of mutation rules."""
        validation = self.validate()
        lines = [
            "═══ MUTATION RULES ═══",
            "",
            f"Genre Collision: {self.genre_primary} × {self.genre_hidden}",
            f"  Why: {self.genre_collision_note}",
            "",
            f"Villain Type: {self.villain_type}",
            f"  Note: {self.villain_note}",
            "",
            f"Protagonist Edge: {self.protagonist_uncomfortable_quality}",
            f"  Worst Action: {self.protagonist_worst_action}",
            "",
            f"Theme Paradox: {self.theme_paradox}",
            f"  Side A: {self.theme_side_a}",
            f"  Side B: {self.theme_side_b}",
            "",
            f"Fairy Tale Role: {self.fairy_tale_role}",
            f"  Cost: {self.fairy_tale_cost}",
            f"  Danger: {self.fairy_tale_danger}",
            "",
            f"Pitch: {self.one_sentence_pitch}",
            "",
            f"Validation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}",
            f"  Rules defined: {validation['rules_defined']}/8",
        ]

        if not validation['valid']:
            for err in validation['errors']:
                lines.append(f"  ❌ {err}")

        return "\n".join(lines)


@dataclass
class LocationSpec:
    """A specific location, not a country or city name."""
    country: str = ""
    specific_place: str = ""     # "Bakery at 14 Rue de Rivoli, Paris"
    time: str = ""               # "6:00 AM, Tuesday, November"
    sensory_details: str = ""    # "Smell of warm croissants, wet cobblestones, grey light"
    why_this_place: str = ""     # Why THIS place matters to the story
    what_happens_here: str = ""  # What story event occurs here


# ═══════════════════════════════════════════════════════
# GENERATION PROMPTS
# ═══════════════════════════════════════════════════════

TRANSMUTATION_PROMPT = """You are a master storyteller who has studied every great
animated film ever made. You understand WHY stories work at a structural level,
but you also know that structure without surprise is death.

You are transmuting a Film Genome Document from a reference film into a new,
original film. You have been given:

1. The reference Film Genome (the DNA to preserve)
2. A creative direction (the mutation vector)
3. A set of MUTATION RULES (constraints that force originality)

## YOUR TASK

Create a new Film Genome Document that:
- PRESERVES the reference film's structural DNA (beat timing, emotional arc shape,
  causal chain logic, pacing dynamics)
- MUTATES everything else through the creative direction and mutation rules
- PASSES the Judgment Engine (score >= 0.70 on all dimensions, zero kill criteria)

## CRITICAL RULES

1. **NO EXTERNAL VILLAINS.** The conflict must be internal, systemic, or a genuine
   dilemma where both sides have a point.

2. **NO BUMPER STICKER THEMES.** The theme must be a PARADOX that smart people can
   disagree about. If you can print it on a t-shirt, it's too simple.

3. **NO TOURIST SETTINGS.** Every location must have a specific address, a specific
   time, specific sensory details. I want to SMELL the place.

4. **NO NAIVE PROTAGONISTS.** The protagonist must have a quality that makes the
   audience uncomfortable. Not a cute flaw — something that makes you wonder if
   they're the good guy.

5. **NO HELPER FAIRY TALES.** Fairy tales are not cute friends. They are ancient,
   powerful, ambiguous forces with their own agenda and a COST for engaging with them.

6. **THE PITCH TEST.** Before you start, write your one-sentence pitch. If it sounds
   like any existing film, START OVER.

7. **GENRE COLLISION.** The film must be two genres at once — one visible, one hidden.
   This is what makes great films surprising.

## REFERENCE GENOME:
{reference_genome}

## CREATIVE DIRECTION:
{creative_direction}

## MUTATION RULES:
{mutation_rules}

## OUTPUT:
A complete Film Genome Document in YAML format with all 8 strands.
Include TRANSMUTATION NOTES in comments showing what was preserved vs mutated.
"""


# ═══════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example: Kazka v2 mutation rules (fixing v1's failures)
    rules = MutationRules(
        genre_primary="coming-of-age road movie",
        genre_hidden="psychological horror",
        genre_collision_note=(
            "It LOOKS like a Pixar adventure but FEELS like Pan's Labyrinth. "
            "The fairy tales aren't cute — they're manifestations of displacement "
            "trauma that the protagonist can't control."
        ),

        villain_type="internal",
        villain_note=(
            "No villain. The conflict is Olenka vs her own displacement trauma. "
            "The fairy tales are HER psyche — they become dangerous when she's "
            "angry, beautiful when she's at peace, and they'll consume her if "
            "she can't integrate the trauma."
        ),

        locations=[
            LocationSpec(
                country="France",
                specific_place="The basement of a refugee processing center in Calais",
                time="2:00 AM, February, fluorescent lighting",
                sensory_details="Bleach, instant coffee, the hum of ventilation, "
                                "children sleeping on cots, whispered phone calls",
                why_this_place="Not tourist Paris — the REAL first stop for displaced people",
                what_happens_here="The first fairy tale manifests here — in the worst possible place"
            ),
            LocationSpec(
                country="Switzerland",
                specific_place="A psychiatric facility for displaced children near Zurich",
                time="Afternoon, sterile white rooms, snow outside",
                sensory_details="Antiseptic, clicking pens, the therapist's too-calm voice",
                why_this_place="Switzerland as the place that 'helps' by trying to make you forget",
                what_happens_here="A therapist tells Olenka the fairy tales are delusions"
            ),
            LocationSpec(
                country="Germany",
                specific_place="An empty apartment in Berlin-Neukölln assigned by social services",
                time="Evening, autumn, neighbors playing Turkish music through walls",
                sensory_details="New paint smell, IKEA furniture, someone else's curtains, "
                                "the specific loneliness of a place that's yours but isn't HOME",
                why_this_place="The cruel kindness of being given a 'home' that isn't one",
                what_happens_here="Olenka tries to destroy the fairy tale book"
            ),
        ],

        protagonist_uncomfortable_quality=(
            "Olenka is CRUEL to people who try to help her. She pushes away every "
            "kind adult because accepting help means accepting that she needs it — "
            "which means accepting that her old life is gone. Her cruelty is a "
            "defense mechanism, but it hurts real people."
        ),
        protagonist_worst_action=(
            "She tells a foster family's biological child that their 'problems "
            "aren't real problems' because they've never lost a country. The child "
            "cries. Olenka knows she was wrong but can't bring herself to apologize."
        ),

        theme_paradox="To heal, you must remember. But remembering is what keeps the wound open.",
        theme_side_a="Forgetting is freedom — the therapist's position. Let go, move forward, assimilate.",
        theme_side_b="Remembering is identity — grandmother's position. Hold on, carry forward, resist erasure.",

        fairy_tale_role=(
            "The fairy tales are involuntary manifestations of Olenka's emotional state. "
            "She doesn't control them. When she's angry, the Iron Wolf appears and BREAKS "
            "things. When she's grieving, the Mavka appears and drowns people in nostalgia. "
            "When she's hopeful, the Firebird appears and it's beautiful — but also "
            "terrifyingly powerful. They are her TRAUMA given form."
        ),
        fairy_tale_cost=(
            "Every time a fairy tale manifests, Olenka loses a memory. The cost of "
            "expressing trauma through story is that the story EATS the original memory. "
            "If she lets all the fairy tales out, she'll have the stories but not "
            "the real memories of her grandmother, her home, her life."
        ),
        fairy_tale_danger=(
            "The fairy tales don't distinguish between helping and destroying. The Iron "
            "Wolf protects Olenka by attacking anyone who upsets her — including kind "
            "people. Lys the Fox lies to everyone, including Olenka, because that's "
            "what foxes DO in the old tales. They are pre-moral forces."
        ),

        comparable_works=[
            "Pan's Labyrinth (2006) — child uses fantasy to cope with real horror",
            "Spirited Away (2001) — displaced child in a world of dangerous spirits",
            "The Florida Project (2017) — child's perspective on instability",
            "Wolfwalkers (2020) — folk mythology meets real historical displacement",
        ],
        differentiation=(
            "Unlike Pan's Labyrinth, the fantasy isn't an escape — it's the PROBLEM. "
            "Unlike Spirited Away, the protagonist doesn't enter a fantasy world — "
            "the fantasy world leaks into ours and can't be controlled. Unlike "
            "Wolfwalkers, the mythology isn't empowering — it's the manifestation "
            "of trauma that threatens to consume the protagonist. "
            "The unique element: fairy tales as INVOLUNTARY emotional expression, "
            "like panic attacks in narrative form."
        ),

        one_sentence_pitch=(
            "A displaced Ukrainian girl's fairy tales escape her grandmother's book "
            "and begin manifesting as dangerous, uncontrollable forces that feed on "
            "her trauma — and every time one appears, she loses a real memory."
        ),
        pitch_uniqueness_score=0.80,
    )

    print(rules.summary())
