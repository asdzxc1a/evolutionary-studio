"""
Judgment Engine — System 4, Component 4

Evaluates generated content against quality criteria.
The component that catches "generic" and "boring" BEFORE showing output to a human.

This is the component that was MISSING when we produced the generic Kazka story.
It should have killed that draft before it reached the user.

SCORING DIMENSIONS:
1. Surprise Factor    — Does this subvert expectations? Is there a genre mismatch?
2. Emotional Danger   — Are the stakes real? Can the protagonist FAIL in a way that hurts?
3. Specificity        — Is this grounded in real, specific details (not tourism-poster generics)?
4. Thematic Depth     — Is the theme complex, debatable, not preachy?
5. Character Edge     — Do characters have genuine flaws, not movie-flaws?
6. Originality        — Has this exact story been told before? (Pagemaster test)
7. DNA Fidelity       — Does it actually carry the reference film's structural DNA?
8. Cultural Authenticity — Are cultural elements genuine, not decorative?

KILL CRITERIA (instant rejection):
- The villain is "a corporation" or "a shadowy force"
- The message can be stated in one bumper-sticker sentence
- The protagonist is "good but naive" with no real darkness
- Any country/city is described as a tourist would describe it
- The fairy tales are "helpers" (Pagemaster/Inkheart clone)
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScoreCard:
    """Quality evaluation for a generated Film Genome or content piece."""

    # Core scores (0.0 - 1.0)
    surprise_factor: float = 0.0
    emotional_danger: float = 0.0
    specificity: float = 0.0
    thematic_depth: float = 0.0
    character_edge: float = 0.0
    originality: float = 0.0
    dna_fidelity: float = 0.0
    cultural_authenticity: float = 0.0

    # Kill flags (any True = instant reject)
    kill_corporate_villain: bool = False
    kill_bumper_sticker_theme: bool = False
    kill_naive_protagonist: bool = False
    kill_tourism_setting: bool = False
    kill_helper_fairy_tales: bool = False
    kill_seen_before: bool = False

    # Feedback
    diagnosis: str = ""
    what_works: list = field(default_factory=list)
    what_fails: list = field(default_factory=list)
    fix_suggestions: list = field(default_factory=list)
    comparable_existing_works: list = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Weighted average. Surprise and originality weighted highest."""
        weights = {
            'surprise_factor': 0.20,
            'emotional_danger': 0.15,
            'specificity': 0.10,
            'thematic_depth': 0.15,
            'character_edge': 0.10,
            'originality': 0.15,
            'dna_fidelity': 0.10,
            'cultural_authenticity': 0.05,
        }
        total = sum(
            getattr(self, dim) * weight
            for dim, weight in weights.items()
        )
        return round(total, 3)

    @property
    def killed(self) -> bool:
        """Whether any kill criteria triggered."""
        return any([
            self.kill_corporate_villain,
            self.kill_bumper_sticker_theme,
            self.kill_naive_protagonist,
            self.kill_tourism_setting,
            self.kill_helper_fairy_tales,
            self.kill_seen_before,
        ])

    @property
    def kill_reasons(self) -> list:
        """List of triggered kill criteria."""
        reasons = []
        if self.kill_corporate_villain:
            reasons.append("KILL: Villain is a generic corporation/shadowy force")
        if self.kill_bumper_sticker_theme:
            reasons.append("KILL: Theme is a bumper sticker ('stories matter!', 'be yourself!')")
        if self.kill_naive_protagonist:
            reasons.append("KILL: Protagonist is 'good but naive' with no real darkness")
        if self.kill_tourism_setting:
            reasons.append("KILL: Settings are described like a travel brochure")
        if self.kill_helper_fairy_tales:
            reasons.append("KILL: Fairy tales are cute helpers (Pagemaster/Inkheart clone)")
        if self.kill_seen_before:
            reasons.append("KILL: This story already exists (provide comparable works)")
        return reasons

    @property
    def pass_threshold(self) -> bool:
        """Does this meet minimum quality for human review?"""
        return not self.killed and self.overall_score >= 0.70

    def summary(self) -> str:
        """Human-readable quality report."""
        lines = [
            "═══ JUDGMENT ENGINE — QUALITY REPORT ═══",
            "",
        ]

        if self.killed:
            lines.append("🔴 VERDICT: KILLED — DO NOT SHOW TO USER")
            lines.append("")
            for reason in self.kill_reasons:
                lines.append(f"  💀 {reason}")
            lines.append("")
        elif self.overall_score >= 0.85:
            lines.append("🟢 VERDICT: EXCEPTIONAL — ready for user review")
        elif self.overall_score >= 0.70:
            lines.append("🟡 VERDICT: ACCEPTABLE — needs polish before user review")
        else:
            lines.append("🔴 VERDICT: BELOW THRESHOLD — regenerate with fixes")

        lines.append("")
        lines.append(f"Overall Score: {self.overall_score:.2f} / 1.00")
        lines.append("")
        lines.append("Dimension Scores:")
        lines.append(f"  Surprise Factor:      {self._bar(self.surprise_factor)} {self.surprise_factor:.2f}")
        lines.append(f"  Emotional Danger:     {self._bar(self.emotional_danger)} {self.emotional_danger:.2f}")
        lines.append(f"  Specificity:          {self._bar(self.specificity)} {self.specificity:.2f}")
        lines.append(f"  Thematic Depth:       {self._bar(self.thematic_depth)} {self.thematic_depth:.2f}")
        lines.append(f"  Character Edge:       {self._bar(self.character_edge)} {self.character_edge:.2f}")
        lines.append(f"  Originality:          {self._bar(self.originality)} {self.originality:.2f}")
        lines.append(f"  DNA Fidelity:         {self._bar(self.dna_fidelity)} {self.dna_fidelity:.2f}")
        lines.append(f"  Cultural Authenticity: {self._bar(self.cultural_authenticity)} {self.cultural_authenticity:.2f}")

        if self.what_works:
            lines.append("")
            lines.append("✅ What Works:")
            for item in self.what_works:
                lines.append(f"  • {item}")

        if self.what_fails:
            lines.append("")
            lines.append("❌ What Fails:")
            for item in self.what_fails:
                lines.append(f"  • {item}")

        if self.fix_suggestions:
            lines.append("")
            lines.append("🔧 Fix Suggestions:")
            for item in self.fix_suggestions:
                lines.append(f"  → {item}")

        if self.comparable_existing_works:
            lines.append("")
            lines.append("⚠️ Similar Existing Works:")
            for item in self.comparable_existing_works:
                lines.append(f"  • {item}")

        if self.diagnosis:
            lines.append("")
            lines.append(f"Diagnosis: {self.diagnosis}")

        return "\n".join(lines)

    @staticmethod
    def _bar(value: float, width: int = 20) -> str:
        """Visual bar for score display."""
        filled = int(value * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"


# ═══════════════════════════════════════════════════════
# JUDGMENT PROMPTS — Used by the Creative Loop Engine
# ═══════════════════════════════════════════════════════

JUDGMENT_PROMPT = """You are a ruthless creative director and film executive.
You have greenlit films that made $1B and killed projects that would have been
embarrassments. You have NO patience for generic, safe, or boring.

You are evaluating a Film Genome Document for a new animated film.
Your job is to score it HONESTLY and KILL it if it's not good enough.

## SCORING DIMENSIONS (score each 0.0 to 1.0)

### 1. SURPRISE FACTOR
- 0.0: "I've seen this exact story before"
- 0.3: "This has one unexpected element"
- 0.5: "This has an interesting twist on a familiar formula"
- 0.7: "This subverts expectations in a way that's exciting"
- 1.0: "I've never seen anything like this — it redefines the genre"
Questions to ask:
- What genre does this THINK it is? What genre is it ACTUALLY?
- Where does this zig when I expected it to zag?
- If I described this to someone in one sentence, would they say "tell me more"?

### 2. EMOTIONAL DANGER
- 0.0: "The protagonist never really risks anything"
- 0.3: "There's a moment of sadness but it's safe"
- 0.5: "The protagonist could genuinely lose something important"
- 0.7: "The protagonist might BECOME the villain if they're not careful"
- 1.0: "The audience will be genuinely afraid for the protagonist's soul"
Questions to ask:
- What's the WORST thing that could happen to this character?
- Does the film go there, or does it flinch?
- Would a child watching this feel genuinely scared for the character?

### 3. SPECIFICITY
- 0.0: "This could be set anywhere, with anyone"
- 0.3: "There are some cultural details but they're decorative"
- 0.5: "The setting matters to the story"
- 0.7: "This story COULD NOT be told in any other setting"
- 1.0: "Every detail is so specific it feels like a documentary"
Questions to ask:
- Could I swap this setting for another and the story still works? (Bad if yes)
- Are there details only someone who LIVED HERE would know?
- Do the cultural elements drive the plot, or just decorate it?

### 4. THEMATIC DEPTH
- 0.0: "The theme is a bumper sticker ('be yourself!')"
- 0.3: "The theme has two sides but one is clearly right"
- 0.5: "Smart people could disagree about which side is right"
- 0.7: "The film argues AGAINST its own theme at some point"
- 1.0: "After the film ends, the audience will still be debating"
Questions to ask:
- Can I state the theme in 5 words? (Bad if too easy)
- Does the villain have a point? A GOOD point?
- Would a philosopher find something interesting here?

### 5. CHARACTER EDGE
- 0.0: "The protagonist is 'good but naive' — a Disney template"
- 0.3: "The protagonist has a flaw but it's endearing"
- 0.5: "The protagonist does something genuinely wrong"
- 0.7: "The protagonist has a quality that makes them hard to like sometimes"
- 1.0: "The protagonist makes you uncomfortable — and you can't look away"
Questions to ask:
- Would I want to be friends with this character? (Best answer: "complicated")
- Does the character do anything that makes the AUDIENCE feel bad?
- Is the character's flaw cosmetic or structural?

### 6. ORIGINALITY
- 0.0: "This is a known existing movie with different names"
- 0.3: "I can name 3 movies this is similar to"
- 0.5: "I can see the influences but the combination is fresh"
- 0.7: "The core concept is new — I haven't seen this before"
- 1.0: "This creates a new category"
List ALL comparable works. If you can name more than 3, the score drops.

### 7. DNA FIDELITY
- 0.0: "This has nothing to do with the reference film"
- 0.5: "The structure matches but the feeling doesn't"
- 0.7: "Structure and emotional arc both transfer well"
- 1.0: "It FEELS like the reference film in a new skin"

### 8. CULTURAL AUTHENTICITY
- 0.0: "The cultural elements are stereotypes"
- 0.5: "The cultural elements are accurate but surface-level"
- 1.0: "Someone from this culture would say 'they got it right'"

## KILL CRITERIA (check each)
- [ ] KILL_CORPORATE_VILLAIN: Is the villain a corporation, shadowy organization, or generic "force"?
- [ ] KILL_BUMPER_STICKER_THEME: Can the theme be printed on a t-shirt?
- [ ] KILL_NAIVE_PROTAGONIST: Is the protagonist "good but naive" with no real edge?
- [ ] KILL_TOURISM_SETTING: Are the locations described like a travel brochure?
- [ ] KILL_HELPER_FAIRY_TALES: Are fairy tales just "magic friends who help"?
- [ ] KILL_SEEN_BEFORE: Does this story already exist as a film?

## OUTPUT FORMAT
Return a JSON object with all scores, kill flags, and textual feedback.
Be SPECIFIC in your feedback — don't say "needs more edge", say exactly
what scene needs what change.

## THE GENOME TO EVALUATE:
{genome_yaml}

## THE REFERENCE FILM:
{reference_film}

## CREATIVE DIRECTION GIVEN:
{creative_direction}
"""

SELF_SCORE_KAZKA_V1 = ScoreCard(
    surprise_factor=0.20,
    emotional_danger=0.25,
    specificity=0.15,
    thematic_depth=0.30,
    character_edge=0.20,
    originality=0.15,
    dna_fidelity=0.85,
    cultural_authenticity=0.30,

    kill_corporate_villain=True,
    kill_bumper_sticker_theme=True,
    kill_naive_protagonist=True,
    kill_tourism_setting=True,
    kill_helper_fairy_tales=True,
    kill_seen_before=True,

    diagnosis=(
        "The Kazka v1 genome is a structural success (DNA fidelity 0.85) "
        "but a creative failure. It triggers ALL SIX kill criteria. "
        "The transmutation engine preserved the skeleton perfectly but "
        "produced dead flesh. The system needs a creative mutation layer "
        "that forces genre-breaking, specificity, and character danger "
        "BEFORE the genome is assembled."
    ),
    what_works=[
        "Beat-for-beat structural mapping from Zootopia is solid",
        "Causal chain logic is airtight",
        "Emotional valence/arousal curve matches reference precisely",
        "The Fox (Lys) as deuteragonist is a natural DNA transfer",
    ],
    what_fails=[
        "'The Forgetting' is a cliché villain concept — Coco already did 'being forgotten'",
        "'The Archivist' is a generic corporate villain in a suit",
        "Paris, Switzerland, Germany described like a Lonely Planet guide",
        "Olenka is 'good but naive' — exact same flaw as Judy without Judy's specificity",
        "Theme ('stories are who we are') fits on a bumper sticker",
        "Fairy tales as 'helpers who appear when you read them' = Pagemaster (1994)",
        "The ferry interview scene is the press conference with different words",
    ],
    fix_suggestions=[
        "Genre mismatch: Make this a THRILLER, not an adventure. What if Olenka is running FROM the fairy tales?",
        "Villain: No villain. The conflict is INTERNAL — Olenka vs her own displacement trauma",
        "Setting specificity: Each country should be a SPECIFIC place, not a country. A specific street in Lyon, not 'France'",
        "Character edge: Olenka should be ANGRY, not naive. She resents being displaced. She takes it out on people",
        "Fairy tales: They should be UNCONTROLLABLE, not helpful. They manifest her subconscious fears",
        "Theme: Make it debatable. 'Is it better to forget and move on, or remember and be trapped?'",
    ],
    comparable_existing_works=[
        "The Pagemaster (1994) — books come to life to help a child",
        "Inkheart (2008) — reading brings fairy tales to life",
        "Coco (2017) — being forgotten as the threat",
        "The NeverEnding Story (1984) — child enters story world to save it",
        "Kubo and the Two Strings (2016) — mythical quest with cultural identity",
        "Strange World (2022) — travel-adventure animated film",
    ],
)


# Entry point for quick testing
if __name__ == "__main__":
    print(SELF_SCORE_KAZKA_V1.summary())
