#!/usr/bin/env python3
"""OG 1200x630 para un sondeo concreto desde polls_history.csv."""
from __future__ import annotations
import argparse, csv, json, os
from PIL import Image, ImageDraw, ImageFont

BG=(15,16,38); PANEL=(24,26,54); FG=(238,240,246); MUTED=(180,184,205); ACCENT=(255,90,31); OK=(61,220,151); LINE=(48,52,88)
COLORS={"PP":(59,130,246),"PSOE":(239,68,68),"VOX":(34,197,94),"SUMAR":(217,70,239),"PODEMOS":(124,58,237),"Otros":(148,163,184)}

def font(size,bold=False,serif=False):
    c=[]
    if serif: c+=["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
    if bold: c+=["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
    else: c+=["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for x in c:
        if os.path.exists(x): return ImageFont.truetype(x,size)
    return ImageFont.load_default()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pollster",default="Sigma Dos"); ap.add_argument("--date",default="2026-11-02")
    ap.add_argument("--history",default="data/polls_history.csv"); ap.add_argument("--latest",default="web/data/latest.json")
    ap.add_argument("--out",default="web/og-sondeo-sigma-20261102.png")
    a=ap.parse_args()
    vals={}
    with open(a.history,encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            if r.get("pollster")==a.pollster and r.get("date")==a.date:
                try: vals[r["party"]]=float(r["value"])
                except Exception: pass
    if not vals: raise SystemExit("sin datos del sondeo")
    latest=json.load(open(a.latest,encoding="utf-8"))
    means={p["party"]:p.get("mean") for p in latest.get("parties",[])}
    img=Image.new("RGB",(1200,630),BG); d=ImageDraw.Draw(img)
    d.rectangle([0,0,12,630],fill=ACCENT); d.rectangle([0,0,1200,8],fill=ACCENT)
    d.text((52,38),"elecciones29n-osint",font=font(28,True),fill=FG)
    d.text((52,76),"Sondeo publicado · 29N 2026",font=font(22),fill=MUTED)
    d.text((52,126),a.pollster,font=font(62,True,serif=True),fill=FG)
    d.text((52,198),f"{a.date[8:10]}/{a.date[5:7]}/{a.date[:4]} · intención de voto",font=font(24),fill=MUTED)
    d.rectangle([54,236,190,241],fill=ACCENT)
    y=278
    for party in ["PP","PSOE","VOX","SUMAR"]:
        v=vals.get(party); m=means.get(party)
        if v is None: continue
        d.text((52,y),party,font=font(30,True),fill=FG)
        d.text((250,y),f"{v:.1f}%",font=font(30,True),fill=ACCENT)
        d.text((430,y+4),f"media 29N {m:.1f}%" if m is not None else "",font=font(20),fill=MUTED)
        w=int(v/35*540)
        d.rounded_rectangle([620,y+4,620+w,y+24],radius=5,fill=COLORS.get(party,ACCENT))
        y+=58
    d.text((52,540),"Media agregada: PP 31,4 % · PSOE 26,2 %. Sin pronóstico.",font=font(22),fill=MUTED)
    d.text((52,576),"Fuente: Onda Cero · compilación. No es un dato del observatorio.",font=font(18),fill=MUTED)
    d.text((875,576),"elecciones29n.pruebapublica.com",font=font(18),fill=OK)
    os.makedirs(os.path.dirname(a.out) or ".",exist_ok=True); img.save(a.out,optimize=True)
    print("og ok",a.out,img.size,vals)

if __name__=="__main__": main()
