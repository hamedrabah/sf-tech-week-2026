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

from categorize import build_collections
from calendars import build_calendars
from visuals import build_visuals
from presentation import build_presentation


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
    bundle = build_collections(events)
    collections = bundle['collections']
    write('data/collections.json', json.dumps(bundle, ensure_ascii=False, indent=2))
    by_id = {e['id']: e for e in events}
    index = ['# Find your room', '', '[Guide](../README.md) · [Calendar desk](https://hamedrabah.github.io/sf-tech-week-2026/)', '', bundle['method'], '', '| Collection | Events | What you will find |', '| --- | ---: | --- |']
    for collection in collections:
        rows = [by_id[i] for i in collection['event_ids']]
        rows.sort(key=lambda e: (e['date'], e['start_time'] or '99:99', e['title'].casefold()))
        slug, title = collection['id'], collection['name']
        feed = f'https://hamedrabah.github.io/sf-tech-week-2026/calendars/collections/{slug}.ics'
        index.append(f"| [{esc(title)}](collections/{slug}.md) | {len(rows)} | {esc(collection['description'])} |")
        write(f'docs/collections/{slug}.md', f"# {title}\n\n[Guide](../../README.md) · [All collections](../collections.md) · [Subscribe / export](https://hamedrabah.github.io/sf-tech-week-2026/#{slug}) · [Download .ics]({feed})\n\n{collection['description']}\n\n**{len(rows)} events.** One editorial primary collection per event, based on public titles. Check the organizer for full details. All times Pacific.\n\n" + event_table(rows, True))
    write('docs/collections.md', '\n'.join(index))
    # Remove the superseded generated keyword indexes after replacing their links.
    for legacy in (ROOT / 'docs/topics').glob('*.md'):
        legacy.unlink()
    write('docs/tracks.md', '# Official curated tracks\n\n[Guide](../README.md) · [Our collections](collections.md)\n\nThese are the official calendar tracks. Our finer collections are a separate editorial classification.\n\n' + '\n'.join(f"- [{t['name']}]({t['url']})" for t in tracks))
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
    seed_doc = ["# The shortlist", "", "[Guide](../README.md)", "", "These ten came from the starting shortlist. The order preserves that shortlist; it is not a ranking of the full calendar. Public registration pages were checked September 23, 2026 (Pacific). All ten showed application/approval. No explicit price was verified for any of them."]
    for p in sorted(picks, key=lambda p: p['seed_rank']):
        seed_doc += ["", f'<a id="{p["id"]}"></a>', "", f"## {p['seed_rank']}. {p['title']}", "", f"**{pick_time(p)} PT.** [Public listing / apply]({p['url']}).", "", p['reason_to_attend'], "", f"Admission: {p['admission']}. Price: {p['cost']}."]
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
    build_calendars(ROOT, events, picks, collections)
    build_visuals(ROOT, picks, load('brands.json'), len(events), len(collections))
    build_presentation(ROOT, events, picks, collections, meta, counts, day, pick_time)
    print(f"Built guide for {len(events):,} events, {len(collections)} collections, and {len(collections) + 9} calendar feeds.")



if __name__ == "__main__":
    main()
