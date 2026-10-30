# Video Insights: "His AI Made 20 Reels Before Breakfast"

- Date analyzed: 2026-10-29
- Source: https://www.youtube.com/watch?v=AtjFk9f44HE (Matt Wolfe & Nate Herk), liked 2026-10-28 (score 9)
- Transcript: complete, 44,981 characters (about 38 minutes). Fetched through Google NotebookLM.
- Grounded in: `taste-profile.md`

## 1. Bottom line for you

The highest-leverage pattern in this interview is building an agent skill from a "golden set" of proven work rather than inventing rules in a blank prompt. By having Claude Code study 27 top-performing human-edited videos frame by frame (extracting scene-change intervals, audio ducking levels, and graphic timing), every correction compounds into a reusable skill file instead of getting lost in chat history.

## 2. Key ideas from the video

Self-interest labels: Guest sells a paid community and uses free repos as lead magnets; host runs a sponsored newsletter.

| # | Idea | Detail |
|---|---|---|
| 1 | Reverse-engineer a golden set | Analyze 20-27 proven examples by screenshotting every few seconds to record cut timing, layout patterns, and audio levels into a skill file. |
| 2 | Word timestamps + waveform silence check | Combine word-level transcription timestamps with an audio waveform check so cuts never clip the tail of a spoken word. |
| 3 | Screenshot verification loop | Bake "screenshot every rendered element and verify it is inside safe bounds" into any visual agent workflow. |
| 4 | Compounding feedback log | Save every human review correction back into the skill's rules file so the next run requires fewer manual edits. |

## 3. How this applies to you

- **Video & Content Flywheel:** Derive editing and layout presets directly from your best-performing uploads and verify every visual beat with a contact sheet before final render.
- **Claude & Harnesses:** Log every human review fix into a persistent rules file so the agent never repeats the same layout or pacing mistake twice.

## 4. Suggested next steps

1. Build a golden-set reference table from your top-performing videos or posts before tuning a new content skill.
2. Add an automated contact-sheet and word-sync check before rendering any long-form video.
