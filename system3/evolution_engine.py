"""Story Evolution Engine — The Core of System 3.

Implements the generate → prototype → critic → select → iterate loop
that mirrors how real animation studios develop stories through
competing concepts and selection pressure.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Bridges
import sys
bridge_dir = Path(__file__).resolve().parent.parent / "bridge"
if str(bridge_dir) not in sys.path:
    sys.path.insert(0, str(bridge_dir))

from obsidian_bridge import ObsidianBridge, ObsidianNote, get_bridge
from platform_bridge import CollaborationHubPy

# System 4: Pattern Recognition (replaces heuristic critics)
system4_dir = Path(__file__).resolve().parent.parent / "system4"
if str(system4_dir) not in sys.path:
    sys.path.insert(0, str(system4_dir))
try:
    from pattern_recognition import PatternRecognizer, PatternScore
    PATTERN_RECOGNITION_AVAILABLE = True
except ImportError:
    PATTERN_RECOGNITION_AVAILABLE = False


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class CharacterArc:
    """Character arc definition for a concept."""
    name: str
    archetype: str
    starting_state: str
    ending_state: str
    key_transformation: str
    core_wound: Optional[str] = None


@dataclass
class Concept:
    """A competing story concept."""
    id: str
    title: str
    logline: str
    genre: str
    setting: str
    theme: str
    social_metaphor: str
    
    # 3-act structure
    act1_summary: str = ""
    act2a_summary: str = ""
    midpoint: str = ""
    act2b_summary: str = ""
    act3_summary: str = ""
    
    # Characters
    protagonist: Optional[CharacterArc] = None
    deuteragonist: Optional[CharacterArc] = None
    antagonist: Optional[CharacterArc] = None
    supporting: list[CharacterArc] = field(default_factory=list)
    
    # Metadata
    round_num: int = 1
    parent_concept_id: Optional[str] = None
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_markdown(self) -> str:
        """Convert to Obsidian markdown note."""
        lines = [
            "# Concept: " + self.title,
            "",
            f"**Logline**: {self.logline}",
            f"**Genre**: {self.genre}",
            f"**Setting**: {self.setting}",
            f"**Theme**: {self.theme}",
            f"**Social Metaphor**: {self.social_metaphor}",
            "",
            "## Characters",
        ]
        
        for char in [self.protagonist, self.deuteragonist, self.antagonist] + self.supporting:
            if char:
                lines.extend([
                    f"### {char.name} ({char.archetype})",
                    f"- **Start**: {char.starting_state}",
                    f"- **End**: {char.ending_state}",
                    f"- **Transformation**: {char.key_transformation}",
                ])
                if char.core_wound:
                    lines.append(f"- **Core Wound**: {char.core_wound}")
                lines.append("")
        
        lines.extend([
            "## Structure",
            f"### Act 1\n{self.act1_summary}",
            f"### Act 2A\n{self.act2a_summary}",
            f"### Midpoint\n{self.midpoint}",
            f"### Act 2B\n{self.act2b_summary}",
            f"### Act 3\n{self.act3_summary}",
        ])
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to plain dict for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "logline": self.logline,
            "genre": self.genre,
            "setting": self.setting,
            "theme": self.theme,
            "social_metaphor": self.social_metaphor,
            "act1": self.act1_summary,
            "act2a": self.act2a_summary,
            "midpoint": self.midpoint,
            "act2b": self.act2b_summary,
            "act3": self.act3_summary,
            "characters": [
                {
                    "name": c.name,
                    "archetype": c.archetype,
                    "start": c.starting_state,
                    "end": c.ending_state,
                    "transformation": c.key_transformation,
                    "wound": c.core_wound
                }
                for c in [self.protagonist, self.deuteragonist, self.antagonist] + self.supporting
                if c
            ],
            "round": self.round_num,
            "parent": self.parent_concept_id,
            "generated_at": self.generated_at
        }


@dataclass
class ScenePrototype:
    """A prototyped scene (text + metadata, not actual rendered media yet)."""
    scene_type: str  # "hook", "midpoint", "climax"
    scene_number: int
    slugline: str
    description: str
    dialogue: list[dict] = field(default_factory=list)
    action_beats: list[str] = field(default_factory=list)
    emotional_valence: float = 0.0  # -1.0 to +1.0
    estimated_duration_seconds: int = 120
    key_characters: list[str] = field(default_factory=list)
    visual_notes: str = ""


@dataclass
class Prototype:
    """A full prototype package for a concept (3 key scenes)."""
    concept_id: str
    concept_title: str
    scenes: list[ScenePrototype] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_scene_by_type(self, scene_type: str) -> Optional[ScenePrototype]:
        for s in self.scenes:
            if s.scene_type == scene_type:
                return s
        return None


@dataclass
class CriticScore:
    """Score from a single critic agent."""
    critic_name: str
    category: str  # structure, emotion, pacing, theme
    score: float  # 0.0 to 10.0
    notes: str
    specific_issues: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    
    def is_passing(self, threshold: float = 5.0) -> bool:
        return self.score >= threshold


@dataclass
class Evaluation:
    """Full evaluation of a prototype by the critic swarm."""
    prototype: Prototype
    scores: list[CriticScore] = field(default_factory=list)
    weighted_total: float = 0.0
    combined_score: float = 0.0
    
    def get_score_by_category(self, category: str) -> Optional[CriticScore]:
        for s in self.scores:
            if s.category == category:
                return s
        return None
    
    def get_all_issues(self) -> list[str]:
        issues = []
        for s in self.scores:
            issues.extend(s.specific_issues)
        return issues
    
    def get_all_strengths(self) -> list[str]:
        strengths = []
        for s in self.scores:
            strengths.extend(s.strengths)
        return strengths


# =============================================================================
# Concept Generator
# =============================================================================

class ConceptGenerator:
    """Generates N competing story concepts from Creative DNA + user constraints.
    
    Uses the DNA as a structural template and applies constraint-driven
    transformations to create differentiated variants.
    """
    
    # Expanded template pools for high-variation concept generation
    # Each template includes narrative specificity, not just keyword swaps
    SETTING_TEMPLATES = [
        "a {group_a} neighborhood where old {group_b} stories still echo in the architecture",
        "a borderland where {group_a} and {group_b} territories meet under a shared sky",
        "a forgotten district buried beneath the {group_a} city, where {group_b} history sleeps",
        "a traveling carnival that moves between {group_a} and {group_b} lands",
        "a coastal port where {group_a} fishermen and {group_b} traders negotiate daily",
        "a mountain observatory where {group_a} scholars study {group_b} artifacts",
        "a subterranean library where {group_a} and {group_b} knowledge is stored separately",
        "a war-torn village rebuilding with {group_a} hands and {group_b} memories",
        "a grand hotel where {group_a} and {group_b} guests pretend equality",
        "a factory floor where {group_a} managers oversee {group_b} workers",
        "a hospital ward where {group_a} doctors treat {group_b} patients in secret",
        "a train line connecting {group_a} capital to {group_b} outlands",
    ]
    
    CONFLICT_TEMPLATES = [
        "{protagonist} discovers that {group_b} history has been systematically erased by {group_a} authorities, and the proof lies in a buried neighborhood",
        "{protagonist} is assigned to work with a {group_b} partner they distrust, but the partnership reveals a conspiracy against both groups",
        "A {group_a} celebration covers up the truth: {group_b}s built the city walls that keep them out, and {protagonist} holds the original patent",
        "{protagonist}'s mother falls ill, and the only cure requires crossing into {group_b} territory — where {group_b} fairy tales come alive to help",
        "{protagonist} uncovers that the {institution} they serve was founded on stolen {group_b} labor, and exposing it means betraying their own family",
        "When {group_b} artifacts begin awakening in {group_a} homes, {protagonist} must convince both sides that the stories are real — and dangerous",
        "{protagonist} is the first {group_a} to believe {group_b} legends. Their faith summons {group_b} allies, but also awakens a buried threat",
        "A {group_a} child befriends a {group_b} outcast. Their bond reveals that the border between {group_a} and {group_b} was built on a lie",
        "{protagonist} must smuggle {group_b} refugees through {group_a} territory, using {group_b} stories as disguises and passwords",
        "The {institution} claims {group_b}s are extinct. {protagonist} finds one living in the walls — and the {group_b} holds the key to the city's survival",
    ]
    
    # Archetypes now include specific emotional mechanics and relationship dynamics
    CHARACTER_ARCHETYPES = [
        # (protagonist, deuteragonist, antagonist, relationship_mechanic)
        ("earnest believer", "cynical trickster", "meek villain", "humor_as_armor"),
        ("frightened outsider", "folksy warrior", "hidden tyrant", "size_contrast"),
        ("determined reformer", "apathetic con-artist", "ambitious schemer", "motivation_vs_cynicism"),
        ("naive idealist", "wounded veteran", "corrupt bureaucrat", "innocence_vs_experience"),
        ("curious explorer", "jaded survivor", "manipulative advisor", "wonder_vs_cynicism"),
        ("optimistic underdog", "reluctant mentor", "charismatic demagogue", "student_teacher_inversion"),
        ("earnest child", "foreign fairy-tale ally", "paranoid ruler", "innocence_summons_magic"),
        ("ambitious outsider", "gruff protector", "family_legacy_villain", "belonging_vs_birthright"),
    ]
    
    # Richer name pools with cultural and thematic variety
    NAME_POOLS = {
        "predator": ["Leo", "Fang", "Shadow", "Rex", "Claw", "Stripe", "Onyx", "Blaze", "Storm", "Griff"],
        "prey": ["Dawn", "Clover", "Swift", "Bramble", "Pip", "Cotton", "Willow", "Poppy", "Finch", "Hazel"],
        "robot": ["Unit-7", "Bolt", "Spark", "Gear", "Cipher", "Relay", "Axis", "Vector", "Pulse", "Cog"],
        "human": ["Alex", "Jordan", "Casey", "Morgan", "Riley", "Quinn", "Taylor", "Jamie", "Avery", "Sam"],
        "alien": ["Zyx", "Kthar", "Nyx", "Vorin", "Lum", "Zara", "Qel", "Thren", "Vex", "Ool"],
        "spirit": ["Aura", "Wisp", "Shade", "Prism", "Echo", "Flicker", "Glimmer", "Mist", "Sol", "Luna"],
        "default_male": ["Nick", "Gary", "Pawbert", "Milton", "Brian", "Stu", "Jesús", "Finnick", "Clawhauser", "Bogo"],
        "default_female": ["Judy", "Nibbles", "Bellwether", "Fabienne", "Gazelle", "Dawn", "Bonnie", "Fru Fru", "Koslov", "Yax"],
        "child": ["Anya", "Misha", "Sasha", "Katya", "Olya", "Petro", "Ivan", "Nadia", "Zoya", "Boris"],
    }
    
    def __init__(self, obsidian_bridge: Optional[ObsidianBridge] = None):
        self.bridge = obsidian_bridge or get_bridge()
        self.generated_concepts: list[Concept] = []
    
    def load_dna(self, dna_source: str = "memory/films_analyzed/zootopia_dna.md") -> dict[str, Any]:
        """Load Creative DNA from the vault with rich parsing for beats and archetypes."""
        note = self.bridge.read_note(dna_source)
        if note is None:
            raise FileNotFoundError(f"DNA not found: {dna_source}")
        
        dna = {
            "source_film": note.frontmatter.get("source_film", "Unknown"),
            "dna_version": note.frontmatter.get("dna_version", "1.0"),
        }
        
        content = note.content
        lines = content.split("\n")
        
        # Parse hierarchical structure: ## Section -> ### Subsection -> content
        current_section = None
        current_subsection = None
        section_data: dict[str, Any] = {}
        subsection_data: list[str] = []
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith("## "):
                # Save previous subsection
                if current_section and current_subsection and subsection_data:
                    if current_section not in section_data:
                        section_data[current_section] = {}
                    section_data[current_section][current_subsection] = subsection_data
                # Save previous section's subsections
                elif current_section and subsection_data and not current_subsection:
                    if current_section not in section_data:
                        section_data[current_section] = []
                    section_data[current_section].extend(subsection_data)
                
                current_section = stripped[3:].strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_")
                current_subsection = None
                subsection_data = []
                
            elif stripped.startswith("### "):
                # Save previous subsection
                if current_section and current_subsection and subsection_data:
                    if current_section not in section_data:
                        section_data[current_section] = {}
                    section_data[current_section][current_subsection] = subsection_data
                elif current_section and not current_subsection and subsection_data:
                    if current_section not in section_data:
                        section_data[current_section] = []
                    section_data[current_section].extend(subsection_data)
                
                current_subsection = stripped[4:].strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "_")
                subsection_data = []
                
            elif stripped.startswith("- ") or stripped.startswith("* "):
                item = stripped[2:].strip()
                if item:
                    subsection_data.append(item)
            elif stripped and not stripped.startswith("#") and current_section:
                # Non-list content under a section
                if stripped:
                    subsection_data.append(stripped)
        
        # Save final subsection
        if current_section and current_subsection and subsection_data:
            if current_section not in section_data:
                section_data[current_section] = {}
            section_data[current_section][current_subsection] = subsection_data
        elif current_section and subsection_data:
            if current_section not in section_data:
                section_data[current_section] = []
            section_data[current_section].extend(subsection_data)
        
        dna["sections"] = section_data
        
        # Flatten for backward compatibility
        for section_name, data in section_data.items():
            if isinstance(data, list):
                dna[section_name] = data
            elif isinstance(data, dict):
                # For dict sections, concatenate all subsections
                flattened = []
                for sub_name, items in data.items():
                    if isinstance(items, list):
                        flattened.extend(items)
                dna[section_name] = flattened
        
        # Extract specific beats if available
        story_structure = section_data.get("story_structure_save_the_cat___animation_mechanics", {})
        if story_structure:
            dna["story_structure"] = []
            for beat_name, beat_content in story_structure.items():
                dna["story_structure"].append({
                    "beat": beat_name,
                    "content": " ".join(beat_content)
                })
        
        # Extract character archetypes if available
        char_section = section_data.get("character_archetypes", {})
        if char_section:
            dna["character_archetypes"] = []
            for char_name, char_content in char_section.items():
                dna["character_archetypes"].append({
                    "name": char_name,
                    "content": " ".join(char_content)
                })
        
        return dna
    
    def generate(self, dna_source: str, constraints: dict[str, str],
                 n_concepts: int = 6, round_num: int = 1,
                 parent_concept_id: Optional[str] = None) -> list[Concept]:
        """Generate N competing concepts from DNA + constraints.
        
        Args:
            dna_source: Path to DNA file in vault
            constraints: Dict with keys like 'setting', 'protagonist_type', 
                        'social_metaphor', 'differentiation_seed'
            n_concepts: Number of concepts to generate
            round_num: Which evolution round this is
            parent_concept_id: If iterating, the parent concept ID
            
        Returns:
            List of Concept objects
        """
        dna = self.load_dna(dna_source)
        concepts = []
        
        for i in range(n_concepts):
            concept_id = f"concept-{round_num}-{chr(65 + i)}"  # concept-1-A, concept-1-B, ...
            concept = self._generate_single_concept(
                dna, constraints, concept_id, round_num, parent_concept_id
            )
            concepts.append(concept)
        
        self.generated_concepts.extend(concepts)
        return concepts
    
    def _generate_single_concept(self, dna: dict[str, Any], constraints: dict[str, str],
                                  concept_id: str, round_num: int,
                                  parent_id: Optional[str]) -> Concept:
        """Generate a single concept with DNA-aware variation logic."""
        
        # Extract from constraints or use defaults
        setting_desc = constraints.get("setting", "a bustling metropolis")
        group_a = constraints.get("group_a", "predator")
        group_b = constraints.get("group_b", "prey")
        theme = constraints.get("theme", "prejudice and trust")
        metaphor = constraints.get("social_metaphor", 
            f"{group_a}/{group_b} dynamics mirror real-world prejudice")
        
        # Pick archetype trio with relationship mechanic
        archetype_row = random.choice(self.CHARACTER_ARCHETYPES)
        archetypes = archetype_row[:3]
        relationship_mechanic = archetype_row[3] if len(archetype_row) > 3 else "buddy_cop"
        
        # Generate title with specificity
        title = self._generate_title(setting_desc, group_a, group_b, concept_id, theme)
        
        # Generate logline with narrative specificity
        logline = self._generate_logline(
            archetypes[0], archetypes[1], archetypes[2], group_a, group_b, setting_desc, theme, metaphor
        )
        
        # Build characters with archetype-specific emotional mechanics
        protagonist = self._build_protagonist(archetypes[0], group_a, group_b, setting_desc, theme)
        deuteragonist = self._build_deuteragonist(archetypes[1], group_a, group_b, setting_desc, theme, protagonist)
        antagonist = self._build_antagonist(archetypes[2], group_a, group_b, setting_desc, theme, relationship_mechanic)
        
        # Generate structure summaries using DNA beats if available
        structure = self._generate_structure(
            protagonist, deuteragonist, antagonist, setting_desc, group_a, group_b, theme, metaphor, dna
        )
        
        return Concept(
            id=concept_id,
            title=title,
            logline=logline,
            genre=constraints.get("genre", "animated comedy-drama"),
            setting=setting_desc,
            theme=theme,
            social_metaphor=metaphor,
            act1_summary=structure["act1"],
            act2a_summary=structure["act2a"],
            midpoint=structure["midpoint"],
            act2b_summary=structure["act2b"],
            act3_summary=structure["act3"],
            protagonist=protagonist,
            deuteragonist=deuteragonist,
            antagonist=antagonist,
            round_num=round_num,
            parent_concept_id=parent_id
        )
    
    def _generate_title(self, setting: str, group_a: str, group_b: str, concept_id: str, theme: str) -> str:
        """Generate a concept title with thematic and narrative specificity."""
        seed = hash(concept_id) % 1000
        
        # Extract a key noun from the setting for specificity
        setting_words = setting.replace("a ", "").replace("an ", "").split()
        key_noun = setting_words[0].title() if setting_words else "City"
        
        titles = [
            f"The {group_a.title()} Who Remembered",
            f"{key_noun} of the Forgotten",
            f"The Last {group_b.title()} Story",
            f"When {group_a.title()} Met {group_b.title()}",
            f"{key_noun} Calls",
            f"The Patent of {group_b.title()}s",
            f"Beneath the {group_a.title()} City",
            f"{group_a.title()} and {group_b.title()}: A Hustle",
            f"The {group_b.title()} Beneath",
            f"{key_noun} Tales",
        ]
        return titles[seed % len(titles)]
    
    def _generate_logline(self, protag_arch: str, deut_arch: str, antag_arch: str,
                         group_a: str, group_b: str, setting: str, theme: str, metaphor: str) -> str:
        """Generate a logline with narrative specificity and emotional stakes."""
        templates = [
            f"In {setting}, a {protag_arch} {group_a} discovers that {group_b} history has been buried by those in power — and their mother's survival depends on proving the truth.",
            f"When {setting} begins to crumble, a {protag_arch} {group_a} must partner with a {deut_arch} {group_b} to uncover a conspiracy that erased an entire people from history.",
            f"A {protag_arch} {group_a} in {setting} holds the key to a buried {group_b} neighborhood — but exposing it means betraying their own family to a {antag_arch} who will stop at nothing.",
            f"In {setting}, a {protag_arch} {group_a} who believes in fairy tales discovers they're real when a {deut_arch} {group_b} answers their call — and together they must outwit a {antag_arch} before their history is destroyed forever.",
            f"{setting} was built on a lie. A {protag_arch} {group_a} and a {deut_arch} {group_b} must tear down the walls between their worlds before a {antag_arch} burns the proof that they were never meant to be separate.",
            f"When a {protag_arch} {group_a}'s loved one falls ill in {setting}, the only cure lies in the forbidden {group_b} stories — but a {antag_arch} has made believing in them a crime.",
        ]
        return random.choice(templates)
    
    def _generate_name(self, archetype: str, group: str) -> str:
        """Generate a character name with much larger pools and archetype awareness."""
        # Try group-specific pool first
        pool = self.NAME_POOLS.get(group.lower())
        if pool:
            return random.choice(pool)
        
        # Fallback to archetype-aware pools
        archetype_pools = {
            "earnest believer": self.NAME_POOLS["prey"] + self.NAME_POOLS["child"],
            "cynical trickster": self.NAME_POOLS["predator"] + self.NAME_POOLS["default_male"],
            "meek villain": self.NAME_POOLS["prey"] + self.NAME_POOLS["default_male"],
            "frightened outsider": self.NAME_POOLS["spirit"] + self.NAME_POOLS["default_male"],
            "folksy warrior": self.NAME_POOLS["prey"] + self.NAME_POOLS["default_female"],
            "hidden tyrant": self.NAME_POOLS["predator"] + self.NAME_POOLS["default_male"],
            "determined reformer": self.NAME_POOLS["human"] + self.NAME_POOLS["child"],
            "apathetic con-artist": self.NAME_POOLS["predator"] + self.NAME_POOLS["default_male"],
            "ambitious schemer": self.NAME_POOLS["predator"] + self.NAME_POOLS["default_female"],
            "naive idealist": self.NAME_POOLS["prey"] + self.NAME_POOLS["child"],
            "wounded veteran": self.NAME_POOLS["predator"] + self.NAME_POOLS["default_male"],
            "corrupt bureaucrat": self.NAME_POOLS["human"] + self.NAME_POOLS["default_male"],
            "earnest child": self.NAME_POOLS["child"] + self.NAME_POOLS["prey"],
            "foreign fairy-tale ally": self.NAME_POOLS["spirit"] + self.NAME_POOLS["human"],
            "paranoid ruler": self.NAME_POOLS["predator"] + self.NAME_POOLS["default_male"],
        }
        pool = archetype_pools.get(archetype.lower(), self.NAME_POOLS["human"])
        return random.choice(pool)
    
    def _build_protagonist(self, archetype: str, group_a: str, group_b: str, setting: str, theme: str) -> CharacterArc:
        """Build a protagonist with archetype-specific emotional mechanics."""
        name = self._generate_name(archetype, group_a)
        
        archetype_profiles = {
            "earnest believer": {
                "start": f"believes wholeheartedly in the {group_a} institution, sees the world as solvable through effort and optimism",
                "end": f"learns that optimism without partnership is blindness; becomes wiser but still hopeful",
                "transform": f"discovers that the {self._pluralize(group_b)} were never the enemy — the system that erased them was",
                "wound": f"secretly fears they are exactly what critics say: too small, too naive, too {group_a.rstrip('s')} to matter"
            },
            "earnest child": {
                "start": f"sees the world through stories, believes {group_b} fairy tales are real when no one else does",
                "end": f"learns that stories are weapons against despair, and their faith can summon real allies",
                "transform": f"their love for their mother becomes the catalyst that awakens the {group_b} allies",
                "wound": f"afraid that if they can't save their mother, they are powerless"
            },
            "determined reformer": {
                "start": f"wants to change the {group_a} system from within, believes in rules and procedure",
                "end": f"learns that some rules were built to maintain injustice; becomes a true changemaker",
                "transform": f"discovers that reform requires alliances across {group_a}/{group_b} lines",
                "wound": f"betrayed by a {group_a} mentor they trusted; fears all authority is corrupt"
            },
            "curious explorer": {
                "start": f"asks too many questions about the {group_b} history everyone else ignores",
                "end": f"finds the buried truth and becomes the bridge between {group_a} and {group_b}",
                "transform": f"curiosity becomes courage when they discover the {group_b} neighborhood",
                "wound": f"was told as a child to stop asking about the {self._pluralize(group_b)}; curiosity feels like disobedience"
            },
            "optimistic underdog": {
                "start": f"is the first {group_a} in a position dominated by others, eager to prove themselves",
                "end": f"proves that underdogs win not by being alone, but by building unlikely teams",
                "transform": f"learns that being underestimated is an advantage, not a weakness",
                "wound": f"internalized the belief that {self._pluralize(group_a)} are inferior; overcompensates constantly"
            },
        }
        
        profile = archetype_profiles.get(archetype.lower(), {
            "start": f"naive but determined, believes in the goodness of {setting}",
            "end": f"wiser, scarred, still hopeful but realistic",
            "transform": f"learns that {group_b}s are not the enemy",
            "wound": f"childhood trauma from being underestimated"
        })
        
        return CharacterArc(
            name=name,
            archetype=archetype,
            starting_state=profile["start"],
            ending_state=profile["end"],
            key_transformation=profile["transform"],
            core_wound=profile["wound"]
        )
    
    def _build_deuteragonist(self, archetype: str, group_a: str, group_b: str, setting: str, theme: str, protagonist: CharacterArc) -> CharacterArc:
        """Build a deuteragonist who mirrors and challenges the protagonist."""
        name = self._generate_name(archetype, group_b)
        
        archetype_profiles = {
            "cynical trickster": {
                "start": f"uses humor and scams to survive in a world that distrusts {self._pluralize(group_b)}",
                "end": f"drops the armor and admits that {protagonist.name} is the only partner they ever wanted",
                "transform": f"learns that vulnerability is not weakness — their jokes were hiding loyalty",
                "wound": f"traumatized by {group_a} betrayal as a child; believes all {self._pluralize(group_a)} will eventually turn"
            },
            "foreign fairy-tale ally": {
                "start": f"a {group_b} legend who answers the protagonist's belief because no one has believed in {self._pluralize(group_b)} for generations",
                "end": f"becomes a real friend, not just a story — teaches the protagonist that magic is just love made visible",
                "transform": f"their existence proves the {group_b} history is real; they gain confidence through partnership",
                "wound": f"fading from memory because no one tells their stories anymore; fears becoming forgotten"
            },
            "folksy warrior": {
                "start": f"underestimated because of size or origin, speaks in {group_b} wisdom and country metaphors",
                "end": f"proves that courage comes in all sizes; becomes the hero everyone overlooked",
                "transform": f"discovers that their {group_b} traditions are not backward — they are the key to the mystery",
                "wound": f"was mocked for {group_b} customs; learned to hide their wisdom behind jokes"
            },
            "wounded veteran": {
                "start": f"has seen too much, trusts no one, especially not {self._pluralize(group_a)}",
                "end": f"finds purpose again by protecting the protagonist; becomes a reluctant guardian",
                "transform": f"learns that not all {self._pluralize(group_a)} are the enemy — some are worth dying for",
                "wound": f"lost everything in a {group_a}-{group_b} conflict; blames themselves for surviving"
            },
            "reluctant mentor": {
                "start": f"knows the truth about {group_b} history but has learned that speaking up is dangerous",
                "end": f"finally speaks the truth, empowered by the protagonist's courage",
                "transform": f"passes on forbidden knowledge to the next generation",
                "wound": f"was silenced by the {group_a} institution they once served; carries guilt"
            },
        }
        
        profile = archetype_profiles.get(archetype.lower(), {
            "start": f"cynical, self-serving, hides behind humor",
            "end": f"open, vulnerable, commits to {protagonist.name}",
            "transform": f"discovers not all {self._pluralize(group_a)} are threats",
            "wound": f"betrayed by {self._pluralize(group_a)} in the past"
        })
        
        return CharacterArc(
            name=name,
            archetype=archetype,
            starting_state=profile["start"],
            ending_state=profile["end"],
            key_transformation=profile["transform"],
            core_wound=profile["wound"]
        )
    
    def _build_antagonist(self, archetype: str, group_a: str, group_b: str, setting: str, theme: str, relationship_mechanic: str) -> CharacterArc:
        """Build an antagonist who believes they are the hero of their own story."""
        # Antagonist can be from either group
        antag_group = random.choice([group_a, group_b])
        name = self._generate_name(archetype, antag_group)
        
        archetype_profiles = {
            "meek villain": {
                "start": f"seemingly helpful, eager to please, always defers to authority",
                "end": f"exposed as the true villain — not because they wanted power, but because they wanted to belong",
                "transform": f"their desperate need for family approval turns them against the protagonist",
                "wound": f"never felt loved by their own family; believes villainy is the only way to earn acceptance"
            },
            "hidden tyrant": {
                "start": f"respected authority figure who speaks of tradition and order",
                "end": f"revealed as the architect of the {group_b} erasure, motivated by maintaining power",
                "transform": f"their mask of respectability cracks when the truth threatens their legacy",
                "wound": f"their entire identity is built on a stolen legacy; without it, they are nothing"
            },
            "ambitious schemer": {
                "start": f"charismatic, manipulative, promises change while consolidating control",
                "end": f"their lies unravel when the protagonist proves that cooperation is stronger than division",
                "transform": f"their fear of {group_b} equality drives them to destroy the evidence",
                "wound": f"rose from poverty by exploiting {self._pluralize(group_b)}; fears returning to powerlessness"
            },
            "paranoid ruler": {
                "start": f"maintains power through fear, claims {self._pluralize(group_b)} are dangerous",
                "end": f"their propaganda collapses when the {group_b} neighborhood is revealed",
                "transform": f"their paranoia becomes self-fulfilling as their own crimes are exposed",
                "wound": f"inherited a kingdom built on lies; knows the truth but fears it"
            },
        }
        
        profile = archetype_profiles.get(archetype.lower(), {
            "start": f"seemingly helpful {antag_group} authority figure",
            "end": f"exposed as the true villain",
            "transform": f"reveals deep-seated resentment toward those who threaten their power",
            "wound": f"believes they are protecting their people by maintaining the status quo"
        })
        
        return CharacterArc(
            name=name,
            archetype=archetype,
            starting_state=profile["start"],
            ending_state=profile["end"],
            key_transformation=profile["transform"],
            core_wound=profile["wound"]
        )
    
    @staticmethod
    def _pluralize(word: str) -> str:
        """Simple pluralization: add 's' unless word already ends in 's'."""
        return word if word.endswith("s") else f"{word}s"
    
    def _generate_structure(self, protagonist: CharacterArc, deuteragonist: CharacterArc,
                           antagonist: CharacterArc, setting: str,
                           group_a: str, group_b: str, theme: str, metaphor: str,
                           dna: dict[str, Any]) -> dict[str, str]:
        """Generate 3-act structure summaries using DNA beats and narrative specificity."""
        
        # Try to extract DNA beats for richer structure
        dna_beats = dna.get("story_structure", [])
        dna_archetypes = dna.get("character_archetypes", [])
        
        # Build structure with specificity — each act has emotional + plot progression
        act1_templates = [
            f"{protagonist.name}'s ordinary world: they {protagonist.starting_state.split(';')[0] if ';' in protagonist.starting_state else protagonist.starting_state}. A celebration covers up the truth — {group_b} history has been erased. During a routine assignment, {protagonist.name} discovers {group_b} artifacts in a forbidden place. They meet {deuteragonist.name}, a {deuteragonist.archetype} who seems to know more than they admit. The discovery threatens the {group_a} establishment, and {protagonist.name} is ordered to stand down.",
            f"{protagonist.name} lives in {setting}, where {group_a}s pretend {group_b}s never existed. During the {group_a} celebration, {protagonist.name} finds proof: a {group_b} artifact hidden in plain sight. They meet {deuteragonist.name}, who reveals that {group_b} stories are not fiction — they are suppressed history. When {protagonist.name} tries to report the discovery, they are punished and reassigned.",
            f"In {setting}, {protagonist.name} is the only one who still tells {group_b} stories. Everyone laughs — until a {group_b} artifact appears in {protagonist.name}'s home. They track it to {deuteragonist.name}, a real {group_b} who has been living in the walls. Together they find a map to the buried {group_b} neighborhood, but the authorities burn it. {protagonist.name} is threatened with exile.",
        ]
        
        act2a_templates = [
            f"{protagonist.name} disobeys orders and partners with {deuteragonist.name}. Their investigation reveals a pattern: {group_b} history has been systematically destroyed. They gather allies — other {group_a}s who suspect the truth, and {group_b}s who remember. A bond forms between {protagonist.name} and {deuteragonist.name}, complicated by their groups' mutual distrust. They discover the conspiracy goes deeper than smuggling — it's historical erasure.",
            f"{protagonist.name} and {deuteragonist.name} form an uneasy alliance. {protagonist.name} teaches {deuteragonist.name} about the {group_a} world; {deuteragonist.name} teaches {protagonist.name} the real history. They find more {group_b} artifacts, each revealing a layer of the cover-up. {antagonist.name} seems helpful at first, providing access and information. The partnership deepens — they share a moment of vulnerability.",
            f"Forced to work together, {protagonist.name} and {deuteragonist.name} navigate {setting}'s hidden underworld. They meet {group_b} survivors who have been waiting for someone to believe them. {protagonist.name} begins to question everything they were taught about {group_b}s. {deuteragonist.name} begins to trust {protagonist.name} — a dangerous choice. They find the key to the buried neighborhood, but {antagonist.name} is watching.",
        ]
        
        midpoint_templates = [
            f"False victory: {protagonist.name} and {deuteragonist.name} think they've solved the case. They celebrate. But {antagonist.name} reveals the darker truth — the conspiracy is not about smuggling, it's about maintaining the {group_a} monopoly on history. The partnership fractures: {protagonist.name} wants to go public; {deuteragonist.name} knows the system will crush them. They separate. The case and the love story both break.",
            f"At the height of their success, {protagonist.name} and {deuteragonist.name} believe they can change the world. Then {antagonist.name} shows them the real stakes: exposing the truth means destroying the {group_a} economy, the government, everything. {protagonist.name} insists on truth; {deuteragonist.name} insists on survival. Their argument reveals deep wounds — {protagonist.name} feels betrayed; {deuteragonist.name} feels abandoned. They split.",
            f"{protagonist.name} delivers a speech that should be triumphant. Instead, it backfires. The {group_a} establishment twists their words. {deuteragonist.name} is exposed as a {group_b} and arrested. {protagonist.name} realizes their optimism made things worse. {antagonist.name} offers {protagonist.name} a choice: stay quiet and save their career, or speak up and lose everything. {protagonist.name} chooses silence. {deuteragonist.name} is taken away.",
        ]
        
        act2b_templates = [
            f"Without {deuteragonist.name}, {protagonist.name} is lost. They try to solve the case alone and fail spectacularly. {antagonist.name} tightens the noose — threatening {protagonist.name}'s family, career, safety. {protagonist.name} discovers {antagonist.name}'s true motive: they are protecting a stolen legacy. The buried {group_b} neighborhood is about to be destroyed permanently. {protagonist.name} realizes they cannot do this alone.",
            f"{protagonist.name} hits rock bottom. The {group_a} community turns against them. {antagonist.name} frames {protagonist.name} for the very crimes they were investigating. Alone and discredited, {protagonist.name} finds a {group_b} elder who tells them the full history — how the {group_a}s and {group_b}s once lived together, how the walls were built to divide, not protect. {protagonist.name} realizes the conspiracy is older than they thought.",
            f"Separated from {deuteragonist.name}, {protagonist.name} discovers that {antagonist.name} was once like them — a believer who chose power over truth. {antagonist.name} offers {protagonist.name} a place in the system if they stay silent. {protagonist.name} refuses. They are stripped of everything — badge, home, reputation. In the gutter, they find a community of {group_b}s and sympathetic {group_a}s who have been waiting for a leader. {protagonist.name} is reborn.",
        ]
        
        act3_templates = [
            f"{protagonist.name} and {deuteragonist.name} reunite — not as partners, but as equals. They gather their team: the {group_b} survivors, the sympathetic {group_a}s, the unlikely allies from the B-story. The finale is a heist to save the buried neighborhood before {antagonist.name} destroys it. {protagonist.name} uses {group_a} knowledge; {deuteragonist.name} uses {group_b} wisdom. {antagonist.name} is exposed not through violence, but through truth — the original patent, the music box, the story. The city begins to heal. {protagonist.name} and {deuteragonist.name} are changed forever.",
            f"The climax: {antagonist.name} is about to burn the proof. {protagonist.name} and {deuteragonist.name} race against time through the buried {group_b} neighborhood — a frozen time capsule of beauty and sorrow. They use what they've learned: {protagonist.name}'s {group_a} skills, {deuteragonist.name}'s {group_b} knowledge. {antagonist.name} has a tragic monologue — they wanted to belong, just like everyone else. They are stopped not by force, but by {protagonist.name} offering them a choice: be different from your family. {antagonist.name} refuses. They fall. The neighborhood is saved. The truth is revealed.",
            f"Final confrontation at the heart of the conspiracy — the {group_a} celebration where it all began. {protagonist.name} and {deuteragonist.name} expose {antagonist.name} in front of both {group_a}s and {group_b}s. But {antagonist.name} has one last weapon: they hold the life of someone {protagonist.name} loves. {protagonist.name} must choose between saving one life and saving the truth. They choose both — with help from every ally they made. The B-story pays off: the therapy exercise becomes real. The C-story pays off: the buried neighborhood becomes a monument. The city is changed.",
        ]
        
        return {
            "act1": random.choice(act1_templates),
            "act2a": random.choice(act2a_templates),
            "midpoint": random.choice(midpoint_templates),
            "act2b": random.choice(act2b_templates),
            "act3": random.choice(act3_templates),
        }
    
    def save_concepts_to_vault(self, concepts: list[Concept]) -> list[Path]:
        """Save generated concepts to the Obsidian vault."""
        paths = []
        for concept in concepts:
            note = ObsidianNote(
                path=f"concepts/{concept.id}.md",
                title=concept.title,
                frontmatter={
                    "concept_id": concept.id,
                    "round": concept.round_num,
                    "parent": concept.parent_concept_id or "none",
                    "generated_at": concept.generated_at,
                    "status": "pending_review"
                },
                content=concept.to_markdown(),
                tags=["concept", f"round-{concept.round_num}"]
            )
            path = self.bridge.write_note(f"concepts/{concept.id}.md", note)
            paths.append(path)
        return paths


# =============================================================================
# Prototype Engine
# =============================================================================

class PrototypeEngine:
    """Generates scene prototypes (text + metadata) for key scenes of a concept.
    
    Produces 3 scenes per concept:
    - The Hook (first 2 minutes) — grabs audience
    - The Midpoint (the turn) — false victory or all is lost
    - The Climax (final confrontation) — resolves the arc
    """
    
    def __init__(self, obsidian_bridge: Optional[ObsidianBridge] = None):
        self.bridge = obsidian_bridge or get_bridge()
    
    def prototype_concept(self, concept: Concept) -> Prototype:
        """Generate 3 key scene prototypes for a concept."""
        scenes = []
        
        # Scene 1: The Hook
        hook = self._generate_hook_scene(concept)
        scenes.append(hook)
        
        # Scene 2: The Midpoint
        midpoint = self._generate_midpoint_scene(concept)
        scenes.append(midpoint)
        
        # Scene 3: The Climax
        climax = self._generate_climax_scene(concept)
        scenes.append(climax)
        
        return Prototype(
            concept_id=concept.id,
            concept_title=concept.title,
            scenes=scenes
        )
    
    def _generate_hook_scene(self, concept: Concept) -> ScenePrototype:
        """Generate the opening hook scene."""
        protag = concept.protagonist.name if concept.protagonist else "Protagonist"
        setting = concept.setting
        
        return ScenePrototype(
            scene_type="hook",
            scene_number=1,
            slugline=f"EXT. {setting.upper()} — DAY",
            description=(
                f"We open on {protag} as a child, being bullied by {concept.deuteragonist.group if hasattr(concept.deuteragonist, 'group') else 'others'}. "
                f"A fast cut to present day: {protag} is now an adult, arriving in {setting} with dreams of changing the world. "
                f"The scene establishes the world, the rules, and {protag}'s optimism."
            ),
            dialogue=[
                {"speaker": protag, "line": "I'm going to make the world a better place."},
                {"speaker": "BULLY", "line": "You? A {concept.protagonist.archetype if concept.protagonist else 'nobody'}?"},
                {"speaker": protag, "line": "Watch me."}
            ],
            action_beats=[
                f"{protag} stands up to the bully",
                "Fast cut to adult {protag} arriving in the city",
                "Wide shot revealing the scale of {setting}"
            ],
            emotional_valence=0.6,
            estimated_duration_seconds=120,
            key_characters=[protag],
            visual_notes="Wide establishing shot. Vibrant colors. Optimistic lighting."
        )
    
    def _generate_midpoint_scene(self, concept: Concept) -> ScenePrototype:
        """Generate the midpoint scene (false victory or all is lost)."""
        protag = concept.protagonist.name if concept.protagonist else "Protagonist"
        deut = concept.deuteragonist.name if concept.deuteragonist else "Partner"
        
        return ScenePrototype(
            scene_type="midpoint",
            scene_number=25,
            slugline=f"INT. {concept.setting.upper()} — HEADQUARTERS — NIGHT",
            description=(
                f"{protag} and {deut} celebrate cracking the case. They high-five. "
                f"The crowd cheers. {protag} gives a press conference. "
                f"But then—a bombshell. The real villain reveals themselves. "
                f"Everything {protag} believed was wrong. The partnership fractures."
            ),
            dialogue=[
                {"speaker": deut, "line": "We did it. We actually did it."},
                {"speaker": protag, "line": "I told you we could trust each other."},
                {"speaker": concept.antagonist.name if concept.antagonist else "ANTAGONIST", 
                 "line": "Oh, you sweet naive child. You solved nothing."}
            ],
            action_beats=[
                "Celebration montage",
                "Press conference",
                "The reveal",
                "Partnership breaks"
            ],
            emotional_valence=-0.7,
            estimated_duration_seconds=180,
            key_characters=[protag, deut, concept.antagonist.name if concept.antagonist else "Antagonist"],
            visual_notes="Bright celebration lighting → sudden darkness at reveal."
        )
    
    def _generate_climax_scene(self, concept: Concept) -> ScenePrototype:
        """Generate the climax scene."""
        protag = concept.protagonist.name if concept.protagonist else "Protagonist"
        deut = concept.deuteragonist.name if concept.deuteragonist else "Partner"
        antag = concept.antagonist.name if concept.antagonist else "Antagonist"
        
        return ScenePrototype(
            scene_type="climax",
            scene_number=45,
            slugline=f"EXT. {concept.setting.upper()} — CEREMONY — NIGHT",
            description=(
                f"{antag} is about to be crowned. {protag} bursts in with evidence. "
                f"{antag} sics the guards on them. {deut} arrives to help. "
                f"A chase ensues. {protag} confronts {antag}. "
                f"The truth is revealed to all. {antag} is arrested."
            ),
            dialogue=[
                {"speaker": protag, "line": "You wanted them to fear us. But fear is not power."},
                {"speaker": antag, "line": "They deserve to be afraid!"},
                {"speaker": deut, "line": "No. They deserve a chance to be better."},
                {"speaker": protag, "line": "And that starts with us."}
            ],
            action_beats=[
                "Bursting into the ceremony",
                "Chase sequence",
                "Confrontation on stage",
                "Arrest"
            ],
            emotional_valence=0.8,
            estimated_duration_seconds=240,
            key_characters=[protag, deut, antag],
            visual_notes="Dramatic lighting. Rain or confetti. Slow motion at key beats."
        )
    
    def save_prototype_to_vault(self, prototype: Prototype) -> Path:
        """Save a prototype to the vault."""
        content_lines = [f"# Prototype: {prototype.concept_title}", ""]
        
        for scene in prototype.scenes:
            content_lines.extend([
                f"## Scene {scene.scene_number}: {scene.scene_type.upper()}",
                f"**Slugline**: {scene.slugline}",
                f"**Duration**: {scene.estimated_duration_seconds}s",
                f"**Emotional Valence**: {scene.emotional_valence:+.1f}",
                f"**Characters**: {', '.join(scene.key_characters)}",
                "",
                "### Description",
                scene.description,
                "",
                "### Dialogue",
            ])
            for line in scene.dialogue:
                content_lines.append(f"- **{line['speaker']}**: {line['line']}")
            
            content_lines.extend([
                "",
                "### Action Beats",
            ])
            for beat in scene.action_beats:
                content_lines.append(f"- {beat}")
            
            content_lines.extend([
                "",
                f"### Visual Notes: {scene.visual_notes}",
                "---",
                ""
            ])
        
        note = ObsidianNote(
            path=f"reviews/prototype_{prototype.concept_id}.md",
            title=f"Prototype: {prototype.concept_title}",
            frontmatter={
                "concept_id": prototype.concept_id,
                "generated_at": prototype.generated_at,
                "status": "pending_review"
            },
            content="\n".join(content_lines),
            tags=["prototype", "pending-review"]
        )
        return self.bridge.write_note(f"reviews/prototype_{prototype.concept_id}.md", note)


# =============================================================================
# Critic Swarm
# =============================================================================

class CriticSwarm:
    """Specialized critic agents that score prototypes.
    
    Phase 1 Upgrade: Now powered by System 4 Pattern Recognition instead of
    heuristic keyword matching. Analyzes structure, character arcs, emotional
    curves, pacing formulas, and thematic consistency against established
    story patterns (Save the Cat, 3-Act Structure, Reagan emotional arcs).
    
    Categories:
    - Structure: 3-act breaks, midpoint placement, beat completeness
    - Character: Arc completeness, transformation, voice consistency
    - Emotion: Emotional valence curve, range, recovery timing
    - Pacing: Scene duration, action/dialogue ratio, genre formulas
    - Theme: Social metaphor consistency, show-don't-tell, preachiness
    """
    
    def __init__(self, weights: Optional[dict[str, float]] = None,
                 use_pattern_recognition: bool = True,
                 use_language_engine: bool = True):
        self.weights = weights or {
            "structure": 0.18,
            "character": 0.12,
            "emotion": 0.22,
            "pacing": 0.13,
            "theme": 0.22,
            "dialogue": 0.13
        }
        self.collaboration_hub = CollaborationHubPy()
        
        # Use Pattern Recognition if available and requested
        self.use_pr = use_pattern_recognition and PATTERN_RECOGNITION_AVAILABLE
        if self.use_pr:
            self.pattern_recognizer = PatternRecognizer()
        else:
            self.pattern_recognizer = None
        
        # Use Language Engine if available and requested
        self.use_le = use_language_engine
        if self.use_le:
            try:
                from system4.language_engine import DialogueCritic
                self.dialogue_critic = DialogueCritic()
            except ImportError:
                self.use_le = False
                self.dialogue_critic = None
        else:
            self.dialogue_critic = None
    
    def evaluate(self, prototype: Prototype, concept: Concept) -> Evaluation:
        """Run all critics on a prototype and return combined evaluation."""
        if self.use_pr and self.pattern_recognizer:
            return self._evaluate_with_pattern_recognition(prototype, concept)
        else:
            return self._evaluate_heuristic(prototype, concept)
    
    def _evaluate_with_pattern_recognition(self, prototype: Prototype, concept: Concept) -> Evaluation:
        """Use System 4 Pattern Recognition + Language Engine for analysis."""
        # Run all pattern analyzers
        results = self.pattern_recognizer.analyze(concept, prototype)
        
        # Convert PatternScores to CriticScores for backward compatibility
        scores = []
        for category in ["structure", "character", "emotion", "pacing", "theme"]:
            if category in results:
                scores.append(results[category].to_critic_score())
        
        # Run Dialogue Critic if available
        if self.use_le and self.dialogue_critic:
            try:
                dialogue_score = self.dialogue_critic.evaluate(prototype, concept)
                scores.append(dialogue_score.to_critic_score())
            except Exception as e:
                # Dialogue critic failed, skip it
                pass
        
        # Compute weighted total
        weighted_total = sum(
            s.score * self.weights.get(s.category, 0.15)
            for s in scores
        )
        
        # Combined score (simple average of all critics)
        combined_score = sum(s.score for s in scores) / len(scores) if scores else 0.0
        
        return Evaluation(
            prototype=prototype,
            scores=scores,
            weighted_total=weighted_total,
            combined_score=combined_score
        )
    
    def _evaluate_heuristic(self, prototype: Prototype, concept: Concept) -> Evaluation:
        """Fallback: use original heuristic critics (keyword matching)."""
        scores = []
        
        scores.append(self._structure_critic(prototype, concept))
        scores.append(self._emotion_critic(prototype, concept))
        scores.append(self._pacing_critic(prototype, concept))
        scores.append(self._theme_critic(prototype, concept))
        
        # Add dialogue critic if Language Engine is available
        if self.use_le and self.dialogue_critic:
            try:
                dialogue_score = self.dialogue_critic.evaluate(prototype, concept)
                scores.append(dialogue_score.to_critic_score())
            except Exception:
                pass
        
        # Compute weighted total
        weighted_total = sum(
            s.score * self.weights.get(s.category, 0.15)
            for s in scores
        )
        
        # Combined score (simple average of all critics)
        combined_score = sum(s.score for s in scores) / len(scores) if scores else 0.0
        
        return Evaluation(
            prototype=prototype,
            scores=scores,
            weighted_total=weighted_total,
            combined_score=combined_score
        )
    
    # ========================================================================
    # Heuristic Fallback Methods (kept for backward compatibility)
    # ========================================================================
    
    def _structure_critic(self, prototype: Prototype, concept: Concept) -> CriticScore:
        """Evaluate story structure."""
        score = 7.0
        issues = []
        strengths = []
        
        midpoint = prototype.get_scene_by_type("midpoint")
        if midpoint:
            strengths.append("Midpoint scene present")
            if "false victory" in midpoint.description.lower() or "all is lost" in midpoint.description.lower():
                score += 1.0
                strengths.append("Midpoint has clear turn (false victory / all is lost)")
            else:
                issues.append("Midpoint lacks clear dramatic turn")
                score -= 0.5
        else:
            issues.append("No midpoint scene found")
            score -= 2.0
        
        climax = prototype.get_scene_by_type("climax")
        if climax:
            strengths.append("Climax scene present")
            if "confront" in climax.description.lower() or "arrest" in climax.description.lower():
                score += 0.5
        else:
            issues.append("No climax scene found")
            score -= 2.0
        
        hook = prototype.get_scene_by_type("hook")
        if hook:
            strengths.append("Hook scene present")
        else:
            issues.append("No hook scene found")
            score -= 1.5
        
        if concept.act1_summary and concept.act2a_summary and concept.act3_summary:
            score += 0.5
            strengths.append("Full 3-act structure defined in concept")
        
        score = max(0.0, min(10.0, score))
        
        return CriticScore(
            critic_name="Structure Critic",
            category="structure",
            score=score,
            notes=f"Structure score: {score:.1f}/10. {len(strengths)} strengths, {len(issues)} issues.",
            specific_issues=issues,
            strengths=strengths
        )
    
    def _emotion_critic(self, prototype: Prototype, concept: Concept) -> CriticScore:
        """Evaluate emotional arc."""
        score = 7.0
        issues = []
        strengths = []
        
        valences = [s.emotional_valence for s in prototype.scenes]
        
        if max(valences) > 0.5 and min(valences) < -0.5:
            score += 1.0
            strengths.append("Strong emotional range (highs and lows)")
        else:
            issues.append("Emotional range is narrow")
            score -= 1.0
        
        if any(v < -0.5 for v in valences):
            score += 0.5
            strengths.append("Contains effective negative emotional beat")
        else:
            issues.append("Missing strong negative emotional beat")
        
        climax = prototype.get_scene_by_type("climax")
        if climax and climax.emotional_valence > 0.5:
            score += 1.0
            strengths.append("Climax resolves positively")
        else:
            issues.append("Climax should resolve more positively")
        
        total_lines = sum(len(s.dialogue) for s in prototype.scenes)
        if total_lines >= 3:
            score += 0.5
            strengths.append("Dialogue present in key scenes")
        
        score = max(0.0, min(10.0, score))
        
        return CriticScore(
            critic_name="Emotion Critic",
            category="emotion",
            score=score,
            notes=f"Emotion score: {score:.1f}/10. Valence range: {min(valences):+.1f} to {max(valences):+.1f}",
            specific_issues=issues,
            strengths=strengths
        )
    
    def _pacing_critic(self, prototype: Prototype, concept: Concept) -> CriticScore:
        """Evaluate pacing."""
        score = 7.0
        issues = []
        strengths = []
        
        total_duration = sum(s.estimated_duration_seconds for s in prototype.scenes)
        
        hook = prototype.get_scene_by_type("hook")
        climax = prototype.get_scene_by_type("climax")
        
        if hook and hook.estimated_duration_seconds <= 120:
            score += 0.5
            strengths.append("Hook is concise (under 2 min)")
        else:
            issues.append("Hook may be too long")
        
        if climax and climax.estimated_duration_seconds >= 180:
            score += 0.5
            strengths.append("Climax has adequate duration for impact")
        
        total_dialogue_lines = sum(len(s.dialogue) for s in prototype.scenes)
        total_action_beats = sum(len(s.action_beats) for s in prototype.scenes)
        
        if total_action_beats > total_dialogue_lines:
            score += 0.5
            strengths.append("Action beats exceed dialogue lines (good for animation)")
        else:
            issues.append("Dialogue-heavy; consider more visual storytelling")
        
        if len(prototype.scenes) == 3:
            score += 0.5
            strengths.append("Exactly 3 key scenes prototyped (hook, midpoint, climax)")
        
        score = max(0.0, min(10.0, score))
        
        return CriticScore(
            critic_name="Pacing Critic",
            category="pacing",
            score=score,
            notes=f"Pacing score: {score:.1f}/10. Total prototype duration: {total_duration}s.",
            specific_issues=issues,
            strengths=strengths
        )
    
    def _theme_critic(self, prototype: Prototype, concept: Concept) -> CriticScore:
        """Evaluate thematic consistency."""
        score = 7.0
        issues = []
        strengths = []
        
        theme = concept.theme.lower() if concept.theme else ""
        
        all_text = " ".join([
            s.description + " " + " ".join(d["line"] for d in s.dialogue)
            for s in prototype.scenes
        ]).lower()
        
        theme_keywords = theme.split()
        keyword_hits = sum(1 for kw in theme_keywords if kw in all_text and len(kw) > 3)
        if keyword_hits > 0:
            score += 0.5
            strengths.append("Theme keywords present in prototype scenes")
        
        climax = prototype.get_scene_by_type("climax")
        if climax:
            climax_text = " ".join(d["line"] for d in climax.dialogue).lower()
            if any(kw in climax_text for kw in ["fear", "trust", "together", "better", "change"]):
                score += 1.0
                strengths.append("Climax dialogue addresses core theme")
            else:
                issues.append("Climax dialogue should more explicitly state theme")
        
        hook = prototype.get_scene_by_type("hook")
        if hook:
            hook_text = " ".join(d["line"] for d in hook.dialogue).lower()
            if "world a better place" in hook_text or "prejudice" in hook_text:
                score -= 0.5
                issues.append("Theme stated too explicitly in hook; consider showing, not telling")
        
        if concept.protagonist and concept.deuteragonist:
            if "learns" in concept.protagonist.key_transformation.lower():
                score += 0.5
                strengths.append("Protagonist arc embodies thematic learning")
        
        score = max(0.0, min(10.0, score))
        
        return CriticScore(
            critic_name="Theme Critic",
            category="theme",
            score=score,
            notes=f"Theme score: {score:.1f}/10. Theme: '{concept.theme}'",
            specific_issues=issues,
            strengths=strengths
        )
    
    def save_evaluation_to_hub(self, evaluation: Evaluation, concept: Concept) -> None:
        """Save critic feedback to the collaboration hub."""
        for score in evaluation.scores:
            self.collaboration_hub.add_feedback(
                reviewer_id=f"critic-{score.category}",
                message=score.notes,
                target_scene=f"prototype_{evaluation.prototype.concept_id}",
                score=score.score,
                category=score.category
            )
    
    def save_evaluation_to_vault(self, evaluation: Evaluation, concept: Concept,
                                  bridge: Optional[ObsidianBridge] = None) -> None:
        """Save structured evaluation scores to the vault for frontend display."""
        vault = bridge or get_bridge()
        
        # Build score breakdown
        score_data = {}
        for score in evaluation.scores:
            score_data[score.category] = {
                "score": score.score,
                "notes": score.notes,
                "issues": score.specific_issues,
                "strengths": score.strengths,
            }
        
        note = ObsidianNote(
            path=f"reviews/evaluation_{evaluation.prototype.concept_id}.md",
            title=f"Evaluation: {concept.title}",
            frontmatter={
                "concept_id": evaluation.prototype.concept_id,
                "combined_score": round(evaluation.combined_score, 1),
                "weighted_total": round(evaluation.weighted_total, 1),
                "scores": score_data,
                "evaluated_at": datetime.now().isoformat(),
            },
            content=f"""# Evaluation: {concept.title}

**Combined Score:** {evaluation.combined_score:.1f}/10
**Weighted Total:** {evaluation.weighted_total:.1f}/10

## Score Breakdown

{chr(10).join(f"### {s.critic_name}: {s.score:.1f}/10\n{s.notes}\n\n**Strengths:**\n{chr(10).join('- ' + st for st in s.strengths) if s.strengths else '- None'}\n\n**Issues:**\n{chr(10).join('- ' + iss for iss in s.specific_issues) if s.specific_issues else '- None'}" for s in evaluation.scores)}

## Overall Assessment

This concept scored **{evaluation.combined_score:.1f}/10** across {len(evaluation.scores)} critic categories.
            """,
            tags=["evaluation", "critic-score"]
        )
        vault.write_note(
            f"reviews/evaluation_{evaluation.prototype.concept_id}.md",
            note
        )


# =============================================================================
# Selection Engine
# =============================================================================

class SelectionEngine:
    """Selects top concepts and manages iteration rounds.
    
    Uses weighted critic scores to rank prototypes, selects top-K,
    and determines whether to iterate or converge.
    """
    
    def __init__(self, top_k: int = 2, convergence_threshold: float = 7.5):
        self.top_k = top_k
        self.convergence_threshold = convergence_threshold
        self.round_history: list[list[Evaluation]] = []
    
    def select(self, evaluations: list[Evaluation], 
               round_num: int) -> tuple[list[Evaluation], list[Evaluation], bool]:
        """Select top-K concepts from evaluations.
        
        Returns:
            (winners, losers, should_converge)
        """
        self.round_history.append(evaluations)
        
        # Sort by combined score (descending)
        sorted_evals = sorted(evaluations, key=lambda e: e.combined_score, reverse=True)
        
        winners = sorted_evals[:self.top_k]
        losers = sorted_evals[self.top_k:]
        
        # Check convergence criteria
        should_converge = self._check_convergence(winners, round_num)
        
        return winners, losers, should_converge
    
    def _check_convergence(self, winners: list[Evaluation], round_num: int) -> bool:
        """Determine if evolution should converge on these winners."""
        # Converge if all winners exceed threshold
        all_above_threshold = all(w.combined_score >= self.convergence_threshold for w in winners)
        
        # Converge if we've done enough rounds
        max_rounds = 2
        
        # Converge if top winner is significantly ahead
        if len(winners) >= 2:
            score_gap = winners[0].combined_score - winners[1].combined_score
            clear_winner = score_gap > 1.5
        else:
            clear_winner = False
        
        return all_above_threshold or round_num >= max_rounds or clear_winner
    
    def get_selection_report(self, winners: list[Evaluation], 
                            losers: list[Evaluation]) -> str:
        """Generate a human-readable selection report."""
        lines = ["# Selection Report", ""]
        
        lines.append(f"## Winners (Top {self.top_k})")
        for i, w in enumerate(winners, 1):
            lines.append(f"### {i}. {w.prototype.concept_title}")
            lines.append(f"- **Combined Score**: {w.combined_score:.1f}/10")
            lines.append(f"- **Weighted Score**: {w.weighted_total:.1f}/10")
            for s in w.scores:
                lines.append(f"  - {s.category}: {s.score:.1f}")
            lines.append("")
        
        lines.append(f"## Eliminated ({len(losers)})")
        for e in losers:
            lines.append(f"- {e.prototype.concept_title}: {e.combined_score:.1f}")
        
        return "\n".join(lines)


# =============================================================================
# Story Evolution Engine (Orchestrator)
# =============================================================================

class StoryEvolutionEngine:
    """Orchestrates the full generate → prototype → critic → select → iterate loop.
    
    This is the main entry point for System 3's story evolution process.
    """
    
    def __init__(self, 
                 obsidian_bridge: Optional[ObsidianBridge] = None,
                 n_concepts: int = 6,
                 n_rounds: int = 2,
                 top_k: int = 2):
        self.bridge = obsidian_bridge or get_bridge()
        self.n_concepts = n_concepts
        self.n_rounds = n_rounds
        self.top_k = top_k
        
        self.concept_generator = ConceptGenerator(self.bridge)
        self.prototype_engine = PrototypeEngine(self.bridge)
        self.critic_swarm = CriticSwarm()
        self.selection_engine = SelectionEngine(top_k=top_k)
        
        self.all_concepts: list[Concept] = []
        self.all_evaluations: list[Evaluation] = []
        self.winning_concept: Optional[Concept] = None
    
    def evolve(self, dna_source: str, constraints: dict[str, str]) -> Concept:
        """Run the full evolution loop.
        
        Args:
            dna_source: Path to Creative DNA in vault
            constraints: User constraints dict
            
        Returns:
            The winning Concept
        """
        print(f"\n{'='*60}")
        print("  STORY EVOLUTION ENGINE — Starting Evolution")
        print(f"{'='*60}")
        print(f"  DNA Source: {dna_source}")
        print(f"  Constraints: {constraints}")
        print(f"  Concepts per round: {self.n_concepts}")
        print(f"  Max rounds: {self.n_rounds}")
        print(f"  Top-K selection: {self.top_k}")
        print(f"{'='*60}\n")
        
        current_round = 1
        parent_concepts: list[Concept] = []
        
        while current_round <= self.n_rounds:
            print(f"\n--- Round {current_round} ---")
            
            # Generate concepts
            if current_round == 1:
                concepts = self.concept_generator.generate(
                    dna_source, constraints, 
                    n_concepts=self.n_concepts, 
                    round_num=current_round
                )
            else:
                # Generate refined concepts from winners
                concepts = []
                for i, parent in enumerate(parent_concepts):
                    # Create refined variants of each winner
                    for j in range(self.n_concepts // len(parent_concepts)):
                        refined = self._refine_concept(parent, constraints, current_round)
                        concepts.append(refined)
            
            self.all_concepts.extend(concepts)
            print(f"Generated {len(concepts)} concepts")
            
            # Save concepts to vault
            self.concept_generator.save_concepts_to_vault(concepts)
            
            # Prototype each concept
            prototypes = []
            for concept in concepts:
                proto = self.prototype_engine.prototype_concept(concept)
                prototypes.append(proto)
                self.prototype_engine.save_prototype_to_vault(proto)
            
            print(f"Prototyped {len(prototypes)} concepts (3 scenes each)")
            
            # Critic swarm evaluates each prototype
            evaluations = []
            for proto, concept in zip(prototypes, concepts):
                eval = self.critic_swarm.evaluate(proto, concept)
                evaluations.append(eval)
                self.critic_swarm.save_evaluation_to_hub(eval, concept)
                self.critic_swarm.save_evaluation_to_vault(eval, concept, self.bridge)
            
            self.all_evaluations.extend(evaluations)
            print(f"Critic swarm evaluated {len(evaluations)} prototypes")
            
            # Print score summary
            for eval in evaluations:
                char_score = eval.get_score_by_category('character')
                char_str = f"C:{char_score.score:.1f} " if char_score else ""
                print(f"  {eval.prototype.concept_title}: {eval.combined_score:.1f}/10 "
                      f"(S:{eval.get_score_by_category('structure').score:.1f} "
                      f"{char_str}"
                      f"E:{eval.get_score_by_category('emotion').score:.1f} "
                      f"P:{eval.get_score_by_category('pacing').score:.1f} "
                      f"T:{eval.get_score_by_category('theme').score:.1f})")
            
            # Select winners
            winners, losers, should_converge = self.selection_engine.select(
                evaluations, current_round
            )
            
            print(f"\nSelection: {len(winners)} winners, {len(losers)} eliminated")
            for w in winners:
                print(f"  → {w.prototype.concept_title}: {w.combined_score:.1f}")
            
            # Save selection report
            report = self.selection_engine.get_selection_report(winners, losers)
            report_note = ObsidianNote(
                path=f"reviews/selection_round_{current_round}.md",
                title=f"Selection Report — Round {current_round}",
                frontmatter={
                    "round": current_round,
                    "winners": [w.prototype.concept_id for w in winners],
                    "losers": [l.prototype.concept_id for l in losers]
                },
                content=report,
                tags=["selection", f"round-{current_round}"]
            )
            self.bridge.write_note(f"reviews/selection_round_{current_round}.md", report_note)
            
            if should_converge:
                print(f"\n*** CONVERGED at Round {current_round} ***")
                self.winning_concept = self._select_final_winner(winners)
                break
            
            # Prepare for next round
            parent_concepts = [c for c in concepts if any(
                w.prototype.concept_id == c.id for w in winners
            )]
            current_round += 1
        
        if self.winning_concept is None:
            # If we exhausted rounds, pick the best overall
            best_eval = max(self.all_evaluations, key=lambda e: e.combined_score)
            self.winning_concept = next(
                c for c in self.all_concepts if c.id == best_eval.prototype.concept_id
            )
        
        print(f"\n{'='*60}")
        print(f"  WINNING CONCEPT: {self.winning_concept.title}")
        print(f"  ID: {self.winning_concept.id}")
        print(f"{'='*60}\n")
        
        # Save winner to vault
        winner_note = ObsidianNote(
            path="concepts/WINNER.md",
            title=f"WINNER: {self.winning_concept.title}",
            frontmatter={
                "concept_id": self.winning_concept.id,
                "rounds": current_round,
                "status": "winner"
            },
            content=self.winning_concept.to_markdown(),
            tags=["winner", "final"]
        )
        self.bridge.write_note("concepts/WINNER.md", winner_note)
        
        return self.winning_concept
    
    def _refine_concept(self, parent: Concept, constraints: dict[str, str],
                       round_num: int) -> Concept:
        """Create a refined variant of a parent concept."""
        # Copy parent with modifications based on critic feedback
        import copy
        refined = copy.deepcopy(parent)
        refined.id = f"{parent.id}-refined-{round_num}"
        refined.round_num = round_num
        refined.parent_concept_id = parent.id
        refined.title = f"{parent.title} (Refined)"
        refined.generated_at = datetime.now().isoformat()
        
        # Apply a random refinement strategy
        strategies = [
            self._refine_make_antagonist_more_sympathetic,
            self._refine_deepen_protagonist_wound,
            self._refine_strengthen_midpoint_twist,
            self._refine_add_supporting_character,
        ]
        strategy = random.choice(strategies)
        strategy(refined)
        
        return refined
    
    def _refine_make_antagonist_more_sympathetic(self, concept: Concept) -> None:
        """Refinement: Give antagonist a relatable motivation."""
        if concept.antagonist:
            concept.antagonist.core_wound = "Was once a victim of the same system they now exploit"
            concept.antagonist.starting_state += " (hides pain behind ambition)"
    
    def _refine_deepen_protagonist_wound(self, concept: Concept) -> None:
        """Refinement: Make protagonist's core wound more specific."""
        if concept.protagonist:
            concept.protagonist.core_wound = "Witnessed their sibling rejected by the same system"
    
    def _refine_strengthen_midpoint_twist(self, concept: Concept) -> None:
        """Refinement: Make the midpoint reversal more dramatic."""
        concept.midpoint = (
            concept.midpoint + 
            " The villain reveals they were once the protagonist's mentor. "
            "The betrayal cuts deeper than anyone expected."
        )
    
    def _refine_add_supporting_character(self, concept: Concept) -> None:
        """Refinement: Add a quirky supporting character."""
        supporter = CharacterArc(
            name="Finn",
            archetype="comic relief with hidden wisdom",
            starting_state="appears clueless, always eating",
            ending_state="saves the day with unexpected knowledge",
            key_transformation="reveals they were an expert all along"
        )
        concept.supporting.append(supporter)
    
    def _select_final_winner(self, winners: list[Evaluation]) -> Concept:
        """Select the single best concept from winners."""
        best = max(winners, key=lambda w: w.combined_score)
        return next(
            c for c in self.all_concepts 
            if c.id == best.prototype.concept_id
        )
    
    def get_evolution_stats(self) -> dict[str, Any]:
        """Get statistics about the evolution process."""
        return {
            "total_concepts_generated": len(self.all_concepts),
            "total_evaluations": len(self.all_evaluations),
            "rounds_completed": len(self.selection_engine.round_history),
            "winning_concept": self.winning_concept.to_dict() if self.winning_concept else None,
            "average_scores_by_round": [
                {
                    "round": i + 1,
                    "avg_combined": sum(e.combined_score for e in evals) / len(evals) if evals else 0
                }
                for i, evals in enumerate(self.selection_engine.round_history)
            ]
        }


# =============================================================================
# CLI / Test
# =============================================================================

if __name__ == "__main__":
    # Demo run
    engine = StoryEvolutionEngine(n_concepts=4, n_rounds=1, top_k=2)
    
    winner = engine.evolve(
        dna_source="memory/films_analyzed/zootopia_dna.md",
        constraints={
            "setting": "a city of robots",
            "group_a": "robot",
            "group_b": "human",
            "protagonist_type": "underdog",
            "genre": "sci-fi comedy-drama",
            "theme": "trust between organic and synthetic life",
            "social_metaphor": "robot/human dynamics mirror immigration and assimilation"
        }
    )
    
    print("\nEvolution Stats:")
    print(json.dumps(engine.get_evolution_stats(), indent=2))
