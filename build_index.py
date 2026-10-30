#!/usr/bin/env python3
"""Build index.html: interactive AI YouTube Scout & Video Insights Dashboard.

Reads Markdown briefs from ./briefs/ (or the current directory if ./briefs/ does not exist)
and writes an interactive two-pane dashboard to index.html.
Standard library only. Run: python3 build_index.py
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIEFS_DIR = HERE / "briefs" if (HERE / "briefs").is_dir() else HERE
OUT = HERE / "index.html"


def inline(text: str) -> str:
    """Escape text, then apply inline Markdown: code, bold, italic, links, bare URLs."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        s = html.escape(part, quote=False)
        s = s.replace(r"\$", "$")
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
        s = re.sub(r'(?<!href=")(?<!">)(https?://[^\s<)]+)', r'<a href="\1" target="_blank" rel="noopener">\1</a>', s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"<em>\1</em>", s)
        out.append(s)
    return "".join(out)


def md_to_html(md: str) -> str:
    """Convert the Markdown subset the briefs use: headings, lists, tables, fences, paragraphs."""
    lines = md.splitlines()
    out, para, i = [], [], 0

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush()
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(code))}</code></pre>")
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            flush()
            level = min(len(m.group(1)) + 1, 5)
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush()
            cells = lambda row: [c.strip() for c in row.strip().strip("|").split("|")]
            head = cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            t = ['<div class="tbl"><table><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        lm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", line)
        if lm:
            flush()
            ordered = lm.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                lm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)", lines[i])
                if lm:
                    items.append(lm.group(3))
                elif lines[i].startswith("  ") and lines[i].strip() and items:
                    items[-1] += " " + lines[i].strip()
                else:
                    break
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        if not line.strip():
            flush()
        else:
            para.append(line.strip())
        i += 1
    flush()
    return "\n".join(out)


def extract_yt_id(url: str) -> str:
    if not url:
        return ""
    m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else ""


def extract_bottom_line(md: str) -> str:
    m = re.search(r"^#{2,3}\s*(?:1\.\s*)?Bottom line.*?\n+(.+?)(?:\n\n|\n#{2,3})", md, re.M | re.S | re.I)
    if m:
        raw = re.sub(r"\*\*([^*]+)\*\*", r"\1", m.group(1).strip())
        raw = re.sub(r"`([^`]+)`", r"\1", raw)
        raw = raw.replace(r"\$", "$")
        raw = re.sub(r"\s+", " ", raw)
        return raw
    return ""


def extract_action_items(md: str) -> list[str]:
    m = re.search(
        r"^#{2,3}\s*(?:4\.\s*)?(?:Suggested next steps|Recommended changes|Recommended integrations).*?\n+(.+?)(?:\n#{2,3}\s|\Z)",
        md,
        re.M | re.S | re.I,
    )
    if not m:
        return []
    block = m.group(1)
    items = []
    for line in block.splitlines():
        lm = re.match(r"^\s*(?:\d+\.|[-*])\s+(.+)", line)
        if lm:
            clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", lm.group(1).strip())
            clean = re.sub(r"`([^`]+)`", r"\1", clean)
            items.append(clean)
    return items[:4]


def detect_pillars(md: str, title: str) -> list[str]:
    blob = (title + " " + md[:1500]).lower()
    pillars = []
    if any(k in blob for k in ("claude", "skill", "harness", "subagent", "agent")):
        pillars.append("Claude & Harnesses")
    if any(k in blob for k in ("client", "agency", "sell", "lead", "outreach", "business")):
        pillars.append("Agency & Revenue")
    if any(k in blob for k in ("video", "motion", "reels", "remotion", "preset", "instagram")):
        pillars.append("Video & Content")
    if any(k in blob for k in ("kimi", "opus", "security", "benchmark")):
        pillars.append("Frontier Models")
    return pillars[:3] or ["AI Systems"]


def meta(md: str, path: Path) -> dict:
    title_m = re.search(r'^#\s+(?:Video Insights:\s*)?"?(.*?)"?\s*$', md, re.M)
    title = title_m.group(1) if title_m else path.stem
    src = re.search(r"^- Source:\s*(https?://\S+)\s*(?:\(([^)]*)\))?", md, re.M)
    url = src.group(1) if src else ""
    channel = src.group(2) if src and src.group(2) else "Creator Brief"
    yt_id = extract_yt_id(url)

    liked = re.search(r"liked (\d{4}-\d{2}-\d{2})", md)
    scouted = re.search(r"scouted (\d{4}-\d{2}-\d{2})", md)
    analyzed = re.search(r"^- Date(?: analyzed)?:\s*(\d{4}-\d{2}-\d{2})", md, re.M)
    score_m = re.search(r"score\s+(\d+)", md)
    score = int(score_m.group(1)) if score_m else (10 if scouted else None)

    chars_m = re.search(r"([\d,]+)\s+characters(?:\s+with\s+timestamps)?\s*\((?:about\s+)?([^)]+)\)", md)
    chars = chars_m.group(1) if chars_m else ""
    duration_label = chars_m.group(2) if chars_m else ""

    if scouted:
        date = scouted.group(1)
        sort_key = (date, "23:59")
        origin_kind = "scouted"
        origin_label = f"AI Scouted · {date}"
    elif liked:
        date = liked.group(1)
        sort_key = (date, "12:00")
        origin_kind = "liked"
        origin_label = f"Liked · {date}"
    else:
        date = analyzed.group(1) if analyzed else path.name[:10]
        sort_key = (date, "08:00")
        origin_kind = "analyzed"
        origin_label = f"Analyzed · {date}"

    rel_file = f"briefs/{path.name}" if BRIEFS_DIR != HERE else path.name
    return {
        "id": path.stem,
        "file": rel_file,
        "title": title,
        "url": url,
        "yt_id": yt_id,
        "channel": channel,
        "date": date,
        "origin_kind": origin_kind,
        "origin_label": origin_label,
        "score": score,
        "chars": chars,
        "duration_label": duration_label,
        "in_playlist": True,
        "bottom_line": extract_bottom_line(md),
        "action_items": extract_action_items(md),
        "pillars": detect_pillars(md, title),
        "sort": sort_key,
    }


def main():
    briefs = []
    for p in sorted(BRIEFS_DIR.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*.md")):
        md = p.read_text(encoding="utf-8")
        m = meta(md, p)
        body = re.sub(r"^#\s+.*\n", "", md, count=1)
        m["body_html"] = md_to_html(body)
        briefs.append(m)
    briefs.sort(key=lambda b: b["sort"], reverse=True)
    briefs_json = json.dumps(briefs, ensure_ascii=False)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI YouTube Scout &amp; Video Insights Dashboard</title>
<style>
:root {{
  --bg: #f6f8f4;
  --surface: #ffffff;
  --surface-alt: #eef2eb;
  --ink: #10291f;
  --muted: #55665d;
  --line: #dce2d8;
  --accent: #b84a27;
  --accent-soft: #fdf1ed;
  --green: #146c43;
  --green-soft: #e7f4ed;
  --blue: #1d4ed8;
  --blue-soft: #eff6ff;
  --shadow: 0 10px 30px rgba(16, 41, 31, 0.06);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
}}
.topbar {{
  background: var(--ink);
  color: #fff;
  padding: 14px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}}
.brand {{ display: flex; align-items: center; gap: 14px; }}
.brand-badge {{
  background: var(--accent);
  color: #fff;
  font-weight: 800;
  font-size: 12px;
  letter-spacing: 0.06em;
  padding: 5px 10px;
  border-radius: 6px;
  text-transform: uppercase;
}}
.brand h1 {{ font-size: 19px; font-weight: 800; margin: 0; }}
.brand p {{ margin: 2px 0 0; font-size: 12.5px; color: rgba(255,255,255,0.72); }}
.stats-strip {{ display: flex; gap: 10px; }}
.stat-pill {{
  background: rgba(255,255,255,0.09);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 9px;
  padding: 6px 12px;
  display: flex;
  flex-direction: column;
}}
.stat-pill .v {{ font-size: 16px; font-weight: 800; color: #fff; }}
.stat-pill .l {{ font-size: 10.5px; color: rgba(255,255,255,0.7); text-transform: uppercase; }}
.toolbar {{
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  padding: 10px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}}
.filters {{ display: flex; gap: 6px; }}
.filter-btn {{
  background: var(--surface-alt);
  color: var(--ink);
  border: 1px solid var(--line);
  border-radius: 99px;
  padding: 5px 12px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}}
.filter-btn.active, .filter-btn:hover {{ background: var(--ink); color: #fff; border-color: var(--ink); }}
.toolbar-right {{ display: flex; align-items: center; gap: 8px; }}
.search-input {{
  padding: 6px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 12.5px;
  width: 220px;
  background: var(--bg);
}}
.workspace {{
  display: grid;
  grid-template-columns: 450px 1fr;
  height: calc(100vh - 115px);
  overflow: hidden;
}}
.feed-col {{
  border-right: 1px solid var(--line);
  overflow-y: auto;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}}
.video-card {{
  background: var(--surface);
  border: 1.5px solid var(--line);
  border-radius: 14px;
  padding: 16px;
  cursor: pointer;
}}
.video-card.selected {{
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(184, 74, 39, 0.14);
}}
.card-top {{ display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px; }}
.badge {{
  font-size: 11px;
  font-weight: 800;
  padding: 3px 7px;
  border-radius: 6px;
  text-transform: uppercase;
  white-space: nowrap;
}}
.badge.scouted {{ background: var(--accent-soft); color: var(--accent); border: 1px solid #f2c7b8; }}
.badge.liked {{ background: var(--blue-soft); color: var(--blue); border: 1px solid #bfdbfe; }}
.badge.playlist {{ background: var(--green-soft); color: var(--green); border: 1px solid #b8dfc8; }}
.card-title {{ font-size: 16px; font-weight: 800; line-height: 1.3; margin: 0 0 6px; }}
.card-meta {{ font-size: 12.5px; color: var(--muted); margin-bottom: 10px; }}
.card-summary {{ font-size: 13.5px; color: #2c3e35; line-height: 1.45; margin: 0 0 10px; }}
.pillar-row {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.pillar-tag {{ font-size: 11px; font-weight: 600; background: var(--surface-alt); padding: 2px 8px; border-radius: 5px; }}
.detail-col {{ overflow-y: auto; padding: 28px 40px 80px; background: var(--surface); }}
.detail-header {{ border-bottom: 1px solid var(--line); padding-bottom: 20px; margin-bottom: 24px; }}
.detail-kicker {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
.detail-title {{ font-size: 28px; font-weight: 800; line-height: 1.2; margin: 0 0 12px; }}
.action-bar {{ display: flex; gap: 10px; margin-top: 14px; }}
.btn {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 9px;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid var(--line);
  background: var(--surface-alt);
  color: var(--ink);
  text-decoration: none;
}}
.btn.primary {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
.btn.green {{ background: var(--green); color: #fff; border-color: var(--green); }}
.player-box {{
  margin: 0 0 24px;
  border-radius: 14px;
  overflow: hidden;
  background: #000;
  aspect-ratio: 16 / 9;
  max-width: 820px;
  display: none;
}}
.player-box.open {{ display: block; }}
.player-box iframe {{ width: 100%; height: 100%; border: 0; }}
.takeaway-Banner {{
  background: var(--green-soft);
  border-left: 5px solid var(--green);
  padding: 18px 22px;
  border-radius: 10px;
  margin-bottom: 22px;
}}
.takeaway-Banner h3 {{ margin: 0 0 6px; font-size: 13px; text-transform: uppercase; color: var(--green); }}
.takeaway-Banner p {{ margin: 0; font-size: 15.5px; font-weight: 600; }}
.ideas-box {{
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 18px 22px;
  margin-bottom: 26px;
}}
.ideas-box h3 {{ margin: 0 0 12px; font-size: 14px; text-transform: uppercase; color: var(--accent); }}
.idea-item {{ display: flex; align-items: flex-start; gap: 10px; padding: 7px 0; font-size: 14.5px; font-weight: 600; }}
.brief-body table {{ border-collapse: collapse; width: 100%; font-size: 14px; margin: 14px 0; }}
.brief-body th, .brief-body td {{ border: 1px solid var(--line); padding: 8px 10px; text-align: left; }}
.brief-body th {{ background: var(--bg); }}
</style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span class="brand-badge">AI YouTube Scout</span>
      <div>
        <h1>Video Insights &amp; Idea Triage Dashboard</h1>
        <p>Grounded in your Taste Profile · Creator RSS Scout · 1-Page Action Briefs</p>
      </div>
    </div>
    <div class="stats-strip">
      <div class="stat-pill"><span class="v">508</span><span class="l">Taste Profile Saves</span></div>
      <div class="stat-pill"><span class="v">16</span><span class="l">Core Creators</span></div>
      <div class="stat-pill"><span class="v">{len(briefs)}</span><span class="l">1-Page Briefs Ready</span></div>
      <div class="stat-pill"><span class="v">Top 3</span><span class="l">Queued to Playlist</span></div>
    </div>
  </header>

  <div class="toolbar">
    <div class="filters">
      <button class="filter-btn active" data-filter="all">All Briefs ({len(briefs)})</button>
      <button class="filter-btn" data-filter="scouted">AI Scouted</button>
      <button class="filter-btn" data-filter="liked">Liked</button>
      <button class="filter-btn" data-filter="Claude & Harnesses">Claude &amp; Harnesses</button>
      <button class="filter-btn" data-filter="Video & Content">Video &amp; Content</button>
    </div>
    <div class="toolbar-right">
      <input type="search" id="search" class="search-input" placeholder="Search briefs, creators, numbers...">
      <a class="btn" href="taste-profile.example.md" target="_blank">Taste Profile</a>
    </div>
  </div>

  <div class="workspace">
    <aside class="feed-col" id="feed"></aside>
    <main class="detail-col" id="detail"></main>
  </div>

<script>
const BRIEFS = {briefs_json};
let activeFilter = 'all';
let searchQuery = '';
let selectedId = BRIEFS[0].id;

function renderFeed() {{
  const feed = document.getElementById('feed');
  const q = searchQuery.toLowerCase();
  const filtered = BRIEFS.filter(b => {{
    if (activeFilter === 'scouted' && b.origin_kind !== 'scouted') return false;
    if (activeFilter === 'liked' && b.origin_kind !== 'liked') return false;
    if (!['all','scouted','liked'].includes(activeFilter) && !b.pillars.includes(activeFilter)) return false;
    if (q && !(b.title.toLowerCase().includes(q) || b.channel.toLowerCase().includes(q) || b.bottom_line.toLowerCase().includes(q))) return false;
    return true;
  }});

  feed.innerHTML = filtered.map(b => `
    <div class="video-card ${{b.id === selectedId ? 'selected' : ''}}" onclick="selectBrief('${{b.id}}')">
      <div class="card-top">
        <span class="badge ${{b.origin_kind}}">${{b.origin_label}}</span>
        ${{b.score ? `<span class="badge scouted">Score ${{b.score}}/10</span>` : ''}}
      </div>
      <h3 class="card-title">${{b.title}}</h3>
      <div class="card-meta"><strong>${{b.channel}}</strong> ${{b.duration_label ? '· ' + b.duration_label : ''}}</div>
      <p class="card-summary">${{b.bottom_line}}</p>
      <div class="pillar-row">${{b.pillars.map(p => `<span class="pillar-tag">${{p}}</span>`).join('')}}</div>
    </div>
  `).join('');
}}

function selectBrief(id) {{
  selectedId = id;
  renderFeed();
  const b = BRIEFS.find(x => x.id === id) || BRIEFS[0];
  document.getElementById('detail').innerHTML = `
    <div class="detail-header">
      <div class="detail-kicker">
        <span class="badge ${{b.origin_kind}}">${{b.origin_label}}</span>
        ${{b.score ? `<span class="badge scouted">Taste Match Score: ${{b.score}}/10</span>` : ''}}
        <span style="color:var(--muted);font-size:13px">${{b.channel}} ${{b.duration_label ? '· ' + b.duration_label : ''}}</span>
      </div>
      <h2 class="detail-title">${{b.title}}</h2>
      <div class="action-bar">
        ${{b.yt_id ? `<button class="btn primary" onclick="toggleVideo('${{b.yt_id}}')">▶ Watch Video Here</button>` : ''}}
        ${{b.url ? `<a class="btn" href="${{b.url}}" target="_blank" rel="noopener">↗ Open on YouTube</a>` : ''}}
        <a class="btn" href="${{b.file}}" target="_blank">📄 Raw Markdown</a>
      </div>
    </div>
    <div class="player-box" id="player-box"><iframe id="yt-iframe" src="" allowfullscreen></iframe></div>
    <div class="takeaway-Banner"><h3>90-Second Bottom Line</h3><p>${{b.bottom_line}}</p></div>
    <div class="ideas-box">
      <h3>Actionable Ideas Extracted for Your 60-Day Goals</h3>
      ${{b.action_items.map(item => `<label class="idea-item"><input type="checkbox" checked><span>${{item}}</span></label>`).join('')}}
    </div>
    <div class="brief-body">${{b.body_html}}</div>
  `;
}}

function toggleVideo(ytId) {{
  const box = document.getElementById('player-box');
  const iframe = document.getElementById('yt-iframe');
  if (box.classList.contains('open')) {{ box.classList.remove('open'); iframe.src = ''; }}
  else {{ box.classList.add('open'); iframe.src = 'https://www.youtube.com/embed/' + ytId + '?autoplay=1'; }}
}}

document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    renderFeed();
  }});
}});
document.getElementById('search').addEventListener('input', e => {{ searchQuery = e.target.value; renderFeed(); }});
renderFeed();
selectBrief(selectedId);
</script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} with {len(briefs)} briefs")


if __name__ == "__main__":
    main()
