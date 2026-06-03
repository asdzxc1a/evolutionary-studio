"""OpenMontage Bridge — Tool Execution Layer for the Evolutionary Studio.

Wraps OpenMontage's ToolRegistry and BaseTool to provide a clean Python API
for System 3 department agents. Handles tool discovery, execution, cost tracking,
and result normalization.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass

# Add openmontage to Python path
OPENMONTAGE_ROOT = Path(__file__).resolve().parent.parent / "openmontage"
if str(OPENMONTAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(OPENMONTAGE_ROOT))

from tools.base_tool import BaseTool, ToolResult, ToolStatus
from tools.tool_registry import ToolRegistry, registry as _om_registry
from tools.cost_tracker import CostTracker  # Will be available after discovery


@dataclass
class ToolExecution:
    """Normalized result from executing an OpenMontage tool."""
    tool_name: str
    success: bool
    data: dict[str, Any]
    artifacts: list[str]
    error: Optional[str] = None
    cost_usd: float = 0.0
    duration_seconds: float = 0.0
    
    @property
    def artifact_paths(self) -> list[Path]:
        """Get artifact paths as Path objects."""
        return [Path(a) for a in self.artifacts]


class OpenMontageBridge:
    """Bridge to OpenMontage tool ecosystem.
    
    Provides:
    - Tool discovery and capability queries
    - Tool execution with unified result format
    - Cost tracking across all department agents
    - Fallback tool resolution
    """
    
    def __init__(self, openmontage_root: Optional[Path] = None):
        self.om_root = openmontage_root or OPENMONTAGE_ROOT
        self.registry = ToolRegistry()
        self._discovered = False
        self._cost_tracker: Optional[Any] = None
        
        # Ensure we're in the right directory for imports
        self._original_cwd = os.getcwd()
        
    def discover(self) -> list[str]:
        """Discover all available tools in OpenMontage."""
        os.chdir(self.om_root)
        try:
            discovered = self.registry.discover("tools")
            self._discovered = True
            
            # Try to get cost tracker
            try:
                from tools.cost_tracker import CostTracker
                self._cost_tracker = CostTracker()
            except ImportError:
                self._cost_tracker = None
            
            return discovered
        finally:
            os.chdir(self._original_cwd)
    
    def ensure_discovered(self) -> None:
        """Ensure tools are discovered."""
        if not self._discovered:
            self.discover()
    
    # ---- Tool Discovery ----
    
    def list_tools(self) -> list[str]:
        """List all discovered tool names."""
        self.ensure_discovered()
        return self.registry.list_all()
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        self.ensure_discovered()
        return self.registry.get(name)
    
    def get_available_tools(self) -> list[BaseTool]:
        """Get all currently available tools."""
        self.ensure_discovered()
        return self.registry.get_available()
    
    def find_tools_for_capability(self, capability: str) -> list[BaseTool]:
        """Find tools that support a specific capability."""
        self.ensure_discovered()
        return self.registry.find_by_capability(capability)
    
    def get_provider_menu(self) -> dict[str, Any]:
        """Get the provider menu for preflight."""
        self.ensure_discovered()
        return self.registry.provider_menu()
    
    def get_capability_catalog(self) -> dict[str, list[dict[str, Any]]]:
        """Get tools grouped by capability."""
        self.ensure_discovered()
        return self.registry.capability_catalog()
    
    # ---- Tool Execution ----
    
    def execute(self, tool_name: str, inputs: dict[str, Any],
                dry_run: bool = False) -> ToolExecution:
        """Execute a tool by name with given inputs.
        
        Args:
            tool_name: Name of the tool to execute
            inputs: Tool inputs as a dict
            dry_run: If True, run preflight without side effects
            
        Returns:
            ToolExecution with normalized result
        """
        self.ensure_discovered()
        
        tool = self.registry.get(tool_name)
        if tool is None:
            return ToolExecution(
                tool_name=tool_name,
                success=False,
                data={},
                artifacts=[],
                error=f"Tool '{tool_name}' not found in registry"
            )
        
        # Check availability
        if tool.get_status() != ToolStatus.AVAILABLE:
            # Try fallback
            fallback = self.registry.find_fallback(tool_name)
            if fallback:
                print(f"[Bridge] Tool '{tool_name}' unavailable, using fallback '{fallback.name}'")
                tool = fallback
            else:
                return ToolExecution(
                    tool_name=tool_name,
                    success=False,
                    data={},
                    artifacts=[],
                    error=f"Tool '{tool_name}' unavailable and no fallback found"
                )
        
        os.chdir(self.om_root)
        try:
            if dry_run:
                result_data = tool.dry_run(inputs)
                return ToolExecution(
                    tool_name=tool_name,
                    success=True,
                    data=result_data,
                    artifacts=[],
                    cost_usd=result_data.get("estimated_cost_usd", 0.0),
                    duration_seconds=result_data.get("estimated_runtime_seconds", 0.0)
                )
            
            result: ToolResult = tool.execute(inputs)
            
            return ToolExecution(
                tool_name=tool_name,
                success=result.success,
                data=result.data,
                artifacts=result.artifacts,
                error=result.error,
                cost_usd=result.cost_usd,
                duration_seconds=result.duration_seconds
            )
            
        except Exception as e:
            return ToolExecution(
                tool_name=tool_name,
                success=False,
                data={},
                artifacts=[],
                error=f"Execution error: {str(e)}"
            )
        finally:
            os.chdir(self._original_cwd)
    
    def execute_batch(self, tasks: list[tuple[str, dict[str, Any]]],
                      stop_on_error: bool = False) -> list[ToolExecution]:
        """Execute multiple tools in sequence.
        
        Args:
            tasks: List of (tool_name, inputs) tuples
            stop_on_error: If True, stop at first failure
            
        Returns:
            List of ToolExecution results
        """
        results = []
        for tool_name, inputs in tasks:
            result = self.execute(tool_name, inputs)
            results.append(result)
            
            if stop_on_error and not result.success:
                break
        
        return results
    
    # ---- Cost Tracking ----
    
    def estimate_cost(self, tool_name: str, inputs: dict[str, Any]) -> float:
        """Estimate cost for a tool execution."""
        self.ensure_discovered()
        tool = self.registry.get(tool_name)
        if tool is None:
            return 0.0
        return tool.estimate_cost(inputs)
    
    def get_total_cost(self) -> float:
        """Get total cost across all tracked executions."""
        if self._cost_tracker:
            return self._cost_tracker.total_usd()
        return 0.0
    
    # ---- Convenience methods for department agents ----
    
    def generate_image(self, prompt: str, width: int = 1024, height: int = 1024,
                       output_path: Optional[str] = None,
                       provider: str = "flux") -> ToolExecution:
        """Generate an image using the best available image generation tool."""
        inputs = {
            "prompt": prompt,
            "width": width,
            "height": height
        }
        if output_path:
            inputs["output_path"] = output_path
        
        # Try providers in order of preference
        providers = [f"{provider}_image", "flux_image", "image_generation"]
        for p in providers:
            if self.registry.get(p):
                return self.execute(p, inputs)
        
        return ToolExecution(
            tool_name="image_generation",
            success=False,
            data={},
            artifacts=[],
            error="No image generation tool available"
        )
    
    def generate_video(self, prompt: str, duration: int = 5,
                       aspect_ratio: str = "16:9",
                       provider: str = "wan") -> ToolExecution:
        """Generate a video clip using the best available video generation tool."""
        inputs = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }
        
        providers = [f"{provider}_video", "wan_video", "anisora_video", 
                     "seedance_video", "video_generation"]
        for p in providers:
            if self.registry.get(p):
                return self.execute(p, inputs)
        
        return ToolExecution(
            tool_name="video_generation",
            success=False,
            data={},
            artifacts=[],
            error="No video generation tool available"
        )
    
    def generate_audio(self, text: str, voice_id: Optional[str] = None,
                       provider: str = "piper") -> ToolExecution:
        """Generate audio/TTS using the best available tool."""
        inputs = {"text": text}
        if voice_id:
            inputs["voice_id"] = voice_id
        
        providers = [f"{provider}_tts", "piper_tts", "cosyvoice_tts", 
                     "elevenlabs_tts", "audio_generation"]
        for p in providers:
            if self.registry.get(p):
                return self.execute(p, inputs)
        
        return ToolExecution(
            tool_name="audio_generation",
            success=False,
            data={},
            artifacts=[],
            error="No audio generation tool available"
        )
    
    def generate_music(self, prompt: str, duration: int = 30,
                       provider: str = "suno") -> ToolExecution:
        """Generate music using the best available tool."""
        inputs = {
            "prompt": prompt,
            "duration": duration
        }
        
        providers = [f"{provider}_music", "suno_music", "udio_music", "music_generation"]
        for p in providers:
            if self.registry.get(p):
                return self.execute(p, inputs)
        
        return ToolExecution(
            tool_name="music_generation",
            success=False,
            data={},
            artifacts=[],
            error="No music generation tool available"
        )
    
    def compose_video(self, inputs: list[str], output_path: str,
                      transitions: Optional[list[str]] = None) -> ToolExecution:
        """Compose multiple video clips into one."""
        tool_inputs = {
            "inputs": inputs,
            "output_path": output_path
        }
        if transitions:
            tool_inputs["transitions"] = transitions
        
        return self.execute("video_compose", tool_inputs)
    
    def stitch_video(self, clips: list[str], output_path: str) -> ToolExecution:
        """Stitch video clips together."""
        return self.execute("video_stitch", {
            "clips": clips,
            "output_path": output_path
        })


# ---- Singleton ----

_bridge_instance: Optional[OpenMontageBridge] = None


def get_bridge() -> OpenMontageBridge:
    """Get the default OpenMontage bridge instance."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = OpenMontageBridge()
    return _bridge_instance


if __name__ == "__main__":
    bridge = get_bridge()
    discovered = bridge.discover()
    print(f"Discovered {len(discovered)} tools")
    
    available = bridge.get_available_tools()
    print(f"Available: {len(available)} tools")
    
    # Show capability catalog
    catalog = bridge.get_capability_catalog()
    for cap, tools in catalog.items():
        print(f"\n  {cap}: {len(tools)} tools")
        for t in tools[:3]:
            print(f"    - {t['name']} ({t['provider']}) [{t['status']}]")
