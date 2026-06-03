# Animation Genome Machine

> A compiler-based system that transforms structured Film Genome Documents into production-ready animated films using AI.

## What Is This?

The Animation Genome Machine treats filmmaking like software engineering. Instead of writing code that compiles to machine instructions, you write a **Film Genome Document** (YAML) that compiles into a rendered animated film.

A Film Genome Document encodes the complete DNA of a film — narrative structure, character design, visual style, pacing, audio, and scene-by-scene shot plans — in a single, machine-readable specification.

## Two-System Architecture

### System 1: The Film Compiler

A 6-phase pipeline that transforms a Film Genome Document into executable render plans:

| Phase | Module | Function |
|-------|--------|----------|
| 1 — Lexer | `compiler/lexer.py` | Parse YAML → structured tokens |
| 2 — Parser | `compiler/parser.py` | Tokens → Abstract Syntax Tree (AST) |
| 3 — Analyzer | `compiler/analyzer.py` | Validate AST (arc coherence, budget feasibility) |
| 4 — Optimizer | `compiler/optimizer.py` | Generate render plan (batch similar shots, optimize cost) |
| 5 — Code Generator | `compiler/codegen.py` | Emit ComfyUI workflows + API calls |
| 6 — Linker | `compiler/linker.py` | Assemble final film (stitch, audio sync, transitions) |

### System 2: The Creative Loop (Engine)

Seven cognitive components that power the AI creative process:

| Component | Module | Function |
|-----------|--------|----------|
| Perception | `engine/perception.py` | Watch reference films, read scripts, analyze images |
| Understanding | `engine/understanding.py` | Extract Film DNA from existing works |
| Generation | `engine/generation.py` | Create new content (images, audio, video) |
| Judgment | `engine/judgment.py` | Evaluate quality against the genome spec |
| Correction | `engine/correction.py` | Fix issues (regenerate, inpaint, adjust) |
| Memory | `engine/memory.py` | Persist context across sessions (Obsidian vault) |
| Delegation | `engine/delegation.py` | Route tasks to the best AI model |

## The Film Genome Document

The Film Genome Document is a YAML file containing **8 DNA strands**:

1. **Metadata** — Title, format, duration, version
2. **Narrative DNA** — Story structure, beats, emotional arcs, causal chains
3. **Character DNA** — Archetypes, visual references, voice profiles, relationships
4. **Visual DNA** — Color palettes per act, shot distribution, art direction
5. **Pacing DNA** — Shot lengths, cutting dynamics, tension curves
6. **Audio DNA** — Dialogue ratios, music style, silence moments
7. **Scene Manifest** — Every scene and shot with camera, dialogue, transitions
8. **Rendering Hints** — Model preferences, budget, quality thresholds

See `schema/film_genome_v1.schema.yaml` for the formal specification.
See `examples/zootopia_reference_genome.yaml` for a reference example.

## Project Structure

```
animation-genome-machine/
├── schema/                  # Film Genome Document specification
├── compiler/                # 6-phase compilation pipeline
├── engine/                  # 7-component creative loop
├── vault/                   # Obsidian vault (working memory)
│   ├── 00-film-dna/         # Extracted genomes from reference films
│   ├── 01-screenplay/       # Generated screenplays
│   ├── 02-characters/       # Character sheets and references
│   ├── 03-storyboard/       # Storyboard frames
│   ├── 04-production/       # ComfyUI workflows and API scripts
│   ├── 05-review/           # QA and review notes
│   ├── 06-library/          # Reference genomes and style guides
│   └── 07-meta/             # System metadata
├── examples/                # Example Film Genome Documents
└── tests/                   # Test suite
```

## Getting Started (Week 1)

### 1. Understand the Schema

Read the Film Genome Document specification:

```bash
cat schema/film_genome_v1.schema.yaml
```

### 2. Study the Example

Examine the Zootopia reference genome to see how a real film maps to the schema:

```bash
cat examples/zootopia_reference_genome.yaml
```

### 3. Write Your First Genome

Create a new YAML file following the schema. Start with just Metadata + Narrative DNA + 1 Character. The compiler will tell you what's missing.

### 4. Build the Lexer (Phase 1)

The first compiler phase is the simplest — parse YAML and emit structured tokens:

```bash
python -m compiler.lexer examples/zootopia_reference_genome.yaml
```

### 5. Iterate

Each week adds a new compiler phase and engine component. The system grows incrementally — each piece is independently testable.

## Philosophy

- **Film as Code** — Every creative decision is explicit, version-controlled, and reproducible
- **Compiler Architecture** — Proven software patterns applied to creative production
- **DNA Metaphor** — Films have genetic structure; understanding it enables generation
- **AI-Native** — Built for the world where multiple AI models collaborate on production
