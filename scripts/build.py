#!/usr/bin/env python3
"""Build the GitHub guide and CSV from the reviewed public JSON snapshot."""
import csv
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# These are transparent title searches, not official topic classifications.
TOPICS = {
    "ai-and-agents": ("AI and agents", r"\b(ai|agents?|agentic|llms?|models?|inference|claude|deepmind)\b"),
    "developer-tools": ("Developer tools and infrastructure", r"\b(developers?|engineering|infra(?:structure)?|apis?|coding|code|observability|compute|cloud|databases?|data|devtools|mlops|mcp)\b"),
    "fundraising": ("Fundraising and investing", r"\b(fundrais\w*|invest\w*|vc|vcs|venture|capital|term sheet|cap table|pitch|lp|lps|gp|gps|series [abc])\b"),
    "health-and-biotech": ("Health and biotech", r"\b(health\w*|biotech|bio|medicine|medical|drug|brain|neuro\w*|longevity|wellness|life sciences)\b"),
    "climate-and-energy": ("Climate and energy", r"\b(climate|energy|cleantech|clean tech|sustainab\w*|carbon|power|grid|nuclear)\b"),
    "fintech": ("Fintech and commerce", r"\b(fintech|banking|payments?|finance|financial|commerce|stablecoins?|crypto|web3|blockchain|defi)\b"),
    "consumer-and-creative": ("Consumer and creative", r"\b(consumer|creativ\w*|creators?|gaming|games?|media|entertainment|design|music|film|art|fashion)\b"),
    "deep-tech": ("Deep tech and robotics", r"\b(deep[ -]?tech|robot\w*|hardware|semiconductor\w*|industrial|manufactur\w*|aerospace|quantum|space|defense|defence)\b"),
    "gtm-and-growth": ("GTM and growth", r"\b(gtm|go.to.market|sales|marketing|growth|revenue|customers?|partnership\w*)\b"),
    "global-founders": ("Global founders", r"\b(global|international|cross.border|market entry|immigr\w*|visa|europe\w*|latam|latino\w*|australia\w*|japan\w*|india\w*|africa\w*|korea\w*|canad\w*|brazil\w*|china|chinese)\b"),
    "hackathons-and-demos": ("Hackathons and demos", r"\b(hack\w*|demos?|buildathon\w*|builder\w*|build night|workshops?)\b"),
    "social-and-networking": ("Social and networking", r"\b(network\w*|mixer\w*|happy hour|party|afterparty|dinner|breakfast|brunch|lunch|coffee|run club|pickleball|yoga|hike|hiking|bike|cocktail\w*)\b"),
}


def load(name):
    return json.loads((DATA / name).read_text())


def esc(value):
    return str(value or "—").replace("|", "\\|").replace("\n", " ").replace("[", "\\[").replace("]", "\\]").replace("<", "&lt;").replace(">", "&gt;")


def write(path, text):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text.rstrip() + "\n")


def clock(value):
    if not value:
        return "TBA"
    return datetime.strptime(value, "%H:%M").strftime("%-I:%M %p")


def day(value):
    return datetime.strptime(value, "%Y-%m-%d").strftime("%a, Oct %-d")


def event_table(rows, include_date=False):
    header = "| " + ("Date | " if include_date else "") + "Start (PT) | Event / official details | Area | Calendar label |\n"
    header += "| " + ("--- | " if include_date else "") + "--- | --- | --- | --- |\n"
    return header + "\n".join(
        "| " + (f"{day(e['date'])} | " if include_date else "")
        + f"{clock(e['start_time'])} | [{esc(e['title'])}]({e['source_url']}) | {esc(e['neighborhood'])} | {esc(e['status_as_listed'])} |"
        for e in rows
    )


def pick_time(p):
    start = datetime.fromisoformat(p['start'])
    result = start.strftime("%a %-I:%M %p")
    if p['end']:
        end = datetime.fromisoformat(p['end'])
        result += "–" + end.strftime("%a %-I:%M %p" if end.date() != start.date() else "%-I:%M %p")
    else:
        result += " (end TBA)"
    return result


def main():
    events = sorted(load("events.json"), key=lambda e: (e['date'], e['start_time'] or '99:99', e['title'].casefold(), e['id']))
    meta, picks, more, tracks = (load(f) for f in ["metadata.json", "picks.json", "more-picks.json", "tracks.json"])
    counts = Counter(e['date'] for e in events)
    for date in sorted(counts):
        rows = [e for e in events if e['date'] == date]
        write(f"docs/days/{date}.md", f"# {day(date)}, 2026\n\n[Guide](../../README.md) · [All events](../all-events.md) · [Planning](../planning.md)\n\n{len(rows):,} listings starting this day. All times America/Los_Angeles (PDT, UTC−07:00). The calendar's label is a snapshot, not an admission confirmation; a blank label is shown as **Unspecified**. Follow each event's details link for its current RSVP route. Multi-day events appear on their starting day.\n\n" + event_table(rows))
    write("docs/all-events.md", f"# All {len(events):,} events\n\n[Guide](../README.md) · [Download CSV](../data/events.csv) · [Data notes](methodology.md)\n\nListings starting October 5–11, 2026. All times Pacific. Large GitHub previews may truncate; use the day files or download the CSV. Calendar labels are snapshots, not admission guarantees.\n\n" + event_table(events, True))
    topic_rows = []
    for slug, (title, pattern) in TOPICS.items():
        matches = [e for e in events if re.search(pattern, e['title'], re.I)]
        topic_rows.append(f"| [{title}](docs/topics/{slug}.md) | {len(matches):,} |")
        write(f"docs/topics/{slug}.md", f"# {title}\n\n[Guide](../../README.md) · [Official curated tracks](../../README.md#official-curated-tracks)\n\n{len(matches):,} title matches. This is an automatic keyword index, **not official tagging**. It can miss relevant events or include ambiguous matches. Events can appear in several indexes.\n\nSearch expression: `{pattern}`\n\n" + event_table(matches, True))
    fields = ["id", "date", "start_time", "timezone", "title", "neighborhood", "status_as_listed", "source_url", "checked_at"]
    with (DATA / "events.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for e in events:
            # Guard against formula interpretation when a CSV is opened in a spreadsheet.
            writer.writerow({k: ("'" + str(e[k]) if str(e.get(k) or "").startswith(("=", "+", "-", "@", "\t", "\r")) else e.get(k)) for k in fields})
    seed_lines = []
    for p in sorted(picks, key=lambda p: p['seed_rank']):
        seed_lines.append(f"| {p['seed_rank']} | [{esc(p['title'])}]({p['url']}) | {pick_time(p)} | {esc(p['reason_to_attend'])} |")
    seed_doc = ["# The original ten, rechecked", "", "[Guide](../README.md)", "", "These ten came from the starting shortlist. The order preserves that shortlist; it is not a ranking of the full calendar. Public registration pages were checked September 23, 2026 (Pacific). All ten showed application/approval. No explicit price was verified for any of them."]
    for p in sorted(picks, key=lambda p: p['seed_rank']):
        seed_doc += ["", f"## {p['seed_rank']}. {p['title']}", "", f"**{pick_time(p)} PT.** [Public listing / apply]({p['url']}).", "", p['reason_to_attend'], "", f"Admission: {p['admission']}. Price: {p['cost']}."]
        if p['notes']:
            seed_doc += ["", p['notes']]
    write("docs/seed-picks.md", "\n".join(seed_doc))
    breadth = ["# More ways to spend the week", "", "[Guide](../README.md) · [Planning](planning.md)", "", "Twenty editorial picks to broaden the original AI/startup/investor shortlist. Dates and start times were checked against public official listings. Reasons below are editorial suggestions, not organizer promises. Follow the official details page for the current application route; only links labeled **Organizer page checked** were independently read."]
    for p in more:
        details = p.get('canonical_url') or p['source_url']
        breadth += ["", f"## {p['name']}", "", f"{day(p['date'])}, {clock(p['start'])} PT · {p['neighborhood']} · {', '.join(p['themes'])}", "", p['why'], "", f"[Official / source details]({details})"]
        if p.get('registration_url') and p.get('registration_verified'):
            breadth += [f"[Organizer page checked]({p['registration_url']})"]
        if p.get('practical_note'):
            breadth += ["", p['practical_note']]
    write("docs/more-picks.md", "\n".join(breadth))
    days_table = "\n".join(f"| [{day(date)}](docs/days/{date}.md) | {counts[date]:,} |" for date in sorted(counts))
    official_tracks = "\n".join(f"- [{t['name']}]({t['url']})" for t in tracks)
    readme = f"""# SF Tech Week 2026

**October 5–11 · San Francisco & the Bay Area · All times Pacific**

A public, independent guide to **{len(events):,} official-calendar listings**, with the original ten picks rechecked, twenty more picks across industries, day-by-day schedules, keyword indexes, and reusable CSV/JSON data.

[Browse all events](docs/all-events.md) · [Download CSV](data/events.csv) · [JSON](data/events.json) · [Plan your week](docs/planning.md) · [Official live calendar](https://www.tech-week.com/calendar/sf)

Snapshot: **{meta['checked_at_display']}**. {meta['coverage_summary']} Event details can change. Apply through the organizer; a listing or submitted application does not mean admission. This project is not affiliated with a16z or Tech Week.

## Browse by day

| Day | Listings starting that day |
| --- | ---: |
{days_table}

Multi-day listings appear on their starting day. The week includes events outside San Francisco; check the area before planning travel.

## Start with these ten

The original shortlist, in its original order, with public registration pages rechecked. **All ten currently use application/approval; prices are unconfirmed.** These are options, not one itinerary.

| Pick | Event / apply | Schedule (PT) | Why consider it |
| --- | --- | --- | --- |
{chr(10).join(seed_lines)}

**Timing caveats:** Claude Founder House's header starts at 8:00 AM, while its daily cafe description starts at 11:00 AM. Google's Engineering 10x header says 9:30 AM, while its description mentions 9:00 AM. Confirm your session or accepted arrival time. The investor breakfast and NexxaWorld publish no end time.

[Read all ten's admission and timing notes](docs/seed-picks.md).

## Explore beyond the shortlist

[Twenty more picks](docs/more-picks.md) cover health and biotech, energy and climate, fintech, consumer products, global founders, developer tools, and Sunday hackathons. [Planning notes](docs/planning.md) help choose a useful mix without overbooking.

### Official curated tracks

{official_tracks}

The standalone Deep Tech and Hack Week pages can mix SF and LA events or spill beyond the week. The snapshot here is limited to listings starting October 5–11 on the SF calendar.

### Keyword indexes

These are transparent searches of public event titles, not official classifications. They overlap and can miss relevant events.

| Index | Title matches |
| --- | ---: |
{chr(10).join(topic_rows)}

## Search locally

No dependencies beyond Python 3.10+.

```sh
python3 scripts/search.py --date 2026-10-07 --query agents
python3 scripts/search.py --query climate --json
python3 scripts/search.py --query "happy hour" --area SOMA
```

## Data, privacy, and updates

The full catalog preserves public event titles, start dates/times, general areas, calendar labels, and canonical official detail links. It omits attendee data, personal contact details, private locations, host profiles, account information, and tracking/redirect tokens. Public event titles can name publicly billed speakers; there are no separate people or contact records.

The supplied HTML, browser exports, and raw source pages are not included. Unknown times and prices stay unknown. The full catalog was checked against the official calendar; only the ten starting picks and the explicitly labeled additional organizer pages had individual registration-page checks.

[Source and coverage notes](docs/methodology.md) · [Data schema](docs/data-schema.md) · [Contribute a correction](CONTRIBUTING.md)

```sh
python3 scripts/validate.py
python3 scripts/build.py
```

This is a dated snapshot. CI validates the data and generated guide; it does not refresh listings or check live ticket availability. Original prose and code use the [MIT license](LICENSE); event names and source materials belong to their respective owners.
"""
    write("README.md", readme)
    print(f"Built guide for {len(events):,} events across {len(counts)} days; {len(TOPICS)} keyword indexes.")


if __name__ == "__main__":
    main()
