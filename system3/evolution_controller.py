"""Evolution Controller — Orchestrates the full System 3 pipeline.

Connects the Story Evolution Engine (concept selection) to the Production Swarm
(execution), managing the handoff and monitoring the full lifecycle.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import sys
bridge_dir = Path(__file__).resolve().parent.parent / "bridge"
if str(bridge_dir) not in sys.path:
    sys.path.insert(0, str(bridge_dir))

from obsidian_bridge import ObsidianBridge, ObsidianNote, get_bridge
from platform_bridge import CollaborationHubPy

from system3.evolution_engine import StoryEvolutionEngine, Concept
from system3.production_swarm import ProductionSwarm

# System 4: Director Agent (lazy import)
try:
    from system4.director_agent import DirectorAgent, Verdict
    DIRECTOR_AVAILABLE = True
except ImportError:
    DIRECTOR_AVAILABLE = False


@dataclass
class ProductionPackage:
    """The final deliverable from System 3."""
    concept: Concept
    screenplay: dict[str, Any]
    characters: list[dict[str, Any]]
    environments: list[dict[str, Any]]
    shot_lists: list[dict[str, Any]]
    scenes: list[dict[str, Any]]
    assets: dict[str, list[str]]
    reviews: dict[str, Any]
    cost_report: dict[str, float]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    director_decision: Any = None
    
    def to_dict(self) -> dict[str, Any]:
        result = {
            "concept": self.concept.to_dict(),
            "screenplay": self.screenplay,
            "characters": self.characters,
            "environments": self.environments,
            "shot_lists": self.shot_lists,
            "scenes": self.scenes,
            "assets": self.assets,
            "reviews": self.reviews,
            "cost_report": self.cost_report,
            "generated_at": self.generated_at
        }
        if self.director_decision:
            result["director_decision"] = self.director_decision.to_dict()
        return result


class EvolutionController:
    """Central controller for System 3.
    
    Orchestrates the full pipeline:
    1. Evolve story concepts → select winner
    2. Spawn production swarm → execute all departments
    3. Compile production package → deliver final output
    4. Write post-mortem → update long-term memory
    
    This is the main entry point for System 3.
    """
    
    def __init__(self, 
                 obsidian_bridge: Optional[ObsidianBridge] = None,
                 n_concepts: int = 6,
                 n_rounds: int = 2,
                 top_k: int = 2,
                 budget_usd: float = 50.0):
        self.bridge = obsidian_bridge or get_bridge()
        self.budget_usd = budget_usd
        
        # Subsystems
        self.evolution_engine = StoryEvolutionEngine(
            obsidian_bridge=self.bridge,
            n_concepts=n_concepts,
            n_rounds=n_rounds,
            top_k=top_k
        )
        self.production_swarm = ProductionSwarm(
            obsidian_bridge=self.bridge
        )
        self.collaboration_hub = CollaborationHubPy()
        
        # State
        self.current_production_id: Optional[str] = None
        self.total_cost_usd: float = 0.0
        self.package: Optional[ProductionPackage] = None
    
    def produce(self, 
                dna_source: str,
                constraints: dict[str, str],
                production_id: Optional[str] = None) -> ProductionPackage:
        """Run the full production pipeline.
        
        Args:
            dna_source: Path to Creative DNA in vault
            constraints: User constraints (setting, characters, theme, etc.)
            production_id: Optional production identifier
            
        Returns:
            ProductionPackage with all deliverables
        """
        self.current_production_id = production_id or f"prod-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        print(f"\n{'='*70}")
        print(f"  EVOLUTIONARY STUDIO — Production: {self.current_production_id}")
        print(f"{'='*70}\n")
        
        # Phase 1: Story Evolution
        print("PHASE 1: Story Evolution")
        print("-" * 40)
        winner = self.evolution_engine.evolve(dna_source, constraints)
        
        # Phase 2: Production Swarm
        print("\nPHASE 2: Production Swarm")
        print("-" * 40)
        self.production_swarm.create_production_tasks(winner)
        swarm_results = self.production_swarm.run()
        
        # Phase 3: Compile Package
        print("\nPHASE 3: Production Compiler")
        print("-" * 40)
        self.package = self._compile_package(winner, swarm_results)
        
        # Phase 3.5: Director Review (System 4)
        print("\nPHASE 3.5: Director Review")
        print("-" * 40)
        director_decision = self._director_review(self.package)
        self.package.director_decision = director_decision
        
        # Phase 3.6: Diffused Attention + Emotional Model (System 4)
        print("\nPHASE 3.6: Diffused Attention + Emotional Model")
        print("-" * 40)
        self._run_diffused_attention(self.package)
        
        # Phase 4: Save & Report
        print("\nPHASE 4: Save & Report")
        print("-" * 40)
        self._save_package(self.package)
        self._write_post_mortem()
        
        # Print Director verdict
        print(f"\n  DIRECTOR VERDICT: {director_decision.verdict.value.upper()}")
        print(f"  Confidence: {director_decision.confidence:.0%}")
        print(f"  Reason: {director_decision.reason[:100]}...")
        
        # Phase 5: Index into Long-Term Memory (System 4)
        print("\nPHASE 5: Index into Vector Memory")
        print("-" * 40)
        try:
            from system4.long_term_memory import LongTermMemory
            ltm = LongTermMemory(bridge=self.bridge)
            counts = ltm.ingest_production(self.current_production_id)
            total = sum(counts.values())
            print(f"  Indexed {total} chunks into vector memory")
            for doc_type, count in counts.items():
                if count > 0:
                    print(f"    {doc_type}: {count}")
        except Exception as e:
            print(f"  [Warning] LTM indexing failed: {e}")
        
        print(f"\n{'='*70}")
        print(f"  PRODUCTION COMPLETE: {self.current_production_id}")
        print(f"  Concept: {winner.title}")
        print(f"  Scenes: {len(self.package.scenes)}")
        print(f"  Characters: {len(self.package.characters)}")
        print(f"  Environments: {len(self.package.environments)}")
        print(f"{'='*70}\n")
        
        return self.package
    
    def _compile_package(self, concept: Concept, 
                         swarm_results: dict[str, Any]) -> ProductionPackage:
        """Compile all production outputs into a unified package."""
        
        # Gather scenes
        scenes = []
        scene_notes = self.bridge.query_notes(folder="scenes")
        for note in scene_notes:
            if "shots" not in note.path:  # Exclude shot lists
                scenes.append({
                    "id": Path(note.path).stem,
                    "slugline": note.frontmatter.get("slugline", ""),
                    "characters": note.frontmatter.get("characters", []),
                    "content_preview": note.content[:200] + "..." if len(note.content) > 200 else note.content
                })
        
        # Gather characters
        characters = []
        char_notes = self.bridge.query_notes(folder="characters")
        for note in char_notes:
            if "environment" not in note.path and "supporting" not in note.path:
                characters.append({
                    "id": note.frontmatter.get("character_id", ""),
                    "name": note.frontmatter.get("name", ""),
                    "archetype": note.frontmatter.get("archetype", ""),
                    "role": note.frontmatter.get("role", "")
                })
        
        # Gather environments
        environments = []
        env_notes = self.bridge.query_notes(folder="characters/environments")
        for note in env_notes:
            environments.append({
                "id": note.frontmatter.get("env_id", ""),
                "name": note.frontmatter.get("name", ""),
                "type": note.frontmatter.get("type", "")
            })
        
        # Gather shot lists
        shot_lists = []
        shot_notes = self.bridge.query_notes(folder="scenes")
        for note in shot_notes:
            if "shots" in note.path:
                shot_lists.append({
                    "scene_id": note.frontmatter.get("scene_id", ""),
                    "shot_count": note.frontmatter.get("shot_count", 0),
                    "total_duration": note.frontmatter.get("total_duration_estimate", 0)
                })
        
        # Gather reviews
        reviews = self.collaboration_hub.get_review_summary()
        
        # Cost report
        cost_report = {
            "budget_allocated": self.budget_usd,
            "estimated_concept_generation": 0.0,  # No API calls in template version
            "estimated_prototyping": 0.0,
            "estimated_production": 0.0,
            "total_estimated": 0.0,
            "remaining": self.budget_usd
        }
        
        return ProductionPackage(
            concept=concept,
            screenplay={
                "format": "fountain",
                "scene_count": len(scenes),
                "scenes": [s["id"] for s in scenes]
            },
            characters=characters,
            environments=environments,
            shot_lists=shot_lists,
            scenes=scenes,
            assets={
                "images": [],
                "audio": [],
                "video": []
            },
            reviews=reviews,
            cost_report=cost_report
        )
    
    def _director_review(self, package: ProductionPackage) -> Any:
        """Run Director Agent review on the compiled package."""
        if not DIRECTOR_AVAILABLE:
            print("  [Director Agent not available — skipping review]")
            # Return a default accept decision
            from system4.director_agent import Decision, Verdict
            return Decision(
                verdict=Verdict.ACCEPT,
                production_id=self.current_production_id,
                reason="Director Agent not available. Auto-accepting.",
                action="Proceed with production.",
                confidence=0.5,
            )
        
        # Build package dict for Director
        package_dict = self._package_to_dict(package)
        
        # Load evaluation scores into package dict
        eval_notes = self.bridge.query_notes(folder="reviews")
        for note in eval_notes:
            if "evaluation_" in note.path:
                scores = note.frontmatter.get("scores", {})
                combined = note.frontmatter.get("combined_score", 0)
                package_dict["reviews"] = {
                    "scores": scores,
                    "combined_score": combined,
                }
                break
        
        director = DirectorAgent()
        decision = director.review_production(package_dict, self.current_production_id)
        
        # Write decision to vault
        decision_note = ObsidianNote(
            path=f"reviews/director_decision_{self.current_production_id}.md",
            title=f"Director Decision: {self.current_production_id}",
            frontmatter={
                "production_id": self.current_production_id,
                "verdict": decision.verdict.value,
                "confidence": decision.confidence,
                "reviewed_at": decision.reviewed_at,
            },
            content=decision.to_markdown(),
            tags=["director", "decision"]
        )
        self.bridge.write_note(
            f"reviews/director_decision_{self.current_production_id}.md",
            decision_note
        )
        
        # Also append to decision log
        log_entry = f"\n## {decision.reviewed_at}\n**{decision.verdict.value.upper()}** — {self.current_production_id}\n{decision.reason}\n"
        log_path = "decision_log.md"
        existing = self.bridge.read_note(log_path)
        if existing:
            new_content = existing.content + log_entry
        else:
            new_content = f"# Decision Log\n\n{log_entry}"
        log_note = ObsidianNote(
            path=log_path,
            title="Decision Log",
            frontmatter={},
            content=new_content,
            tags=["decisions"]
        )
        self.bridge.write_note(log_path, log_note)
        
        return decision
    
    def _run_diffused_attention(self, package: ProductionPackage) -> None:
        """Run Diffused Attention scan and Emotional Model analysis."""
        try:
            from system4.diffused_attention import DiffusedAttention, write_concerns_to_vault
            from system4.emotional_model import EmotionalModel
            
            # Diffused Attention scan
            da = DiffusedAttention()
            report = da.scan_package(package)
            
            if report.concerns:
                print(f"  ⚠ {len(report.concerns)} concern(s) flagged:")
                for c in report.concerns[:3]:
                    icon = "🔴" if c.severity == "critical" else "🟠" if c.severity == "major" else "🟡"
                    print(f"    {icon} [{c.category}] {c.message}")
                if len(report.concerns) > 3:
                    print(f"    ... and {len(report.concerns) - 3} more")
            else:
                print("  ✅ No concerns detected")
            
            # Write to vault
            write_concerns_to_vault(report, self.current_production_id, self.bridge)
            
            # Emotional Model analysis
            em = EmotionalModel()
            
            # Build scenes from package
            scenes = []
            for s in getattr(package, "scenes", []) or []:
                scenes.append({
                    "scene_number": getattr(s, "scene_number", 0),
                    "content": getattr(s, "content", getattr(s, "description", "")),
                    "slugline": getattr(s, "slugline", ""),
                    "duration": getattr(s, "duration", 120),
                })
            
            if scenes:
                analysis = em.analyze(scenes)
                print(f"  Emotional arc: {analysis.overall_arc} (score: {analysis.score}/10)")
                print(f"  Valence range: {analysis.valence_range}")
                if analysis.specific_issues:
                    print(f"  Issues: {len(analysis.specific_issues)}")
                
                # Write emotional analysis to vault
                beats_lines = []
                for b in analysis.beats:
                    beats_lines.append(f"- Scene {b.scene_number} ({b.position:.0%}): valence={b.valence:+.2f} [{b.label}]")
                
                em_note = ObsidianNote(
                    path=f"reviews/emotional_analysis_{self.current_production_id}.md",
                    title=f"Emotional Analysis: {self.current_production_id}",
                    frontmatter={
                        "production_id": self.current_production_id,
                        "arc": analysis.overall_arc,
                        "score": analysis.score,
                        "valence_range": analysis.valence_range,
                        "climax_score": analysis.climax_score,
                    },
                    content=f"""#emotional-model #analysis

# Emotional Analysis: {self.current_production_id}

**Arc:** {analysis.overall_arc}
**Score:** {analysis.score}/10
**Valence Range:** {analysis.valence_range}
**Climax Score:** {analysis.climax_score}

## Beats
{chr(10).join(beats_lines)}

## Strengths
{chr(10).join("- " + s for s in analysis.strengths) if analysis.strengths else "- None identified"}

## Issues
{chr(10).join("- " + i for i in analysis.specific_issues) if analysis.specific_issues else "- None identified"}

## Recovery Issues
{chr(10).join(f"- Scene {r['scene']}: {r['issue']}" for r in analysis.recovery_issues) if analysis.recovery_issues else "- None"}
""",
                    tags=["emotional-model", "analysis"]
                )
                self.bridge.write_note(
                    f"reviews/emotional_analysis_{self.current_production_id}.md",
                    em_note
                )
        except Exception as e:
            print(f"  [Warning] Diffused Attention / Emotional Model failed: {e}")
    
    def _package_to_dict(self, package: ProductionPackage) -> dict[str, Any]:
        """Convert ProductionPackage to dict for Director review."""
        return {
            "concept": {
                "title": package.concept.title,
                "logline": package.concept.logline,
                "theme": package.concept.theme,
                "social_metaphor": package.concept.social_metaphor,
                "genre": package.concept.genre,
            },
            "characters": [
                {
                    "name": c.name,
                    "archetype": c.archetype,
                    "starting_state": c.starting_state,
                    "ending_state": c.ending_state,
                }
                for c in [package.concept.protagonist, package.concept.deuteragonist, 
                         package.concept.antagonist] if c
            ],
            "scenes": package.scenes,
            "reviews": package.reviews,
        }
    
    def _save_package(self, package: ProductionPackage) -> None:
        """Save the production package to the vault."""
        package_note = ObsidianNote(
            path=f"memory/post_mortems/package_{self.current_production_id}.md",
            title=f"Production Package: {package.concept.title}",
            frontmatter={
                "production_id": self.current_production_id,
                "concept_id": package.concept.id,
                "concept_title": package.concept.title,
                "generated_at": package.generated_at
            },
            content=self._format_package_report(package),
            tags=["package", "production"]
        )
        self.bridge.write_note(
            f"memory/post_mortems/package_{self.current_production_id}.md",
            package_note
        )
    
    def _format_package_report(self, package: ProductionPackage) -> str:
        """Format the production package as a readable report."""
        lines = [
            f"# Production Package: {package.concept.title}",
            "",
            "## Concept",
            f"- **Title**: {package.concept.title}",
            f"- **Logline**: {package.concept.logline}",
            f"- **Theme**: {package.concept.theme}",
            "",
            "## Screenplay",
            f"- **Format**: {package.screenplay.get('format', 'unknown')}",
            f"- **Scenes**: {package.screenplay.get('scene_count', 0)}",
            "",
            "## Characters",
        ]
        for char in package.characters:
            lines.append(f"- **{char['name']}** ({char['archetype']}) — {char['role']}")
        
        lines.extend([
            "",
            "## Environments",
        ])
        for env in package.environments:
            lines.append(f"- **{env['name']}** ({env['type']})")
        
        lines.extend([
            "",
            "## Shot Lists",
        ])
        for sl in package.shot_lists:
            lines.append(f"- {sl['scene_id']}: {sl['shot_count']} shots, {sl['total_duration']}s estimated")
        
        lines.extend([
            "",
            "## Reviews Summary",
            f"- Total Reviews: {package.reviews.get('total_reviews', 0)}",
            f"- Pending: {package.reviews.get('pending', 0)}",
            f"- Applied: {package.reviews.get('applied', 0)}",
            "",
            "## Cost Report",
            f"- Budget: ${package.cost_report.get('budget_allocated', 0):.2f}",
            f"- Estimated Total: ${package.cost_report.get('total_estimated', 0):.2f}",
            f"- Remaining: ${package.cost_report.get('remaining', 0):.2f}",
        ])
        
        return "\n".join(lines)
    
    def _write_post_mortem(self) -> None:
        """Write a post-mortem for this production."""
        stats = self.evolution_engine.get_evolution_stats()
        
        post_mortem = ObsidianNote(
            path=f"memory/post_mortems/post_mortem_{self.current_production_id}.md",
            title=f"Post-Mortem: {self.current_production_id}",
            frontmatter={
                "production_id": self.current_production_id,
                "generated_at": datetime.now().isoformat(),
                "concept_id": self.evolution_engine.winning_concept.id if self.evolution_engine.winning_concept else None
            },
            content=f"""# Post-Mortem: {self.current_production_id}

## Evolution Stats
- **Concepts Generated**: {stats['total_concepts_generated']}
- **Evaluations**: {stats['total_evaluations']}
- **Rounds**: {stats['rounds_completed']}

## What Worked
- Story evolution engine successfully generated and evaluated concepts
- Critic swarm provided multi-dimensional scoring
- Production swarm executed all departments in parallel

## What to Improve
- Add more variation to concept generation (currently template-based)
- Integrate actual image/video generation when API keys available
- Add real cost tracking per tool execution

## Learnings
- The 4-critic model (structure, emotion, pacing, theme) catches most issues
- Dependency-based task queue prevents blocking
- Obsidian vault makes state human-readable and persistent
""",
            tags=["post-mortem", "learning"]
        )
        self.bridge.write_note(
            f"memory/post_mortems/post_mortem_{self.current_production_id}.md",
            post_mortem
        )
    
    def get_status(self) -> dict[str, Any]:
        """Get current production status."""
        return {
            "production_id": self.current_production_id,
            "phase": "complete" if self.package else "in_progress",
            "evolution_stats": self.evolution_engine.get_evolution_stats() if hasattr(self.evolution_engine, 'get_evolution_stats') else {},
            "swarm_stats": self.production_swarm.queue.get_stats() if hasattr(self.production_swarm, 'queue') else {},
            "total_cost": self.total_cost_usd,
            "budget_remaining": self.budget_usd - self.total_cost_usd
        }


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    # Full pipeline demo
    controller = EvolutionController(
        n_concepts=4,
        n_rounds=1,
        top_k=2,
        budget_usd=50.0
    )
    
    package = controller.produce(
        dna_source="memory/films_analyzed/zootopia_dna.md",
        constraints={
            "setting": "a floating city of robots and humans",
            "group_a": "robot",
            "group_b": "human",
            "genre": "sci-fi animated comedy-drama",
            "theme": "trust between synthetic and organic life",
            "social_metaphor": "robot/human dynamics mirror immigration and assimilation"
        },
        production_id="demo-robot-city-001"
    )
    
    print("\nFinal Package:")
    print(json.dumps(package.to_dict(), indent=2, default=str))
