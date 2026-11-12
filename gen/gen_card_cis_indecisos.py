#!/usr/bin/env python3
"""Tarjeta 1200x630: el 18,1 % que no se pronuncia en el CIS 3584."""
from __future__ import annotations
import argparse, json, os
from PIL import Image, ImageDraw, ImageFont
BG=(15,16,38); PANEL=(24,26,54); FG=(238,240,246); MUTED=(167,171,196); ACCENT=(255,90,31); OK=(61,220,151); BLUE=(142,197,255); LINE=(48,52,88)
def font(size,bold=False,serif=False):
    c=[]
    if serif: c += ["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
    if bold: c += ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    else: c += ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for x in c:
        if os.path.exists(x): return ImageFont.truetype(x,size)
    return ImageFont.load_default()
def fmt(v): return f"{float(v):.1f}".replace(".",",")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--cis",default="data/cis_3584_2026.json"); ap.add_argument("--out",default="web/og-cis-3584-indecisos.png"); a=ap.parse_args()
    d=json.load(open(a.cis,encoding="utf-8")); ns=d["no_sabe_pct"]; nc=d["no_contesta_pct"]; total=ns+nc
    img=Image.new("RGB",(1200,630),BG); dr=ImageDraw.Draw(img)
    dr.rectangle([0,0,10,630],fill=ACCENT)
    dr.text((52,36),"elecciones29n-osint",font=font(27,True),fill=FG)
    dr.text((52,74),"CIS 3584 · 45.074 entrevistas · campo 7–30 oct",font=font(20),fill=MUTED)
    dr.text((52,136),"18,1% no se pronuncia",font=font(68,True,True),fill=FG)
    dr.rectangle([54,220,240,226],fill=ACCENT)
    dr.text((52,244),"15,8 % no sabe  +  2,3 % no contesta",font=font(28,True),fill=BLUE)
    dr.rounded_rectangle([52,320,1148,430],radius=16,fill=PANEL,outline=LINE,width=1)
    dr.text((78,344),"No es un bloque que se reparta",font=font(30,True),fill=FG)
    dr.text((78,390),"Voto directo (censo) y estimación (voto válido) no son intercambiables.",font=font(19),fill=MUTED)
    dr.rounded_rectangle([52,466,1148,534],radius=12,fill=(31,34,66),outline=LINE,width=1)
    dr.text((78,485),"No es un pronóstico. No es voto oculto.",font=font(24,True),fill=OK)
    dr.text((52,578),"Fuente: CIS 3584 · elecciones29n.pruebapublica.com",font=font(15),fill=MUTED)
    img.save(a.out,"PNG",optimize=True); print("ok",a.out)
if __name__=="__main__": main()
