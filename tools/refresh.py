#!/usr/bin/env python3
"""
Refresh the live figures in data/crowdfunds.json from Discord.

Reads through the VesktopClaudeBridge HTTP mirror, which must be running with
the Discord client signed in:  https://github.com/dataterminals/VesktopClaudeBridge

What it updates, and nothing else:
  * `live` / `signups` on every crowdfund currently on the board
  * the whole `cohort` block (distinct backers, buckets, pairwise, new blood)
  * `meta.updated`

What it deliberately does NOT touch: the catalogue itself. Names, creators,
dates, release outcomes and vote tallies were reconstructed by hand from a
channel that deletes its own history — a script cannot re-derive them and must
not overwrite them. New crowdfunds are reported for you to add by hand.

Usage:
    python tools/refresh.py                 # refresh in place
    python tools/refresh.py --dry-run       # print what would change
    python tools/refresh.py --port 8791     # if the mirror moved
"""

from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

BOARD = "1399641218610233427"          # #crowdfund-projects
GUILD = "1302392670181916722"          # Tier 1 Imports
CARL = "235148962103951360"            # T1 Carl — seeds the 👍 on every post
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "crowdfunds.json"


def token() -> str:
    """Ask the sidecar for its bearer token, the same way its README does."""
    for repo in (ROOT.parent / "VesktopClaudeBridge", ROOT.parent.parent / "VesktopClaudeBridge"):
        if (repo / "sidecar" / "package.json").exists():
            out = subprocess.run(
                ["npm", "--prefix", str(repo / "sidecar"), "run", "--silent", "token"],
                capture_output=True, text=True, shell=(sys.platform == "win32"),
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
    sys.exit("Could not read the bridge token. Is VesktopClaudeBridge checked out alongside this repo?")


def get(port: int, tok: str, path: str) -> dict:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}", headers={"Authorization": f"Bearer {tok}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.URLError as e:
        sys.exit(f"Bridge not reachable on :{port} ({e}). Start the sidecar, or pass --port.")


def title_of(body: str) -> str | None:
    """Crowdfund posts put the name on its own bold line under the banner."""
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if "ANNOUNCING OUR NEXT CROWDFUND" in l.upper() and i + 1 < len(lines):
            return re.sub(r"\*+", "", lines[i + 1]).strip() or None
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8791)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tok = token()
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    # Case-insensitive: the board shouts some titles ("HEAVY METAL") that the
    # catalogue stores in title case.
    by_name = {c["name"].casefold(): c for c in doc["crowdfunds"] if c.get("name")}

    board = get(args.port, tok, f"/history?channelId={BOARD}&limit=25&json=1")
    posts = board.get("messages", [])
    print(f"board: {len(posts)} live post(s)")

    sets: dict[str, set[str]] = {}
    seen: list[str] = []
    unknown: list[str] = []

    for m in posts:
        name = title_of(m.get("content", ""))
        if not name:
            continue
        r = get(args.port, tok,
                f"/reactors?channelId={BOARD}&messageId={m['id']}&limit=500&json=1")
        groups = r.get("groups") or []
        if not groups:
            continue
        users = {u["id"] for u in groups[0]["users"] if u["id"] != CARL}
        if groups[0].get("truncated"):
            print(f"  ! {name}: reactor list truncated — raise the limit")

        sets[name] = users
        seen.append(name.casefold())
        target = by_name.get(name.casefold())
        if target is None:
            unknown.append(name)
            print(f"  NEW  {name}: {len(users)} backers — not in the catalogue, add it by hand")
            continue
        was = target.get("signups")
        target["live"] = True
        target["signups"] = len(users)
        print(f"  {name}: {was} -> {len(users)}")

    # Anything previously live that has dropped off the board has completed.
    for c in doc["crowdfunds"]:
        if c.get("live") and c.get("name","").casefold() not in seen:
            c.pop("live", None)
            print(f"  closed: {c['name']} (post gone from the board — set its release outcome by hand)")

    if len(sets) >= 2:
        allu = set().union(*sets.values())
        counts = {u: sum(1 for s in sets.values() if u in s) for u in allu}
        k = len(sets)
        doc["cohort"] = {
            "asOf": doc["meta"]["updated"],
            "basis": f"Exact reactor lists for the {k} crowdfunds live on this date, with the T1 Carl bot removed.",
            "distinct": len(allu),
            "signups": sum(len(s) for s in sets.values()),
            "buckets": [
                {"label": f"{i} of {k}", "people": sum(1 for v in counts.values() if v == i)}
                for i in range(1, k + 1)
            ],
            "pairwise": [
                {"a": a, "b": b, "shared": len(sets[a] & sets[b])}
                for a, b in itertools.combinations(sets, 2)
            ],
            "newBlood": {},
        }
        newest = max(sets, key=lambda n: by_name.get(n.casefold(), {}).get("date", ""))
        others = set().union(*(s for n, s in sets.items() if n != newest))
        doc["cohort"]["newBlood"] = {
            "crowdfund": newest,
            "fresh": len(sets[newest] - others),
            "of": len(sets[newest]),
        }
        print(f"cohort: {len(allu)} distinct across {k} crowdfunds")

    today = subprocess.run(["git", "log", "-1", "--format=%cs"], capture_output=True,
                           text=True, cwd=ROOT).stdout.strip()
    doc["meta"]["updated"] = doc["meta"]["updated"] if args.dry_run else (today or doc["meta"]["updated"])

    if args.dry_run:
        print("\n--dry-run: nothing written")
        return

    DATA.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwrote {DATA.relative_to(ROOT)}")
    if unknown:
        print("ACTION: add these to data/crowdfunds.json — " + ", ".join(unknown))


if __name__ == "__main__":
    main()
