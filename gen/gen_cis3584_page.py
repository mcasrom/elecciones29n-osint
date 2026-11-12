#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def fmt(v,dec=1):
    return f"{float(v):.{dec}f}".replace(".",",")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--cis",default="data/cis_3584_2026.json"); ap.add_argument("--latest",default="web/data/latest.json"); ap.add_argument("--out",default="web/cis-3584.html"); a=ap.parse_args()
    c=json.load(open(a.cis,encoding="utf-8")); l=json.load(open(a.latest,encoding="utf-8"))
    cv={r["party"]:r for r in c["vote_estimate"]}; mv={p["party"]:p for p in l.get("parties",[])}
    common=["PSOE","PP","VOX"]
    rows="".join(f'<tr><td><strong>{p}</strong></td><td class="num">{fmt(cv[p]["pct"])}%</td><td class="num">{fmt(mv[p]["mean"])}%</td><td class="num">{fmt(float(cv[p]["pct"])-float(mv[p]["mean"]))} pp</td></tr>' for p in common if p in cv and p in mv)
    table="".join(f'<tr><td>{r["party"]}</td><td class="num">{fmt(r["pct"])}%</td><td class="num">{fmt(r["direct_pct"])}%</td><td class="num">{r["seats_min"]}–{r["seats_max"]}</td></tr>' for r in c["vote_estimate"] if r.get("seats_min") is not None)
    html=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>El CIS se desmarca de la media · 29N</title>
<meta name="description" content="CIS 3584 frente a la media de 17 sondeos: PSOE +6,9 pp, PP -5,8 pp. Campo 7–30 octubre; no es un pronóstico.">
<link rel="canonical" href="https://elecciones29n.pruebapublica.com/cis-3584.html">
<meta property="og:type" content="article"><meta property="og:site_name" content="Elecciones 29N"><meta property="og:locale" content="es_ES">
<meta property="og:title" content="El CIS se desmarca de la media · 29N"><meta property="og:description" content="CIS 3584: PSOE +6,9 pp y PP -5,8 pp frente a la media de 17 sondeos. Campo 7–30 octubre; no es un pronóstico.">
<meta property="og:url" content="https://elecciones29n.pruebapublica.com/cis-3584.html"><meta property="og:image" content="https://elecciones29n.pruebapublica.com/og-cis-3584.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="El CIS se desmarca de la media · 29N"><meta name="twitter:description" content="PSOE +6,9 pp y PP -5,8 pp frente a la media de 17 sondeos. Campo 7–30 octubre; no es un pronóstico."><meta name="twitter:image" content="https://elecciones29n.pruebapublica.com/og-cis-3584.png">
<style>body{{margin:0;background:#0b0c1c;color:#eef0f6;font:16px/1.6 system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}}main{{max-width:860px;margin:0 auto;padding:42px 20px 60px}}a{{color:#8ec5ff}}.eyebrow{{color:#3ddc97;font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:700}}h1{{font-family:Georgia,serif;font-size:clamp(34px,6vw,58px);line-height:1.04;margin:8px 0 12px}}.lead{{font-size:19px;color:#a7abc4;max-width:64ch}}.box{{background:#12142a;border:1px solid #262a4a;border-radius:14px;padding:18px 20px;margin:22px 0}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}@media(max-width:650px){{.grid{{grid-template-columns:1fr}}}}.kpi{{background:#171a34;border-radius:10px;padding:12px}}.kpi b{{display:block;font-size:30px;color:#ff5a1f}}.kpi span{{font-size:12px;color:#a7abc4}}table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{padding:8px 6px;border-bottom:1px solid #262a4a;text-align:left}}th{{color:#a7abc4;font-size:12px;text-transform:uppercase;letter-spacing:.06em}}.num{{text-align:right;font-variant-numeric:tabular-nums}}.small{{font-size:13px;color:#a7abc4}}code{{background:#171a34;padding:2px 5px;border-radius:4px}}.btn{{display:inline-block;background:#ff5a1f;color:#14080a;font-weight:800;padding:10px 15px;border-radius:9px;text-decoration:none;margin:6px 6px 0 0}}</style></head><body><main>
<p class="eyebrow">CIS 3584 · 12-nov-2026</p><h1>El CIS se desmarca de la media.</h1>
<p class="lead">No es un pronóstico ni una prueba de error: es una divergencia medida entre el CIS y la media de las encuestas publicadas para el 29N.</p>
<div class="grid"><div class="kpi"><b>+6,9 pp</b><span>PSOE en CIS frente a la media</span></div><div class="kpi"><b>−5,8 pp</b><span>PP en CIS frente a la media</span></div><div class="kpi"><b>−0,7 pp</b><span>VOX en CIS frente a la media</span></div></div>
<div class="box"><h2>Datos</h2><table><thead><tr><th>Partido</th><th class="num">CIS</th><th class="num">Media 14 d</th><th class="num">Δ</th></tr></thead><tbody>{rows}</tbody></table><p class="small">Media: {l.get("n_polls")} sondeos · {l.get("health",{}).get("n_pollsters")} casas. CIS: campo 7–30 oct, {c["sample"]:,} entrevistas, CATI, ±0,5 pp.</p></div>
<div class="box"><h2>Estimación CIS por partido</h2><table><thead><tr><th>Partido</th><th class="num">Estimación</th><th class="num">Voto directo</th><th class="num">Escaños p5–p95</th></tr></thead><tbody>{table}</tbody></table><p class="small">Los escaños son percentiles 5–95, no intervalos de confianza, y no se suman entre partidos. El CIS usa Frente Amplio y una ERC-Podemos conjunta; no se trocea aquí.</p></div>
<div class="box"><h2>Por qué se separa</h2><p>Influyen el <strong>efecto de casa</strong>, la diferencia entre <strong>estimación de voto</strong> e intención directa, el <strong>campo</strong> (7–30 oct frente a la ventana actual) y la <strong>estructura de partidos</strong>. No se puede atribuir a una sola causa con estos datos.</p><p class="small">Fuente: <a href="{c["source_url"]}" rel="noopener">CIS 3584</a> · <a href="/data/cis-3584.json">JSON</a> · <a href="/data/cis-3584.csv">CSV</a> · <a href="/robustez.html#cis-3584">Robustez</a>.</p></div>
<p class="small">No es un pronóstico. Publicado como contraste descriptivo, no como error electoral.</p>
</main></body></html>'''
    Path(a.out).write_text(html,encoding="utf-8"); print("ok",a.out)
if __name__=="__main__": main()
