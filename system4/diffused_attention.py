"""System 4 Phase 5: Diffused Attention

Background inconsistency scanner that checks the entire production for problems
that individual analyzers might miss. Mimics "shower insight" — the idea that
comes when you're not focused on the problem.

Scanners:
- ContinuityScanner: Character behavior consistency across scenes
- ThemeDriftScanner: Theme sustainability and drift detection
- PacingDecayScanner: Pacing slowdown in act 3
- ArcCompletenessScanner: Character arc completion across all scenes
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
class Concern:
    """A concern flagged by Diffused Attention."""
    severity: str  # "critical", "major", "minor"
    category: str  # "continuity", "theme", "pacing", "arc", "dialogue"
    message: str
    scene_number: Optional[int] = None
    character: Optional[str] = None
    suggestion: str = ""


@dataclass
class DiffusedAttentionReport:
    """Complete report from Diffused Attention scan."""
    concerns: list[Concern]
    scan_time: float  # seconds
    categories_scanned: list[str]
    
    @property
    def critical_count(self) -> int:
        return sum(1 for c in self.concerns if c.severity == "critical")
    
    @property
    def major_count(self) -> int:
        return sum(1 for c in self.concerns if c.severity == "major")
    
    @property
    def minor_count(self) -> int:
        return sum(1 for c in self.concerns if c.severity == "minor")
    
    @property
    def has_critical(self) -> bool:
        return self.critical_count > 0


# =============================================================================
# Scanners
# =============================================================================

class ContinuityScanner:
    """Checks character behavior consistency across scenes."""
    
    def scan(self, scenes: list[dict], characters: list[dict]) -> list[Concern]:
        """Scan for continuity issues."""
        concerns = []
        
        if not scenes or not characters:
            return concerns
        
        # Build character profiles from vault data
        char_profiles = {}
        for char in characters:
            name = char.get("name", "")
            if name:
                char_profiles[name.lower()] = {
                    "name": name,
                    "archetype": char.get("archetype", ""),
                    "traits": self._extract_traits(char),
                }
        
        # Track character appearances and actions
        char_appearances = {}
        for i, scene in enumerate(scenes):
            content = scene.get("content", "")
            for char_name in char_profiles:
                if char_name.lower() in content.lower():
                    if char_name not in char_appearances:
                        char_appearances[char_name] = []
                    char_appearances[char_name].append({
                        "scene": i + 1,
                        "content": content,
                        "position": i / max(len(scenes) - 1, 1),
                    })
        
        # Check for characters who disappear too long
        for char_name, appearances in char_appearances.items():
            if len(appearances) >= 2:
                gaps = []
                for i in range(1, len(appearances)):
                    gap = appearances[i]["scene"] - appearances[i-1]["scene"]
                    gaps.append(gap)
                
                max_gap = max(gaps) if gaps else 0
                if max_gap > len(scenes) * 0.4:
                    concerns.append(Concern(
                        severity="minor",
                        category="continuity",
                        message=f"{char_profiles.get(char_name, {}).get('name', char_name)} disappears for {max_gap} scenes (too long for protagonist)",
                        character=char_profiles.get(char_name, {}).get('name', char_name),
                        suggestion="Add a brief appearance or mention to maintain audience connection",
                    ))
        
        # Check for characters who never appear in prototype scenes
        for char_name, profile in char_profiles.items():
            if char_name not in char_appearances:
                role = profile.get("archetype", "").lower()
                if "protagonist" in role or "main" in role:
                    concerns.append(Concern(
                        severity="major",
                        category="continuity",
                        message=f"Protagonist '{profile['name']}' does not appear in any prototyped scenes",
                        character=profile['name'],
                        suggestion="Ensure protagonist appears in hook, midpoint, or climax scene",
                    ))
        
        # Check for contradictory actions (simplified)
        for char_name, appearances in char_appearances.items():
            profile = char_profiles.get(char_name, {})
            archetype = profile.get("archetype", "").lower()
            
            # Example: Cynical trickster being overly earnest
            if "cynical" in archetype or "trickster" in archetype:
                for app in appearances:
                    content = app["content"].lower()
                    if any(word in content for word in ["i believe", "i trust", "people are good", "everything happens"]):
                        concerns.append(Concern(
                            severity="minor",
                            category="continuity",
                            message=f"Cynical character '{profile.get('name', char_name)}' uses uncharacteristically earnest language",
                            character=profile.get('name', char_name),
                            scene_number=app["scene"],
                            suggestion="Make dialogue more sarcastic or add irony to the moment",
                        ))
        
        return concerns
    
    def _extract_traits(self, char: dict) -> list[str]:
        """Extract character traits from character data."""
        traits = []
        content = str(char)
        
        # Look for common trait indicators
        trait_patterns = [
            r"(cynical|sarcastic|optimistic|naive|idealistic|jaded|warm|cold)",
            r"(brave|cowardly|selfish|generous|loyal|treacherous)",
        ]
        for pattern in trait_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            traits.extend(matches)
        
        return traits


class ThemeDriftScanner:
    """Checks if theme is sustained across all acts."""
    
    def scan(self, scenes: list[dict], theme: str, social_metaphor: str) -> list[Concern]:
        """Scan for theme drift."""
        concerns = []
        
        if not scenes:
            return concerns
        
        theme_keywords = self._extract_theme_keywords(theme)
        metaphor_keywords = self._extract_theme_keywords(social_metaphor)
        all_keywords = set(theme_keywords + metaphor_keywords)
        
        if not all_keywords:
            return concerns
        
        # Check theme presence in each act
        act_size = max(len(scenes) // 3, 1)
        acts = {
            "Act 1": scenes[:act_size],
            "Act 2": scenes[act_size:act_size*2],
            "Act 3": scenes[act_size*2:],
        }
        
        act_presence = {}
        for act_name, act_scenes in acts.items():
            act_content = " ".join(s.get("content", "").lower() for s in act_scenes)
            matches = sum(1 for kw in all_keywords if kw in act_content)
            act_presence[act_name] = matches / len(all_keywords) if all_keywords else 0
        
        # Flag acts with very low theme presence
        for act_name, presence in act_presence.items():
            if presence < 0.1:
                concerns.append(Concern(
                    severity="major",
                    category="theme",
                    message=f"Theme is nearly absent from {act_name} ({presence:.0%} keyword presence)",
                    suggestion=f"Weave theme keywords ({', '.join(list(all_keywords)[:3])}) into {act_name} scenes",
                ))
            elif presence < 0.25:
                concerns.append(Concern(
                    severity="minor",
                    category="theme",
                    message=f"Theme is weak in {act_name} ({presence:.0%} keyword presence)",
                    suggestion="Strengthen thematic imagery or dialogue in this act",
                ))
        
        # Check for theme decay (Act 3 lower than Act 1)
        if act_presence.get("Act 3", 1) < act_presence.get("Act 1", 0) * 0.5:
            concerns.append(Concern(
                severity="major",
                category="theme",
                message="Theme decays significantly in Act 3 (less than half of Act 1 presence)",
                suggestion="The climax should be where theme is most powerfully expressed, not weakest",
            ))
        
        return concerns
    
    def _extract_theme_keywords(self, text: str) -> list[str]:
        """Extract meaningful keywords from theme text."""
        if not text:
            return []
        
        # Remove common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                     "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
                     "between", "among", "through", "vs", "versus"}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return [w for w in words if w not in stopwords]


class PacingDecayScanner:
    """Checks if pacing slows down in later acts."""
    
    def scan(self, scenes: list[dict]) -> list[Concern]:
        """Scan for pacing decay."""
        concerns = []
        
        if len(scenes) < 6:
            return concerns
        
        # Calculate action density per act
        action_words = ["run", "chase", "fight", "escape", "discover", "confront",
                       "attack", "crash", "explode", "rush", "break", "leap", "fall"]
        
        act_size = max(len(scenes) // 3, 1)
        acts = {
            "Act 1": scenes[:act_size],
            "Act 2": scenes[act_size:act_size*2],
            "Act 3": scenes[act_size*2:],
        }
        
        act_density = {}
        for act_name, act_scenes in acts.items():
            total_words = sum(len(s.get("content", "").split()) for s in act_scenes)
            action_count = sum(
                sum(1 for word in action_words if word in s.get("content", "").lower())
                for s in act_scenes
            )
            density = action_count / max(total_words, 1) * 100  # per 100 words
            act_density[act_name] = density
        
        # Act 3 should have highest or comparable action density
        act3_density = act_density.get("Act 3", 0)
        act1_density = act_density.get("Act 1", 0)
        
        if act3_density < act1_density * 0.5:
            concerns.append(Concern(
                severity="major",
                category="pacing",
                message=f"Pacing decays in Act 3 (action density: {act3_density:.1f} vs Act 1: {act1_density:.1f} per 100 words)",
                suggestion="Add more active confrontation, chase, or discovery scenes to Act 3 climax",
            ))
        elif act3_density < act1_density * 0.7:
            concerns.append(Concern(
                severity="minor",
                category="pacing",
                message=f"Act 3 pacing is slower than Act 1 (action density: {act3_density:.1f} vs {act1_density:.1f})",
                suggestion="Increase action-to-dialogue ratio in climax scenes",
            ))
        
        return concerns


class ArcCompletenessScanner:
    """Checks if character arcs have setup and payoff."""
    
    def scan(self, scenes: list[dict], characters: list[dict]) -> list[Concern]:
        """Scan for incomplete character arcs."""
        concerns = []
        
        if not scenes or not characters:
            return concerns
        
        # Check main characters for transformation setup
        for char in characters:
            name = char.get("name", "")
            if not name:
                continue
            
            role = char.get("role", "").lower()
            if "supporting" in role and len(characters) > 4:
                # Skip deep arc checks for minor supporting characters
                continue
            
            # Check if character appears in first and last third
            first_third = scenes[:max(len(scenes)//3, 1)]
            last_third = scenes[-max(len(scenes)//3, 1):]
            
            first_appears = any(name.lower() in s.get("content", "").lower() for s in first_third)
            last_appears = any(name.lower() in s.get("content", "").lower() for s in last_third)
            
            if not first_appears and not last_appears:
                # Character doesn't appear at all - already flagged by ContinuityScanner
                continue
            
            if first_appears and not last_appears:
                concerns.append(Concern(
                    severity="minor",
                    category="arc",
                    message=f"Character '{name}' appears in Act 1 but not in final act — arc may lack resolution",
                    character=name,
                    suggestion="Give character a concluding moment or callback in the finale",
                ))
            
            if not first_appears and last_appears:
                concerns.append(Concern(
                    severity="minor",
                    category="arc",
                    message=f"Character '{name}' only appears in final act — may feel like deus ex machina",
                    character=name,
                    suggestion="Introduce character earlier or add setup/foreshadowing",
                ))
        
        return concerns


# =============================================================================
# Main Diffused Attention
# =============================================================================

class DiffusedAttention:
    """Background inconsistency scanner — mimics 'shower insight'."""
    
    def __init__(self):
        self.continuity = ContinuityScanner()
        self.theme_drift = ThemeDriftScanner()
        self.pacing_decay = PacingDecayScanner()
        self.arc_completeness = ArcCompletenessScanner()
    
    def scan(
        self,
        scenes: list[dict],
        characters: list[dict],
        theme: str = "",
        social_metaphor: str = "",
    ) -> DiffusedAttentionReport:
        """Run all scanners and compile concerns.
        
        Args:
            scenes: List of scene dicts
            characters: List of character dicts
            theme: Production theme string
            social_metaphor: Social metaphor string
        
        Returns:
            DiffusedAttentionReport with all concerns
        """
        import time
        start = time.time()
        
        concerns = []
        categories = []
        
        # Run continuity scan
        cont_concerns = self.continuity.scan(scenes, characters)
        if cont_concerns:
            concerns.extend(cont_concerns)
            categories.append("continuity")
        
        # Run theme drift scan
        theme_concerns = self.theme_drift.scan(scenes, theme, social_metaphor)
        if theme_concerns:
            concerns.extend(theme_concerns)
            categories.append("theme")
        
        # Run pacing decay scan
        pacing_concerns = self.pacing_decay.scan(scenes)
        if pacing_concerns:
            concerns.extend(pacing_concerns)
            categories.append("pacing")
        
        # Run arc completeness scan
        arc_concerns = self.arc_completeness.scan(scenes, characters)
        if arc_concerns:
            concerns.extend(arc_concerns)
            categories.append("arc")
        
        elapsed = time.time() - start
        
        # Sort by severity
        severity_order = {"critical": 0, "major": 1, "minor": 2}
        concerns.sort(key=lambda c: severity_order.get(c.severity, 3))
        
        return DiffusedAttentionReport(
            concerns=concerns,
            scan_time=elapsed,
            categories_scanned=categories,
        )
    
    def scan_package(self, package) -> DiffusedAttentionReport:
        """Scan a ProductionPackage for inconsistencies."""
        scenes = []
        for scene in getattr(package, "scenes", []) or []:
            scenes.append({
                "scene_number": getattr(scene, "scene_number", 0),
                "content": getattr(scene, "content", getattr(scene, "description", "")),
                "slugline": getattr(scene, "slugline", ""),
                "duration": getattr(scene, "duration", 120),
            })
        
        characters = getattr(package, "characters", []) or []
        char_dicts = []
        for char in characters:
            if isinstance(char, dict):
                char_dicts.append(char)
            else:
                char_dicts.append({
                    "name": getattr(char, "name", ""),
                    "archetype": getattr(char, "archetype", ""),
                    "role": getattr(char, "role", ""),
                })
        
        concept = getattr(package, "concept", None)
        theme = getattr(concept, "theme", "") if concept else ""
        
        # Try to get social metaphor from concept or constraints
        metaphor = ""
        if concept and hasattr(concept, "social_metaphor"):
            metaphor = concept.social_metaphor
        
        return self.scan(scenes, char_dicts, theme, metaphor)


# =============================================================================
# Concerns Writer
# =============================================================================

def write_concerns_to_vault(
    report: DiffusedAttentionReport,
    production_id: str,
    bridge=None,
) -> str:
    """Write concerns to studio/concerns.md vault note."""
    from bridge.obsidian_bridge import ObsidianNote, get_bridge
    
    if bridge is None:
        bridge = get_bridge()
    
    lines = [
        f"---",
        f"production_id: {production_id}",
        f"scanned_at: {__import__('datetime').datetime.now().isoformat()}",
        f"categories: {', '.join(report.categories_scanned)}",
        f"concerns: {len(report.concerns)}",
        f"critical: {report.critical_count}",
        f"major: {report.major_count}",
        f"minor: {report.minor_count}",
        f"---",
        f"",
        f"#concerns #diffused-attention",
        f"",
        f"# Diffused Attention Report: {production_id}",
        f"",
        f"**Scan time:** {report.scan_time:.3f}s",
        f"**Categories:** {', '.join(report.categories_scanned)}",
        f"**Concerns:** {len(report.concerns)} total ({report.critical_count} critical, {report.major_count} major, {report.minor_count} minor)",
        f"",
    ]
    
    if not report.concerns:
        lines.append("✅ No concerns detected. Production passes diffused attention scan.")
    else:
        for concern in report.concerns:
            icon = "🔴" if concern.severity == "critical" else "🟠" if concern.severity == "major" else "🟡"
            lines.append(f"## {icon} {concern.severity.upper()}: {concern.category}")
            lines.append(f"")
            lines.append(f"**{concern.message}**")
            if concern.character:
                lines.append(f"**Character:** {concern.character}")
            if concern.scene_number:
                lines.append(f"**Scene:** {concern.scene_number}")
            if concern.suggestion:
                lines.append(f"")
                lines.append(f"💡 *{concern.suggestion}*")
            lines.append(f"")
    
    content = "\n".join(lines)
    
    note = ObsidianNote(
        path=f"reviews/diffused_attention_{production_id}.md",
        title=f"Diffused Attention: {production_id}",
        frontmatter={
            "production_id": production_id,
            "concerns_count": len(report.concerns),
            "critical_count": report.critical_count,
        },
        content=content,
        tags=["diffused-attention", "concerns"]
    )
    
    bridge.write_note(f"reviews/diffused_attention_{production_id}.md", note)
    
    # Also append to concerns.md
    existing = bridge.read_note("concerns.md")
    if existing:
        new_content = existing.content + f"\n\n## {production_id}\n"
        if report.has_critical:
            new_content += f"🔴 {report.critical_count} critical concerns flagged.\n"
        new_content += f"See [[reviews/diffused_attention_{production_id}]] for details.\n"
        
        bridge.write_note("concerns.md", ObsidianNote(
            path="concerns.md",
            title="Active Concerns",
            frontmatter={},
            content=new_content,
            tags=["concerns"]
        ))
    
    return content


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2 or sys.argv[1] != "demo":
        print("Usage: python diffused_attention.py demo")
        sys.exit(1)
    
    da = DiffusedAttention()
    
    # Demo data
    demo_scenes = [
        {"scene_number": 1, "content": "Judy Hopps arrives in Zootopia, full of dreams. She believes anyone can be anything.", "slugline": "EXT. TRAIN STATION - DAY", "duration": 120},
        {"scene_number": 2, "content": "Assigned parking duty. Her spirit is crushed. She sits alone, questioning everything.", "slugline": "EXT. STREET - DAY", "duration": 120},
        {"scene_number": 3, "content": "Nick Wilde tricks her with the pawpsicle scam. She's humiliated but intrigued.", "slugline": "INT. ICE CREAM SHOP - DAY", "duration": 180},
        {"scene_number": 4, "content": "The case falls apart. Nick leaves her. She's alone, her badge meaningless. All is lost.", "slugline": "INT. APARTMENT - NIGHT", "duration": 150},
        {"scene_number": 5, "content": "She discovers the conspiracy. Predators going savage is not biological — it's manufactured.", "slugline": "INT. TRAIN - NIGHT", "duration": 180},
        {"scene_number": 6, "content": "Confronts Bellwether. A chase through the museum. She saves Nick. The city is healed.", "slugline": "EXT. MUSEUM - NIGHT", "duration": 240},
    ]
    
    demo_chars = [
        {"name": "Judy Hopps", "archetype": "optimistic underdog", "role": "protagonist"},
        {"name": "Nick Wilde", "archetype": "cynical trickster", "role": "deuteragonist"},
        {"name": "Bellwether", "archetype": "hidden tyrant", "role": "antagonist"},
    ]
    
    report = da.scan(
        demo_scenes,
        demo_chars,
        theme="anyone can be anything / prejudice",
        social_metaphor="predator/prey dynamics mirror real-world prejudice",
    )
    
    print("=" * 60)
    print("DIFFUSED ATTENTION DEMO")
    print("=" * 60)
    print(f"\nScanned {len(report.categories_scanned)} categories in {report.scan_time:.3f}s")
    print(f"Concerns: {len(report.concerns)} ({report.critical_count} critical, {report.major_count} major, {report.minor_count} minor)")
    
    if report.concerns:
        print(f"\nConcerns:")
        for c in report.concerns:
            icon = "🔴" if c.severity == "critical" else "🟠" if c.severity == "major" else "🟡"
            print(f"  {icon} [{c.category}] {c.message}")
            if c.suggestion:
                print(f"     💡 {c.suggestion}")
    else:
        print("\n✅ No concerns detected")
