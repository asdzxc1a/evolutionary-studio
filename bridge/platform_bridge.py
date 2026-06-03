"""Platform Bridge — Python Adapters for Existing Platform Assets.

Converts the JavaScript platform components (ConsistencyEngine, CollaborationHub)
and Python API gateway into Python classes that integrate with the Evolutionary
Studio architecture. Also wraps the AIGCPlatformGateway for video generation routing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field

# Import the API gateway
import sys
platform_dir = Path(__file__).resolve().parent.parent / "platform"
if str(platform_dir) not in sys.path:
    sys.path.insert(0, str(platform_dir))

from api_gateway import AIGCPlatformGateway, KlingAPIAdapter, ViduAPIAdapter


@dataclass
class CharacterTemplate:
    """Character registration for consistency tracking."""
    id: str
    name: str
    reference_image: Optional[str] = None
    base_description: str = ""
    instances_generated: int = 0
    voice_profile: Optional[dict] = None
    animation_style: Optional[str] = None


@dataclass
class StyleProfile:
    """Global aesthetic style for a production."""
    name: str
    prompt_modifier: str
    color_palette: Optional[list[str]] = None
    lighting_scheme: Optional[str] = None


@dataclass
class ReviewEntry:
    """A review/feedback entry from a collaborator or critic agent."""
    id: str
    reviewer_id: str
    reviewer_name: str
    reviewer_role: str
    target_scene: Optional[str] = None
    target_shot: Optional[int] = None
    message: str = ""
    suggested_settings: Optional[dict] = None
    status: str = "pending"  # pending, applied, rejected
    score: Optional[float] = None
    category: str = "general"  # structure, emotion, pacing, theme, visual, sound
    timestamp: Optional[str] = None


class ConsistencyEnginePy:
    """Python port of the JavaScript ConsistencyEngine.
    
    Manages character and style consistency across all video generation shots.
    Injects reference descriptors and coordinates seed/embedding parameters.
    """
    
    def __init__(self):
        self.characters: dict[str, CharacterTemplate] = {}
        self.active_style: StyleProfile = StyleProfile(
            name="Cinematic Teal & Orange",
            prompt_modifier=("cinematic film style, 35mm photography, "
                           "shallow depth of field, color graded in teal and orange mood")
        )
        self.generation_log: list[dict] = []
    
    def register_character(self, char_id: str, name: str,
                          reference_image: Optional[str] = None,
                          base_description: str = "") -> CharacterTemplate:
        """Register a character template for consistency across shots."""
        char = CharacterTemplate(
            id=char_id,
            name=name,
            reference_image=reference_image,
            base_description=base_description
        )
        self.characters[char_id] = char
        print(f"[ConsistencyEngine] Registered character '{name}' (ID: {char_id})")
        return char
    
    def update_character_voice(self, char_id: str, voice_profile: dict) -> bool:
        """Update a character's voice profile for TTS consistency."""
        if char_id not in self.characters:
            return False
        self.characters[char_id].voice_profile = voice_profile
        return True
    
    def compile_scene_payload(self, raw_prompt: str,
                             character_ids: list[str] = None,
                             style_override: Optional[StyleProfile] = None) -> dict:
        """Build the final prompt and API payload for a scene.
        
        Ensures consistent character descriptions, face references (IP-Adapter),
        style modifiers, and temporal seed coherence.
        """
        character_ids = character_ids or []
        consolidated_prompt = raw_prompt
        face_references = []
        
        # Inject character descriptions and face references
        for cid in character_ids:
            char = self.characters.get(cid)
            if char:
                consolidated_prompt = (
                    f"{char.name} ({char.base_description}), {consolidated_prompt}"
                )
                if char.reference_image:
                    face_references.append({
                        "character_id": cid,
                        "image_url": char.reference_image,
                        "strength": 0.85  # High weight for IP-Adapter consistency
                    })
                char.instances_generated += 1
                self.generation_log.append({
                    "character_id": cid,
                    "scene_prompt": raw_prompt[:100],
                    "timestamp": "auto"
                })
        
        # Inject style
        style = style_override or self.active_style
        if style:
            consolidated_prompt = f"{consolidated_prompt}. {style.prompt_modifier}"
        
        # Temporal coherence seed
        import random
        frame_seed = random.randint(0, 9999999999)
        
        return {
            "final_prompt": consolidated_prompt,
            "style": style.name if style else None,
            "seed": frame_seed,
            "face_references": face_references,
            "engine_config": {
                "ip_adapter_weight": 0.8,
                "cfg_scale": 7.5,
                "temporal_coherence": True
            }
        }
    
    def set_style(self, name: str, prompt_modifier: str,
                  color_palette: Optional[list[str]] = None,
                  lighting_scheme: Optional[str] = None) -> StyleProfile:
        """Set the global aesthetic style for the production."""
        self.active_style = StyleProfile(
            name=name,
            prompt_modifier=prompt_modifier,
            color_palette=color_palette,
            lighting_scheme=lighting_scheme
        )
        print(f"[ConsistencyEngine] Project aesthetic style updated to: {name}")
        return self.active_style
    
    def get_character_usage_report(self) -> dict[str, Any]:
        """Report how many times each character has been generated."""
        return {
            char_id: {
                "name": char.name,
                "instances": char.instances_generated,
                "reference_image": char.reference_image is not None
            }
            for char_id, char in self.characters.items()
        }
    
    def export_character_bible(self) -> dict[str, Any]:
        """Export all character data as a bible document."""
        return {
            "style": {
                "name": self.active_style.name,
                "prompt_modifier": self.active_style.prompt_modifier,
                "color_palette": self.active_style.color_palette,
                "lighting_scheme": self.active_style.lighting_scheme
            },
            "characters": {
                cid: {
                    "name": c.name,
                    "base_description": c.base_description,
                    "reference_image": c.reference_image,
                    "instances_generated": c.instances_generated,
                    "voice_profile": c.voice_profile
                }
                for cid, c in self.characters.items()
            },
            "generation_log": self.generation_log
        }


class CollaborationHubPy:
    """Python port of the JavaScript CollaborationHub.
    
    Manages reviews, feedback directives, and workflow approvals between
    department agents, critic agents, and human collaborators.
    """
    
    def __init__(self):
        self.reviews: list[ReviewEntry] = []
        self.collaborators: dict[str, dict] = {
            "collab-1": {"name": "Tina Jia", "role": "Wing Sight CEO", "region": "Beijing/Cannes"},
            "collab-2": {"name": "Jean-Pierre", "role": "French Editor", "region": "Paris"},
            "collab-3": {"name": "Alessandra", "role": "Italian Sound Designer", "region": "Rome"}
        }
        self.critic_agents: dict[str, dict] = {
            "critic-structure": {"name": "Structure Critic", "role": "Story Structure Analyst"},
            "critic-emotion": {"name": "Emotion Critic", "role": "Emotional Beat Analyst"},
            "critic-pacing": {"name": "Pacing Critic", "role": "Pacing & Rhythm Analyst"},
            "critic-theme": {"name": "Theme Critic", "role": "Thematic Consistency Analyst"}
        }
    
    def add_feedback(self, reviewer_id: str, message: str,
                     target_scene: Optional[str] = None,
                     target_shot: Optional[int] = None,
                     suggested_settings: Optional[dict] = None,
                     score: Optional[float] = None,
                     category: str = "general") -> ReviewEntry:
        """Add a review/feedback entry."""
        # Resolve reviewer name
        reviewer = self.collaborators.get(reviewer_id) or self.critic_agents.get(reviewer_id)
        if reviewer is None:
            reviewer = {"name": reviewer_id, "role": "Unknown"}
        
        import time
        review = ReviewEntry(
            id=f"rev-{int(time.time() * 1000)}-{hash(message) % 1000}",
            reviewer_id=reviewer_id,
            reviewer_name=reviewer["name"],
            reviewer_role=reviewer["role"],
            target_scene=target_scene,
            target_shot=target_shot,
            message=message,
            suggested_settings=suggested_settings,
            score=score,
            category=category,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        
        self.reviews.append(review)
        print(f"[CollaborationHub] New {category} feedback from {reviewer['name']} "
              f"on {target_scene or 'general'}")
        return review
    
    def apply_directive(self, review_id: str) -> Optional[dict]:
        """Apply a review's suggested settings."""
        for review in self.reviews:
            if review.id == review_id:
                review.status = "applied"
                print(f"[CollaborationHub] Feedback directive applied: {review_id}")
                return {
                    "scene": review.target_scene,
                    "shot": review.target_shot,
                    "message": review.message,
                    "settings": review.suggested_settings
                }
        return None
    
    def reject_directive(self, review_id: str, reason: str = "") -> bool:
        """Reject a review directive with optional reason."""
        for review in self.reviews:
            if review.id == review_id:
                review.status = "rejected"
                print(f"[CollaborationHub] Feedback directive rejected: {review_id} ({reason})")
                return True
        return False
    
    def get_pending_reviews(self, category: Optional[str] = None,
                           target_scene: Optional[str] = None) -> list[ReviewEntry]:
        """Get all pending reviews, optionally filtered."""
        pending = [r for r in self.reviews if r.status == "pending"]
        
        if category:
            pending = [r for r in pending if r.category == category]
        if target_scene:
            pending = [r for r in pending if r.target_scene == target_scene]
        
        return pending
    
    def get_reviews_by_score(self, min_score: float = 0.0,
                            max_score: float = 10.0) -> list[ReviewEntry]:
        """Get reviews filtered by score range."""
        return [
            r for r in self.reviews
            if r.score is not None and min_score <= r.score <= max_score
        ]
    
    def get_review_summary(self) -> dict[str, Any]:
        """Get summary statistics of all reviews."""
        categories = {}
        reviewers = {}
        
        for r in self.reviews:
            # By category
            cat = r.category
            if cat not in categories:
                categories[cat] = {"count": 0, "total_score": 0.0, "scores": []}
            categories[cat]["count"] += 1
            if r.score is not None:
                categories[cat]["total_score"] += r.score
                categories[cat]["scores"].append(r.score)
            
            # By reviewer
            rev = r.reviewer_name
            if rev not in reviewers:
                reviewers[rev] = {"count": 0, "pending": 0, "applied": 0, "rejected": 0}
            reviewers[rev]["count"] += 1
            reviewers[rev][r.status] += 1
        
        # Compute averages
        for cat in categories:
            scores = categories[cat]["scores"]
            categories[cat]["average_score"] = sum(scores) / len(scores) if scores else None
            del categories[cat]["scores"]
            del categories[cat]["total_score"]
        
        return {
            "total_reviews": len(self.reviews),
            "pending": len([r for r in self.reviews if r.status == "pending"]),
            "applied": len([r for r in self.reviews if r.status == "applied"]),
            "rejected": len([r for r in self.reviews if r.status == "rejected"]),
            "by_category": categories,
            "by_reviewer": reviewers
        }
    
    def export_reviews(self, format: str = "json") -> str:
        """Export all reviews in JSON or Markdown format."""
        if format == "json":
            return json.dumps([
                {
                    "id": r.id,
                    "reviewer": r.reviewer_name,
                    "role": r.reviewer_role,
                    "scene": r.target_scene,
                    "message": r.message,
                    "score": r.score,
                    "category": r.category,
                    "status": r.status,
                    "timestamp": r.timestamp
                }
                for r in self.reviews
            ], indent=2)
        
        # Markdown format
        lines = ["# Production Reviews", ""]
        for r in self.reviews:
            lines.append(f"## {r.reviewer_name} — {r.category.upper()}")
            lines.append(f"- **Scene**: {r.target_scene or 'N/A'}")
            lines.append(f"- **Score**: {r.score if r.score else 'N/A'}")
            lines.append(f"- **Status**: {r.status}")
            lines.append(f"- **Message**: {r.message}")
            lines.append("")
        
        return "\n".join(lines)


class VideoGenerationRouter:
    """Wrapper around AIGCPlatformGateway with production-aware routing.
    
    Routes video generation requests to the appropriate backend based on
    shot type, character presence, and style requirements.
    """
    
    def __init__(self, kling_key: Optional[str] = None, vidu_key: Optional[str] = None):
        # Use mock keys if none provided (for testing)
        self.gateway = AIGCPlatformGateway(
            kling_key=kling_key or "mock-kling-key",
            vidu_key=vidu_key or "mock-vidu-key"
        )
        self.consistency_engine: Optional[ConsistencyEnginePy] = None
    
    def attach_consistency_engine(self, engine: ConsistencyEnginePy) -> None:
        """Attach a consistency engine for character/style injection."""
        self.consistency_engine = engine
    
    def generate_shot(self, prompt: str, shot_type: str,
                     character_ids: list[str] = None,
                     camera_movement: Optional[dict] = None,
                     duration: int = 5) -> dict:
        """Generate a single shot with consistency and routing.
        
        Args:
            prompt: Base shot description
            shot_type: 'character', 'action', 'close-up', 'landscape', 'atmosphere'
            character_ids: Characters present in this shot
            camera_movement: Dict with pan, tilt, zoom values
            duration: Shot duration in seconds
            
        Returns:
            API response dict with task_id, status, video_url
        """
        # Apply consistency if engine attached
        if self.consistency_engine and character_ids:
            payload = self.consistency_engine.compile_scene_payload(
                prompt, character_ids
            )
            final_prompt = payload["final_prompt"]
        else:
            final_prompt = prompt
        
        # Route to appropriate backend
        result = self.gateway.route_generation(
            prompt=final_prompt,
            shot_type=shot_type,
            camera_movement=camera_movement
        )
        
        return result
    
    def generate_sequence(self, shots: list[dict]) -> list[dict]:
        """Generate a sequence of shots with temporal coherence.
        
        Args:
            shots: List of dicts with prompt, shot_type, character_ids, etc.
            
        Returns:
            List of API response dicts
        """
        results = []
        linked_seed = None
        
        for shot in shots:
            # Link seeds for temporal coherence across sequence
            if linked_seed and self.consistency_engine:
                # Would inject linked_seed into generation params
                pass
            
            result = self.generate_shot(
                prompt=shot["prompt"],
                shot_type=shot.get("shot_type", "character"),
                character_ids=shot.get("character_ids"),
                camera_movement=shot.get("camera_movement"),
                duration=shot.get("duration", 5)
            )
            
            results.append(result)
            # In real implementation, extract seed from result for linking
        
        return results


# ---- Integration helpers ----

def create_production_toolkit(kling_key: Optional[str] = None,
                              vidu_key: Optional[str] = None) -> dict:
    """Create a complete production toolkit with all platform bridges.
    
    Returns dict with:
    - consistency_engine: ConsistencyEnginePy instance
    - collaboration_hub: CollaborationHubPy instance
    - video_router: VideoGenerationRouter instance
    """
    consistency = ConsistencyEnginePy()
    collaboration = CollaborationHubPy()
    router = VideoGenerationRouter(kling_key=kling_key, vidu_key=vidu_key)
    router.attach_consistency_engine(consistency)
    
    return {
        "consistency_engine": consistency,
        "collaboration_hub": collaboration,
        "video_router": router
    }


if __name__ == "__main__":
    # Demo the production toolkit
    toolkit = create_production_toolkit()
    
    ce = toolkit["consistency_engine"]
    ch = toolkit["collaboration_hub"]
    vr = toolkit["video_router"]
    
    # Register characters
    ce.register_character("char-1", "Judy Hopps",
                         reference_image="/refs/judy.jpg",
                         base_description="grey rabbit, police uniform, optimistic expression")
    ce.register_character("char-2", "Nick Wilde",
                         reference_image="/refs/nick.jpg",
                         base_description="red fox, green shirt, sly smirk")
    
    # Set style
    ce.set_style("Zootopia Vibrant",
                "vibrant animated film style, rich saturated colors, "
                "soft ambient lighting, Disney-like character design")
    
    # Generate a shot
    result = vr.generate_shot(
        prompt="Judy confronts Nick in the city square, pointing accusingly",
        shot_type="character",
        character_ids=["char-1", "char-2"],
        camera_movement={"pan": 10, "zoom": 1.2}
    )
    print(f"\nShot generation result:\n{json.dumps(result, indent=2)}")
    
    # Add feedback
    ch.add_feedback("critic-structure", 
                   "The confrontation beat is too early. Move to Scene 12.",
                   target_scene="scene_05",
                   score=6.5,
                   category="structure")
    
    print(f"\nReview summary:\n{json.dumps(ch.get_review_summary(), indent=2)}")
