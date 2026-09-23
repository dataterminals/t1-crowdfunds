# T1 Crowdfund Registry

**→ <https://dataterminals.github.io/t1-crowdfunds/>**

A persistent panel tracking every crowdfund **Tier 1 Imports** has run — the Ghost Recon: Breakpoint modding community.

It answers the questions the Discord itself can no longer answer, because `#crowdfund-projects` keeps only the handful of posts currently on the board and roughly twenty `@everyone` links into it are dead:

- What crowdfunds have there **been**? (at least 61, since the server opened in November 2024)
- How many people actually **supported** each one, as opposed to clicking 👍?
- Where did it end up — public, the supporter armoury, or exclusive to that crowdfund's backers?
- What did backers get *after* the vote? *(198 further drops across 11 crowdfunds, median 64 days.)*

Every figure here traces to a Discord message or a release vote. The narrative write-up carrying those
citations is not linked for now.

### How complete it is

Two things widened the record on 2026-08-30, and one thing did not:

- **Release votes: 40 of 61.** A Tier 1 moderator supplied vote tallies and supporter counts for 40
  crowdfunds, compiled by going through the confirmed channels by hand. They were checked against the
  11 votes this account can read first-hand and matched 11 for 11. Every figure is a crowdfund's own
  tally, never the summary sentence beside it.
- **Destination: 49 of 61.** Where each crowdfund's output actually landed, reconstructed from public
  channels, Nexus and the supporter armoury. This is a broader and weaker claim than the vote, and not
  always the same answer, because some votes cover only part of a project.
- **Delivery: still 11 of 61.** Drops happen inside a crowdfund's own supporter channel, leave no
  public trace, and nobody tallies them the way they tally a vote. These 11 are what a single
  supporter's account can see, and the panel says so above that section.

Era 1 (the buy-in system, 2024-11 to 2025-07) is a recovered floor, not a count. Era 2 (the
reaction-role system, since 2025-07-29) is complete and, since 2026-08-24, completely named.

---

## Updating it

Everything the panel draws is in **[`data/crowdfunds.json`](data/crowdfunds.json)**. The page is a static
reader over that file — edit the JSON, commit, and the site updates. No build step.

### By hand

Add an object to `crowdfunds[]`:

```jsonc
{
  "n": 62,                    // running number
  "era": 2,                   // 1 = buy-in, 2 = the reaction-role era
  "date": "2026-09-14",
  "approx": false,            // true prints a ~ next to the date
  "name": "Some Crowdfund",   // null if the name is not recoverable
  "creator": "SomeModder",
  "announced": "everyone",    // "everyone" | "chat"
  "live": true,               // still on the board — refresh.py maintains this
  "signups": 61,              // 👍 count, bot excluded — refresh.py maintains this
  "items": ["Plate carrier.", "Helmet."],   // what the post advertises; shown while it is on the board
  "members": 88,              // the confirmed channel's membership: the people who supported it
  "vote": {                   // the release vote, if one is readable
    "question": "Release.",   // verbatim, because scope varies
    "scope": "project",       // "project" | "items" — see below
    "scopeNote": null,        // what the vote covered, when it wasn't the whole thing
    "options": [{ "label": "Public", "count": 40 }, { "label": "Tier 2", "count": 48 }],
    "total": 88,
    "winner": "supporters",   // "public" | "supporters" | "private"
    "basis": "moderator",     // present when the tally came from the moderator's list; absent when read first-hand
    "src": "1543764047386910781"
  },
  "release": "supporters",    // mirrors vote.winner — the table draws a solid pill only where a vote was read
  "destination": {            // where the output actually landed — a separate, weaker claim than the vote
    "where": "supporters",    // "public" | "supporters" | "private"
    "confidence": "vote",     // "vote" | "strong" | "moderate" | "disputed"
    "src": null,
    "note": "From the release vote read in the crowdfund's own channel."
  },
  "delivery": {               // what backers got after the vote
    "creator": "SomeModder", "posts": 12,
    "first": "2026-09-20", "last": "2026-11-02", "days": 43,
    "exclusiveMentions": 3
  },
  "note": "Anything worth a line under the name.",
  "src": "1539733497500016770" // the message this came from
}
```

Only `n`, `era`, `date` and `name` are required. Everything else degrades gracefully — a crowdfund
with no `vote` simply shows no turnout, and `"name": null` renders as *name not recoverable*.

**`vote` and `destination` are different claims.** The vote is what the backers decided, read from the
crowdfund's own channel or from the moderator's list of them. The destination is where the output
turned up afterwards, and it can be known for a crowdfund whose vote is not. The table draws a solid
pill from the vote and a dashed one from the destination, so keep `release` in step with `vote.winner`
and never set it from a destination alone. `confidence` says how the destination is known: `vote` =
read from the crowdfund's own channel, `strong` = the creator or a moderator said so, `moderate` =
members only, `disputed` = the sources disagree, and `where` is left null.

**Set `scope` honestly.** A crowdfund does not have one destination. Two of the forty readable votes
were scoped to named items rather than the project — one asked only where to put the XOF Outfits, and
most of that crowdfund stayed supporter-side regardless. Those carry `"scope": "items"` and a
`scopeNote`, and the panel marks them **subset**. Exclusives never enter the vote at all: they stay
with the crowdfund that funded them.

**Write `note` for a reader, not for the researcher.** It says what the thing was, and stops. The
chain of custody — which message named it, who bound it to which post — belongs in the `src` fields,
not in the cell next to the name.

### Automatically

`tools/refresh.py` re-pulls the parts that actually change — sign-up counts and backer overlap —
through the [VesktopClaudeBridge](https://github.com/dataterminals/VesktopClaudeBridge) HTTP mirror.
The sidecar has to be running with Discord signed in, and checked out alongside this repo so the
script can ask it for its token (or set `BRIDGE_TOKEN`).

```bash
python tools/refresh.py --dry-run   # show what would change
python tools/refresh.py             # write it
python tools/refresh.py --port 8791 # if the mirror is not where its config says
```

It updates `live` / `signups` on everything currently posted, clears `live` on anything that has
dropped off the board, rebuilds the whole `cohort` block from exact reactor lists, and reports any
crowdfund on the board that isn't in the catalogue yet. The new-blood figure skips a crowdfund posted
less than a week ago, because the first people through the door are the regulars and the number would
read backwards.

It deliberately **will not** touch names, creators, dates, supporter counts, release outcomes,
destinations or vote tallies. Those were reconstructed by hand from a channel that no longer holds
them; a script cannot re-derive them and must not overwrite them. When a crowdfund drops off the
board, set its outcome by hand.

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
