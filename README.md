# AI YouTube Scout (`ai-youtube-scout`)

An open-source AI agent skill and interactive local dashboard that stops your YouTube **Liked videos** and **Watch Later** lists from turning into a 500-video graveyard.

Instead of scrolling the home feed or using a generic *"summarize this video"* prompt that makes every 40-minute video sound equally urgent, **AI YouTube Scout** runs a 3-step pipeline:

1. **Audits your historical saves into a `taste-profile.md`:** Interviews you (or analyzes the last 30–500 videos you actually liked) to extract your top 10–16 channels, your 3–5 active 60-day goals, and hard negative filters (auto-drop Shorts under 4 minutes, music, and generic hype without a workflow demo).
2. **Scouts new uploads & writes 1-page action briefs:** Polls RSS feeds (`https://www.youtube.com/feeds/videos.xml?channel_id=...`, zero API key required) from your core creators, scores new long-form uploads against your `taste-profile.md`, pulls the word-for-word transcript (via Google's free [NotebookLM](https://notebooklm.google.com) or `youtube-transcript-api`), and generates a 1-page Markdown brief in `briefs/` with the 90-second bottom line, concrete numbers, and action items for your 60-day goals.
3. **Builds an interactive local dashboard (`index.html`) + queues your Top 3:** Compiles every brief into a zero-dependency two-pane HTML dashboard (`python3 build_index.py`) where you can filter by goal pillar, check off action items, watch the embedded video right inside the brief, or open your curated **Worth Watching** playlist.

---

## Copy-Paste Agent Setup Prompt (Claude Code, Cursor, Codex, or Antigravity)

Paste this prompt into your coding agent to set up the entire system on your machine in 5 minutes:

```text
Clone https://github.com/nexaiadvisors/ai-youtube-scout into ~/ai-youtube-scout, install the skill in skill/ into my agent skills folder (~/.claude/skills/ai-youtube-scout), and walk me through the 5-question setup interview to generate my taste-profile.md, run my first YouTube RSS scout, and open my local index.html dashboard.
```

---

## Quick Start (Manual or Agent-Driven)

```bash
git clone https://github.com/nexaiadvisors/ai-youtube-scout.git
cd ai-youtube-scout

# Optional: install as a Claude Code / Cursor / Codex skill
cp -R skill ~/.claude/skills/ai-youtube-scout

# Rebuild and open the interactive dashboard with the included sample briefs
python3 build_index.py
open index.html
```

---

## Repository Contents

| Path | Description |
|---|---|
| [`index.html`](index.html) | Interactive two-pane **Video Insights & Idea Triage Dashboard** (pre-built with 3 sample briefs so you can try it immediately) |
| [`build_index.py`](build_index.py) | Zero-dependency Python script (standard library only) that compiles all Markdown briefs in `briefs/` into `index.html` |
| [`taste-profile.example.md`](taste-profile.example.md) | Template for your 60-day goal pillars, tiered creator roster, and negative filters |
| [`briefs/`](briefs/) | Folder of 1-page Markdown video briefs (`YYYY-MM-DD-slug.md`) |
| [`skill/SKILL.md`](skill/SKILL.md) | The complete agent skill (`ai-youtube-scout`) with the 5-question onboarding interview, RSS scout workflow, NotebookLM / transcript prompt, and dashboard rebuild steps |
| [`skill/scripts/scout_rss.py`](skill/scripts/scout_rss.py) | Standard-library Python RSS scout that fetches recent uploads from your creator channels and scores them against your `taste-profile.md` |

---

## The 10-Minute No-Code Version (Claude/ChatGPT + Free Google NotebookLM)

If you don't want to run scripts locally, you can get 80% of the benefit in 10 minutes using three free steps:

1. **Audit your taste:** Copy the titles of the last 20–30 videos in your YouTube **Liked videos** or **Watch Later** list and paste them into Claude or ChatGPT:
   > *"Based on the videos I actually save, what are the 5 channels and 3 business/technical problems I care about most right now?"*
2. **Generate a 1-page brief in NotebookLM:** Once a week, paste 1–3 new video URLs from those top channels into Google's free [NotebookLM](https://notebooklm.google.com) and run this prompt:
   > *"Give me a 1-page brief on this video with: (1) the bottom-line takeaway for my 60-day goal, (2) every real number, price, or benchmark mentioned, (3) what is creator sales pitch vs. replicable workflow, and (4) whether I need to watch the screen share."*
3. **Guard your playlist:** Create one private YouTube playlist called **`Worth Watching`** and only add a video after its 1-page brief proves it is worth 30 minutes of your attention.

---

## License

MIT — see [LICENSE](LICENSE).
