#!/usr/bin/env python3
"""Vigila nuevos sondeos y microdatos del 29N. No importa nada: avisa."""
from __future__ import annotations
import argparse, hashlib, json, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path('/home/deploy/elecciones29n-osint')
STATE = ROOT / 'data' / 'tracking_watch_state.json'
CIS_URL = 'https://www.cis.es/es/w/avance-de-resultados-del-estudio-3584-preelectoral-elecciones-generales-2026-'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
QUERIES = {
    '40dB': '"40dB" encuesta 29N',
    'Sigma Dos': '"Sigma Dos" encuesta 29N',
    'SW Demoscopia': '"SW Demoscopia" 29N',
    'GAD3': 'GAD3 29N encuesta',
    'GAD3 provincial': 'GAD3 estimación voto provincias 29N',
    'CIS': 'CIS 29N encuesta',
}

def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xml'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read(2_000_000)

def fetch_rss(q: str):
    url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': q, 'hl': 'es', 'gl': 'ES', 'ceid': 'ES:es'})
    root = ET.fromstring(get(url))
    out = []
    for it in root.findall('.//item'):
        title = re.sub(r'\s+', ' ', (it.findtext('title') or '')).strip()
        link = (it.findtext('link') or '').strip()
        raw = (it.findtext('pubDate') or '').strip()
        try:
            dt = parsedate_to_datetime(raw).astimezone(timezone.utc)
        except Exception:
            continue
        out.append({'title': title, 'link': link, 'date': dt.date().isoformat(),
                    'dt': dt.isoformat(timespec='seconds')})
    return out

def key(item: dict) -> str:
    return hashlib.sha256((item['title'].lower() + '|' + item['link']).encode()).hexdigest()[:16]

def load_state():
    try:
        return json.loads(STATE.read_text(encoding='utf-8'))
    except Exception:
        return {'seen': [], 'last_run': None}

def save_state(st):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def cis_microdata_links():
    try:
        html = get(CIS_URL).decode('utf-8', 'ignore')
    except Exception as exc:
        return [f'ERROR al leer CIS: {exc}']
    links = re.findall(r'href="([^"]+)"', html, flags=re.I)
    return [u for u in links if 'microdat' in u.lower() or ('.zip' in u.lower() and '3584' in u)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--test', action='store_true')
    ap.add_argument('--seed', action='store_true', help='marca lo actual como visto; no alerta')
    ap.add_argument('--dias', type=int, default=2)
    a = ap.parse_args()
    if a.seed:
        st0 = load_state(); seen0 = set(st0.get('seen', []))
        since0 = datetime.now(timezone.utc).date() - timedelta(days=max(0, a.dias - 1))
        n0 = 0
        for name, query in QUERIES.items():
            try:
                for item in fetch_rss(query):
                    if datetime.fromisoformat(item['date']).date() >= since0:
                        seen0.add(key(item)); n0 += 1
            except Exception as exc:
                print(f'watch: seed error {name}: {exc}', file=sys.stderr)
        st0['seen'] = sorted(seen0)[-400:]
        st0['last_run'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
        save_state(st0)
        print(f'seed: {n0} vistos')
        return 0
    if a.test:
        sys.path.insert(0, '/home/deploy/social-poster')
        import social_queue as q
        from pathlib import Path
        env = q.load_env(Path('/home/deploy/hybrid-fimi-radar/.env'))
        chat = env.get('FIMI_OWNER_CHAT', '')
        ok = q.send_tg(chat, '✅ Watch 29N operativo. Avisaré de nuevos sondeos/microdatos; no importo nada automáticamente.')
        print('test', ok); return 0 if ok else 1
    st = load_state(); seen = set(st.get('seen', []))
    since = datetime.now(timezone.utc).date() - timedelta(days=max(0, a.dias - 1))
    found = []
    for name, query in QUERIES.items():
        try:
            for item in fetch_rss(query):
                if datetime.fromisoformat(item['date']).date() < since:
                    continue
                # Exigir el nombre de la casa en el titular para evitar ruido.
                if name.split()[0].lower() not in item['title'].lower() and name not in ('GAD3 provincial',):
                    continue
                if key(item) not in seen:
                    found.append((name, item))
        except Exception as exc:
            print(f'watch: error {name}: {exc}', file=sys.stderr)
    micro = cis_microdata_links()
    print(f'nuevos={len(found)} micro_links={len(micro)}')
    for name, item in found:
        print(name, item['date'], item['title'][:160])
    if micro:
        print('CIS micro links:', micro)
    if not found and not micro:
        if not a.dry:
            st['last_run'] = datetime.now(timezone.utc).isoformat(timespec='seconds'); save_state(st)
        return 0
    if a.dry:
        return 0
    lines = ['🔎 29N · datos nuevos detectados', '']
    for name, item in found[:12]:
        lines += [f'• {name} · {item["date"]}', f'  {item["title"][:180]}', f'  {item["link"]}', '']
    if micro:
        lines += ['• CIS 3584: posible microdato/enlace nuevo', '']
        lines += [f'  {u}' for u in micro[:5]]
    lines += ['No se ha importado nada. Revisar ficha, campo, muestra y URL antes de activar.']
    sys.path.insert(0, '/home/deploy/social-poster')
    import social_queue as q
    env = q.load_env(Path('/home/deploy/hybrid-fimi-radar/.env'))
    chat = env.get('FIMI_OWNER_CHAT', '')
    ok = q.send_tg(chat, '\n'.join(lines))
    print('telegram', ok)
    if ok:
        for _, item in found:
            seen.add(key(item))
        st['seen'] = sorted(seen)[-400:]
        st['last_run'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
        save_state(st)
    return 0 if ok else 1
if __name__ == '__main__':
    raise SystemExit(main())
