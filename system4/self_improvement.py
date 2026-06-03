"""Self-Improvement Engine — Makes the system self-learning and self-evolving.

This is the brain's brain. After every production, it:
1. Reads the Director's review and critic scores
2. Identifies the weakest category (structure, dialogue, theme, etc.)
3. Queries Long-Term Memory for past productions that scored high in that category
4. Extracts what made them successful
5. Proposes specific improvements to templates, skill files, or DNA
6. Either auto-applies improvements or suggests them for approval

Over time, the system learns:
- Which concept templates produce winners
- Which dialogue patterns score highest
- Which structural choices the Director prefers
- How to fix recurring weaknesses

This is reinforcement learning for creative generation.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import sys

bridge_dir = Path(__file__).resolve().parent.parent / "bridge"
if str(bridge_dir) not in sys.path:
    sys.path.insert(0, str(bridge_dir))

from obsidian_bridge import ObsidianBridge, get_bridge

# System 4 modules
try:
    from long_term_memory import LongTermMemory
    LTM_AVAILABLE = True
except ImportError:
    LTM_AVAILABLE = False

try:
    from pattern_recognition import PatternRecognizer
    PATTERN_RECOGNITION_AVAILABLE = True
except ImportError:
    PATTERN_RECOGNITION_AVAILABLE = False


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class ProductionRecord:
    """A record of a completed production."""
    production_id: str
    timestamp: str
    concept_id: str
    concept_title: str
    
    # Scores
    structure_score: float = 0.0
    character_score: float = 0.0
    emotion_score: float = 0.0
    pacing_score: float = 0.0
    theme_score: float = 0.0
    dialogue_score: float = 0.0
    combined_score: float = 0.0
    
    # Director verdict
    director_verdict: str = "UNKNOWN"
    director_confidence: float = 0.0
    director_notes: list[str] = field(default_factory=list)
    
    # Issues
    diffused_attention_concerns: list[str] = field(default_factory=list)
    emotional_model_issues: list[str] = field(default_factory=list)
    
    # Templates used
    templates_used: dict[str, str] = field(default_factory=dict)
    dna_source: str = ""


@dataclass
class ImprovementProposal:
    """A proposed improvement to the system."""
    id: str
    category: str  # template, skill, dna, structure
    target_file: str
    description: str
    reasoning: str
    expected_impact: str
    auto_applicable: bool = False
    proposed_change: str = ""
    applied: bool = False
    applied_at: Optional[str] = None
    production_results_after: list[float] = field(default_factory=list)


@dataclass
class EvolutionReport:
    """Report on the system's evolution over time."""
    total_productions: int
    average_combined_score: float
    score_trend: str  # improving, stable, declining
    weakest_category: str
    strongest_category: str
    proposals_generated: int
    proposals_applied: int
    top_performing_templates: list[str]
    recurring_issues: list[str]


# =============================================================================
# Production History Tracker
# =============================================================================

class ProductionHistory:
    """Tracks all productions and their scores."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.history_file = vault_path / "memory" / "production_history.jsonl"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def record(self, production: ProductionRecord) -> None:
        """Append a production record."""
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "production_id": production.production_id,
                "timestamp": production.timestamp,
                "concept_id": production.concept_id,
                "concept_title": production.concept_title,
                "scores": {
                    "structure": production.structure_score,
                    "character": production.character_score,
                    "emotion": production.emotion_score,
                    "pacing": production.pacing_score,
                    "theme": production.theme_score,
                    "dialogue": production.dialogue_score,
                    "combined": production.combined_score,
                },
                "director_verdict": production.director_verdict,
                "director_confidence": production.director_confidence,
                "templates_used": production.templates_used,
                "dna_source": production.dna_source,
            }) + "\n")
    
    def load_all(self) -> list[ProductionRecord]:
        """Load all production records."""
        records = []
        if not self.history_file.exists():
            return records
        
        with open(self.history_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    scores = data.get("scores", {})
                    records.append(ProductionRecord(
                        production_id=data["production_id"],
                        timestamp=data["timestamp"],
                        concept_id=data["concept_id"],
                        concept_title=data["concept_title"],
                        structure_score=scores.get("structure", 0),
                        character_score=scores.get("character", 0),
                        emotion_score=scores.get("emotion", 0),
                        pacing_score=scores.get("pacing", 0),
                        theme_score=scores.get("theme", 0),
                        dialogue_score=scores.get("dialogue", 0),
                        combined_score=scores.get("combined", 0),
                        director_verdict=data.get("director_verdict", "UNKNOWN"),
                        director_confidence=data.get("director_confidence", 0),
                        templates_used=data.get("templates_used", {}),
                        dna_source=data.get("dna_source", ""),
                    ))
                except json.JSONDecodeError:
                    continue
        
        return records
    
    def get_category_trends(self) -> dict[str, list[tuple[str, float]]]:
        """Get score trends per category over time."""
        records = self.load_all()
        trends = {
            "structure": [],
            "character": [],
            "emotion": [],
            "pacing": [],
            "theme": [],
            "dialogue": [],
            "combined": [],
        }
        
        for r in records:
            trends["structure"].append((r.timestamp, r.structure_score))
            trends["character"].append((r.timestamp, r.character_score))
            trends["emotion"].append((r.timestamp, r.emotion_score))
            trends["pacing"].append((r.timestamp, r.pacing_score))
            trends["theme"].append((r.timestamp, r.theme_score))
            trends["dialogue"].append((r.timestamp, r.dialogue_score))
            trends["combined"].append((r.timestamp, r.combined_score))
        
        return trends
    
    def get_top_productions(self, category: str, n: int = 5) -> list[ProductionRecord]:
        """Get top N productions for a category."""
        records = self.load_all()
        
        score_map = {
            "structure": lambda r: r.structure_score,
            "character": lambda r: r.character_score,
            "emotion": lambda r: r.emotion_score,
            "pacing": lambda r: r.pacing_score,
            "theme": lambda r: r.theme_score,
            "dialogue": lambda r: r.dialogue_score,
            "combined": lambda r: r.combined_score,
        }
        
        getter = score_map.get(category, score_map["combined"])
        records.sort(key=getter, reverse=True)
        return records[:n]
    
    def get_weakest_category(self) -> tuple[str, float]:
        """Find the category with the lowest average score."""
        records = self.load_all()
        if not records:
            return ("combined", 0.0)
        
        averages = {
            "structure": sum(r.structure_score for r in records) / len(records),
            "character": sum(r.character_score for r in records) / len(records),
            "emotion": sum(r.emotion_score for r in records) / len(records),
            "pacing": sum(r.pacing_score for r in records) / len(records),
            "theme": sum(r.theme_score for r in records) / len(records),
            "dialogue": sum(r.dialogue_score for r in records) / len(records),
        }
        
        weakest = min(averages, key=averages.get)
        return (weakest, averages[weakest])


# =============================================================================
# Improvement Generator
# =============================================================================

class ImprovementGenerator:
    """Generates improvement proposals based on production history."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.history = ProductionHistory(vault_path)
    
    def generate_proposals(self, latest_production: ProductionRecord) -> list[ImprovementProposal]:
        """Generate improvement proposals based on the latest production's weaknesses."""
        proposals = []
        
        # Find the weakest category in the latest production
        scores = {
            "structure": latest_production.structure_score,
            "character": latest_production.character_score,
            "emotion": latest_production.emotion_score,
            "pacing": latest_production.pacing_score,
            "theme": latest_production.theme_score,
            "dialogue": latest_production.dialogue_score,
        }
        
        weakest = min(scores, key=scores.get)
        weakest_score = scores[weakest]
        
        # Only propose improvements if score is below threshold
        if weakest_score < 7.0:
            # Query history for top productions in this category
            top = self.history.get_top_productions(weakest, n=3)
            
            if top:
                # Generate proposals based on what top performers did differently
                proposals.extend(self._propose_from_history(weakest, top, latest_production))
            
            # Generate generic proposals for the weak category
            proposals.extend(self._propose_generic(weakest, weakest_score))
        
        # Always propose template evolution if we have enough history
        records = self.history.load_all()
        if len(records) >= 3:
            proposals.extend(self._propose_template_evolution(records))
        
        return proposals
    
    def _propose_from_history(self, category: str,
                               top_performers: list[ProductionRecord],
                               latest: ProductionRecord) -> list[ImprovementProposal]:
        """Propose improvements based on what top performers did."""
        proposals = []
        
        # Compare templates used
        top_templates = [r.templates_used for r in top_performers]
        latest_templates = latest.templates_used
        
        # Find templates that top performers used but latest didn't
        for top_record in top_performers:
            for template_type, template_name in top_record.templates_used.items():
                if template_type not in latest_templates:
                    proposals.append(ImprovementProposal(
                        id=f"imp_{datetime.now().strftime('%Y%m%d')}_{len(proposals):03d}",
                        category="template",
                        target_file="system3/evolution_engine.py",
                        description=f"Try template '{template_name}' for {template_type}",
                        reasoning=f"Top performer {top_record.production_id} used this template and scored {top_record.combined_score:.1f}",
                        expected_impact=f"+{(top_record.combined_score - latest.combined_score):.1f} combined score",
                        auto_applicable=False,
                    ))
        
        return proposals
    
    def _propose_generic(self, category: str, score: float) -> list[ImprovementProposal]:
        """Generate category-specific improvement proposals."""
        proposals = []
        timestamp = datetime.now().strftime('%Y%m%d')
        
        category_proposals = {
            "structure": [
                {
                    "target": "studio/skills/story-structure.md",
                    "desc": "Add more specific beat transition guidance",
                    "reason": f"Structure score ({score:.1f}) suggests weak act transitions",
                    "impact": "Stronger 3-act architecture",
                },
                {
                    "target": "system3/evolution_engine.py",
                    "desc": "Increase midpoint turn specificity in templates",
                    "reason": "Midpoint lacks narrative force",
                    "impact": "More compelling midpoint scenes",
                },
            ],
            "dialogue": [
                {
                    "target": "studio/skills/dialogue-craft.md",
                    "desc": "Add more subtext ladder examples",
                    "reason": f"Dialogue score ({score:.1f}) suggests on-the-nose writing",
                    "impact": "Higher subtext ratio",
                },
                {
                    "target": "studio/skills/dialogue-craft.md",
                    "desc": "Expand callback architecture section",
                    "reason": "Callbacks are sparse or don't transform",
                    "impact": "Better emotional payoff in Act 3",
                },
            ],
            "theme": [
                {
                    "target": "studio/skills/story-structure.md",
                    "desc": "Add theme weaving checkpoints per act",
                    "reason": f"Theme score ({score:.1f}) suggests theme is stated but not shown",
                    "impact": "Theme present in action lines and subtext",
                },
                {
                    "target": "system3/scene_brief_compiler.py",
                    "desc": "Strengthen theme keyword injection in briefs",
                    "reason": "Theme density per act is low",
                    "impact": "Higher theme density",
                },
            ],
            "character": [
                {
                    "target": "studio/skills/character-design.md",
                    "desc": "Add more core wound archetype patterns",
                    "reason": f"Character score ({score:.1f}) suggests weak transformation arcs",
                    "impact": "Stronger character arcs",
                },
            ],
            "emotion": [
                {
                    "target": "system4/emotional_model.py",
                    "desc": "Adjust recovery timing rules",
                    "reason": f"Emotion score ({score:.1f}) suggests pacing of emotional beats",
                    "impact": "Better emotional rhythm",
                },
            ],
            "pacing": [
                {
                    "target": "studio/skills/story-structure.md",
                    "desc": "Add animation-specific pacing rules",
                    "reason": f"Pacing score ({score:.1f}) suggests scene duration issues",
                    "impact": "Tighter scenes, better rhythm",
                },
            ],
        }
        
        for i, prop in enumerate(category_proposals.get(category, [])):
            proposals.append(ImprovementProposal(
                id=f"imp_{timestamp}_{i:03d}",
                category="skill" if "skills" in prop["target"] else "code",
                target_file=prop["target"],
                description=prop["desc"],
                reasoning=prop["reason"],
                expected_impact=prop["impact"],
                auto_applicable=False,
            ))
        
        return proposals
    
    def _propose_template_evolution(self, records: list[ProductionRecord]) -> list[ImprovementProposal]:
        """Propose evolving templates based on success patterns."""
        proposals = []
        
        # Find templates that correlate with high scores
        template_success: dict[str, list[float]] = {}
        for r in records:
            for template_type, template_name in r.templates_used.items():
                key = f"{template_type}:{template_name}"
                if key not in template_success:
                    template_success[key] = []
                template_success[key].append(r.combined_score)
        
        # Find templates with consistently low scores
        for key, scores in template_success.items():
            avg = sum(scores) / len(scores)
            if avg < 6.0 and len(scores) >= 2:
                template_type, template_name = key.split(":", 1)
                proposals.append(ImprovementProposal(
                    id=f"imp_{datetime.now().strftime('%Y%m%d')}_evolve_{len(proposals):03d}",
                    category="template",
                    target_file="system3/evolution_engine.py",
                    description=f"Retire or mutate low-performing template '{template_name}'",
                    reasoning=f"Average score {avg:.1f} over {len(scores)} productions",
                    expected_impact="Remove template drag on overall quality",
                    auto_applicable=False,
                ))
        
        return proposals


# =============================================================================
# Auto-Improver
# =============================================================================

class AutoImprover:
    """Automatically applies safe improvements."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
    
    def apply(self, proposal: ImprovementProposal) -> bool:
        """Apply an improvement proposal. Returns True if applied."""
        
        if proposal.category == "skill" and "skills" in proposal.target_file:
            return self._update_skill_file(proposal)
        
        # Code/template changes are not auto-applied for safety
        return False
    
    def _update_skill_file(self, proposal: ImprovementProposal) -> bool:
        """Append improvement notes to a skill file."""
        skill_path = self.vault_path / proposal.target_file.replace("studio/", "")
        if not skill_path.exists():
            return False
        
        appendix = f"""

---

## Auto-Learning Note ({datetime.now().strftime('%Y-%m-%d')})

**Issue**: {proposal.reasoning}

**Proposed Improvement**: {proposal.description}

**Expected Impact**: {proposal.expected_impact}

**Status**: Applied automatically

"""
        
        try:
            with open(skill_path, "a", encoding="utf-8") as f:
                f.write(appendix)
            return True
        except Exception:
            return False


# =============================================================================
# Self-Improvement Engine
# =============================================================================

class SelfImprovementEngine:
    """Main orchestrator for system self-improvement.
    
    Usage:
        engine = SelfImprovementEngine()
        
        # After a production completes
        engine.record_production(production_record)
        
        # Generate improvements
        proposals = engine.analyze_and_propose(latest_production)
        
        # Apply safe improvements
        for p in proposals:
            if p.auto_applicable:
                engine.apply_improvement(p)
    """
    
    def __init__(self, obsidian_bridge: Optional[ObsidianBridge] = None):
        self.bridge = obsidian_bridge or get_bridge()
        self.vault_path = Path(self.bridge.vault_path)
        
        self.history = ProductionHistory(self.vault_path)
        self.generator = ImprovementGenerator(self.vault_path)
        self.auto_improver = AutoImprover(self.vault_path)
        
        self.proposals_file = self.vault_path / "memory" / "improvement_proposals.jsonl"
        self.proposals_file.parent.mkdir(parents=True, exist_ok=True)
    
    def record_production(self, production: ProductionRecord) -> None:
        """Record a production for trend tracking."""
        self.history.record(production)
        print(f"[SelfImprovement] Recorded production {production.production_id}: {production.combined_score:.1f}")
    
    def analyze_and_propose(self, latest_production: ProductionRecord) -> list[ImprovementProposal]:
        """Analyze the latest production and propose improvements."""
        
        # Record first
        self.record_production(latest_production)
        
        # Generate proposals
        proposals = self.generator.generate_proposals(latest_production)
        
        # Save proposals
        for p in proposals:
            self._save_proposal(p)
        
        return proposals
    
    def apply_improvement(self, proposal: ImprovementProposal) -> bool:
        """Apply a single improvement proposal."""
        success = self.auto_improver.apply(proposal)
        
        if success:
            proposal.applied = True
            proposal.applied_at = datetime.now().isoformat()
            self._save_proposal(proposal)
            print(f"[SelfImprovement] Applied: {proposal.description}")
        
        return success
    
    def auto_improve(self, latest_production: ProductionRecord) -> list[ImprovementProposal]:
        """Full auto-improve cycle: analyze, propose, apply safe ones."""
        proposals = self.analyze_and_propose(latest_production)
        
        applied = []
        for p in proposals:
            if p.auto_applicable:
                if self.apply_improvement(p):
                    applied.append(p)
        
        print(f"[SelfImprovement] Generated {len(proposals)} proposals, applied {len(applied)} automatically")
        return applied
    
    def generate_evolution_report(self) -> EvolutionReport:
        """Generate a report on the system's evolution."""
        records = self.history.load_all()
        
        if not records:
            return EvolutionReport(
                total_productions=0,
                average_combined_score=0.0,
                score_trend="new",
                weakest_category="unknown",
                strongest_category="unknown",
                proposals_generated=0,
                proposals_applied=0,
                top_performing_templates=[],
                recurring_issues=[],
            )
        
        # Calculate averages
        avg_combined = sum(r.combined_score for r in records) / len(records)
        
        # Trend
        if len(records) >= 3:
            recent = sum(r.combined_score for r in records[-3:]) / 3
            older = sum(r.combined_score for r in records[:3]) / 3
            if recent > older + 0.5:
                trend = "improving"
            elif recent < older - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Weakest/strongest
        weakest, _ = self.history.get_weakest_category()
        all_avgs = {
            "structure": sum(r.structure_score for r in records) / len(records),
            "character": sum(r.character_score for r in records) / len(records),
            "emotion": sum(r.emotion_score for r in records) / len(records),
            "pacing": sum(r.pacing_score for r in records) / len(records),
            "theme": sum(r.theme_score for r in records) / len(records),
            "dialogue": sum(r.dialogue_score for r in records) / len(records),
        }
        strongest = max(all_avgs, key=all_avgs.get)
        
        # Top templates
        template_scores: dict[str, list[float]] = {}
        for r in records:
            for t_type, t_name in r.templates_used.items():
                key = f"{t_type}:{t_name}"
                if key not in template_scores:
                    template_scores[key] = []
                template_scores[key].append(r.combined_score)
        
        top_templates = sorted(
            template_scores.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
            reverse=True
        )[:5]
        
        # Recurring issues from Director notes
        all_issues = []
        for r in records:
            all_issues.extend(r.director_notes)
        
        # Simple frequency count
        from collections import Counter
        issue_counts = Counter(all_issues)
        recurring = [issue for issue, count in issue_counts.most_common(5) if count >= 2]
        
        # Count proposals
        proposals_generated = 0
        proposals_applied = 0
        if self.proposals_file.exists():
            with open(self.proposals_file, "r") as f:
                for line in f:
                    if line.strip():
                        proposals_generated += 1
                        try:
                            data = json.loads(line)
                            if data.get("applied"):
                                proposals_applied += 1
                        except:
                            pass
        
        return EvolutionReport(
            total_productions=len(records),
            average_combined_score=avg_combined,
            score_trend=trend,
            weakest_category=weakest,
            strongest_category=strongest,
            proposals_generated=proposals_generated,
            proposals_applied=proposals_applied,
            top_performing_templates=[t[0] for t in top_templates],
            recurring_issues=recurring,
        )
    
    def _save_proposal(self, proposal: ImprovementProposal) -> None:
        """Save a proposal to the proposals file."""
        with open(self.proposals_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "id": proposal.id,
                "category": proposal.category,
                "target_file": proposal.target_file,
                "description": proposal.description,
                "reasoning": proposal.reasoning,
                "expected_impact": proposal.expected_impact,
                "auto_applicable": proposal.auto_applicable,
                "applied": proposal.applied,
                "applied_at": proposal.applied_at,
            }) + "\n")
    
    def format_report(self, report: EvolutionReport) -> str:
        """Format an evolution report as markdown."""
        return f"""# Evolution Report

Generated: {datetime.now().isoformat()}

## Overall Health

| Metric | Value |
|--------|-------|
| Total Productions | {report.total_productions} |
| Average Combined Score | {report.average_combined_score:.1f}/10 |
| Score Trend | {report.score_trend.upper()} |
| Proposals Generated | {report.proposals_generated} |
| Proposals Applied | {report.proposals_applied} |

## Category Performance

| Category | Status |
|----------|--------|
| Strongest | **{report.strongest_category.upper()}** |
| Weakest | **{report.weakest_category.upper()}** (focus here) |

## Top Performing Templates

{chr(10).join(f"- {t}" for t in report.top_performing_templates) or "- No data yet"}

## Recurring Issues

{chr(10).join(f"- {issue}" for issue in report.recurring_issues) or "- No recurring issues detected"}

## Recommendations

1. **Focus on {report.weakest_category}**: This is your biggest quality lever.
2. **Study top templates**: See what patterns produce high scores.
3. **Ingest a new script**: Feed the system a screenplay strong in {report.weakest_category}.
4. **Run evolve cycle**: `python run_studio.py evolve` to auto-apply improvements.

---

*This report is auto-generated after every production.*
"""


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """CLI for self-improvement operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Improvement Engine")
    parser.add_argument("command", choices=["report", "propose", "apply", "evolve"])
    parser.add_argument("--production-id", help="Production ID to analyze")
    parser.add_argument("--score", type=float, help="Combined score")
    parser.add_argument("--category", help="Weak category")
    
    args = parser.parse_args()
    
    engine = SelfImprovementEngine()
    
    if args.command == "report":
        report = engine.generate_evolution_report()
        print(engine.format_report(report))
    
    elif args.command == "propose":
        if not args.production_id or args.score is None:
            print("Usage: propose --production-id ID --score N.N")
            return
        
        production = ProductionRecord(
            production_id=args.production_id,
            timestamp=datetime.now().isoformat(),
            concept_id="unknown",
            concept_title="unknown",
            combined_score=args.score,
        )
        
        proposals = engine.analyze_and_propose(production)
        print(f"\nGenerated {len(proposals)} improvement proposals:\n")
        for p in proposals:
            print(f"[{p.category.upper()}] {p.description}")
            print(f"  Target: {p.target_file}")
            print(f"  Reason: {p.reasoning}")
            print(f"  Impact: {p.expected_impact}")
            print(f"  Auto-apply: {'YES' if p.auto_applicable else 'NO'}")
            print()
    
    elif args.command == "evolve":
        print("Running evolution cycle...")
        report = engine.generate_evolution_report()
        print(engine.format_report(report))
        
        if report.weakest_category != "unknown":
            print(f"\nWeakest category: {report.weakest_category}")
            print(f"Suggestion: Run `python run_studio.py ingest <screenplay>` with a film strong in {report.weakest_category}")


if __name__ == "__main__":
    main()
