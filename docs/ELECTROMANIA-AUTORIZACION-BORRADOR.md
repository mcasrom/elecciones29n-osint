# Electomanía — solicitud de autorización (enviada)

> **Enviado:** 23-oct-2026, 09:21 UTC.
> **Estado Resend:** `delivered`.
> **ID Resend:** `01a16810-599f-730d-8061-f122065fc952`.
> **De:** Miguel Castillo · Observatorio 29N `<prensa@viajeinteligencia.com>`.
> **Reply-To:** `info.elecciones29n@pruebapublica.com`.
> **Para:** `info@electomania.es`.
> **CC:** ninguno.
> **Asunto:** Autorización para el uso limitado de sondeos de Electomanía en el Observatorio 29N.

Hola:

Me dirijo a ustedes como autor de Observatorio 29N
(https://elecciones29n.pruebapublica.com), un proyecto individual, gratuito y de
código abierto (AGPL-3.0), que publica una media agregada de sondeos para las
elecciones generales del 29 de noviembre de 2026. No es un pronóstico ni una
estimación propia de intención de voto.

He leído sus condiciones de derechos de autor y quiero solicitar autorización
para un uso limitado de sus datos. En concreto, desde el 30 de agosto he usado
ocho ElectoPanel y dos ElectoPromedio (30-ago, 6, 13, 20 y 27-sep, 4, 11 y
18-oct; y 30-sep y 19-oct), con estos campos: fecha, casa, porcentaje por
partido, tamaño de muestra cuando consta y enlace a la pieza original. No
reproduzco sus tablas, gráficos, artículos, ElectoPaneles completos ni
microdatos.

El uso es el siguiente:

1. Calcular mi propia media agregada, con una fila por sondeo y su fecha.
2. Publicar esos sondeos con su casa, fecha y enlace a Electomanía.
3. Incluir los datos agregados en JSON/CSV abiertos, sin tablas ni gráficos de
   Electomanía.
4. Mantener el histórico ya publicado mientras la autorización siga vigente.

Actualmente el ElectoPromedio figura como una entrada más, identificada como
promedio y separada de los sondeos individuales. Si prefieren que lo retire de
mis cálculos y lo deje solo como enlace, lo haré.

Les agradecería que me confirmaran por escrito:

1. Si autorizan este uso limitado y no sustitutivo.
2. La atribución exacta que prefieren («Fuente: Electomanía», enlace a la
   página general o a cada pieza) y dónde debe aparecer.
3. Si la autorización cubre el histórico y los ficheros JSON/CSV, o si tiene
   límites de plazo, volumen o revocación.
4. Si requiere una licencia o condiciones económicas, para valorarlas antes de
   continuar.

Si la autorización no cubre este uso, retiraré la fuente y los sondeos que
dependan de ella de la media y de los ficheros públicos. Si detectan un error
de atribución o de dato, lo corregiré en cuanto me lo indiquen. Si lo prefieren,
suspendo la ingesta mientras revisan la solicitud.

Gracias por su tiempo.

Miguel Castillo
Observatorio 29N
info.elecciones29n@pruebapublica.com
https://elecciones29n.pruebapublica.com

---

## Notas internas (no enviar)

- **Qué se usa**: 8 ElectoPanel (tracking) y 2 ElectoPromedio (average), con
  fecha, casa, porcentajes, muestra cuando consta y enlace.
- **Qué no se usa**: tablas, gráficos, artículos, ElectoPaneles completos,
  microdatos ni bases de datos de Electomanía.
- **Riesgo**: sus términos prohíben scraping, extracción automatizada y
  reutilización sistemática para agregadores o bases de datos sin autorización
  escrita; la API pública no equivale a permiso.
- **Si no autorizan**: retirar ElectoPanel/ElectoPromedio de
  `data/polls_history.csv`, recalcular la media y regenerar.
- **Remitente**: `prensa@viajeinteligencia.com` porque Resend solo tiene
  verificado ese dominio; `pruebapublica.com` no está verificado para envío.
- **Seguimiento**: si no responden en 7–10 días, un único recordatorio breve.
  No insistir después.

---

## Respuesta recibida (23-oct-2026, 13:45)

**Autorizado por escrito** por `info@electomania.es`.

- Uso limitado y no sustitutivo de los datos **en abierto del ElectoPanel**
  (voto y escaños para generales).
- **Usar los escaños publicados, sin recalcularlos**.
- Atribución **«Fuente: Electomanía»** y **enlace a cada pieza** (no solo a la
  portada).
- Cubre el **histórico**; sin límite de plazo o volumen si se respetan las
  pautas.
- **Sin coste** mientras sean datos publicados en abierto, con enlace y mención.

No publicar el correo completo: lleva aviso de confidencialidad. Registro
interno en `demo/electromania_autorizacion_20261023.md`.
