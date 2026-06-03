"""
Component 7 — Delegation: Route to Best Model

The task routing system. Delegation decides which AI model handles each
generation task based on:
    - rendering_hints.preferred_models (user preferences)
    - Task type (closeup vs. establishing vs. dialogue)
    - Budget constraints (budget_mode, max_cost_usd)
    - Model availability and rate limits
    - Historical quality scores per model per task type

Delegation also manages:
    - API key rotation and rate limiting
    - Fallback chains (if preferred model fails)
    - Cost tracking and budget enforcement
    - Parallel request orchestration
"""

# TODO: Implement
# - Model registry (capabilities, costs, rate limits)
# - Task-to-model matching algorithm
# - API client pool management
# - Cost tracking and budget alerts
# - Fallback chain execution
