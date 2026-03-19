"""Badge generation — shields.io-style SVG badges for skill grades."""

from __future__ import annotations


# Grade-to-color mapping (shields.io palette)
_GRADE_COLORS: dict[str, str] = {
    "A+": "#4c1",
    "A": "#4c1",
    "B": "#97ca00",
    "C": "#dfb317",
    "D": "#fe7d37",
    "F": "#e05d44",
}


def _text_width(text: str) -> int:
    """Estimate text width in tenths of a pixel for Verdana 11px."""
    # Approximate character widths for Verdana at 110 (scaled .1)
    # These are rough estimates matching shields.io behavior
    widths = {
        "A": 75, "B": 72, "C": 72, "D": 76, "F": 64,
        "+": 65, "a": 63, "b": 65, "c": 56, "d": 65,
        "e": 60, "f": 37, "g": 63, "h": 65, "i": 28,
        "j": 31, "k": 60, "l": 28, "m": 96, "n": 65,
        "o": 63, "p": 65, "q": 65, "r": 42, "s": 52,
        "t": 40, "u": 65, "v": 58, "w": 82, "x": 58,
        "y": 58, "z": 52, " ": 33, ":": 33, ".": 33,
        "0": 65, "1": 65, "2": 65, "3": 65, "4": 65,
        "5": 65, "6": 65, "7": 65, "8": 65, "9": 65,
    }
    return sum(widths.get(ch, 65) for ch in text)


def generate_badge_svg(
    label: str = "proofagent",
    grade: str = "A+",
    score: float = 9.2,
) -> str:
    """Generate a shields.io-style SVG badge.

    Args:
        label: Left-side text (default: "proofagent").
        grade: Grade to display on the right side (A+, A, B, C, D, F).
        score: Numeric score for the title/accessibility attribute.

    Returns:
        SVG string suitable for writing to a .svg file.
    """
    color = _GRADE_COLORS.get(grade, "#9f9f9f")

    # Calculate widths (in tenths of pixels, matching shields.io scale(.1))
    label_tw = _text_width(label)
    grade_tw = _text_width(grade)

    # Padding: 5px each side = 100 tenths; minimum 30px for grade section
    label_width = (label_tw + 100) // 10
    grade_width = max(30, (grade_tw + 100) // 10)

    total_width = label_width + grade_width

    # Text positions (center of each section, in tenths)
    label_x = label_width * 10 // 2
    grade_x = label_width * 10 + grade_width * 10 // 2

    title = f"{label}: {grade} ({score:.1f}/10)"

    return f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {grade}">
  <title>{title}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{grade_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110">
    <text aria-hidden="true" x="{label_x}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{label_tw}">{label}</text>
    <text x="{label_x}" y="140" transform="scale(.1)" fill="#fff" textLength="{label_tw}">{label}</text>
    <text aria-hidden="true" x="{grade_x}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="{grade_tw}">{grade}</text>
    <text x="{grade_x}" y="140" transform="scale(.1)" fill="#fff" textLength="{grade_tw}">{grade}</text>
  </g>
</svg>
"""


def generate_badge_markdown(
    agent_name: str,
    grade: str,
    base_url: str = "https://proofagent.dev",
) -> str:
    """Generate markdown for embedding the badge.

    Args:
        agent_name: Name/identifier for the agent (used in URL path).
        grade: Grade string to display in alt text.
        base_url: Base URL for the badge and skill page links.

    Returns:
        Markdown image-link string.
    """
    return f"[![proofagent: {grade}]({base_url}/badge/{agent_name}.svg)]({base_url}/skills/{agent_name})"


def generate_badge_html(
    agent_name: str,
    grade: str,
    base_url: str = "https://proofagent.dev",
) -> str:
    """Generate HTML for embedding the badge.

    Args:
        agent_name: Name/identifier for the agent (used in URL path).
        grade: Grade string to display in alt text.
        base_url: Base URL for the badge and skill page links.

    Returns:
        HTML anchor+img string.
    """
    return (
        f'<a href="{base_url}/skills/{agent_name}">'
        f'<img src="{base_url}/badge/{agent_name}.svg" alt="proofagent: {grade}" />'
        f"</a>"
    )
