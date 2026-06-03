"""Obsidian Bridge — Shared Memory Layer for the Evolutionary Studio.

Provides Python read/write/query access to the Obsidian vault, making the studio
state human-readable (open in Obsidian) and machine-readable (query from Python).
"""

from __future__ import annotations

import os
import re
import json
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ObsidianNote:
    """Represents an Obsidian markdown note with frontmatter and content."""
    path: str
    title: str
    frontmatter: dict[str, Any] = field(default_factory=dict)
    content: str = ""
    tags: list[str] = field(default_factory=list)
    backlinks: list[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Serialize to full markdown with YAML frontmatter."""
        lines = ["---"]
        for key, value in self.frontmatter.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")
        
        # Add tags line if present
        if self.tags:
            tag_str = " ".join(f"#{tag}" for tag in self.tags)
            lines.append(f"{tag_str}")
            lines.append("")
        
        lines.append(self.content)
        return "\n".join(lines)
    
    @classmethod
    def from_markdown(cls, path: str, markdown: str) -> "ObsidianNote":
        """Parse markdown with YAML frontmatter into ObsidianNote."""
        lines = markdown.split("\n")
        
        frontmatter = {}
        content_lines = []
        tags = []
        
        if lines and lines[0].strip() == "---":
            # Parse frontmatter
            fm_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    fm_end = i
                    break
            
            if fm_end > 0:
                fm_text = "\n".join(lines[1:fm_end])
                try:
                    import yaml
                    frontmatter = yaml.safe_load(fm_text) or {}
                except ImportError:
                    # Fallback: simple key: value parsing
                    for line in lines[1:fm_end]:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            frontmatter[key.strip()] = value.strip()
                
                content_lines = lines[fm_end + 1:]
        else:
            content_lines = lines
        
        # Extract tags from content
        content_text = "\n".join(content_lines)
        tags = re.findall(r'#(\w[\w/-]*)', content_text)
        
        # Clean tags from content for storage
        content_clean = re.sub(r'#\w[\w/-]*', '', content_text).strip()
        
        # Extract wiki-link backlinks
        backlinks = re.findall(r'\[\[([^\]]+)\]\]', content_text)
        
        title = Path(path).stem.replace("_", " ").replace("-", " ").title()
        
        return cls(
            path=path,
            title=title,
            frontmatter=frontmatter,
            content=content_clean,
            tags=tags,
            backlinks=backlinks
        )


class ObsidianBridge:
    """Bridge between Python and the Obsidian vault.
    
    All studio state lives in the Obsidian vault as markdown files.
    This bridge provides read/write/query operations.
    """
    
    def __init__(self, vault_path: str | Path = "studio"):
        self.vault_path = Path(vault_path).resolve()
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        # Ensure standard directories exist
        for subdir in ["concepts", "characters", "scenes", "reviews", 
                       "assets", "memory/films_analyzed", "memory/post_mortems", 
                       "memory/cost_curves"]:
            (self.vault_path / subdir).mkdir(parents=True, exist_ok=True)
    
    # ---- Core I/O ----
    
    def write_note(self, rel_path: str, note: ObsidianNote) -> Path:
        """Write an ObsidianNote to the vault. Creates parent dirs if needed."""
        full_path = self.vault_path / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure .md extension
        if not full_path.suffix:
            full_path = full_path.with_suffix(".md")
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(note.to_markdown())
        
        return full_path
    
    def read_note(self, rel_path: str) -> Optional[ObsidianNote]:
        """Read an ObsidianNote from the vault. Returns None if not found."""
        full_path = self.vault_path / rel_path
        if not full_path.exists():
            # Try with .md extension
            full_path = full_path.with_suffix(".md")
            if not full_path.exists():
                return None
        
        with open(full_path, "r", encoding="utf-8") as f:
            markdown = f.read()
        
        return ObsidianNote.from_markdown(rel_path, markdown)
    
    def update_note(self, rel_path: str, **kwargs) -> Optional[ObsidianNote]:
        """Update specific fields of an existing note."""
        note = self.read_note(rel_path)
        if note is None:
            return None
        
        for key, value in kwargs.items():
            if hasattr(note, key):
                setattr(note, key, value)
            elif key in note.frontmatter:
                note.frontmatter[key] = value
        
        # Auto-update modified timestamp
        note.frontmatter["modified"] = datetime.now().isoformat()
        
        self.write_note(rel_path, note)
        return note
    
    def delete_note(self, rel_path: str) -> bool:
        """Delete a note from the vault. Returns True if deleted."""
        full_path = self.vault_path / rel_path
        if not full_path.exists():
            full_path = full_path.with_suffix(".md")
        
        if full_path.exists():
            full_path.unlink()
            return True
        return False
    
    # ---- Queries ----
    
    def query_notes(self, tag: Optional[str] = None, 
                    folder: Optional[str] = None,
                    pattern: Optional[str] = None) -> list[ObsidianNote]:
        """Query notes by tag, folder, or regex pattern in content."""
        results = []
        
        # Determine search root
        if folder:
            search_root = self.vault_path / folder
        else:
            search_root = self.vault_path
        
        if not search_root.exists():
            return results
        
        # Find all .md files
        md_files = list(search_root.rglob("*.md"))
        
        for md_file in md_files:
            rel_path = md_file.relative_to(self.vault_path).as_posix()
            note = self.read_note(rel_path)
            if note is None:
                continue
            
            # Filter by tag
            if tag and tag not in note.tags:
                continue
            
            # Filter by pattern
            if pattern:
                if not re.search(pattern, note.content, re.IGNORECASE):
                    continue
            
            results.append(note)
        
        return results
    
    def get_all_notes(self, folder: Optional[str] = None) -> list[ObsidianNote]:
        """Get all notes in a folder (or entire vault)."""
        return self.query_notes(folder=folder)
    
    def get_notes_by_tag(self, tag: str) -> list[ObsidianNote]:
        """Get all notes with a specific tag."""
        return self.query_notes(tag=tag)
    
    def search_content(self, query: str, folder: Optional[str] = None) -> list[ObsidianNote]:
        """Full-text search across note content."""
        return self.query_notes(folder=folder, pattern=query)
    
    # ---- Links & Canvas ----
    
    def link_notes(self, from_path: str, to_path: str, 
                   link_text: Optional[str] = None) -> bool:
        """Add a wiki-link from one note to another."""
        from_note = self.read_note(from_path)
        if from_note is None:
            return False
        
        to_name = Path(to_path).stem
        link = f"[[{to_name}]]" if link_text is None else f"[[{to_name}|{link_text}]]"
        
        if link not in from_note.content:
            from_note.content += f"\n\n{link}"
            from_note.backlinks.append(to_name)
            self.write_note(from_path, from_note)
        
        return True
    
    def get_backlinks(self, rel_path: str) -> list[str]:
        """Get all notes that link TO this note."""
        target_name = Path(rel_path).stem
        all_notes = self.get_all_notes()
        
        backlinks = []
        for note in all_notes:
            if target_name in note.backlinks:
                backlinks.append(note.path)
        
        return backlinks
    
    # ---- Production Board (Canvas) ----
    
    def update_canvas(self, canvas_name: str, nodes: list[dict]) -> Path:
        """Update or create an Obsidian canvas file.
        
        Canvas files are JSON with nodes (notes, images, text) and edges.
        """
        canvas_path = self.vault_path / f"{canvas_name}.canvas"
        
        # Build canvas structure
        canvas_data = {
            "nodes": [],
            "edges": []
        }
        
        x, y = 0, 0
        for i, node in enumerate(nodes):
            canvas_node = {
                "id": node.get("id", f"node-{i}"),
                "type": node.get("type", "file"),  # file, text, link, group
                "x": node.get("x", x),
                "y": node.get("y", y),
                "width": node.get("width", 300),
                "height": node.get("height", 200),
                "color": node.get("color", "")
            }
            
            if node.get("type") == "text":
                canvas_node["text"] = node.get("text", "")
            elif node.get("type") == "link":
                canvas_node["url"] = node.get("url", "")
            else:
                canvas_node["file"] = node.get("file", "")
            
            canvas_data["nodes"].append(canvas_node)
            
            # Add edges if specified
            for edge in node.get("edges", []):
                canvas_data["edges"].append({
                    "id": f"edge-{i}-{edge}",
                    "fromNode": canvas_node["id"],
                    "fromSide": "right",
                    "toNode": edge,
                    "toSide": "left"
                })
            
            x += 350
            if x > 2000:
                x = 0
                y += 250
        
        with open(canvas_path, "w", encoding="utf-8") as f:
            json.dump(canvas_data, f, indent=2)
        
        return canvas_path
    
    # ---- Utility ----
    
    def get_vault_stats(self) -> dict[str, Any]:
        """Get statistics about the vault."""
        all_notes = self.get_all_notes()
        
        stats = {
            "total_notes": len(all_notes),
            "total_tags": len(set(tag for note in all_notes for tag in note.tags)),
            "all_tags": sorted(set(tag for note in all_notes for tag in note.tags)),
            "folder_counts": {}
        }
        
        for note in all_notes:
            folder = Path(note.path).parent.as_posix()
            stats["folder_counts"][folder] = stats["folder_counts"].get(folder, 0) + 1
        
        return stats
    
    def ensure_note(self, rel_path: str, default_content: str = "",
                    default_frontmatter: Optional[dict] = None,
                    tags: Optional[list[str]] = None) -> ObsidianNote:
        """Ensure a note exists. Create with defaults if not found."""
        note = self.read_note(rel_path)
        if note is not None:
            return note
        
        # Create new note
        title = Path(rel_path).stem.replace("_", " ").replace("-", " ").title()
        note = ObsidianNote(
            path=rel_path,
            title=title,
            frontmatter=default_frontmatter or {},
            content=default_content,
            tags=tags or []
        )
        note.frontmatter["created"] = datetime.now().isoformat()
        
        self.write_note(rel_path, note)
        return note


# ---- Convenience factory ----

def get_bridge(vault_path: str = "studio") -> ObsidianBridge:
    """Get the default Obsidian bridge instance."""
    return ObsidianBridge(vault_path)


# ---- Seed data helpers ----

def seed_creative_dna(bridge: ObsidianBridge, dna: dict[str, Any]) -> Path:
    """Seed the vault with Creative DNA from a reference film analysis."""
    note = ObsidianNote(
        path="memory/films_analyzed/creative_dna.md",
        title="Creative DNA Template",
        frontmatter={
            "source_film": dna.get("source_film", "Unknown"),
            "analyzed_at": datetime.now().isoformat(),
            "dna_version": "1.0"
        },
        content=_format_dna_content(dna),
        tags=["dna", "template", dna.get("source_film", "unknown").lower().replace(" ", "-")]
    )
    return bridge.write_note("memory/films_analyzed/creative_dna.md", note)


def _format_dna_content(dna: dict[str, Any]) -> str:
    """Format Creative DNA dict into readable markdown."""
    lines = ["# Creative DNA", ""]
    
    for section, data in dna.items():
        lines.append(f"## {section.replace('_', ' ').title()}")
        if isinstance(data, dict):
            for key, value in data.items():
                lines.append(f"- **{key}**: {value}")
        elif isinstance(data, list):
            for item in data:
                lines.append(f"- {item}")
        else:
            lines.append(str(data))
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Quick test
    bridge = get_bridge()
    
    # Create a test note
    test_note = ObsidianNote(
        path="test/hello_world.md",
        title="Hello World",
        frontmatter={"project": "Evolutionary Studio", "version": "0.1.0"},
        content="This is a test note for the Evolutionary Studio.",
        tags=["test", "hello"]
    )
    
    bridge.write_note("test/hello_world.md", test_note)
    
    # Query it back
    found = bridge.get_notes_by_tag("test")
    print(f"Found {len(found)} note(s) with tag #test")
    for note in found:
        print(f"  - {note.title}: {note.content[:50]}...")
    
    # Stats
    print(f"\nVault stats: {json.dumps(bridge.get_vault_stats(), indent=2)}")
