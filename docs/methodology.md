# Sources, coverage, and limits

[Guide](../README.md) · [Data schema](data-schema.md)

## What this snapshot covers

The [official SF Tech Week calendar](https://www.tech-week.com/calendar/sf)
advertises **October 5–11, 2026**. At **September 23, 2026, 8:24 PM Pacific**
(September 24, 03:24 UTC), its unfiltered view contained 1,716 listings. This
repository captures every one of the **1,713 listings starting during that
week**, including entries labeled closed, full, or waitlist.

| Date | Listings |
| --- | ---: |
| October 5 | 203 |
| October 6 | 395 |
| October 7 | 438 |
| October 8 | 398 |
| October 9 | 161 |
| October 10 | 85 |
| October 11 | 33 |
| Total | 1,713 |

The remaining three official listings are outside the advertised week and are
excluded from the dataset and counts:

- October 12: [Build AI agents that own their inference](https://www.tech-week.com/calendar/sf/events/build-ai-agents-that-own-their-inference-5a4cd286-92d3-4d62-9055-853d8faa1fc7).
- October 16: [How We Found Our Way Into AI](https://www.tech-week.com/calendar/sf/events/how-we-found-our-way-into-ai-328bf3da-fcf2-45e7-8537-8ca6cc1adcd3).
- October 28: [The Quantum Portfolio](https://www.tech-week.com/calendar/sf/events/the-quantum-portfolio-576a08f1-86e2-4ff0-abe8-aa414d221d64).

This is comprehensive coverage of that public calendar at that moment. It is
not a claim to cover every unofficial gathering or private invitation in the
Bay Area. Later additions and edits require a new snapshot.

## How it was collected

The public calendar was read through its rendered table. Each day was loaded
through the end of its infinite-scroll list; the results were reconciled with
the unfiltered total. Featured-only filtering was off and closed entries were
included. Records were deduplicated by the stable ID in the canonical official
event URL. Different official IDs are retained even when titles are similar.

Only table-visible facts were copied: title, starting date/time, general area,
availability label, and official detail link. Whitespace was normalized.
Opaque registration redirects were replaced with clean event detail URLs.
Host columns were omitted from the full catalog to avoid collecting individual
host identities. No login or private registration data was used.

At the snapshot, 17 entries were labeled **Closed**, 4 **Full**, and 16
**Waitlist**. The other 1,676 had no explicit availability label and are marked
**Unspecified**. A missing label does not mean open admission. Promotional
words such as "free" in an event title remain the organizer's claim, not a
separately verified ticket price. Featured badges are not admission labels.

## What was checked individually

The ten starting picks were checked against their unauthenticated public
Partiful pages on September 23. Every page showed application/approval. No
explicit price was verified. Two descriptions disagree with their header
start times, and two events publish no end time; the [pick notes](seed-picks.md)
retain those limits.

Twenty additional editorial picks were checked against official calendars or
curated tracks and matched to their exact catalog IDs, dates, and start times.
Only those labeled **Organizer page checked** in [the expanded shortlist](more-picks.md)
also had their direct organizer-page contents read. Resolving a registration
link is not equivalent to checking its contents or availability.

Calendar area labels and organizer pages sometimes disagree. In the seed
checks, the investor breakfast, MATCH HOUSE, and Who Will Own the Future? had
different neighborhood labels between sources. Catalog areas preserve the
calendar's labels; use the location in your current organizer confirmation for
travel. Exact addresses are intentionally absent.

## Editorial choices and reuse

The original ten's order is preserved, not extended into a ranking of all
events. Reasons to attend and planning suggestions are original editorial
judgments. Official curated tracks are linked directly. The guide's 36 finer
collections assign each event one primary home according to its public title's
topic, audience, or format. Deterministic rules and reviewed title overrides
are published in `scripts/categorize.py`. The result is a more balanced browsing
index, without adding unrelated entries to fill quotas. Categories are editorial
inferences, not official tags or quality rankings. Broad or opaque titles remain
in a general discovery collection.

No source descriptions, event photographs, guest lists, personal contact details, host
profiles, RSVP confirmations, local file paths, or browser exports are
published. Public event titles may include publicly billed speakers. Source
event names and trademarks remain their owners' property. Verified organization
logos are used for editorial identification with [source credits](asset-credits.md).
The cover and event-card layouts are original vector artwork. The MIT license
covers the repository's original prose and code, not third-party source
material. Every catalog record links back to its public source.

## Refreshing the guide

Check the public calendar again with all filters cleared, include closed
events, and load every day completely. Keep only starts within the intended
week and reconcile the count, documenting any exclusions. Update
`data/events.json`, the snapshot metadata, and any curated records affected by
changes. Use current public organizer pages when changing admission, prices,
or end times. Run the build and validator described in [Contributing](../CONTRIBUTING.md).

There is no background scraper or availability monitor. CI checks data
structure, clean links, dates, duplicates, source references, local links,
privacy patterns, and generated-file consistency. Pattern checks supplement
human review; they cannot prove that arbitrary new text contains no personal
information.
