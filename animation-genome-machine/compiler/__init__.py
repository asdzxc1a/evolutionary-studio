# Animation Genome Machine — Compiler Package
"""
The Film Compiler: A 6-phase pipeline that transforms Film Genome Documents
(YAML) into production-ready animated films.

Phases:
    1. Lexer     — Parse YAML into structured tokens
    2. Parser    — Build an Abstract Syntax Tree (AST)
    3. Analyzer  — Validate the AST for coherence and completeness
    4. Optimizer  — Generate an optimal render plan
    5. CodeGen   — Emit ComfyUI workflows and API calls
    6. Linker    — Assemble the final film
"""

__version__ = "0.1.0"
