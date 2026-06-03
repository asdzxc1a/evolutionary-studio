import json
import time
import uuid
import random

class KlingAPIAdapter:
    """
    Adapter for Kuaishou's Kling AI Video Generation API.
    Known strengths: Motion control, lip-sync, camera path adjustments.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.klingai.com/v1"

    def submit_video_task(self, prompt: str, camera_config: dict, duration: int = 5, aspect_ratio: str = "16:9") -> dict:
        """
        Submits a video generation task to Kling AI.
        """
        print(f"[Kling API] Submitting task with prompt: '{prompt}'")
        print(f"[Kling API] Camera configuration: {json.dumps(camera_config)}")
        
        # Simulate API submission response
        task_id = f"kling-task-{uuid.uuid4()}"
        return {
            "code": 200,
            "message": "success",
            "data": {
                "task_id": task_id,
                "status": "SUBMITTED",
                "estimated_time_seconds": 45
            }
        }

    def query_task_status(self, task_id: str) -> dict:
        """
        Queries the status of a Kling AI generation task.
        """
        # Mock status updates based on task ID randomness
        stages = ["PROCESSING", "PROCESSING", "COMPLETED"]
        status = random.choice(stages)
        
        if status == "COMPLETED":
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "task_id": task_id,
                    "status": "COMPLETED",
                    "video_url": f"https://assets.ai-platform.internal/videos/{task_id}.mp4",
                    "cover_url": f"https://assets.ai-platform.internal/covers/{task_id}.jpg",
                    "duration_seconds": 5
                }
            }
        else:
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "task_id": task_id,
                    "status": "PROCESSING",
                    "progress": random.randint(30, 80)
                }
            }


class ViduAPIAdapter:
    """
    Adapter for Shengshu Technology's Vidu Video Generation API.
    Known strengths: Physical accuracy, cinematic lighting, spatial consistency.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.vidu.com/v2"

    def submit_video_task(self, prompt: str, physics_weight: float = 1.0, duration: int = 4, aspect_ratio: str = "16:9") -> dict:
        """
        Submits a video generation task to Vidu.
        """
        print(f"[Vidu API] Submitting task with prompt: '{prompt}'")
        print(f"[Vidu API] Physics guidance weight: {physics_weight}")
        
        task_id = f"vidu-task-{uuid.uuid4()}"
        return {
            "status": "ok",
            "task": {
                "id": task_id,
                "state": "pending",
                "created_at": int(time.time())
            }
        }

    def query_task_status(self, task_id: str) -> dict:
        """
        Queries the status of a Vidu generation task.
        """
        stages = ["processing", "completed"]
        state = random.choice(stages)
        
        if state == "completed":
            return {
                "status": "ok",
                "task": {
                    "id": task_id,
                    "state": "completed",
                    "result": {
                        "video_url": f"https://assets.ai-platform.internal/videos/{task_id}.mp4",
                        "duration": 4,
                        "resolution": "1920x1080"
                    }
                }
            }
        else:
            return {
                "status": "ok",
                "task": {
                    "id": task_id,
                    "state": "processing",
                    "percent_complete": random.randint(40, 90)
                }
            }


class AIGCPlatformGateway:
    """
    Unified entry point for our platform. 
    Routes requests to Kling or Vidu depending on the requirements of the shot.
    """
    def __init__(self, kling_key: str, vidu_key: str):
        self.kling = KlingAPIAdapter(kling_key)
        self.vidu = ViduAPIAdapter(vidu_key)

    def route_generation(self, prompt: str, shot_type: str, camera_movement: dict = None) -> dict:
        """
        Intelligently routes the shot based on type:
        - Character-driven, action, lip-sync -> Kling
        - Atmospheric, physics-heavy, scenery -> Vidu
        """
        if shot_type.lower() in ["character", "action", "close-up"]:
            camera_config = camera_movement or {"pan": 0, "tilt": 0, "zoom": 1.0}
            return {
                "routed_to": "Kling AI",
                "response": self.kling.submit_video_task(prompt, camera_config)
            }
        else:
            return {
                "routed_to": "Vidu",
                "response": self.vidu.submit_video_task(prompt, physics_weight=1.2)
            }


# Local script execution for testing and simulation
if __name__ == "__main__":
    print("=== AIGC Platform Gateway Simulation ===")
    gateway = AIGCPlatformGateway(kling_key="mock-kling-key-123", vidu_key="mock-vidu-key-abc")
    
    # Test Kling routing (character-driven)
    print("\n--- Test 1: Routing a Character Action Shot ---")
    kling_result = gateway.route_generation(
        prompt="A young director in a Parisian cafe, talking expressively, cinematic lighting.",
        shot_type="character",
        camera_movement={"pan": 15, "tilt": 0, "zoom": 1.1}
    )
    print("Result:", json.dumps(kling_result, indent=2))
    
    # Test Vidu routing (scenery/physics)
    print("\n--- Test 2: Routing a Physics/Landscape Shot ---")
    vidu_result = gateway.route_generation(
        prompt="Slow motion water droplets splashing on ancient stone, macro lens.",
        shot_type="landscape"
    )
    print("Result:", json.dumps(vidu_result, indent=2))
