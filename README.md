# T1 Crowdfund Registry

**→ <https://dataterminals.github.io/t1-crowdfunds/>**

A persistent panel tracking every crowdfund [Tier 1 Imports](https://discord.gg/) has run — the Ghost Recon: Breakpoint modding community — across **both** of its funding systems.

It answers the questions the Discord itself can no longer answer, because `#crowdfund-projects` keeps only the handful of posts currently on the board and roughly twenty `@everyone` links into it are dead:

- What crowdfunds have there **been**? (at least 55, since 2024-11-02)
- How did the **buy-in era** differ from **"Smiley's way"**?
- How many people actually **paid**, as opposed to clicking 👍?
- Why can't I find that mod on Nexus? *(Two thirds of measured projects voted to stay supporter-only.)*

The narrative write-up, with a Discord message ID behind every claim, lives in the knowledgebase:
[**grb-modding-knowledgebase / reference/crowdfund-history.md**](https://github.com/dataterminals/grb-modding-knowledgebase/blob/main/reference/crowdfund-history.md).

---

## Updating it

Everything the panel draws is in **[`data/crowdfunds.json`](data/crowdfunds.json)**. The page is a static
reader over that file — edit the JSON, commit, and the site updates. No build step.

### By hand

Add an object to `crowdfunds[]`:

```jsonc
{
  "n": 56,                    // running number
  "era": 2,                   // 1 = buy-in, 2 = Smiley's way
  "date": "2026-09-14",
  "approx": false,            // true prints a ~ next to the date
  "name": "Some Crowdfund",   // null if the name is not recoverable
  "creator": "SomeModder",
  "announced": "everyone",    // "everyone" | "chat"
  "live": true,               // still on the board
  "signups": 61,              // 👍 count, bot excluded
  "vote":    { "total": 88, "public": 40, "supporters": 48 },
  "release": "supporters",    // "public" | "supporters" | "private"
  "note": "Anything worth a line under the name.",
  "src": "1539733497500016770" // the message this came from
}
```

Only `n`, `era`, `date` and `name` are required. Everything else degrades gracefully — a crowdfund
with no `vote` simply shows no turnout, and `"name": null` renders as *name not recoverable*.

### Automatically

`tools/refresh.py` re-pulls the parts that actually change — sign-up counts and backer overlap —
through the [VesktopClaudeBridge](https://github.com/dataterminals/VesktopClaudeBridge) HTTP mirror.
The sidecar has to be running with Discord signed in.

```bash
python tools/refresh.py --dry-run   # show what would change
python tools/refresh.py             # write it
```

It updates `live` / `signups` on everything currently posted, rebuilds the whole `cohort` block from
exact reactor lists, and reports any crowdfund on the board that isn't in the catalogue yet.

It deliberately **will not** touch names, creators, dates, release outcomes or vote tallies. Those were
reconstructed by hand from a channel that no longer holds them; a script cannot re-derive them and
must not overwrite them.

> The bot account **T1 Carl** seeds the 👍 on every crowdfund post, so every raw reaction count is
> inflated by exactly one. The script removes it; if you enter a figure by hand, subtract it yourself.

---

## Design

The visual language follows **DeckardX1**, the long-time Tier 1 modder and moderator who drew the T1
logo and most of the marks this community wears on its gear — credited across the mod corpus as
*"Logos designed by DeckardX"*.

Read off his own work: stamped-metal relief with a soft top-light bevel, squircle badges, chamfered
geometry, scratched surface texture, a monochrome warm-stone ground, and oxide red as the single
accent. Type is square-techno throughout — Michroma standing in for the Microgramma he names as his
own reference, with Chakra Petch for its chamfered corners.

The two chart hues (`#C0392B` oxide, `#AE8726` brass) were run through a colourblind-separation
validator rather than picked by eye, and both are direct-labelled so colour is never the only cue.
The panel is dark-only by deliberate choice — it is a brand, not a theme.

---

## Layout

```
index.html            the panel — one file, no build, no dependencies but Google Fonts
data/crowdfunds.json  every crowdfund, the two systems, cohort stats, and the known gaps
tools/refresh.py      re-pull live figures from Discord via the bridge
```

Not an official Tier 1 Imports publication.
