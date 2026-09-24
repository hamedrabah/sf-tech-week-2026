# Subscribe or download calendars

[Guide](../README.md) · [Choose a calendar](https://hamedrabah.github.io/sf-tech-week-2026/)

Choose the original ten, a themed collection, a single day, or the full catalog.
Start with a smaller feed: the full catalog contains more than 1,700 entries.
These calendars help you discover events. **Apply separately; an entry does not
confirm admission, reserve a place, or provide a ticket.**

| Feed | Subscription / download URL |
| --- | --- |
| Original ten | [top-10.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/top-10.ics) |
| Full catalog | [all-events.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/all-events.ics) |
| Monday, October 5 | [2026-10-05.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/days/2026-10-05.ics) |
| Tuesday, October 6 | [2026-10-06.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/days/2026-10-06.ics) |
| Wednesday, October 7 | [2026-10-07.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/days/2026-10-07.ics) |
| Thursday, October 8 | [2026-10-08.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/days/2026-10-08.ics) |
| Friday, October 9 | [2026-10-09.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/days/2026-10-09.ics) |
| Saturday, October 10 | [2026-10-10.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/days/2026-10-10.ics) |
| Sunday, October 11 | [2026-10-11.ics](https://hamedrabah.github.io/sf-tech-week-2026/calendars/days/2026-10-11.ics) |

The [calendar picker](https://hamedrabah.github.io/sf-tech-week-2026/) includes
every themed collection. Copy the HTTPS `.ics` URL, rather than the GitHub page
that displays the file.

## Subscribe

**Google Calendar:** use a computer browser. Next to **Other calendars**, choose
**+ → From URL**, paste the feed URL, then select **Add calendar**. The mobile
app cannot add a new URL subscription. [Google instructions](https://support.google.com/calendar/answer/37100).

**Apple Calendar on Mac:** choose **File → New Calendar Subscription**, paste
the feed URL, then select **Subscribe**. Choose iCloud as the location to make
the subscription available on your other devices. On iPhone or iPad, use
**Calendars → Add Calendar → Add Subscription Calendar** and enter the URL.
[Apple instructions](https://support.apple.com/en-us/102301).

Subscriptions can receive future repository updates. This is still a dated
snapshot, not an automatic sync with organizers. Calendar apps control refresh
timing, so updates may not appear immediately. Confirm details on the linked
organizer page before attending.

## Download a one-time copy

Save any `.ics` link above or in the calendar picker. In Google Calendar on a
computer, open **Settings → Import & export**, select the file, choose its
destination calendar, and import. A separate calendar makes the entries easier
to hide or remove. A file import is a one-time copy, not a subscription.
[Google import instructions](https://support.google.com/calendar/answer/37118).

## Timing and duplicate entries

All source times are Pacific. Feeds encode timed events in UTC so your calendar
can display them in its selected timezone. Most listings have no verified end
time: their feeds omit both an end and a duration. Under iCalendar rules these
are point events; an app may give them a visual default length. **That display
length is not a verified event duration.** Eight of the original ten have
verified end times. [iCalendar event rules](https://www.rfc-editor.org/rfc/rfc5545#section-3.6.1).

Claude Founder House uses its published multi-day window, not a claim of
continuous programming. Its cafe hours and the Google Engineering 10x timing
conflict remain in the event notes. Multi-day listings appear in the feed for
their starting day.

Every entry is marked tentative and free for busy-time calculations. The
feeds include no alarms, attendee lists, organizer contact records, private
addresses, or RSVP information. Location fields contain only the public area.

The same event keeps the same identifier and content across all feeds. Calendar
apps can still display copies when several subscribed calendars overlap. Choose
one broad feed or several non-overlapping themed collections; avoid importing
the same file repeatedly. Removing a subscription does not cancel any organizer
registration you made separately.

## Rebuild and verify

Run `python3 scripts/calendars.py` to regenerate the files. Feed content is
deterministic: event timestamps come from the source snapshot, not the build
clock. `DTSTAMP` and `LAST-MODIFIED` describe that snapshot, not the organizer's
own revision time. UIDs derive from official event IDs and remain stable when
titles or times change.

The exporter uses CRLF lines, UTF-8-safe folding at 75 octets, escaped text, and
explicit UTC times. Tests parse the feeds with the independent `icalendar`
package, check every source event's time, compare IDs across feeds, and cover
unknown ends, Unicode, delimiters, and accidental property injection.
[iCalendar format](https://www.rfc-editor.org/rfc/rfc5545).
