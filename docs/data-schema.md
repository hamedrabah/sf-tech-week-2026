# Data schema

[Guide](../README.md) · [Methodology](methodology.md)

`data/events.json` is a JSON array with one record per distinct official event
detail URL. `data/events.csv` contains the same fields. Records are sorted by
start date/time and title. All source links are canonical public event detail
pages; open them to reach the current organizer registration route.

| Field | Meaning |
| --- | --- |
| `id` | Stable identifier from the official event detail URL. |
| `title` | Public event title as listed; whitespace normalized. |
| `date` | Starting date in `YYYY-MM-DD`. |
| `start_time` | Listed local start time in 24-hour `HH:MM`, or `null`. |
| `timezone` | `America/Los_Angeles` (PDT, UTC−07:00 during this week). |
| `neighborhood` | Public general area label; may refer to another Bay Area city. `null` means not listed. |
| `status_as_listed` | Label exposed by the calendar. `Unspecified` means no explicit label was captured. It is not a claim of open admission. |
| `source_url` | Canonical official event page used for attribution and current details. |
| `checked_at` | ISO timestamp of the calendar snapshot. It is not a timestamp of an individual organizer-page check. |

The full catalog deliberately has no end times, prices, exact addresses, or
admission guarantees because the calendar table does not establish them.
Separately listed sessions retain their own official IDs, even when their
titles are similar. A multi-day event appears once, on its starting day.

`data/picks.json` contains the ten starting recommendations. It adds separately
checked start/end timestamps, organization names, public venue names when
verified, admission and cost labels, original editorial reasons, and per-row
verification limits. An unknown end is `null`; an unpublished price stays
`Not published`. A multi-day date range does not mean continuous programming.

`data/more-picks.json` contains twenty editorial additions. `canonical_url`,
where present, links the selection to its official event page. A direct
`registration_url` is only labeled independently checked when
`registration_verified` is `true`. A resolved link alone is not a check of the
page's contents. Theme labels in these picks are editorial.

`data/tracks.json` points to official curated tracks. Generated keyword indexes
are separate from these tracks: their regular expressions are published in
each index and in `scripts/build.py`.

CSV cells starting with spreadsheet formula characters are prefixed with a
single quote for safer spreadsheet import. JSON retains the original text.
