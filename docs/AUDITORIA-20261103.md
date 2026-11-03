# Auditoría 29N — 2026-11-03

Base: web **v0.11.2** (build posterior a la revisión de las 07:15). La crítica
externa se contrastó contra `web/data/latest.json`, `data/polls_history.csv`,
el generador y los tests. No se aplican cambios de scoring ni de datos.

## P0 aplicado

### 1. AVE sin fuente

Se retiró el hito sin fuente primaria. La fuente oficial del **112 de
Castilla-La Mancha** (nota de 2-nov-2026) confirma **69 fallecidos**, no 68.
Se reincorpora como contexto, con enlace primario y sin atribuirle cambios en
la media.

### 2. Blackout

- Fechas: **24–28 nov 2026**, inclusivas (`agg/blackout.py`).
- Nuevo `scripts/blackout_switch.sh`: construye una copia de staging, aplica
  `write_blackout_site`, valida que no queden agregados ni OG y publica.
- Cron de madrugada: **00:00 del 24–28 nov**, no a las 06:15.
- Retira además de `latest/robustez/status/changelog`:
  - todas las `og*.png` de la raíz y de `og/`;
  - `lideres.html`, `comportamiento.html`;
  - `data/cis_lideres_2026.json`, `data/cis-m4-2026.json`,
    `data/cis-m4-2023.csv`.
- `run_daily_server.sh` ya no regenera OG durante blackout y no exige
  `robustez.html` en la comprobación posterior.
- `alertas_29n.py` tiene guarda explícita 24–28.
- `campaign_digest.py` termina el 23 y `social_queue.py` ya tenía guarda.
- Pruebas: `blackout_switch.sh --simulate-dry` y
  `tests/test_blackout_site.py`.

**Pendiente externo, manual:** artículo del blog, enlaces desde FIMI,
publicaciones sociales ya emitidas, CDN y Wayback. El kill-switch local no
puede borrar copias de terceros. Checklist:

1. Blog: retirar o poner `noindex`/410 al artículo del 29N durante 24–28.
2. FIMI: desactivar el enlace cruzado a `elecciones29n` en
   `casos/electoral/` durante la ventana.
3. Redes: no hay borrado automático; conservar el registro y no republicar.
4. Cloudflare: el switch hace purge de la zona `pruebapublica`.
5. Wayback: solicitar exclusión de la URL durante la ventana; no se puede
   garantizar el borrado de instantáneas ya tomadas.
6. Probar el **20–21 nov** con `--simulate-dry` y, el 24, con `--dry-run`
   dentro de la ventana.

### 3. D’Hondt nacional

Se retiró de la portada el reparto de 350 escaños. El D’Hondt nacional
asignaba todos los escaños a cuatro partidos, dejaba a los territoriales fuera
y producía «otros: 0», que no existe en el Congreso. La tarjeta ahora explica
por qué no se publica y enlaza al método. `/hemiciclo.html` se conserva como
material mecánico con aviso, no como titular.

### 4. Pesos

- Tope por **casa: 25 %**.
- Tope por **fuente: 40 %**.
- Se mantiene una entrada por casa y oleada (`party + date + pollster`).
- Se publica el contraste por casa; no se sustituye la media ponderada.
- En la revisión, Onda Cero pesaba 47,7 % y ElectoPanel 20,6 %. El tope que
  muerde hoy es el de fuente: Onda Cero baja al 40 %. El tope de casa (25 %)
  queda como guarda; la casa mayor queda en ~23 %.

## P1 pendiente

1. **Contador de días:** corregido a diferencia de fechas naturales
   (nov: 26 al 29N y 21 al blackout a 3-nov).
2. **«Sin CIS»:** corregido. La columna usa ahora **45 días** (incluye el CIS
   del 14/10 en la ventana de contraste, excluido del cálculo), se rotula
   **«Sin CIS (45 d)»** y no altera la media principal.
3. **Media móvil centrada:** en el borde derecho es una media truncada.
   Sustituir por suavizado unilateral/Kalman/LOESS con banda, o rotular el
   borde.
4. **Composición 23J:** ya no se llama «vigente»; es resultado oficial 2023.
   Falta explicar que el Sumar de 2023 incluía a Podemos.
5. **FAQ de fuentes:** la FAQ nombra Onda Cero, Electomanía y CIS; el JSON
   incluye también ElDiario, El Español, El Mundo y La Razón. Unificar.
6. **Bloques:** PP+VOX 50,7 % y PSOE+Sumar+Podemos 35,0 % dejan fuera el 14,3 %
   restante. Añadir «sin territoriales» y el no asignado, o retirar el bloque.
7. **Tabla:** suma 98,91 %, no 96,6; ya se explica que no es 100 %. Decidir si
   se normaliza o se mantiene como cuota parcial.
8. **«Otros»:** n=10, no n=5. Mantener la nota de residual.
9. **IQR:** el agregado es 2,1 pp; el 2,4 es el IQR de PSOE. No es un valor
   huérfano.
10. **Gráficos duplicados:** se eliminó el gráfico de «Agregado»; queda uno en
    «Evolución». El dataset ya no se incrusta dos veces.
11. **15.181 encuestados:** es correcto (4.309 + 1.527 + 3.223 + 3.122 +
    2.000 + 1.000). La crítica omitía los 1.527 de ElectoPanel.
12. **Tendencia por casa:** de 10-ago a 2-nov, PP −1,15 pp y VOX +1,7 pp
    (no −1,6 y +1,2). La dirección es correcta; las cifras exactas no.
13. **ElectoPanel:** pesa 20,6 %, no 36 %. El dominante era Onda Cero (47,7 %).
14. **D’Hondt +16 escaños a VOX:** la dirección estructural es correcta, pero
    los 136/65/104 de Sigma Dos son un modelo provincial externo que no se
    puede reproducir con este repo. No usar esas cifras como nuestras.
15. **AVE:** fuente primaria 112, **69 fallecidos**; se mantiene como contexto. Las encuestas de la
    media incluyen fechas anteriores y posteriores al 28-O; no se atribuye
    causalidad.

## Reglas que quedan

- Un escaño nacional no se publica como titular sin reparto provincial.
- Una cifra factual sin fuente primaria no se publica.
- Un blackout retira agregados, JSON, OG y derivados; no basta con el HTML.
- Un tope de peso se declara y se prueba; no se renormaliza después.
- Una media con ventana de 14 días no sirve para probar el efecto de un CIS
  que queda fuera de esa ventana.
