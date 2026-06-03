"""Pydantic models for the Evolutionary Studio API."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel


class ProduceRequest(BaseModel):
    """Request body for starting a production."""
    dna_source: str = "memory/films_analyzed/zootopia_dna.md"
    setting: str
    group_a: str = "robot"
    group_b: str = "human"
    theme: str
    metaphor: Optional[str] = None
    genre: str = "animated comedy-drama"
    n_concepts: int = 4
    n_rounds: int = 1
    budget: float = 50.0
    production_id: Optional[str] = None


class ProduceResponse(BaseModel):
    """Response from starting a production."""
    production_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    """Production status response."""
    production_id: Optional[str]
    phase: str
    evolution_stats: dict[str, Any]
    swarm_stats: dict[str, Any]
    total_cost: float
    budget_remaining: float


class ScoreBreakdown(BaseModel):
    """Individual category scores."""
    score: float
    notes: str
    issues: list[str] = []
    strengths: list[str] = []


class ConceptItem(BaseModel):
    """A concept in the list."""
    id: str
    title: str
    logline: str
    genre: str
    setting: str
    theme: str
    combined_score: Optional[float] = None
    scores: Optional[dict[str, ScoreBreakdown]] = None
    status: str


class ReviewItem(BaseModel):
    """A review entry."""
    id: str
    reviewer: str
    category: str
    score: Optional[float]
    message: str
    status: str
    target_scene: Optional[str]


class VaultNote(BaseModel):
    """A note from the vault."""
    path: str
    title: str
    tags: list[str]
    frontmatter: dict[str, Any]
    content_preview: str


class PackageResponse(BaseModel):
    """Full production package."""
    production_id: str
    concept: dict[str, Any]
    screenplay: dict[str, Any]
    characters: list[dict[str, Any]]
    environments: list[dict[str, Any]]
    shot_lists: list[dict[str, Any]]
    scenes: list[dict[str, Any]]
    reviews: dict[str, Any]
    cost_report: dict[str, float]
    generated_at: str
