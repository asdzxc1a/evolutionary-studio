"""
Phase 1 — Lexer: YAML → Tokens

Reads a Film Genome Document (YAML file) and produces a stream of typed tokens
representing each strand, field, and value. The lexer validates YAML syntax and
reports parse errors with line numbers.

Usage:
    python -m compiler.lexer <genome.yaml>
"""

# TODO: Implement in Week 1
# - Load YAML with ruamel.yaml (preserves comments and line numbers)
# - Emit Token objects with type, value, line_number, strand
# - Report syntax errors with context
