# Kazka & Animation Genome Machine v3 Delivery Package

Welcome to the **Kazka & Animation Genome Machine v3** delivery workspace. This consolidated archive captures all intellectual property, architectural design, evolutionary code, and creative genomes compiled during our collaborative session.

---

## 1. Directory Structure

This archive is structured as a self-contained, ready-to-run package:

```
kazka_v3_delivery/
├── README.md                           # This document
├── runner.py                           # Main CLI entrypoint
├── engine/                             # Core Python engine modules
│   ├── strands.py                      # 11-strand schema definitions
│   ├── competitive.py                  # Agent swarm tournament logic
│   ├── scene_judge.py                  # Deep story & pacing evaluation
│   ├── antipatterns.py                 # Structure & cliché screening
│   ├── refinement.py                   # Automated feedback & corrections
│   └── outputs.py                      # Export & packaging generators
├── genomes/                            # Stored film DNA genomes
│   ├── zootopia_reference_genome.yaml  # Structural baseline film (Disney)
│   ├── kazka_genome.yaml               # Kazka v1 (Initial draft - generic)
│   ├── kazka_v2_genome.yaml            # Kazka v2 (Improved, 8-strand, 6 issues)
│   ├── kazka_v2_deep_review.md         # Deep critique of v2 issues
│   ├── kazka_v3_genome.yaml            # Kazka v3 (Production-ready, 11-strand)
│   ├── kazka_genome_score.json         # Evaluation scores for v1
│   ├── kazka_v2_genome_score.json      # Evaluation scores for v2
│   ├── kazka_v2_deep_score.json        # Detailed review metric matrix
│   └── kazka_v2_genome_beats.txt       # Extracted narrative beat sheets
└── research/                           # Domain intelligence & strategies
    ├── ai_animation_factory_research.md # Multi-agent AI film studio systems
    ├── chinese_ai_tools_research.md    # Chinese open-source Sora & ComfyUI research
    └── four_opinions.md                # Strategic opinions on AI drama
```

---

## 2. The 11-Strand Narrative Genome

The **Animation Genome Machine v3** shifts storytelling from linear scripts to structural DNA strands. The `kazka_v3_genome.yaml` uses this highly advanced framework:

| Strand # | Strand Name | Focus / Metrics Tracked |
|---|---|---|
| **Strand 1** | **Core Concept** | Theme, Target Audience, Metaphor, Genre, Logline |
| **Strand 2** | **Narrative Beats** | 15-beat structural roadmap (Save the Cat alignment) |
| **Strand 3** | **Character Arcs** | Core wounds, lies, transformations, relationships |
| **Strand 4** | **Pacing Curves** | Action/dialogue ratios, compression beats, high-velocity indices |
| **Strand 5** | **Emotional Arc** | Emotional valence curve (-1.0 to +1.0) and recovery beats |
| **Strand 6** | **World Rules** | Physical, magical, and displacement laws of the universe |
| **Strand 7** | **Visual Grammar** | Color scripts, lighting palettes, motifs, camera guidelines |
| **Strand 8** | **Dialogue DNA** | Signature phrases, character voice profiles, dialogue rules |
| **Strand 9** | **Audience Psych** | Cognitive engagement targets, tension hooks, release beats |
| **Strand 10** | **Production Constraints** | Location counts, crowd indices, rendering complexity |
| **Strand 11** | **Refinement Directives** | Specific review overrides, consistency tags, quality thresholds |

---

## 3. Kazka v3: Key Creative Resolutions

The v3 genome resolves the six structural and creative critiques identified during the deep review of the v2 genome, elevating the story from formulaic to a raw, unique, and deeply symbolic narrative:

1. **Elif's Reality (Real Scene)**: Replaced vague descriptions of displacement with a concrete, painful scene where Elif is pushed to the margins at a train station, capturing the visceral reality of being a refugee.
2. **Mother-Daughter Confrontation**: Designed a raw confrontation where words are weapons, challenging the idealized view of mother-daughter ties.
3. **European End-Destination**: Rooted the climax in Berlin-Neukölln, capturing the real diaspora experience rather than escaping to an idealized America.
4. **Subverting the Manifestation Pattern**: Broke standard fantasy tropes by demanding a heavy cost for fairy tale assistance: **the sacrifice of the memory of self**.
5. **Dangerous Lys Arrival**: The fairy helper Lys is no longer a cute mascot; its arrival is volatile, dangerous, and triggered exclusively by intense, suppressed negative emotions.
6. **Displacement Legal & Social Context**: Embedded the Temporary Protection Directive, bureaucracy, housing queues, and the complex legal status of Ukrainian refugees into the actual fabric of the world rules.

---

## 4. How to Use the Engine (CLI Guide)

You can run the engine directly from this directory. 

### 4.1 CLI Runner Commands
The main CLI is located in `runner.py`. Here are the most useful commands:

* **Compare Genomes**:
  ```bash
  python runner.py compare genomes/kazka_v3_genome.yaml genomes/zootopia_reference_genome.yaml
  ```

* **Evaluate & Judge a Genome**:
  ```bash
  python runner.py judge genomes/kazka_v3_genome.yaml
  ```

* **Inspect Genome Strands**:
  ```bash
  python runner.py inspect genomes/kazka_v3_genome.yaml --strand pacing
  ```

* **Generate Story Assets (Screenplay, Storyboards, etc.)**:
  ```bash
  python runner.py generate-assets genomes/kazka_v3_genome.yaml --type screenplay --output genomes/kazka_v3_screenplay.txt
  ```

* **Search/Query the Genome**:
  ```bash
  python runner.py query genomes/kazka_v3_genome.yaml "core wound"
  ```

---

## 5. Session Research Overview

* **`ai_animation_factory_research.md`**: Outlines how a multi-agent system (Writer, Visual Planner, World Builder, Sound, Editorial) works in parallel to produce high-end content at scale.
* **`chinese_ai_tools_research.md`**: Provides a deep dive into advanced Chinese video foundation models (Wan 2.2, AniSora, Kling, Vidu) and local ComfyUI workflow structures.
* **`four_opinions.md`**: Explores the philosophical and creative implications of automated drama generation, outlining a roadmap from simple compilation to a true evolutionary storytelling loop.
