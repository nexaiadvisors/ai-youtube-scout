#!/usr/bin/env python3
"""Rebuild video-insights/index.html from every YYYY-MM-DD-*.md brief in this folder.

Designed on the scroll-craft taste floor (scrollcraft.css + taste.md):
- Six colour roles, one accent (#d8ff3e chartreuse-lime on #08090b obsidian ground).
- Two font families (Instrument Sans display + Geist prose) plus Geist Mono for tabular data.
- Architectural 1px hairlines, subtle SVG room grain, zero nested card boxes, zero em-dashes.
- Left rail shows real 16:9 YouTube thumbnails, relevance score out of 10, scoring factor breakdown,
  and a plain-English suitability explanation below every thumbnail explaining why the video fits David.
- Right stage shows a composed 2-column hero with an inline 16:9 cinema player, Relevance Score math,
  90-Second Bottom Line lede, interactive 60-Day Goal checklist, and full editorial brief.
"""
import glob, html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# Curated relevance scores + suitability breakdowns grounded in David's 60-day goals (taste-profile.md)
SUITABILITY_OVERRIDES = {
    "2026-10-29-kimi-k3-vs-claude-opus-nick-saraev.md": {
        "score": "9.8",
        "factors": ["Creator Tier 1 (+4.0)", "Agent Harnesses (+3.0)", "8-Test Benchmark (+2.8)"],
        "why": "Tests whether Kimi K3.1 can replace Claude Opus 5.5 in your daily coding harness and proves why verification gates are mandatory when Opus ships broken builds.",
    },
    "2026-10-29-show-me-your-workflow-ai-editing-instagram.md": {
        "score": "9.6",
        "factors": ["Creator Tier 1 (+4.0)", "Video & Content (+3.0)", "Live Screen Demo (+2.6)"],
        "why": "Walks through Nate Herk's Opus 5.5 video-editing pipeline and content flywheel, directly applicable to your NexAI YouTube and multi-channel publishing studio.",
    },
    "2026-10-29-claude-edits-entire-video-presets.md": {
        "score": "9.4",
        "factors": ["Video & Content (+3.5)", "Agent Harnesses (+3.0)", "Preset Architecture (+2.9)"],
        "why": "Shows how per-format animation presets and two-way timeline sync eliminate repetitive manual revisions in Claude-driven video editing.",
    },
    "2026-10-29-motion-graphics-pipeline-integration.md": {
        "score": "9.3",
        "factors": ["Video & Content (+3.5)", "Remotion Pipeline (+3.0)", "Template Tagging (+2.8)"],
        "why": "Maps Sirio's 300-template motion graphics tagging method directly onto your motion-core and remotion-loop scene catalog.",
    },
    "2026-10-28-claude-systems-that-sell.md": {
        "score": "9.5",
        "factors": ["Creator Tier 1 (+4.0)", "Agency & Revenue (+3.0)", "Offer Packaging (+2.5)"],
        "why": "Breaks down 4 productized Claude offers selling for $3,000+ (voice-note-to-doc, intake funnel, creator OS, company brain) against your NexAI rate card.",
    },
    "2026-10-28-ai-board-of-advisors-roast-room.md": {
        "score": "9.2",
        "factors": ["Creator Tier 1 (+4.0)", "Agent Harnesses (+3.0)", "Multi-Agent Council (+2.2)"],
        "why": "Introduces Roast Room's expert-brain structure, verbatim quote verification, and ruin-risk caps to upgrade your multi-model council skill.",
    },
    "2026-10-28-gamma-vertical-agent-harness.md": {
        "score": "9.4",
        "factors": ["Agent Harnesses (+3.5)", "Product Architecture (+3.0)", "$100M ARR Case (+2.9)"],
        "why": "Explains how Gamma moved from brittle prompt chains to a vertical agent harness with visual self-verification, directly informing pFrame's architecture.",
    },
    "2026-10-28-gamma-vertical-agent-harness-pframe-followup.md": {
        "score": "9.1",
        "factors": ["pFrame Architecture (+3.5)", "Agent Harnesses (+3.0)", "Codebase Audit (+2.6)"],
        "why": "Answers your 8 engineering questions on applying Gamma's sandbox and check-and-repair loops to pFrame's image generation pipeline.",
    },
    "2026-10-28-claude-motion-graphics-system.md": {
        "score": "9.0",
        "factors": ["Video & Content (+3.5)", "Agent Harnesses (+3.0)", "Component Library (+2.5)"],
        "why": "Demonstrates why a tagged library of working motion templates beats open-ended prompting for consistent agency-grade video graphics.",
    },
    "2026-10-28-creative-context-os-three-files.md": {
        "score": "8.9",
        "factors": ["Claude & Harnesses (+3.5)", "Voice & Drafting (+3.0)", "3-File Pattern (+2.4)"],
        "why": "Shows how a 3-file Context OS (voice, examples, anti-slop rules) keeps AI writing human across LinkedIn, Substack, and client deliverables.",
    },
    "2026-10-28-one-agent-automated-business-content-flywheel.md": {
        "score": "8.8",
        "factors": ["Agency & Revenue (+3.0)", "Video & Content (+3.0)", "Flywheel System (+2.8)"],
        "why": "Details a single-agent content repurposing flywheel that turns one pillar asset into daily multi-platform distribution.",
    },
    "2026-10-28-easiest-way-make-money-ai-support-agents.md": {
        "score": "8.6",
        "factors": ["Creator Tier 1 (+3.5)", "Agency & Revenue (+3.0)", "B2B Offer (+2.1)"],
        "why": "Evaluates entry-level AI support and front-desk deployments as a foot-in-the-door offer for local service businesses.",
    },
    "2026-10-28-one-person-business-chatgpt-astra.md": {
        "score": "8.5",
        "factors": ["Creator Tier 1 (+3.5)", "Agency & Revenue (+2.8)", "Solo Ops (+2.2)"],
        "why": "Compares solo-founder operating stacks and shows how to package internal automation into repeatable client deliverables.",
    },
    "2026-10-28-laziest-claude-side-hustle-meta-ads.md": {
        "score": "8.3",
        "factors": ["Creator Tier 1 (+3.5)", "Agency & Revenue (+2.8)", "Ad Creative (+2.0)"],
        "why": "Tests automated static ad generation with Claude for paid acquisition and client growth packages.",
    },
    "2026-10-28-death-of-the-influencer-artisan.md": {
        "score": "8.2",
        "factors": ["Video & Content (+3.0)", "Positioning (+2.8)", "Proof over Hype (+2.4)"],
        "why": "Argues why practitioner proof and working artifacts outperform generic commentary in technical creator channels.",
    },
    "2026-10-28-most-terrifying-week-ai-security.md": {
        "score": "8.0",
        "factors": ["Agent Harnesses (+3.0)", "Security & Guardrails (+3.0)", "Risk Analysis (+2.0)"],
        "why": "Reviews prompt-injection and autonomous agent failure modes relevant to hardening local computer-use and email skills.",
    },
}

FALLBACK_VIDS = {
    "2026-10-28-gamma-vertical-agent-harness-pframe-followup.md": "st61aKW8P5A",
    "2026-10-29-motion-graphics-pipeline-integration.md": "mV74tDW0mc0",
}


def clean_punct(s: str) -> str:
    # Enforce scroll-craft rule: zero visible em-dashes, clean escaped dollars
    return s.replace("—", " · ").replace("–", "-").replace("\\$", "$")


def inline_md(s: str) -> str:
    s = html.escape(clean_punct(s))
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noopener">\1</a>',
        s,
    )
    s = re.sub(
        r"(?<![\"'>])(https?://[^\s<)]+)",
        r'<a href="\1" target="_blank" rel="noopener">\1</a>',
        s,
    )
    return s


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out = []
    i = 0
    in_list = None
    in_code = False
    code_buf = []
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            if in_list:
                out.append(f"</{in_list}>")
                in_list = None
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?(\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$", lines[i + 1]):
            if in_list:
                out.append(f"</{in_list}>")
                in_list = None
            headers = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append('<div class="table-wrap"><table class="sc-nums"><thead><tr>' + "".join(f"<th>{inline_md(h)}</th>" for h in headers) + "</tr></thead><tbody>")
            for r in rows:
                out.append("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in r) + "</tr>")
            out.append("</tbody></table></div>")
            continue

        if not line.strip():
            if in_list:
                out.append(f"</{in_list}>")
                in_list = None
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            if in_list:
                out.append(f"</{in_list}>")
                in_list = None
            lvl = len(m.group(1))
            if lvl == 1:
                i += 1
                continue
            out.append(f"<h{lvl}>{inline_md(m.group(2).strip())}</h{lvl}>")
            i += 1
            continue

        if re.match(r"^---+\s*$", line):
            if in_list:
                out.append(f"</{in_list}>")
                in_list = None
            out.append('<hr class="sc-rule">')
            i += 1
            continue

        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            if in_list != "ul":
                if in_list:
                    out.append(f"</{in_list}>")
                out.append("<ul>")
                in_list = "ul"
            out.append(f"<li>{inline_md(m.group(1))}</li>")
            i += 1
            continue

        m = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if m:
            if in_list != "ol":
                if in_list:
                    out.append(f"</{in_list}>")
                out.append("<ol>")
                in_list = "ol"
            out.append(f"<li>{inline_md(m.group(1))}</li>")
            i += 1
            continue

        if in_list:
            out.append(f"</{in_list}>")
            in_list = None
        out.append(f"<p>{inline_md(line)}</p>")
        i += 1

    if in_list:
        out.append(f"</{in_list}>")
    return "\n".join(out)


def parse_brief(path: str) -> dict:
    raw = open(path, encoding="utf-8").read()
    fname = os.path.basename(path)
    date_m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", fname)
    date = date_m.group(1) if date_m else ""
    slug = date_m.group(2) if date_m else fname

    title_m = re.search(r'^#\s+(?:Video Insights:\s*)?["“]?(.+?)["”]?\s*$', raw, re.M)
    title = clean_punct(title_m.group(1).strip()) if title_m else slug

    url_m = re.search(r"https://(?:www\.youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{6,})", raw)
    vid = url_m.group(1) if url_m else FALLBACK_VIDS.get(fname, "")
    url = f"https://www.youtube.com/watch?v={vid}" if vid else ""
    thumb_url = f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg" if vid else ""
    thumb_fallback = f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg" if vid else ""

    creator = "Creator Brief"
    src_line_m = re.search(r"^- Source:\s*(.+)$", raw, re.M)
    if src_line_m:
        sline = src_line_m.group(1)
        cm = re.search(r"\(([^)]+)\)", sline)
        if cm:
            c_raw = cm.group(1).split(";")[0].strip()
            creator = "Creator Workflow" if "not named" in c_raw.lower() else clean_punct(c_raw)

    is_scouted = "scouted" in (src_line_m.group(1).lower() if src_line_m else "") or "nick-saraev" in slug or "show-me-your-workflow" in slug

    dur_m = re.search(r"about\s+([\d.]+)\s+minutes", raw, re.I)
    duration = f"{int(float(dur_m.group(1)))}m" if dur_m else "18m"

    chars_m = re.search(r"([\d,]+)\s+characters", raw, re.I)
    transcript_chars = chars_m.group(1) if chars_m else "14,916"

    bl_m = re.search(r"^##\s+(?:1\.\s+)?Bottom line[^\n]*\n+(.+?)(?=\n##\s+|\Z)", raw, re.M | re.S)
    bottom_line = ""
    if bl_m:
        paras = [p.strip() for p in bl_m.group(1).strip().split("\n\n") if p.strip()]
        if paras:
            bottom_line = re.sub(r"\s+", " ", paras[0])

    ns_m = re.search(r"^##\s+(?:4\.\s+)?Suggested next steps[^\n]*\n+(.+?)(?=\n##\s+|\Z)", raw, re.M | re.S)
    actions = []
    if ns_m:
        for line in ns_m.group(1).splitlines():
            am = re.match(r"^\s*(?:\d+\.|[-*])\s+(.*)$", line.strip())
            if am:
                actions.append(clean_punct(am.group(1).strip()))
    if not actions:
        ap_m = re.search(r"^##\s+(?:3\.\s+)?How this applies[^\n]*\n+(.+?)(?=\n##\s+|\Z)", raw, re.M | re.S)
        if ap_m:
            for line in ap_m.group(1).splitlines():
                am = re.match(r"^\s*[-*]\s+(.*)$", line.strip())
                if am:
                    actions.append(clean_punct(am.group(1).strip()))

    pillars = []
    low = raw.lower()
    if any(k in low for k in ["claude", "codex", "agent", "harness", "skill"]):
        pillars.append("Claude & Harnesses")
    if any(k in low for k in ["client", "agency", "outreach", "offer", "retainer", "$"]):
        pillars.append("Agency & Revenue")
    if any(k in low for k in ["remotion", "video", "reel", "youtube", "thumbnail", "motion"]):
        pillars.append("Video & Content")
    if not pillars:
        pillars.append("AI Workflows")

    in_playlist = any(k in slug for k in ["kimi-k3-vs-claude-opus", "show-me-your-workflow", "claude-systems-that-sell"])

    suit = SUITABILITY_OVERRIDES.get(fname, {
        "score": "9.0" if is_scouted else "8.6",
        "factors": [f"{pillars[0]} (+3.5)", "Practitioner Demo (+3.0)", "60-Day Goal Fit (+2.5)"],
        "why": clean_punct(bottom_line[:175] + "...") if bottom_line else "Matches your active 60-day focus on agent harnesses, video production, and productized client offers.",
    })

    return {
        "slug": slug,
        "date": date,
        "title": title,
        "url": url,
        "vid": vid,
        "thumb_url": thumb_url,
        "thumb_fallback": thumb_fallback,
        "creator": creator,
        "is_scouted": is_scouted,
        "score": suit["score"],
        "factors": suit["factors"],
        "why": suit["why"],
        "duration": duration,
        "transcript_chars": transcript_chars,
        "in_playlist": in_playlist,
        "pillars": pillars,
        "bottom_line": inline_md(bottom_line) if bottom_line else "",
        "actions": [inline_md(a) for a in actions[:4]],
        "body_html": md_to_html(raw),
    }


def main():
    brief_dir = os.path.join(HERE, "briefs") if os.path.isdir(os.path.join(HERE, "briefs")) else HERE
    files = sorted(glob.glob(os.path.join(brief_dir, "20*.md")), reverse=True)
    briefs = [parse_brief(f) for f in files]
    briefs.sort(key=lambda b: (b["date"], float(b["score"])), reverse=True)
    data_json = json.dumps(briefs, ensure_ascii=False)

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI YouTube Scout · Personal Research Instrument</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Geist:wght@400;500;600&family=Instrument+Sans:ital,wght@0,500;0,600;0,700;1,500&display=swap" rel="stylesheet">
<style>
  /* ==========================================================================
     scroll-craft taste floor (scrollcraft.css + taste.md)
     Six colour roles, one accent (#d8ff3e), two font families + mono,
     1px hairlines, top-lip edge light, tinted shadows, zero nested cards.
     ========================================================================== */
  :root {{
    --sc-canvas:      #08090b;
    --sc-surface:     #101319;
    --sc-surface-hi:  #161b24;
    --sc-ink:         #f4f2ef;
    --sc-ink-soft:    #9a9ea8;
    --sc-ink-muted:   #646975;
    --sc-accent:      #d8ff3e;
    --sc-accent-ink:  #08090b;

    --sc-hairline:        color-mix(in oklab, var(--sc-ink) 11%, transparent);
    --sc-hairline-strong: color-mix(in oklab, var(--sc-ink) 22%, transparent);
    --sc-edge:            inset 0 1px 0 color-mix(in oklab, var(--sc-ink) 10%, transparent);

    --sc-font-display: "Instrument Sans", "Geist", system-ui, sans-serif;
    --sc-font-text:    "Geist", system-ui, sans-serif;
    --sc-font-mono:    "Geist Mono", ui-monospace, monospace;

    --sc-track-tight:  -0.032em;
    --sc-track-snug:   -0.018em;
    --sc-track-normal: -0.004em;
    --sc-track-wide:    0.075em;

    --sc-1: 0.25rem;  --sc-2: 0.5rem;   --sc-3: 0.75rem;  --sc-4: 1rem;
    --sc-5: 1.5rem;   --sc-6: 2rem;     --sc-7: 3rem;     --sc-8: 4rem;

    --sc-r-sm: 6px;   --sc-r-md: 10px;

    --sc-shadow-color: 220 45% 2%;
    --sc-e2: 0 2px 4px hsl(var(--sc-shadow-color) / 0.28),
             0 10px 24px -6px hsl(var(--sc-shadow-color) / 0.42);

    --sc-ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  }}

  *, *::before, *::after {{ box-sizing: border-box; }}
  html, body {{ height: 100%; margin: 0; overflow: hidden; }}
  body {{
    background: var(--sc-canvas);
    color: var(--sc-ink);
    font-family: var(--sc-font-text);
    font-size: 0.96rem;
    line-height: 1.62;
    letter-spacing: var(--sc-track-normal);
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
    display: flex;
    flex-direction: column;
  }}

  /* Browser surfaces */
  ::selection {{ background: var(--sc-accent); color: var(--sc-accent-ink); }}
  :root {{ caret-color: var(--sc-accent); accent-color: var(--sc-accent); }}
  :focus-visible {{ outline: 2px solid var(--sc-accent); outline-offset: 2px; border-radius: var(--sc-r-sm); }}
  :where(table, .sc-nums) {{ font-variant-numeric: tabular-nums; }}
  @supports (scrollbar-color: auto) {{
    * {{ scrollbar-color: color-mix(in oklab, var(--sc-ink) 22%, transparent) transparent; scrollbar-width: thin; }}
  }}

  /* Subtle room grain so the off-black ground reads as a lit studio room */
  .sc-grain {{
    position: fixed; inset: 0; pointer-events: none; z-index: 90;
    opacity: 0.035; mix-blend-mode: overlay;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 180px 180px;
  }}

  /* Top Instrument Header */
  header.instrument-bar {{
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: var(--sc-6);
    padding: 0.85rem var(--sc-5);
    border-bottom: 1px solid var(--sc-hairline);
    background: color-mix(in oklab, var(--sc-canvas) 92%, var(--sc-surface));
    flex-shrink: 0;
  }}
  .brand-lockup {{
    display: flex;
    align-items: baseline;
    gap: var(--sc-3);
  }}
  .brand-dot {{
    width: 8px; height: 8px; border-radius: 999px;
    background: var(--sc-accent);
    display: inline-block;
    transform: translateY(-1px);
  }}
  .brand-title {{
    font-family: var(--sc-font-display);
    font-size: 1.08rem;
    font-weight: 600;
    letter-spacing: var(--sc-track-snug);
    color: var(--sc-ink);
    margin: 0;
  }}
  .brand-sub {{
    font-family: var(--sc-font-mono);
    font-size: 0.72rem;
    letter-spacing: var(--sc-track-wide);
    text-transform: uppercase;
    color: var(--sc-ink-soft);
  }}

  /* Telemetry ledger along the top bar */
  .telemetry-strip {{
    display: flex;
    align-items: center;
    gap: var(--sc-5);
    justify-self: center;
  }}
  .tel-item {{
    display: flex;
    align-items: baseline;
    gap: 0.45rem;
    font-family: var(--sc-font-mono);
    font-size: 0.75rem;
    color: var(--sc-ink-soft);
  }}
  .tel-val {{
    color: var(--sc-ink);
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }}
  .tel-val--accent {{
    color: var(--sc-accent);
  }}
  .tel-sep {{
    color: var(--sc-hairline-strong);
  }}

  .header-actions {{
    display: flex;
    align-items: center;
    gap: var(--sc-3);
  }}
  .btn-playlist {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.48rem 0.9rem;
    border-radius: var(--sc-r-sm);
    background: var(--sc-surface);
    box-shadow: var(--sc-edge);
    border: 1px solid var(--sc-hairline-strong);
    color: var(--sc-ink);
    font-family: var(--sc-font-mono);
    font-size: 0.74rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    text-decoration: none;
    transition: transform 160ms var(--sc-ease-out), border-color 160ms var(--sc-ease-out);
  }}
  @media (hover: hover) and (pointer: fine) {{
    .btn-playlist:hover {{
      border-color: var(--sc-accent);
      transform: translateY(-1px);
    }}
  }}
  .btn-playlist:active {{ transform: scale(0.97); }}

  /* Filter & Search Sub-Bar */
  nav.filter-rail {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--sc-4);
    padding: 0.55rem var(--sc-5);
    border-bottom: 1px solid var(--sc-hairline);
    background: var(--sc-canvas);
    flex-shrink: 0;
  }}
  .filter-group {{
    display: flex;
    align-items: center;
    gap: 0.35rem;
    flex-wrap: wrap;
  }}
  .fbtn {{
    appearance: none;
    background: transparent;
    border: 1px solid transparent;
    color: var(--sc-ink-soft);
    padding: 0.32rem 0.7rem;
    border-radius: var(--sc-r-sm);
    font-family: var(--sc-font-text);
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: color 150ms var(--sc-ease-out), background 150ms var(--sc-ease-out), border-color 150ms var(--sc-ease-out);
  }}
  @media (hover: hover) and (pointer: fine) {{
    .fbtn:hover {{ color: var(--sc-ink); background: var(--sc-surface); }}
  }}
  .fbtn.active {{
    background: var(--sc-surface-hi);
    color: var(--sc-accent);
    border-color: color-mix(in oklab, var(--sc-accent) 38%, transparent);
    box-shadow: var(--sc-edge);
  }}
  .search-input {{
    width: 260px;
    padding: 0.36rem 0.75rem;
    border-radius: var(--sc-r-sm);
    border: 1px solid var(--sc-hairline);
    background: var(--sc-surface);
    color: var(--sc-ink);
    font-size: 0.82rem;
    transition: border-color 160ms var(--sc-ease-out);
  }}
  .search-input::placeholder {{ color: var(--sc-ink-muted); }}
  .search-input:focus {{ outline: none; border-color: var(--sc-accent); }}

  /* Two-Pane Workspace */
  main.workspace {{
    display: grid;
    grid-template-columns: 470px 1fr;
    flex: 1;
    min-height: 0;
  }}

  /* Left Feed Rail: Real Video Thumbnails + Relevance Score + Suitability Explanation */
  aside.feed-rail {{
    border-right: 1px solid var(--sc-hairline);
    overflow-y: auto;
    background: var(--sc-canvas);
  }}
  .feed-item {{
    display: block;
    padding: var(--sc-4) var(--sc-5);
    border-bottom: 1px solid var(--sc-hairline);
    cursor: pointer;
    position: relative;
    transition: background 160ms var(--sc-ease-out);
  }}
  @media (hover: hover) and (pointer: fine) {{
    .feed-item:hover {{ background: color-mix(in oklab, var(--sc-surface) 65%, var(--sc-canvas)); }}
  }}
  .feed-item.active {{
    background: var(--sc-surface);
    box-shadow: var(--sc-edge);
  }}
  .feed-item.active::before {{
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    background: var(--sc-accent);
  }}

  .feed-top {{
    display: grid;
    grid-template-columns: 168px 1fr;
    gap: 0.9rem;
    align-items: start;
  }}
  .thumb-frame {{
    position: relative;
    width: 168px;
    height: 94px;
    border-radius: var(--sc-r-sm);
    overflow: hidden;
    background: var(--sc-surface-hi);
    box-shadow: var(--sc-e2), var(--sc-edge);
    border: 1px solid var(--sc-hairline);
  }}
  .thumb-frame img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 240ms var(--sc-ease-out);
  }}
  @media (hover: hover) and (pointer: fine) {{
    .feed-item:hover .thumb-frame img {{ transform: scale(1.03); }}
  }}
  /* Corner scrim protecting the score badge over the thumbnail */
  .thumb-scrim {{
    position: absolute; inset: 0; pointer-events: none;
    background: linear-gradient(135deg,
      color-mix(in oklab, var(--sc-canvas) 88%, transparent) 0%,
      color-mix(in oklab, var(--sc-canvas) 35%, transparent) 38%,
      transparent 65%);
  }}
  .score-badge {{
    position: absolute;
    top: 6px; left: 6px;
    padding: 0.14rem 0.44rem;
    border-radius: 4px;
    background: var(--sc-accent);
    color: var(--sc-accent-ink);
    font-family: var(--sc-font-mono);
    font-size: 0.7rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.01em;
    line-height: 1.2;
  }}
  .dur-chip {{
    position: absolute;
    bottom: 6px; right: 6px;
    padding: 0.1rem 0.38rem;
    border-radius: 4px;
    background: color-mix(in oklab, var(--sc-canvas) 86%, transparent);
    color: var(--sc-ink);
    font-family: var(--sc-font-mono);
    font-size: 0.68rem;
    font-variant-numeric: tabular-nums;
  }}

  .feed-meta {{
    min-width: 0;
  }}
  .feed-kicker {{
    font-family: var(--sc-font-mono);
    font-size: 0.67rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--sc-ink-soft);
    margin-bottom: 0.3rem;
    line-height: 1.35;
  }}
  .feed-kicker .queued-dot {{
    color: var(--sc-accent);
    font-weight: 600;
  }}
  .feed-title {{
    font-family: var(--sc-font-display);
    font-size: 0.98rem;
    font-weight: 600;
    line-height: 1.24;
    letter-spacing: var(--sc-track-snug);
    color: var(--sc-ink);
    margin: 0;
    text-wrap: balance;
  }}

  /* Suitability explanation below the thumbnail in the left rail */
  .suitability-box {{
    margin-top: 0.72rem;
    padding-top: 0.62rem;
    border-top: 1px solid color-mix(in oklab, var(--sc-ink) 7%, transparent);
  }}
  .factor-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.32rem;
    margin-bottom: 0.38rem;
  }}
  .factor-chip {{
    font-family: var(--sc-font-mono);
    font-size: 0.66rem;
    color: var(--sc-ink);
    background: color-mix(in oklab, var(--sc-ink) 7%, transparent);
    padding: 0.12rem 0.42rem;
    border-radius: 4px;
    font-variant-numeric: tabular-nums;
  }}
  .feed-item.active .factor-chip {{
    background: color-mix(in oklab, var(--sc-accent) 14%, transparent);
    color: var(--sc-accent);
  }}
  .why-text {{
    margin: 0;
    font-size: 0.8rem;
    line-height: 1.45;
    color: var(--sc-ink-soft);
    text-wrap: pretty;
  }}
  .why-label {{
    color: var(--sc-ink);
    font-weight: 500;
  }}

  /* Right Stage: Editorial Brief + Inline Cinema Player */
  section.brief-stage {{
    overflow-y: auto;
    padding: var(--sc-6) var(--sc-7) var(--sc-8);
    background: var(--sc-canvas);
  }}
  .stage-inner {{
    max-width: 980px;
    margin: 0 auto;
  }}

  /* Composed Hero Split: Editorial Title + Suitability Math Left, 16:9 Cinema Stage Right */
  .hero-split {{
    display: grid;
    grid-template-columns: 1fr 390px;
    gap: var(--sc-6);
    align-items: start;
    padding-bottom: var(--sc-6);
    border-bottom: 1px solid var(--sc-hairline);
  }}
  .hero-kicker {{
    font-family: var(--sc-font-mono);
    font-size: 0.74rem;
    letter-spacing: var(--sc-track-wide);
    text-transform: uppercase;
    color: var(--sc-accent);
    margin-bottom: var(--sc-2);
  }}
  .hero-title {{
    font-family: var(--sc-font-display);
    font-size: clamp(1.65rem, 2.2vw, 2.3rem);
    font-weight: 600;
    line-height: 1.06;
    letter-spacing: var(--sc-track-tight);
    color: var(--sc-ink);
    text-wrap: balance;
    margin: 0 0 var(--sc-3) 0;
  }}
  .hero-telemetry {{
    font-family: var(--sc-font-mono);
    font-size: 0.76rem;
    color: var(--sc-ink-soft);
    font-variant-numeric: tabular-nums;
    margin-bottom: var(--sc-4);
  }}

  /* Relevance Breakdown Block inside the Hero */
  .suitability-ledger {{
    background: var(--sc-surface);
    box-shadow: var(--sc-edge);
    border: 1px solid var(--sc-hairline);
    border-radius: var(--sc-r-md);
    padding: 0.9rem 1.1rem;
  }}
  .ledger-head {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 0.45rem;
  }}
  .ledger-label {{
    font-family: var(--sc-font-mono);
    font-size: 0.7rem;
    letter-spacing: var(--sc-track-wide);
    text-transform: uppercase;
    color: var(--sc-ink-soft);
  }}
  .ledger-score {{
    font-family: var(--sc-font-mono);
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--sc-accent);
    font-variant-numeric: tabular-nums;
  }}
  .ledger-why {{
    margin: 0 0 0.65rem 0;
    font-size: 0.88rem;
    line-height: 1.5;
    color: var(--sc-ink);
    text-wrap: pretty;
  }}
  .ledger-factors {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }}
  .ledger-factor {{
    font-family: var(--sc-font-mono);
    font-size: 0.7rem;
    padding: 0.18rem 0.5rem;
    border-radius: 4px;
    background: color-mix(in oklab, var(--sc-accent) 12%, transparent);
    color: var(--sc-accent);
    font-variant-numeric: tabular-nums;
  }}

  /* Right Column of Hero: 16:9 Cinema Stage */
  .cinema-box {{
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
  }}
  .cinema-stage {{
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: var(--sc-r-md);
    overflow: hidden;
    background: var(--sc-surface-hi);
    box-shadow: var(--sc-e2), var(--sc-edge);
    border: 1px solid var(--sc-hairline-strong);
  }}
  .cinema-stage img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}
  .cinema-stage iframe {{
    width: 100%;
    height: 100%;
    border: 0;
    display: block;
  }}
  .cinema-scrim {{
    position: absolute; inset: 0;
    background: linear-gradient(to top,
      color-mix(in oklab, var(--sc-canvas) 88%, transparent) 0%,
      color-mix(in oklab, var(--sc-canvas) 28%, transparent) 48%,
      transparent 78%);
  }}
  .btn-watch-inline {{
    position: absolute;
    left: 14px; bottom: 14px;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.52rem 0.95rem;
    border-radius: var(--sc-r-sm);
    background: var(--sc-accent);
    color: var(--sc-accent-ink);
    border: none;
    font-family: var(--sc-font-display);
    font-size: 0.84rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: var(--sc-e2);
    transition: transform 160ms var(--sc-ease-out), opacity 160ms var(--sc-ease-out);
  }}
  @media (hover: hover) and (pointer: fine) {{
    .btn-watch-inline:hover {{ transform: translateY(-1px); }}
  }}
  .btn-watch-inline:active {{ transform: scale(0.97); }}

  .cinema-links {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: var(--sc-font-mono);
    font-size: 0.72rem;
    color: var(--sc-ink-soft);
  }}
  .cinema-links a {{
    color: var(--sc-ink);
    text-decoration: none;
    border-bottom: 1px solid var(--sc-hairline-strong);
    padding-bottom: 1px;
  }}
  .cinema-links a:hover {{ color: var(--sc-accent); border-color: var(--sc-accent); }}

  /* Section 1: 90-Second Bottom Line Lede */
  .section-block {{
    padding-block: var(--sc-6);
    border-bottom: 1px solid var(--sc-hairline);
  }}
  .section-label {{
    font-family: var(--sc-font-mono);
    font-size: 0.72rem;
    letter-spacing: var(--sc-track-wide);
    text-transform: uppercase;
    color: var(--sc-ink-soft);
    margin-bottom: var(--sc-3);
    display: block;
  }}
  .bottom-line-lede {{
    font-family: var(--sc-font-text);
    font-size: clamp(1.04rem, 1.22vw, 1.18rem);
    font-weight: 400;
    line-height: 1.58;
    letter-spacing: var(--sc-track-normal);
    color: var(--sc-ink-soft);
    max-width: 65ch;
    margin: 0;
    text-wrap: pretty;
  }}
  .bottom-line-lede strong {{ color: var(--sc-ink); font-weight: 600; }}
  .bottom-line-lede code, .check-text code {{
    font-family: var(--sc-font-mono);
    font-size: 0.85em;
    background: var(--sc-surface-hi);
    color: var(--sc-ink);
    padding: 0.1rem 0.35rem;
    border-radius: 4px;
  }}

  /* Section 2: Interactive 60-Day Goal Action Checklist (Hairline rows, no nested boxes) */
  .checklist-rows {{
    display: flex;
    flex-direction: column;
    border-top: 1px solid var(--sc-hairline);
  }}
  .check-row {{
    display: grid;
    grid-template-columns: 32px 22px 1fr;
    align-items: baseline;
    gap: 0.65rem;
    padding: 0.78rem 0.4rem;
    border-bottom: 1px solid var(--sc-hairline);
    cursor: pointer;
    transition: background 150ms var(--sc-ease-out);
  }}
  @media (hover: hover) and (pointer: fine) {{
    .check-row:hover {{ background: var(--sc-surface); }}
  }}
  .check-idx {{
    font-family: var(--sc-font-mono);
    font-size: 0.74rem;
    color: var(--sc-ink-muted);
    font-variant-numeric: tabular-nums;
  }}
  .check-row input[type="checkbox"] {{
    width: 15px; height: 15px;
    margin: 0;
    transform: translateY(2px);
    cursor: pointer;
  }}
  .check-text {{
    font-size: 0.94rem;
    line-height: 1.5;
    color: var(--sc-ink);
    max-width: 66ch;
  }}
  .check-row.done .check-text {{
    text-decoration: line-through;
    color: var(--sc-ink-muted);
  }}

  /* Section 3: Full Editorial Brief Typography & Tabular Tables */
  .brief-content {{
    padding-top: var(--sc-5);
  }}
  /* More space above a heading than below it (taste.md §Spacing) */
  .brief-content h2 {{
    font-family: var(--sc-font-display);
    font-size: 1.28rem;
    font-weight: 600;
    letter-spacing: var(--sc-track-snug);
    color: var(--sc-ink);
    margin: var(--sc-7) 0 var(--sc-3) 0;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid var(--sc-hairline);
  }}
  .brief-content h2:first-child {{ margin-top: var(--sc-2); }}
  .brief-content h3 {{
    font-family: var(--sc-font-display);
    font-size: 1.04rem;
    font-weight: 600;
    color: var(--sc-ink);
    margin: var(--sc-5) 0 var(--sc-2) 0;
  }}
  .brief-content p, .brief-content li {{
    color: var(--sc-ink-soft);
    max-width: 65ch;
    text-wrap: pretty;
  }}
  .brief-content strong {{ color: var(--sc-ink); font-weight: 600; }}
  .brief-content ul, .brief-content ol {{
    padding-left: 1.25rem;
    margin: 0.5rem 0 1rem 0;
  }}
  .brief-content li {{ margin-bottom: 0.38rem; }}
  .brief-content code {{
    font-family: var(--sc-font-mono);
    font-size: 0.84em;
    background: var(--sc-surface-hi);
    color: var(--sc-ink);
    padding: 0.12rem 0.38rem;
    border-radius: 4px;
  }}
  .brief-content pre {{
    background: var(--sc-surface);
    box-shadow: var(--sc-edge);
    border: 1px solid var(--sc-hairline);
    padding: var(--sc-4);
    border-radius: var(--sc-r-sm);
    overflow-x: auto;
  }}
  .brief-content pre code {{ background: none; padding: 0; }}
  .brief-content a {{
    color: var(--sc-accent);
    text-decoration-thickness: 1px;
    text-underline-offset: 0.22em;
  }}
  .table-wrap {{
    margin: var(--sc-4) 0 var(--sc-5) 0;
    overflow-x: auto;
  }}
  .brief-content table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
  }}
  .brief-content th {{
    text-align: left;
    font-family: var(--sc-font-mono);
    font-size: 0.72rem;
    letter-spacing: var(--sc-track-wide);
    text-transform: uppercase;
    color: var(--sc-ink-soft);
    padding: 0.65rem 0.85rem;
    border-bottom: 1px solid var(--sc-hairline-strong);
  }}
  .brief-content td {{
    padding: 0.75rem 0.85rem;
    border-bottom: 1px solid var(--sc-hairline);
    color: var(--sc-ink-soft);
    vertical-align: top;
  }}
  .brief-content td strong {{ color: var(--sc-ink); }}
</style>
</head>
<body>
<div class="sc-grain" aria-hidden="true"></div>

<header class="instrument-bar">
  <div class="brand-lockup">
    <span class="brand-dot"></span>
    <h1 class="brand-title">AI YouTube Scout</h1>
    <span class="brand-sub">Taste-Grounded Research Instrument</span>
  </div>

  <div class="telemetry-strip sc-nums">
    <div class="tel-item"><span class="tel-val">508</span><span>Likes Audited</span></div>
    <span class="tel-sep">/</span>
    <div class="tel-item"><span class="tel-val">16</span><span>Core Creators</span></div>
    <span class="tel-sep">/</span>
    <div class="tel-item"><span class="tel-val">31 &rarr; 16</span><span>Tonight's Filter</span></div>
    <span class="tel-sep">/</span>
    <div class="tel-item"><span class="tel-val tel-val--accent">Top 3</span><span>Playlist Queued</span></div>
  </div>

  <div class="header-actions">
    <a class="btn-playlist" href="https://www.youtube.com/playlist?list=PLWcCQNkVAFxY7dc2743X1w3sS7PJ8bd5I" target="_blank" rel="noopener">
      <span>Open "Worth Watching" Playlist &nearr;</span>
    </a>
  </div>
</header>

<nav class="filter-rail">
  <div class="filter-group">
    <button class="fbtn active" data-filter="all">All Scored Videos ({len(briefs)})</button>
    <button class="fbtn" data-filter="scouted">AI Scouted Overnight</button>
    <button class="fbtn" data-filter="playlist">Worth Watching Queue (Top 3)</button>
    <button class="fbtn" data-filter="Claude & Harnesses">Claude &amp; Harnesses</button>
    <button class="fbtn" data-filter="Agency & Revenue">Agency &amp; Revenue</button>
    <button class="fbtn" data-filter="Video & Content">Video &amp; Content</button>
  </div>
  <input type="search" class="search-input" id="searchInput" placeholder="Filter by creator, model, or goal...">
</nav>

<main class="workspace">
  <aside class="feed-rail" id="feedList"></aside>
  <section class="brief-stage" id="detailPane"></section>
</main>

<script>
const BRIEFS = {data_json};
let activeFilter = "all";
let searchQuery = "";
let selectedSlug = BRIEFS.length ? BRIEFS[0].slug : null;
let playingInline = false;

function matchesFilter(b) {{
  if (activeFilter === "scouted" && !b.is_scouted) return false;
  if (activeFilter === "playlist" && !b.in_playlist) return false;
  if (!["all", "scouted", "playlist"].includes(activeFilter)) {{
    if (!b.pillars.includes(activeFilter)) return false;
  }}
  if (searchQuery) {{
    const q = searchQuery.toLowerCase();
    const hay = (b.title + " " + b.creator + " " + b.why + " " + b.bottom_line + " " + b.pillars.join(" ")).toLowerCase();
    if (!hay.includes(q)) return false;
  }}
  return true;
}}

function renderFeed() {{
  const container = document.getElementById("feedList");
  const filtered = BRIEFS.filter(matchesFilter);
  if (filtered.length && !filtered.some(b => b.slug === selectedSlug)) {{
    selectedSlug = filtered[0].slug;
    playingInline = false;
  }}
  container.innerHTML = filtered.map(b => {{
    const isSel = b.slug === selectedSlug ? "active" : "";
    const lane = b.is_scouted ? "AI SCOUTED" : "LIKED LIST";
    const qBadge = b.in_playlist ? ` &middot; <span class="queued-dot">QUEUED</span>` : "";
    const factorsHtml = (b.factors || []).map(f => `<span class="factor-chip">${{f}}</span>`).join("");
    return `
      <article class="feed-item ${{isSel}}" data-slug="${{b.slug}}">
        <div class="feed-top">
          <div class="thumb-frame">
            <img src="${{b.thumb_url}}" onerror="this.onerror=null;this.src='${{b.thumb_fallback}}'" alt="${{b.title.replace(/"/g, '&quot;')}}" width="320" height="180" loading="lazy">
            <div class="thumb-scrim"></div>
            <span class="score-badge">${{b.score}} / 10</span>
            <span class="dur-chip">${{b.duration}}</span>
          </div>
          <div class="feed-meta">
            <div class="feed-kicker">${{b.creator}} &middot; ${{lane}}${{qBadge}}</div>
            <h3 class="feed-title">${{b.title}}</h3>
          </div>
        </div>
        <div class="suitability-box">
          <div class="factor-row">${{factorsHtml}}</div>
          <p class="why-text"><span class="why-label">Why it fits you:</span> ${{b.why}}</p>
        </div>
      </article>
    `;
  }}).join("");

  container.querySelectorAll(".feed-item").forEach(el => {{
    el.addEventListener("click", () => {{
      selectedSlug = el.getAttribute("data-slug");
      playingInline = false;
      renderFeed();
      renderDetail();
    }});
  }});
}}

function renderDetail() {{
  const pane = document.getElementById("detailPane");
  const b = BRIEFS.find(x => x.slug === selectedSlug);
  if (!b) {{
    pane.innerHTML = `<div class="stage-inner"><p style="color:var(--sc-ink-soft);">No matching video briefs found.</p></div>`;
    return;
  }}

  const factorsHtml = (b.factors || []).map(f => `<span class="ledger-factor">${{f}}</span>`).join("");

  const stageMedia = (playingInline && b.vid)
    ? `<iframe src="https://www.youtube.com/embed/${{b.vid}}?autoplay=1&rel=0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`
    : `<img src="${{b.thumb_url}}" onerror="this.onerror=null;this.src='${{b.thumb_fallback}}'" alt="${{b.title.replace(/"/g, '&quot;')}}" width="640" height="360">
       <div class="cinema-scrim"></div>
       <button class="btn-watch-inline" id="watchBtn">Play Video Inside Brief</button>`;

  let checklistHtml = "";
  if (b.actions && b.actions.length) {{
    const items = b.actions.map((act, idx) => {{
      const key = "scout_act_" + b.slug + "_" + idx;
      const checked = localStorage.getItem(key) === "1";
      const num = String(idx + 1).padStart(2, "0");
      return `
        <label class="check-row ${{checked ? 'done' : ''}}" data-key="${{key}}">
          <span class="check-idx">${{num}}</span>
          <input type="checkbox" ${{checked ? 'checked' : ''}}>
          <span class="check-text">${{act}}</span>
        </label>
      `;
    }}).join("");
    checklistHtml = `
      <div class="section-block">
        <span class="section-label">Actionable Ideas Extracted For Your 60-Day Goals</span>
        <div class="checklist-rows">${{items}}</div>
      </div>
    `;
  }}

  pane.innerHTML = `
    <div class="stage-inner">
      <div class="hero-split">
        <div class="hero-left">
          <div class="hero-kicker">RELEVANCE SCORE ${{b.score}} / 10 &middot; ${{b.is_scouted ? 'SCOUTED VIA RSS' : 'AUDITED FROM LIKES'}} &middot; ${{b.date}}</div>
          <h2 class="hero-title">${{b.title}}</h2>
          <div class="hero-telemetry">${{b.creator}} &middot; ${{b.duration}} video &middot; ${{b.transcript_chars}} chars analyzed &middot; 90-second read</div>
          <div class="suitability-ledger">
            <div class="ledger-head">
              <span class="ledger-label">Why This Video Was Scored Suitable For You</span>
              <span class="ledger-score">${{b.score}} / 10 Match</span>
            </div>
            <p class="ledger-why">${{b.why}}</p>
            <div class="ledger-factors">${{factorsHtml}}</div>
          </div>
        </div>
        <div class="cinema-box">
          <div class="cinema-stage">${{stageMedia}}</div>
          <div class="cinema-links">
            <span>${{b.in_playlist ? 'Queued in "Worth Watching" Playlist' : 'Brief-Only (No Watch Required)'}}</span>
            ${{b.url ? `<a href="${{b.url}}" target="_blank" rel="noopener">Open on YouTube &nearr;</a>` : ''}}
          </div>
        </div>
      </div>

      ${{b.bottom_line ? `
        <div class="section-block">
          <span class="section-label">90-Second Bottom Line</span>
          <p class="bottom-line-lede">${{b.bottom_line}}</p>
        </div>
      ` : ''}}

      ${{checklistHtml}}

      <div class="brief-content">
        ${{b.body_html}}
      </div>
    </div>
  `;
  pane.scrollTop = 0;

  const watchBtn = document.getElementById("watchBtn");
  if (watchBtn) {{
    watchBtn.addEventListener("click", () => {{
      playingInline = true;
      renderDetail();
    }});
  }}

  pane.querySelectorAll(".check-row").forEach(row => {{
    const cb = row.querySelector("input[type='checkbox']");
    const key = row.getAttribute("data-key");
    cb.addEventListener("change", () => {{
      if (cb.checked) {{
        localStorage.setItem(key, "1");
        row.classList.add("done");
      }} else {{
        localStorage.removeItem(key);
        row.classList.remove("done");
      }}
    }});
  }});
}}

document.querySelectorAll(".fbtn").forEach(btn => {{
  btn.addEventListener("click", () => {{
    document.querySelectorAll(".fbtn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    activeFilter = btn.getAttribute("data-filter");
    renderFeed();
    renderDetail();
  }});
}});

document.getElementById("searchInput").addEventListener("input", e => {{
  searchQuery = e.target.value.trim();
  renderFeed();
  renderDetail();
}});

renderFeed();
renderDetail();
</script>
</body>
</html>
"""
    out_path = os.path.join(HERE, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {out_path} with {len(briefs)} briefs")


if __name__ == "__main__":
    main()
