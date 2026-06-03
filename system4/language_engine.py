"""Language Engine — System 4, Phase 2

Analyzes character voice consistency, dialogue quality, and subtext.
Generates voice profiles, scores dialogue lines, suggests rewrites.

Inspired by:
- Blake Snyder's dialogue rules (Save the Cat)
- Robert McKee's "Dialogue: The Art of Verbal Action for Stage, Page, and Screen"
- Pixar's story rules (especially #10: "Pull apart the characters you love")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

# Lazy imports to avoid circular dependency
import sys
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))


# =============================================================================
# Voice Profile
# =============================================================================

@dataclass
class VoiceProfile:
    """A character's vocal fingerprint — how they speak, not what they say."""
    character_id: str
    character_name: str
    archetype: str = ""
    
    # Six dimensions of voice (0-100 scale)
    sarcasm: float = 50.0        # Irony, understatement, deflection
    cynicism: float = 50.0       # Negative expectations, distrust
    warmth: float = 50.0         # Affection, caring, openness
    formality: float = 50.0      # Vocabulary, grammar, contractions
    verbosity: float = 50.0      # Word count per sentence
    subtext: float = 50.0        # Implication vs direct statement
    
    # Derived properties
    vocabulary_level: str = "moderate"  # simple, moderate, sophisticated
    sentence_structure: str = "mixed"   # short, mixed, complex
    
    # Character-specific patterns
    signature_phrases: list[str] = field(default_factory=list)
    forbidden_phrases: list[str] = field(default_factory=list)
    catchphrases: list[str] = field(default_factory=list)
    
    # Emotional range
    emotional_range: tuple[float, float] = (-0.8, 0.8)  # min, max valence they express
    
    def get_description(self) -> str:
        """Human-readable voice description."""
        traits = []
        if self.sarcasm > 70:
            traits.append("highly sarcastic")
        elif self.sarcasm < 30:
            traits.append("earnest")
        
        if self.cynicism > 70:
            traits.append("deeply cynical")
        elif self.cynicism < 30:
            traits.append("optimistic")
        
        if self.warmth > 70:
            traits.append("warm")
        elif self.warmth < 30:
            traits.append("cold")
        
        if self.formality > 70:
            traits.append("formal")
        elif self.formality < 30:
            traits.append("colloquial")
        
        if self.verbosity > 70:
            traits.append("verbose")
        elif self.verbosity < 30:
            traits.append("terse")
        
        if self.subtext > 70:
            traits.append("subtext-heavy")
        elif self.subtext < 30:
            traits.append("direct")
        
        trait_str = ", ".join(traits) if traits else "balanced"
        return f"{self.character_name} speaks in a {trait_str} voice."


# =============================================================================
# Archetype Voice Templates
# =============================================================================

ARCHETYPE_VOICES: dict[str, dict[str, Any]] = {
    "optimistic underdog": {
        "sarcasm": 15, "cynicism": 10, "warmth": 85, "formality": 60,
        "verbosity": 70, "subtext": 25,
        "vocabulary_level": "moderate", "sentence_structure": "mixed",
        "signature_phrases": ["I know I can", "Watch me", "I won't give up"],
        "forbidden_phrases": ["It's hopeless", "I don't care", "Whatever"],
    },
    "cynical trickster": {
        "sarcasm": 90, "cynicism": 75, "warmth": 20, "formality": 25,
        "verbosity": 60, "subtext": 85,
        "vocabulary_level": "moderate", "sentence_structure": "short",
        "signature_phrases": ["It's called a hustle", "Never let them see", "Sly fox"],
        "forbidden_phrases": ["I apologize", "I was wrong", "I trust you"],
    },
    "hidden tyrant": {
        "sarcasm": 40, "cynicism": 60, "warmth": 15, "formality": 80,
        "verbosity": 50, "subtext": 70,
        "vocabulary_level": "sophisticated", "sentence_structure": "complex",
        "signature_phrases": ["For the greater good", "You leave me no choice", "It's necessary"],
        "forbidden_phrases": ["I'm sorry", "I don't know", "Please"],
    },
    "naive idealist": {
        "sarcasm": 10, "cynicism": 5, "warmth": 90, "formality": 65,
        "verbosity": 75, "subtext": 20,
        "vocabulary_level": "moderate", "sentence_structure": "mixed",
        "signature_phrases": ["I believe in", "We can make a difference", "Everyone deserves"],
        "forbidden_phrases": ["People are terrible", "It's all pointless", "I hate"],
    },
    "wounded veteran": {
        "sarcasm": 70, "cynicism": 80, "warmth": 30, "formality": 40,
        "verbosity": 40, "subtext": 75,
        "vocabulary_level": "moderate", "sentence_structure": "short",
        "signature_phrases": ["I've seen enough", "Trust me, you don't want to", "Old habits"],
        "forbidden_phrases": ["Everything will be fine", "I believe in the system", "Love conquers all"],
    },
    "corrupt bureaucrat": {
        "sarcasm": 50, "cynicism": 80, "warmth": 10, "formality": 90,
        "verbosity": 60, "subtext": 60,
        "vocabulary_level": "sophisticated", "sentence_structure": "complex",
        "signature_phrases": ["Regulations clearly state", "I'm just doing my job", "It's out of my hands"],
        "forbidden_phrases": ["I was wrong", "Let's break the rules", "I care"],
    },
    "reluctant mentor": {
        "sarcasm": 60, "cynicism": 50, "warmth": 70, "formality": 50,
        "verbosity": 55, "subtext": 65,
        "vocabulary_level": "moderate", "sentence_structure": "mixed",
        "signature_phrases": ["I didn't sign up for this", "One more thing", "Listen to me"],
        "forbidden_phrases": ["I love this", "This is easy", "No problem"],
    },
    "charismatic demagogue": {
        "sarcasm": 30, "cynicism": 40, "warmth": 70, "formality": 60,
        "verbosity": 80, "subtext": 50,
        "vocabulary_level": "moderate", "sentence_structure": "complex",
        "signature_phrases": ["My friends", "They don't want you to know", "Together we will"],
        "forbidden_phrases": ["I don't know", "I was wrong", "It's complicated"],
    },
    "curious explorer": {
        "sarcasm": 30, "cynicism": 20, "warmth": 75, "formality": 50,
        "verbosity": 70, "subtext": 40,
        "vocabulary_level": "moderate", "sentence_structure": "mixed",
        "signature_phrases": ["What if", "I wonder", "Have you ever noticed"],
        "forbidden_phrases": ["I don't care", "It's boring", "Not my problem"],
    },
    "jaded survivor": {
        "sarcasm": 80, "cynicism": 90, "warmth": 15, "formality": 30,
        "verbosity": 35, "subtext": 80,
        "vocabulary_level": "simple", "sentence_structure": "short",
        "signature_phrases": ["Seen it all", "Doesn't matter", "Trust no one"],
        "forbidden_phrases": ["Everything happens for a reason", "People are good", "I have hope"],
    },
    "manipulative advisor": {
        "sarcasm": 60, "cynicism": 70, "warmth": 40, "formality": 75,
        "verbosity": 65, "subtext": 90,
        "vocabulary_level": "sophisticated", "sentence_structure": "complex",
        "signature_phrases": ["If I may suggest", "Consider the optics", "For your own good"],
        "forbidden_phrases": ["I want", "I need", "Help me"],
    },
    "determined reformer": {
        "sarcasm": 25, "cynicism": 35, "warmth": 70, "formality": 70,
        "verbosity": 65, "subtext": 45,
        "vocabulary_level": "moderate", "sentence_structure": "mixed",
        "signature_phrases": ["The system is broken", "We must change", "For justice"],
        "forbidden_phrases": ["It's fine the way it is", "Why bother", "I give up"],
    },
    "apathetic con-artist": {
        "sarcasm": 85, "cynicism": 70, "warmth": 25, "formality": 30,
        "verbosity": 55, "subtext": 80,
        "vocabulary_level": "moderate", "sentence_structure": "short",
        "signature_phrases": ["Trust me", "It's a win-win", "What's in it for me"],
        "forbidden_phrases": ["I care about you", "This is wrong", "I want to help"],
    },
    "earnest believer": {
        "sarcasm": 5, "cynicism": 10, "warmth": 90, "formality": 60,
        "verbosity": 70, "subtext": 20,
        "vocabulary_level": "moderate", "sentence_structure": "mixed",
        "signature_phrases": ["I know we can", "Together", "I believe"],
        "forbidden_phrases": ["It's pointless", "Nobody cares", "Why try"],
    },
    "sarcastic realist": {
        "sarcasm": 90, "cynicism": 65, "warmth": 40, "formality": 40,
        "verbosity": 50, "subtext": 75,
        "vocabulary_level": "moderate", "sentence_structure": "short",
        "signature_phrases": ["Oh great", "Perfect", "Just what I needed"],
        "forbidden_phrases": ["Everything is wonderful", "I'm so happy", "Life is beautiful"],
    },
    "ambitious schemer": {
        "sarcasm": 40, "cynicism": 60, "warmth": 20, "formality": 70,
        "verbosity": 60, "subtext": 80,
        "vocabulary_level": "sophisticated", "sentence_structure": "complex",
        "signature_phrases": ["I have a plan", "Trust the process", "Long game"],
        "forbidden_phrases": ["I don't know what to do", "Let's just wing it", "I trust you completely"],
    },
}


def _normalize_archetype(archetype: str) -> str:
    """Normalize archetype name for template lookup."""
    archetype = archetype.lower().strip()
    # Direct match
    if archetype in ARCHETYPE_VOICES:
        return archetype
    # Try to find partial match
    for template_name in ARCHETYPE_VOICES:
        if template_name in archetype or archetype in template_name:
            return template_name
    # Default
    return "optimistic underdog"


# =============================================================================
# Dialogue Analysis
# =============================================================================

@dataclass
class DialogueScore:
    """Score for a single dialogue line."""
    line: str
    speaker: str
    voice_consistency: float = 0.0  # 0.0-1.0
    subtext_score: float = 0.0       # 0.0-1.0
    on_the_nose: bool = False
    formality_match: float = 0.0     # 0.0-1.0
    verbosity_match: float = 0.0     # 0.0-1.0
    warmth_match: float = 0.0        # 0.0-1.0
    cynicism_match: float = 0.0      # 0.0-1.0
    sarcasm_match: float = 0.0       # 0.0-1.0
    
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    rewrite: Optional[str] = None


@dataclass
class ScreenplayDialogueAnalysis:
    """Analysis of all dialogue in a screenplay."""
    total_lines: int = 0
    total_speakers: int = 0
    lines_by_speaker: dict[str, list[DialogueScore]] = field(default_factory=dict)
    voice_violations: list[DialogueScore] = field(default_factory=list)
    on_the_nose_lines: list[DialogueScore] = field(default_factory=list)
    low_subtext_lines: list[DialogueScore] = field(default_factory=list)
    overall_voice_consistency: float = 0.0
    overall_subtext_score: float = 0.0
    
    def get_worst_lines(self, n: int = 3) -> list[DialogueScore]:
        """Get the N worst-scoring lines."""
        all_lines = []
        for speaker_lines in self.lines_by_speaker.values():
            all_lines.extend(speaker_lines)
        all_lines.sort(key=lambda x: x.voice_consistency)
        return all_lines[:n]
    
    def get_speaker_consistency(self, speaker: str) -> float:
        """Get average voice consistency for a speaker."""
        lines = self.lines_by_speaker.get(speaker, [])
        if not lines:
            return 0.0
        return sum(l.voice_consistency for l in lines) / len(lines)


# =============================================================================
# Language Engine
# =============================================================================

class LanguageEngine:
    """Analyzes dialogue for voice consistency, subtext, and quality."""
    
    # Markers for linguistic analysis
    SARCASM_MARKERS = [
        "oh great", "perfect", "just what i needed", "wonderful", "fantastic",
        "sure", "obviously", "clearly", "obviously", "of course",
        "because that worked", "what could go wrong", "this is fine",
    ]
    
    CYNICISM_MARKERS = [
        "never", "always", "nobody", "everyone", "nothing",
        "people are", "the world is", "it doesn't matter",
        "why bother", "what's the point", "trust no one",
    ]
    
    WARMTH_MARKERS = [
        "care", "friend", "together", "help", "thank", "please",
        "appreciate", "grateful", "kind", "gentle", "sorry",
    ]
    
    FORMAL_MARKERS = [
        "however", "furthermore", "nevertheless", "therefore",
        "consequently", "regarding", "pursuant", "hereby",
    ]
    
    INFORMAL_MARKERS = [
        "gonna", "wanna", "kinda", "sorta", "yeah", "nah",
        "dunno", "lemme", "gimme", "ain't", "y'all",
    ]
    
    ON_THE_NOSE_PATTERNS = [
        r"i (feel|am|'m) (so |very |really |just |kind of )*(sad|angry|happy|scared|worried|excited|disappointed|lonely|jealous|betrayed)",
        r"the moral of the story is",
        r"the lesson here is",
        r"what i'm trying to say is",
        r"what i mean is",
        r"i love you" + r"\s+(because|and the reason is)",
        r"i'm afraid of",
        r"i trust you" + r"\s+(because|since)",
    ]
    
    EMOTION_DIRECT_STATEMENTS = [
        "i love you", "i hate you", "i'm sorry", "i forgive you",
        "i'm angry", "i'm sad", "i'm happy", "i'm scared",
        "i trust you", "i don't trust you",
    ]
    
    def __init__(self):
        self.voice_profiles: dict[str, VoiceProfile] = {}
    
    # ========================================================================
    # Voice Profile Generation
    # ========================================================================
    
    def create_voice_profile(self, character_id: str, character_name: str,
                             archetype: str, starting_state: str = "",
                             ending_state: str = "") -> VoiceProfile:
        """Generate a voice profile from character data."""
        template = ARCHETYPE_VOICES.get(_normalize_archetype(archetype), {})
        
        profile = VoiceProfile(
            character_id=character_id,
            character_name=character_name,
            archetype=archetype,
            sarcasm=template.get("sarcasm", 50.0),
            cynicism=template.get("cynicism", 50.0),
            warmth=template.get("warmth", 50.0),
            formality=template.get("formality", 50.0),
            verbosity=template.get("verbosity", 50.0),
            subtext=template.get("subtext", 50.0),
            vocabulary_level=template.get("vocabulary_level", "moderate"),
            sentence_structure=template.get("sentence_structure", "mixed"),
            signature_phrases=list(template.get("signature_phrases", [])),
            forbidden_phrases=list(template.get("forbidden_phrases", [])),
        )
        
        # Adjust based on arc direction
        if starting_state and ending_state:
            start_lower = starting_state.lower()
            end_lower = ending_state.lower()
            
            # If character becomes warmer, start slightly colder
            if "warm" in end_lower or "open" in end_lower or "trust" in end_lower:
                if "cold" in start_lower or "closed" in start_lower or "distant" in start_lower:
                    profile.warmth = max(10.0, profile.warmth - 15)
            
            # If character becomes less cynical, start more cynical
            if "hope" in end_lower or "trust" in end_lower or "believe" in end_lower:
                if "cynic" in start_lower or "jaded" in start_lower:
                    profile.cynicism = min(95.0, profile.cynicism + 15)
        
        self.voice_profiles[character_id] = profile
        return profile
    
    def load_voice_profiles_from_vault(self, character_notes: list[Any]) -> dict[str, VoiceProfile]:
        """Load voice profiles from character notes in vault."""
        profiles = {}
        for note in character_notes:
            frontmatter = getattr(note, 'frontmatter', {})
            char_id = frontmatter.get("character_id", "")
            name = frontmatter.get("name", "")
            archetype = frontmatter.get("archetype", "")
            
            if char_id and name:
                profile = self.create_voice_profile(char_id, name, archetype)
                profiles[char_id] = profile
        
        return profiles
    
    # ========================================================================
    # Dialogue Scoring
    # ========================================================================
    
    def score_dialogue(self, line: str, speaker_id: str) -> DialogueScore:
        """Score a single dialogue line against the speaker's voice profile."""
        profile = self.voice_profiles.get(speaker_id)
        if not profile:
            return DialogueScore(line=line, speaker=speaker_id, voice_consistency=0.5,
                                issues=["No voice profile found for speaker"])
        
        issues = []
        suggestions = []
        line_lower = line.lower()
        
        # 1. Sarcasm match
        sarcasm_score = self._score_sarcasm(line_lower, profile)
        
        # 2. Cynicism match
        cynicism_score = self._score_cynicism(line_lower, profile)
        
        # 3. Warmth match
        warmth_score = self._score_warmth(line_lower, profile)
        
        # 4. Formality match
        formality_score = self._score_formality(line_lower, profile)
        
        # 5. Verbosity match
        verbosity_score = self._score_verbosity(line, profile)
        
        # 6. Subtext score
        subtext_score = self._analyze_subtext(line)
        
        # 7. On-the-nose detection
        on_the_nose = self._detect_on_the_nose(line_lower)
        if on_the_nose:
            issues.append("Line is on-the-nose (states emotion directly)")
            suggestions.append("Replace direct emotional statement with action or subtext")
        
        # 8. Forbidden phrases
        for forbidden in profile.forbidden_phrases:
            if forbidden.lower() in line_lower:
                issues.append(f"Uses forbidden phrase: '{forbidden}'")
                suggestions.append(f"This character would never say '{forbidden}' — rewrite to match their voice")
        
        # 9. Signature phrases (bonus for using)
        signature_bonus = 0.0
        for sig in profile.signature_phrases:
            if sig.lower() in line_lower:
                signature_bonus = 0.15
        
        # Calculate overall voice consistency
        dimension_scores = [sarcasm_score, cynicism_score, warmth_score,
                          formality_score, verbosity_score]
        avg_dimension = sum(dimension_scores) / len(dimension_scores)
        
        # Weight: dimensions 70%, subtext 20%, on-the-nose penalty 10%
        voice_consistency = avg_dimension * 0.7 + subtext_score * 0.2 + signature_bonus
        if on_the_nose:
            voice_consistency *= 0.7  # 30% penalty
        
        voice_consistency = max(0.0, min(1.0, voice_consistency))
        
        # Generate rewrite if score is low
        rewrite = None
        if voice_consistency < 0.6 and issues:
            rewrite = self._suggest_rewrite(line, profile, issues[0])
        
        return DialogueScore(
            line=line,
            speaker=speaker_id,
            voice_consistency=voice_consistency,
            subtext_score=subtext_score,
            on_the_nose=on_the_nose,
            formality_match=formality_score,
            verbosity_match=verbosity_score,
            warmth_match=warmth_score,
            cynicism_match=cynicism_score,
            sarcasm_match=sarcasm_score,
            issues=issues,
            suggestions=suggestions,
            rewrite=rewrite,
        )
    
    def _score_sarcasm(self, line_lower: str, profile: VoiceProfile) -> float:
        """Score how well line matches expected sarcasm level."""
        sarcasm_markers = sum(1 for m in self.SARCASM_MARKERS if m in line_lower)
        has_sarcasm = sarcasm_markers > 0
        
        if profile.sarcasm > 70:
            # High sarcasm expected — reward sarcasm markers, penalize absence
            if has_sarcasm:
                return 0.8 + min(0.2, sarcasm_markers * 0.05)
            else:
                return 0.4  # Too earnest for a sarcastic character
        elif profile.sarcasm < 30:
            # Low sarcasm expected — penalize sarcasm markers
            if has_sarcasm:
                return 0.3
            else:
                return 0.9
        else:
            # Medium sarcasm — neutral
            return 0.7
    
    def _score_cynicism(self, line_lower: str, profile: VoiceProfile) -> float:
        """Score how well line matches expected cynicism level."""
        cynicism_markers = sum(1 for m in self.CYNICISM_MARKERS if m in line_lower)
        has_cynicism = cynicism_markers > 0
        
        if profile.cynicism > 70:
            if has_cynicism:
                return 0.8 + min(0.2, cynicism_markers * 0.05)
            else:
                return 0.4
        elif profile.cynicism < 30:
            if has_cynicism:
                return 0.3
            else:
                return 0.9
        else:
            return 0.7
    
    def _score_warmth(self, line_lower: str, profile: VoiceProfile) -> float:
        """Score how well line matches expected warmth level."""
        warmth_markers = sum(1 for m in self.WARMTH_MARKERS if m in line_lower)
        has_warmth = warmth_markers > 0
        
        if profile.warmth > 70:
            if has_warmth:
                return 0.8 + min(0.2, warmth_markers * 0.05)
            else:
                return 0.5
        elif profile.warmth < 30:
            if has_warmth:
                return 0.3
            else:
                return 0.9
        else:
            return 0.7
    
    def _score_formality(self, line_lower: str, profile: VoiceProfile) -> float:
        """Score how well line matches expected formality level."""
        formal_count = sum(1 for m in self.FORMAL_MARKERS if m in line_lower)
        informal_count = sum(1 for m in self.INFORMAL_MARKERS if m in line_lower)
        
        if profile.formality > 70:
            # High formality expected
            if formal_count > 0 and informal_count == 0:
                return 0.9
            elif informal_count > 0:
                return 0.3
            else:
                return 0.7
        elif profile.formality < 30:
            # Low formality expected
            if informal_count > 0 and formal_count == 0:
                return 0.9
            elif formal_count > 0:
                return 0.3
            else:
                return 0.7
        else:
            return 0.7
    
    def _score_verbosity(self, line: str, profile: VoiceProfile) -> float:
        """Score how well line length matches expected verbosity."""
        word_count = len(line.split())
        
        if profile.verbosity > 70:
            expected = 15  # High verbosity = longer sentences
        elif profile.verbosity < 30:
            expected = 5   # Low verbosity = shorter sentences
        else:
            expected = 10
        
        # Score based on deviation from expected
        deviation = abs(word_count - expected) / expected
        score = max(0.0, 1.0 - deviation * 0.5)
        return score
    
    def _analyze_subtext(self, line: str) -> float:
        """Score how much subtext is present (0.0 = direct, 1.0 = highly implied)."""
        line_lower = line.lower()
        
        # Direct emotional statements = low subtext
        direct_patterns = [
            r"i (feel|am|'m) (sad|angry|happy|scared|worried|excited|disappointed|lonely|jealous)",
            r"i (love|hate|like|dislike) you",
            r"the (point|lesson|moral) is",
            r"what i'm (trying to say|saying) is",
        ]
        
        for pattern in direct_patterns:
            if re.search(pattern, line_lower):
                return 0.2
        
        # Questions and implications = higher subtext
        subtext_indicators = [
            line.endswith("?"),
            "maybe" in line_lower,
            "perhaps" in line_lower,
            "suppose" in line_lower,
            "wonder" in line_lower,
            "if" in line_lower and "then" not in line_lower,
        ]
        
        subtext_score = 0.5 + sum(subtext_indicators) * 0.1
        return min(1.0, subtext_score)
    
    def _detect_on_the_nose(self, line_lower: str) -> bool:
        """Detect if a line states emotions directly (on-the-nose)."""
        for pattern in self.ON_THE_NOSE_PATTERNS:
            if re.search(pattern, line_lower):
                return True
        
        # Check for direct emotional statements
        for statement in self.EMOTION_DIRECT_STATEMENTS:
            if statement in line_lower:
                # But allow "I love you" without explanation (that's subtext)
                if statement == "i love you":
                    # Only flag if followed by "because" or explanation
                    idx = line_lower.find(statement)
                    rest = line_lower[idx + len(statement):]
                    if "because" in rest or "and" in rest:
                        return True
                    return False
                return True
        
        return False
    
    def _suggest_rewrite(self, line: str, profile: VoiceProfile, issue: str) -> str:
        """Suggest a rewrite for a low-scoring line."""
        line_lower = line.lower()
        
        # Issue: on-the-nose emotional statement
        if "on-the-nose" in issue.lower():
            if "i love you" in line_lower:
                return f"[Action: {profile.character_name} reaches out, hesitates, then takes their hand.]"
            elif "i'm sorry" in line_lower:
                return f"[Action: {profile.character_name} looks away, voice dropping.] 'I shouldn't have...'"
            elif "i'm angry" in line_lower or "i'm mad" in line_lower:
                return f"[Action: {profile.character_name} slams their fist on the table.] 'You knew. You knew and you didn't tell me.'"
            elif "i'm scared" in line_lower or "i'm afraid" in line_lower:
                return f"[Action: {profile.character_name} glances at the door, voice barely audible.] 'What if they come back?'"
            else:
                return f"[Action: Show {profile.character_name}'s emotion through physical reaction, not words.]"
        
        # Issue: forbidden phrase
        if "forbidden phrase" in issue.lower():
            if profile.sarcasm > 70:
                return f"[Suggested rewrite in sarcastic voice] 'Oh, absolutely. Because that approach has worked SO well before.'"
            elif profile.cynicism > 70:
                return f"[Suggested rewrite in cynical voice] 'Sure. And I'm sure everyone will do the right thing. Like they always do.'"
            elif profile.warmth > 70:
                return f"[Suggested rewrite in warm voice] 'I understand. Let's figure this out together.'"
            else:
                return f"[Suggested rewrite] Consider what {profile.character_name} would actually say given their personality."
        
        # Issue: wrong formality
        if "formal" in issue.lower() or "informal" in issue.lower():
            if profile.formality > 70:
                return f"[More formal] 'I must confess, your approach leaves something to be desired.'"
            elif profile.formality < 30:
                return f"[More casual] 'Yeah, no. That's not gonna work.'"
        
        # Default
        return f"[Review line against voice profile: sarcasm={profile.sarcasm:.0f}, cynicism={profile.cynicism:.0f}, warmth={profile.warmth:.0f}]"
    
    # ========================================================================
    # Screenplay Analysis
    # ========================================================================
    
    def analyze_screenplay(self, scenes: list[Any], 
                           profiles: Optional[dict[str, VoiceProfile]] = None) -> ScreenplayDialogueAnalysis:
        """Analyze all dialogue in a screenplay."""
        if profiles:
            self.voice_profiles.update(profiles)
        
        analysis = ScreenplayDialogueAnalysis()
        all_scores = []
        speakers = set()
        
        for scene in scenes:
            for dialogue_entry in scene.dialogue:
                if not isinstance(dialogue_entry, dict):
                    continue
                
                speaker = dialogue_entry.get("speaker", "Unknown")
                line = dialogue_entry.get("line", "")
                
                if not line:
                    continue
                
                speakers.add(speaker)
                score = self.score_dialogue(line, speaker)
                
                analysis.total_lines += 1
                if speaker not in analysis.lines_by_speaker:
                    analysis.lines_by_speaker[speaker] = []
                analysis.lines_by_speaker[speaker].append(score)
                all_scores.append(score)
                
                if score.voice_consistency < 0.5:
                    analysis.voice_violations.append(score)
                if score.on_the_nose:
                    analysis.on_the_nose_lines.append(score)
                if score.subtext_score < 0.4:
                    analysis.low_subtext_lines.append(score)
        
        analysis.total_speakers = len(speakers)
        if all_scores:
            analysis.overall_voice_consistency = sum(s.voice_consistency for s in all_scores) / len(all_scores)
            analysis.overall_subtext_score = sum(s.subtext_score for s in all_scores) / len(all_scores)
        
        return analysis
    
    # ========================================================================
    # Skill Loading
    # ========================================================================
    
    def load_skills(self, vault_path: str = "studio") -> dict[str, str]:
        """Load craft knowledge from skill files."""
        skills_dir = Path(vault_path) / "skills"
        skills = {}
        
        if not skills_dir.exists():
            return skills
        
        for skill_file in skills_dir.glob("*.md"):
            skills[skill_file.stem] = skill_file.read_text(encoding="utf-8")
        
        return skills
    
    def get_voice_guidance(self, character_id: str) -> str:
        """Get voice guidance text for a character."""
        profile = self.voice_profiles.get(character_id)
        if not profile:
            return ""
        
        guidance = f"""## Voice Profile: {profile.character_name}

**Archetype:** {profile.archetype}
**Overall:** {profile.get_description()}

### Voice Dimensions (0-100)
- **Sarcasm:** {profile.sarcasm:.0f}
- **Cynicism:** {profile.cynicism:.0f}
- **Warmth:** {profile.warmth:.0f}
- **Formality:** {profile.formality:.0f}
- **Verbosity:** {profile.verbosity:.0f}
- **Subtext:** {profile.subtext:.0f}

### Writing Rules
{chr(10).join(f"- {phrase}" for phrase in profile.signature_phrases)}

### NEVER Write
{chr(10).join(f"- '{phrase}'" for phrase in profile.forbidden_phrases)}
"""
        return guidance


# =============================================================================
# Dialogue Critic (for CriticSwarm integration)
# =============================================================================

class DialogueCritic:
    """Critic agent that uses Language Engine to score dialogue quality."""
    
    def __init__(self, language_engine: Optional[LanguageEngine] = None):
        self.engine = language_engine or LanguageEngine()
    
    def evaluate(self, prototype: Any, concept: Any) -> Any:
        """Evaluate dialogue in a prototype. Returns PatternScore-compatible dict."""
        from system4.pattern_recognition import PatternScore
        
        # Generate voice profiles from concept characters
        profiles = {}
        for char in [concept.protagonist, concept.deuteragonist, concept.antagonist]:
            if char:
                profile = self.engine.create_voice_profile(
                    char.name.lower().replace(" ", "_"),
                    char.name,
                    char.archetype,
                    char.starting_state,
                    char.ending_state
                )
                profiles[char.name] = profile
        
        # Analyze dialogue
        analysis = self.engine.analyze_screenplay(prototype.scenes, profiles)
        
        issues = []
        strengths = []
        suggestions = []
        
        # Score based on analysis
        score = 7.0
        
        if analysis.overall_voice_consistency > 0.7:
            score += 1.5
            strengths.append(f"Strong voice consistency ({analysis.overall_voice_consistency:.0%})")
        elif analysis.overall_voice_consistency > 0.5:
            score += 0.5
            strengths.append("Adequate voice consistency")
        else:
            score -= 1.5
            issues.append(f"Weak voice consistency ({analysis.overall_voice_consistency:.0%})")
            suggestions.append("Review dialogue against character voice profiles")
        
        if analysis.overall_subtext_score > 0.6:
            score += 1.0
            strengths.append("Good use of subtext")
        elif analysis.overall_subtext_score < 0.4:
            score -= 1.0
            issues.append("Dialogue is too on-the-nose")
            suggestions.append("Replace direct emotional statements with actions and implications")
        
        if len(analysis.on_the_nose_lines) == 0:
            score += 0.5
            strengths.append("No on-the-nose dialogue detected")
        else:
            score -= 0.5 * len(analysis.on_the_nose_lines)
            issues.append(f"{len(analysis.on_the_nose_lines)} lines are on-the-nose")
            for bad_line in analysis.on_the_nose_lines[:2]:
                suggestions.append(f"Rewrite: '{bad_line.line[:40]}...'")
        
        if analysis.total_speakers >= 2:
            score += 0.5
            strengths.append("Multiple distinct voices in dialogue")
        
        # Add worst lines as specific issues
        worst = analysis.get_worst_lines(2)
        for w in worst:
            if w.voice_consistency < 0.5:
                issues.append(f"'{w.line[:40]}...' doesn't sound like {w.speaker}")
                if w.rewrite:
                    suggestions.append(f"Try: {w.rewrite[:60]}...")
        
        score = max(0.0, min(10.0, score))
        
        return PatternScore(
            analyzer_name="Dialogue Critic",
            category="dialogue",
            score=score,
            confidence=0.75,
            notes=f"Dialogue score: {score:.1f}/10. {analysis.total_lines} lines across {analysis.total_speakers} speakers. Voice consistency: {analysis.overall_voice_consistency:.0%}. Subtext: {analysis.overall_subtext_score:.0%}.",
            specific_issues=list(set(issues)),
            strengths=list(set(strengths)),
            suggestions=list(set(suggestions)),
        )
