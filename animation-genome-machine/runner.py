#!/usr/bin/env python3
"""
AGM Runner — CLI interface for the Animation Genome Machine.

This script is the bridge between the Python scoring engine and the
Antigravity agent. The agent generates content; this script scores it.

USAGE (from agent):
    # Score a genome file
    python3 runner.py judge vault/00-film-dna/kazka_genome.yaml

    # Score and get corrections if failed
    python3 runner.py diagnose vault/00-film-dna/kazka_genome.yaml

    # Validate mutation rules
    python3 runner.py validate-rules rules.yaml

    # Show system status
    python3 runner.py status

    # Initialize a new generation session
    python3 runner.py init-session --reference vault/00-film-dna/zootopia.yaml --direction "..."
"""

import sys
import os
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.judgment import ScoreCard, JUDGMENT_PROMPT
from engine.generation import MutationRules, LocationSpec
from engine.correction import diagnose, format_correction_prompt
from engine.scene_judge import score_beats
from engine.outputs import generate_scene_script, generate_pitch_deck, generate_emotion_map, generate_visual_prompts
from engine.competitive import GENERATORS, CompetitionEntry, select_winner, build_competition_prompt
from engine.refinement import ProgressiveRefinementLoop, identify_weakest_beats
from engine.antipatterns import ANTI_PATTERNS, find_patterns_in_text, summary as ap_summary


# ═══════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════

SESSION_DIR = "vault/07-meta/sessions"


def init_session(reference_path: str, creative_direction: str,
                 mutation_rules_path: str = None) -> str:
    """Initialize a new generation session. Returns session ID."""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = Path(SESSION_DIR) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # Copy reference genome
    if os.path.exists(reference_path):
        with open(reference_path) as f:
            ref_content = f.read()
        with open(session_dir / "reference_genome.yaml", 'w') as f:
            f.write(ref_content)

    # Save creative direction
    with open(session_dir / "creative_direction.txt", 'w') as f:
        f.write(creative_direction)

    # Save session state
    state = {
        "session_id": session_id,
        "created": datetime.now().isoformat(),
        "reference_path": reference_path,
        "creative_direction": creative_direction,
        "iteration": 0,
        "best_score": 0.0,
        "status": "initialized",
        "history": [],
    }

    with open(session_dir / "state.json", 'w') as f:
        json.dump(state, f, indent=2)

    print(f"✅ Session initialized: {session_id}")
    print(f"   Directory: {session_dir}")
    print(f"   Reference: {reference_path}")
    print(f"   Direction: {creative_direction[:80]}...")
    return session_id


def get_latest_session() -> str:
    """Get the most recent session ID."""
    sessions_path = Path(SESSION_DIR)
    if not sessions_path.exists():
        return None
    sessions = sorted(sessions_path.iterdir(), reverse=True)
    return sessions[0].name if sessions else None


def load_session_state(session_id: str) -> dict:
    """Load session state."""
    state_path = Path(SESSION_DIR) / session_id / "state.json"
    if state_path.exists():
        with open(state_path) as f:
            return json.load(f)
    return None


def save_session_state(session_id: str, state: dict):
    """Save session state."""
    state_path = Path(SESSION_DIR) / session_id / "state.json"
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


# ═══════════════════════════════════════════════════════
# JUDGMENT (Heuristic — fast, deterministic)
# ═══════════════════════════════════════════════════════

def heuristic_judge(genome_yaml: str) -> ScoreCard:
    """
    Fast heuristic judgment based on content analysis.
    This is the FIRST pass — catches obvious issues before
    the agent does deep creative review.
    """
    # Strip YAML comment lines AND inline comments to avoid false positives
    # from transmutation notes like "# villain → FIXED" or "# Zootopia: 'Anyone can be anything'"
    import re
    content_lines = []
    for line in genome_yaml.split('\n'):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue  # Full comment line
        # Remove inline comments (after # not inside quotes)
        line_no_comment = re.sub(r'\s+#\s.*$', '', line)
        content_lines.append(line_no_comment)
    text = '\n'.join(content_lines).lower()
    score = ScoreCard()

    # ─── KILL CRITERIA (keyword-based, with negation awareness) ───
    # We check that keywords appear in POSITIVE context, not negation
    # e.g., "No corporation" should NOT trigger kill_corporate_villain

    villain_keywords = [
        "corporation", "shadowy", "the archivist", "dark lord",
        "evil organization", "secret society", "dark force",
        "shadowy figure", "generic villain",
    ]
    negation_words = ["no ", "not ", "never ", "without ", "eliminated",
                      "removed", "fixed", "no villain", "instead of"]

    def keyword_in_positive_context(text: str, keywords: list) -> bool:
        """Check if keywords appear in non-negated context."""
        for kw in keywords:
            pos = text.find(kw)
            while pos != -1:
                # Check the 40 chars before the keyword for negation
                context_before = text[max(0, pos - 40):pos]
                if not any(neg in context_before for neg in negation_words):
                    return True
                pos = text.find(kw, pos + 1)
        return False

    score.kill_corporate_villain = keyword_in_positive_context(text, villain_keywords)

    bumper_sticker_themes = [
        "stories matter!", "be yourself", "believe in yourself",
        "follow your dream", "anyone can be anything",
        "love conquers all", "the power of friendship",
        "stories are who we are", "never give up",
    ]
    # NOTE: "stories mattered" (past tense in character narration) is NOT a
    # bumper sticker — it's a character recollecting. Only flag slogans.
    score.kill_bumper_sticker_theme = keyword_in_positive_context(text, bumper_sticker_themes)

    naive_patterns = [
        "good but naive", "innocent and kind", "pure of heart",
        "optimistic and hopeful", "bright-eyed and eager",
        "wide-eyed wonder", "innocent girl",
    ]
    score.kill_naive_protagonist = keyword_in_positive_context(text, naive_patterns)

    tourism_keywords = [
        "the eiffel tower", "the louvre", "big ben", "times square",
        "the colosseum", "the statue of liberty", "buckingham palace",
        "the alps were majestic", "beautiful countryside",
        "picturesque village",
    ]
    score.kill_tourism_setting = keyword_in_positive_context(text, tourism_keywords)

    helper_patterns = [
        "helps her", "comes to her aid", "friendly fairy",
        "magic helper", "guardian angel", "protector spirit",
        "wise guide who helps", "fairy tale allies",
        "the firebird helps", "lys helps",
    ]
    # More nuanced: check if fairy tales are described as helpers
    fairy_tale_sections = []
    for line in genome_yaml.split('\n'):
        if any(ft in line.lower() for ft in ['fairy', 'firebird', 'lys', 'mavka', 'wolf']):
            fairy_tale_sections.append(line.lower())
    helper_context = ' '.join(fairy_tale_sections)
    score.kill_helper_fairy_tales = any(p in helper_context for p in helper_patterns)

    existing_films = [
        "pagemaster", "inkheart", "neverending story",
        "the book of life", "strange world",
    ]
    score.kill_seen_before = keyword_in_positive_context(text, existing_films)

    # ─── DIMENSION SCORING ───

    # Surprise Factor (genre collision present?)
    genre_indicators = ["genre", "collision", "hidden genre", "secretly",
                        "on the surface", "underneath", "but actually"]
    surprise_hits = sum(1 for g in genre_indicators if g in text)
    score.surprise_factor = min(0.3 + surprise_hits * 0.1, 1.0)

    # Emotional Danger
    danger_words = ["cruel", "angry", "destroy", "betray", "consume",
                    "lose", "hurt", "damage", "break", "wound", "scar",
                    "rage", "spite", "resentment", "trauma"]
    danger_hits = sum(1 for d in danger_words if d in text)
    score.emotional_danger = min(0.1 + danger_hits * 0.05, 1.0)

    # Specificity (specific addresses, times, sensory details?)
    specificity_markers = ["rue ", "strasse", "street", "avenue", "2am", "3am",
                           "basement", "smell of", "sound of", "taste of",
                           "fluorescent", "antiseptic", "concrete",
                           "specific", "exact", "particular"]
    spec_hits = sum(1 for s in specificity_markers if s in text)
    score.specificity = min(0.1 + spec_hits * 0.06, 1.0)

    # Thematic Depth (paradox present?)
    paradox_markers = ["paradox", "dilemma", "both sides", "but also",
                       "on the other hand", "debatable", "tension between",
                       "contradiction", "opposing"]
    paradox_hits = sum(1 for p in paradox_markers if p in text)
    score.thematic_depth = min(0.2 + paradox_hits * 0.12, 1.0)

    # Character Edge
    edge_markers = ["cruel", "angry", "selfish", "resentful", "bitter",
                    "pushes away", "uncomfortable", "dark quality",
                    "makes the audience", "worst thing", "deliberately"]
    edge_hits = sum(1 for e in edge_markers if e in text)
    score.character_edge = min(0.1 + edge_hits * 0.08, 1.0)

    # Originality (fewer comparable works mentioned = higher score)
    comparable_count = text.count("comparable") + text.count("similar to")
    score.originality = max(0.2, 0.8 - comparable_count * 0.1)

    # DNA Fidelity
    dna_markers = ["save_the_cat", "cinderella", "emotional_valence",
                   "causal_chain", "beat_", "timestamp_pct"]
    dna_hits = sum(1 for d in dna_markers if d in text)
    score.dna_fidelity = min(0.2 + dna_hits * 0.1, 1.0)

    # Cultural Authenticity
    cultural_markers = ["vyshyvanka", "bandura", "sopilka", "babusya",
                        "казка", "котигорошко", "жар-птиця", "мавка",
                        "залізний", "колись давно", "рукавичка",
                        "petrykivka", "dakhabrakha"]
    cultural_hits = sum(1 for c in cultural_markers if c in text)
    score.cultural_authenticity = min(0.1 + cultural_hits * 0.08, 1.0)

    # ─── DIAGNOSIS ───
    if score.killed:
        score.diagnosis = (
            f"KILLED by {len(score.kill_reasons)} criteria. "
            f"Heuristic score: {score.overall_score:.2f}. "
            f"This genome should NOT reach the user."
        )
    elif score.overall_score < 0.70:
        score.diagnosis = (
            f"Below threshold ({score.overall_score:.2f} < 0.70). "
            f"Needs correction and regeneration."
        )
    else:
        score.diagnosis = (
            f"Score: {score.overall_score:.2f}. Passes threshold. "
            f"Ready for agent deep review."
        )

    return score


# ═══════════════════════════════════════════════════════
# CLI COMMANDS
# ═══════════════════════════════════════════════════════

def cmd_judge(args):
    """Score a genome file."""
    filepath = args.file
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        genome_yaml = f.read()

    score = heuristic_judge(genome_yaml)
    print(score.summary())

    # Save score alongside genome
    score_path = filepath.replace('.yaml', '_score.json')
    score_data = {
        "file": filepath,
        "timestamp": datetime.now().isoformat(),
        "overall_score": score.overall_score,
        "killed": score.killed,
        "kill_reasons": score.kill_reasons,
        "dimensions": {
            "surprise_factor": score.surprise_factor,
            "emotional_danger": score.emotional_danger,
            "specificity": score.specificity,
            "thematic_depth": score.thematic_depth,
            "character_edge": score.character_edge,
            "originality": score.originality,
            "dna_fidelity": score.dna_fidelity,
            "cultural_authenticity": score.cultural_authenticity,
        },
        "pass": score.pass_threshold,
    }
    with open(score_path, 'w') as f:
        json.dump(score_data, f, indent=2)
    print(f"\n💾 Score saved to: {score_path}")

    return score


def cmd_diagnose(args):
    """Score and generate corrections if failed."""
    score = cmd_judge(args)

    if score.pass_threshold:
        print("\n✅ Genome PASSES — no corrections needed.")
        return

    print("\n" + "─" * 60)
    print("GENERATING CORRECTIONS...")
    print("─" * 60)

    # Determine iteration from session state
    session_id = get_latest_session()
    iteration = 0
    if session_id:
        state = load_session_state(session_id)
        if state:
            iteration = state.get('iteration', 0)

    with open(args.file) as f:
        genome_yaml = f.read()

    prescription = diagnose(score, genome_yaml, iteration=iteration)
    print(prescription.summary())

    # Save prescription
    prescription_path = args.file.replace('.yaml', '_prescription.txt')
    with open(prescription_path, 'w') as f:
        f.write(prescription.summary())

    # Generate corrected prompt
    from engine.generation import TRANSMUTATION_PROMPT
    corrected_prompt = format_correction_prompt(prescription, TRANSMUTATION_PROMPT)
    prompt_path = args.file.replace('.yaml', '_corrected_prompt.txt')
    with open(prompt_path, 'w') as f:
        f.write(corrected_prompt)

    print(f"\n💾 Prescription saved to: {prescription_path}")
    print(f"💾 Corrected prompt saved to: {prompt_path}")

    # Update session state
    if session_id:
        state = load_session_state(session_id)
        if state:
            state['iteration'] = iteration + 1
            state['history'].append({
                "iteration": iteration + 1,
                "file": args.file,
                "score": score.overall_score,
                "killed": score.killed,
                "timestamp": datetime.now().isoformat(),
            })
            save_session_state(session_id, state)


def cmd_init_session(args):
    """Initialize a new generation session."""
    init_session(args.reference, args.direction)


def cmd_status(args):
    """Show system status."""
    print("═══ ANIMATION GENOME MACHINE — SYSTEM STATUS ═══")
    print()

    # Engine modules
    engine_dir = Path("engine")
    total_lines = 0
    for f in sorted(engine_dir.glob("*.py")):
        lines = sum(1 for _ in open(f))
        total_lines += lines
        status = "✅" if lines > 20 else "📦"  # stub vs real
        print(f"  {status} {f.name}: {lines} lines")
    print(f"\n  Total engine code: {total_lines} lines")

    # Genomes in vault
    print()
    vault_dna = Path("vault/00-film-dna")
    if vault_dna.exists():
        genomes = list(vault_dna.glob("*.yaml"))
        print(f"  📁 Film genomes: {len(genomes)}")
        for g in genomes:
            lines = sum(1 for _ in open(g))
            print(f"     {g.name}: {lines} lines")

    # Sessions
    print()
    sessions_path = Path(SESSION_DIR)
    if sessions_path.exists():
        sessions = sorted(sessions_path.iterdir(), reverse=True)
        print(f"  📁 Sessions: {len(sessions)}")
        for s in sessions[:3]:
            state = load_session_state(s.name)
            if state:
                print(f"     {s.name}: iteration {state['iteration']}, "
                      f"best={state.get('best_score', 'N/A')}, "
                      f"status={state['status']}")
    else:
        print("  📁 Sessions: none")

    # Review files
    print()
    review_dir = Path("vault/05-review")
    if review_dir.exists():
        reviews = list(review_dir.glob("*.yaml"))
        print(f"  📁 Review iterations: {len(reviews)}")
        for r in sorted(reviews):
            print(f"     {r.name}")


def cmd_compare(args):
    """Compare two genome scores side by side."""
    file_a, file_b = args.files
    for f in [file_a, file_b]:
        if not os.path.exists(f):
            print(f"❌ File not found: {f}")
            sys.exit(1)

    with open(file_a) as f:
        yaml_a = f.read()
    with open(file_b) as f:
        yaml_b = f.read()

    score_a = heuristic_judge(yaml_a)
    score_b = heuristic_judge(yaml_b)

    name_a = Path(file_a).stem
    name_b = Path(file_b).stem

    print(f"═══ COMPARISON: {name_a} vs {name_b} ═══")
    print()
    print(f"{'Dimension':<25} {'':>3}{name_a:>12} {name_b:>12}  {'Winner':>10}")
    print("─" * 70)

    dimensions = [
        ('Surprise Factor', score_a.surprise_factor, score_b.surprise_factor),
        ('Emotional Danger', score_a.emotional_danger, score_b.emotional_danger),
        ('Specificity', score_a.specificity, score_b.specificity),
        ('Thematic Depth', score_a.thematic_depth, score_b.thematic_depth),
        ('Character Edge', score_a.character_edge, score_b.character_edge),
        ('Originality', score_a.originality, score_b.originality),
        ('DNA Fidelity', score_a.dna_fidelity, score_b.dna_fidelity),
        ('Cultural Auth', score_a.cultural_authenticity, score_b.cultural_authenticity),
    ]

    for dim, va, vb in dimensions:
        winner = name_a if va > vb else name_b if vb > va else "tie"
        arrow = "←" if va > vb else "→" if vb > va else "="
        print(f"  {dim:<23} {arrow:>3}{va:>10.2f}   {vb:>10.2f}  {winner:>10}")

    print("─" * 70)
    print(f"  {'OVERALL':<23} {'':>3}{score_a.overall_score:>10.2f}   {score_b.overall_score:>10.2f}  "
          f"{'← ' + name_a if score_a.overall_score > score_b.overall_score else '→ ' + name_b:>10}")
    print()
    print(f"  Killed: {name_a}={'YES 💀' if score_a.killed else 'no'}, "
          f"{name_b}={'YES 💀' if score_b.killed else 'no'}")

def cmd_beats(args):
    """Run beat-by-beat scene-level scoring on a genome."""
    filepath = args.file
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        genome_yaml = f.read()

    ref_yaml = ''
    if args.reference and os.path.exists(args.reference):
        with open(args.reference) as f:
            ref_yaml = f.read()

    report = score_beats(genome_yaml, ref_yaml)
    print(report.summary())

    # Save report alongside genome
    report_path = filepath.replace('.yaml', '_beats.txt')
    with open(report_path, 'w') as f:
        f.write(report.summary())
    print(f"\n💾 Beat report saved to: {report_path}")


def cmd_script(args):
    """Generate a scene script from a beat."""
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    with open(args.file) as f:
        genome_yaml = f.read()
    script = generate_scene_script(genome_yaml, args.beat)
    print(script)
    out_path = args.file.replace('.yaml', f'_{args.beat}_script.txt')
    with open(out_path, 'w') as f:
        f.write(script)
    print(f"\n💾 Script saved to: {out_path}")


def cmd_pitch(args):
    """Generate a pitch deck."""
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    with open(args.file) as f:
        genome_yaml = f.read()
    pitch = generate_pitch_deck(genome_yaml)
    print(pitch)
    out_path = args.file.replace('.yaml', '_pitch.txt')
    with open(out_path, 'w') as f:
        f.write(pitch)
    print(f"\n💾 Pitch saved to: {out_path}")


def cmd_emotions(args):
    """Generate audience emotion map."""
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    with open(args.file) as f:
        genome_yaml = f.read()
    data, chart = generate_emotion_map(genome_yaml)
    print(chart)
    out_path = args.file.replace('.yaml', '_emotions.txt')
    with open(out_path, 'w') as f:
        f.write(chart)
    json_path = args.file.replace('.yaml', '_emotions.json')
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n💾 Emotion map saved to: {out_path}")
    print(f"💾 Emotion data saved to: {json_path}")


def cmd_patterns(args):
    """Show anti-pattern database or scan a file."""
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        with open(args.file) as f:
            text = f.read()
        found = find_patterns_in_text(text)
        if found:
            print(f"═══ ANTI-PATTERNS FOUND IN {Path(args.file).name} ═══")
            for ap, kw in found:
                icon = "💀" if ap.severity == 'kill' else '⚠️'
                print(f"  {icon} {ap.id}: {ap.name}")
                print(f"     Matched: '{kw}'")
                print(f"     Fix: {ap.fix_strategy[:120]}...")
                print()
        else:
            print("✅ No anti-patterns detected.")
    else:
        print(ap_summary())


def cmd_compete(args):
    """Show competitive generation setup."""
    print("═══ COMPETITIVE GENERATION — GENERATOR PROFILES ═══")
    print()
    for g in GENERATORS:
        print(f"  🎭 {g.name}: {g.role}")
        print(f"     Priorities: {', '.join(g.priority_dimensions)}")
        print(f"     Sacrifices: {', '.join(g.sacrifice_dimensions)}")
        print()
    print("To launch competitive generation, the orchestrator invokes")
    print("3 genome_generator subagents with different personalities.")
    print("Results are scored and the winner is selected or merged.")


def cmd_refine(args):
    """Run progressive refinement analysis on a genome."""
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)
    with open(args.file) as f:
        genome_yaml = f.read()
    weakest = identify_weakest_beats(genome_yaml, n=int(args.top or 5))
    print("═══ PROGRESSIVE REFINEMENT — BEAT ANALYSIS ═══")
    print()
    print("Beats ranked weakest to strongest:")
    for w in weakest:
        dims = ', '.join(f"{d}={s:.2f}" for d, s in w['weak_dimensions'])
        print(f"  {w['overall']:.2f}  {w['beat_id']}: {w['beat_name']}")
        print(f"         Weakest dims: {dims}")
    print()
    print(f"Recommended: regenerate the top {min(3, len(weakest))} weakest beats.")
    print("Run 'python3 runner.py beats <file>' for full scene-level scoring.")


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Animation Genome Machine — Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 runner.py status
  python3 runner.py judge vault/00-film-dna/kazka_genome.yaml
  python3 runner.py diagnose vault/00-film-dna/kazka_genome.yaml
  python3 runner.py compare file_a.yaml file_b.yaml
  python3 runner.py init-session --reference zootopia.yaml --direction "..."
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    # judge
    p_judge = subparsers.add_parser("judge", help="Score a genome file")
    p_judge.add_argument("file", help="Path to genome YAML file")

    # diagnose
    p_diagnose = subparsers.add_parser("diagnose", help="Score + generate corrections")
    p_diagnose.add_argument("file", help="Path to genome YAML file")

    # init-session
    p_init = subparsers.add_parser("init-session", help="Initialize a generation session")
    p_init.add_argument("--reference", required=True, help="Path to reference genome")
    p_init.add_argument("--direction", required=True, help="Creative direction text")

    # status
    subparsers.add_parser("status", help="Show system status")

    # compare
    p_compare = subparsers.add_parser("compare", help="Compare two genomes")
    p_compare.add_argument("files", nargs=2, help="Two YAML files to compare")

    # beats
    p_beats = subparsers.add_parser("beats", help="Beat-by-beat scene-level scoring")
    p_beats.add_argument("file", help="Path to genome YAML file")
    p_beats.add_argument("--reference", "-r", default="", help="Optional reference genome for comparison")

    # script
    p_script = subparsers.add_parser("script", help="Generate scene script from a beat")
    p_script.add_argument("file", help="Path to genome YAML file")
    p_script.add_argument("beat", help="Beat ID (e.g. beat_09)")

    # pitch
    p_pitch = subparsers.add_parser("pitch", help="Generate pitch deck")
    p_pitch.add_argument("file", help="Path to genome YAML file")

    # emotions
    p_emotions = subparsers.add_parser("emotions", help="Generate audience emotion map")
    p_emotions.add_argument("file", help="Path to genome YAML file")

    # patterns
    p_patterns = subparsers.add_parser("patterns", help="Show anti-pattern database or scan file")
    p_patterns.add_argument("file", nargs="?", default=None, help="Optional file to scan")

    # compete
    subparsers.add_parser("compete", help="Show competitive generation setup")

    # refine
    p_refine = subparsers.add_parser("refine", help="Progressive refinement analysis")
    p_refine.add_argument("file", help="Path to genome YAML file")
    p_refine.add_argument("--top", "-n", default=5, help="Number of weakest beats to show")

    args = parser.parse_args()

    commands = {
        "judge": cmd_judge,
        "diagnose": cmd_diagnose,
        "init-session": cmd_init_session,
        "status": cmd_status,
        "compare": cmd_compare,
        "beats": cmd_beats,
        "script": cmd_script,
        "pitch": cmd_pitch,
        "emotions": cmd_emotions,
        "patterns": cmd_patterns,
        "compete": cmd_compete,
        "refine": cmd_refine,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
