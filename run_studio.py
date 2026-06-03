#!/usr/bin/env python3
"""Evolutionary Studio — Production-Grade CLI Entry Point.

Commands
--------
produce     Run the full production pipeline (default)
status      Check production status from vault
list        List completed productions
package     Retrieve a production package

Environment Variables
---------------------
STUDIO_DNA          Default DNA source path
STUDIO_SETTING      Story setting
STUDIO_GROUP_A      First social group
STUDIO_GROUP_B      Second social group
STUDIO_THEME        Core theme
STUDIO_GENRE        Genre
STUDIO_BUDGET       Budget in USD
STUDIO_CONFIG       Path to config YAML

Examples
--------
# Basic production
python run_studio.py --setting "a city of robots" --theme "trust"

# Full custom production with 6 concepts across 2 rounds
python run_studio.py produce \\
    --setting "a floating city of robots and humans" \\
    --group-a robot --group-b human \\
    --theme "trust between synthetic and organic life" \\
    --n-concepts 6 --n-rounds 2 \\
    --production-id "my-film-001"

# Dry-run to validate inputs without executing
python run_studio.py --dry-run --setting "a city of robots" --theme "trust"

# Output JSON to file
python run_studio.py --output package.json --format json \\
    --setting "a city of robots" --theme "trust"

# Check status of existing production
python run_studio.py status my-film-001

# List all productions
python run_studio.py list
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import textwrap
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Path bootstrap — ensure project root and bridge are importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BRIDGE_DIR = PROJECT_ROOT / "bridge"
if str(BRIDGE_DIR) not in sys.path:
    sys.path.insert(0, str(BRIDGE_DIR))

# ---------------------------------------------------------------------------
# Imports with graceful degradation
# ---------------------------------------------------------------------------
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from system3.evolution_controller import EvolutionController, ProductionPackage

# Optional System 4 imports
try:
    from system4.long_term_memory import LongTermMemory
    LTM_AVAILABLE = True
except ImportError:
    LTM_AVAILABLE = False

try:
    from bridge.obsidian_bridge import get_bridge
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERSION = "0.2.0"
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "studio.yaml"
DEFAULT_DNA = "memory/films_analyzed/zootopia_dna.md"

# ANSI colours — auto-disabled when not a TTY
_COLOURS_ENABLED = sys.stdout.isatty()


class C:
    """ANSI colour helpers."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    @classmethod
    def disable(cls) -> None:
        for attr in dir(cls):
            if not attr.startswith("_") and isinstance(getattr(cls, attr), str):
                setattr(cls, attr, "")


if not _COLOURS_ENABLED:
    C.disable()

# ---------------------------------------------------------------------------
# Logging / output helpers
# ---------------------------------------------------------------------------
class Logger:
    """Minimal structured logger with verbosity levels."""

    LEVEL_QUIET = 0
    LEVEL_NORMAL = 1
    LEVEL_VERBOSE = 2
    LEVEL_DEBUG = 3

    def __init__(self, level: int = LEVEL_NORMAL, log_file: Optional[Path] = None):
        self.level = level
        self.log_file = log_file
        self._file_handle: Optional[Any] = None
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            self._file_handle = open(log_file, "a", encoding="utf-8")

    def _write(self, msg: str) -> None:
        if self._file_handle:
            self._file_handle.write(f"{datetime.now().isoformat()} {msg}\n")
            self._file_handle.flush()

    def debug(self, msg: str) -> None:
        if self.level >= self.LEVEL_DEBUG:
            print(f"{C.DIM}[DEBUG] {msg}{C.RESET}")
        self._write(f"[DEBUG] {msg}")

    def info(self, msg: str) -> None:
        if self.level >= self.LEVEL_NORMAL:
            print(msg)
        self._write(f"[INFO] {msg}")

    def success(self, msg: str) -> None:
        if self.level >= self.LEVEL_NORMAL:
            print(f"{C.GREEN}{msg}{C.RESET}")
        self._write(f"[SUCCESS] {msg}")

    def warning(self, msg: str) -> None:
        if self.level >= self.LEVEL_NORMAL:
            print(f"{C.YELLOW}⚠ {msg}{C.RESET}")
        self._write(f"[WARNING] {msg}")

    def error(self, msg: str) -> None:
        if self.level >= self.LEVEL_NORMAL:
            print(f"{C.RED}✖ {msg}{C.RESET}", file=sys.stderr)
        self._write(f"[ERROR] {msg}")

    def phase(self, title: str) -> None:
        if self.level >= self.LEVEL_NORMAL:
            print(f"\n{C.CYAN}{C.BOLD}▶ {title}{C.RESET}")
            print(f"{C.DIM}{'─' * (len(title) + 3)}{C.RESET}")
        self._write(f"[PHASE] {title}")

    def close(self) -> None:
        if self._file_handle:
            self._file_handle.close()


log = Logger()

# ---------------------------------------------------------------------------
# Configuration loading
# ---------------------------------------------------------------------------
def load_yaml_config(path: Path) -> dict[str, Any]:
    """Load studio YAML configuration."""
    if not path.exists():
        log.debug(f"Config file not found: {path}")
        return {}
    if yaml is None:
        log.warning("PyYAML not installed — cannot load config file")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("studio", data)  # type: ignore[return-value]


def merge_config(
    args: argparse.Namespace,
    env_prefix: str = "STUDIO_"
) -> dict[str, Any]:
    """Build final configuration from defaults < file < env < CLI."""
    config_path = Path(args.config) if args.config else DEFAULT_CONFIG
    file_cfg = load_yaml_config(config_path)

    evo = file_cfg.get("evolution", {})
    prod = file_cfg.get("production", {})

    # Mapping: arg_name -> (env_var, default, type)
    mapping: dict[str, tuple[str, Any, Any]] = {
        "dna": (f"{env_prefix}DNA", DEFAULT_DNA, str),
        "setting": (f"{env_prefix}SETTING", None, str),
        "group_a": (f"{env_prefix}GROUP_A", "robot", str),
        "group_b": (f"{env_prefix}GROUP_B", "human", str),
        "theme": (f"{env_prefix}THEME", None, str),
        "genre": (f"{env_prefix}GENRE", "animated comedy-drama", str),
        "n_concepts": (f"{env_prefix}N_CONCEPTS", evo.get("n_concepts", 4), int),
        "n_rounds": (f"{env_prefix}N_ROUNDS", evo.get("n_rounds", 1), int),
        "budget": (f"{env_prefix}BUDGET", prod.get("max_budget_usd", 50.0), float),
    }

    # Helper: check if CLI actually provided a value (not just argparse default)
    def _user_provided(key: str) -> bool:
        val = getattr(args, key, None)
        if val is None:
            return False
        # For booleans, anything non-None means user provided it
        if isinstance(val, bool):
            return True
        # For numbers/strings, if it's truthy or zero/false was explicitly set
        return True

    merged: dict[str, Any] = {}
    for key, (env_var, default, _) in mapping.items():
        # CLI wins over env over file over default
        cli_val = getattr(args, key, None)
        env_val = os.environ.get(env_var)
        if cli_val is not None:
            merged[key] = cli_val
        elif env_val is not None:
            # Attempt type conversion for env vars
            if isinstance(default, bool):
                merged[key] = env_val.lower() in ("1", "true", "yes", "on")
            elif isinstance(default, int):
                merged[key] = int(env_val)
            elif isinstance(default, float):
                merged[key] = float(env_val)
            else:
                merged[key] = env_val
        else:
            merged[key] = default

    # Additional overrides from CLI
    for attr in ("metaphor", "production_id", "output", "format", "dry_run",
                 "output_json", "force", "verbose", "quiet", "log_file"):
        val = getattr(args, attr, None)
        if val is not None:
            merged[attr] = val

    return merged


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate(cfg: dict[str, Any]) -> list[str]:
    """Return a list of validation errors. Empty list = valid."""
    errors: list[str] = []

    if not cfg.get("setting"):
        errors.append("--setting is required")
    if not cfg.get("theme"):
        errors.append("--theme is required")

    n_concepts = cfg.get("n_concepts", 0)
    if not (1 <= n_concepts <= 20):
        errors.append(f"--n-concepts must be 1-20 (got {n_concepts})")

    n_rounds = cfg.get("n_rounds", 0)
    if not (1 <= n_rounds <= 10):
        errors.append(f"--n-rounds must be 1-10 (got {n_rounds})")

    budget = cfg.get("budget", 0.0)
    if budget < 0:
        errors.append(f"--budget must be >= 0 (got {budget})")

    dna_path = PROJECT_ROOT / "studio" / cfg.get("dna", DEFAULT_DNA)
    if not dna_path.exists():
        errors.append(f"DNA source not found: {dna_path}")

    return errors


# ---------------------------------------------------------------------------
# Vault helpers for status / list / package commands
# ---------------------------------------------------------------------------
def get_bridge_instance() -> Any:
    if not BRIDGE_AVAILABLE:
        raise RuntimeError("Obsidian bridge not available")
    return get_bridge(str(PROJECT_ROOT / "studio"))


def production_exists(production_id: str) -> bool:
    """Check if a production already exists in the vault."""
    if not BRIDGE_AVAILABLE:
        return False
    try:
        bridge = get_bridge_instance()
        note = bridge.read_note(f"memory/post_mortems/post_mortem_{production_id}.md")
        return note is not None
    except Exception:
        return False


def get_production_status(production_id: str) -> Optional[dict[str, Any]]:
    """Load production status from vault."""
    if not BRIDGE_AVAILABLE:
        return None
    try:
        bridge = get_bridge_instance()
        pm = bridge.read_note(f"memory/post_mortems/post_mortem_{production_id}.md")
        if not pm:
            return None
        return {
            "production_id": production_id,
            "status": "complete",
            "generated_at": pm.frontmatter.get("generated_at", "unknown"),
            "concept_id": pm.frontmatter.get("concept_id"),
        }
    except Exception as e:
        log.debug(f"Failed to load status: {e}")
        return None


def list_productions() -> list[dict[str, Any]]:
    """List all productions found in vault post-mortems."""
    if not BRIDGE_AVAILABLE:
        return []
    try:
        bridge = get_bridge_instance()
        notes = bridge.query_notes(folder="memory/post_mortems")
        results = []
        for note in notes:
            if note.path.startswith("memory/post_mortems/post_mortem_"):
                pid = note.path.replace("memory/post_mortems/post_mortem_", "").replace(".md", "")
                results.append({
                    "production_id": pid,
                    "generated_at": note.frontmatter.get("generated_at", "unknown"),
                    "concept_id": note.frontmatter.get("concept_id"),
                })
        return sorted(results, key=lambda x: x["generated_at"], reverse=True)
    except Exception as e:
        log.debug(f"Failed to list productions: {e}")
        return []


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------
def fmt_pretty_package(pkg: ProductionPackage) -> str:
    """Format a ProductionPackage as a human-readable string."""
    d = pkg.to_dict()
    lines = [
        "",
        f"{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════════════════════╗{C.RESET}",
        f"{C.BOLD}{C.CYAN}║{C.RESET}  {C.BOLD}PRODUCTION COMPLETE{C.RESET}{' ' * 47}{C.BOLD}{C.CYAN}║{C.RESET}",
        f"{C.BOLD}{C.CYAN}╠══════════════════════════════════════════════════════════════════════╣{C.RESET}",
        f"{C.BOLD}{C.CYAN}║{C.RESET}  Concept:    {d['concept']['title']:<52}{C.BOLD}{C.CYAN}║{C.RESET}",
        f"{C.BOLD}{C.CYAN}║{C.RESET}  Logline:    {d['concept']['logline'][:50]:<52}{C.BOLD}{C.CYAN}║{C.RESET}",
        f"{C.BOLD}{C.CYAN}║{C.RESET}  Scenes:     {len(d.get('scenes', [])):<52}{C.BOLD}{C.CYAN}║{C.RESET}",
        f"{C.BOLD}{C.CYAN}║{C.RESET}  Characters: {len(d.get('characters', [])):<52}{C.BOLD}{C.CYAN}║{C.RESET}",
        f"{C.BOLD}{C.CYAN}║{C.RESET}  Environments: {len(d.get('environments', [])):<50}{C.BOLD}{C.CYAN}║{C.RESET}",
        f"{C.BOLD}{C.CYAN}╚══════════════════════════════════════════════════════════════════════╝{C.RESET}",
        "",
    ]

    # Director verdict
    dd = d.get("director_decision")
    if dd:
        verdict = dd.get("verdict", "unknown").upper()
        conf = dd.get("confidence", 0.0)
        vcol = C.GREEN if verdict == "ACCEPT" else C.YELLOW if verdict == "ITERATE" else C.RED
        lines.append(f"  Director Verdict: {vcol}{verdict}{C.RESET} ({conf:.0%} confidence)")
        lines.append(f"  Reason: {dd.get('reason', 'N/A')[:100]}...")
        lines.append("")

    return "\n".join(lines)


def fmt_markdown_package(pkg: ProductionPackage) -> str:
    """Format a ProductionPackage as Markdown."""
    d = pkg.to_dict()
    lines = [
        f"# Production Package: {d['concept']['title']}",
        "",
        f"- **Production ID**: {d.get('production_id', 'N/A')}",
        f"- **Generated At**: {d.get('generated_at', 'N/A')}",
        "",
        "## Concept",
        f"- **Title**: {d['concept']['title']}",
        f"- **Logline**: {d['concept']['logline']}",
        f"- **Theme**: {d['concept'].get('theme', 'N/A')}",
        "",
        "## Screenplay",
        f"- **Format**: {d.get('screenplay', {}).get('format', 'unknown')}",
        f"- **Scenes**: {len(d.get('scenes', []))}",
        "",
        "## Characters",
    ]
    for char in d.get("characters", []):
        lines.append(f"- **{char.get('name', 'Unnamed')}** ({char.get('archetype', '?')}) — {char.get('role', '')}")
    lines.extend(["", "## Environments"])
    for env in d.get("environments", []):
        lines.append(f"- **{env.get('name', 'Unnamed')}** ({env.get('type', '')})")
    lines.extend(["", "## Shot Lists"])
    for sl in d.get("shot_lists", []):
        lines.append(f"- {sl.get('scene_id', '?')}: {sl.get('shot_count', 0)} shots")
    lines.extend(["", "## Cost Report"])
    cr = d.get("cost_report", {})
    lines.append(f"- **Budget**: ${cr.get('budget_allocated', 0):.2f}")
    lines.append(f"- **Remaining**: ${cr.get('remaining', 0):.2f}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Signal handling
# ---------------------------------------------------------------------------
_interrupted = False


def _signal_handler(signum: int, _frame: Any) -> None:
    global _interrupted
    _interrupted = True
    print(f"\n{C.YELLOW}⚠ Interrupted by signal {signum}. Shutting down gracefully…{C.RESET}")


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

# ---------------------------------------------------------------------------
# Core commands
# ---------------------------------------------------------------------------
def cmd_produce(cfg: dict[str, Any]) -> int:
    """Run the full production pipeline."""
    # Validate
    errors = validate(cfg)
    if errors:
        log.error("Validation failed:")
        for err in errors:
            log.error(f"  • {err}")
        return 3

    # Dry-run preview
    if cfg.get("dry_run"):
        log.phase("Dry Run Preview")
        log.info(f"  DNA source:      {cfg['dna']}")
        log.info(f"  Setting:         {cfg['setting']}")
        log.info(f"  Groups:          {cfg['group_a']} / {cfg['group_b']}")
        log.info(f"  Theme:           {cfg['theme']}")
        log.info(f"  Metaphor:        {cfg.get('metaphor') or '(auto-generated)'}")
        log.info(f"  Genre:           {cfg['genre']}")
        log.info(f"  Concepts:        {cfg['n_concepts']} per round")
        log.info(f"  Rounds:          {cfg['n_rounds']}")
        log.info(f"  Budget:          ${cfg['budget']:.2f}")
        log.info(f"  Production ID:   {cfg.get('production_id') or '(auto-generated)'}")
        log.info("")
        log.success("Dry run complete — all inputs valid.")
        return 0

    # Resume / duplicate protection
    prod_id = cfg.get("production_id")
    if prod_id and production_exists(prod_id) and not cfg.get("force"):
        log.error(f"Production '{prod_id}' already exists in vault.")
        log.info(f"Use --force to overwrite, or choose a different --production-id.")
        return 1

    # Build constraints
    metaphor = cfg.get("metaphor") or f"{cfg['group_a']}/{cfg['group_b']} dynamics mirror real-world prejudice"
    constraints = {
        "setting": cfg["setting"],
        "group_a": cfg["group_a"],
        "group_b": cfg["group_b"],
        "theme": cfg["theme"],
        "social_metaphor": metaphor,
        "genre": cfg["genre"]
    }

    # Banner
    log.info("")
    log.info(f"{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════════════════════╗{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}║{C.RESET}     {C.BOLD}EVOLUTIONARY STUDIO (System 3 + 4) v{VERSION}{C.RESET}{' ' * (25 - len(VERSION))}{C.BOLD}{C.CYAN}║{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}╠══════════════════════════════════════════════════════════════════════╣{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}║{C.RESET}  DNA:        {cfg['dna']:<50}{C.BOLD}{C.CYAN}║{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}║{C.RESET}  Setting:    {cfg['setting']:<50}{C.BOLD}{C.CYAN}║{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}║{C.RESET}  Groups:     {cfg['group_a']} / {cfg['group_b']:<45}{C.BOLD}{C.CYAN}║{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}║{C.RESET}  Theme:      {cfg['theme']:<50}{C.BOLD}{C.CYAN}║{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}║{C.RESET}  Concepts:   {cfg['n_concepts']} per round × {cfg['n_rounds']} rounds{'':<30}{C.BOLD}{C.CYAN}║{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}║{C.RESET}  Budget:     ${cfg['budget']:.2f}{'':<49}{C.BOLD}{C.CYAN}║{C.RESET}")
    log.info(f"{C.BOLD}{C.CYAN}╚══════════════════════════════════════════════════════════════════════╝{C.RESET}")
    log.info("")

    # Execute
    controller = EvolutionController(
        n_concepts=cfg["n_concepts"],
        n_rounds=cfg["n_rounds"],
        budget_usd=cfg["budget"]
    )

    overall_start = time.time()
    try:
        package = controller.produce(
            dna_source=cfg["dna"],
            constraints=constraints,
            production_id=prod_id
        )
    except Exception as e:
        log.error(f"Production failed: {e}")
        if cfg.get("verbose", 0) >= Logger.LEVEL_VERBOSE:
            traceback.print_exc()
        return 1

    if _interrupted:
        log.warning("Production was interrupted.")
        return 2

    overall_elapsed = time.time() - overall_start

    # Output formatting
    out_format = cfg.get("format", "pretty")
    if cfg.get("output_json"):
        out_format = "json"

    if out_format == "json":
        output_text = json.dumps(package.to_dict(), indent=2, default=str)
    elif out_format == "markdown":
        output_text = fmt_markdown_package(package)
    else:
        output_text = fmt_pretty_package(package)

    log.info(output_text)

    # Save to file if requested
    out_path = cfg.get("output")
    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        log.success(f"Output saved to {out_path}")

    log.info(f"\n{C.DIM}Total elapsed time: {overall_elapsed:.1f}s{C.RESET}")
    return 0


def cmd_status(production_id: str) -> int:
    """Show status of a production."""
    if not BRIDGE_AVAILABLE:
        log.error("Obsidian bridge not available.")
        return 1

    status = get_production_status(production_id)
    if not status:
        log.error(f"Production '{production_id}' not found in vault.")
        return 1

    log.info(f"\n{C.BOLD}Production: {production_id}{C.RESET}")
    log.info(f"  Status: {C.GREEN}complete{C.RESET}")
    log.info(f"  Generated: {status['generated_at']}")
    if status.get("concept_id"):
        log.info(f"  Concept ID: {status['concept_id']}")
    return 0


def cmd_list() -> int:
    """List all productions."""
    if not BRIDGE_AVAILABLE:
        log.error("Obsidian bridge not available.")
        return 1

    productions = list_productions()
    if not productions:
        log.info("No productions found in vault.")
        return 0

    log.info(f"\n{C.BOLD}{'Production ID':<30} {'Generated':<25} {'Concept ID'}{C.RESET}")
    log.info(f"{C.DIM}{'─' * 80}{C.RESET}")
    for p in productions:
        pid = p["production_id"]
        gen = p["generated_at"]
        cid = p.get("concept_id") or "N/A"
        log.info(f"{pid:<30} {gen:<25} {cid}")
    log.info(f"\nTotal: {len(productions)} production(s)")
    return 0


def cmd_package(production_id: str, out_format: str = "pretty", out_path: Optional[Path] = None) -> int:
    """Retrieve and display a production package."""
    if not BRIDGE_AVAILABLE:
        log.error("Obsidian bridge not available.")
        return 1

    try:
        bridge = get_bridge_instance()
        pkg_note = bridge.read_note(f"memory/post_mortems/package_{production_id}.md")
        if not pkg_note:
            log.error(f"Package for '{production_id}' not found.")
            return 1

        # Minimal package reconstruction
        concept_note = None
        concept_id = pkg_note.frontmatter.get("concept_id")
        if concept_id:
            concept_note = bridge.read_note(f"concepts/{concept_id}.md")

        # Build a lightweight display dict
        display = {
            "production_id": production_id,
            "generated_at": pkg_note.frontmatter.get("generated_at", "unknown"),
            "concept": {
                "title": concept_note.title if concept_note else "Unknown",
                "logline": concept_note.frontmatter.get("logline", "") if concept_note else "",
            },
            "package_preview": pkg_note.content[:800] + "..." if len(pkg_note.content) > 800 else pkg_note.content,
        }

        if out_format == "json":
            output_text = json.dumps(display, indent=2, default=str)
        else:
            lines = [
                f"\n{C.BOLD}Package: {production_id}{C.RESET}",
                f"  Generated: {display['generated_at']}",
                f"  Concept:   {display['concept']['title']}",
                f"  Logline:   {display['concept']['logline']}",
                "",
                display["package_preview"],
            ]
            output_text = "\n".join(lines)

        log.info(output_text)

        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(output_text)
            log.success(f"Saved to {out_path}")

        return 0
    except Exception as e:
        log.error(f"Failed to load package: {e}")
        return 1


# ---------------------------------------------------------------------------
# New commands: briefs, assemble, ingest, evolve
# ---------------------------------------------------------------------------
def cmd_briefs(production_id: str, concept_id: str = "WINNER", dna_source: Optional[str] = None) -> int:
    """Generate scene briefs for AI writers."""
    log.phase("Generating Scene Briefs")
    
    try:
        from system3.scene_brief_compiler import SceneBriefCompiler
        from bridge.obsidian_bridge import get_bridge
        
        bridge = get_bridge(str(PROJECT_ROOT / "studio"))
        compiler = SceneBriefCompiler(obsidian_bridge=bridge)
        
        briefs = compiler.compile_briefs(concept_id=concept_id)
        paths = compiler.save_briefs(briefs, production_id=production_id)
        
        log.success(f"Generated {len(briefs)} scene briefs for production: {production_id}")
        log.info("")
        log.info(f"{C.BOLD}Writer's Packet:{C.RESET} {paths[-1]}")
        log.info("")
        log.info("Next steps:")
        log.info("  1. Read the Writer's Packet")
        log.info("  2. Write each scene following the briefs")
        log.info("  3. Save scenes to studio/scenes/")
        log.info(f"  4. Run: python run_studio.py assemble {production_id}")
        
        return 0
    except Exception as e:
        log.error(f"Brief generation failed: {e}")
        if log.level >= Logger.LEVEL_VERBOSE:
            traceback.print_exc()
        return 1


def cmd_assemble(production_id: str, out_path: Optional[Path] = None) -> int:
    """Assemble AI-written scenes into final screenplay."""
    log.phase("Assembling Screenplay")
    
    try:
        from system3.scene_brief_compiler import ScreenplayAssembler
        from bridge.obsidian_bridge import get_bridge
        
        bridge = get_bridge(str(PROJECT_ROOT / "studio"))
        assembler = ScreenplayAssembler(obsidian_bridge=bridge)
        
        result = assembler.assemble(production_id)
        
        if "error" in result:
            log.error(result["error"])
            return 1
        
        log.success(f"Assembled {result['scenes_assembled']} scenes")
        log.info(f"  Issues found: {result['issues_found']}")
        log.info(f"  Word count: {result['word_count']}")
        log.info(f"  Screenplay: {result['screenplay_path']}")
        
        if result.get("issues"):
            log.warning("Issues to fix:")
            for issue in result["issues"]:
                log.warning(f"  • {issue}")
        
        return 0
    except Exception as e:
        log.error(f"Assembly failed: {e}")
        if log.level >= Logger.LEVEL_VERBOSE:
            traceback.print_exc()
        return 1


def cmd_ingest(screenplay_path: str, title: Optional[str] = None) -> int:
    """Ingest a screenplay to learn from it."""
    log.phase("Ingesting Screenplay")
    
    try:
        from system4.script_ingestor import ScriptIngestor
        from bridge.obsidian_bridge import get_bridge
        
        bridge = get_bridge(str(PROJECT_ROOT / "studio"))
        ingestor = ScriptIngestor(obsidian_bridge=bridge)
        
        result = ingestor.ingest(screenplay_path, title=title)
        
        log.success(f"Ingested: {result.source_title}")
        log.info(f"  Scenes extracted: {result.scenes_extracted}")
        log.info(f"  Characters profiled: {result.characters_profiled}")
        log.info(f"  Callbacks identified: {result.callbacks_identified}")
        log.info(f"  Theme keywords: {', '.join(result.theme_keywords[:5])}")
        log.info(f"  DNA saved: {result.dna_path}")
        log.info(f"  LTM indexed: {'Yes' if result.ltm_indexed else 'No'}")
        
        if result.skill_updates:
            log.info("  Skill updates:")
            for update in result.skill_updates:
                log.info(f"    • {update}")
        
        log.info("")
        log.info("The system has learned from this screenplay.")
        log.info("Future productions will use these patterns.")
        
        return 0
    except Exception as e:
        log.error(f"Ingestion failed: {e}")
        if log.level >= Logger.LEVEL_VERBOSE:
            traceback.print_exc()
        return 1


def cmd_evolve() -> int:
    """Run self-improvement analysis."""
    log.phase("Self-Improvement Analysis")
    
    try:
        from system4.self_improvement import SelfImprovementEngine
        from bridge.obsidian_bridge import get_bridge
        
        bridge = get_bridge(str(PROJECT_ROOT / "studio"))
        engine = SelfImprovementEngine(obsidian_bridge=bridge)
        
        report = engine.generate_evolution_report()
        report_text = engine.format_report(report)
        
        log.info(report_text)
        
        # Save report
        report_path = PROJECT_ROOT / "studio" / "memory" / "evolution_reports" / f"report_{datetime.now().strftime('%Y%m%d')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")
        log.success(f"Report saved: {report_path}")
        
        return 0
    except Exception as e:
        log.error(f"Evolution analysis failed: {e}")
        if log.level >= Logger.LEVEL_VERBOSE:
            traceback.print_exc()
        return 1


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_studio.py",
        description="Evolutionary Studio — AI Animation Production System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              # Quick production with defaults
              python run_studio.py --setting "a city of robots" --theme "trust"

              # Full control
              python run_studio.py produce --n-concepts 6 --n-rounds 2 \\
                --setting "floating city" --theme "prejudice" \\
                --production-id "film-001"

              # Dry-run to validate inputs
              python run_studio.py --dry-run --setting "city" --theme "trust"

              # Generate scene briefs for AI writers
              python run_studio.py briefs --production-id "film-001"

              # Assemble AI-written scenes
              python run_studio.py assemble film-001

              # Ingest a new screenplay to learn from
              python run_studio.py ingest screenplay.fountain --title "Zootopia 2"

              # Run self-improvement analysis
              python run_studio.py evolve

              # Check existing production
              python run_studio.py status film-001

              # List all productions
              python run_studio.py list

            environment variables:
              STUDIO_DNA, STUDIO_SETTING, STUDIO_THEME, STUDIO_GROUP_A,
              STUDIO_GROUP_B, STUDIO_GENRE, STUDIO_BUDGET, STUDIO_CONFIG
        """),
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("-c", "--config", metavar="PATH",
                        help=f"Path to studio config YAML (default: {DEFAULT_CONFIG})")
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="Increase verbosity (-v = verbose, -vv = debug)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress non-error output")
    parser.add_argument("--log-file", metavar="PATH",
                        help="Write structured log to file")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable coloured output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── produce ─────────────────────────────────────────────────────────────
    produce_parser = subparsers.add_parser(
        "produce",
        help="Run the full production pipeline",
        description="Generate concepts, evolve, produce, review, and save.",
    )
    produce_parser.add_argument("--dna", default=None,
                                help=f"Path to Creative DNA in vault (default: {DEFAULT_DNA})")
    produce_parser.add_argument("--setting", help="Story setting")
    produce_parser.add_argument("--group-a", default=None,
                                help="First social group (default: robot)")
    produce_parser.add_argument("--group-b", default=None,
                                help="Second social group (default: human)")
    produce_parser.add_argument("--theme", help="Core theme")
    produce_parser.add_argument("--metaphor", default=None,
                                help="Social metaphor (auto-generated if omitted)")
    produce_parser.add_argument("--genre", default=None,
                                help="Genre (default: animated comedy-drama)")
    produce_parser.add_argument("--n-concepts", type=int, default=None,
                                help="Concepts per round (default: 4)")
    produce_parser.add_argument("--n-rounds", type=int, default=None,
                                help="Evolution rounds (default: 1)")
    produce_parser.add_argument("--budget", type=float, default=None,
                                help="Budget in USD (default: 50.0)")
    produce_parser.add_argument("--production-id",
                                help="Production identifier (auto-generated if omitted)")
    produce_parser.add_argument("--dry-run", action="store_true",
                                help="Validate inputs and preview without executing")
    produce_parser.add_argument("--force", action="store_true",
                                help="Overwrite existing production with same ID")
    produce_parser.add_argument("-o", "--output", metavar="PATH",
                                help="Save result to file")
    produce_parser.add_argument("-f", "--format", choices=["pretty", "json", "markdown"],
                                default="pretty", help="Output format")
    produce_parser.add_argument("--output-json", action="store_true",
                                help=argparse.SUPPRESS)  # Legacy compat

    # ── status ──────────────────────────────────────────────────────────────
    status_parser = subparsers.add_parser("status", help="Check production status")
    status_parser.add_argument("production_id", help="Production identifier")

    # ── list ────────────────────────────────────────────────────────────────
    subparsers.add_parser("list", help="List completed productions")

    # ── package ─────────────────────────────────────────────────────────────
    package_parser = subparsers.add_parser("package", help="Retrieve a production package")
    package_parser.add_argument("production_id", help="Production identifier")
    package_parser.add_argument("-o", "--output", metavar="PATH",
                                help="Save to file")
    package_parser.add_argument("-f", "--format", choices=["pretty", "json"],
                                default="pretty", help="Output format")

    # ── briefs ──────────────────────────────────────────────────────────────
    briefs_parser = subparsers.add_parser(
        "briefs",
        help="Generate scene briefs for AI writers",
        description="Compile rich creative briefs for each scene. The AI (Claude Code, Codex, Kimi) reads these briefs and writes the actual scenes.",
    )
    briefs_parser.add_argument("--dna", default=None,
                               help=f"Path to Creative DNA (default: {DEFAULT_DNA})")
    briefs_parser.add_argument("--production-id", required=True,
                               help="Production identifier")
    briefs_parser.add_argument("--concept-id", default="WINNER",
                               help="Concept ID to use (default: WINNER)")

    # ── assemble ────────────────────────────────────────────────────────────
    assemble_parser = subparsers.add_parser(
        "assemble",
        help="Assemble AI-written scenes into final screenplay",
        description="Validate and compile scenes written by the AI into a complete Fountain screenplay.",
    )
    assemble_parser.add_argument("production_id", help="Production identifier")
    assemble_parser.add_argument("-o", "--output", metavar="PATH",
                                 help="Save screenplay to file")

    # ── ingest ──────────────────────────────────────────────────────────────
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest a new screenplay to learn from",
        description="Parse a professional screenplay, extract patterns, and update Creative DNA and skill files.",
    )
    ingest_parser.add_argument("screenplay", help="Path to screenplay file (.fountain or .txt)")
    ingest_parser.add_argument("--title", help="Film title (default: filename)")

    # ── evolve ──────────────────────────────────────────────────────────────
    evolve_parser = subparsers.add_parser(
        "evolve",
        help="Run self-improvement analysis",
        description="Analyze production history, identify weaknesses, and propose improvements.",
    )

    return parser


# ---------------------------------------------------------------------------
# Backward-compatible subcommand inference
# ---------------------------------------------------------------------------
def _infer_subcommand(argv: list[str]) -> Optional[list[str]]:
    """Prepend 'produce' if no subcommand is present in argv.

    This preserves the legacy usage where users could run:
        python run_studio.py --setting "x" --theme "y"
    instead of requiring:
        python run_studio.py produce --setting "x" --theme "y"

    Global flags are kept before the subcommand so argparse remains happy.
    """
    subcommands = {"produce", "status", "list", "package", "briefs", "assemble", "ingest", "evolve"}
    global_flags = {"-h", "--help", "--version", "-v", "--verbose", "-q", "--quiet", "--no-color"}
    global_flags_with_values = {"-c", "--config", "--log-file"}

    # Check if a subcommand is already present
    skip_next = False
    for arg in argv:
        if skip_next:
            skip_next = False
            continue
        if arg in global_flags_with_values:
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        if arg in subcommands:
            return None  # No modification needed
        break

    # No subcommand found — prepend 'produce' while keeping global flags first
    global_parts: list[str] = []
    rest: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in global_flags:
            global_parts.append(arg)
            i += 1
        elif arg in global_flags_with_values:
            global_parts.append(arg)
            i += 1
            if i < len(argv):
                global_parts.append(argv[i])
                i += 1
        else:
            rest.append(arg)
            i += 1

    return global_parts + ["produce"] + rest


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def main(argv: Optional[list[str]] = None) -> int:
    raw_argv = argv if argv is not None else sys.argv[1:]
    inferred = _infer_subcommand(raw_argv)
    effective_argv = inferred if inferred is not None else raw_argv

    parser = build_parser()
    args = parser.parse_args(effective_argv)

    # Global options
    if args.no_color:
        C.disable()

    log_level = Logger.LEVEL_NORMAL
    if args.quiet:
        log_level = Logger.LEVEL_QUIET
    elif args.verbose >= 2:
        log_level = Logger.LEVEL_DEBUG
    elif args.verbose == 1:
        log_level = Logger.LEVEL_VERBOSE

    global log
    log = Logger(level=log_level, log_file=Path(args.log_file) if args.log_file else None)

    # Default command = produce
    command = args.command or "produce"

    # Merge configuration
    cfg = merge_config(args)
    cfg["verbose"] = args.verbose
    cfg["quiet"] = args.quiet

    log.debug(f"Effective config: {json.dumps({k: v for k, v in cfg.items() if v is not None}, indent=2)}")

    try:
        if command == "produce":
            return cmd_produce(cfg)
        elif command == "status":
            return cmd_status(args.production_id)
        elif command == "list":
            return cmd_list()
        elif command == "package":
            return cmd_package(args.production_id, args.format, Path(args.output) if args.output else None)
        elif command == "briefs":
            return cmd_briefs(args.production_id, args.concept_id, args.dna)
        elif command == "assemble":
            return cmd_assemble(args.production_id, Path(args.output) if args.output else None)
        elif command == "ingest":
            return cmd_ingest(args.screenplay, args.title)
        elif command == "evolve":
            return cmd_evolve()
        else:
            parser.print_help()
            return 0
    finally:
        log.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Interrupted.{C.RESET}", file=sys.stderr)
        sys.exit(130)
