# Contributing

Found a missing event, a changed time, or a broken link? Open an issue with a
public organizer or official-calendar link. A listing should be relevant to
SF Tech Week 2026, October 5–11, and have a publicly checkable date.

For a pull request:

1. Update the relevant record in `data/events.json`. Use the existing fields.
2. Cite the public source and record the date you checked it. Use `null` for
   unknown values; do not infer an end time, free admission, or an open RSVP.
3. Keep the source event ID when correcting an existing listing. Check both
   its registration URL and its title/date before adding a possible duplicate.
4. Run `python3 scripts/build.py` and `python3 scripts/validate.py`.
5. Include the regenerated CSV, day lists, topic lists, and README in the PR.

The JSON is the source of truth for generated files. Editorial picks live in
`data/picks.json`. Clearly label a community suggestion that is not on the
official calendar. Do not present a suggestion as an official Tech Week event.

Only include public event facts. Do not add attendee lists, RSVP confirmations,
personal contact details, personal profiles, private venue addresses, calendar
invitation tokens, browser exports, or analytics/referral parameters. Public
event titles may contain a publicly billed speaker's name; do not create
separate records about people. Use organizations for host fields.

No registration, payment, attendance, or invitation is arranged by this repo.
Corrections take priority over promotional copy. Organizers can request a
correction or removal through an issue without providing private information.
