#!/usr/bin/env python3
"""Zero-key YouTube RSS Scout for ai-youtube-scout.

Polls public YouTube channel Atom feeds (https://www.youtube.com/feeds/videos.xml?channel_id=...)
defined in channels.json, scores recent uploads against 60-day goal keywords, drops noise/Shorts,
and outputs the ranked shortlist as JSON.
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}

JUNK_PATTERN = re.compile(
    r"\b(mix|remix|lofi|lo-fi|chill|ambient|soundtrack|gameplay|walkthrough|"
    r"speedrun|gaming|asmr|24/7|#shorts|shorts)\b",
    re.IGNORECASE,
)

PROOF_PATTERN = re.compile(
    r"(\$\d+|\bwith\s+proof\b|\bstep-by-step\b|\bbreaks?\s+down\b|\bhow\s+i\s+built\b|"
    r"\bfull\s+course\b|\bplaybook\b|\bfiles\b|\bsystem\b|\bworkflow\b|\bbenchmark\b)",
    re.IGNORECASE,
)


def fetch_channel_feed(channel_id: str, name: str, tier: int) -> list[dict]:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "ai-youtube-scout/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_bytes = resp.read()
    except Exception:
        return []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []

    out = []
    for entry in root.findall("atom:entry", ATOM_NS):
        vid_el = entry.find("yt:videoId", ATOM_NS)
        title_el = entry.find("atom:title", ATOM_NS)
        pub_el = entry.find("atom:published", ATOM_NS)
        if vid_el is None or title_el is None:
            continue
        vid = (vid_el.text or "").strip()
        title = (title_el.text or "").strip()
        pub = (pub_el.text or "").strip() if pub_el is not None else ""
        out.append(
            {
                "id": vid,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "title": title,
                "channel": name,
                "published_at": pub,
                "tier": tier,
            }
        )
    return out


def score_item(item: dict, pillars: dict[str, list[str]]) -> tuple[int, list[str]]:
    title = item["title"]
    if JUNK_PATTERN.search(title):
        return -100, ["rejected: noise/Short pattern"]

    score = 4 if item.get("tier") == 1 else 2
    reasons = [f"Tier {item.get('tier', 2)} creator (+{score})"]

    hits = 0
    tl = title.lower()
    for pillar_name, keywords in pillars.items():
        matched = [k for k in keywords if k.lower() in tl]
        if matched:
            hits += 1
            if hits <= 2:
                score += 3
                reasons.append(f"pillar:{pillar_name} ({matched[0]!r}: +3)")

    pm = PROOF_PATTERN.search(title)
    if pm:
        score += 2
        reasons.append(f"proof/workflow signal ({pm.group(0)!r}: +2)")

    return score, reasons


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="channels.json", help="Path to channels.json")
    ap.add_argument("--days", type=int, default=7, help="Lookback window in days")
    ap.add_argument("--min-score", type=int, default=5, help="Minimum score threshold")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.is_file():
        print(json.dumps({"error": f"{cfg_path} not found"}))
        return 1

    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    channels = cfg.get("channels", [])
    pillars = cfg.get("pillars", {})
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=args.days)).isoformat()

    candidates = []
    for ch in channels:
        items = fetch_channel_feed(ch["channel_id"], ch["name"], int(ch.get("tier", 1)))
        for it in items:
            if it["published_at"] and it["published_at"] < cutoff:
                continue
            sc, reasons = score_item(it, pillars)
            if sc >= args.min_score:
                it["score"] = sc
                it["reasons"] = reasons
                candidates.append(it)

    candidates.sort(key=lambda x: (x["score"], x["published_at"]), reverse=True)
    print(
        json.dumps(
            {
                "scanned_channels": len(channels),
                "matched_count": len(candidates),
                "candidates": candidates[:15],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
