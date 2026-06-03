"""
Output Engine — System v3, Layer 6

Generates 4 new output types from a Film Genome Document:
1. Scene Scripts — 2-minute screenplay format scenes
2. Visual Prompts — Image generation prompts for key frames
3. Pitch Deck — Structured 1-page pitch
4. Audience Emotion Map — Beat-by-beat emotional trajectory with ASCII chart
"""

import yaml
from typing import Optional


def _parse_genome(genome_yaml: str) -> dict:
    """Parse genome YAML into dict, with error handling."""
    try:
        return yaml.safe_load(genome_yaml) or {}
    except Exception:
        return {}


def _get_beat(data: dict, beat_id: str) -> Optional[dict]:
    """Find a specific beat by ID."""
    beats = data.get('narrative_dna', {}).get('beats', [])
    for b in beats:
        if isinstance(b, dict) and b.get('id') == beat_id:
            return b
    return None


def _get_character(data: dict, char_id: str) -> Optional[dict]:
    """Find a character by ID."""
    chars = data.get('character_dna', {}).get('characters', [])
    for c in chars:
        if isinstance(c, dict) and c.get('id') == char_id:
            return c
    return None


# ═══════════════════════════════════════════════════════
# OUTPUT 1: SCENE SCRIPT
# ═══════════════════════════════════════════════════════

def generate_scene_script(genome_yaml: str, beat_id: str) -> str:
    """
    Expand a beat into a 2-minute screenplay-format scene.
    Pulls from narrative, character, visual, and audio DNA.
    """
    data = _parse_genome(genome_yaml)
    beat = _get_beat(data, beat_id)

    if not beat:
        return f"# ERROR: Beat '{beat_id}' not found in genome."

    name = beat.get('name', 'Untitled')
    description = beat.get('description', '')
    timestamp = beat.get('timestamp_pct', 0)
    duration = beat.get('duration_pct', 0.05)

    # Extract location from description
    location = "UNKNOWN LOCATION"
    for line in description.split('\n'):
        line_stripped = line.strip()
        if line_stripped.upper().startswith('LOCATION:'):
            location = line_stripped[9:].strip()
            break

    # Determine INT/EXT and time
    loc_lower = location.lower()
    prefix = "INT." if any(w in loc_lower for w in ['apartment', 'basement', 'room',
                                                      'facility', 'hallway', 'center',
                                                      'kitchen', 'bathroom']) else "EXT."
    time = "NIGHT" if any(w in loc_lower for w in ['2am', '3am', '11 pm', 'night',
                                                     'evening']) else "DAY"

    # Calculate screen time
    runtime_min = data.get('metadata', {}).get('target_duration_minutes', 90)
    scene_seconds = int(runtime_min * 60 * duration)
    scene_min = scene_seconds // 60
    scene_sec = scene_seconds % 60

    lines = []
    lines.append("=" * 65)
    lines.append(f"  SCENE SCRIPT: {name}")
    lines.append(f"  Beat: {beat_id} | Screen Time: ~{scene_min}:{scene_sec:02d}")
    lines.append(f"  Film Position: {timestamp:.0%}")
    lines.append("=" * 65)
    lines.append("")
    lines.append(f"  {prefix} {location.upper()} — {time}")
    lines.append("")

    # Parse description into action + dialogue blocks
    desc_lines = description.strip().split('\n')
    for line in desc_lines:
        line = line.strip()
        if not line:
            lines.append("")
            continue

        # Skip meta-lines (LOCATION, MAPS TO)
        if line.upper().startswith(('LOCATION:', 'MAPS TO', 'KEY DIFFERENCE',
                                    'MAPS TO ZOOTOPIA', 'THE "FUN"')):
            lines.append(f"  [{line}]")
            continue

        # Character dialogue (NAME: "text" or NAME: (text))
        if ':' in line and line.split(':')[0].strip().isupper():
            parts = line.split(':', 1)
            char_name = parts[0].strip()
            dialogue = parts[1].strip()

            # Check for parenthetical
            if dialogue.startswith('(') and ')' in dialogue:
                paren_end = dialogue.index(')') + 1
                parenthetical = dialogue[:paren_end]
                actual_dialogue = dialogue[paren_end:].strip()
                lines.append(f"                    {char_name}")
                lines.append(f"              {parenthetical}")
                if actual_dialogue:
                    lines.append(f"        {actual_dialogue}")
            else:
                lines.append(f"                    {char_name}")
                lines.append(f"        {dialogue}")
            lines.append("")
            continue

        # Dialogue indicated by quotes or em-dash
        if line.startswith(('—', '"', "'")) or line.startswith('\"'):
            lines.append(f"        {line}")
            continue

        # Action/description
        lines.append(f"  {line}")

    lines.append("")
    lines.append("=" * 65)
    lines.append(f"  END SCENE: {name}")
    lines.append("=" * 65)

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# OUTPUT 2: VISUAL PROMPTS
# ═══════════════════════════════════════════════════════

def generate_visual_prompts(genome_yaml: str, beat_id: str) -> list:
    """
    Generate image prompts for key frames of a scene.
    Returns list of dicts with frame info.
    """
    data = _parse_genome(genome_yaml)
    beat = _get_beat(data, beat_id)

    if not beat:
        return [{"error": f"Beat '{beat_id}' not found"}]

    description = beat.get('description', '')
    name = beat.get('name', '')
    valence = beat.get('emotional_valence', 0)
    arousal = beat.get('emotional_arousal', 0)

    # Get visual DNA
    visual = data.get('visual_dna', {})
    style = visual.get('animation_style', {})
    style_desc = style.get('base', '3D animation') if isinstance(style, dict) else '3D animation'

    # Determine mood from emotional values
    if valence < -0.3:
        mood = "dark, somber, heavy"
    elif valence < 0.2:
        mood = "tense, uncertain, liminal"
    elif valence < 0.6:
        mood = "cautiously warm, fragile hope"
    else:
        mood = "warm, luminous, earned"

    if arousal > 0.7:
        mood += ", high intensity, visceral"
    elif arousal < 0.3:
        mood += ", quiet, still, intimate"

    # Extract key moments from description for frames
    desc_lines = [l.strip() for l in description.split('\n') if l.strip()]
    # Find lines with visual action (not dialogue, not meta)
    visual_moments = []
    for line in desc_lines:
        if line.upper().startswith(('LOCATION:', 'MAPS TO')):
            continue
        if ':' in line and line.split(':')[0].strip().isupper() and len(line.split(':')[0]) < 20:
            continue  # Skip dialogue
        if any(word in line.lower() for word in ['appears', 'manifests', 'breaks',
                                                   'opens', 'sits', 'walks', 'stands',
                                                   'looks', 'holds', 'touches', 'cries',
                                                   'enters', 'leaves', 'burns', 'floods']):
            visual_moments.append(line)

    # Generate prompts for up to 6 key frames
    prompts = []
    frame_moments = visual_moments[:6] if visual_moments else desc_lines[:6]

    for i, moment in enumerate(frame_moments):
        # Determine camera based on content
        if any(w in moment.lower() for w in ['face', 'eyes', 'tears', 'expression']):
            camera = "extreme close-up"
        elif any(w in moment.lower() for w in ['room', 'apartment', 'hallway', 'center']):
            camera = "wide establishing shot"
        elif any(w in moment.lower() for w in ['manifests', 'appears', 'burns', 'floods']):
            camera = "medium shot, slight low angle"
        else:
            camera = "medium close-up"

        # Determine lighting
        if any(w in moment.lower() for w in ['fluorescent', 'clinical', 'white']):
            lighting = "harsh fluorescent overhead, institutional"
        elif any(w in moment.lower() for w in ['night', '2am', 'dark', 'evening']):
            lighting = "dim practical lighting, shadows dominant"
        elif any(w in moment.lower() for w in ['golden', 'warm', 'sun']):
            lighting = "warm golden hour, soft directional"
        else:
            lighting = "naturalistic, soft overcast window light"

        prompt = {
            "frame_number": i + 1,
            "description": moment[:150],
            "prompt": (
                f"Animated film still, {style_desc}. {moment[:200]}. "
                f"Mood: {mood}. {camera}. {lighting}. "
                f"Cinematic, feature-film quality, emotional, "
                f"studio Ghibli meets Pan's Labyrinth aesthetic."
            ),
            "camera": camera,
            "lighting": lighting,
            "mood": mood,
        }
        prompts.append(prompt)

    return prompts


# ═══════════════════════════════════════════════════════
# OUTPUT 3: PITCH DECK
# ═══════════════════════════════════════════════════════

def generate_pitch_deck(genome_yaml: str) -> str:
    """Generate a structured pitch document from a Film Genome."""
    data = _parse_genome(genome_yaml)
    meta = data.get('metadata', {})
    narrative = data.get('narrative_dna', {})
    chars = data.get('character_dna', {}).get('characters', [])
    visual = data.get('visual_dna', {})
    themes = narrative.get('themes', [])

    title = meta.get('title', 'Untitled')
    genre_surface = meta.get('genre_surface', meta.get('genre', 'Animation'))
    genre_hidden = meta.get('genre_hidden', '')
    pitch = meta.get('one_sentence_pitch', '')
    runtime = meta.get('target_duration_minutes', 90)

    # Build synopsis from beats
    beats = narrative.get('beats', [])
    setup_beats = [b for b in beats if b.get('timestamp_pct', 0) < 0.25]
    confrontation_beats = [b for b in beats if 0.25 <= b.get('timestamp_pct', 0) < 0.75]
    resolution_beats = [b for b in beats if b.get('timestamp_pct', 0) >= 0.75]

    def summarize_beats(beat_list, max_chars=400):
        descs = []
        for b in beat_list:
            desc = b.get('description', '')
            # First meaningful sentence
            for line in desc.split('\n'):
                line = line.strip()
                if line and not line.upper().startswith(('LOCATION:', 'MAPS TO', 'KEY DIFF')):
                    if ':' in line and line.split(':')[0].strip().isupper() and len(line.split(':')[0]) < 15:
                        continue
                    descs.append(line)
                    break
        combined = ' '.join(descs)
        return combined[:max_chars] + ('...' if len(combined) > max_chars else '')

    # Thematic statement
    theme_text = ""
    if themes and isinstance(themes[0], dict):
        t = themes[0]
        theme_text = t.get('paradox', '')

    # Characters
    char_lines = []
    for c in chars[:4]:
        if isinstance(c, dict):
            name = c.get('name', 'Unknown')
            archetype = c.get('archetype', '')
            arc = c.get('arc', '')
            # First sentence of arc
            arc_short = arc.split('.')[0].strip() + '.' if arc else ''
            char_lines.append(f"  **{name}** ({archetype}): {arc_short[:120]}")

    lines = [
        "╔══════════════════════════════════════════════════════════════╗",
        f"║  {title.upper():^58}  ║",
        "║  PITCH DECK                                                 ║",
        "╚══════════════════════════════════════════════════════════════╝",
        "",
        f"**Logline:** {pitch}",
        "",
        f"**Genre:** {genre_surface}" + (f" (hidden: {genre_hidden})" if genre_hidden else ""),
        f"**Runtime:** {runtime} minutes",
        f"**Format:** Animated Feature Film",
        "",
        "───────────────────────────────────────────────────────────────",
        "  SYNOPSIS",
        "───────────────────────────────────────────────────────────────",
        "",
        f"**Setup:** {summarize_beats(setup_beats)}",
        "",
        f"**Confrontation:** {summarize_beats(confrontation_beats)}",
        "",
        f"**Resolution:** {summarize_beats(resolution_beats)}",
        "",
        "───────────────────────────────────────────────────────────────",
        "  CHARACTERS",
        "───────────────────────────────────────────────────────────────",
        "",
    ]
    lines.extend(char_lines)
    lines.extend([
        "",
        "───────────────────────────────────────────────────────────────",
        "  THEMATIC STATEMENT",
        "───────────────────────────────────────────────────────────────",
        "",
        f"  \"{theme_text}\"",
        "",
        "  This is not a moral. It is a paradox. The film argues both sides.",
        "",
        "───────────────────────────────────────────────────────────────",
        "  WHY NOW",
        "───────────────────────────────────────────────────────────────",
        "",
        "  The world has 100 million displaced people. Every one of them",
        "  carries stories from a place they can't return to. This film",
        "  is for them — and for everyone who needs to understand what",
        "  it means to carry a home that exists only in memory.",
        "",
        "╔══════════════════════════════════════════════════════════════╗",
        "║  END PITCH                                                  ║",
        "╚══════════════════════════════════════════════════════════════╝",
    ])

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# OUTPUT 4: AUDIENCE EMOTION MAP
# ═══════════════════════════════════════════════════════

def generate_emotion_map(genome_yaml: str):
    """
    Generate beat-by-beat emotional trajectory.
    Returns (data: list[dict], ascii_chart: str).
    """
    data = _parse_genome(genome_yaml)
    beats = data.get('narrative_dna', {}).get('beats', [])

    emotion_data = []
    for b in beats:
        if isinstance(b, dict):
            emotion_data.append({
                'beat_id': b.get('id', ''),
                'beat_name': b.get('name', ''),
                'timestamp_pct': b.get('timestamp_pct', 0),
                'valence': b.get('emotional_valence', 0),
                'arousal': b.get('emotional_arousal', 0),
            })

    # Build ASCII chart
    chart_width = 60
    chart_height = 20
    min_val = -1.0
    max_val = 1.0

    # Create grid
    grid = [[' ' for _ in range(chart_width)] for _ in range(chart_height)]

    # Draw axes
    mid_y = chart_height // 2
    for x in range(chart_width):
        grid[mid_y][x] = '─'  # Zero line
    for y in range(chart_height):
        grid[y][0] = '│'
    grid[mid_y][0] = '┼'

    # Plot valence points
    for ed in emotion_data:
        x = int(ed['timestamp_pct'] * (chart_width - 2)) + 1
        # Map valence (-1..1) to y position (chart_height-1..0)
        y = int((1 - (ed['valence'] + 1) / 2) * (chart_height - 1))
        y = max(0, min(chart_height - 1, y))
        x = max(1, min(chart_width - 1, x))

        # Use arousal to determine character
        if ed['arousal'] > 0.7:
            char = '●'
        elif ed['arousal'] > 0.4:
            char = '◉'
        else:
            char = '○'
        grid[y][x] = char

    # Build chart string
    chart_lines = [
        "═══ AUDIENCE EMOTION MAP ═══",
        "",
        "  Valence (emotional positivity) over film timeline",
        "  ● = high arousal | ◉ = medium | ○ = low arousal",
        "",
        f"  +1.0 {'':─>{chart_width - 4}}",
    ]

    for y in range(chart_height):
        row = ''.join(grid[y])
        label = ""
        if y == 0:
            label = " +1.0 (joy)"
        elif y == mid_y:
            label = "  0.0 (neutral)"
        elif y == chart_height - 1:
            label = " -1.0 (grief)"
        chart_lines.append(f"  {row} {label}")

    chart_lines.append(f"  {'':─>{chart_width}}")
    chart_lines.append(f"  0%{'':>{chart_width - 6}}100%")
    chart_lines.append("")

    # Beat legend
    chart_lines.append("─── BEAT LEGEND ───")
    for ed in emotion_data:
        name_short = ed['beat_name'][:35]
        bar_val = int((ed['valence'] + 1) / 2 * 20)
        bar = '█' * bar_val + '░' * (20 - bar_val)
        chart_lines.append(
            f"  {ed['timestamp_pct']:>5.0%} [{bar}] {ed['valence']:+.1f}v {ed['arousal']:.1f}a  {name_short}"
        )

    return emotion_data, "\n".join(chart_lines)


if __name__ == "__main__":
    import os
    import sys

    genome_path = "vault/00-film-dna/kazka_v2_genome.yaml"
    if not os.path.exists(genome_path):
        print(f"File not found: {genome_path}")
        sys.exit(1)

    with open(genome_path) as f:
        genome_yaml = f.read()

    # Test pitch deck
    print(generate_pitch_deck(genome_yaml))
    print("\n")

    # Test emotion map
    _, chart = generate_emotion_map(genome_yaml)
    print(chart)
    print("\n")

    # Test scene script
    print(generate_scene_script(genome_yaml, "beat_09"))
