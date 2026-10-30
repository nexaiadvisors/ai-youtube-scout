# Video Insights: "Train Your AI to Write Like a Human With Just 3 Files"

- Date analyzed: 2026-10-28
- Source: https://www.youtube.com/watch?v=yDFCJzDgWhI (Marketing Against the Grain), liked 2026-10-28 (score 9)
- Transcript: complete, 29,317 characters (about 29 minutes). Fetched through Google NotebookLM.
- Grounded in: `taste-profile.md`

## 1. Bottom line for you

Most AI writing sounds like commodity filler because the model has general knowledge but zero point of view. Splitting context into three focused files—`creator.md` (how you think and write, built from real examples rather than adjectives), `audience.md` (five specific dream readers and their real bottlenecks), and `taste.md` (your quality bar, never-do list, and publish test)—lets an agent critique and draft with your actual voice.

## 2. Key ideas from the video

Self-interest labels: Podcast published by HubSpot; promotes a lead-magnet prompt pack and an affiliated tool.

| # | Idea | Detail |
|---|---|---|
| 1 | The 3-file context architecture | Separate `creator.md` (voice & real examples), `audience.md` (specific buyer profiles), and `taste.md` (quality bar & negative rules). |
| 2 | Strip one-off viral outliers | Remove one-time launch announcements or outlier posts from your voice training set so the agent learns repeatable structure. |
| 3 | Sequential pass beats single mega-prompt | Loading all three files at once caused the model to ignore `taste.md`; running a dedicated second pass against `taste.md` caught AI tells reliably. |

## 3. How this applies to you

- **Claude & Harnesses:** Keep a dedicated `taste-profile.md` with explicit negative filters and run a separate verification pass after drafting.
- **Agency & Revenue:** Package the 3-file interview (`creator.md`, `audience.md`, `taste.md`) as the onboarding step for any client content or communication system.

## 4. Suggested next steps

1. Maintain an explicit negative-filter list in `taste-profile.md` and enforce it with a deterministic check.
2. Run a separate critic pass against `taste-profile.md` rather than stuffing every rule into a single generation prompt.
