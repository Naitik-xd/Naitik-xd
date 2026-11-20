import html
import json
import math
import os
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

STATIC = os.environ.get("STATIC", "0") == "1"

# Light Paper & Ink Palette
PAPER = "#FAF8F5"
PAPER_ALT = "#F3EFE9"
BORDER = "#E5E0D8"
INK = "#1A1918"
INK_MUTED = "#6E6A63"
BLUE = "#2563EB"
RED = "#DC2626"
YELLOW = "#D97706"

BLUE_LEVELS = ["#ECE8E1", "#BFDBFE", "#60A5FA", "#2563EB", "#1E3A8A"]

COMMON_CSS = f"""
  .serif {{ font-family: Georgia, 'Times New Roman', serif; }}
  .sans  {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; }}
  .mono  {{ font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }}
  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  @keyframes popIn {{
    0%   {{ opacity: 0; transform: scale(0.6); }}
    70%  {{ opacity: 1; transform: scale(1.08); }}
    100% {{ opacity: 1; transform: scale(1); }}
  }}
  @keyframes barGrow {{
    from {{ transform: scaleY(0); }}
    to   {{ transform: scaleY(1); }}
  }}
  @keyframes pulseDot {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%      {{ opacity: 0.45; transform: scale(1.35); }}
  }}
  @keyframes tileSpring {{
    0%   {{ opacity: 0; transform: translateY(20px) rotate(-1.5deg); }}
    70%  {{ opacity: 1; transform: translateY(-3px) rotate(0.4deg); }}
    100% {{ opacity: 1; transform: translateY(0) rotate(0deg); }}
  }}
  @keyframes ringPulse {{
    0%   {{ opacity: 0.5; transform: scale(0.8); }}
    100% {{ opacity: 0; transform: scale(1.7); }}
  }}
  @keyframes arrowNudge {{
    0%, 100% {{ transform: translateX(0); }}
    50%      {{ transform: translateX(4px); }}
  }}
  @keyframes rowPrint {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; opacity: 1 !important; transform: none !important; }}
  }}
"""


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def load_data():
    with open("data/contributions.json", "r", encoding="utf-8") as f:
        return json.load(f)


def face_to_ascii_lines(img_path="source-photo.png", cols=88, rows=52):
    """High-res sharpened face-only ASCII portrait with clean outer fade."""
    if not os.path.exists(img_path):
        return ["   [ upload source-photo.png ]"]

    img = Image.open(img_path).convert("L")
    w, h = img.size

    # Tight face + hair crop
    crop_box = (int(w * 0.33), int(h * 0.22), int(w * 0.99), int(h * 0.58))
    face = img.crop(crop_box)
    face = ImageOps.autocontrast(face, cutoff=2)
    face = face.filter(ImageFilter.SHARPEN)
    face = ImageEnhance.Contrast(face).enhance(1.65)
    face = face.resize((cols, rows), Image.Resampling.LANCZOS)

    # Richer character ramp for crisp glasses, eyes, and smile
    chars = "@#W$9876543210?!abc;:+=-,._ "
    pixels = face.load()
    lines = []

    cx, cy = cols / 2.0, rows / 2.0
    rx, ry = cols * 0.49, rows * 0.49

    for y in range(rows):
        row_chars = []
        for x in range(cols):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            dist = math.sqrt(dx * dx + dy * dy)
            val = pixels[x, y]
            if dist > 0.96:
                val = 255
            elif dist > 0.80:
                blend = (dist - 0.80) / 0.16
                val = int(val * (1 - blend) + 255 * blend)

            idx = min(len(chars) - 1, int(val / 256 * len(chars)))
            row_chars.append(chars[idx])
        lines.append("".join(row_chars))
    return lines


def render_hero():
    ascii_lines = face_to_ascii_lines()
    ascii_svg = []
    for i, line in enumerate(ascii_lines):
        delay = 0 if STATIC else round(0.12 + i * 0.016, 3)
        style = "" if STATIC else f"opacity:0;animation:rowPrint 0.06s ease forwards {delay}s;"
        ascii_svg.append(
            f'<text x="530" y="{28 + i * 4.6:.1f}" class="mono" font-size="4.3" '
            f'fill="{INK}" xml:space="preserve" style="{style}">{esc(line)}</text>'
        )

    anim_title = "" if STATIC else "opacity:0;animation:fadeUp 0.6s ease forwards 0.1s;"
    anim_sub = "" if STATIC else "opacity:0;animation:fadeUp 0.6s ease forwards 0.25s;"
    anim_dot = "" if STATIC else "transform-box:fill-box;transform-origin:center;animation:pulseDot 2.2s ease-in-out infinite;"
    shine_anim = (
        ""
        if STATIC
        else '<animateTransform attributeName="gradientTransform" type="translate" from="-1 0" to="2 0" dur="4s" repeatCount="indefinite"/>'
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 285" width="840" height="285">
  <defs>
    <linearGradient id="inkShine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{INK}"/>
      <stop offset="42%" stop-color="{INK}"/>
      <stop offset="50%" stop-color="{BLUE}"/>
      <stop offset="58%" stop-color="{INK}"/>
      <stop offset="100%" stop-color="{INK}"/>
      {shine_anim}
    </linearGradient>
  </defs>
  <style>{COMMON_CSS}</style>
  <rect x="0.5" y="0.5" width="839" height="284" rx="14" fill="{PAPER}" stroke="{BORDER}"/>

  <g style="{anim_title}">
    <rect x="36" y="34" width="210" height="26" rx="13" fill="{PAPER_ALT}" stroke="{BORDER}"/>
    <circle cx="52" cy="47" r="4" fill="{BLUE}" style="{anim_dot}"/>
    <text x="64" y="51" class="mono" font-size="10.5" fill="{INK_MUTED}">AI WEB DEVELOPER · INDIA</text>
  </g>

  <g style="{anim_title}">
    <text x="36" y="122" class="serif" font-size="54" fill="{INK}" letter-spacing="-1">Naitik</text>
    <text x="36" y="176" class="serif" font-size="54" font-style="italic" fill="url(#inkShine)" letter-spacing="-1">Agarwal.</text>
  </g>

  <g style="{anim_sub}">
    <text x="36" y="214" class="sans" font-size="14.5" fill="{INK_MUTED}">Building full-stack AI web apps, open-weight tools,</text>
    <text x="36" y="234" class="sans" font-size="14.5" fill="{INK_MUTED}">and clean interactive experiences.</text>
    <text x="36" y="262" class="mono" font-size="11" fill="{BLUE}">na1t1k.vercel.app  ·  @Naitik-xd</text>
  </g>

  <line x1="505" y1="24" x2="505" y2="261" stroke="{BORDER}" stroke-dasharray="3 4"/>
  <g>{''.join(ascii_svg)}</g>
</svg>"""


def render_contrib_graph(data):
    days = data["days"]
    cells = []
    cell_size = 11
    gap = 3.5
    start_x = 36
    start_y = 58

    for idx, d in enumerate(days):
        week = idx // 7
        dow = idx % 7
        x = start_x + week * (cell_size + gap)
        y = start_y + dow * (cell_size + gap)
        color = BLUE_LEVELS[min(4, d["level"])]
        delay = 0 if STATIC else round(0.5 + week * 0.018, 3)
        style = (
            ""
            if STATIC
            else f"opacity:0;transform-box:fill-box;transform-origin:center;animation:popIn 0.25s ease forwards {delay}s;"
        )
        cells.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" height="{cell_size}" rx="2.5" fill="{color}" style="{style}"/>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 185" width="840" height="185">
  <style>{COMMON_CSS}</style>
  <rect x="0.5" y="0.5" width="839" height="184" rx="14" fill="{PAPER}" stroke="{BORDER}"/>
  <text x="36" y="36" class="serif" font-size="20" fill="{INK}">Contribution Graph</text>
  <text x="804" y="36" text-anchor="end" class="mono" font-size="11.5" fill="{INK_MUTED}">{data['total']} contributions in the last year</text>
  {''.join(cells)}
</svg>"""


def render_activity(data):
    months = data["months"]
    max_val = max((m["count"] for m in months), default=1) or 1
    best_idx = max(range(len(months)), key=lambda i: months[i]["count"]) if months else -1

    bars = []
    bar_w = 34
    gap = 14
    start_x = 40
    base_y = 158
    max_h = 84

    for i, m in enumerate(months):
        h = max(4, (m["count"] / max_val) * max_h)
        x = start_x + i * (bar_w + gap)
        y = base_y - h
        is_best = i == best_idx and m["count"] > 0
        fill = BLUE if is_best else "#D6D1C7"
        delay = 0 if STATIC else round(0.9 + i * 0.04, 2)
        bar_style = (
            ""
            if STATIC
            else f"transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:barGrow 0.45s cubic-bezier(0.22,1,0.36,1) forwards {delay}s;"
        )
        bars.append(f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" rx="4" fill="{fill}" style="{bar_style}"/>')
        bars.append(f'<text x="{x + bar_w/2}" y="{base_y + 18}" text-anchor="middle" class="mono" font-size="10" fill="{INK_MUTED}">{esc(m["month"])}</text>')
        if is_best:
            pop_style = "" if STATIC else f"opacity:0;animation:fadeUp 0.3s ease forwards {delay + 0.35:.2f}s;"
            bars.append(
                f'<text x="{x + bar_w/2}" y="{y - 7:.1f}" text-anchor="middle" class="mono" font-size="10.5" font-weight="bold" fill="{BLUE}" style="{pop_style}">{m["count"]}</text>'
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 205" width="840" height="205">
  <style>{COMMON_CSS}</style>
  <rect x="0.5" y="0.5" width="839" height="204" rx="14" fill="{PAPER}" stroke="{BORDER}"/>
  <text x="40" y="36" class="serif" font-size="20" fill="{INK}">Monthly Rhythm</text>
  <line x1="40" y1="{base_y}" x2="612" y2="{base_y}" stroke="{BORDER}"/>
  {''.join(bars)}

  <line x1="640" y1="30" x2="640" y2="175" stroke="{BORDER}" stroke-dasharray="3 4"/>
  <text x="665" y="54" class="mono" font-size="10" fill="{INK_MUTED}">LONGEST STREAK</text>
  <text x="665" y="76" class="serif" font-size="24" fill="{INK}">{data['longest_streak']} days</text>

  <text x="665" y="108" class="mono" font-size="10" fill="{INK_MUTED}">ACTIVE DAYS</text>
  <text x="665" y="130" class="serif" font-size="24" fill="{INK}">{data['active_days']}</text>

  <text x="665" y="160" class="mono" font-size="10" fill="{INK_MUTED}">BUSIEST DAY</text>
  <text x="665" y="180" class="sans" font-size="14" font-weight="600" fill="{BLUE}">{esc(data['busiest_day'])} ({data['busiest_count']} commits)</text>
</svg>"""


def render_tile(label, title, subtitle, target_num, suffix, accent, delay_s):
    count_els = []
    if STATIC:
        count_els.append(f'<text x="24" y="114" class="serif" font-size="40" fill="{accent}">{target_num}{esc(suffix)}</text>')
    else:
        steps = 12
        for i in range(steps + 1):
            val = int(round((target_num / steps) * i))
            begin = round(delay_s + 0.25 + i * 0.045, 3)
            end_attr = 'dur="0.045s"' if i < steps else 'fill="freeze"'
            count_els.append(
                f'<text x="24" y="114" class="serif" font-size="40" fill="{accent}" visibility="hidden">'
                f'{val}{esc(suffix)}<set attributeName="visibility" to="visible" begin="{begin}s" {end_attr}/></text>'
            )

    card_anim = "" if STATIC else f"opacity:0;transform-box:fill-box;transform-origin:center;animation:tileSpring 0.65s cubic-bezier(0.22,1,0.36,1) forwards {delay_s}s;"
    ring_anim = "" if STATIC else f"transform-box:fill-box;transform-origin:center;animation:ringPulse 2.8s ease-out infinite {delay_s + 0.5}s;"
    arrow_anim = "" if STATIC else f"animation:arrowNudge 1.8s ease-in-out infinite {delay_s}s;"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 272 175" width="272" height="175">
  <style>{COMMON_CSS}</style>
  <g style="{card_anim}">
    <rect x="0.5" y="0.5" width="271" height="174" rx="14" fill="{PAPER}" stroke="{BORDER}"/>
    <rect x="0.5" y="0.5" width="271" height="5" rx="2.5" fill="{accent}"/>
    <circle cx="240" cy="36" r="10" fill="none" stroke="{accent}" stroke-width="1.5" style="{ring_anim}"/>
    <circle cx="240" cy="36" r="4" fill="{accent}"/>
    <text x="24" y="40" class="mono" font-size="11" font-weight="bold" fill="{accent}">{esc(label)}</text>
    {''.join(count_els)}
    <text x="24" y="140" class="sans" font-size="13.5" font-weight="600" fill="{INK}">{esc(title)}</text>
    <text x="24" y="158" class="sans" font-size="11.5" fill="{INK_MUTED}">{esc(subtitle)}</text>
    <text x="238" y="154" class="sans" font-size="16" fill="{accent}" style="{arrow_anim}">→</text>
  </g>
</svg>"""


def render_projects():
    projects = [
        ("CurriculumCraft AI", "Gemma 4 CBSE paper & lesson generator", BLUE),
        ("Luminae", "Bridal & salon marketplace · Supabase", RED),
        ("StageMap", "Interactive hackathon web app · Vercel", YELLOW),
    ]
    rows = []
    for i, (name, desc, color) in enumerate(projects):
        x = 28 + i * 268
        delay = 0 if STATIC else round(1.4 + i * 0.12, 2)
        style = "" if STATIC else f"opacity:0;animation:fadeUp 0.5s ease forwards {delay}s;"
        rows.append(f"""
        <g style="{style}">
          <rect x="{x}" y="54" width="248" height="82" rx="10" fill="{PAPER_ALT}" stroke="{BORDER}"/>
          <circle cx="{x + 18}" cy="76" r="4.5" fill="{color}"/>
          <text x="{x + 30}" y="80" class="serif" font-size="17" fill="{INK}">{esc(name)}</text>
          <text x="{x + 16}" y="106" class="sans" font-size="11.5" fill="{INK_MUTED}">{esc(desc)}</text>
          <text x="{x + 16}" y="124" class="mono" font-size="10" fill="{color}">LIVE PROJECT ↗</text>
        </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 160" width="840" height="160">
  <style>{COMMON_CSS}</style>
  <rect x="0.5" y="0.5" width="839" height="159" rx="14" fill="{PAPER}" stroke="{BORDER}"/>
  <text x="28" y="36" class="serif" font-size="20" fill="{INK}">Featured Builds</text>
  {''.join(rows)}
</svg>"""


def main():
    os.makedirs("cards", exist_ok=True)
    data = load_data()

    files = {
        "cards/hero.svg": render_hero(),
        "cards/contrib-graph.svg": render_contrib_graph(data),
        "cards/activity.svg": render_activity(data),
        "cards/tile-build.svg": render_tile("BUILD", "Web & AI Apps", "na1t1k.vercel.app", 10, "+", BLUE, 1.15),
        "cards/tile-connect.svg": render_tile("COMMITS", "This Year", "linkedin.com/in/na1t1k", data["total"], "", RED, 1.28),
        "cards/tile-cloud.svg": render_tile("STREAK", "Longest Streak", "x.com/NA1T1Kxd", data["longest_streak"], "d", YELLOW, 1.40),
        "cards/projects.svg": render_projects(),
    }

    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Rendered {path}")


if __name__ == "__main__":
    main()
