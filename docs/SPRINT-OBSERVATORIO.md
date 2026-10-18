# Sprint del observatorio electoral (a partir de la auditoría estratégica)

> Regla: no se abandona el agregador de sondeos. Se añade una capa de datos
> oficiales alrededor de él, con la misma disciplina: cada cifra rastrea a su
> fuente, cada estimación muestra su incertidumbre y cada hipótesis se distingue
> de un resultado.
>
> Prioridad: **P0** = datos oficiales ya disponibles · **P1** = valor alto con
> datos existentes · **P2** = requiere curación o investigación.

---

## Conclusiones de la auditoría (validadas)

1. **El diagnóstico es correcto.** La web responde «¿qué dicen las encuestas?».
   La oportunidad es responder también «¿quién puede votar, quién participa y
   qué sabemos del comportamiento electoral?» sin convertirse en cuatro webs.
2. **El orden propuesto es el adecuado**: censo → participación → territorio →
   comportamiento → factores externos. Pero se ajusta: censo y participación
   primero (oficiales y de bajo riesgo); demografía × voto después (curación y
   muestras); meteorología al final (investigación, no dashboard).
3. **Los datos del censo están disponibles y son descargables** (verificado
   18-oct): el INE publica XLSX oficiales del 29N. No hace falta scraping.
4. **Tres precisiones metodológicas** que hay que aplicar ya:
   - La **suma de entrevistados** no es «una muestra única»: son muestras
     distintas en fechas y metodologías distintas. Etiquetar como
     «entrevistas sumadas», no como tamaño muestral del agregado.
   - El **rango mín–máx** no es un intervalo de confianza: es dispersión
     observada entre sondeos.
   - El **censo por edad/sexo** describe quién puede votar, no a quién vota.
     No cruzar cuotas del censo con porcentajes de voto.
5. **Riesgo de la ampliación**: una granja de gráficos. Cada módulo debe
   responder una pregunta concreta y publicar su dataset normalizado.

## Fuentes verificadas (18-oct-2026)

| Dato | Fuente | Formato | Estado |
|---|---|---|---|
| Censo total y por provincia (CER+CERA) | INE CEL · `Elecgral_2026_cc_tab2/3.xlsx` | XLSX | ✅ descargado y validado (total 38.728.356) |
| Electores en España por sexo y edad | INE CEL · `Elecgral_2026_cc_tab9/10/11.xlsx` | XLSX | ✅ (CER: 35.958.711; **no incluye CERA**) |
| CERA por país | INE CEL · `tab6/7/8.xlsx` | XLSX | ✅ |
| Nuevos electores desde 23-J-2023 | INE CEL · `tab12.xlsx` | XLSX | ✅ (1.615.127; por provincia) |
| Cifras de prensa (contraste) | La Moncloa, 14-oct-2026 | HTML | ✅ 38.728.356 / 35.958.711 / 2.769.645 / 1.615.127 |
| Participación y resultados históricos | Ministerio del Interior (archivo de resultados) | HTML/JSON | ⏳ a normalizar (M2) |
| Voto por correo | INE CEL (`vc_tab*`) | XLSX | ⏳ URL a corregir |

**Nota**: la tabla de edad/sexo es solo de residentes en España (CER). El censo
total incluye 2.769.645 residentes en el extranjero, para los que esta tabla no
da edad/sexo. El gráfico debe decirlo.

---

## M1 · Censo 29N (P0) — ✅ HECHO 18-oct (`8851a8d`)

**Pregunta**: ¿quién forma el electorado del 29N?

- Ingesta de los XLSX del INE (tab2/3/9/10/11/12) → `data/censo_2026.json` + CSV.
- Normalización: `ambito` (nacional/CCAA/provincia), `sexo`, `grupo_edad`,
  `cer`, `cera`, `total`, `nuevos_electores`.
- Guardar **procedencia**: URL, fecha de descarga y SHA-256 del XLSX.
- UI: página `/electorado.html` con:
  - 4 cifras oficiales (total, España, extranjero, nuevos electores).
  - Barras por grupo de edad y sexo (CER), con nota de ámbito.
  - Tabla por provincia ordenable (CER, CERA, total).
  - Enlace al XLSX original y a los datos normalizados.
- **Tests**: suma de provincias = total; CER + CERA = total; suma por edad y
  sexo = CER; nuevos electores = 1.615.127.
- **Aceptación**: las 4 cifras cuadran con La Moncloa; la página declara que
  edad/sexo no cubre el extranjero; 200 en vivo y en sitemap.

## M2 · Participación histórica (P1) — ✅ HECHO 18-oct (`f75b33a`)

**Pregunta**: ¿quién participa y cómo ha cambiado?

- Serie 1977–2023 (generales): participación, abstención, votos válidos/nulos.
- Desglose por CCAA/provincia si el archivo del Interior lo permite.
- Normalizar a `data/participacion.csv` con `eleccion`, `ambito`, `participacion`.
- UI: gráfico de línea + tabla + comparación 29N cuando exista (post-electoral).
- **Tests**: 23-J-2023 nacional ≈ 66,6 % (verificar contra fuente); suma de
  provincias = nacional.
- **Aceptación**: cada punto enlaza a la fuente; no se proyecta participación.

## M3 · Territorio y representación (P1) — ✅ HECHO 18-oct (`bdda73e`)

**Pregunta**: ¿por qué un voto vale distinto según dónde se emite?

- Electores y escaños por provincia/circunscripción.
- Resultados 2023 por provincia (votos y escaños) para mostrar la diferencia
  entre % nacional y representación.
- Explicador del sistema: 350 diputados, mínimo 2 por provincia, Ceuta/Melilla.
- **No** hacer una simulación provincial sin encuestas provinciales: seguir con
  D'Hondt nacional etiquetado como simulación.
- **Aceptación**: tabla votos↔escaños 2023 verificada; explicador sin proyección.

## M4 · Comportamiento por grupos (P2, ~6–8 h, curación)

**Pregunta**: ¿qué sabemos de las preferencias por edad, sexo, renta o ideología?

- Solo con **cross-tabs publicados** (CIS, medios) y `n` visible.
- Cada gráfico: fuente, fecha, muestra, margen y advertencia de comparabilidad.
- Prohibido cruzar cuotas del censo con porcentajes de voto.
- **Aceptación**: cada estimación tiene fuente y n; ninguna conclusión causal.

## M5 · Meteorología y participación (P2, investigación)

**Pregunta**: ¿la lluvia/frío se asocian con cambios de participación?

- Estudio histórico por provincia: AEMET + participación oficial.
- Publicar primero el **método** (variables, controles, limitaciones).
- Sin previsiones convertidas en participación estimada.
- **Aceptación**: informe con tamaño de efecto e incertidumbre, no un dashboard.

---

## Documentación y páginas institucionales — ✅ HECHO 18-oct (`31af075`)

- `metodologia.html` reescrita con los 4 módulos y reglas comunes.
- `fuentes.html` con tabla de fuentes, catálogo de datos y licencias.
- Nuevas `/apoyo.html` (Ko-fi, compartir, colaboración) y `/sobre-mi.html` (autor, principios, proyectos, contacto).
- Subnavegación en la portada y footer; sitemap 10 URLs.

## Orden de ejecución

1. **M1 censo** (datos listos, bajo riesgo) → enlazar desde la portada.
2. **M2 participación** (oficial, alto valor).
3. **M3 territorio/representación** (explica el sistema).
4. **M4 demografía × voto** (solo curado).
5. **M5 meteorología** (investigación, al final).

## Correcciones inmediatas al proyecto actual (30 min)

- Etiquetar «entrevistados» como **«entrevistas sumadas»** (no una muestra única).
- Añadir nota: **el rango no es un intervalo de confianza**.
- Enlazar «Electorado» y «Participación» desde la nav cuando existan.

## Medición

- UTM por módulo (`utm_source=electorado`, `utm_medium=internal`).
- Lectura de accesos con el clasificador existente (humano vs máquina), sin
  analítica de terceros.
- Criterio de éxito: módulos con retorno >0 y tiempo en página superior a la
  media del sitio; no vanity metrics.

## No-objetivos

- No predecir el resultado ni la participación del 29N.
- No atribuir preferencias por demografía.
- No convertir correlaciones territoriales en causalidad.
- No mezclar encuestas con señales sociales.
- No añadir backend: todo estático y datos abiertos.
