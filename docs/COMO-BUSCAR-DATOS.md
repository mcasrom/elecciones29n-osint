# Cómo buscar participación provincial y votos por provincia

> Lo que necesitamos primero: **participación por provincia** de una o varias
> elecciones generales. Después: **votos y escaños por provincia** de 2023.

## 1. Fuente oficial (primera opción)

**Ministerio del Interior · Resultados electorales**

- https://infoelectoral.interior.gob.es/es/inicio/
- https://www.interior.gob.es/opencms/es/servicios-al-ciudadano/procesos-electorales/

Pasos en el navegador:

1. Entra en **Resultados electorales**.
2. Elige **Elecciones Generales** y la convocatoria (2023, 2019, 2016…).
3. Abre **Participación** (o «Resultados por provincia»).
4. Selecciona **todas las provincias** y el nivel **provincia**.
5. Copia la tabla a LibreOffice/Excel o usa «Descargar CSV» si aparece.
6. Guarda el enlace exacto de la página.

> El sitio puede tardar o pedir un reto de Cloudflare. Prueba con un navegador
> normal, sin VPN y, si falla, con datos móviles. No uses `curl`.

## 2. Alternativas si el Interior no responde

- **JEC**: https://www.juntaelectoralcentral.es/cs/jec/elecciones/Generales-julio2023
  (suele enlazar al Interior; PDFs de CERA y Ceuta/Melilla).
- **Congreso**: https://www.congreso.es/ (documentación y resultados publicados).
- **Wayback Machine**: busca la URL del Interior en https://web.archive.org/.
- **Portales autonómicos**: algunas CCAA publican resultados provinciales.
- **Medios** (El País, RTVE): solo como **contraste**, nunca como fuente oficial.

## 3. Qué guardar

Un CSV con estas columnas (una fila por provincia y elección):

```
eleccion,provincia,censo,votantes,participacion,fuente_url
2023,Madrid,5038039,,66.59,https://…
```

- `censo` y `votantes` si aparecen; si no, deja `votantes` vacío.
- `participacion` en % (coma o punto).
- `fuente_url`: la página exacta de la que copiaste.
- Una fila por provincia. Si copias varias elecciones, añade una fila por cada una.

Para votos/escaños por provincia:

```
eleccion,provincia,partido,votos,escanos,fuente_url
2023,Madrid,PP,1234567,15,https://…
```

## 4. Cómo comprobar que está bien

- La **suma de votantes** provinciales debe coincidir con el total nacional.
- La participación ponderada por censo debe dar el dato nacional
  (2023: **66,59 %**).
- Si una provincia no cuadra, anótalo; no la corrijas a mano sin fuente.
- Nombres de provincia oficiales (con tildes y artículos: `Coruña, A`,
  `Palmas, Las`, `Rioja, La`).

## 5. Qué hago yo con eso

- Normalizo el CSV a `data/participacion_provincial.json`.
- Valido sumas y comparo con el dato nacional.
- Desbloqueo **M5 (meteorología × participación)** y **votos↔escaños por
  provincia**.
- Si solo tienes un PDF o una captura, pásame el enlace: lo extraigo y lo
  contrasto.

## 6. Plantilla

`data/participacion_provincial.csv` ya tiene la cabecera y una fila `EJEMPLO`
que se ignora. Rellena las provincias y ejecuta:

```bash
.venv/bin/python scripts/import_participacion_provincial.py
```
