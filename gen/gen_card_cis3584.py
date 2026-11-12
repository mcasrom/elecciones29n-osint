#!/usr/bin/env python3
"""Tarjeta 1200x630 para la divergencia CIS 3584 vs media 29N."""
from __future__ import annotations
import argparse, json, os
from PIL import Image, ImageDraw, ImageFont

BG=(15,16,38); PANEL=(24,26,54); PANEL2=(31,34,66); FG=(238,240,246); MUTED=(167,171,196)
ACCENT=(255,90,31); OK=(61,220,151); BLUE=(142,197,255); LINE=(48,52,88)

def font(size,bold=False,serif=False):
    cands=[]
    if serif: cands += ["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
    if bold: cands += ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    else: cands += ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for c in cands:
        if os.path.exists(c): return ImageFont.truetype(c,size)
    return ImageFont.load_default()

def fmt(v,dec=1):
    if v is None: return "—"
    return f"{float(v):.{dec}f}".replace(".",",")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cis",default="data/cis_3584_2026.json")
    ap.add_argument("--latest",default="web/data/latest.json")
    ap.add_argument("--out",default="web/og-cis-3584.png")
    a=ap.parse_args()
    cis=json.load(open(a.cis,encoding="utf-8")); latest=json.load(open(a.latest,encoding="utf-8"))
    cv={r["party"]:float(r["pct"]) for r in cis["vote_estimate"]}
    mv={p["party"]:float(p["mean"]) for p in latest.get("parties",[])}
    rows=[("PSOE",cv.get("PSOE",0),mv.get("PSOE",0)),("PP",cv.get("PP",0),mv.get("PP",0)),("VOX",cv.get("VOX",0),mv.get("VOX",0))]
    img=Image.new("RGB",(1200,630),BG); dr=ImageDraw.Draw(img)
    dr.rectangle([0,0,10,630],fill=ACCENT)
    dr.text((52,36),"elecciones29n-osint",font=font(27,True),fill=FG)
    dr.text((52,74),"CIS 3584 · publicado 12-nov-2026",font=font(20),fill=MUTED)
    dr.text((52,132),"El CIS se desmarca",font=font(64,True,True),fill=FG)
    dr.rectangle([54,212,220,218],fill=ACCENT)
    dr.text((52,236),"PSOE +6,9 pp · PP −5,8 pp frente a la media de 17 sondeos",font=font(23),fill=MUTED)
    y=304
    for name,c,m in rows:
        d=c-m; col=OK if d>=0 else ACCENT
        dr.rounded_rectangle([52,y,1148,y+75],radius=14,fill=PANEL,outline=LINE,width=1)
        dr.text((74,y+18),name,font=font(26,True),fill=FG)
        dr.text((180,y+18),f"CIS {fmt(c)} %",font=font(22,True),fill=BLUE)
        dr.text((360,y+18),f"media {fmt(m)} %",font=font(22),fill=MUTED)
        dr.text((590,y+16),f"{'+' if d>=0 else ''}{fmt(d)} pp",font=font(30,True),fill=col)
        y+=87
    dr.text((52,578),"Campo 7–30 octubre · 45.074 entrevistas · no es un pronóstico",font=font(18),fill=MUTED)
    dr.text((975,578),"29n.pruebapublica.com",font=font(15),fill=MUTED)
    img.save(a.out,"PNG",optimize=True); print("ok",a.out)

if __name__=="__main__": main()
