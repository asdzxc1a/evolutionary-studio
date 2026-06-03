"""Director Agent — System 4, Phase 3

The executive function of the Cognitive OS. Reviews production packages
and makes quality decisions: ACCEPT, REJECT, ITERATE, or ESCALATE.

Operates with explicit reasoning: every decision includes REASON, ACTION,
and EVIDENCE. Uses Working Memory to avoid context overflow.

Inspired by:
- Pixar's Brain Trust (peer review with candor)
- Save the Cat's "Board of Directors" (test audience logic)
- McKee's story diagnosis methodology
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import sys
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))


# =============================================================================
# Decision Types
# =============================================================================

class Verdict(Enum):
    """Possible Director decisions."""
    ACCEPT = "accept"
    REJECT = "reject"
    ITERATE = "iterate"
    ESCALATE = "escalate"


@dataclass
class Decision:
    """A structured decision from the Director Agent."""
    verdict: Verdict
    production_id: str
    reason: str
    action: str
    evidence: dict[str, Any] = field(default_factory=dict)
    specific_notes: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0-1.0
    reviewed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_markdown(self) -> str:
        """Convert decision to markdown for the vault."""
        lines = [
            f"# Director Review: {self.production_id}",
            "",
            f"**Verdict:** {self.verdict.value.upper()}",
            f"**Confidence:** {self.confidence:.0%}",
            f"**Reviewed At:** {self.reviewed_at}",
            "",
            "## Reason",
            self.reason,
            "",
            "## Action",
            self.action,
            "",
            "## Evidence",
        ]
        
        for key, value in self.evidence.items():
            if isinstance(value, (int, float)):
                lines.append(f"- **{key}:** {value:.1f}")
            else:
                lines.append(f"- **{key}:** {value}")
        
        if self.specific_notes:
            lines.extend(["", "## Specific Notes"])
            for note in self.specific_notes:
                lines.append(f"- {note}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for API serialization."""
        return {
            "verdict": self.verdict.value,
            "production_id": self.production_id,
            "reason": self.reason,
            "action": self.action,
            "evidence": self.evidence,
            "specific_notes": self.specific_notes,
            "confidence": self.confidence,
            "reviewed_at": self.reviewed_at,
        }


# =============================================================================
# Quality Thresholds
# =============================================================================

@dataclass
class QualityThresholds:
    """Thresholds for automatic decisions."""
    # Minimum scores for ACCEPT
    min_structure_score: float = 7.0
    min_character_score: float = 6.5
    min_emotion_score: float = 7.0
    min_pacing_score: float = 6.5
    min_theme_score: float = 6.0
    min_dialogue_score: float = 6.5
    min_combined_score: float = 7.0
    
    # Maximum issues for ACCEPT
    max_critical_issues: int = 2
    max_voice_violations: int = 3
    max_on_the_nose_lines: int = 2
    
    # Auto-reject thresholds
    reject_if_combined_below: float = 4.0
    reject_if_structure_below: float = 3.0
    reject_if_theme_below: float = 3.0
    
    # Escalate thresholds (needs human judgment)
    escalate_if_confidence_below: float = 0.5
    escalate_if_mixed_signals: bool = True  # High scores but many issues


# =============================================================================
# Working Memory
# =============================================================================

@dataclass
class WorkingMemoryContext:
    """Context loaded into working memory for review."""
    concept: dict[str, Any] = field(default_factory=dict)
    scenes: list[dict[str, Any]] = field(default_factory=list)
    characters: list[dict[str, Any]] = field(default_factory=list)
    evaluations: list[dict[str, Any]] = field(default_factory=list)
    focus_area: str = ""  # "structure", "character", "dialogue", etc.


class WorkingMemory:
    """Manages limited context loading to prevent overflow.
    
    Mimics human working memory: can only hold ~5 scenes + 3 characters
    + 1 focus area at a time. Everything else is swapped to Obsidian.
    """
    
    def __init__(self, max_scenes: int = 5, max_characters: int = 3):
        self.max_scenes = max_scenes
        self.max_characters = max_characters
        self.current_context: Optional[WorkingMemoryContext] = None
    
    def load_package(self, package: dict[str, Any], 
                     focus_area: str = "") -> WorkingMemoryContext:
        """Load package into working memory, respecting limits."""
        context = WorkingMemoryContext(focus_area=focus_area)
        
        # Load concept (always fits)
        context.concept = package.get("concept", {})
        
        # Load characters (limit to max)
        all_chars = package.get("characters", [])
        context.characters = all_chars[:self.max_characters]
        if len(all_chars) > self.max_characters:
            context.characters.append({
                "name": f"... and {len(all_chars) - self.max_characters} more",
                "note": "Additional characters not loaded into working memory"
            })
        
        # Load scenes (limit to max, prioritize by relevance)
        all_scenes = package.get("scenes", [])
        if focus_area == "structure":
            # Load opening, midpoint, climax
            key_scenes = self._select_key_scenes(all_scenes, [0, len(all_scenes)//2, -1])
        elif focus_area == "dialogue":
            # Load scenes with most dialogue
            key_scenes = sorted(all_scenes, 
                              key=lambda s: len(s.get("dialogue", [])),
                              reverse=True)[:self.max_scenes]
        else:
            # Load first N scenes
            key_scenes = all_scenes[:self.max_scenes]
        
        context.scenes = key_scenes
        
        # Load evaluations
        context.evaluations = package.get("reviews", {}).get("scores", [])
        
        self.current_context = context
        return context
    
    def _select_key_scenes(self, scenes: list[dict], indices: list[int]) -> list[dict]:
        """Select scenes by index, handling negative indices."""
        result = []
        for idx in indices:
            if idx < 0:
                idx = len(scenes) + idx
            if 0 <= idx < len(scenes):
                result.append(scenes[idx])
        return result
    
    def get_focused_context(self) -> str:
        """Get a summary of what's currently in working memory."""
        if not self.current_context:
            return "No context loaded"
        
        ctx = self.current_context
        lines = [
            f"Focus: {ctx.focus_area or 'general'}",
            f"Concept: {ctx.concept.get('title', 'Unknown')}",
            f"Characters loaded: {len(ctx.characters)}",
            f"Scenes loaded: {len(ctx.scenes)}",
            f"Evaluations: {len(ctx.evaluations)} scores",
        ]
        return "\n".join(lines)


# =============================================================================
# Director Agent
# =============================================================================

class DirectorAgent:
    """The executive function of the studio.
    
    Reviews production packages and makes quality decisions.
    Uses Working Memory to avoid context overflow.
    Applies structured reasoning to every decision.
    """
    
    def __init__(self, thresholds: Optional[QualityThresholds] = None,
                 working_memory: Optional[WorkingMemory] = None):
        self.thresholds = thresholds or QualityThresholds()
        self.memory = working_memory or WorkingMemory()
        self.decision_history: list[Decision] = []
    
    def review_production(self, package: dict[str, Any], 
                          production_id: str) -> Decision:
        """Review a complete production package and render a verdict.
        
        This is the main entry point. The Director:
        1. Loads package into working memory
        2. Evaluates each dimension (structure, character, dialogue, etc.)
        3. Applies decision protocol
        4. Returns structured Decision
        """
        # Load into working memory
        context = self.memory.load_package(package)
        
        # Gather evidence from all System 4 modules
        evidence = self._gather_evidence(package)
        
        # Evaluate each dimension
        dimension_scores = self._evaluate_dimensions(evidence)
        
        # Apply decision protocol
        decision = self._apply_decision_protocol(
            production_id=production_id,
            dimension_scores=dimension_scores,
            evidence=evidence,
            context=context
        )
        
        self.decision_history.append(decision)
        return decision
    
    def _gather_evidence(self, package: dict[str, Any]) -> dict[str, Any]:
        """Collect all available evidence from the package."""
        evidence = {}
        
        # Concept quality
        concept = package.get("concept", {})
        evidence["concept_title"] = concept.get("title", "Unknown")
        evidence["has_theme"] = bool(concept.get("theme"))
        evidence["has_social_metaphor"] = bool(concept.get("social_metaphor"))
        evidence["character_count"] = len(package.get("characters", []))
        
        # Evaluation scores (from Pattern Recognition + Language Engine)
        reviews = package.get("reviews", {})
        scores = reviews.get("scores", {})
        
        for category, score_data in scores.items():
            if isinstance(score_data, dict) and "score" in score_data:
                evidence[f"{category}_score"] = score_data["score"]
                evidence[f"{category}_issues"] = len(score_data.get("issues", []))
                evidence[f"{category}_strengths"] = len(score_data.get("strengths", []))
        
        # Combined score
        if "combined_score" in reviews:
            evidence["combined_score"] = reviews["combined_score"]
        
        # Scene metrics
        scenes = package.get("scenes", [])
        evidence["scene_count"] = len(scenes)
        evidence["has_hook"] = any("hook" in str(s).lower() for s in scenes)
        evidence["has_climax"] = any("climax" in str(s).lower() for s in scenes)
        
        # Dialogue metrics (from Language Engine)
        dialogue_lines = 0
        speakers = set()
        for scene in scenes:
            for line in scene.get("dialogue", []):
                dialogue_lines += 1
                if isinstance(line, dict):
                    speakers.add(line.get("speaker", "Unknown"))
        
        evidence["dialogue_lines"] = dialogue_lines
        evidence["dialogue_speakers"] = len(speakers)
        
        return evidence
    
    def _evaluate_dimensions(self, evidence: dict[str, Any]) -> dict[str, float]:
        """Evaluate each creative dimension and return scores."""
        dimensions = {}
        
        # Structure dimension
        structure_score = evidence.get("structure_score", 5.0)
        if evidence.get("has_hook") and evidence.get("has_climax"):
            structure_score = max(structure_score, 6.0)
        dimensions["structure"] = structure_score
        
        # Character dimension
        char_score = evidence.get("character_score", 5.0)
        if evidence.get("character_count", 0) >= 3:
            char_score = max(char_score, 6.0)
        dimensions["character"] = char_score
        
        # Emotion dimension
        dimensions["emotion"] = evidence.get("emotion_score", 5.0)
        
        # Pacing dimension
        dimensions["pacing"] = evidence.get("pacing_score", 5.0)
        
        # Theme dimension
        theme_score = evidence.get("theme_score", 5.0)
        if evidence.get("has_theme") and evidence.get("has_social_metaphor"):
            theme_score = max(theme_score, 5.5)
        dimensions["theme"] = theme_score
        
        # Dialogue dimension
        dialogue_score = evidence.get("dialogue_score", 5.0)
        if evidence.get("dialogue_speakers", 0) >= 2:
            dialogue_score = max(dialogue_score, 5.5)
        dimensions["dialogue"] = dialogue_score
        
        # Overall
        dimensions["combined"] = evidence.get("combined_score", 
                                             sum(dimensions.values()) / len(dimensions))
        
        return dimensions
    
    def _apply_decision_protocol(self, production_id: str,
                                  dimension_scores: dict[str, float],
                                  evidence: dict[str, Any],
                                  context: WorkingMemoryContext) -> Decision:
        """Apply the decision protocol to render a verdict.
        
        Protocol:
        1. Check auto-reject conditions (fundamental flaws)
        2. Check auto-accept conditions (meets all thresholds)
        3. Check iterate conditions (promising but needs work)
        4. Default to escalate (needs human judgment)
        """
        t = self.thresholds
        scores = dimension_scores
        
        # Count failures
        failures = []
        if scores["structure"] < t.min_structure_score:
            failures.append(f"Structure: {scores['structure']:.1f} < {t.min_structure_score}")
        if scores["character"] < t.min_character_score:
            failures.append(f"Character: {scores['character']:.1f} < {t.min_character_score}")
        if scores["emotion"] < t.min_emotion_score:
            failures.append(f"Emotion: {scores['emotion']:.1f} < {t.min_emotion_score}")
        if scores["pacing"] < t.min_pacing_score:
            failures.append(f"Pacing: {scores['pacing']:.1f} < {t.min_pacing_score}")
        if scores["theme"] < t.min_theme_score:
            failures.append(f"Theme: {scores['theme']:.1f} < {t.min_theme_score}")
        if scores["dialogue"] < t.min_dialogue_score:
            failures.append(f"Dialogue: {scores['dialogue']:.1f} < {t.min_dialogue_score}")
        
        critical_issues = sum(
            evidence.get(f"{cat}_issues", 0) 
            for cat in ["structure", "theme", "dialogue"]
        )
        
        # === AUTO-REJECT CHECK ===
        if scores["combined"] < t.reject_if_combined_below:
            return Decision(
                verdict=Verdict.REJECT,
                production_id=production_id,
                reason=f"Combined score {scores['combined']:.1f} is below auto-reject threshold ({t.reject_if_combined_below}). Fundamental quality issues detected.",
                action="Discard this production. Consider running evolution with different constraints or more rounds.",
                evidence=scores,
                specific_notes=failures,
                confidence=0.9,
            )
        
        if scores["structure"] < t.reject_if_structure_below:
            return Decision(
                verdict=Verdict.REJECT,
                production_id=production_id,
                reason=f"Structure score {scores['structure']:.1f} indicates fundamental structural problems.",
                action="Reject and re-run evolution. Focus on 3-act structure and midpoint placement.",
                evidence=scores,
                specific_notes=failures,
                confidence=0.85,
            )
        
        if scores["theme"] < t.reject_if_theme_below:
            return Decision(
                verdict=Verdict.REJECT,
                production_id=production_id,
                reason=f"Theme score {scores['theme']:.1f} indicates the story lacks thematic coherence.",
                action="Reject and refine concept. Ensure theme is present across all acts and social metaphor is specific.",
                evidence=scores,
                specific_notes=failures,
                confidence=0.85,
            )
        
        # === AUTO-ACCEPT CHECK ===
        if (len(failures) == 0 and 
            scores["combined"] >= t.min_combined_score and
            critical_issues <= t.max_critical_issues):
            return Decision(
                verdict=Verdict.ACCEPT,
                production_id=production_id,
                reason=f"All quality thresholds met. Combined score {scores['combined']:.1f} exceeds minimum {t.min_combined_score}. No critical issues detected.",
                action="Approve production for final delivery. Package is ready for human review and potential generation.",
                evidence=scores,
                specific_notes=[
                    f"Structure: {scores['structure']:.1f} — solid",
                    f"Character: {scores['character']:.1f} — well-developed",
                    f"Dialogue: {scores['dialogue']:.1f} — distinct voices",
                ],
                confidence=0.85,
            )
        
        # === ITERATE CHECK ===
        # Promising but needs specific improvements
        if scores["combined"] >= t.min_combined_score - 1.0 and len(failures) <= 3:
            notes = failures.copy()
            
            # Check if too many critical issues despite good scores
            if critical_issues > t.max_critical_issues:
                notes.append(f"Too many critical issues ({critical_issues} > {t.max_critical_issues}). Review structure, theme, and dialogue for specific problems.")
            
            # Add specific improvement suggestions for weak dimensions
            if scores["theme"] < t.min_theme_score:
                notes.append("ITERATION: Add theme to scene descriptions. Show theme through action, not just dialogue.")
            if scores["dialogue"] < t.min_dialogue_score:
                notes.append("ITERATION: Strengthen character voices. Review voice profiles and ensure each line matches.")
            if scores["structure"] < t.min_structure_score:
                notes.append("ITERATION: Clarify midpoint turn. Ensure it's a false victory or false defeat.")
            if scores["character"] < t.min_character_score:
                notes.append("ITERATION: Deepen character arcs. Ensure each main character has a core wound.")
            
            issue_desc = f"{len(failures)} dimension(s) below threshold" if failures else f"{critical_issues} critical issues to resolve"
            return Decision(
                verdict=Verdict.ITERATE,
                production_id=production_id,
                reason=f"Combined score {scores['combined']:.1f} is promising but {issue_desc}.",
                action="Send specific notes back to production swarm for targeted revision.",
                evidence=scores,
                specific_notes=notes,
                confidence=0.7,
            )
        
        # === DEFAULT: ESCALATE ===
        # Mixed signals — high in some areas, low in others, needs human judgment
        return Decision(
            verdict=Verdict.ESCALATE,
            production_id=production_id,
            reason=f"Mixed quality signals. Combined score {scores['combined']:.1f} with {len(failures)} failing dimensions. Auto-decision confidence is low.",
            action="Flag for human creative director review. Provide full evidence package for judgment.",
            evidence=scores,
            specific_notes=failures + [
                "Human judgment needed: some dimensions are strong while others are weak.",
                f"Strongest: {max(scores, key=scores.get)} ({scores[max(scores, key=scores.get)]:.1f})",
                f"Weakest: {min(scores, key=scores.get)} ({scores[min(scores, key=scores.get)]:.1f})",
            ],
            confidence=0.5,
        )
    
    def review_with_focus(self, package: dict[str, Any], 
                          production_id: str,
                          focus_area: str) -> Decision:
        """Review with a specific focus area loaded into working memory.
        
        Useful for deep-dives: "Review just the dialogue" or 
        "Review just the structure."
        """
        context = self.memory.load_package(package, focus_area=focus_area)
        evidence = self._gather_evidence(package)
        
        # Override: only evaluate the focus area
        dimension_scores = self._evaluate_dimensions(evidence)
        focus_score = dimension_scores.get(focus_area, 5.0)
        
        if focus_score >= 7.5:
            verdict = Verdict.ACCEPT
            reason = f"{focus_area.title()} is strong ({focus_score:.1f}). No issues found in focused review."
            action = f"Approve {focus_area} dimension. Continue with full review or proceed."
            confidence = 0.8
        elif focus_score >= 5.0:
            verdict = Verdict.ITERATE
            reason = f"{focus_area.title()} is adequate ({focus_score:.1f}) but could be improved."
            action = f"Refine {focus_area} based on specific notes."
            confidence = 0.6
        else:
            verdict = Verdict.REJECT
            reason = f"{focus_area.title()} is weak ({focus_score:.1f}). Needs significant rework."
            action = f"Rebuild {focus_area} from scratch with clearer direction."
            confidence = 0.75
        
        decision = Decision(
            verdict=verdict,
            production_id=production_id,
            reason=reason,
            action=action,
            evidence={focus_area: focus_score},
            confidence=confidence,
        )
        
        self.decision_history.append(decision)
        return decision
    
    def get_decision_stats(self) -> dict[str, Any]:
        """Get statistics on all decisions made."""
        if not self.decision_history:
            return {"total": 0}
        
        verdicts = {}
        for d in self.decision_history:
            v = d.verdict.value
            verdicts[v] = verdicts.get(v, 0) + 1
        
        avg_confidence = sum(d.confidence for d in self.decision_history) / len(self.decision_history)
        
        return {
            "total": len(self.decision_history),
            "by_verdict": verdicts,
            "average_confidence": round(avg_confidence, 2),
            "accept_rate": verdicts.get("accept", 0) / len(self.decision_history),
        }
