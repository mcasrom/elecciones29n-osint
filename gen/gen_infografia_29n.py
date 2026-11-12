#!/usr/bin/env python3
"""Infografía de resumen 29N (2400x1350) + variante LinkedIn (1200x627)."""
from __future__ import annotations
import argparse, json, os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
TZ=ZoneInfo("Europe/Madrid")

def fmt(v,dec=1):
    if v is None: return "—"
    s=f"{float(v):,.{dec}f}"
    return s.replace(",","X").replace(".",",").replace("X",".")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--latest",default="web/data/latest.json"); ap.add_argument("--leaders",default="data/cis_lideres_2026.json"); ap.add_argument("--out",default="web/og/29n-infografia.png"); ap.add_argument("--linkedin",default=""); a=ap.parse_args()
    d=json.load(open(a.latest,encoding="utf-8")); leaders=json.load(open(a.leaders,encoding="utf-8")).get("leaders",[])
    by={p["party"]:p for p in d.get("parties",[]) if not p.get("territorial")}; hem=d.get("hemicycle",[])[-1]; h=d.get("health",{}); blocks={"right":d.get("bloc_right"),"left":d.get("bloc_left")}
    main_parties=[x for x in ("PP","PSOE","VOX","SUMAR") if x in by]
    maxmean=max((by[x]["mean"] for x in main_parties),default=40)
    bars=""
    colors={"PP":"#2f6fdb","PSOE":"#d9343e","VOX":"#4b9b3f","SUMAR":"#d63f8a"}
    for x in main_parties:
        p=by[x]; w=float(p["mean"])/maxmean*100
        bars+=f'<div class="barrow"><span class="pl">{x}</span><div class="track"><i style="width:{w:.1f}%;background:{colors.get(x,"#77a")}"></i></div><b>{fmt(p["mean"])}%</b><small>{fmt(p["min"])}–{fmt(p["max"])}</small></div>'
    leadrows=""
    for l in leaders[:4]:
        w=float(l["mean"])/5*100
        leadrows+=f'<div class="leadrow"><span>{l["name"].replace("Alberto Núñez ","").replace("Pedro ","").replace("Yolanda ","").replace("Santiago ","")}</span><div class="track2"><i style="width:{w:.1f}%"></i></div><b>{fmt(l["mean"],2)}</b></div>'
    gap=d.get("gap_pp_psoe"); days=d.get("days_to_election")
    html=f'''<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;background:#0b0c1c;color:#f0f2f7;font-family:Arial,Helvetica,sans-serif}}
.page{{width:1200px;height:675px;padding:26px 30px 20px;background:#0b0c1c;position:relative}}
.top{{border-top:5px solid #f03b2e;padding-top:14px;display:flex;justify-content:space-between;align-items:flex-start}}
.brand{{font-weight:900;font-size:27px;letter-spacing:.02em}} .brand span{{color:#f03b2e}}
.sub{{font-size:12px;color:#a8adbf;margin-top:4px}} .right{{text-align:right;font-size:12px;color:#a8adbf}} .right b{{display:block;color:#f5c542;font-size:12px;margin-top:5px}}
h1{{font-family:Georgia,serif;font-size:38px;line-height:1.02;margin:18px 0 5px;letter-spacing:-.03em}} .lead{{font-size:13px;color:#a8adbf;margin:0 0 12px}}
.kpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:12px 0 14px}} .kpi{{background:#151a2c;border:1px solid #2a3047;border-radius:10px;padding:12px 14px}} .kpi b{{display:block;font-size:26px;line-height:1}} .kpi span{{display:block;font-size:11px;color:#a8adbf;margin-top:5px}}
.grid{{display:grid;grid-template-columns:1.15fr .85fr;gap:14px}} .card{{background:#151a2c;border:1px solid #2a3047;border-radius:12px;padding:16px 18px}} .card h2{{font-size:17px;margin:0 0 12px}} .card p{{font-size:11.5px;color:#a8adbf;line-height:1.45;margin:8px 0 0}}
.barrow{{display:grid;grid-template-columns:52px 1fr 54px 76px;gap:8px;align-items:center;font-size:12px;margin:9px 0}} .pl{{font-weight:800}} .track{{height:16px;background:#293047;border-radius:8px;overflow:hidden}} .track i{{display:block;height:100%;border-radius:8px}} .barrow b{{text-align:right;font-size:13px}} .barrow small{{color:#a8adbf;font-size:10.5px;white-space:nowrap}}
.blockrow{{display:flex;gap:10px;margin:8px 0 12px}} .bl{{flex:1;background:#0e1323;border:1px solid #2a3047;border-radius:10px;padding:12px}} .bl b{{display:block;font-size:29px;color:#f03b2e}} .bl:last-child b{{color:#3ddc97}} .bl span{{font-size:10.5px;color:#a8adbf}}
.leadrow{{display:grid;grid-template-columns:112px 1fr 40px;gap:8px;align-items:center;font-size:12px;margin:8px 0}} .track2{{height:12px;background:#293047;border-radius:7px;overflow:hidden}} .track2 i{{display:block;height:100%;background:#f5c542;border-radius:7px}} .leadrow b{{text-align:right;font-size:12px}}
.note{{font-size:10.5px;color:#a8adbf;line-height:1.4;margin-top:10px}} .foot{{position:absolute;left:30px;right:30px;bottom:17px;border-top:1px solid #2a3047;padding-top:8px;font-size:9.5px;color:#858da4;display:flex;justify-content:space-between;gap:20px}} .stamp{{color:#f5c542;font-weight:700}} .badge{{font-size:10px;color:#3ddc97;border:1px solid #3ddc97;border-radius:10px;padding:2px 7px;display:inline-block}}
</style></head><body><div class="page">
<div class="top"><div><div class="brand">ESPAÑA <span>|</span> ELECCIONES GENERALES 29N 2026</div><div class="sub">Media agregada de sondeos con rango · sin pronóstico</div></div><div class="right">{d.get("updated_at","")}<b>NO ES UN PRONÓSTICO</b></div></div>
<h1>El 29N en una imagen.</h1><p class="lead">Datos observados, no una predicción. La incertidumbre va en el rango.</p>
<div class="kpis"><div class="kpi"><b>{days if days is not None else "—"}</b><span>días para el 29N</span></div><div class="kpi"><b>{d.get("n_polls","—")}</b><span>sondeos · {h.get("n_pollsters","—")} casas</span></div><div class="kpi"><b>{("+"+fmt(gap)) if gap is not None else "—"}</b><span>puntos PP–PSOE</span></div><div class="kpi"><b>{fmt(blocks.get("right"))} / {fmt(blocks.get("left"))}</b><span>bloques de voto PP+VOX / PSOE+SUMAR</span></div><div class="kpi"><b>{fmt(h.get("dispersion_iqr"))} pp</b><span>dispersión entre casas (IQR)</span></div></div>
<div class="grid"><div class="card"><h2>Estimación de voto · media y rango</h2>{bars}<p>Barra = media; texto = mínimo–máximo observado. No es intención de voto individual.</p></div><div class="card"><h2>Bloques y líderes</h2><div class="blockrow"><div class="bl"><b>{fmt(blocks.get("right"))}%</b><span>PP + VOX</span></div><div class="bl"><b>{fmt(blocks.get("left"))}%</b><span>PSOE + SUMAR + PODEMOS</span></div></div><p style="margin:0 0 8px">Mayoría absoluta: 176 escaños. Los bloques son suma de medias de voto, no escaños ni una coalición.</p>{leadrows}<p class="note">Valoración de líderes: CIS oct-2026, escala 1–10, una sola casa y ola. No es intención de voto.</p></div></div>
<div class="foot"><span>Fuente: sondeos publicados (Onda Cero, Electomanía, CIS, Sigma Dos, SocioMétrica, NC Report, GAD3, 40dB, IMOP, DYM, Celeste-Tel, Target Point). Datos abiertos AGPL-3.0.</span><span>elecciones29n.pruebapublica.com</span></div></div></body></html>'''
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path="/home/deploy/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome", args=["--no-sandbox"]); page=b.new_page(viewport={"width":1200,"height":675},device_scale_factor=2); page.set_content(html,wait_until="load"); page.screenshot(path=a.out,type="png"); b.close()
    print("ok",a.out)
    if a.linkedin:
        im=Image.open(a.out).convert("RGB"); tw,th=1200,627; bg=(15,16,28); canvas=Image.new("RGB",(tw,th),bg); w,h=im.size; scale=th/h; rw=int(w*scale); r=im.resize((rw,th),Image.LANCZOS); canvas.paste(r,((tw-rw)//2,0)); canvas.save(a.linkedin,"PNG",optimize=True); print("ok",a.linkedin)

if __name__=="__main__": main()
