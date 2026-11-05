# Sprint de mejora — Escenarios 29N

**Fecha:** 5-nov-2026  
**Estado:** planificación, no ejecutado  
**Página viva:** https://elecciones29n.pruebapublica.com/escenarios.html  
**Último commit de la página:** `7317d15`

## Objetivo

Mejorar la **honestidad y la precisión del escenario**, no añadir más gráficos.
La página ya explica qué es un percentil y qué no; el límite está ahora en el
motor y en la calidad de los datos.

La prioridad es que el rango p10–p90 deje de ser artificialmente estrecho y que
el swing provincial no sea uniforme por decreto.

## Estado de partida medido

- **12 sondeos · 8 casas** en la foto actual; corte **5-nov-2026**.
- `polls_history.csv`: **868 filas**, **120 sondeos únicos**, **18 casas**,
  ventana 2025-09-01 → 2026-11-02.
- `sample` informado en **158/868 filas** (18 %). No se puede fingir error de
  muestreo donde no hay `n`.
- **26 filas** con `kind=average` (`ElectoPromedio`). Pueden ser una media de
  medias y no deben entrar como un sondeo más sin declararlo.
- Monte Carlo: **5.000 iteraciones**; en cada una se toman **12 sondeos con
  reemplazo**, se promedian y se aplica el swing uniforme.
- Escenario actual: PP 136 (132–139) · PSOE 110 (107–114) · VOX 66 (65–67).
- Bloques: PP+VOX 202 (198–205) · PSOE+Sumar 118 (115–122) ·
  PSOE+Sumar+territoriales 147 (144–151).
- Backtest 2019: **MAE 1 escaño** en PSOE, PP, VOX y Cs.
- Página: **128 tests OK**, build y validación correctos.

## Lo que no se hará

- No inventar sondeos provinciales.
- No publicar “probabilidad de investidura”.
- No presentar el p50 como resultado probable.
- No mezclar 2019, 2023 y 2026 en una sola cifra.
- No ocultar que el modelo es un escenario de swing uniforme.
- No añadir más gráficos hasta arreglar la incertidumbre.

---

## Sprint 1 — P0 · Incertidumbre y provincia (≈4 h)

### E0. Auditoría de datos y del Monte Carlo (30 min)

**Problema:** el Monte Carlo promedia 12 sondeos en cada iteración; eso reduce
la dispersión. Además, `ElectoPromedio` puede estar entrando como un sondeo
individual y el escenario determinista no usa exactamente el mismo universo que
el Monte Carlo.

**Tareas:**

- [ ] Comparar el universo de `latest.json` con el de `polls_history.csv`.
- [ ] Verificar si `kind=average` entra en `load_poll_groups`; excluirlo o
      separarlo con etiqueta.
- [ ] Detectar duplicados por `(date, pollster, party)`.
- [ ] Medir cuántos sondeos tienen `sample` y en qué casas.
- [ ] Escribir `docs/AUDITORIA-INCERTIDUMBRE-20261105.md` con:
      universo, exclusiones, cobertura de `sample`, rangos actuales.

**Aceptación:**

- [ ] El informe deja claro qué datos entran y qué no.
- [ ] Ningún `average` se cuenta como sondeo individual sin aviso.
- [ ] El escenario determinista y el Monte Carlo usan el mismo universo o se
      documenta la diferencia.

### E1. Incertidumbre jerárquica (1,5 h)

**Problema:** el p10–p90 actual mide la dispersión de una media de 12 sondeos,
no la incertidumbre de la estimación. El rango es demasiado estrecho para la
calidad del dato.

**Tareas:**

- [ ] Diseñar un bootstrap jerárquico:
      sondeo → casa → error de muestreo (solo si hay `n`) → cuota nacional.
- [ ] Si no hay `n`, usar dispersión entre sondeos/casas y declararlo; no
      inventar error de muestreo.
- [ ] Mantener una versión con una encuesta por iteración como contraste.
- [ ] Comparar rangos antiguos y nuevos; no elegir el más estrecho.
- [ ] Mantener `prob_mayoria_176` **solo interno** hasta revisión.

**Aceptación:**

- [ ] Test sintético de reproducibilidad con semilla fija.
- [ ] Informe de sensibilidad: rango actual vs rango nuevo.
- [ ] La página no afirma “100 %” ni “probabilidad electoral”.
- [ ] Si el rango se ensancha, se actualiza la narrativa pública.

### E2. Swing provincial histórico (2 h)

**Problema:** el swing uniforme supone que cada partido se mueve igual en todas
las provincias. Es la simplificación más fuerte del modelo.

**Tareas:**

- [ ] Calcular el swing provincial 2019 → 2023 por partido y provincia.
- [ ] Encogerlo hacia el swing nacional: `Δ_prov = λ·Δ_hist + (1−λ)·Δ_nac`.
- [ ] Elegir `λ` con backtest, no a ojo; probar 0, 0,25, 0,5, 0,75.
- [ ] Resolver el mapeo de partidos y coaliciones; no inventar etiquetas.
- [ ] Repetir el backtest 2019 y comparar MAE con el modelo uniforme.
- [ ] No aplicar cambios a la página pública hasta revisar el resultado.

**Aceptación:**

- [ ] El backtest no empeora de forma injustificada.
- [ ] Está documentado qué provincias cambian y por qué.
- [ ] No se usan datos provinciales de 2026 que no existan.
- [ ] El resultado sigue siendo un escenario, no una proyección.

---

## Sprint 2 — P1 · Agregación y backtest (≈2 h)

### E3. Agregación de sondeos (1 h)

- [ ] Ponderar por recencia (vida media 10 días).
- [ ] Ponderar por `√n` cuando exista `sample`; si falta, peso 1.
- [ ] Separar efecto de casa y no mezclar métodos distintos.
- [ ] Alinear la media determinista con el Monte Carlo.
- [ ] Test: un sondeo viejo pesa menos; un `average` no duplica.

### E4. Backtest ampliado (1 h)

- [ ] Añadir 2015 y 2016 con mapeo explícito de partidos.
- [ ] Medir MAE por partido y por bloque, no solo total.
- [ ] No ajustar parámetros con 2026; usarlo solo como escenario.
- [ ] Documentar qué elecciones no se pueden comparar por cambio de partidos.

---

## Sprint 3 — P2 · Página (≈1 h)

### E5. Sensibilidad y provincias decisivas

- [ ] Tabla “qué cambia la mayoría” con ±1, ±2 y ±3 pp.
- [ ] Top 10 provincias por margen o por escaño decisivo.
- [ ] CSV además de JSON.
- [ ] Enlace desde el bloque de bloques, sin duplicar la narrativa.
- [ ] No añadir nuevos gráficos grandes.

**Aceptación:**

- [ ] La página sigue sin “probabilidad” ni “predicción” en el titular.
- [ ] Los nuevos datos tienen fecha y fuente.
- [ ] `validate_site` y `check.sh` pasan.
- [ ] Móvil y contraste revisados.

---

## Definición de “hecho”

- [ ] Tests del modelo y del build en verde.
- [ ] `scripts/validate_site.py` y `scripts/check.sh` OK.
- [ ] Comparación escrita: rango viejo vs nuevo y backtest viejo vs nuevo.
- [ ] Página pública actualizada con la narrativa correcta.
- [ ] Sin `100 %` ni “probabilidad electoral” en la página.
- [ ] Commit y push; caché purgada.
- [ ] Documento de auditoría enlazado desde el sprint.

## Riesgos y decisiones

- **Muestra incompleta:** no se puede modelar error de muestreo en el 82 % de
  las filas. Se declara y se usa dispersión entre casas.
- **Sobreajuste:** elegir `λ` con 2019 y validar con 2023/2019, no con 2026.
- **Cambio de sistema de partidos:** Sumar, Cs y coaliciones impiden comparar
  todas las series; se compara solo lo que tenga etiqueta estable.
- **Falsa precisión:** un rango más ancho no es un fracaso; es información.
- **Alcance:** nada de pactos, investidura ni probabilidad de gobierno.

## Archivos de referencia

- `seat_model.py` — modelo, swing, D’Hondt, Monte Carlo.
- `data/polls_history.csv` — 868 filas, 120 sondeos, 18 casas.
- `data/congreso.json` — resultados oficiales 2019/2023.
- `data/escanos_2026.json` — escaños por provincia.
- `backtest.py` — backtest abril → noviembre 2019.
- `tests/test_monte_carlo.py`, `tests/test_backtest.py`.
- `elecciones29n-osint/data/escenarios.json` — copia pública congelada.
- `elecciones29n-osint/gen/build.py` — gráficos y contexto.
- `elecciones29n-osint/gen/templates/escenarios.html.j2` — página.

## Primer paso

Ejecutar **E0** y escribir la auditoría antes de tocar el modelo. Sin ese
informe, cualquier mejora del rango sería otra caja negra.
