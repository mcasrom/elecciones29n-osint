# Sprint de optimización · 18-oct-2026

> Objetivo: dejar `elecciones29n.pruebapublica.com` listo para la campaña
> (13–27 nov) con datos más robustos, medición fiable y una distribución que
> no dependa de publicar a mano.
>
> Duración estimada: **4–5 h** en una sola sesión. Todo lo marcado P0 es lo que
> convierte el MVP en un producto defendible.

---

## Estado de partida (medido 17-oct)

- 8 sondeos en histórico (30-ago → 11-oct), **79 filas** en `polls_history.csv`.
- Solo **2 sondeos** en la ventana de 14 días → `n=2` en la tabla.
- Una única fuente (Electomania). `sample` vacío en todas las filas.
- Web en vivo con tabs, evolución por partido, D'Hondt etiquetado, tema claro/oscuro,
  aviso stale, sitemap/robots/OG/FAQ/IndexNow. GSC ya registrado por el dueño.
- Cron 08:00 con deploy automático. `Linger=no`.

## Definición de "hecho"

- [ ] La media se sostiene con **≥4 sondeos** o muestra un aviso explícito de `n` bajo.
- [ ] Cada sondeo guarda **muestra** y **encuestadora**, y la media las usa.
- [ ] Tests automáticos verdes en local y en `pre-push`.
- [ ] Móvil y tema claro sin defectos de contraste ni desbordes.
- [ ] Una segunda fuente o un canal manual fiable para añadir sondeos.
- [ ] Distribución: un comando publica la tarjeta OG en Mastodon/Bluesky/Telegram.
- [ ] GSC: sitemap leído y al menos 4 URLs "Descubiertas/Indexadas" en 72 h.

---

## P0 — Robustez del dato (2 h)

### 1. Extraer y usar la muestra
- Parsear del texto `Tamaño muestral: 3.141` / `4.125 cuestionarios`.
- Guardar en la columna `sample`; validar rango (200–20.000).
- Ponderar la media por `√n` (menos ruido que el peso lineal) y por recencia
  (vida media 10 días). Si falta `sample`, peso 1.
- **Aceptación:** `latest.json` incluye `weight_basis` y la tabla muestra `n` y `muestra total`.

### 2. Media robusta + aviso de ventana corta
- Calcular **mediana** además de la media; si difieren >1,5 pts, mostrarlo.
- Si `n < 4`, banner discreto: «Ventana con pocos sondeos: interpreta el rango».
- **Aceptación:** con el histórico actual, la web muestra el aviso; con ≥4 no.

### 3. Deduplicación y procedencia
- Columnas nuevas: `pollster` (`ElectoPanel`, `ElectoPromedio`, …) y `kind` (`tracking|average`).
- No mezclar `ElectoPromedio` (media de medias) con paneles: se etiqueta y se excluye
  de la media principal.
- **Aceptación:** existe al menos una fila `kind=average` marcada y excluida; test que lo verifica.

### 4. Tests de verdad
- Convertir `tests/` a `unittest` ejecutable con `python -m unittest discover -s tests`.
- Tests: blackout (4/4), parseo de muestra, ponderación, build smoke (HTML contiene
  canvas de tabs + JSON-LD + og:image), dedup por fecha.
- **Aceptación:** `python -m unittest discover -s tests` devuelve `OK` y cubre los 4 bloques.

---

## P0 — UI y accesibilidad (45 min)

### 5. Contraste en tema claro
- Sustituir colores hardcodeados del SVG (`#b9b9c3`, `#e7e7ea`) por `var(--muted)`/`var(--fg)`.
- Revisar `th`, `.hint`, `.stamp`, `.delta`.
- **Aceptación:** ratio ≥4,5:1 en texto normal (medido con axe o cálculo manual).

### 6. Móvil
- Tablas con `overflow-x:auto`; tabs con scroll horizontal si no caben;
  KPIs y sparks ya responsive.
- **Aceptación:** 360 px sin scroll horizontal de página (solo en la tabla si hace falta).

### 7. Movimiento reducido
- `@media (prefers-reduced-motion: reduce)` → sin animación en `.dot` y `.stale`.
- **Aceptación:** con la preferencia activa, no hay parpadeo.

---

## P1 — Segunda fuente y distribución (1,5 h)

### 8. Canal manual fiable (si el scraping no es viable)
- `scripts/add_poll.py` gana `--pollster`, `--sample`, `--kind` y validación de suma.
- Documentar en `docs/FUENTES.md` cómo añadir un sondeo en 30 s.
- **Aceptación:** alta manual de un sondeo de otra encuestadora visible en el build.

### 9. Explorar una segunda fuente automática
- Candidatas: CIS (barómetros), 40dB, GAD3, Sigma Dos, Simple Lógica.
- Regla: **medir antes de implementar** (una sonda por fuente, sin tocar el pipeline).
- **Aceptación:** decisión documentada (implementar o aplazar) con el motivo medido.

### 10. Lanzador social
- `scripts/publish_card.py`: sube `og.png` a Mastodon + Bluesky + Telegram y
  remite el texto de X (manual), reutilizando `social-poster/`.
- **Aceptación:** `--dry` imprime los textos; ejecución real publica y deja log.

### 11. Calendario electoral visible
- Bloque en la pestaña Agregado: convocatoria (6-oct), campaña (13–27 nov),
  blackout (24–28), jornada (29). Destacar el próximo hito.
- **Aceptación:** el hito mostrado cambia solo con la fecha.

### 12. Enlaces entrantes
- Añadir elecciones29n al blog (`Sidebar.astro` del ecosistema) y al sitemap del apex
  si aplica. UTM `source=analisis`.
- **Aceptación:** enlace en vivo con UTM; GSC detecta la URL.

---

## P2 — Si sobra tiempo (45 min)

### 13. Serie de cambios (RSS)
- `web/cambios.xml`: cada vez que entra un sondeo nuevo. Enlace en el `<head>`.

### 14. Bandas de incertidumbre
- En la vista conjunta, banda min–máx por partido (semitransparente) además de la línea.

### 15. Congreso por provincias (aplazado)
- Requiere datos provinciales que hoy no tenemos. **No hacer** sin fuente.

### 16. Linger
- `sudo loginctl enable-linger miguelc` para que el timer corra sin sesión.
- Verificar con `loginctl show-user miguelc | grep Linger`.

---

## Orden de ejecución sugerido

1. P0.1 muestra + P0.2 robustez + P0.3 procedencia (núcleo del valor).
2. P0.4 tests → `pre-push`.
3. P0.5–7 UI/accesibilidad.
4. P1.8 canal manual, P1.10 social, P1.11 calendario.
5. P1.9 segunda fuente (solo sonda y decisión).
6. P1.12 enlaces; P2 si hay margen.

## Comandos

```bash
# ciclo completo + tests
python -m unittest discover -s tests -v
bash scripts/run_daily.sh

# verificación en vivo (forzando edge)
UA="Mozilla/5.0"; R="--resolve elecciones29n.pruebapublica.com:443:188.114.97.3"
curl -s -A "$UA" $R https://elecciones29n.pruebapublica.com/ | grep -E 'og:image|FAQPage|tab-evolucion'
curl -s -A "$UA" $R https://elecciones29n.pruebapublica.com/sitemap.xml

# purga tras deploy
bash /home/miguelc/Desktop/demo/cf_purge.sh pruebapublica
```

## No-objetivos (para no romper lo que funciona)

- No simular el Senado.
- No presentar D'Hondt como proyección.
- No mezclar señales sociales con la media.
- No añadir backend ni bases de datos en el servidor.
- No tocar `municipal-intel`, FIMI ni el landing más allá del enlace.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| La fuente única se cae o cambia el HTML | Ingesta best-effort + último válido + canal manual |
| Ponderar por muestra con datos incompletos | Peso 1 si falta; registrar `weight_basis` |
| Cambios de copy que rompan el JSON-LD | Test que compara FAQ visible con `FAQPage` |
| Caché de edge sirviendo CSS viejo | `?v=` ya implementado; purga tras deploy |
| Sprint se estira y se toca el motor sin tests | P0.4 antes de tocar nada del pipeline |

---

## Estado al cierre (18-oct-2026, ~08:40 CEST)

**Hecho**
- P0 dato: `sample` extraída y validada; ponderación `√n` + recencia (vida media 10 d);
  mediana; `pollster`/`kind` y exclusión de `ElectoPromedio`; ventana adaptativa a 4
  sondeos con aviso de `n` bajo.
- P0 tests: `tests/` en `unittest` (15 pruebas) + hook `pre-push` (`core.hooksPath`).
- P0 UI: SVG con `var()` (claro/oscuro), tablas con scroll, `prefers-reduced-motion`.
- P1: `add_poll.py` con muestra/encuestadora/kind y validación de suma; calendario
  electoral con próximo hito; launcher social `social-poster/publish_e29n_card.py`
  (verificado en `--dry`); enlace desde el sidebar del blog con UTM; decisión sobre
  la 2.ª fuente en `docs/FUENTES.md` (Wikipedia: viable pero frágil, no integrada).
- P2: `web/cambios.xml` (RSS de nuevos sondeos) enlazado en `<head>` y pie; bandas
  min–máx en el gráfico conjunto (top 3) y en los minigráficos.

**Pendiente**
- Publicar la tarjeta social (requiere OK explícito; el launcher está listo).
- `sudo loginctl enable-linger miguelc` (requiere contraseña; el timer corre con sesión).
- GSC: verificar cobertura (4+ URLs indexadas en 72 h).
- Congreso por provincias: aplazado (sin fuente provincial fiable).
