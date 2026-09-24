#!/usr/bin/env python3
"""Build public RFC 5545 discovery calendars using only reviewed event fields."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID
from zoneinfo import ZoneInfo

BASE_URL = "https://hamedrabah.github.io/sf-tech-week-2026"
PACIFIC = ZoneInfo("America/Los_Angeles")

# Reviewed links between the independent organizer checks and official listings.
# Keeping an explicit mapping avoids accidental matches between similar titles.
SEED_CATALOG_IDS = {
    "claude-founder-house": "5b9edb5a-cbc2-437a-9610-b17c2c26bbd5",
    "official-tech-week-kickoff": "affc8860-5de6-482b-97ed-7667718ab905",
    "capturing-value-intelligence": "a73bb032-f79e-45aa-9340-dc6d6a8c30b6",
    "speedrun-ai-faire": "70750ac4-237e-42a9-9b03-f9589abdae34",
    "deep-tech-investor-breakfast": "450fd0b7-12d3-420c-92dc-0634b984ac92",
    "match-house": "3b9cb867-dfaa-4642-9af3-ea75412d40a0",
    "camp-ai-production-ready-agents": "fa378e29-57e0-4583-aa85-56f4e4015894",
    "google-engineering-10x": "b8ad61d1-0cb8-4d07-bf6b-8aacafcb8c60",
    "nexxaworld": "9c04f81c-210d-4e7a-bba1-1637f862e8e3",
    "who-will-own-future": "7df29c71-1e55-44ef-8828-a9dfc26aa119",
}


def text_value(value):
    """Escape RFC 5545 TEXT, retaining Unicode and intentional newlines."""
    value = str(value).replace("\r\n", "\n").replace("\r", "\n")
    if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", value):
        raise ValueError("Calendar text contains a control character")
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace(";", "\\;").replace(",", "\\,")


def fold_line(line):
    """Fold UTF-8 at 75 octets, counting the continuation space in that limit."""
    if "\r" in line or "\n" in line:
        raise ValueError("Unescaped newline in content line")
    parts, current, size = [], "", 0
    for character in line:
        width = len(character.encode("utf-8"))
        if size + width > 75:
            parts.append(current)
            current, size = " ", 1
        current += character
        size += width
    parts.append(current)
    return "\r\n".join(parts)


def clean_url(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or re.search(r"[\s\x00-\x1f\x7f]", value)):
        raise ValueError("Expected a clean public HTTPS URL")
    return value


def parse_aware(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.utcoffset() is None:
        raise ValueError("Expected a timezone-aware source timestamp")
    return result


def utc_value(value):
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def catalog_start(event):
    if not event["start_time"]:
        raise ValueError(f"No known start time for {event['id']}; do not invent an all-day event")
    if event["timezone"] != "America/Los_Angeles":
        raise ValueError("Unexpected source timezone")
    return datetime.fromisoformat(event["date"] + "T" + event["start_time"]).replace(tzinfo=PACIFIC)


def map_seed_picks(events_by_id, picks):
    mapped = {}
    for pick in picks:
        event_id = SEED_CATALOG_IDS[pick["id"]]
        if event_id in mapped:
            raise ValueError("Duplicate seed event")
        event = events_by_id[event_id]
        if catalog_start(event) != parse_aware(pick["start"]):
            raise ValueError(f"Seed and catalog schedules differ: {pick['id']}")
        mapped[event_id] = pick
    return mapped


def event_lines(event, pick=None):
    """The same event is serialized identically in every feed containing it."""
    event_id = str(UUID(event["id"]))
    start = catalog_start(event)
    stamp = utc_value(parse_aware(event["checked_at"]))
    source_url = clean_url(event["source_url"])
    notes = [
        "Discovery listing. Apply separately with the organizer; admission is not confirmed.",
        "This calendar entry is not a ticket or invitation. Confirm the current time and venue before attending.",
        f"Official details: {source_url}",
        f"Calendar label at snapshot: {event['status_as_listed']}. This label is not an admission guarantee.",
        f"Source snapshot: {event['checked_at']}. This feed updates only when the repository is updated.",
    ]
    lines = ["BEGIN:VEVENT", f"UID:urn:uuid:{event_id}", f"DTSTAMP:{stamp}",
             f"LAST-MODIFIED:{stamp}", f"DTSTART:{utc_value(start)}"]
    end = parse_aware(pick["end"]) if pick and pick.get("end") else None
    if end:
        if end <= start:
            raise ValueError(f"Event ends before it starts: {event_id}")
        lines.append(f"DTEND:{utc_value(end)}")
        if end.astimezone(PACIFIC).date() != start.date():
            notes.append("Multi-day listing window; this does not mean continuous programming. Check the session agenda.")
    else:
        notes.append("End time is unknown in this guide. No end or duration is supplied; calendar apps may display this as a point event or apply their own visual default.")
    if event.get("neighborhood"):
        notes.append(f"General area from official calendar: {event['neighborhood']}. Area labels can differ from organizer pages; confirm the venue.")
        lines.append("LOCATION:" + text_value(event["neighborhood"] + " (general area; confirm venue)"))
    if pick:
        notes += [f"Application page: {clean_url(pick['url'])}", pick["reason_to_attend"],
                  f"Admission: {pick['admission']}. Price: {pick['cost']}."]
        if pick.get("notes"):
            notes.append(pick["notes"])
    lines += ["SUMMARY:" + text_value(event["title"]), "DESCRIPTION:" + text_value("\n\n".join(notes)),
              "URL:" + source_url, "STATUS:TENTATIVE", "TRANSP:TRANSPARENT", "END:VEVENT"]
    return lines


def calendar_bytes(name, description, rows, picks_by_id):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//SF Tech Week Community Guide//2026//EN",
             "CALSCALE:GREGORIAN", "X-WR-CALNAME:" + text_value(name),
             "X-WR-CALDESC:" + text_value(description), "X-WR-TIMEZONE:America/Los_Angeles"]
    for event in sorted(rows, key=lambda e: (e["date"], e["start_time"] or "99:99", e["id"])):
        lines.extend(event_lines(event, picks_by_id.get(event["id"])))
    lines.append("END:VCALENDAR")
    return ("\r\n".join(fold_line(line) for line in lines) + "\r\n").encode("utf-8")


def build_calendars(root, events, picks, collections):
    """Write feeds below docs/calendars; return a docs-relative feed manifest."""
    root = Path(root)
    by_id = {event["id"]: event for event in events}
    if len(by_id) != len(events) or not events:
        raise ValueError("Expected a non-empty catalog of unique event IDs")
    picks_by_id = map_seed_picks(by_id, picks)
    feeds = [("all-events", "SF Tech Week 2026 — all events", "All public catalog listings. Apply separately; admission is not confirmed.", "all-events.ics", events)]
    if picks:
        feeds.append(("top-10", "SF Tech Week 2026 — original ten", "The original ten picks, with independently checked organizer schedules and caveats.", "top-10.ics", [by_id[key] for key in picks_by_id]))
    for day in sorted({event["date"] for event in events}):
        feeds.append((day, f"SF Tech Week 2026 — {day}", "Listings starting this day. Multi-day events appear only on their starting day.", f"days/{day}.ics", [event for event in events if event["date"] == day]))
    collection_ids = set()
    for collection in sorted(collections, key=lambda c: c["id"]):
        slug = collection["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in collection_ids:
            raise ValueError("Collection IDs must be unique safe slugs")
        collection_ids.add(slug)
        ids = collection["event_ids"]
        if not ids or len(ids) != len(set(ids)) or not set(ids) <= set(by_id):
            raise ValueError(f"Invalid event membership for collection {slug}")
        feeds.append((slug, "SF Tech Week 2026 — " + collection["name"], collection["description"], f"collections/{slug}.ics", [by_id[key] for key in ids]))

    # Serialize every feed first, so validation errors cannot leave partial new output.
    rendered = [(feed, calendar_bytes(feed[1], feed[2], feed[4], picks_by_id)) for feed in feeds]
    destination = root / "docs" / "calendars"
    manifest = []
    for (feed_id, name, description, relative, rows), payload in rendered:
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        public_path = "calendars/" + relative
        manifest.append({"id": feed_id, "name": name, "description": description,
                         "path": public_path, "url": BASE_URL + "/" + public_path, "event_count": len(rows)})
    expected = {destination / feed[3] for feed in feeds}
    for obsolete in destination.rglob("*.ics"):
        if obsolete not in expected:
            obsolete.unlink()
    return manifest


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    load = lambda name: json.loads((root / "data" / name).read_text())
    collections_file = root / "data" / "collections.json"
    collections = load("collections.json") if collections_file.exists() else []
    if isinstance(collections, dict):
        collections = collections["collections"]
    manifest = build_calendars(root, load("events.json"), load("picks.json"), collections)
    print(f"Built {len(manifest)} calendar feeds; all-events has {manifest[0]['event_count']:,} listings.")
