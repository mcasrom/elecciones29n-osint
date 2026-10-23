# Changelog

## 0.10.5 — 2026-10-23

- **Autochequeo de privacidad**: la política se ajusta a lo que hace el servicio: responsable y contacto, versión del consentimiento (`2026-10-23-v1`), retención de logs (14 días) y copias (30 días), y encargados con enlaces a los DPA de Resend y Cloudflare (SCC/DPF).
- **Baja con minimización**: al darse de baja se borran página, UTM y referrer; solo quedan email y fecha en la lista de exclusión. El alta guarda la versión del consentimiento.
- **Límites declarados**: autochequeo técnico, no dictamen jurídico; si hay actividad económica, faltarían los datos de la LSSI.

## 0.10.4 — 2026-10-23

- **Doble opt-in a prueba de escáneres**: `GET /api/confirm` y `GET /api/unsubscribe` ya no cambian el estado; muestran una página con botón y la acción exige `POST`. Un prefetch del correo (Outlook, antivirus, proxy) no puede confirmar ni dar de baja por su cuenta.
- **CSP del servicio**: `form-action 'self'` para permitir el formulario de confirmación.
- **Copia de seguridad**: el build diario guarda `data/subs.db` en `~/backups/elecciones29n/` (30 días, permisos `0600`).

## 0.10.3 — 2026-10-23

- **Aviso por correo**: formulario en portada, robustez, territorio y fichas provinciales; **doble opt-in** y baja en un clic. Guarda solo email, estado, fecha, página, UTM y host del referrer; sin cookies ni IP. Retención de pendientes: 30 días.
- **API**: `POST /api/subscribe`, `GET /api/confirm`, `GET /api/unsubscribe` y `GET /api/health` en `scripts/subs_api.py` (puerto 3031, PM2 `elecciones29n-api`, SQLite `data/subs.db`, rate limit y `RESEND_DRY_RUN` para pruebas).
- **Privacidad**: `/privacidad.html` con responsable, finalidad, base jurídica, conservación, Resend y derechos; enlazada en nav, pie y formularios.
- **Medición**: `scripts/subs_report.py` agrega altas por fuente, página, UTM, referrer y día, sin PII.
- **Resultados 2023**: orden estable por escaños, votos y partido (antes cambiaba entre builds por empate).
- **Operación**: el build diario verifica `/privacidad.html`; el canario comprueba la página y `/api/health`. 102 tests.

## 0.10.2 — 2026-10-23

- **Blackout 24–28 nov**: no se conserva la media congelada. La portada, `/robustez.html` y `/novedades.html` pasan a un aviso legal; se retiran `data/latest.json`, `data/robustez.json` y `og-robustez.png`; el canario y el validador verifican que no queden publicados. El 29 se restablece.
- **Portada**: la brecha PP–PSOE muestra también la media sin CIS (`+5.2`). La simulación D'Hondt se etiqueta como «bloques» y advierte de que solo incluye partidos estatales: ERC, Junts, EH Bildu y PNV no se simulan y su ausencia infla PP/PSOE; no es la composición real del Congreso.
- **Operación**: `needs.py` y la auditoría detectan el blackout y no generan falsos avisos por falta de `latest.json`. 94 tests.

## 0.10.1 — 2026-10-23

- **Ventana por fecha, no por hora**: la media usa 14 días naturales contando hoy (y 45/90 en sus ventanas). Un sondeo del día 14 ya no entra a las 23:00 y desaparece a las 08:00; el peso por recencia también se calcula en días naturales. Test de invariancia 08:00/23:00.
- **Frente Amplio → SUMAR**: ElectoPanel del 18-oct publica «Frente Amplio … 4,9 %»; el parser solo buscaba «Sumar» y la fila se descartaba (suma 87,3). Se mapea FA a SUMAR, se amplía la ventana de captura de la cifra y se backfilla la fila (suma 92,2).
- **Sin doble conteo territorial**: ERC, Junts, Bildu y PNV salen de la tabla principal (en Onda Cero ya están dentro de «Otros») y se publican aparte. La tabla muestra su suma y distingue casas de 45 d y de 14 d; `latest.json` añade `table_sum`, `n_houses_window`, `n_houses_recent` y `sample_n`.
- **Etiquetas y auditoría**: «Datos suficientes/frágiles/insuficientes»; la muestra se lee como «3/9 con muestra (12.291 encuestados)». `audit_datos.py` exige 90–110 en sondeos tracking, comprueba la suma de la tabla y las casas de la media. 93 tests y 233 comprobaciones offline.

## 0.10.0 — 2026-10-22

- **Peso de cada sondeo**: la portada indica cada día qué casa concentra el peso de la media; `/robustez.html#peso` publica el reparto completo (cuota por casa y por sondeo, muestra y fecha). El peso combina recencia y √n, y una cuota alta avisa de que la media sigue a esa casa.
- `latest.json` y `robustez.json` incluyen `weights` (casas y sondeos).
- Metodología: corregidas dos etiquetas HTML mal cerradas y enlazado el reparto diario.

## 0.9.0 — 2026-10-22

- **Circunscripciones**: corregido el escaño marginal. La «primera candidatura sin escaño» ya no es el siguiente cociente (que podía tener escaño); el margen son los votos adicionales mínimos para obtener uno, recalculando D'Hondt y el umbral del 3 %.
- **Fuente oficial**: los resultados provinciales se atribuyen al Ministerio del Interior (XLSX oficial, CC BY 4.0, actualización 2024-01-01) en fichas, índice y JSON; se retira «archivo facilitado».
- **Plural**: «1 diputado» / «N diputados» en títulos, descripciones y tarjetas.
- **Sondeos**: la FAQ y las fuentes aclaran Onda Cero, Electomanía y CIS; se declara que no se reutilizan tablas, gráficos ni bases de terceros.
- **Portada**: «serie completa» pasa a «últimos 90 días», que es la ventana real de la serie.
- **Novedades**: página `/novedades.html` generada desde este changelog, con enlace en la navegación y el pie.

## 0.8.5 — 2026-10-18

- **Navegación**: `Factores` y `Comportamiento` pasan a la barra común de todas las páginas (antes solo estaban en el submenú de la portada).

## 0.8.4 — 2026-10-18

- **Auditoría de datos reproducible** (`scripts/audit_datos.py`): **202 comprobaciones, 0 fallos críticos** (offline + online). Verifica sondeos, censo, participación, territorio, M4, M5, etiquetas de UI y fuentes (Onda Cero/CIS/Electomania).
- `check.sh` ejecuta la auditoría offline; `docs/AUDITORIA-DATOS.md` documenta alcance y límites.

## 0.8.3 — 2026-10-18

- **SEO**: JSON-LD por página (`Dataset` en participación, territorio, M5 y M4; `WebPage` en método/fuentes/límites/apoyo/acerca) en vez del Dataset de sondeos en todas.
- **`favicon.ico`** (Googlebot-Image pedía `/favicon.ico` y daba 404).
- Validador: comprueba JSON-LD por página y `favicon.ico`; canario incluye favicon.
- Auditoría de sitemap/indexado: 13 URLs, todas 200 con Googlebot; Googlebot/Bingbot/Applebot rastrean. Nuevas páginas pendientes de recrawl/GSC.

## 0.8.2 — 2026-10-18

- **Anexo de transparencia meteorológico** en `/factores.html`: tabla nacional por elección (16 filas) en un `<details>` colapsable, con descarga JSON/CSV nacional y CSV provincial. Sin mapa ni cambios en la portada.

## 0.8.1 — 2026-10-18

- **Auditoría de métricas**: `metrics.py` como fuente única (MA 14 d, resumen de tarjeta, periodo).
- Fix: la tarjeta de Evolución usaba el **último sondeo** (CIS) y un delta contra el primer sondeo de otra casa. Ahora cifra y delta son **MA 14 d**; periodo real.
- Tests (`test_metrics.py`) y validador recalculan la MA y el periodo desde `latest.json`.

## 0.8.0 — 2026-10-18

- **M4 v1**: voto declarado en 2023 por **edad, sexo e ideología** (CIS 3582, n=5.025), base de votantes a partidos, **N ponderado** y **celdas n<30 suprimidas**.
- Página `/comportamiento.html` con tablas, fuente y límites; JSON/CSV abiertos.
- Corrección de la agregación de «Otros» y de la normalización a voto a partidos.

## 0.7.0 — 2026-10-18

- **Onda Cero**: 94 sondeos de 14 casas integrados como fuente secundaria (sondeos individuales, no su promedio; fecha de publicación).
- **CIS**: barómetros de septiembre (n=4.042) y octubre (n=5.025) añadidos a mano con PDF y muestra.
- **Contraste por casa**: última encuesta de cada casa en 45 días con peso igual (14 casas), frente a la media por sondeo.
- Normalización de nombres (`Podemos`/`PODEMOS`, `Bildu`/`BILDU`, `Junts`/`JUNTS`); `n_polls` cuenta sondeos, no fechas.
- «Otros» se excluye de KPIs, gráficos y simulación; se mantiene en la tabla.

## 0.6.0 — 2026-10-18

- **M5 v1**: meteorología × participación con panel provincia × elección (806 obs, 16 elecciones), AEMET OpenData y OLS con efectos fijos y SE agrupados.
- Resultados en `/factores.html` y `data/m5-results.json`: asociación negativa modesta; en 2004–2023, −0,041 pp/mm (p=0,007). Sin afirmación causal.

## 0.5.0 — 2026-10-18

- **Datos provinciales**: 16 elecciones × 52 provincias; participación 1977–2023 con selector y comparación con la media nacional.
- **Votos↔escaños 2023** en `/territorio.html`, con índice de Gallagher y aviso CERA.
- **PWA**: aviso de nueva versión con Recargar/×; el cierre se recuerda por versión y pestaña. Fix: `[hidden]` ya no queda anulado por CSS.
- `ingest/congreso.py` y `data/raw/elecciones-congreso.xlsx` como fuente reproducible.

## 0.4.0 — 2026-10-18

- **PWA-lite**: manifest, iconos, service worker network-first y aviso de nueva versión.
- **Observatorio**: censo (INE), participación (JEC), territorio (BOE) y página de factores.
- **Sondeos**: media ponderada, mediana, salud de la muestra y alta manual (CSV/comando).
- **Documentación**: método, fuentes, rutina semanal, noche electoral y registro de fuentes.
- **Calidad**: staging + validación + swap atómico + canario en vivo; 34 tests.
- **Versión en el pie** y `version.json` público.

## 0.3.0 — 2026-10-17

- Agregado de sondeos con rango, evolución, Congreso y Senado.
- SEO: sitemap, robots, OG, JSON-LD, FAQ e IndexNow.
- Tema claro/oscuro y aviso de datos desactualizados.

## 0.2.0 — 2026-10-17

- Ingesta real de Electomania, blackout electoral y primeros tests.

## 0.1.0 — 2026-10-17

- MVP: ingesta, agregado, build estático y despliegue.
