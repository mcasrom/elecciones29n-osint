# Lista de búsqueda de sondeos — 29N

**Estado:** preparada, sin ejecutar solicitudes ni envíos.
**Objetivo:** añadir casas nuevas con ficha técnica, no acumular trackings.
**Meta:** 3 casas nuevas antes del 13-N; revisión 2 veces por semana; máximo
2 sondeos nuevos por día.

## Criterios de admisión

- Fecha de **campo** y fecha de publicación.
- **Muestra** y procedimiento (CAWI, telefónica, presencial, panel…).
- **Una fila por sondeo**, no por medio que lo republica.
- Enlace a la **fuente primaria** o a la pieza que publica la tabla completa.
- Sin promedios de otras webs, sin encuestas internas no publicadas y sin
  filtraciones.
- Sin pagos, logins, paywalls ni elusión de mecanismos de acceso.
- Si falta muestra, se registra como **sin ficha** y no se presenta como
  equivalente a las demás.
- **CIS** se mantiene separado: es estimación de voto, no intención directa.

## Prioridad 1 — casas no representadas ahora

| Casa | Fuente pública | Búsqueda sugerida |
|---|---|---|
| 40dB | `https://40db.es/` · El País | `site:40db.es (encuesta OR sondeo) 29N`; `site:elpais.com 40dB encuesta 29N` |
| GAD3 | `https://www.gad3.com/` · ABC / La Vanguardia | `site:gad3.com encuesta 29N`; `site:abc.es GAD3 29N` |
| DYM | `https://www.dyminstitute.com/` · El Confidencial | `site:dyminstitute.com encuesta 29N`; `site:elconfidencial.com DYM 29N` |
| Target Point | `https://www.targetpoint.es/` · El Debate | `site:targetpoint.es encuesta 29N`; `site:eldebate.com Target Point 29N` |
| Invymark | `https://www.invymark.es/` · La Sexta | `site:invymark.es encuesta 29N`; `site:lasexta.com Invymark 29N` |
| GESOP | `https://www.gesop.net/` · El Periódico | `site:gesop.net encuesta 29N`; `site:elperiodico.com GESOP 29N` |

## Prioridad 2 — oportunidades

| Casa | Fuente pública | Búsqueda sugerida |
|---|---|---|
| Ipsos | `https://www.ipsos.com/es-es` | `site:ipsos.com/es-es encuesta 29N` |
| Celeste-Tel | `https://www.celeste-tel.es/` · elDiario.es | `site:celeste-tel.es encuesta 29N`; `site:eldiario.es Celeste-Tel 29N` |
| Opina 360 | `https://www.opina360.es/` · Antena 3 | `site:opina360.es encuesta 29N` |
| Simple Lógica | `https://www.simplelogica.com/` · elDiario.es | `site:simplelogica.com encuesta 29N` |
| Hamalgama Métrica | `https://www.hamalgametrica.com/` · OKDiario | `site:hamalgametrica.com encuesta 29N` |
| KeyData | `https://www.keydata.es/` | `site:keydata.es encuesta 29N` |
| YouGov | `https://yougov.es/` | `site:yougov.es 29N` |

## Medios que publican tablas

| Medio | Búsqueda |
|---|---|
| El Mundo | `site:elmundo.es encuestas 29N`; `site:elmundo.es Sondeo 29N` |
| La Razón | `site:larazon.es encuesta 29N` |
| elDiario.es | `site:eldiario.es encuesta 29N` |
| Onda Cero | `https://www.ondacero.es/elecciones/generales/encuestas/` |
| El Confidencial | `site:elconfidencial.com encuesta 29N` |
| El Debate | `site:eldebate.com encuesta 29N` |
| La Sexta | `site:lasexta.com encuesta 29N` |
| El Periódico | `site:elperiodico.com encuesta 29N` |
| ABC | `site:abc.es encuesta 29N` |
| La Vanguardia | `site:lavanguardia.com encuesta 29N` |
| COPE | `site:cope.es encuesta 29N` |
| EITB | `site:eitb.eus encuesta 29N` |

## Contraste, no fuente

- **ElectoPromedio** y agregadores similares: solo para localizar piezas; no se
  usan como sondeo.
- **Política Sin Ruido**: contraste de casas y metadatos; no entra en la media.
- **Onda Cero**: compilación; no tiene `sample` en todas las piezas. Se usa solo
  cuando la ficha permite identificar muestra y campo.

## Flujo de alta

1. Localizar la pieza y abrir la fuente primaria.
2. Anotar casa, medio, fecha de publicación, campo, muestra, método y URL.
3. Añadir a `data/entrada_sondeos.csv` con una fila por partido.
4. Ejecutar `scripts/import_polls.py` y las comprobaciones.
5. Regenerar; verificar salud, media, rango e IQR.
6. Si no hay muestra, marcar `sin ficha`; no tratarla como equivalente.

## Reglas de cierre

- No enviar solicitudes de microdatos por esta lista.
- No llamar, no usar DMs, no eludir formularios.
- No republicar tablas ni gráficos de casas sin autorización.
- No añadir más de un tracking de la misma casa el mismo día.
- No cambiar el agregado por una pieza aislada.
