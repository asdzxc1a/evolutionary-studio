"""FastAPI server for the Evolutionary Studio frontend.

Provides REST endpoints for:
- Starting productions
- Checking status
- Retrieving results
- Browsing the vault
"""

from __future__ import annotations

import json
import sys
import os
import uuid
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from api.models import (
    ProduceRequest, ProduceResponse, StatusResponse,
    ConceptItem, ReviewItem, VaultNote, PackageResponse
)

# System 3 imports
from system3.evolution_controller import EvolutionController, ProductionPackage
from bridge.obsidian_bridge import ObsidianBridge, get_bridge

# System 4 imports
from system4.long_term_memory import LongTermMemory, SearchResult


# =============================================================================
# Long-Term Memory singleton
# =============================================================================

_ltm: Optional[LongTermMemory] = None


def get_ltm() -> LongTermMemory:
    global _ltm
    if _ltm is None:
        _ltm = LongTermMemory()
    return _ltm


# =============================================================================
# In-memory production store
# =============================================================================

_productions: dict[str, dict[str, Any]] = {}
_bridge: Optional[ObsidianBridge] = None


def get_obsidian_bridge() -> ObsidianBridge:
    global _bridge
    if _bridge is None:
        _bridge = get_bridge(str(PROJECT_ROOT / "studio"))
    return _bridge


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Evolutionary Studio API",
    description="System 3 — AI Animation Production Pipeline",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (frontend)
frontend_path = PROJECT_ROOT / "frontend" / "static"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


# =============================================================================
# Background task: run production
# =============================================================================

def _run_production(production_id: str, req: ProduceRequest) -> None:
    """Run the production pipeline in background."""
    try:
        _productions[production_id]["status"] = "running"
        _productions[production_id]["phase"] = "evolution"
        
        metaphor = req.metaphor or f"{req.group_a}/{req.group_b} dynamics mirror real-world prejudice"
        constraints = {
            "setting": req.setting,
            "group_a": req.group_a,
            "group_b": req.group_b,
            "theme": req.theme,
            "social_metaphor": metaphor,
            "genre": req.genre
        }
        
        controller = EvolutionController(
            obsidian_bridge=get_obsidian_bridge(),
            n_concepts=req.n_concepts,
            n_rounds=req.n_rounds,
            budget_usd=req.budget
        )
        
        package = controller.produce(
            dna_source=req.dna_source,
            constraints=constraints,
            production_id=production_id
        )
        
        _productions[production_id]["status"] = "complete"
        _productions[production_id]["phase"] = "done"
        _productions[production_id]["package"] = package
        _productions[production_id]["controller"] = controller
        _productions[production_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        _productions[production_id]["status"] = "failed"
        _productions[production_id]["error"] = str(e)
        print(f"[ERROR] Production {production_id} failed: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# Routes
# =============================================================================

@app.get("/", response_class=HTMLResponse)
def root() -> str:
    """Serve the main frontend app."""
    index_path = PROJECT_ROOT / "frontend" / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Evolutionary Studio API</h1><p>Frontend not built yet.</p>"


@app.post("/api/produce", response_model=ProduceResponse)
def produce(req: ProduceRequest, background_tasks: BackgroundTasks) -> ProduceResponse:
    """Start a new production."""
    production_id = req.production_id or f"prod-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    
    _productions[production_id] = {
        "id": production_id,
        "status": "queued",
        "phase": "queued",
        "started_at": datetime.now().isoformat(),
        "package": None,
        "controller": None,
        "error": None
    }
    
    background_tasks.add_task(_run_production, production_id, req)
    
    return ProduceResponse(
        production_id=production_id,
        status="queued",
        message="Production started in background. Check /api/status/{id} for progress."
    )


def _load_status_from_vault(production_id: str) -> Optional[dict[str, Any]]:
    """Load production status from vault post-mortem."""
    bridge = get_obsidian_bridge()
    pm = bridge.read_note(f"memory/post_mortems/post_mortem_{production_id}.md")
    if not pm:
        return None
    
    return {
        "production_id": production_id,
        "phase": "complete",
        "evolution_stats": {
            "concepts_generated": pm.frontmatter.get("concepts_generated", 0),
            "rounds": pm.frontmatter.get("rounds", 1),
        },
        "swarm_stats": {
            "total_tasks": pm.frontmatter.get("total_tasks", 0),
            "completed_tasks": pm.frontmatter.get("completed_tasks", 0),
        },
        "total_cost": 0.0,
        "budget_remaining": 50.0,
    }


@app.get("/api/status/{production_id}", response_model=StatusResponse)
def get_status(production_id: str) -> StatusResponse:
    """Get production status."""
    prod = _productions.get(production_id)
    if prod:
        controller = prod.get("controller")
        if controller and hasattr(controller, 'get_status'):
            ctrl_status = controller.get_status()
        else:
            ctrl_status = {
                "production_id": production_id,
                "phase": prod.get("phase", "unknown"),
                "evolution_stats": {},
                "swarm_stats": {},
                "total_cost": 0.0,
                "budget_remaining": 50.0
            }
        
        return StatusResponse(
            production_id=production_id,
            phase=prod.get("phase", "unknown"),
            evolution_stats=ctrl_status.get("evolution_stats", {}),
            swarm_stats=ctrl_status.get("swarm_stats", {}),
            total_cost=ctrl_status.get("total_cost", 0.0),
            budget_remaining=ctrl_status.get("budget_remaining", 50.0)
        )
    
    # Fall back to vault
    vault_status = _load_status_from_vault(production_id)
    if vault_status:
        return StatusResponse(**vault_status)
    
    raise HTTPException(status_code=404, detail="Production not found")


def _load_package_from_vault(production_id: str) -> Optional[dict[str, Any]]:
    """Load a production package from vault files."""
    bridge = get_obsidian_bridge()
    
    # Try to find package note
    pkg_note = bridge.read_note(f"memory/post_mortems/package_{production_id}.md")
    if not pkg_note:
        return None
    
    # Build package dict from vault files
    result: dict[str, Any] = {
        "status": "complete",
        "production_id": production_id,
        "concept": {},
        "screenplay": "",
        "characters": [],
        "environments": [],
        "scenes": [],
        "shot_lists": [],
        "reviews": [],
        "director_decision": None,
        "generated_at": pkg_note.frontmatter.get("generated_at", ""),
    }
    
    # Load concept
    concept_id = pkg_note.frontmatter.get("concept_id")
    if concept_id:
        concept_note = bridge.read_note(f"concepts/{concept_id}.md")
        if concept_note:
            result["concept"] = {
                "id": concept_id,
                "title": concept_note.title,
                "logline": concept_note.frontmatter.get("logline", ""),
                "genre": concept_note.frontmatter.get("genre", ""),
                "setting": concept_note.frontmatter.get("setting", ""),
                "theme": concept_note.frontmatter.get("theme", ""),
            }
    
    # Load characters
    char_notes = bridge.query_notes(folder="characters")
    for cn in char_notes:
        if "_voice.md" not in cn.path:
            result["characters"].append({
                "name": cn.frontmatter.get("name", cn.title),
                "archetype": cn.frontmatter.get("archetype", ""),
                "role": cn.frontmatter.get("role", ""),
            })
    
    # Load environments
    env_notes = bridge.query_notes(folder="characters/environments")
    for en in env_notes:
        result["environments"].append({
            "name": en.frontmatter.get("name", en.title),
            "type": en.frontmatter.get("type", ""),
        })
    
    # Load scenes (screenplay)
    scene_notes = bridge.query_notes(folder="scenes")
    for sn in scene_notes:
        result["scenes"].append({
            "scene_number": sn.frontmatter.get("scene_number", 0),
            "title": sn.title,
            "slugline": sn.frontmatter.get("slugline", ""),
            "content": sn.content[:500] + "..." if len(sn.content) > 500 else sn.content,
        })
        result["screenplay"] += f"\n\n{sn.content}"
    
    # Load director decision
    decision_note = bridge.read_note(f"reviews/director_decision_{production_id}.md")
    if decision_note:
        result["director_decision"] = {
            "verdict": decision_note.frontmatter.get("verdict", "unknown"),
            "confidence": decision_note.frontmatter.get("confidence", 0.0),
            "reason": decision_note.frontmatter.get("reason", ""),
            "reviewed_at": decision_note.frontmatter.get("reviewed_at", ""),
        }
    
    return result


@app.get("/api/package/{production_id}")
def get_package(production_id: str) -> dict[str, Any]:
    """Get the full production package."""
    prod = _productions.get(production_id)
    if prod:
        package = prod.get("package")
        if package:
            return package.to_dict()
        return {"status": prod.get("status"), "message": "Package not ready yet"}
    
    # Fall back to vault
    vault_package = _load_package_from_vault(production_id)
    if vault_package:
        return vault_package
    
    raise HTTPException(status_code=404, detail="Production not found")


@app.get("/api/concepts")
def list_concepts() -> list[ConceptItem]:
    """List all concepts in the vault with evaluation scores."""
    bridge = get_obsidian_bridge()
    notes = bridge.query_notes(folder="concepts")
    
    # Load all evaluations for score lookup
    eval_notes = bridge.query_notes(folder="reviews")
    evaluations = {}
    for en in eval_notes:
        if "evaluation_" in en.path:
            concept_id = en.frontmatter.get("concept_id")
            if concept_id:
                evaluations[concept_id] = en.frontmatter.get("scores", {})
    
    items = []
    for note in notes:
        if note.frontmatter.get("status") == "winner":
            status = "winner"
        else:
            status = note.frontmatter.get("status", "pending")
        
        concept_id = note.frontmatter.get("concept_id", note.path)
        eval_scores = evaluations.get(concept_id)
        
        # Parse combined score from evaluation
        combined_score = None
        scores = None
        if eval_scores:
            combined_score = eval_scores.get("_combined")
            if combined_score is None:
                # Calculate from individual scores
                individual = {k: v for k, v in eval_scores.items() if isinstance(v, dict) and "score" in v}
                if individual:
                    combined_score = sum(v["score"] for v in individual.values()) / len(individual)
            scores = eval_scores
        
        items.append(ConceptItem(
            id=concept_id,
            title=note.title,
            logline=note.frontmatter.get("logline", ""),
            genre=note.frontmatter.get("genre", ""),
            setting=note.frontmatter.get("setting", ""),
            theme=note.frontmatter.get("theme", ""),
            combined_score=round(combined_score, 1) if combined_score else None,
            scores=scores,
            status=status
        ))
    
    return items


@app.get("/api/concepts/{concept_id}")
def get_concept(concept_id: str) -> dict[str, Any]:
    """Get a specific concept."""
    bridge = get_obsidian_bridge()
    note = bridge.read_note(f"concepts/{concept_id}.md")
    if not note:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    return {
        "path": note.path,
        "title": note.title,
        "frontmatter": note.frontmatter,
        "content": note.content,
        "tags": note.tags
    }


@app.get("/api/reviews")
def list_reviews() -> list[ReviewItem]:
    """List all reviews."""
    bridge = get_obsidian_bridge()
    notes = bridge.query_notes(folder="reviews")
    
    items = []
    for note in notes:
        if "selection" in note.path:
            continue  # Skip selection reports
        items.append(ReviewItem(
            id=note.frontmatter.get("review_id", note.path),
            reviewer=note.frontmatter.get("reviewer", "Unknown"),
            category=note.frontmatter.get("category", "general"),
            score=note.frontmatter.get("score"),
            message=note.content[:200],
            status=note.frontmatter.get("status", "pending"),
            target_scene=note.frontmatter.get("target_scene")
        ))
    
    return items


@app.get("/api/vault")
def browse_vault(folder: Optional[str] = None) -> list[VaultNote]:
    """Browse the Obsidian vault."""
    bridge = get_obsidian_bridge()
    notes = bridge.get_all_notes(folder=folder)
    
    items = []
    for note in notes:
        items.append(VaultNote(
            path=note.path,
            title=note.title,
            tags=note.tags,
            frontmatter=note.frontmatter,
            content_preview=note.content[:300] + "..." if len(note.content) > 300 else note.content
        ))
    
    return items


@app.get("/api/vault/{path:path}")
def read_vault_note(path: str) -> dict[str, Any]:
    """Read a specific vault note."""
    bridge = get_obsidian_bridge()
    note = bridge.read_note(path)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {
        "path": note.path,
        "title": note.title,
        "frontmatter": note.frontmatter,
        "content": note.content,
        "tags": note.tags,
        "backlinks": note.backlinks
    }


# =============================================================================
# Memory (Vector Search) Endpoints
# =============================================================================

@app.get("/api/memory/search")
def memory_search(
    q: str,
    doc_type: Optional[str] = None,
    production_id: Optional[str] = None,
    n: int = 10,
) -> dict[str, Any]:
    """Semantic search across all studio memory."""
    ltm = get_ltm()
    doc_types = [dt.strip() for dt in doc_type.split(",")] if doc_type else None
    
    results = ltm.search(
        query=q,
        doc_types=doc_types,
        production_id=production_id,
        n_results=n,
    )
    
    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "id": r.id,
                "text": r.text,
                "doc_type": r.doc_type,
                "score": r.score,
                "metadata": r.metadata,
            }
            for r in results
        ]
    }


@app.get("/api/memory/stats")
def memory_stats() -> dict[str, Any]:
    """Get vector memory statistics."""
    return get_ltm().stats()


@app.post("/api/memory/ingest")
def memory_ingest(production_id: Optional[str] = None) -> dict[str, Any]:
    """Ingest vault documents into vector memory."""
    ltm = get_ltm()
    if production_id:
        counts = ltm.ingest_production(production_id)
    else:
        counts = ltm.ingest_vault()
    
    return {
        "status": "ok",
        "production_id": production_id,
        "counts": counts,
        "total": sum(counts.values()),
    }


@app.get("/api/emotional/{production_id}")
def get_emotional_analysis(production_id: str) -> dict[str, Any]:
    """Get emotional model analysis for a production."""
    bridge = get_obsidian_bridge()
    note = bridge.read_note(f"reviews/emotional_analysis_{production_id}.md")
    if not note:
        raise HTTPException(status_code=404, detail="Emotional analysis not found")
    
    return {
        "production_id": production_id,
        "arc": note.frontmatter.get("arc", "unknown"),
        "score": note.frontmatter.get("score", 0),
        "valence_range": note.frontmatter.get("valence_range", 0),
        "climax_score": note.frontmatter.get("climax_score", 0),
        "content": note.content,
    }


@app.get("/api/concerns/{production_id}")
def get_concerns(production_id: str) -> dict[str, Any]:
    """Get diffused attention concerns for a production."""
    bridge = get_obsidian_bridge()
    note = bridge.read_note(f"reviews/diffused_attention_{production_id}.md")
    if not note:
        raise HTTPException(status_code=404, detail="Concerns not found")
    
    return {
        "production_id": production_id,
        "concerns_count": note.frontmatter.get("concerns_count", 0),
        "critical_count": note.frontmatter.get("critical_count", 0),
        "content": note.content,
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok", "version": "0.1.0"}


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
