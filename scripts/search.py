#!/usr/bin/env python3
"""Search the public snapshot without dependencies or network calls."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--date", help="Starting date, YYYY-MM-DD")
parser.add_argument("--query", default="", help="Case-insensitive title substring")
parser.add_argument("--area", default="", help="Case-insensitive area substring")
parser.add_argument("--json", action="store_true", help="Return machine-readable results")
args = parser.parse_args()
events = json.loads((Path(__file__).resolve().parents[1] / "data/events.json").read_text())
matches = sorted((e for e in events if (not args.date or e['date'] == args.date)
                  and args.query.casefold() in e['title'].casefold()
                  and args.area.casefold() in (e['neighborhood'] or '').casefold()),
                 key=lambda e: (e['date'], e['start_time'] or '99:99', e['title']))
if args.json:
    print(json.dumps(matches, ensure_ascii=False, indent=2))
else:
    print(f"{len(matches)} matches. All times Pacific; check the organizer before attending.\n")
    for e in matches:
        print(f"{e['date']} {e['start_time'] or 'TBA'} | {e['title']} | {e['neighborhood'] or 'Area unspecified'}")
        print(e['source_url'])
