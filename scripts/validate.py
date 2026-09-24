#!/usr/bin/env python3
"""Validate provenance, date/time fields, duplicates, and accidental private data."""
import csv
import json
import re
import hashlib
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
errors = []


def require(ok, message):
    if not ok:
        errors.append(message)


def check_url(url, where, official=False):
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and bool(parsed.hostname), f"Invalid HTTPS URL: {where}")
    require(not parsed.username and not parsed.password and not parsed.query and not parsed.fragment,
            f"URL contains credentials, query parameters, or fragment: {where}")
    if official:
        require(parsed.hostname == "www.tech-week.com" and parsed.path.startswith("/calendar/sf/events/"),
                f"Expected canonical SF event detail URL: {where}")


events = json.loads((ROOT / "data/events.json").read_text())
meta = json.loads((ROOT / "data/metadata.json").read_text())
picks = json.loads((ROOT / "data/picks.json").read_text())
more = json.loads((ROOT / "data/more-picks.json").read_text())
tracks = json.loads((ROOT / "data/tracks.json").read_text())
collections = json.loads((ROOT / "data/collections.json").read_text())
brands = json.loads((ROOT / "data/brands.json").read_text())
allowed = {"id", "title", "date", "start_time", "timezone", "neighborhood", "status_as_listed", "source_url", "checked_at"}
seen_ids, seen_urls = set(), set()
for index, event in enumerate(events):
    label = f"event {index} ({event.get('id')})"
    require(set(event) == allowed, f"Unexpected/missing fields in {label}")
    require(event['id'] not in seen_ids, f"Duplicate id: {label}")
    require(event['source_url'] not in seen_urls, f"Duplicate source URL: {label}")
    seen_ids.add(event['id'])
    seen_urls.add(event['source_url'])
    require(bool(event['title'].strip()), f"Empty title: {label}")
    try:
        d = date.fromisoformat(event['date'])
        require(date(2026, 10, 5) <= d <= date(2026, 10, 11), f"Outside week: {label}")
        if event['start_time'] is not None:
            require(bool(re.fullmatch(r"\d{2}:\d{2}", event['start_time'])), f"Time format: {label}")
            datetime.strptime(event['start_time'], "%H:%M")
        datetime.fromisoformat(event['checked_at'].replace('Z', '+00:00'))
    except ValueError:
        errors.append(f"Invalid date/time: {label}")
    require(event['timezone'] == 'America/Los_Angeles', f"Unexpected timezone: {label}")
    check_url(event['source_url'], label, official=True)
    require(event['source_url'].endswith(event['id']), f"ID and source URL differ: {label}")

require(len(events) == meta['captured_events'], 'Metadata captured count differs from data')
require(dict(Counter(e['date'] for e in events)) == meta['day_counts'], 'Metadata day counts differ from data')
require(meta['captured_events'] + meta['outside_week_excluded'] == meta['official_calendar_total'], 'Coverage counts do not reconcile')
require(len(picks) == 10 and {p['seed_rank'] for p in picks} == set(range(1, 11)), 'Expected original ten picks')
pick_fields = {'id', 'title', 'seed_rank', 'url', 'start', 'end', 'timezone', 'city', 'venue', 'organizers', 'tags', 'admission', 'cost', 'reason_to_attend', 'notes', 'verification'}
for pick in picks:
    require(set(pick) == pick_fields, f"Unexpected/missing pick fields: {pick.get('id')}")
    require(set(pick['verification']) == {'checked_at', 'source_url', 'method', 'verified_fields', 'limits'}, f"Unexpected verification fields: {pick['id']}")
    check_url(pick['url'], pick['id'])
    start = datetime.fromisoformat(pick['start'])
    require(start.utcoffset().total_seconds() == -7 * 3600, f"Pick timezone: {pick['id']}")
    if pick['end']:
        require(datetime.fromisoformat(pick['end']) > start, f"Pick ends before it starts: {pick['id']}")
    require(pick['cost'] == 'Not published', f"Review newly asserted price: {pick['id']}")
    require(pick['admission'] == 'Application / approval', f"Review newly asserted admission: {pick['id']}")

more_fields = {'name', 'host', 'date', 'start', 'end', 'neighborhood', 'themes', 'why', 'source_url', 'registration_url', 'registration_verified', 'verification_note', 'practical_note', 'official_listing_url', 'canonical_url', 'official_event_id'}
by_id = {e['id']: e for e in events}
for pick in more:
    require(set(pick) <= more_fields, f"Unexpected extra-pick fields: {pick.get('name')}")
    event = by_id.get(pick.get('official_event_id'))
    require(event is not None, f"Extra pick missing catalog match: {pick.get('name')}")
    if event:
        require((pick['date'], pick['start'], pick['canonical_url']) == (event['date'], event['start_time'], event['source_url']), f"Extra pick disagrees with catalog: {pick['name']}")
for track in tracks:
    require(set(track) <= {'name', 'url', 'note', 'related_url'}, f"Unexpected track fields: {track.get('name')}")

require(set(collections) == {'method', 'collections'}, 'Unexpected collection bundle fields')
members = []
slugs = set()
for collection in collections['collections']:
    require(set(collection) == {'id', 'name', 'description', 'event_ids'}, f"Unexpected collection fields: {collection.get('id')}")
    require(bool(re.fullmatch(r'[a-z0-9-]+', collection['id'])), 'Invalid collection slug')
    require(collection['id'] not in slugs, 'Duplicate collection slug')
    require(bool(collection['event_ids']), f"Empty collection: {collection['id']}")
    slugs.add(collection['id'])
    members.extend(collection['event_ids'])
require(len(members) == len(set(members)) == len(events), 'Collections must contain every event exactly once')
require(set(members) == seen_ids, 'Collection IDs differ from catalog')
brand_fields = {'pick_id', 'name', 'asset', 'source_url', 'source_asset_url', 'license_note', 'checked_at', 'asset_kind', 'preparation', 'sha256', 'alternate_asset', 'alternate_source_asset_url', 'alternate_usage', 'fallback_reason'}
require({b['pick_id'] for b in brands} == {p['id'] for p in picks}, 'Brand mapping does not cover the ten')
for brand in brands:
    require(set(brand) <= brand_fields, f"Unexpected brand fields: {brand.get('name')}")
    if brand['asset']:
        asset = ROOT / brand['asset']
        require(asset.is_file(), f"Missing logo: {brand['asset']}")
        if asset.is_file():
            require(hashlib.sha256(asset.read_bytes()).hexdigest() == brand['sha256'], f"Logo changed without a source update: {brand['asset']}")


def walk_json(value, where):
    if isinstance(value, dict):
        for key, item in value.items():
            require(key.casefold() not in {'email', 'phone', 'address', 'attendees', 'guests', 'profile', 'user', 'account', 'token'}, f"Private-data field in {where}: {key}")
            if (key == 'url' or key.endswith('_url')) and item is not None:
                check_url(item, f'{where}.{key}')
            walk_json(item, f'{where}.{key}')
    elif isinstance(value, list):
        for index, item in enumerate(value):
            walk_json(item, f'{where}[{index}]')


for path in (ROOT / 'data').glob('*.json'):
    walk_json(json.loads(path.read_text()), path.name)

# Catch accidental email exports, credentials, local paths, or private guest data.
# Public event titles may mention publicly announced people; this is not named-entity detection.
private_patterns = [
    (r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "email address"),
    (r"/(?:Users|home)/[^/\s]+", "local home path"),
    (r"\b(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_]+", "credential-shaped value"),
    (r"\b(?:utm_source|utm_campaign|invite_token|access_token|auth_token)=", "tracking or invitation parameter"),
    (r"(?<!\w)(?:\+1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\w)", "phone-shaped value"),
]
for path in ROOT.rglob('*'):
    if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts or path.suffix == '.pyc':
        continue
    rel = str(path.relative_to(ROOT))
    require(path.suffix.lower() not in {'.html', '.har', '.eml', '.mbox'} or rel == 'docs/index.html', f"Raw export must not be published: {rel}")
    if path.suffix in {'.json', '.csv', '.md', '.yml', '.svg', '.html', '.ics'} or path.name == 'LICENSE':
        content = path.read_text()
        for pattern, reason in private_patterns:
            scan_content = content
            if path.suffix == '.svg' and reason == 'phone-shaped value':
                try:
                    # Decimal vector coordinates can resemble telephone numbers.
                    scan_content = ' '.join(ET.fromstring(content).itertext())
                except ET.ParseError:
                    pass
            require(not re.search(pattern, scan_content, re.I), f"Possible {reason} in {rel}")
        if path.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', content):
                if not urlsplit(target).scheme and not target.startswith('#'):
                    require((path.parent / target.split('#')[0]).exists(), f"Broken local link in {rel}: {target}")
            for target in re.findall(r'(?:src|href)="([^"]+)"', content):
                if not urlsplit(target).scheme and not target.startswith('#'):
                    require((path.parent / target.split('#')[0]).exists(), f"Broken HTML link in {rel}: {target}")
        if path.suffix == '.svg':
            try:
                xml = ET.fromstring(content)
                for el in xml.iter():
                    require(el.tag.split('}')[-1] not in {'script', 'foreignObject'}, f"Unsafe SVG element in {rel}")
                    require(not any(k.lower().startswith('on') for k in el.attrib), f"Inline SVG handler in {rel}")
                    for key, value in el.attrib.items():
                        if key.split('}')[-1] == 'href':
                            require(value.startswith(('#', 'data:image/png;base64,', 'data:image/jpeg;base64,')), f"External SVG asset in {rel}")
            except ET.ParseError:
                errors.append(f'Invalid SVG: {rel}')

csv_path = ROOT / 'data/events.csv'
if csv_path.exists():
    rows = list(csv.DictReader(csv_path.open()))
    require(len(rows) == len(events), 'CSV row count differs from JSON')
    require({r['id'] for r in rows} == seen_ids, 'CSV ids differ from JSON')

if errors:
    raise SystemExit('Validation failed:\n' + '\n'.join(f'- {e}' for e in errors))
print(f"Validated {len(events):,} unique official listings and {len(picks)} seed picks; privacy-pattern scan passed.")
