# T1 Crowdfund Registry

**→ <https://dataterminals.github.io/t1-crowdfunds/>**

A persistent panel tracking every crowdfund **Tier 1 Imports** has run — the Ghost Recon: Breakpoint modding community.

It answers the questions the Discord itself can no longer answer, because `#crowdfund-projects` keeps only the handful of posts currently on the board and roughly twenty `@everyone` links into it are dead:

- What crowdfunds have there **been**? (at least 55, since 2024-11-02)
- How many people actually **paid**, as opposed to clicking 👍?
- Where did it end up — public, the supporter armoury, or exclusive to that crowdfund's backers?
- What did backers get *after* the vote? *(198 further drops across 11 crowdfunds, median 64 days.)*

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
  "era": 2,                   // 1 = buy-in, 2 = the reaction-role era
  "date": "2026-09-14",
  "approx": false,            // true prints a ~ next to the date
  "name": "Some Crowdfund",   // null if the name is not recoverable
  "creator": "SomeModder",
  "announced": "everyone",    // "everyone" | "chat"
  "live": true,               // still on the board
  "signups": 61,              // 👍 count, bot excluded
  "vote": {                   // the release vote, if one is readable
    "question": "Release.",   // verbatim, because scope varies
    "scope": "project",       // "project" | "items" — see below
    "scopeNote": null,        // what the vote covered, when it wasn't the whole thing
    "options": [{ "label": "Public", "count": 40 }, { "label": "Tier 2", "count": 48 }],
    "total": 88,
    "winner": "supporters"    // "public" | "supporters" | "private"
  },
  "delivery": {               // what backers got after the vote
    "creator": "SomeModder", "posts": 12,
    "first": "2026-09-20", "last": "2026-11-02", "days": 43,
    "exclusiveMentions": 3
  },
  "release": "supporters",    // mirrors vote.winner, for the table
  "note": "Anything worth a line under the name.",
  "src": "1539733497500016770" // the message this came from
}
```

Only `n`, `era`, `date` and `name` are required. Everything else degrades gracefully — a crowdfund
with no `vote` simply shows no turnout, and `"name": null` renders as *name not recoverable*.

**Set `scope` honestly.** A crowdfund does not have one destination. Two of the eleven readable votes
were scoped to named items rather than the project — one asked only where to put the XOF Outfits, and
most of that crowdfund stayed supporter-side regardless. Those carry `"scope": "items"` and a
`scopeNote`, and the panel marks them **subset**. Exclusives never enter the vote at all: they stay
with the crowdfund that paid for them.

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

The mark is the community's own — the glitch-skull from the closing frames of the animated server
icon, taken from the supplied logo kit rather than traced. It sits unboxed in the masthead because
the glitch trail runs right, into the wordmark, and a frame would crop the one gesture carrying it.
Below about 48px that trail turns to noise, so the small favicons use the cranium alone.

**`#AA0F1B`** is the brand red, from the kit's `color_match` layer. On this ground it measures 2.45:1,
under the 3:1 contrast floor, so it is used for identity — the masthead rule, the mark's glow — and
never to carry data. Charts use **`#C41220`**: the same hue to within 0.1°, the same saturation, value
lifted only until it clears. Against **`#3E92C4`** that pair measures normal-vision ΔE 32.5 and
deuteranopia 23.5 on a colourblind-separation validator, run rather than eyeballed. Both segments are
direct-labelled regardless, so colour never carries identity alone. The panel is dark-only by
deliberate choice — it is a brand, not a theme.

---

## Layout

```
index.html            the panel — one file, no build, no dependencies but Google Fonts
data/crowdfunds.json  every crowdfund, the release destinations, cohort stats
tools/refresh.py      re-pull live figures from Discord via the bridge
assets/               the logo kit as supplied, plus the derived mark, icons and link card
```

Not an official Tier 1 Imports publication.

Non-creator names are omitted throughout: modders are credited for their work, everyone else is referred to by role.
