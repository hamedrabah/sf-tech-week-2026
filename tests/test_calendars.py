"""Integration checks with an independent RFC 5545 parser (icalendar)."""
import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from calendars import SEED_CATALOG_IDS, build_calendars, calendar_bytes  # noqa: E402


class CalendarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.destination = Path(cls.temp.name)
        cls.events = json.loads((ROOT / "data/events.json").read_text())
        cls.picks = json.loads((ROOT / "data/picks.json").read_text())
        source = ROOT / "data/collections.json"
        cls.collections = json.loads(source.read_text()) if source.exists() else []
        if isinstance(cls.collections, dict):
            cls.collections = cls.collections["collections"]
        cls.manifest = build_calendars(cls.destination, cls.events, cls.picks, cls.collections)
        cls.payloads = {feed["path"]: (cls.destination / "docs" / feed["path"]).read_bytes() for feed in cls.manifest}
        cls.parsed = {path: Calendar.from_ical(raw) for path, raw in cls.payloads.items()}
        cls.all = cls.parsed["calendars/all-events.ics"]
        cls.by_uid = {str(event["UID"]): event for event in cls.all.walk("VEVENT")}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_source_counts_and_shared_identical_entries(self):
        self.assertEqual(len(self.by_uid), len(self.events))
        self.assertEqual(len(self.parsed["calendars/top-10.ics"].walk("VEVENT")), 10)
        expected_ids = {"urn:uuid:" + event["id"] for event in self.events}
        self.assertEqual(set(self.by_uid), expected_ids)
        days = {event["date"] for event in self.events}
        for day in days:
            actual = self.parsed[f"calendars/days/{day}.ics"].walk("VEVENT")
            self.assertEqual({str(event["UID"]) for event in actual},
                             {"urn:uuid:" + event["id"] for event in self.events if event["date"] == day})
        for collection in self.collections:
            actual = self.parsed[f"calendars/collections/{collection['id']}.ics"].walk("VEVENT")
            self.assertEqual({str(event["UID"]) for event in actual},
                             {"urn:uuid:" + event_id for event_id in collection["event_ids"]})
        for feed in self.manifest:
            calendar = self.parsed[feed["path"]]
            self.assertEqual(len(calendar.walk("VEVENT")), feed["event_count"])
            for event in calendar.walk("VEVENT"):
                self.assertEqual(event.to_ical(), self.by_uid[str(event["UID"])].to_ical())

    def test_every_source_time_round_trips_in_pacific(self):
        pacific = ZoneInfo("America/Los_Angeles")
        for source in self.events:
            event = self.by_uid["urn:uuid:" + source["id"]]
            actual = event.decoded("DTSTART")
            expected = datetime.fromisoformat(source["date"] + "T" + source["start_time"]).replace(tzinfo=pacific)
            self.assertEqual(actual.utcoffset().total_seconds(), 0)
            self.assertEqual(actual.astimezone(pacific), expected)
            checked = datetime.fromisoformat(source["checked_at"].replace("Z", "+00:00")).replace(microsecond=0)
            self.assertEqual(event.decoded("DTSTAMP"), checked)
            self.assertEqual(event.decoded("LAST-MODIFIED"), checked)
            self.assertEqual(str(event["SUMMARY"]), source["title"])
        kickoff = self.by_uid["urn:uuid:" + SEED_CATALOG_IDS["official-tech-week-kickoff"]]
        self.assertEqual(kickoff.decoded("DTSTART"), datetime(2026, 10, 6, 1, tzinfo=timezone.utc))

    def test_known_and_unknown_ends_preserve_source_caveats(self):
        known_ids = {SEED_CATALOG_IDS[pick["id"]]: pick for pick in self.picks if pick["end"]}
        self.assertEqual(len(known_ids), 8)
        for source in self.events:
            event = self.by_uid["urn:uuid:" + source["id"]]
            self.assertNotIn("DURATION", event)
            if source["id"] in known_ids:
                expected = datetime.fromisoformat(known_ids[source["id"]]["end"])
                self.assertEqual(event.decoded("DTEND"), expected)
            else:
                self.assertNotIn("DTEND", event)
                self.assertIn("End time is unknown", str(event["DESCRIPTION"]))
        claude = self.by_uid["urn:uuid:" + SEED_CATALOG_IDS["claude-founder-house"]]
        self.assertIn("not mean continuous programming", str(claude["DESCRIPTION"]))
        self.assertIn("11:00 AM", str(claude["DESCRIPTION"]))
        google = self.by_uid["urn:uuid:" + SEED_CATALOG_IDS["google-engineering-10x"]]
        self.assertIn("9:30 AM", str(google["DESCRIPTION"]))
        self.assertIn("9:00 AM", str(google["DESCRIPTION"]))

    def test_crlf_utf8_folding_and_parser_round_trip(self):
        for path, payload in self.payloads.items():
            self.assertTrue(payload.endswith(b"\r\n"), path)
            remainder = payload.replace(b"\r\n", b"")
            self.assertNotIn(b"\n", remainder, path)
            self.assertNotIn(b"\r", remainder, path)
            for line in payload.split(b"\r\n"):
                self.assertLessEqual(len(line), 75, path)
                line.decode("utf-8")  # Never split a multibyte character.
            calendar = self.parsed[path]
            reparsed = Calendar.from_ical(calendar.to_ical())
            self.assertEqual(len(reparsed.walk("VEVENT")), len(calendar.walk("VEVENT")))
            self.assertFalse(calendar.errors, path)

    def test_unicode_escaping_and_newline_cannot_create_properties(self):
        event = copy.deepcopy(self.events[0])
        title = 'Café 🤝 東京 ' * 18 + ', semicolon; slash\\\nBEGIN:VALARM\nACTION:DISPLAY'
        event["title"] = title
        event["private_guests"] = ["SHOULD_NOT_BE_EXPORTED"]
        event["email"] = "SHOULD_NOT_BE_EXPORTED"
        payload = calendar_bytes("Test", "comma, semi; backslash\\\nsecond line", [event], {})
        parsed = Calendar.from_ical(payload)
        self.assertEqual(str(parsed.walk("VEVENT")[0]["SUMMARY"]), title)
        self.assertEqual(len(parsed.walk("VEVENT")), 1)
        self.assertEqual(parsed.walk("VALARM"), [])
        self.assertNotIn(b"SHOULD_NOT_BE_EXPORTED", payload)
        for line in payload.split(b"\r\n"):
            self.assertLessEqual(len(line), 75)
            line.decode("utf-8")

    def test_discovery_semantics_and_no_private_calendar_properties(self):
        for event in self.all.walk("VEVENT"):
            self.assertEqual(str(event["STATUS"]), "TENTATIVE")
            self.assertEqual(str(event["TRANSP"]), "TRANSPARENT")
            self.assertIn("Apply separately", str(event["DESCRIPTION"]))
            for forbidden in ["ATTENDEE", "ORGANIZER", "CONTACT", "GEO", "ATTACH"]:
                self.assertNotIn(forbidden, event)
            self.assertEqual(event.walk("VALARM"), [])
            self.assertTrue(str(event["URL"]).startswith("https://www.tech-week.com/calendar/sf/events/"))

    def test_deterministic_regeneration_and_stale_feed_cleanup(self):
        stale = self.destination / "docs/calendars/collections/removed.ics"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_bytes(b"outdated generated feed")
        result = build_calendars(self.destination, list(reversed(self.events)), self.picks, list(reversed(self.collections)))
        self.assertEqual(result, self.manifest)
        self.assertFalse(stale.exists())
        for path, payload in self.payloads.items():
            self.assertEqual((self.destination / "docs" / path).read_bytes(), payload)

    def test_rejects_unsafe_links_missing_time_and_wrong_seed_mapping(self):
        event = copy.deepcopy(self.events[0])
        for url in [event["source_url"] + "?invite_token=private", "https://example.com/\nATTENDEE:x", "http://example.com"]:
            event["source_url"] = url
            with self.assertRaises(ValueError):
                calendar_bytes("Test", "Test", [event], {})
        event = copy.deepcopy(self.events[0])
        event["start_time"] = None
        with self.assertRaises(ValueError):
            calendar_bytes("Test", "Test", [event], {})
        picks = copy.deepcopy(self.picks)
        picks[0]["start"] = "2026-10-06T09:00:00-07:00"
        with self.assertRaises(ValueError):
            build_calendars(self.destination, self.events, picks, [])
        with self.assertRaises(ValueError):
            build_calendars(self.destination, self.events, self.picks,
                            [{"id": "../escape", "name": "Invalid", "description": "Invalid", "event_ids": [self.events[0]["id"]]}])


if __name__ == "__main__":
    unittest.main()
