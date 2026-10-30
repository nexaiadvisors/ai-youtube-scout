---
name: ai-youtube-scout
description: "Audits your YouTube Liked/Watch Later list into a taste-profile.md, scouts new uploads from your top channels via RSS, generates 1-page action briefs aligned with your 60-day goals, and builds an interactive local HTML dashboard (index.html). Use for 'scout youtube', 'summarize my youtube feed', 'build my youtube taste profile', or 'update video insights dashboard'."
---

# AI YouTube Scout (`ai-youtube-scout`)

Turns passive YouTube bookmarking into an active research pipeline grounded in your own past behavior and 60-day goals.

## Core Principles

1. **Past behavior beats vague prompts:** Never ask an LLM to *"find good videos"* in a vacuum. Ground `taste-profile.md` in the videos the user has actually saved or liked, plus their explicit 60-day goals.
2. **Score before summarizing:** Filter out Shorts (`< 4` minutes), music, and generic hype *before* pulling full transcripts.
3. **Separate reading from watching:** 80% of videos only need a 90-second read of the 1-page brief (`index.html`). Only the top 1–3 videos with visual screen-share walkthroughs belong in the **Worth Watching** playlist.
4. **Label creator self-interest:** Every 1-page brief explicitly separates the creator's commercial pitch (course, paid community, sponsor, affiliate link) from the replicable mechanism.

---

## Step 1: First-Run Onboarding Interview (`taste-profile.md`)

If `taste-profile.md` does not exist in the workspace, interview the user with **5 plain-English questions** (proposing sensible defaults based on their answers or any pasted list of saved video titles):

1. **60-Day Goals:** *"What are the 3–5 concrete project goals, capability upgrades, or business outcomes you are trying to ship over the next 60 days?"*
2. **Core Channels (or Paste Saved Titles):** *"Which 5–15 YouTube channels do you trust most—or would you like to paste 20–30 titles from your YouTube Liked / Watch Later list so I can extract them automatically?"*
3. **Hard Negative Filters:** *"What should I automatically drop? (Default: Shorts under 4 minutes, music/ambient mixes, gaming, and news hype without a live workflow demo.)"*
4. **Transcript Engine:** *"How should we pull transcripts for winning videos? (Option A: `youtube-transcript-api` / `yt-dlp` locally with zero setup; Option B: Google NotebookLM MCP if installed.)"*
5. **Playlist Queue:** *"Do you want to link a private YouTube playlist URL for your top picks on the dashboard?"*

Write the resulting configuration to `taste-profile.md` (modeled on `taste-profile.example.md`) and `channels.json`.

---

## Step 2: Scout & Score Recent Uploads (`scripts/scout_rss.py`)

Run the zero-key RSS scout against `channels.json` and `taste-profile.md`:

```bash
python3 scripts/scout_rss.py --config channels.json --days 7 --min-score 5
```

- Pulls the public YouTube Atom feed (`https://www.youtube.com/feeds/videos.xml?channel_id=<ID>`) for each tracked creator.
- Scores each candidate (`+4` Tier 1 creator, `+2` Tier 2 creator, `+3` per 60-day goal pillar match, `+2` concrete proof/workflow signal in title, `-100` for Shorts/noise).
- Emits the ranked JSON shortlist of videos that cleared `--min-score`.

---

## Step 3: Generate 1-Page Action Briefs (`briefs/YYYY-MM-DD-slug.md`)

For the top 1–3 scored videos (or any video URL the user explicitly requests):

1. **Fetch the full word-for-word transcript:**
   - Local CLI route: `python3 -m youtube_transcript_api <video_id>` or `yt-dlp --skip-download --write-auto-sub --sub-lang en <url>`.
   - NotebookLM route (if configured): add the YouTube URL as a source and query the notebook.
2. **Write `briefs/YYYY-MM-DD-<slug>.md` using this exact structure:**

```markdown
# Video Insights: "<Video Title>"

- Date analyzed: YYYY-MM-DD
- Source: https://www.youtube.com/watch?v=<ID> (<Channel Name>), scouted YYYY-MM-DD (score <N>)
- Transcript: complete, <char_count> characters (about <minutes> minutes)
- Grounded in: `taste-profile.md`

## 1. Bottom line for you

<One crisp paragraph (3-5 sentences): what the speaker actually proved, the key numbers/tradeoffs, and the single highest-leverage takeaway for the user's 60-day goals.>

## 2. Key ideas from the video

Self-interest labels: <Note any course, Skool community, sponsor, or affiliate product the speaker promotes.>

| # | Idea | Detail |
|---|---|---|
| 1 | <Core mechanism> | <Specific numbers, steps, or benchmarks from the transcript> |

## 3. How this applies to you

- **Goal 1 (<Name>):** <Concrete application>
- **What does not fit:** <What to ignore or skip>

## 4. Suggested next steps

1. <Specific, bounded action item #1>
2. <Specific, bounded action item #2>
```

---

## Step 4: Rebuild & Open the Interactive Dashboard (`build_index.py`)

After writing or updating any brief in `briefs/`, rebuild `index.html`:

```bash
python3 build_index.py
```

Verify that `index.html` was written cleanly and open it in the user's browser (`open index.html` on macOS, `xdg-open index.html` on Linux).
