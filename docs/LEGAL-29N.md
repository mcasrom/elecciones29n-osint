# Nota legal — Observatorio 29N

> **No es un dictamen jurídico.** Es una lista de comprobación interna para
> ordenar riesgos y decisiones. Antes de publicar cambios legales conviene
> revisarlos con un profesional.
>
> Estado: **23-oct-2026**. Próxima revisión obligatoria: **antes del 24-nov-2026**
> (inicio del blackout electoral).

## 1. Identidad y naturaleza del proyecto

- **Titular**: Miguel Castillo, proyecto individual.
- **Sitio**: `https://elecciones29n.pruebapublica.com`.
- **Código**: `https://github.com/mcasrom/elecciones29n-osint`, AGPL-3.0.
- **Qué es**: agregador de sondeos ya publicados y datos oficiales (censo,
  participación, escaños, resultados). **No es un pronóstico ni un sondeo
  propio**; no estima intención de voto.
- **Cómo se financia**: apoyo voluntario vía Ko-fi. Sin publicidad, sin
  patrocinio político y sin venta de datos.
- **Precaución**: no presentarlo como asociación, fundación ni entidad sin
  ánimo de lucro registrada. “Proyecto individual sin ánimo de lucro” describe
  la finalidad, no una forma jurídica.

## 2. Onda Cero — compilación de encuestas

- **Uso actual**: sondeos individuales de
  `https://www.ondacero.es/elecciones/generales/encuestas/`: fecha de
  publicación, casa, porcentajes y muestra cuando consta.
- **No se usa**: su tabla completa, gráficos, base de datos, microdatos ni
  textos.
- **Qué se publica**: media propia, rango mínimo–máximo, método y JSON/CSV
  agregados, con enlace a la fuente.
- **Estado**: solicitud **enviada** el 23-oct-2026 (08:30 UTC), `delivered`;
  pendiente de respuesta. Registro en
  `docs/ONDA-CERO-AUTORIZACION-BORRADOR.md`.
- **Límite**: la autorización de Onda Cero, si llega, no cubre por sí sola los
  derechos de cada casa encuestadora sobre sus propios sondeos. Si su
  condición es enlazar/citar, mantener el enlace individual; si exige retirar,
  hacerlo.
- **Si no autorizan**: retirar sus filas de `data/polls_history.csv`,
  recalcular la media y regenerar. No dejar sus sondeos en los ficheros
  públicos.
- **Atribución**: usar la mención que indiquen; por defecto, enlace a la página
  de encuestas y a la pieza original cuando exista.

## 3. Otras fuentes de sondeos

| Fuente | Uso | Riesgo / pendiente |
|---|---|---|
| **Electomanía** | API pública de WordPress; se enlaza cada sondeo | **Autorizado por escrito el 23-oct-2026**: uso limitado y no sustitutivo de los datos en abierto del **ElectoPanel** (voto y escaños), histórico incluido, sin coste. Condiciones: **«Fuente: Electomanía»**, **enlace a cada pieza**, **escaños publicados sin recalcular** y no reproducir tablas/gráficos/microdatos. |
| **Electomanía · hemiciclo** | El hemiciclo **no usa sus escaños publicados**; aplica D'Hondt a la media agregada de voto, que incluye sondeos de varias casas. | Riesgo interpretativo: derivar escaños de porcentajes que incluyen ElectoPanel podría leerse como recálculo. Mitigación: etiqueta «simulación propia», sin atribuir a la casa. Si hay objeción, excluir Electomanía del cálculo del hemiciclo o retirar esa capa; la media principal no cambia. |
| **CIS** | PDF del barómetro, añadido a mano con muestra y fecha | Reutilización permitida con condiciones: citar «Origen: CIS», no desnaturalizar, no sugerir patrocinio y conservar fecha/metadatos. Guardar nº de estudio y ficha técnica. |
| **Política Sin Ruido** | Contraste metodológico, no fuente de la media | Revisar condiciones si se incorporan sus datos de forma sistemática |
| **Onda Cero** | Compilación secundaria | Autorización pendiente (ver arriba) |

Regla: **no reproducir tablas, gráficos ni bases de datos de terceros**. Si una
fuente no autoriza el uso, se retira y se recalcula.

## 4. Blackout electoral (LOREG)

- **Norma**: LOREG, art. 69. Durante los **cinco días anteriores** a la
  votación no se publican, difunden ni reproducen por ningún medio resultados
  de encuestas o sondeos de opinión referidos a las elecciones (art. 69.7).
- **Ficha técnica (art. 69.1)**: al publicar un sondeo, la norma exige
  identificar el organismo y su domicilio, las características técnicas
  (universo, tamaño, muestreo, error, fechas de campo), el texto de las
  preguntas y el número de no respuesta. **Pendiente**: revisar si el sitio
  entra en el ámbito de «medio de comunicación» y, por prudencia, publicar una
  ficha técnica por sondeo cuando la fuente la ofrezca.
- **Fechas**: **24–28 de noviembre de 2026**, ambos inclusive. El **29** se
  restablece la publicación.
- **Implementación**: `agg/blackout.py` y `gen/build.py`. Durante la ventana:
  - la portada, `/robustez.html`, `/novedades.html` y `/hemiciclo.html` muestran un aviso legal;
  - se retiran `data/latest.json`, `data/robustez.json` y `og-robustez.png`;
  - el sitemap y el RSS no anuncian los datos retirados;
  - `validate_site.py` y `canary_live.py` comprueban el estado.
- **Pendiente**: revisar la redacción legal del aviso y **bloquear también
  cualquier publicación social programada** con cifras de sondeos en esa
  ventana. La regla no depende del canal.
- **Resultados oficiales**: se publican tras el cierre de los colegios, con
  fuente oficial; no son encuestas. No mezclar resultados oficiales con la
  media de sondeos.

## 5. Protección de datos (RGPD/LOPDGDD)

- **Situación actual (23-oct-2026)**: sitio estático, sin cookies ni analítica
  de terceros, con **aviso por correo** de doble opt-in (`/privacidad.html`).
  El alta guarda **email, fecha, página, UTM y host del referrer**; no guarda IP
  ni URL completa del referrer. El único canal sigue siendo el correo de
  contacto.
- **Datos que pueden existir**:
  - logs del servidor (IP, fecha, agente) por seguridad y funcionamiento;
  - correos recibidos, para responder;
  - suscripciones al aviso: email, estado, fecha, página/UTM y host del
    referrer; sin perfilado.
- **Implementado (autochequeo 23-oct-2026)**: página de privacidad,
  doble opt-in con confirmación por `POST` (un `GET` no cambia el estado),
  baja con botón, retención de pendientes 30 días, borrado de página/UTM/referrer
  al darse de baja (solo queda email + fecha en lista de exclusión), versión del
  consentimiento (`2026-10-23-v1`), sin cookies y sin cesión a terceros.
  - Logs de acceso: **14 días** (rotación de nginx).
  - Copias de `subs.db`: **30 días**, permisos `0600`, en
    `~/backups/elecciones29n/`.
  - Envío transaccional: **Resend** como encargado, con DPA y SCC publicadas
    (tratamiento principal en EE. UU.); **Cloudflare** como encargado de CDN y
    seguridad, con DPA/SCC/DPF. Enlaces en `/privacidad.html`.
- **Límites honestos**: esto es un autochequeo técnico, no un dictamen jurídico.
  No hay revisión externa. Si el proyecto se convierte en actividad económica,
  habría que añadir los datos identificativos que exige la LSSI.
- **Pendiente**:
  - decidir si el aviso pasa a tener envíos periódicos (hoy solo confirmación);
  - mantener actualizada la versión del consentimiento si cambia el texto y
    revisar anualmente los DPA/subencargados de Resend y Cloudflare.
- **Principio**: no recoger más datos de los necesarios y no cederlos a
  terceros.

## 6. Propiedad intelectual y datos

- **Código**: AGPL-3.0. Cualquier reutilización debe cumplir la licencia.
- **Datos agregados propios**: reutilizables citando el proyecto. No se
  reclama exclusividad sobre hechos aislados.
- **Datos de terceros**: cada fuente conserva sus condiciones. Especial
  atención a la **selección y disposición** de tablas ajenas (derecho *sui
  generis* sobre bases de datos en la UE): no copiar la estructura ni el
  contenido completo.
- **Licencias verificadas**: Ministerio del Interior, CC BY 4.0 (resultados
  provinciales). INE, JEC, BOE y CIS: citar fuente; revisar condiciones antes
  de un uso masivo.
- **Imágenes**: las tarjetas OG y gráficos son generados por el proyecto. No
  usar imágenes de terceros sin licencia.

## 7. Neutralidad electoral y comunicación

- No hay pronóstico, estimación propia de intención de voto ni recomendación de
  voto.
- No hay publicidad política ni pago por cobertura.
- En redes: evitar titulares que sugieran un resultado; usar rango, fecha y
  fuente. **X se publica manualmente**; no automatizar.
- Si se comparte una cifra, incluir siempre el contexto (“media de sondeos
  publicados”, no “resultado”).
- No coordinarse con partidos ni campañas para publicar datos.

## 8. Correcciones y derecho de réplica

- Canal: `info.elecciones29n@pruebapublica.com`.
- Toda corrección de dato se registra en `CHANGELOG.md` y, si afecta a una
  página, se regenera.
- Si una fuente o una persona identificable solicita corrección, responder y
  corregir si hay error; si no hay error, explicar la fuente y el método.
- No borrar el histórico sin dejar rastro: marcar la corrección.

## 9. Términos de uso y responsabilidad

- El sitio ofrece información y datos “tal cual”, sin garantía de
  disponibilidad ni de ausencia de errores.
- No es asesoramiento electoral, jurídico ni financiero.
- Los enlaces externos no implican respaldo.
- La media no predice el resultado; el rango no es un intervalo de confianza.
- El apoyo en Ko-fi no compra influencia ni cambia las cifras.

## 10. Ko-fi y financiación

- **Estado**: botón de apoyo activo. No hay recompensas ni acceso anticipado.
- **Pendiente**:
  - revisar las condiciones de Ko-fi y el tratamiento de datos de la
    plataforma;
  - no presentar el apoyo como donación fiscalmente deducible;
  - separar claramente “apoyo al mantenimiento” de “pago por servicio”;
  - consultar obligaciones fiscales si el volumen crece.

## 11. Prioridades antes del 24-N

1. **Alta**: Onda Cero enviada; decidir el fallback si no responde.
2. **Hecho**: Electomanía **autorizó por escrito** el 23-oct-2026 (ElectoPanel
   en abierto, histórico, sin coste; «Fuente: Electomanía» + enlace por pieza;
   escaños publicados sin recalcular). Mantener esas condiciones en cada build.
   **Hemiciclo**: no usa sus escaños publicados; es una simulación propia sobre
   la media agregada. Revisar la etiqueta y, si la casa objeta, excluirla del
   cálculo del hemiciclo o retirar la capa.
3. **Alta**: revisar la ficha técnica del art. 69.1 LOREG y la redacción del
   aviso de blackout; bloquear redes 24–28-N.
4. **Alta**: privacidad publicada (`/privacidad.html`); queda la revisión legal
   y la política de logs.
5. **Media**: conservar número de estudio y condiciones del CIS; revisar
   licencia/cita de los datos agregados.
6. **Baja**: revisar Ko-fi y obligaciones fiscales.

## 12. Referencias

- LOREG: `https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672`
- JEC: `https://www.juntaelectoralcentral.es/`
- RGPD: `https://eur-lex.europa.eu/eli/reg/2016/679/oj`
- LOPDGDD: `https://www.boe.es/buscar/act.php?id=BOE-A-2018-16673`
- AGPL-3.0: `https://www.gnu.org/licenses/agpl-3.0.html`
