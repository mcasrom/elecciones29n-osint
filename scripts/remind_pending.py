#!/usr/bin/env python3
"""Un recordatorio de confirmación a pendientes de 29N. Dry por defecto."""
from __future__ import annotations
import argparse, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path('/home/deploy/elecciones29n-osint')
sys.path.insert(0,str(ROOT/'scripts'))
import subs_api
DB=ROOT/'data'/'subs.db'

def mask(e: str) -> str:
    local,_,dom=e.partition('@')
    return (local[:3]+'***@'+dom) if dom else '***'

def ensure_col(con):
    cols={r[1] for r in con.execute('pragma table_info(subscribers)')}
    if 'reminder_sent_at' not in cols:
        con.execute('alter table subscribers add column reminder_sent_at TEXT')
        con.commit()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--apply',action='store_true'); a=ap.parse_args()
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; ensure_col(con)
    rows=con.execute("select id,email,created_at,last_sent_at from subscribers where status='pending' and reminder_sent_at is null order by created_at").fetchall()
    print(f'pendientes sin recordatorio: {len(rows)}')
    for r in rows:
        print(' -',mask(r['email']),'alta',r['created_at'])
    if not a.apply:
        print('dry: no se envía')
        return 0
    sent=0
    for r in rows:
        ok=subs_api.send_confirmation(r['email'],r['id'])
        print(('OK ' if ok else 'FALLO ')+mask(r['email']))
        if ok:
            con.execute('update subscribers set reminder_sent_at=? where id=?',(datetime.now(timezone.utc).isoformat(timespec='seconds'),r['id']))
            con.commit(); sent+=1
    print('recordatorios enviados:',sent)
    return 0 if sent==len(rows) else 1
if __name__=='__main__': raise SystemExit(main())
