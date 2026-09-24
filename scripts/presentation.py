"""GitHub-native editorial layout and a small public calendar subscription page."""
from html import escape
import json

SITE = 'https://hamedrabah.github.io/sf-tech-week-2026'
REPO = 'https://github.com/hamedrabah/sf-tech-week-2026'


def build_presentation(root, events, picks, collections, meta, counts, day, pick_time):
    cards = ['<table>']
    for i, pick in enumerate(sorted(picks, key=lambda p:p['seed_rank'])):
        if i % 2 == 0: cards.append('<tr>')
        asset = f"assets/cards/{pick['seed_rank']:02d}-{pick['id']}.svg"
        alt = escape(f"{pick['seed_rank']:02d}. {pick['title']} · {pick_time(pick)} PT · Application required", quote=True)
        cards.append(f'<td width="50%" valign="top"><a href="{pick["url"]}"><img src="{asset}" width="100%" alt="{alt}"></a><br><a href="{pick["url"]}">Apply ↗</a> · <a href="docs/seed-picks.md#{pick["id"]}">Details &amp; timing</a></td>')
        if i % 2 == 1: cards.append('</tr>')
    cards.append('</table>')
    collection_rows = []
    half = (len(collections) + 1) // 2
    for i in range(half):
        row = []
        for n in (i, i+half):
            if n < len(collections):
                c = collections[n]
                row += [f"[{c['name']}](docs/collections/{c['id']}.md)",str(len(c['event_ids']))]
            else: row += ['','']
        collection_rows.append('| ' + ' | '.join(row) + ' |')
    days_table = '\n'.join(f"| [{day(date)}](docs/days/{date}.md) | {counts[date]:,} | [Calendar]({SITE}/calendars/days/{date}.ics) |" for date in sorted(counts))
    size_min = min(len(c['event_ids']) for c in collections)
    size_max = max(len(c['event_ids']) for c in collections)
    readme = f"""<p align="center"><img src="assets/cover.svg" width="100%" alt="The SF Edit — San Francisco Tech Week, October 5–11, 2026. Ten selected rooms, {len(events):,} public listings, {len(collections)} focused collections."></p>

<p align="center"><b>THE SHORTLIST. THE CITY. YOUR WEEK.</b></p>
<p align="center"><a href="#the-shortlist">The ten</a> · <a href="#find-your-room">Collections</a> · <a href="{SITE}/">Subscribe to a calendar</a> · <a href="docs/all-events.md">All events</a></p>

A considered edit of SF Tech Week. Start with ten selected rooms, then explore **{len(collections)} focused collections** across the full **{len(events):,}-event** calendar. October 5–11, 2026. San Francisco and the Bay Area. All times Pacific.

## The shortlist

Ten picks for founders, builders, investors, and operators. Each links directly to the organizer's application. All ten require approval; the investor breakfast is invite-only. Selection is editorial, and admission remains with the host.

{chr(10).join(cards)}

<p align="center"><a href="{SITE}/#top-10"><b>Subscribe to the shortlist →</b></a> · <a href="{SITE}/calendars/top-10.ics">Download the ten (.ics)</a> · <a href="docs/seed-picks.md">Read the selection notes</a></p>

<sub>*Claude's daily café description begins at 11 AM despite its 8 AM event header; Google's description mentions 9 AM despite its 9:30 AM header. Confirm arrival with the host. The breakfast and NexxaWorld publish no end time. Prices are unconfirmed.</sub>

## Find your room

Smaller collections, each with its own list and calendar. Every event has one primary home; collections currently hold **{size_min}–{size_max} events**. Placement follows the public title's topic, audience, or format and is editorial, not an organizer classification.

| Collection | Events | Collection | Events |
| --- | ---: | --- | ---: |
{chr(10).join(collection_rows)}

[Browse collection descriptions](docs/collections.md) · [Explore twenty more picks](docs/more-picks.md) · [Official curated tracks](docs/tracks.md)

## Put it on your calendar

**[Open the calendar desk →]({SITE}/)**

Choose the ten, a collection, a single day, or the full week. Subscribe for future revisions to this guide, or download an `.ics` file for a one-time import into Apple Calendar, Google Calendar, Outlook, and other calendar apps.

| Feed | Subscribe / copy URL | Export |
| --- | --- | --- |
| The shortlist · 10 events | [Calendar desk]({SITE}/#top-10) | [Download .ics]({SITE}/calendars/top-10.ics) |
| Your interests · {len(collections)} collections | [Choose a collection]({SITE}/#collections) | Each collection has an export |
| A single day | [Choose a day]({SITE}/#days) | Each day has an export |
| The full week · {len(events):,} events | [Calendar desk]({SITE}/#all-events) | [Download .ics]({SITE}/calendars/all-events.ics) |

Feeds are a planning aid, not tickets or attendance confirmations. Most catalog entries only publish a start time; their calendar entries do not invent a duration. Subscribers receive revisions when this repository is updated, on their app's refresh schedule. [Calendar setup and limitations](docs/calendar.md).

## Follow the week

| Day | Events | Export |
| --- | ---: | --- |
{days_table}

Multi-day listings appear on their starting day. Check the actual location before pairing events; the calendar extends beyond San Francisco. [Plan your week](docs/planning.md).

<details>
<summary><b>Data, sources, and contribution notes</b></summary>

Snapshot: **{meta['checked_at_display']}**. {meta['coverage_summary']} Individual organizer pages were checked for the ten and the explicitly labeled additional picks. Open the [official calendar](https://www.tech-week.com/calendar/sf) for new listings.

[CSV](data/events.csv) · [JSON](data/events.json) · [Source notes](docs/methodology.md) · [Data schema](docs/data-schema.md) · [Contribute](CONTRIBUTING.md) · [Visual credits](docs/asset-credits.md)

Public event facts only. No personal contacts, attendee records, private addresses, RSVP confirmations, source HTML, or account data. Publicly billed names can remain in event titles. Organization marks identify the selected events; they do not imply endorsement. This is an independent guide, unaffiliated with a16z or Tech Week.

```sh
python3 scripts/search.py --collection agents-and-automation
python3 scripts/search.py --date 2026-10-07 --query agents
python3 scripts/build.py
python3 scripts/validate.py
```

Original prose, layouts, and code use the [MIT license](LICENSE). Third-party marks and source materials retain their owners' rights. CI validates the guide and calendars; it does not check ticket availability or automatically refresh the official calendar.

</details>
"""
    (root/'README.md').write_text(readme)
    feeds = [dict(id='top-10',label='The shortlist',count=10,path='top-10.ics',type='The edit',description='Ten selected rooms. The simplest place to start.'),
             dict(id='all-events',label='The full week',count=len(events),path='all-events.ics',type='Full directory',description='Every listing in the guide. Best kept in a separate calendar.')]
    feeds += [dict(id=c['id'],label=c['name'],count=len(c['event_ids']),path=f"collections/{c['id']}.ics",type='Collection',description=c['description']) for c in collections]
    feeds += [dict(id=date,label=day(date),count=counts[date],path=f'days/{date}.ics',type='Day',description='A single day of SF Tech Week. All times Pacific.') for date in sorted(counts)]
    build_calendar_page(root, feeds, len(events), len(collections), meta)


def build_calendar_page(root, feeds, count, collection_count, meta):
    feed_cards = []
    for f in feeds:
        url=f'{SITE}/calendars/{f["path"]}'
        webcal=url.replace('https://','webcal://',1)
        feed_cards.append(f'''<article class="feed" id="{f['id']}" data-kind="{f['type']}" data-name="{escape(f['label'].lower(),quote=True)}">
<div class="eyebrow">{escape(f['type'])}<span>{f['count']} events</span></div>
<h3>{escape(f['label'])}</h3><p>{escape(f['description'])}</p>
<div class="actions"><a class="subscribe" href="{webcal}">Subscribe ↗</a><a href="calendars/{f['path']}" download>Export .ics</a><button data-copy="{url}" aria-label="Copy subscription URL for {escape(f['label'],quote=True)}">Copy URL</button></div>
</article>''')
    html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Subscribe to the SF Tech Week 2026 shortlist, focused event collections, or daily calendars."><title>The SF Edit · Calendar desk</title>
<style>
:root{{--ink:#172a29;--paper:#f5f1e8;--gold:#b29260;--muted:#5d6e64}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}a{{color:inherit;text-decoration-thickness:1px;text-underline-offset:4px}}button,input{{font:inherit}}header{{background:var(--ink);color:var(--paper);padding:34px max(6vw,24px) 62px}}nav{{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:60px}}.brand{{font-size:13px;letter-spacing:4px;color:#d0b283;text-decoration:none}}nav a:last-child{{font-size:13px;color:#c7d0c7}}.kicker{{font-size:12px;letter-spacing:2px;color:#d0b283;text-transform:uppercase}}h1{{font:clamp(44px,7vw,86px)/1.04 Georgia,serif;letter-spacing:-2px;margin:20px 0 24px;font-weight:normal}}header p{{max-width:630px;color:#b9c8bb;font-size:18px}}.stats{{display:flex;gap:50px;margin-top:38px;padding-top:28px;border-top:1px solid #41534b;max-width:800px}}.stats b{{font:32px Georgia,serif;display:block}}.stats small{{font-size:11px;letter-spacing:1.8px;color:#c7b08d}}main{{max-width:1280px;margin:auto;padding:46px 24px}}.guide{{display:grid;grid-template-columns:1fr 1fr;gap:32px;border-bottom:1px solid #d4d1c7;padding-bottom:30px}}h2{{font:34px/1.2 Georgia,serif;margin:0 0 16px}}.guide p{{color:var(--muted);max-width:570px;font-size:14px}}.guide ol{{padding-left:22px;margin:0;font-size:14px}}.toolbar{{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:36px 0 28px}}.toolbar button{{border:1px solid #b5bfb3;background:transparent;border-radius:999px;padding:8px 17px;cursor:pointer;font-size:13px}}.toolbar button[aria-pressed=true]{{background:var(--ink);color:var(--paper);border-color:var(--ink)}}input{{flex:1;min-width:190px;background:transparent;border:0;border-bottom:1px solid #abb7aa;padding:10px;font-size:14px}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}.feed{{padding:27px;background:#fffdf8;border:1px solid #dcded3;display:flex;flex-direction:column;scroll-margin-top:20px;min-height:230px}}.feed:first-child{{background:#e9e1d0;border-color:#b7a077}}.eyebrow{{display:flex;justify-content:space-between;gap:10px;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#7a704f}}.eyebrow span{{letter-spacing:.3px;white-space:nowrap}}h3{{font:27px/1.12 Georgia,serif;margin:18px 0 10px}}.feed p{{font-size:13px;color:var(--muted);line-height:1.5;margin:0 0 22px}}.actions{{margin-top:auto;display:flex;gap:14px;align-items:center;flex-wrap:wrap;font-size:12px}}.subscribe{{font-weight:700}}.actions button{{padding:0;border:0;background:none;color:#52685a;font-size:12px;text-decoration:underline;text-underline-offset:4px;cursor:pointer}}.feed[hidden]{{display:none}}.note{{font-size:13px;color:var(--muted);margin:28px 0}}footer{{border-top:1px solid #d4d1c7;padding:25px 0 35px;color:var(--muted);font-size:12px}}footer a{{margin-right:20px}}#status{{min-height:24px;font-size:13px}}@media(max-width:950px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:600px){{.grid,.guide{{grid-template-columns:1fr}}nav{{margin-bottom:45px}}.stats{{gap:26px}}.stats b{{font-size:27px}}.stats small{{font-size:9px}}h1{{letter-spacing:-1px}}main{{padding:32px 20px}}.feed{{min-height:210px}}}}
</style></head><body>
<header><nav><a class="brand" href="{REPO}">THE SF EDIT</a><a href="{REPO}">Explore the guide ↗</a></nav><div class="kicker">San Francisco · October 05–11, 2026</div><h1>Your week.<br><i>On your calendar.</i></h1><p>Ten selected rooms. A collection that fits your interests. Or a single day in the city. Choose what belongs on your calendar.</p><div class="stats"><div><b>10</b><small>THE SHORTLIST</small></div><div><b>{collection_count}</b><small>COLLECTIONS</small></div><div><b>{count:,}</b><small>EVENTS</small></div></div></header>
<main><section class="guide"><div><h2>The calendar desk</h2><p>Subscribe to receive future revisions to this guide. Export for a one-time import. Keep a dedicated calendar so these discovery listings stay separate from confirmed plans.</p></div><div><ol><li><b>Apple Calendar:</b> choose Subscribe, or File → New Calendar Subscription and paste the URL.</li><li><b>Google Calendar:</b> Copy URL, then Other calendars → + → From URL on desktop.</li><li><b>Outlook:</b> Copy URL, then Add calendar → Subscribe from web.</li></ol><p><a href="{REPO}/blob/main/docs/calendar.md">Full setup instructions and limitations ↗</a></p></div></section>
<div class="toolbar" aria-label="Filter calendars"><button data-filter="all" aria-pressed="true">All feeds</button><button data-filter="The edit" aria-pressed="false">The shortlist</button><button data-filter="Collection" aria-pressed="false" id="collections">Collections</button><button data-filter="Day" aria-pressed="false" id="days">By day</button><input type="search" id="search" aria-label="Search calendar feeds" placeholder="Find your interest…"></div><div id="status" role="status" aria-live="polite"></div><section class="grid" aria-label="Calendar feeds">{''.join(feed_cards)}</section>
<p class="note">All times are shown in your calendar's local time zone. The event source is Pacific time. Listings are not tickets: apply separately and confirm admission and location with the organizer. Unknown end times are left unset. This is a dated guide; subscriptions refresh when the repository changes, not directly from organizers.</p>
<footer><a href="{REPO}">The guide</a><a href="{REPO}/blob/main/docs/methodology.md">Source notes</a><a href="{REPO}/blob/main/CONTRIBUTING.md">Suggest a correction</a><p>Independent, unaffiliated guide · Snapshot {escape(meta['checked_at_display'])} · No sign-in, analytics, or attendee data.</p></footer></main>
<script>
const buttons=[...document.querySelectorAll('[data-filter]')], cards=[...document.querySelectorAll('.feed')], search=document.querySelector('#search'), status=document.querySelector('#status');let active='all';
function filter(){{let count=0;for(const card of cards){{const show=(active==='all'||card.dataset.kind===active)&&card.dataset.name.includes(search.value.trim().toLowerCase());card.hidden=!show;if(show)count++;}}status.textContent=count+' calendar feed'+(count===1?'':'s');}}
for(const button of buttons)button.addEventListener('click',()=>{{active=button.dataset.filter;for(const b of buttons)b.setAttribute('aria-pressed',String(b===button));filter();}});search.addEventListener('input',filter);
for(const button of document.querySelectorAll('[data-copy]'))button.addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(button.dataset.copy);button.textContent='Copied';status.textContent='Subscription URL copied. Paste it into your calendar app.';setTimeout(()=>button.textContent='Copy URL',2500);}}catch{{status.textContent='Copy this URL: '+button.dataset.copy;}}}});
function followHash(){{const kind={{collections:'Collection',days:'Day','top-10':'The edit'}}[location.hash.slice(1)];if(kind){{active=kind;search.value='';for(const b of buttons)b.setAttribute('aria-pressed',String(b.dataset.filter===kind));}}filter();}}
window.addEventListener('hashchange',followHash);followHash();
</script></body></html>'''
    (root/'docs/index.html').write_text(html)
    (root/'docs/.nojekyll').write_text('')
