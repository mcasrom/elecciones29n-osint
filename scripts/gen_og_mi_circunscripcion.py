#!/usr/bin/env python3
"""OG 1200x630 para Mi circunscripción."""
from __future__ import annotations
import argparse, os
from PIL import Image, ImageDraw, ImageFont
BG=(15,16,38); PANEL=(24,26,54); FG=(238,240,246); MUTED=(184,188,208); ACCENT=(255,90,31); OK=(61,220,151); LINE=(48,52,88)
def font(size,bold=False,serif=False):
    c=[]
    if serif: c+=["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
    if bold: c+=["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
    else: c+=["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    for x in c:
        if os.path.exists(x): return ImageFont.truetype(x,size)
    return ImageFont.load_default()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="public/og-mi-circunscripcion.png"); a=ap.parse_args()
    img=Image.new("RGB",(1200,630),BG); d=ImageDraw.Draw(img)
    d.rectangle([0,0,12,630],fill=ACCENT); d.rectangle([0,0,1200,8],fill=ACCENT)
    d.text((52,36),"elecciones29n-osint",font=font(28,True),fill=FG)
    d.text((52,78),"Tu municipio · tu provincia · 29N",font=font(22),fill=MUTED)
    d.text((52,132),"Mi circunscripción",font=font(62,True,serif=True),fill=FG)
    d.text((52,208),"Escaños, censo, resultado de 2023, vivienda y población",font=font(23,True),fill=MUTED)
    d.rectangle([54,252,190,257],fill=ACCENT)
    labels=[("Escaños","de tu provincia"),("Censo","electores"),("2023","resultado oficial"),("Vivienda","alquiler de referencia"),("Población","INE 2025"),("Simulador","D'Hondt con sliders")]
    x0=[52,610]; y0=292
    for i,(title,sub) in enumerate(labels):
        col=i//3; row=i%3; x=x0[col]; y=y0+row*76
        d.rounded_rectangle([x,y,x+530,y+60],radius=9,fill=PANEL,outline=LINE)
        d.text((x+16,y+9),title,font=font(20,True),fill=FG)
        d.text((x+16,y+33),sub,font=font(16),fill=MUTED)
    d.text((52,574),"Busca tu municipio y consulta lo que se juega tu provincia. Sin media provincial inventada.",font=font(18),fill=MUTED)
    d.text((850,574),"elecciones29n.pruebapublica.com",font=font(17),fill=OK)
    os.makedirs(os.path.dirname(a.out) or ".",exist_ok=True); img.save(a.out,optimize=True)
    print("og ok",a.out,img.size)
if __name__=="__main__": main()
