"""System 4 Phase 5: Emotional Model

Simulates audience emotional valence beat-by-beat across a screenplay.
Validates recovery timing, climax resolution, and emotional arc patterns.

Rules:
- After a -0.8 beat, need 90s recovery
- All-is-lost moment should occur at ~75% of runtime
- Climax should resolve to +0.8 valence
- Emotional range should span at least 1.5 (from negative to positive)
- No more than 2 consecutive negative beats without recovery
"""

from __future__ import annotations

import sys
import re
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if TYPE_CHECKING:
    from system3.evolution_engine import Concept, Prototype


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class EmotionalBeat:
    """A single emotional beat in the story."""
    scene_number: int
    position: float  # 0.0 to 1.0 (percent through story)
    duration: float  # seconds
    valence: float   # -1.0 (negative) to +1.0 (positive)
    arousal: float   # 0.0 (calm) to 1.0 (excited)
    label: str = ""  # e.g., "hook", "midpoint", "all_is_lost", "climax"
    cause: str = ""  # What caused this emotional state


@dataclass
class EmotionalArc:
    """A complete emotional arc pattern."""
    name: str
    description: str
    beats: list[tuple[float, float]]  # [(position, valence), ...]


@dataclass
class EmotionalAnalysis:
    """Results of emotional model analysis."""
    beats: list[EmotionalBeat]
    overall_arc: str  # "Rags to Riches", "Tragedy", "Comedy", etc.
    valence_range: float  # max - min
    recovery_issues: list[dict]
    climax_score: float
    all_is_lost_position: Optional[float]
    score: float  # 0.0 to 10.0
    notes: str
    specific_issues: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)


# =============================================================================
# Arc Patterns
# =============================================================================

class ArcLibrary:
    """Library of ideal emotional arc patterns."""
    
    PATTERNS = {
        "rags_to_riches": EmotionalArc(
            name="Rags to Riches",
            description="Start negative, rise steadily, dip at all-is-lost, strong positive climax",
            beats=[(0.0, -0.6), (0.25, -0.2), (0.5, 0.3), (0.75, -0.7), (1.0, 0.9)],
        ),
        "comedy": EmotionalArc(
            name="Comedy",
            description="Mostly positive with small dips, strong positive resolution",
            beats=[(0.0, 0.2), (0.25, 0.5), (0.5, -0.2), (0.75, 0.4), (1.0, 0.9)],
        ),
        "tragedy": EmotionalArc(
            name="Tragedy",
            description="Start positive or neutral, decline steadily, negative climax",
            beats=[(0.0, 0.3), (0.25, 0.1), (0.5, -0.3), (0.75, -0.6), (1.0, -0.9)],
        ),
        "man_in_hole": EmotionalArc(
            name="Man in a Hole",
            description="Start positive, fall deep, climb back out",
            beats=[(0.0, 0.4), (0.25, -0.5), (0.5, -0.8), (0.75, -0.2), (1.0, 0.7)],
        ),
        "icarus": EmotionalArc(
            name="Icarus",
            description="Rise high, then crash",
            beats=[(0.0, -0.2), (0.25, 0.4), (0.5, 0.8), (0.75, 0.3), (1.0, -0.8)],
        ),
    }
    
    @classmethod
    def get_pattern(cls, name: str) -> Optional[EmotionalArc]:
        return cls.PATTERNS.get(name.lower().replace(" ", "_"))
    
    @classmethod
    def match_arc(cls, beats: list[EmotionalBeat]) -> tuple[str, float]:
        """Match beats against all patterns and return best match."""
        if not beats:
            return "unknown", 0.0
        
        # Sample actual beats at pattern positions
        best_match = ("unknown", 0.0)
        
        for pattern_name, pattern in cls.PATTERNS.items():
            score = cls._pattern_match_score(beats, pattern)
            if score > best_match[1]:
                best_match = (pattern.name, score)
        
        return best_match
    
    @classmethod
    def _pattern_match_score(cls, beats: list[EmotionalBeat], pattern: EmotionalArc) -> float:
        """Calculate how well beats match a pattern (0.0-1.0)."""
        if not beats:
            return 0.0
        
        total_error = 0.0
        for pos, target_valence in pattern.beats:
            # Find closest beat to this position
            closest = min(beats, key=lambda b: abs(b.position - pos))
            error = abs(closest.valence - target_valence)
            total_error += error
        
        # Convert to similarity (lower error = higher score)
        avg_error = total_error / len(pattern.beats)
        similarity = max(0.0, 1.0 - avg_error)
        return similarity


# =============================================================================
# Emotional Simulator
# =============================================================================

class EmotionalSimulator:
    """Simulates audience emotional response to screenplay content."""
    
    # Keyword-based valence indicators
    POSITIVE_INDICATORS = [
        "victory", "triumph", "hope", "love", "joy", "laugh", "reunion",
        "success", "breakthrough", "discover", "friendship", "trust",
        "sacrifice", "redemption", "forgive", "heal", "save", "rescue",
        "celebrate", "win", "free", "peace", "home", "together",
    ]
    
    NEGATIVE_INDICATORS = [
        "death", "die", "kill", "murder", "betray", "loss", "lose",
        "fail", "failure", "trap", "captured", "prison", "alone",
        "abandon", "rejected", "fear", "terrified", "despair", "hopeless",
        "guilty", "ashamed", "broken", "destroy", "defeat", "crash",
        "accident", "injured", "wound", "bleed", "cry", "weep", "scream",
    ]
    
    INTENSITY_BOOSTERS = [
        "extremely", "utterly", "completely", "totally", "absolutely",
        "devastating", "shattering", "crushing", "overwhelming",
    ]
    
    # Scene-type valence baselines
    SCENE_TYPE_VALENCE = {
        "hook": 0.0,        # Neutral/slightly intriguing
        "setup": 0.2,       # Mildly positive (world introduction)
        "inciting": -0.1,   # Slight disruption
        "rising_action": 0.1,
        "midpoint": 0.0,    # Could go either way
        "confrontation": -0.4,
        "all_is_lost": -0.8,
        "climax": 0.6,
        "resolution": 0.8,
        "denouement": 0.5,
    }
    
    def __init__(self):
        self.arc_library = ArcLibrary()
    
    def simulate(self, scenes: list[dict]) -> list[EmotionalBeat]:
        """Generate emotional beats from a list of scenes."""
        if not scenes:
            return []
        
        total_duration = sum(s.get("duration", 120) for s in scenes)
        beats = []
        
        for i, scene in enumerate(scenes):
            position = i / max(len(scenes) - 1, 1)
            duration = scene.get("duration", 120)
            content = scene.get("content", "")
            slugline = scene.get("slugline", "")
            
            # Base valence from scene type detection
            valence = self._detect_scene_valence(content, slugline, position)
            
            # Adjust based on position in story
            valence = self._apply_position_adjustment(valence, position)
            
            # Calculate arousal (energy level)
            arousal = self._calculate_arousal(content, valence)
            
            # Detect label
            label = self._detect_beat_label(position, valence, i, len(scenes))
            
            beats.append(EmotionalBeat(
                scene_number=scene.get("scene_number", i + 1),
                position=position,
                duration=duration,
                valence=round(valence, 2),
                arousal=round(arousal, 2),
                label=label,
                cause=self._extract_cause(content),
            ))
        
        return beats
    
    def _detect_scene_valence(self, content: str, slugline: str, position: float) -> float:
        """Detect emotional valence from scene content."""
        text = (content + " " + slugline).lower()
        
        # Count positive and negative indicators
        pos_count = sum(1 for word in self.POSITIVE_INDICATORS if word in text)
        neg_count = sum(1 for word in self.NEGATIVE_INDICATORS if word in text)
        
        # Check for intensity boosters
        intensity = 1.0
        for booster in self.INTENSITY_BOOSTERS:
            if booster in text:
                intensity = 1.3
                break
        
        # Calculate base valence
        if pos_count + neg_count == 0:
            base_valence = 0.0
        else:
            raw = (pos_count - neg_count) / max(pos_count + neg_count, 1)
            base_valence = raw * 0.6  # Scale to avoid extremes from keywords alone
        
        # Apply intensity
        base_valence *= intensity
        
        # Clamp
        return max(-1.0, min(1.0, base_valence))
    
    def _apply_position_adjustment(self, valence: float, position: float) -> float:
        """Adjust valence based on story position."""
        # All-is-lost zone (65-80%) should tend negative
        if 0.65 <= position <= 0.80:
            valence = min(valence, -0.3)
        
        # Climax zone (85-95%) should tend positive
        if 0.85 <= position <= 0.95:
            valence = max(valence, 0.2)
        
        # Resolution (95%+) should be positive
        if position > 0.95:
            valence = max(valence, 0.5)
        
        return valence
    
    def _calculate_arousal(self, content: str, valence: float) -> float:
        """Calculate arousal (energy) from content."""
        text = content.lower()
        
        # Action words indicate high arousal
        action_words = ["run", "chase", "fight", "escape", "rush", "crash",
                       "explode", "scream", "discover", "confront", "attack"]
        action_count = sum(1 for w in action_words if w in text)
        
        # Dialogue-heavy scenes tend lower arousal
        dialogue_ratio = text.count('"') / max(len(text), 1)
        
        base_arousal = 0.3 + (action_count * 0.1) - (dialogue_ratio * 0.2)
        
        # Extreme valence (positive or negative) increases arousal
        valence_boost = abs(valence) * 0.3
        
        return max(0.0, min(1.0, base_arousal + valence_boost))
    
    def _detect_beat_label(self, position: float, valence: float, index: int, total: int) -> str:
        """Detect which story beat this scene represents."""
        if index == 0:
            return "hook"
        elif position < 0.15:
            return "setup"
        elif 0.65 <= position <= 0.80 and valence < -0.5:
            return "all_is_lost"
        elif position > 0.85 and valence > 0.3:
            return "climax"
        elif position > 0.95:
            return "resolution"
        elif valence < -0.4:
            return "confrontation"
        else:
            return "rising_action"
    
    def _extract_cause(self, content: str) -> str:
        """Extract a short description of what caused the emotion."""
        # Take first sentence or first 60 chars
        first_sentence = content.split(".")[0] if "." in content else content[:60]
        return first_sentence.strip()[:80]


# =============================================================================
# Validators
# =============================================================================

class RecoveryValidator:
    """Validates that negative emotional beats are followed by recovery."""
    
    RECOVERY_WINDOW = 90  # seconds
    MIN_RECOVERY_VALENCE = -0.2  # Must recover to at least this level
    
    def validate(self, beats: list[EmotionalBeat]) -> list[dict]:
        """Find recovery issues in the emotional trajectory."""
        issues = []
        
        for i, beat in enumerate(beats):
            if beat.valence < -0.5:
                # Check if followed by recovery within window
                cumulative_duration = 0
                recovered = False
                
                for j in range(i + 1, len(beats)):
                    cumulative_duration += beats[j].duration
                    if cumulative_duration > self.RECOVERY_WINDOW:
                        break
                    if beats[j].valence >= self.MIN_RECOVERY_VALENCE:
                        recovered = True
                        break
                
                if not recovered:
                    issues.append({
                        "scene": beat.scene_number,
                        "position": beat.position,
                        "valence": beat.valence,
                        "issue": f"Strong negative beat (valence {beat.valence}) at scene {beat.scene_number} not followed by recovery within {self.RECOVERY_WINDOW}s",
                        "suggestion": "Add a hope moment, ally appearance, or small victory within 90 seconds",
                    })
        
        # Check for too many consecutive negative beats
        consecutive_negative = 0
        for beat in beats:
            if beat.valence < -0.2:
                consecutive_negative += 1
                if consecutive_negative > 3:
                    issues.append({
                        "scene": beat.scene_number,
                        "position": beat.position,
                        "issue": f"{consecutive_negative} consecutive negative/emotionally flat scenes",
                        "suggestion": "Insert a positive or neutral beat to give audience breathing room",
                    })
                    consecutive_negative = 0
            else:
                consecutive_negative = 0
        
        return issues


class ClimaxValidator:
    """Validates climax emotional requirements."""
    
    def validate(self, beats: list[EmotionalBeat]) -> dict:
        """Check climax valence and timing."""
        if not beats:
            return {"score": 0, "issues": ["No beats to analyze"]}
        
        issues = []
        strengths = []
        
        # Find climax (highest valence in last 20%)
        climax_zone = [b for b in beats if b.position >= 0.80]
        if not climax_zone:
            return {"score": 5, "issues": ["No scenes in climax zone (80-100%)"]}
        
        climax = max(climax_zone, key=lambda b: b.valence)
        
        # Check climax valence
        if climax.valence < 0.5:
            issues.append(f"Climax valence ({climax.valence}) is too low. Should resolve to +0.5 or higher.")
        else:
            strengths.append(f"Climax resolves positively (valence: {climax.valence})")
        
        # Check all-is-lost timing
        all_is_lost_candidates = [b for b in beats if b.valence < -0.5 and 0.60 <= b.position <= 0.85]
        if not all_is_lost_candidates:
            issues.append("No clear 'all-is-lost' moment detected in 60-85% range")
        else:
            ail = min(all_is_lost_candidates, key=lambda b: b.valence)
            strengths.append(f"All-is-lost moment at {ail.position:.0%} (valence: {ail.valence})")
        
        # Check emotional range
        all_valences = [b.valence for b in beats]
        valence_range = max(all_valences) - min(all_valences)
        
        if valence_range < 1.0:
            issues.append(f"Emotional range ({valence_range:.2f}) is too narrow. Need at least 1.0 (e.g., -0.5 to +0.5)")
        else:
            strengths.append(f"Good emotional range: {valence_range:.2f}")
        
        score = 10.0 - (len(issues) * 2.5)
        score = max(0.0, min(10.0, score))
        
        return {
            "score": round(score, 1),
            "climax_valence": climax.valence,
            "climax_position": climax.position,
            "valence_range": round(valence_range, 2),
            "issues": issues,
            "strengths": strengths,
        }


# =============================================================================
# Main Emotional Model
# =============================================================================

class EmotionalModel:
    """Complete emotional analysis engine."""
    
    def __init__(self):
        self.simulator = EmotionalSimulator()
        self.recovery_validator = RecoveryValidator()
        self.climax_validator = ClimaxValidator()
        self.arc_library = ArcLibrary()
    
    def analyze(self, scenes: list[dict]) -> EmotionalAnalysis:
        """Analyze emotional trajectory of a screenplay.
        
        Args:
            scenes: List of scene dicts with keys: scene_number, content, slugline, duration
        
        Returns:
            EmotionalAnalysis with beats, issues, and scores
        """
        # Generate beats
        beats = self.simulator.simulate(scenes)
        
        if not beats:
            return EmotionalAnalysis(
                beats=[],
                overall_arc="unknown",
                valence_range=0.0,
                recovery_issues=[],
                climax_score=0.0,
                all_is_lost_position=None,
                score=0.0,
                notes="No scenes provided for emotional analysis",
            )
        
        # Match arc pattern
        arc_name, arc_match = self.arc_library.match_arc(beats)
        
        # Validate recovery
        recovery_issues = self.recovery_validator.validate(beats)
        
        # Validate climax
        climax_result = self.climax_validator.validate(beats)
        
        # Calculate score
        score = climax_result["score"]
        
        # Boost for good arc match
        if arc_match > 0.7:
            score += 1.0
        
        # Penalize recovery issues
        score -= len(recovery_issues) * 1.5
        
        score = max(0.0, min(10.0, score))
        
        # Build notes
        notes = f"Emotional arc: {arc_name} ({arc_match:.0%} match). "
        notes += f"Range: {climax_result['valence_range']}. "
        notes += f"Climax valence: {climax_result['climax_valence']}. "
        if recovery_issues:
            notes += f"{len(recovery_issues)} recovery issue(s)."
        
        # Find all-is-lost position
        ail_beats = [b for b in beats if b.label == "all_is_lost"]
        all_is_lost_pos = ail_beats[0].position if ail_beats else None
        
        return EmotionalAnalysis(
            beats=beats,
            overall_arc=arc_name,
            valence_range=climax_result["valence_range"],
            recovery_issues=recovery_issues,
            climax_score=climax_result["score"],
            all_is_lost_position=all_is_lost_pos,
            score=round(score, 1),
            notes=notes,
            specific_issues=climax_result["issues"] + [r["issue"] for r in recovery_issues],
            strengths=climax_result["strengths"],
        )
    
    def analyze_prototype(self, concept, prototype) -> EmotionalAnalysis:
        """Analyze emotional arc from a concept + prototype."""
        scenes = []
        
        # Extract scenes from prototype
        if hasattr(prototype, 'scenes') and prototype.scenes:
            for i, scene in enumerate(prototype.scenes):
                scenes.append({
                    "scene_number": getattr(scene, 'scene_number', i + 1),
                    "content": getattr(scene, 'content', getattr(scene, 'description', '')),
                    "slugline": getattr(scene, 'slugline', ''),
                    "duration": getattr(scene, 'duration', 120),
                })
        
        # Fallback: use scene descriptions if available
        elif hasattr(prototype, 'scene_descriptions') and prototype.scene_descriptions:
            for i, desc in enumerate(prototype.scene_descriptions):
                scenes.append({
                    "scene_number": i + 1,
                    "content": desc,
                    "slugline": "",
                    "duration": 120,
                })
        
        return self.analyze(scenes)


# =============================================================================
# Convenience
# =============================================================================

def analyze_screenplay(scenes: list[dict]) -> EmotionalAnalysis:
    """Quick function to analyze a screenplay's emotional arc."""
    model = EmotionalModel()
    return model.analyze(scenes)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python emotional_model.py <command>")
        print("")
        print("Commands:")
        print("  demo    Run demo analysis on sample scenes")
        print("")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "demo":
        model = EmotionalModel()
        
        # Demo scenes representing a typical animated feature
        demo_scenes = [
            {"scene_number": 1, "content": "A young fox dreams of becoming the first predator police officer. Her parents laugh but support her.", "slugline": "EXT. BUNNYBURROW - DAY", "duration": 120},
            {"scene_number": 2, "content": "She arrives in the big city full of hope. The city is magnificent but overwhelming.", "slugline": "INT. ZOOTOPIA TRAIN - DAY", "duration": 90},
            {"scene_number": 3, "content": "Assigned to parking duty. Her dreams crushed. She sits alone eating a sad lunch.", "slugline": "EXT. STREET - DAY", "duration": 120},
            {"scene_number": 4, "content": "Meets a con-artist fox. He tricks her. She feels humiliated. A chase begins.", "slugline": "INT. ICE CREAM SHOP - DAY", "duration": 180},
            {"scene_number": 5, "content": "The case goes wrong. She loses her only ally. Her career is over. She cries alone.", "slugline": "INT. HER APARTMENT - NIGHT", "duration": 150},
            {"scene_number": 6, "content": "She discovers the conspiracy. Realizes she was wrong about predators. Hope returns.", "slugline": "INT. TRAIN STATION - NIGHT", "duration": 180},
            {"scene_number": 7, "content": "Confronts the villain. A tense chase through the city. She saves the fox.", "slugline": "EXT. NATURAL HISTORY MUSEUM - NIGHT", "duration": 240},
            {"scene_number": 8, "content": "Graduation ceremony. She and the fox are partners. The city is healed. Celebrate.", "slugline": "INT. POLICE ACADEMY - DAY", "duration": 120},
        ]
        
        result = model.analyze(demo_scenes)
        
        print("=" * 60)
        print("EMOTIONAL MODEL DEMO")
        print("=" * 60)
        print(f"\nArc: {result.overall_arc}")
        print(f"Valence Range: {result.valence_range}")
        print(f"Score: {result.score}/10")
        print(f"\nBeats:")
        for b in result.beats:
            emoji = "😊" if b.valence > 0.3 else "😢" if b.valence < -0.3 else "😐"
            print(f"  Scene {b.scene_number:2d} ({b.position:4.0%}) {emoji} valence={b.valence:+.2f} [{b.label}]")
        
        print(f"\nStrengths:")
        for s in result.strengths:
            print(f"  ✓ {s}")
        
        if result.specific_issues:
            print(f"\nIssues:")
            for issue in result.specific_issues:
                print(f"  ⚠ {issue}")
        
        if result.recovery_issues:
            print(f"\nRecovery Issues:")
            for ri in result.recovery_issues:
                print(f"  ⚠ {ri['issue']}")
                print(f"    → {ri['suggestion']}")
