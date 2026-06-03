"""Parallel Production Swarm — Department Agents for System 3.

Each department is a specialized agent that:
- Reads the winning screenplay from Obsidian
- Claims tasks from a shared queue
- Uses OpenMontage tools for generation
- Writes results back to Obsidian
- Reports status to the Evolution Controller
"""

from __future__ import annotations

import json
import random
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import sys
bridge_dir = Path(__file__).resolve().parent.parent / "bridge"
if str(bridge_dir) not in sys.path:
    sys.path.insert(0, str(bridge_dir))

from obsidian_bridge import ObsidianBridge, ObsidianNote, get_bridge
from openmontage_bridge import OpenMontageBridge, get_bridge as get_om_bridge
from platform_bridge import ConsistencyEnginePy, CollaborationHubPy

# System 4: Language Engine (lazy import to avoid circular dependency)
try:
    from system4.language_engine import LanguageEngine, VoiceProfile
    LANGUAGE_ENGINE_AVAILABLE = True
except ImportError:
    LANGUAGE_ENGINE_AVAILABLE = False

# Scene Brief Compiler (AI-as-Engine architecture)
try:
    from system3.scene_brief_compiler import SceneBriefCompiler, ScreenplayAssembler
    BRIEF_COMPILER_AVAILABLE = True
except ImportError:
    BRIEF_COMPILER_AVAILABLE = False


# =============================================================================
# Task Queue & Dependencies
# =============================================================================

@dataclass
class ProductionTask:
    """A single task in the production queue."""
    id: str
    department: str  # writer, visual, character, world, animation, sound, editorial
    task_type: str   # e.g., "write_scene", "design_character", "generate_shot"
    target: str      # scene_id, character_id, shot_id
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"  # pending, blocked, in_progress, completed, failed
    priority: int = 5  # 1 (highest) to 10 (lowest)
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    assigned_agent: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class TaskQueue:
    """Central task queue with dependency resolution."""
    
    def __init__(self):
        self.tasks: dict[str, ProductionTask] = {}
        self.completed_task_ids: set[str] = set()
    
    def add_task(self, task: ProductionTask) -> None:
        """Add a task to the queue."""
        self.tasks[task.id] = task
    
    def add_tasks(self, tasks: list[ProductionTask]) -> None:
        for task in tasks:
            self.add_task(task)
    
    def get_ready_tasks(self, department: Optional[str] = None) -> list[ProductionTask]:
        """Get tasks whose dependencies are all satisfied."""
        ready = []
        for task in self.tasks.values():
            if task.status != "pending":
                continue
            
            # Check if all dependencies are completed
            deps_satisfied = all(
                dep in self.completed_task_ids or 
                (dep in self.tasks and self.tasks[dep].status == "completed")
                for dep in task.dependencies
            )
            
            if deps_satisfied:
                if department is None or task.department == department:
                    ready.append(task)
        
        # Sort by priority (lower = higher priority)
        ready.sort(key=lambda t: t.priority)
        return ready
    
    def claim_task(self, task_id: str, agent_name: str) -> Optional[ProductionTask]:
        """Claim a task for an agent."""
        task = self.tasks.get(task_id)
        if task and task.status == "pending":
            task.status = "in_progress"
            task.assigned_agent = agent_name
            return task
        return None
    
    def complete_task(self, task_id: str, outputs: dict[str, Any]) -> bool:
        """Mark a task as completed."""
        task = self.tasks.get(task_id)
        if task and task.status == "in_progress":
            task.status = "completed"
            task.outputs = outputs
            task.completed_at = datetime.now().isoformat()
            self.completed_task_ids.add(task_id)
            return True
        return False
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed."""
        task = self.tasks.get(task_id)
        if task:
            task.status = "failed"
            task.error_message = error
            return True
        return False
    
    def get_stats(self) -> dict[str, Any]:
        """Get queue statistics."""
        counts = {"pending": 0, "in_progress": 0, "completed": 0, "failed": 0, "blocked": 0}
        for task in self.tasks.values():
            if task.status in counts:
                counts[task.status] += 1
            # Count blocked separately
            if task.status == "pending" and task.dependencies:
                if not all(d in self.completed_task_ids for d in task.dependencies):
                    counts["blocked"] += 1
        
        return {
            "total": len(self.tasks),
            **counts
        }


# =============================================================================
# Base Department Agent
# =============================================================================

class DepartmentAgent(ABC):
    """Base class for all department agents.
    
    Each agent:
    1. Reads context from Obsidian
    2. Claims tasks from the queue
    3. Executes work
    4. Writes results back to Obsidian
    5. Marks tasks complete
    """
    
    def __init__(self, 
                 name: str,
                 obsidian_bridge: Optional[ObsidianBridge] = None,
                 om_bridge: Optional[OpenMontageBridge] = None):
        self.name = name
        self.bridge = obsidian_bridge or get_bridge()
        self.om = om_bridge or get_om_bridge()
        self.queue: Optional[TaskQueue] = None
        self.consistency_engine: Optional[ConsistencyEnginePy] = None
        self.collaboration_hub: Optional[CollaborationHubPy] = None
    
    def attach_queue(self, queue: TaskQueue) -> None:
        self.queue = queue
    
    def attach_consistency_engine(self, engine: ConsistencyEnginePy) -> None:
        self.consistency_engine = engine
    
    def attach_collaboration_hub(self, hub: CollaborationHubPy) -> None:
        self.collaboration_hub = hub
    
    def get_ready_tasks(self) -> list[ProductionTask]:
        """Get tasks ready for this department."""
        if self.queue is None:
            return []
        return self.queue.get_ready_tasks(department=self.name)
    
    def claim_and_work(self) -> list[ProductionTask]:
        """Claim all ready tasks and process them."""
        completed = []
        for task in self.get_ready_tasks():
            claimed = self.queue.claim_task(task.id, self.name)
            if claimed:
                try:
                    outputs = self.execute_task(claimed)
                    self.queue.complete_task(claimed.id, outputs)
                    completed.append(claimed)
                    print(f"[{self.name}] Completed: {claimed.task_type} → {claimed.target}")
                except Exception as e:
                    self.queue.fail_task(claimed.id, str(e))
                    print(f"[{self.name}] FAILED: {claimed.task_type} — {e}")
        return completed
    
    @abstractmethod
    def execute_task(self, task: ProductionTask) -> dict[str, Any]:
        """Execute a single task. Must be implemented by subclasses."""
        ...
    
    def _read_concept(self, concept_id: str = "WINNER") -> Optional[ObsidianNote]:
        """Read a concept from the vault."""
        return self.bridge.read_note(f"concepts/{concept_id}.md")
    
    def _write_scene(self, scene_id: str, content: str, 
                    frontmatter: Optional[dict] = None) -> Path:
        """Write a scene note to the vault."""
        note = ObsidianNote(
            path=f"scenes/{scene_id}.md",
            title=scene_id.replace("_", " ").title(),
            frontmatter=frontmatter or {},
            content=content,
            tags=["scene"]
        )
        return self.bridge.write_note(f"scenes/{scene_id}.md", note)


# =============================================================================
# Writer Agent
# =============================================================================

class WriterAgent(DepartmentAgent):
    """Generates full screenplay in Fountain format from the winning concept.
    
    Writes scene by scene, storing each as a separate Obsidian note.
    """
    
    def __init__(self, **kwargs):
        super().__init__("writer", **kwargs)
        self.scenes_per_batch = 5
    
    def execute_task(self, task: ProductionTask) -> dict[str, Any]:
        """Write scenes for the screenplay."""
        if task.task_type == "write_screenplay":
            return self._write_screenplay(task)
        elif task.task_type == "write_scene":
            return self._write_single_scene(task)
        elif task.task_type == "generate_briefs":
            return self._generate_briefs(task)
        else:
            return {"status": "unknown_task_type"}
    
    def _write_screenplay(self, task: ProductionTask) -> dict[str, Any]:
        """Generate the full screenplay from the winning concept."""
        concept_note = self._read_concept("WINNER")
        if concept_note is None:
            raise ValueError("No winning concept found")
        
        # Parse concept into structure
        concept_data = self._parse_concept_note(concept_note)
        
        # Load voice profiles from vault
        voice_profiles = self._load_voice_profiles()
        
        # Load craft skills
        skills = self._load_skills()
        
        # Generate scene list
        scenes = self._generate_scene_list(concept_data, voice_profiles)
        
        # Validate dialogue with Language Engine
        if LANGUAGE_ENGINE_AVAILABLE:
            scenes = self._validate_and_improve_dialogue(scenes, voice_profiles)
        
        # Write each scene
        scene_ids = []
        for i, scene in enumerate(scenes, 1):
            scene_id = f"scene_{i:03d}"
            self._write_scene(
                scene_id=scene_id,
                content=scene["fountain"],
                frontmatter={
                    "scene_number": i,
                    "slugline": scene["slugline"],
                    "characters": scene["characters"],
                    "duration_estimate": scene["duration"],
                    "concept_id": "WINNER",
                    "voice_validated": scene.get("voice_validated", False),
                    "dialogue_score": scene.get("dialogue_score", 0.0),
                }
            )
            scene_ids.append(scene_id)
        
        return {
            "scenes_written": len(scenes),
            "scene_ids": scene_ids,
            "format": "fountain",
            "voice_profiles_used": len(voice_profiles),
            "skills_loaded": len(skills),
        }
    
    def _generate_briefs(self, task: ProductionTask) -> dict[str, Any]:
        """Generate scene briefs using the SceneBriefCompiler.
        
        This creates rich creative briefs for AI writers (Claude Code, Codex, Kimi)
        to write professional scenes from. The briefs are saved alongside templates.
        """
        if not BRIEF_COMPILER_AVAILABLE:
            return {"status": "error", "message": "SceneBriefCompiler not available"}
        
        production_id = task.inputs.get("production_id", "default")
        concept_id = task.inputs.get("concept_id", "WINNER")
        
        compiler = SceneBriefCompiler(obsidian_bridge=self.bridge)
        
        try:
            briefs = compiler.compile_briefs(concept_id=concept_id)
            paths = compiler.save_briefs(briefs, production_id=production_id)
            
            return {
                "status": "success",
                "briefs_generated": len(briefs),
                "production_id": production_id,
                "brief_paths": [str(p) for p in paths],
                "writer_packet": str(paths[-1]) if paths else None,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _parse_concept_note(self, note: ObsidianNote) -> dict[str, Any]:
        """Parse a concept note into structured data."""
        # Simple parsing from markdown
        content = note.content
        data = {
            "title": note.title,
            "characters": [],
            "structure": {}
        }
        
        # Extract character names
        char_pattern = r'###\s+(.+?)\s+\('
        data["characters"] = re.findall(char_pattern, content)
        
        # Extract act summaries
        for act in ["Act 1", "Act 2A", "Midpoint", "Act 2B", "Act 3"]:
            pattern = rf'###\s+{act}\s*\n(.+?)(?=###|\Z)'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                data["structure"][act.lower().replace(" ", "_")] = match.group(1).strip()
        
        return data
    
    def _load_voice_profiles(self) -> dict[str, Any]:
        """Load voice profiles from vault."""
        profiles = {}
        if not LANGUAGE_ENGINE_AVAILABLE:
            return profiles
        
        try:
            from system4.language_engine import LanguageEngine, VoiceProfile
            engine = LanguageEngine()
            
            # Look for voice profile notes
            voice_notes = self.bridge.query_notes(folder="characters")
            for note in voice_notes:
                if "_voice" in note.path:
                    fm = note.frontmatter
                    char_id = fm.get("character_id", "")
                    if char_id:
                        profile = VoiceProfile(
                            character_id=char_id,
                            character_name=fm.get("name", ""),
                            archetype=fm.get("archetype", ""),
                            sarcasm=fm.get("sarcasm", 50.0),
                            cynicism=fm.get("cynicism", 50.0),
                            warmth=fm.get("warmth", 50.0),
                            formality=fm.get("formality", 50.0),
                            verbosity=fm.get("verbosity", 50.0),
                            subtext=fm.get("subtext", 50.0),
                            vocabulary_level=fm.get("vocabulary_level", "moderate"),
                            sentence_structure=fm.get("sentence_structure", "mixed"),
                        )
                        profiles[profile.character_name] = profile
                        engine.voice_profiles[char_id] = profile
            
            return profiles
        except Exception as e:
            print(f"[Writer] Failed to load voice profiles: {e}")
            return {}
    
    def _load_skills(self) -> dict[str, str]:
        """Load craft skills from vault."""
        skills = {}
        skills_dir = Path(self.bridge.vault_path) / "skills"
        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.md"):
                skills[skill_file.stem] = skill_file.read_text(encoding="utf-8")
        return skills
    
    def _generate_scene_list(self, concept_data: dict,
                              voice_profiles: dict[str, Any] = None) -> list[dict]:
        """Generate 8 scenes mapping to Save the Cat beats with voice-aware dialogue."""
        scenes = []
        chars = concept_data["characters"]
        profiles = voice_profiles or {}
        structure = concept_data.get("structure", {})
        
        # Beat 1: Opening Image / Cold Open (action + comedy + tone)
        scenes.append({
            "slugline": "EXT. CITY — MORNING",
            "fountain": self._format_fountain_scene(
                "EXT. CITY — MORNING",
                structure.get("act_1", "The protagonist's world."),
                chars[:2],
                profiles,
                beat_type="opening"
            ),
            "characters": chars[:2],
            "duration": 120,
            "beat": "opening_image"
        })
        
        # Beat 2: Catalyst (inciting incident — visual, specific)
        scenes.append({
            "slugline": "INT. BUREAU — DAY",
            "fountain": self._format_fountain_scene(
                "INT. BUREAU — DAY",
                structure.get("act_1", "The discovery."),
                chars[:3],
                profiles,
                beat_type="catalyst"
            ),
            "characters": chars[:3],
            "duration": 180,
            "beat": "catalyst"
        })
        
        # Beat 3: Debate / B-Story Launch (relationship setup)
        scenes.append({
            "slugline": "INT. COUNSELING ROOM — DAY",
            "fountain": self._format_fountain_scene(
                "INT. COUNSELING ROOM — DAY",
                structure.get("act_2a", "Partnership formation."),
                chars[:2],
                profiles,
                beat_type="debate"
            ),
            "characters": chars[:2],
            "duration": 150,
            "beat": "debate"
        })
        
        # Beat 4: Fun & Games (comedy set piece, world-building)
        scenes.append({
            "slugline": "EXT. UNDERWORLD — NIGHT",
            "fountain": self._format_fountain_scene(
                "EXT. UNDERWORLD — NIGHT",
                structure.get("act_2a", "The investigation deepens."),
                chars[:3],
                profiles,
                beat_type="fun_games"
            ),
            "characters": chars[:3],
            "duration": 180,
            "beat": "fun_games"
        })
        
        # Beat 5: Midpoint (false victory + fracture)
        scenes.append({
            "slugline": "INT. HEADQUARTERS — NIGHT",
            "fountain": self._format_fountain_scene(
                "INT. HEADQUARTERS — NIGHT",
                structure.get("midpoint", "The partnership breaks."),
                chars,
                profiles,
                beat_type="midpoint"
            ),
            "characters": chars,
            "duration": 180,
            "beat": "midpoint"
        })
        
        # Beat 6: Bad Guys Close In (conspiracy deepens)
        scenes.append({
            "slugline": "INT. HIDEOUT — NIGHT",
            "fountain": self._format_fountain_scene(
                "INT. HIDEOUT — NIGHT",
                structure.get("act_2b", "The antagonist tightens control."),
                chars[:3],
                profiles,
                beat_type="bad_guys"
            ),
            "characters": chars[:3],
            "duration": 150,
            "beat": "bad_guys_close_in"
        })
        
        # Beat 7: All Is Lost / Dark Night (emotional death)
        scenes.append({
            "slugline": "INT. PRISON CELL — NIGHT",
            "fountain": self._format_fountain_scene(
                "INT. PRISON CELL — NIGHT",
                structure.get("act_2b", "Despair. The protagonist is alone."),
                chars[:2],
                profiles,
                beat_type="dark_night"
            ),
            "characters": chars[:2],
            "duration": 150,
            "beat": "dark_night"
        })
        
        # Beat 8: Finale (climax + emotional payoff)
        scenes.append({
            "slugline": "EXT. MONUMENT — DAWN",
            "fountain": self._format_fountain_scene(
                "EXT. MONUMENT — DAWN",
                structure.get("act_3", "The final confrontation."),
                chars,
                profiles,
                beat_type="finale"
            ),
            "characters": chars,
            "duration": 240,
            "beat": "finale"
        })
        
        return scenes
    
    def _format_fountain_scene(self, slugline: str, description: str,
                                characters: list[str],
                                voice_profiles: dict[str, Any] = None,
                                beat_type: str = "scene") -> str:
        """Format a scene in Fountain with voice-aware dialogue, visual gags, and parentheticals."""
        lines = [
            slugline,
            "",
        ]
        
        profiles = voice_profiles or {}
        
        # Add visual/action opening based on beat type
        action_openings = {
            "opening": [
                "TIGHT ON: A broken toy. A child's hand reaches for it.",
                "We see quick pops of morning routine — one character springs up, the other is slow.",
                "OVER BLACK: A typewriter clacks. A beat. Then silence.",
            ],
            "catalyst": [
                "A crate splits open. Eyes peer from the darkness inside.",
                "A document falls from a shelf, revealing a map no one was meant to see.",
                "The celebration continues overhead. Below, a wall cracks.",
            ],
            "debate": [
                "Two characters sit in mismatched chairs. One bounces. The other slouches.",
                "A sign reads: 'Partners in Crisis.' Neither character looks at each other.",
                "One character lists reasons on their fingers. The other checks their watch.",
            ],
            "fun_games": [
                "A disguise is revealed to be ridiculous — but effective.",
                "Chase sequence: they navigate a space that was built for someone twice their size.",
                "A misunderstanding becomes a performance. The audience doesn't know it's fake.",
            ],
            "midpoint": [
                "They celebrate. Glasses clink. But one character doesn't drink.",
                "A confession that should bring them together instead drives them apart.",
                "The truth is spoken. The room goes silent. Then: the door slams.",
            ],
            "bad_guys": [
                "Shadows on the wall. The antagonist's silhouette does something gentle — then cruel.",
                "A family photo on the antagonist's desk. They turn it face-down.",
                "The protagonist finds what they were looking for. It's worse than they imagined.",
            ],
            "dark_night": [
                "One character is trapped. The other is too far away to help.",
                "Rain on glass. The protagonist watches their reflection distort.",
                "A letter is read. The handwriting is familiar. The message is devastating.",
            ],
            "finale": [
                "The two groups face each other across a divide — physical and metaphorical.",
                "The antagonist holds the proof. The protagonist holds the truth.",
                "Dawn breaks. The monument stands. Two characters stand before it, transformed.",
            ],
        }
        
        openings = action_openings.get(beat_type, ["The scene begins."])
        lines.append(random.choice(openings))
        lines.append("")
        
        # Add description context
        if description and len(description) > 20:
            # Truncate to first sentence or 150 chars, whichever is shorter
            desc_text = description[:200].split(".")[0] + "."
            lines.append(desc_text)
            lines.append("")
        
        # Add voice-aware dialogue with visual business
        if len(characters) >= 2:
            char_a = characters[0]
            char_b = characters[1] if len(characters) > 1 else characters[0]
            profile_a = profiles.get(char_a)
            profile_b = profiles.get(char_b)
            
            # Generate a mini-exchange (3-6 lines) with parentheticals and visual business
            exchange = self._generate_dialogue_exchange(char_a, char_b, profile_a, profile_b, beat_type)
            lines.extend(exchange)
        
        # Add closing visual based on beat
        closings = {
            "opening": ["A camera flashes. SMASH TO TITLE.", "The door closes. We hold on the empty room.", "They walk away — in opposite directions."],
            "catalyst": ["The discovery is made. Nothing will be the same.", "A shadow falls across the map. Someone was watching.", "The alarm sounds. Too late."],
            "debate": ["They leave separately. The chairs remain askew.", "One looks back. The other doesn't.", "The sign creaks in the wind: 'Partners in Crisis.'"],
            "fun_games": ["They escape — but leave something important behind.", "The disguise falls off. They're exposed. But they got what they needed.", "Laughter echoes. Then: silence."],
            "midpoint": ["SMASH CUT TO BLACK. A door slams.", "The partnership is broken. The case continues alone.", "They walk away from each other. The space between them is the whole world."],
            "bad_guys": ["The trap closes. The protagonist doesn't see it yet.", "A phone rings. The caller ID says everything.", "The antagonist smiles. It's worse than a threat."],
            "dark_night": ["The light goes out. They're alone.", "A tear falls. They wipe it before anyone sees.", "Hope is gone. Only the truth remains — and it hurts."],
            "finale": ["They stand together. The city behind them is changed.", "The sun rises on a new world. They walk into it — together.", "SMASH TO: the empty monument. Then: two shadows appear."],
        }
        
        closing_pool = closings.get(beat_type, ["The scene ends."])
        lines.append(random.choice(closing_pool))
        lines.append("")
        lines.append("~FADE OUT.")
        return "\n".join(lines)
    
    def _generate_dialogue_exchange(self, char_a: str, char_b: str,
                                     profile_a: Optional[Any], profile_b: Optional[Any],
                                     beat_type: str) -> list[str]:
        """Generate a mini dialogue exchange (3-6 lines) with parentheticals and visual business."""
        lines = []
        
        # Get archetype hints from profiles
        arch_a = getattr(profile_a, 'archetype', 'generic') if profile_a else 'generic'
        arch_b = getattr(profile_b, 'archetype', 'generic') if profile_b else 'generic'
        
        # Generate exchange based on beat type and archetypes
        exchanges = self._get_exchange_pool(beat_type, arch_a, arch_b)
        chosen = random.choice(exchanges)
        
        for entry in chosen:
            speaker = entry.get("speaker", char_a)
            parenthetical = entry.get("parenthetical", "")
            line_text = entry.get("line", "...")
            action = entry.get("action", "")
            
            if action:
                lines.append(action)
            if parenthetical:
                lines.append(f"{speaker.upper()}")
                lines.append(f"({parenthetical})")
                lines.append(line_text)
            else:
                lines.append(f"{speaker.upper()}")
                lines.append(line_text)
            lines.append("")
        
        return lines
    
    def _get_exchange_pool(self, beat_type: str, arch_a: str, arch_b: str) -> list[list[dict]]:
        """Return pools of dialogue exchanges for different beat types."""
        
        # Helper: determine if archetype is cynical/trickster type
        is_cynical = lambda a: any(x in a.lower() for x in ["cynical", "trickster", "con-artist", "veteran", "survivor"])
        is_earnest = lambda a: any(x in a.lower() for x in ["earnest", "believer", "idealist", "reformer", "child"])
        is_villain = lambda a: any(x in a.lower() for x in ["villain", "tyrant", "schemer", "ruler", "bureaucrat"])
        
        # OPENING exchanges: establish voice, visual comedy
        opening_pools = [
            [
                {"speaker": "A", "line": "You know you're milking it."},
                {"speaker": "B", "action": "A adjusts posture. Straightens a tie. They're not the same size.", "line": "I mean, we're not that different."},
                {"speaker": "A", "parenthetical": "sotto", "line": "We really are."},
            ],
            [
                {"speaker": "A", "action": "A springs out of bed. B is slow.", "line": "We're gonna crack a new case, make the world a better place!"},
                {"speaker": "B", "action": "B brushes fur with a brush... then uses it to brush teeth.", "line": "And be the greatest partners of all time. Sure."},
            ],
            [
                {"speaker": "B", "action": "TIGHT ON: A broken toy. A child's hand reaches for it.", "line": "Blood, blood, blood and death..."},
                {"speaker": "A", "line": "Alright, you know you're milking it."},
            ],
        ]
        
        # CATALYST exchanges: discovery, specific visual
        catalyst_pools = [
            [
                {"speaker": "A", "parenthetical": "sotto", "line": "Are you sure this will work?"},
                {"speaker": "B", "line": "You're the one that said we needed a bust. Just follow my lead. Act casual."},
                {"speaker": "A", "action": "A hijacks the conversation, not subtle.", "line": "What do you do? Ensure that nothing illegal gets smuggled?"},
                {"speaker": "B", "action": "B looks at A like, 'that wasn't subtle.'", "line": "That's a weird way to ask that."},
            ],
            [
                {"speaker": "B", "action": "A crate splits open. Eyes peer from inside.", "line": "Reptile...?"},
                {"speaker": "A", "line": "Zootopia ain't just a mammal city. It has a secret tiny reptile population."},
                {"speaker": "B", "line": "Not sure 'Nibbles Maplestick' is our most reliable source."},
            ],
        ]
        
        # DEBATE exchanges: therapy, mismatch, humor masking fear
        debate_pools = [
            [
                {"speaker": "A", "line": "We are not dysfunctional at all. Functioning fine — better than fine!"},
                {"speaker": "B", "parenthetical": "poking A", "line": "Happy anniversary!"},
                {"speaker": "A", "line": "And we did sorta save the city, so us being here kinda seems like a huge misunderstanding."},
            ],
            [
                {"speaker": "B", "line": "Knock-knock? Hi, you know, this kinda sounds like a 'just-a you guys' conversation..."},
                {"speaker": "A", "action": "A is about to respond when B continues.", "line": "So what I'm going to do, is I'm gonna go ahead--"},
                {"speaker": "B", "action": "B starts to head for the door.", "line": "Is there a reason why you don't take anything seriously?"},
            ],
        ]
        
        # FUN & GAMES exchanges: chase, disguise, comedy set piece
        fun_games_pools = [
            [
                {"speaker": "B", "parenthetical": "really milking it", "line": "And you know the one thing this little stinker wished for? Was to see a choo-choo..."},
                {"speaker": "A", "action": "A leans down revealing the 'baby' is someone in a costume.", "line": "Toot toot."},
                {"speaker": "B", "line": "Oh, you are a saint. Here ya go, either leg... or both."},
            ],
            [
                {"speaker": "A", "line": "Stop! Stop in the name of the law!"},
                {"speaker": "B", "action": "A pig in a 'hog rod' honks aggressively.", "line": "Get outta the road, you dumb bunny!"},
                {"speaker": "A", "action": "A smiles at B.", "line": "Agree to disagree."},
            ],
        ]
        
        # MIDPOINT exchanges: false victory, then fracture
        midpoint_pools = [
            [
                {"speaker": "A", "line": "We did it. We actually did it."},
                {"speaker": "B", "line": "Told you. Teamwork makes the dream work."},
                {"speaker": "A", "action": "A's phone buzzes. They read it. Their face falls.", "line": "They lied to us. It's all a lie."},
                {"speaker": "B", "line": "What are you talking about?"},
                {"speaker": "A", "line": "You knew. You knew the whole time and you didn't tell me."},
            ],
            [
                {"speaker": "B", "line": "Not every case is going to save the world."},
                {"speaker": "A", "line": "This one does. This one has to."},
                {"speaker": "B", "line": "You can't save everyone, Carrots."},
                {"speaker": "A", "action": "A turns away.", "line": "Watch me."},
            ],
        ]
        
        # BAD GUYS exchanges: antagonist tightens control
        bad_guys_pools = [
            [
                {"speaker": "ANTAGONIST", "action": "The antagonist turns a family photo face-down.", "line": "You don't belong in this family. You will never belong."},
                {"speaker": "A", "line": "Wait! I wasn't working with them. I was helping us."},
                {"speaker": "ANTAGONIST", "line": "You want to keep your job, you say nothing."},
            ],
            [
                {"speaker": "ANTAGONIST", "parenthetical": "smiling, worse than a threat", "line": "Please don't be mad at me."},
                {"speaker": "A", "line": "You can be different than your family..."},
                {"speaker": "ANTAGONIST", "action": "A beat. Then:", "line": "I don't want to be different."},
            ],
        ]
        
        # DARK NIGHT exchanges: despair, vulnerability
        dark_night_pools = [
            [
                {"speaker": "A", "parenthetical": "desperate", "line": "I can't... move... and you're... too cold..."},
                {"speaker": "B", "parenthetical": "tiny, emotional", "line": "The world was never meant to be on one animal's shoulders."},
                {"speaker": "B", "line": "That's why my great grandma wanted Zootopia to be for everyone. So we could all help each other."},
                {"speaker": "A", "action": "A tears up, ashamed.", "line": "I didn't... help..."},
            ],
            [
                {"speaker": "B", "line": "Okay... I don't... care that we're different, you know. What I care about is you."},
                {"speaker": "B", "action": "B struggles to find words.", "line": "And I didn't say it, and I should have said it, but I didn't... because... well, because I am... an emotionally-insecure source of your discomfort..."},
                {"speaker": "A", "action": "A can't believe it.", "line": "I... do... try too hard because deep down I'm afraid that I am what everyone thinks I am..."},
            ],
        ]
        
        # FINALE exchanges: climax + emotional payoff
        finale_pools = [
            [
                {"speaker": "ANTAGONIST", "line": "It's not worth dying for."},
                {"speaker": "B", "action": "B considers this — an echo of the last thing they said before the split.", "line": "Agree... to disagree."},
                {"speaker": "A", "action": "A goes absolutely ham, knocking through obstacles.", "line": "It's called an arrest, sweetheart."},
                {"speaker": "B", "line": "Boom."},
            ],
            [
                {"speaker": "ANTAGONIST", "line": "No one will believe you over us. We've always been better than you."},
                {"speaker": "A", "action": "A looks to B, then to the ally they saved.", "line": "Well... it matters to him."},
                {"speaker": "B", "action": "B motions to the monument.", "line": "Shall we?"},
            ],
        ]
        
        # Default/generic pool
        default_pools = [
            [
                {"speaker": "A", "line": "We need to talk."},
                {"speaker": "B", "line": "About what?"},
                {"speaker": "A", "line": "About the truth. And who's really behind all this."},
            ],
        ]
        
        pools = {
            "opening": opening_pools,
            "catalyst": catalyst_pools,
            "debate": debate_pools,
            "fun_games": fun_games_pools,
            "midpoint": midpoint_pools,
            "bad_guys": bad_guys_pools,
            "dark_night": dark_night_pools,
            "finale": finale_pools,
        }
        
        return pools.get(beat_type, default_pools)
    
    def _generate_dialogue_line(self, character: str, profile: Optional[Any],
                                 context: str) -> str:
        """Generate a dialogue line matching the character's voice profile."""
        if not profile:
            defaults = {
                "opening": "We need to talk.",
                "response": "About what?",
                "revelation": "About the truth. And who's really behind all this.",
            }
            return defaults.get(context, "...")
        
        # Richer dialogue pools based on archetype + voice dimensions
        archetype = getattr(profile, 'archetype', 'generic').lower()
        
        # Archetype-specific dialogue pools
        cynical_trickster_lines = {
            "opening": [
                "Oh great. Just what I needed. Another conversation with you.",
                "Let me guess. You want to tell me everything's going to be fine.",
                "Jokes are a classic defense mechanism for someone with a traumatic childhood.",
                "Knock-knock? Hi, you know, this kinda sounds like a 'just-a you guys' conversation...",
            ],
            "response": [
                "Oh, this should be good. What did I do now?",
                "About what? How the world's falling apart? I'm aware.",
                "If I may, I think someone's just jealous.",
                "Sorry, could you show me that clip again, I wasn't wearing my glasses.",
            ],
            "revelation": [
                "About how everything we thought was true is actually worse. Surprise.",
                "About who benefits from all this chaos. And it's not us.",
                "Okay... I don't... care that we're different, you know. What I care about is you.",
                "I didn't join because I wanted to be a cop. I joined because I always wanted to be part of a pack.",
            ],
        }
        
        earnest_believer_lines = {
            "opening": [
                "Hey. I was hoping I'd run into you. We should talk.",
                "We're gonna crack a new case, make the world a better place!",
                "I must speak with you. It concerns a matter of some importance.",
                "Sir, today may not have been ideal but we made a significant discovery.",
            ],
            "response": [
                "Of course. What's on your mind?",
                "About what? How we can fix this? I'm ready.",
                "Article six, paragraph B states if the lead officers—",
                "We did sorta save the city, so this kinda seems like a huge misunderstanding.",
            ],
            "revelation": [
                "About the truth. And how we can still make things right. Together.",
                "I... do... try too hard because deep down I'm afraid that I am what everyone thinks I am.",
                "I make dangerous choices because I have an unhealthy hero complex.",
                "And no one else in the world matters to me more than you do either.",
            ],
        }
        
        meek_villain_lines = {
            "opening": [
                "Please don't be mad at me.",
                "I thought you knew. I thought you knew.",
                "Sorry partner... hate to leave you out in the cold...",
            ],
            "response": [
                "But you get it... we've always been on the same page...",
                "I know it's messed up, but this is my chance. I have to take it.",
                "'Cause when I get there... and I burn the original patent — I'll finally be something in my family.",
            ],
            "revelation": [
                "I'll destroy the patent, that town and everything in it!",
                "I don't want to be different.",
                "No one will believe you over us. We've always been better than you.",
            ],
        }
        
        frightened_outsider_lines = {
            "opening": [
                "Permission to... speak?",
                "Howdy partner.",
                "I know it's not much, but it's all I have.",
            ],
            "response": [
                "Of course. I mean... if you want to.",
                "I'm not sure I'm the right person for this.",
                "Permission to hug?",
            ],
            "revelation": [
                "The world was never meant to be on one animal's shoulders.",
                "We're going to save you... and save your friend.",
                "I know where the reptile neighborhood is buried.",
            ],
        }
        
        folksy_warrior_lines = {
            "opening": [
                "Takes a threesome to be sumpin'.",
                "Hey whiskers! You're done hurting muh city.",
                "Tides have turned —",
            ],
            "response": [
                "Uh-oh.",
                "Go! We got this!",
                "You wanna be a hero... or just play one on TV?",
            ],
            "revelation": [
                "Takes a threesome to be sumpin' — but a FOURWAY TO BUST YOUR DOORWAY!",
                "Now that is what we call, an overshare. I'm alive by the way.",
                "That'll do, pig. That'll do.",
            ],
        }
        
        # Select pool based on archetype
        if "cynical" in archetype or "trickster" in archetype or "con-artist" in archetype:
            pool = cynical_trickster_lines
        elif "earnest" in archetype or "believer" in archetype or "idealist" in archetype or "reformer" in archetype:
            pool = earnest_believer_lines
        elif "meek" in archetype or "villain" in archetype or "tyrant" in archetype or "schemer" in archetype:
            pool = meek_villain_lines
        elif "frightened" in archetype or "outsider" in archetype:
            pool = frightened_outsider_lines
        elif "folksy" in archetype or "warrior" in archetype:
            pool = folksy_warrior_lines
        else:
            # Fallback to voice dimensions
            pool = self._generic_dialogue_pool(profile)
        
        lines = pool.get(context, ["..."])
        return random.choice(lines)
    
    def _generic_dialogue_pool(self, profile: Any) -> dict[str, list[str]]:
        """Fallback dialogue pool based on voice dimensions."""
        if profile.sarcasm > 70:
            return {
                "opening": ["Oh great. Just what I needed.", "Let me guess. Everything's fine."],
                "response": ["Oh, this should be good.", "What did I do now?"],
                "revelation": ["About how everything is worse. Surprise.", "About who benefits. Not us."],
            }
        elif profile.cynicism > 70:
            return {
                "opening": ["Let me guess. You want to tell me everything's going to be fine."],
                "response": ["About what? How the world's falling apart? I'm aware."],
                "revelation": ["About who benefits from all this chaos. And it's not us."],
            }
        elif profile.warmth > 70:
            return {
                "opening": ["Hey. I was hoping I'd run into you. We should talk."],
                "response": ["Of course. What's on your mind?"],
                "revelation": ["About the truth. And how we can still make things right. Together."],
            }
        elif profile.formality > 70:
            return {
                "opening": ["I must speak with you. It concerns a matter of some importance."],
                "response": ["Very well. I am listening."],
                "revelation": ["About the truth. And the individual who has orchestrated these events."],
            }
        else:
            return {
                "opening": ["We need to talk."],
                "response": ["About what?"],
                "revelation": ["About the truth. And who's really behind all this."],
            }
    
    def _validate_and_improve_dialogue(self, scenes: list[dict],
                                        voice_profiles: dict[str, Any]) -> list[dict]:
        """Run Language Engine validation and improve dialogue."""
        if not LANGUAGE_ENGINE_AVAILABLE:
            return scenes
        
        try:
            from system4.language_engine import LanguageEngine
            from system3.evolution_engine import ScenePrototype
            engine = LanguageEngine()
            engine.voice_profiles.update({
                k.lower().replace(" ", "_"): v for k, v in voice_profiles.items()
            })
            
            for scene in scenes:
                # Parse dialogue from fountain format for validation
                # This is a simplified parser
                fountain_lines = scene["fountain"].split("\n")
                dialogue_entries = []
                current_speaker = None
                
                for line in fountain_lines:
                    line = line.strip()
                    if line.isupper() and len(line) > 1 and line not in ["EXT. CITY — DAY", "INT. HEADQUARTERS — DAY", "INT. ALLEY — NIGHT", "EXT. CEREMONY — NIGHT"]:
                        current_speaker = line.title()
                    elif current_speaker and line and not line.startswith("~"):
                        dialogue_entries.append({
                            "speaker": current_speaker,
                            "line": line
                        })
                        current_speaker = None
                
                # Create mock scene for analysis
                mock_scene = ScenePrototype(
                    scene_type="scene",
                    scene_number=1,
                    slugline=scene["slugline"],
                    description=scene["fountain"][:100],
                    dialogue=dialogue_entries,
                    action_beats=[],
                    emotional_valence=0.0,
                )
                
                # Analyze
                analysis = engine.analyze_screenplay([mock_scene])
                scene["dialogue_score"] = analysis.overall_voice_consistency
                scene["voice_validated"] = analysis.overall_voice_consistency > 0.5
                
                # If low score, flag for review
                if analysis.voice_violations:
                    violation_notes = []
                    for v in analysis.voice_violations[:2]:
                        note = f"<!-- VOICE NOTE: {v.speaker} — {v.issues[0] if v.issues else 'voice mismatch'} -->"
                        if v.rewrite:
                            note += f" Suggest: {v.rewrite[:50]}..."
                        violation_notes.append(note)
                    scene["fountain"] += "\n\n" + "\n".join(violation_notes)
        
        except Exception as e:
            print(f"[Writer] Dialogue validation failed: {e}")
        
        return scenes
    
    def _write_single_scene(self, task: ProductionTask) -> dict[str, Any]:
        """Write a single scene (for batch processing)."""
        scene_data = task.inputs.get("scene_data", {})
        scene_id = task.target
        
        self._write_scene(
            scene_id=scene_id,
            content=scene_data.get("fountain", "Scene content TBD"),
            frontmatter={
                "scene_number": scene_data.get("number", 0),
                "slugline": scene_data.get("slugline", ""),
                "characters": scene_data.get("characters", [])
            }
        )
        
        return {"scene_id": scene_id, "status": "written"}


# =============================================================================
# Visual Planner Agent
# =============================================================================

class VisualPlannerAgent(DepartmentAgent):
    """Generates shot lists for each scene.
    
    Reads scenes from Obsidian and creates shot lists with:
    - Shot size (WS, MS, CU, etc.)
    - Camera movement
    - Angle
    - Duration estimate
    - Key visual notes
    """
    
    def __init__(self, **kwargs):
        super().__init__("visual_planner", **kwargs)
        self.shots_per_scene_max = 12
    
    def execute_task(self, task: ProductionTask) -> dict[str, Any]:
        if task.task_type == "plan_shots":
            return self._plan_scene_shots(task)
        return {"status": "unknown_task_type"}
    
    def _plan_scene_shots(self, task: ProductionTask) -> dict[str, Any]:
        """Generate shot list for a scene."""
        scene_id = task.target
        scene_note = self.bridge.read_note(f"scenes/{scene_id}.md")
        
        if scene_note is None:
            raise ValueError(f"Scene not found: {scene_id}")
        
        slugline = scene_note.frontmatter.get("slugline", "SCENE")
        characters = scene_note.frontmatter.get("characters", [])
        
        # Generate shots based on scene type
        shots = self._generate_shots_for_scene(slugline, characters, scene_note.content)
        
        # Write shot list to vault
        shot_note = ObsidianNote(
            path=f"scenes/{scene_id}_shots.md",
            title=f"Shot List: {scene_id}",
            frontmatter={
                "scene_id": scene_id,
                "shot_count": len(shots),
                "total_duration_estimate": sum(s["duration"] for s in shots)
            },
            content=self._format_shot_list(shots),
            tags=["shots", "visual-plan"]
        )
        self.bridge.write_note(f"scenes/{scene_id}_shots.md", shot_note)
        
        return {
            "scene_id": scene_id,
            "shots_planned": len(shots),
            "total_duration": sum(s["duration"] for s in shots)
        }
    
    def _generate_shots_for_scene(self, slugline: str, characters: list[str],
                                   content: str) -> list[dict]:
        """Generate shots for a scene."""
        shots = []
        
        # Shot 1: Establishing
        shots.append({
            "number": 1,
            "size": "WS",
            "movement": "static",
            "angle": "eye level",
            "description": f"Establishing shot of {slugline}",
            "duration": 5,
            "characters": characters
        })
        
        # Shot 2: Character entrance
        if characters:
            shots.append({
                "number": 2,
                "size": "MS",
                "movement": "pan",
                "angle": "eye level",
                "description": f"{characters[0]} enters the scene",
                "duration": 4,
                "characters": [characters[0]]
            })
        
        # Shot 3: Two-shot
        if len(characters) >= 2:
            shots.append({
                "number": 3,
                "size": "2S",
                "movement": "static",
                "angle": "eye level",
                "description": f"{characters[0]} and {characters[1]} face each other",
                "duration": 6,
                "characters": characters[:2]
            })
        
        # Shot 4: Close-up protagonist
        if characters:
            shots.append({
                "number": 4,
                "size": "CU",
                "movement": "static",
                "angle": "slight low",
                "description": f"Close-up of {characters[0]} reacting",
                "duration": 3,
                "characters": [characters[0]]
            })
        
        # Shot 5: Over-shoulder
        if len(characters) >= 2:
            shots.append({
                "number": 5,
                "size": "OTS",
                "movement": "static",
                "angle": "eye level",
                "description": f"Over {characters[1]}'s shoulder at {characters[0]}",
                "duration": 4,
                "characters": characters[:2]
            })
        
        # Shot 6: Action/detail
        shots.append({
            "number": 6,
            "size": "ECU",
            "movement": "rack focus",
            "angle": "eye level",
            "description": "Key detail or prop",
            "duration": 2,
            "characters": []
        })
        
        return shots
    
    def _format_shot_list(self, shots: list[dict]) -> str:
        """Format shots as markdown."""
        lines = ["# Shot List", ""]
        for shot in shots:
            lines.extend([
                f"## Shot {shot['number']}: {shot['size']}",
                f"- **Movement**: {shot['movement']}",
                f"- **Angle**: {shot['angle']}",
                f"- **Duration**: {shot['duration']}s",
                f"- **Characters**: {', '.join(shot['characters']) or 'None'}",
                f"- **Description**: {shot['description']}",
                ""
            ])
        return "\n".join(lines)


# =============================================================================
# Character Agent
# =============================================================================

class CharacterAgent(DepartmentAgent):
    """Designs characters and manages consistency.
    
    - Generates concept art prompts
    - Registers characters with ConsistencyEngine
    - Creates character bibles
    """
    
    def __init__(self, **kwargs):
        super().__init__("character", **kwargs)
    
    def execute_task(self, task: ProductionTask) -> dict[str, Any]:
        if task.task_type == "design_characters":
            return self._design_characters(task)
        return {"status": "unknown_task_type"}
    
    def _design_characters(self, task: ProductionTask) -> dict[str, Any]:
        """Read concept and create character bibles with voice profiles."""
        concept_note = self._read_concept("WINNER")
        if concept_note is None:
            raise ValueError("No winning concept found")
        
        # Parse characters from concept
        char_data = self._parse_characters(concept_note)
        
        # Initialize Language Engine for voice profiling
        lang_engine = LanguageEngine() if LANGUAGE_ENGINE_AVAILABLE else None
        
        designed = []
        for char in char_data:
            char_id = f"char_{char['name'].lower().replace(' ', '_')}"
            
            # Generate voice profile
            voice_profile = None
            if lang_engine:
                voice_profile = lang_engine.create_voice_profile(
                    char_id,
                    char["name"],
                    char["archetype"],
                    char.get("starting_state", ""),
                    char.get("ending_state", "")
                )
            
            # Register with consistency engine
            if self.consistency_engine:
                self.consistency_engine.register_character(
                    char_id,
                    char["name"],
                    reference_image=None,  # Would be generated by image tool
                    base_description=char["description"]
                )
            
            # Write character bible
            bible = ObsidianNote(
                path=f"characters/{char_id}.md",
                title=f"Character Bible: {char['name']}",
                frontmatter={
                    "character_id": char_id,
                    "name": char["name"],
                    "archetype": char["archetype"],
                    "role": char["role"]
                },
                content=self._format_character_bible(char, voice_profile),
                tags=["character", "bible"]
            )
            self.bridge.write_note(f"characters/{char_id}.md", bible)
            
            # Also write voice profile as separate note for easy lookup
            if voice_profile:
                voice_note = ObsidianNote(
                    path=f"characters/{char_id}_voice.md",
                    title=f"Voice Profile: {char['name']}",
                    frontmatter={
                        "character_id": char_id,
                        "name": char["name"],
                        "archetype": char["archetype"],
                        "sarcasm": voice_profile.sarcasm,
                        "cynicism": voice_profile.cynicism,
                        "warmth": voice_profile.warmth,
                        "formality": voice_profile.formality,
                        "verbosity": voice_profile.verbosity,
                        "subtext": voice_profile.subtext,
                        "vocabulary_level": voice_profile.vocabulary_level,
                        "sentence_structure": voice_profile.sentence_structure,
                    },
                    content=voice_profile.get_description() + "\n\n## Signature Phrases\n" +
                           "\n".join(f"- {p}" for p in voice_profile.signature_phrases) +
                           "\n\n## Forbidden Phrases\n" +
                           "\n".join(f"- {p}" for p in voice_profile.forbidden_phrases),
                    tags=["voice-profile", "character"]
                )
                self.bridge.write_note(f"characters/{char_id}_voice.md", voice_note)
            
            designed.append(char_id)
        
        return {
            "characters_designed": len(designed),
            "character_ids": designed
        }
    
    def _parse_characters(self, concept_note: ObsidianNote) -> list[dict]:
        """Parse character sections from concept note."""
        chars = []
        content = concept_note.content
        
        # Find character sections
        pattern = r'###\s+(.+?)\s+\((.+?)\)\s*\n(.+?)(?=###|\Z)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            name, archetype, details = match
            chars.append({
                "name": name.strip(),
                "archetype": archetype.strip(),
                "description": details.strip()[:200],
                "role": "protagonist" if "protagonist" in details.lower() else "supporting"
            })
        
        return chars
    
    def _format_character_bible(self, char: dict, voice_profile: Optional[Any] = None) -> str:
        """Format character bible content with voice profile."""
        if voice_profile:
            voice_section = f"""## Voice Profile
{voice_profile.get_description()}

### Dimensions
| Dimension | Score | Description |
|-----------|-------|-------------|
| Sarcasm | {voice_profile.sarcasm:.0f}/100 | {'Highly sarcastic' if voice_profile.sarcasm > 70 else 'Earnest' if voice_profile.sarcasm < 30 else 'Balanced'} |
| Cynicism | {voice_profile.cynicism:.0f}/100 | {'Deeply cynical' if voice_profile.cynicism > 70 else 'Optimistic' if voice_profile.cynicism < 30 else 'Balanced'} |
| Warmth | {voice_profile.warmth:.0f}/100 | {'Warm' if voice_profile.warmth > 70 else 'Cold' if voice_profile.warmth < 30 else 'Balanced'} |
| Formality | {voice_profile.formality:.0f}/100 | {'Formal' if voice_profile.formality > 70 else 'Colloquial' if voice_profile.formality < 30 else 'Balanced'} |
| Verbosity | {voice_profile.verbosity:.0f}/100 | {'Verbose' if voice_profile.verbosity > 70 else 'Terse' if voice_profile.verbosity < 30 else 'Balanced'} |
| Subtext | {voice_profile.subtext:.0f}/100 | {'Subtext-heavy' if voice_profile.subtext > 70 else 'Direct' if voice_profile.subtext < 30 else 'Balanced'} |

### Signature Phrases
{chr(10).join(f"- '{p}'" for p in voice_profile.signature_phrases) if voice_profile.signature_phrases else '- TBD'}

### Forbidden Phrases
{chr(10).join(f"- '{p}'" for p in voice_profile.forbidden_phrases) if voice_profile.forbidden_phrases else '- TBD'}
"""
        else:
            voice_section = """## Voice Profile
- **Tone**: TBD
- **Speech Pattern**: TBD
- **Signature Phrases**: TBD
"""
        
        return f"""# {char['name']}

## Archetype
{char['archetype']}

## Physical Description
{char['description']}

## Role
{char['role']}

## Concept Art Prompt
{char['name']}, {char['archetype']}, character design sheet, front view, side view, 
back view, expression sheet, color palette, animation-ready, clean lines, 
professional concept art.

{voice_section}

## Animation Notes
- **Movement Style**: TBD
- **Key Poses**: TBD
- **Prop Interactions**: TBD
"""


# =============================================================================
# World Builder Agent
# =============================================================================

class WorldBuilderAgent(DepartmentAgent):
    """Designs environments and sets for the production."""
    
    def __init__(self, **kwargs):
        super().__init__("world_builder", **kwargs)
    
    def execute_task(self, task: ProductionTask) -> dict[str, Any]:
        if task.task_type == "build_environments":
            return self._build_environments(task)
        return {"status": "unknown_task_type"}
    
    def _build_environments(self, task: ProductionTask) -> dict[str, Any]:
        """Create environment catalog from concept."""
        concept_note = self._read_concept("WINNER")
        if concept_note is None:
            raise ValueError("No winning concept found")
        
        # Extract setting
        setting_match = re.search(r'\*\*Setting\*\*:\s*(.+)', concept_note.content)
        setting = setting_match.group(1).strip() if setting_match else "Unknown setting"
        
        environments = [
            {"name": "Main City", "type": "exterior", "description": setting},
            {"name": "Headquarters", "type": "interior", "description": "Main command center"},
            {"name": "Alley", "type": "exterior", "description": "Back alley for secret meetings"},
            {"name": "Ceremony Hall", "type": "interior", "description": "Grand hall for climax"}
        ]
        
        env_ids = []
        for env in environments:
            env_id = f"env_{env['name'].lower().replace(' ', '_')}"
            note = ObsidianNote(
                path=f"characters/environments/{env_id}.md",
                title=f"Environment: {env['name']}",
                frontmatter={
                    "env_id": env_id,
                    "type": env["type"],
                    "name": env["name"]
                },
                content=self._format_environment(env),
                tags=["environment", "world"]
            )
            self.bridge.write_note(f"characters/environments/{env_id}.md", note)
            env_ids.append(env_id)
        
        return {
            "environments_created": len(env_ids),
            "env_ids": env_ids
        }
    
    def _format_environment(self, env: dict) -> str:
        return f"""# {env['name']}

## Type
{env['type'].title()}

## Description
{env['description']}

## Concept Art Prompt
{env['description']}, environment concept art, matte painting style, 
cinematic lighting, wide angle, detailed, atmospheric, production-ready.

## Lighting Scheme
- **Primary**: TBD
- **Secondary**: TBD
- **Mood**: TBD

## Key Elements
- TBD

## References
- TBD
"""


# =============================================================================
# Animation Agent
# =============================================================================

class AnimationAgent(DepartmentAgent):
    """Generates video clips for shots.
    
    Uses OpenMontage video generation tools with consistency injection.
    """
    
    def __init__(self, **kwargs):
        super().__init__("animation", **kwargs)
    
    def execute_task(self, task: ProductionTask) -> dict[str, Any]:
        if task.task_type == "animate_shot":
            return self._animate_shot(task)
        elif task.task_type == "animate_scene":
            return self._animate_scene(task)
        return {"status": "unknown_task_type"}
    
    def _animate_shot(self, task: ProductionTask) -> dict[str, Any]:
        """Generate a single shot animation."""
        shot_data = task.inputs.get("shot", {})
        
        # Build prompt from shot data
        prompt = shot_data.get("description", "A cinematic shot")
        
        # Inject consistency if available
        if self.consistency_engine and shot_data.get("characters"):
            char_ids = shot_data.get("characters", [])
            # Map character names to IDs
            # (simplified — would need proper mapping)
            payload = self.consistency_engine.compile_scene_payload(
                prompt, character_ids=[]  # Would map names to IDs
            )
            prompt = payload["final_prompt"]
        
        # Try to generate via OpenMontage
        result = self.om.generate_video(
            prompt=prompt,
            duration=shot_data.get("duration", 5),
            aspect_ratio="16:9"
        )
        
        return {
            "shot_id": task.target,
            "generated": result.success,
            "video_path": result.artifacts[0] if result.artifacts else None,
            "cost": result.cost_usd
        }
    
    def _animate_scene(self, task: ProductionTask) -> dict[str, Any]:
        """Generate all shots for a scene."""
        scene_id = task.target
        shot_list_note = self.bridge.read_note(f"scenes/{scene_id}_shots.md")
        
        if shot_list_note is None:
            raise ValueError(f"Shot list not found for {scene_id}")
        
        # In real implementation, would parse shots and generate each
        # For now, return placeholder
        return {
            "scene_id": scene_id,
            "shots_generated": 0,
            "note": "Shot list found. Would generate video per shot with OpenMontage tools."
        }


# =============================================================================
# Sound Agent
# =============================================================================

class SoundAgent(DepartmentAgent):
    """Generates dialogue, music, and sound effects."""
    
    def __init__(self, **kwargs):
        super().__init__("sound", **kwargs)
    
    def execute_task(self, task: ProductionTask) -> dict[str, Any]:
        if task.task_type == "generate_dialogue_audio":
            return self._generate_dialogue(task)
        elif task.task_type == "generate_music":
            return self._generate_music(task)
        return {"status": "unknown_task_type"}
    
    def _generate_dialogue(self, task: ProductionTask) -> dict[str, Any]:
        """Generate TTS for dialogue lines."""
        lines = task.inputs.get("dialogue_lines", [])
        generated = []
        
        for line in lines:
            result = self.om.generate_audio(
                text=line["text"],
                voice_id=line.get("voice_id")
            )
            generated.append({
                "speaker": line.get("speaker"),
                "success": result.success,
                "audio_path": result.artifacts[0] if result.artifacts else None
            })
        
        return {
            "lines_generated": len(generated),
            "details": generated
        }
    
    def _generate_music(self, task: ProductionTask) -> dict[str, Any]:
        """Generate music for a scene."""
        scene_mood = task.inputs.get("mood", "neutral")
        
        result = self.om.generate_music(
            prompt=f"Cinematic score, {scene_mood}, emotional, orchestral",
            duration=task.inputs.get("duration", 30)
        )
        
        return {
            "generated": result.success,
            "music_path": result.artifacts[0] if result.artifacts else None,
            "mood": scene_mood
        }


# =============================================================================
# Editorial Agent
# =============================================================================

class EditorialAgent(DepartmentAgent):
    """Assembles final cut from all generated clips."""
    
    def __init__(self, **kwargs):
        super().__init__("editorial", **kwargs)
    
    def execute_task(self, task: ProductionTask) -> dict[str, Any]:
        if task.task_type == "assemble_cut":
            return self._assemble_cut(task)
        return {"status": "unknown_task_type"}
    
    def _assemble_cut(self, task: ProductionTask) -> dict[str, Any]:
        """Assemble final video from all scene clips."""
        # In real implementation, would use video_compose tool
        return {
            "assembled": True,
            "output_path": "studio/assets/video/final_cut.mp4",
            "note": "Would compose all scene clips with transitions"
        }


# =============================================================================
# Swarm Orchestrator
# =============================================================================

class ProductionSwarm:
    """Manages all department agents and their task queue.
    
    Creates tasks from the winning concept, assigns to departments,
    and runs the swarm until all tasks are complete.
    """
    
    def __init__(self, 
                 obsidian_bridge: Optional[ObsidianBridge] = None,
                 om_bridge: Optional[OpenMontageBridge] = None):
        self.bridge = obsidian_bridge or get_bridge()
        self.om = om_bridge or get_om_bridge()
        
        self.queue = TaskQueue()
        self.agents: dict[str, DepartmentAgent] = {}
        
        # Shared resources
        self.consistency_engine = ConsistencyEnginePy()
        self.collaboration_hub = CollaborationHubPy()
        
        # Initialize agents
        self._init_agents()
    
    def _init_agents(self) -> None:
        """Create and configure all department agents."""
        agent_classes = [
            WriterAgent,
            VisualPlannerAgent,
            CharacterAgent,
            WorldBuilderAgent,
            AnimationAgent,
            SoundAgent,
            EditorialAgent
        ]
        
        for AgentClass in agent_classes:
            agent = AgentClass(
                obsidian_bridge=self.bridge,
                om_bridge=self.om
            )
            agent.attach_queue(self.queue)
            agent.attach_consistency_engine(self.consistency_engine)
            agent.attach_collaboration_hub(self.collaboration_hub)
            self.agents[agent.name] = agent
    
    def create_production_tasks(self, winning_concept: Any) -> None:
        """Create all production tasks from the winning concept."""
        tasks = []
        
        # Phase 1: Pre-production
        tasks.append(ProductionTask(
            id="task-write-screenplay",
            department="writer",
            task_type="write_screenplay",
            target="WINNER",
            priority=1
        ))
        
        tasks.append(ProductionTask(
            id="task-design-characters",
            department="character",
            task_type="design_characters",
            target="WINNER",
            priority=1
        ))
        
        tasks.append(ProductionTask(
            id="task-build-worlds",
            department="world_builder",
            task_type="build_environments",
            target="WINNER",
            priority=2
        ))
        
        # Phase 2: Production (depends on screenplay)
        for i in range(1, 6):  # 5 scenes
            tasks.append(ProductionTask(
                id=f"task-plan-shots-scene{i:03d}",
                department="visual_planner",
                task_type="plan_shots",
                target=f"scene_{i:03d}",
                dependencies=["task-write-screenplay"],
                priority=3
            ))
        
        # Phase 3: Post-production (depends on shots)
        tasks.append(ProductionTask(
            id="task-assemble-cut",
            department="editorial",
            task_type="assemble_cut",
            target="final",
            dependencies=[f"task-plan-shots-scene{i:03d}" for i in range(1, 6)],
            priority=5
        ))
        
        self.queue.add_tasks(tasks)
        print(f"[Swarm] Created {len(tasks)} production tasks")
    
    def run(self, max_iterations: int = 50) -> dict[str, Any]:
        """Run the swarm until all tasks complete or max iterations reached.
        
        Returns production statistics.
        """
        print(f"\n{'='*60}")
        print("  PARALLEL PRODUCTION SWARM — Starting Run")
        print(f"{'='*60}\n")
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # Check if done
            stats = self.queue.get_stats()
            if stats["pending"] == 0 and stats["in_progress"] == 0 and stats["blocked"] == 0:
                print(f"\n[Swarm] All tasks completed in {iteration} iterations")
                break
            
            # Run each agent
            any_work_done = False
            for name, agent in self.agents.items():
                completed = agent.claim_and_work()
                if completed:
                    any_work_done = True
            
            if not any_work_done and stats["pending"] == 0:
                # No work possible and nothing pending — done or blocked
                if stats["blocked"] == 0:
                    break
                else:
                    print(f"[Swarm] Warning: {stats['blocked']} tasks blocked by unresolved dependencies")
                    break
        
        # Final stats
        final_stats = self.queue.get_stats()
        print(f"\n[Swarm] Final stats: {final_stats}")
        
        return {
            "iterations": iteration,
            **final_stats,
            "agents": list(self.agents.keys())
        }


# =============================================================================
# CLI / Test
# =============================================================================

if __name__ == "__main__":
    # Test the production swarm with a mock winning concept
    swarm = ProductionSwarm()
    
    # Create tasks (would normally use real concept)
    swarm.create_production_tasks(None)
    
    # Run swarm
    results = swarm.run()
    
    print("\nProduction Results:")
    print(json.dumps(results, indent=2))
