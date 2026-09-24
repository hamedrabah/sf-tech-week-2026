"""Original vector artwork for the editorial guide. No external render dependencies."""
import base64
from datetime import datetime
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

INK = '#172a29'
PAPER = '#f5f1e8'
GOLD = '#ba945c'

EDITS = {'claude-founder-house': (['Claude', 'Founder House'],
                          'ANTHROPIC',
                          'FRONTIER AI',
                          'A three-day base for founders building with AI.'),
 'official-tech-week-kickoff': (['The official', 'kickoff'],
                                'FIREWORKS × A16Z',
                                'OPENING NIGHT',
                                'One opening night. Five startup ecosystems.'),
 'capturing-value-intelligence': (['The value of', 'intelligence'],
                                  'HSBC × A16Z',
                                  'AI INFRASTRUCTURE',
                                  'Where AI infrastructure meets investment.'),
 'speedrun-ai-faire': (['The AI Faire'],
                       'A16Z SPEEDRUN',
                       'STARTUP DISCOVERY',
                       'Meet the builders. See the products working.'),
 'deep-tech-investor-breakfast': (['Deep tech', 'investor breakfast'],
                                  'RENEGADE × SPEEDRUN',
                                  'INVESTOR CIRCLE',
                                  'An investor-focused morning, off the record.'),
 'match-house': (['MATCH HOUSE'],
                 'MATCH HOUSE',
                 'CURATED CONNECTIONS',
                 'A room built around relevant introductions.'),
 'camp-ai-production-ready-agents': (['Production-ready', 'agents'],
                                     'AUTH0',
                                     'BUILD & DEPLOY',
                                     'The practical work behind agents in production.'),
 'google-engineering-10x': (['Engineering', '10x'],
                            'GOOGLE FOR STARTUPS',
                            'FRONTIER ENGINEERING',
                            'A morning for ambitious technical founders.'),
 'nexxaworld': (['NexxaWorld'],
                'NEXXA × A16Z',
                'INDUSTRIAL AI',
                'AI meets the operations of heavy industry.'),
 'who-will-own-future': (['Who will own', 'the future?'],
                         'ARK INVEST',
                         'THE INVESTMENT VIEW',
                         'A Thursday evening with the investment world.')}


def text(x, y, value, size=20, fill=INK, extra='', serif=False):
    font = "Georgia, 'Times New Roman', serif" if serif else 'Arial, Helvetica, sans-serif'
    return f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" {extra}>{escape(value)}</text>'


def logo_markup(root, brand, x=506, y=41, width=188, height=50):
    if not brand or not brand.get('asset'):
        return ''
    source = root / brand['asset']
    if source.suffix.lower() == '.svg':
        svg = ET.fromstring(source.read_text())
        # Self-contained authentic brand geometry. IDs are prefixed to avoid collisions.
        prefix = source.stem + '-'
        ids = {el.attrib['id']: prefix + el.attrib['id'] for el in svg.iter() if 'id' in el.attrib}
        for el in svg.iter():
            for key, value in list(el.attrib.items()):
                if key == 'id': el.set(key, ids[value])
                else:
                    for old, new in ids.items():
                        value = value.replace('url(#' + old + ')', 'url(#' + new + ')')
                        if value == '#' + old: value = '#' + new
                    el.set(key, value)
        svg.set('x', str(x)); svg.set('y', str(y))
        svg.set('width', str(width)); svg.set('height', str(height))
        svg.set('preserveAspectRatio', 'xMaxYMid meet')
        return ET.tostring(svg, encoding='unicode')
    mime = 'image/png' if source.suffix.lower() == '.png' else 'image/jpeg'
    encoded = base64.b64encode(source.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{width}" height="{height}" preserveAspectRatio="xMaxYMid meet" href="data:{mime};base64,{encoded}"/>'


def schedule_labels(pick):
    start = datetime.fromisoformat(pick['start'])
    end = datetime.fromisoformat(pick['end']) if pick.get('end') else None
    def clock(dt):
        hour = dt.hour % 12 or 12
        minutes = f':{dt.minute:02d}' if dt.minute else ''
        return f'{hour}{minutes} {"AM" if dt.hour < 12 else "PM"}'
    if end and end.date() != start.date():
        label = f"{start.strftime('%b').upper()} {start.day:02d}–{end.day:02d}"
        schedule = f"{start.strftime('%a').upper()} {clock(start)} – {end.strftime('%a').upper()} {clock(end)}"
    else:
        label = start.strftime('%a · %b %d').upper()
        schedule = clock(start) + ((' – ' + clock(end)) if end else ' · END TBA')
    if pick['id'] in {'claude-founder-house', 'google-engineering-10x'}:
        schedule += '*'
    return label, schedule


def build_visuals(root, picks, brands, count, collection_count):
    out = root / 'assets'
    (out / 'cards').mkdir(parents=True, exist_ok=True)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="570" viewBox="0 0 1440 570" role="img" aria-labelledby="title desc">',
             '<title id="title">The SF Edit. San Francisco Tech Week 2026.</title>',
             f'<desc id="desc">October 5–11. Ten selected events. {count:,} public listings. {collection_count} focused collections.</desc>',
             f'<rect width="1440" height="570" fill="{INK}"/>',
             '<path d="M928 0V570M960 0V570M1116 0V570M1334 0V570M884 132H1440M884 375H1440" stroke="#36504b" stroke-width="1"/>']
    # An original bridge-inspired line drawing; no third-party imagery.
    parts += ['<g fill="none" stroke="#c8ab7d" stroke-width="2" opacity=".58">',
              '<path d="M870 366H1410M873 380H1410M996 126V408M1009 126V408M1272 126V408M1285 126V408M985 153H1020M1261 153H1296M985 198H1020M1261 198H1296"/>',
              '<path d="M862 303Q937 269 1002 145Q1137 405 1278 145Q1346 264 1420 303"/>']
    for x in range(904, 1400, 31):
        if x < 1002: top = 303 - ((x - 862) / 140) * 158
        elif x < 1278: top = 145 + 125 * (1 - ((x - 1140) / 138) ** 2)
        else: top = 145 + ((x - 1278) / 142) * 158
        parts.append(f'<path d="M{x} {max(145,top):.1f}V366" opacity=".55"/>')
    parts += ['</g>',text(60,67,'THE SF EDIT',21,GOLD,'letter-spacing="5"'),
              text(60,160,'San Francisco.',82,PAPER,serif=True),
              text(60,251,'A week, well chosen.',70,PAPER,'font-style="italic"',True),
              text(63,318,'TECH WEEK 2026  /  OCTOBER 05–11',22,'#d5dbd2','letter-spacing="2"'),
              text(63,371,'A considered guide to the rooms worth your time.',23,'#adbab0'),
              '<path d="M60 435H1380" stroke="#4c6058"/>']
    for x, big, small in [(62,'10','THE SHORTLIST'),(440,f'{count:,}','PUBLIC LISTINGS'),(842,str(collection_count),'FOCUSED COLLECTIONS'),(1218,'07','DAYS')]:
        parts += [text(x,495,big,38,PAPER,serif=True),text(x,531,small,12,GOLD,'letter-spacing="1.8"')]
    parts.append('</svg>')
    (out / 'cover.svg').write_text('\n'.join(parts)+'\n')
    by_pick = {b['pick_id']: b for b in brands}
    for p in picks:
        lines, host, tag, reason = EDITS[p['id']]
        date, schedule = schedule_labels(p)
        rank = p['seed_rank']
        brand = by_pick.get(p['id'])
        card = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="450" viewBox="0 0 760 450" role="img" aria-labelledby="title desc">',
                f'<title id="title">{rank:02d}. {escape(p["title"])}</title>',
                f'<desc id="desc">{escape(date)}, {escape(schedule)} Pacific. {escape(reason)} Application required.</desc>',
                f'<rect width="760" height="450" rx="4" fill="{PAPER}"/>',
                f'<rect x="0" width="6" height="450" fill="{GOLD}"/>',
                f'<circle cx="64" cy="66" r="27" fill="{INK}"/>',
                text(64,73,f'{rank:02d}',18,PAPER,'text-anchor="middle"'),
                text(109,60,'THE SHORTLIST',12,'#68726c','letter-spacing="2"'),
                text(109,82,tag,12,GOLD,'letter-spacing="1.2"'),
                logo_markup(root,brand),
                '<path d="M38 112H720" stroke="#d9d3c7"/>']
        title_size=53 if max(map(len,lines)) < 18 else 47
        for i,line in enumerate(lines):
            card.append(text(39,184 + i*57,line,title_size,INK,serif=True))
        card += [text(41,280,host,13,'#6b756d','letter-spacing="1.4"'),
                 text(41,318,reason,18,'#4b6056'),
                 '<path d="M38 347H720" stroke="#d9d3c7"/>',
                 text(40,380,date,16,INK,'font-weight="700"'),
                 text(40,410,schedule+' PT',15,'#526258'),
                 f'<rect x="548" y="368" width="169" height="33" rx="16" fill="{INK}"/>',
                 text(632,389,'INVITE-ONLY' if rank==5 else 'APPLICATION',11,PAPER,'text-anchor="middle" letter-spacing="1.8"')]
        if '*' in schedule:
            card.append(text(550,428,'*Confirm arrival time',11,'#697268'))
        card.append('</svg>')
        (out / 'cards' / f'{rank:02d}-{p["id"]}.svg').write_text('\n'.join(card)+'\n')
