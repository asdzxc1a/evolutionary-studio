"""System 3: The Evolutionary Studio — Parallel Production Swarm.

A compiler that generates competing story concepts, prototypes key scenes,
runs critic agents, and iterates through selection pressure to converge
on a production-ready story package.
"""

from .evolution_engine import (
    StoryEvolutionEngine,
    ConceptGenerator,
    PrototypeEngine,
    CriticSwarm,
    SelectionEngine,
    Concept,
    Prototype,
    CriticScore,
)

__all__ = [
    "StoryEvolutionEngine",
    "ConceptGenerator",
    "PrototypeEngine",
    "CriticSwarm",
    "SelectionEngine",
    "Concept",
    "Prototype",
    "CriticScore",
]
