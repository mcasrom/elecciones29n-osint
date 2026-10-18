# Participación y resultados provinciales · búsqueda de fuente (18-oct-2026)

## Objetivo

Desbloquear dos módulos:

- **M5 Meteorología × participación**: requiere participación por provincia.
- **Votos↔escaños provinciales 2023**: requiere votos y escaños por provincia.

## Intentos

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

No hay una fuente oficial accesible por HTTP para participación provincial ni
para votos↔escaños provinciales. **No se inventan datos ni se usan datasets no
oficiales.**

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
