# Participación y resultados provinciales · FUENTE ENCONTRADA (18-oct-2026)

## Fuente encontrada

`demo/Elecciones-Congreso.xlsx` (facilitado por el dueño; open data del
Ministerio del Interior). Copiado a **`data/raw/elecciones-congreso.xlsx`**;
SHA-256 en `data/congreso.json`.

- 16 elecciones generales (1977–2023), 52 provincias.
- Por provincia: electores, votantes, votos válidos/nulos/blancos, escaños y
  votos/escaños por partido (familias).
- **Validación**: 2023 participación 66,59 %; 350 escaños; PP 137, PSOE 121,
  VOX 33, SUMAR 31; Madrid 37. Gallagher 5,62.
- **Aviso**: los votos incluyen CERA (PP 8.160.837 aquí vs 8.091.840 en tablas
  que excluyen el voto exterior). Los escaños y la participación coinciden.

## Objetivo

Desbloquear dos módulos:

- **M5 Meteorología × participación**: requiere participación por provincia.
- **Votos↔escaños provinciales 2023**: requiere votos y escaños por provincia.

## Intentos previos (bloqueados)

| Fuente | Resultado |
|---|---|
| `infoelectoral.interior.gob.es` | timeout (portátil y servidor) |
| `interior.gob.es` | 403 Cloudflare |
| `resultados.elecciones.gob.es` | sin respuesta (000) |
| `elecciones.mir.es` | timeout |
| JEC | 200, pero solo enlaza al Interior; PDFs de CERA y Ceuta/Melilla, no provinciales |
| `resultados.elpais.com` | 403 |
| datos.gob.es (API) | sin dataset nacional de participación provincial |
| Wikipedia (página 2023 y anexo) | sin tabla de participación por provincia |
| Wayback Machine (CDX MIR) | sin resultados |

## Conclusión

La fuente oficial **sí existe**: el XLSX de resultados del Interior con datos
provinciales. El acceso HTTP directo a MIR/Interior sigue bloqueado, pero el
archivo permite construir el módulo sin inventar nada.

## Alternativas

1. **Navegador del dueño**: la web oficial puede abrirse manualmente; exportar
   o copiar tablas a un CSV y validarlas (mismo patrón que la noche electoral).
2. **Archivo del Interior** en otro dominio/espejo oficial, si aparece.
3. **JEC**: comprobar si publica actas/resultados provinciales en PDF tras la
   jornada.
4. **Curación manual** de PDFs oficiales: costosa (52 provincias × elecciones),
   pero viable para una sola elección (2023) y para el 29N.

## Qué desbloquea

- Con participación provincial (una o varias elecciones) → estudio de
  meteorología con AEMET.
- Con votos/escaños provinciales 2023 → tabla de disproporcionalidad y
  comparación voto↔escaño.
