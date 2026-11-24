# Informe post-29N — estructura

**Estado:** pendiente de escrutinio oficial.  
**No se publica hasta que exista `data/resultados_29n.json` con fuente oficial.**

## 0. Ficha del informe

- Fecha de publicación:
- Fuente oficial:
- URL de la fuente:
- Fecha y hora del escrutinio:
- Foto pre-electoral congelada:
- Nº de sondeos de la foto:
- Nº de casas:
- Ventana de la media:
- Versión del pre-registro:

## 1. Qué se midió

- Media pre-electoral publicada antes del blackout.
- Resultado oficial por partido.
- Error en puntos porcentuales.
- No se comparan escaños simulados con escaños oficiales.

## 2. Resultado oficial

| Dato | Valor | Fuente |
|---|---:|---|
| Participación | — | — |
| Votos válidos | — | — |
| Diputados | — | — |

## 3. Media vs oficial

| Partido | Media | Oficial | Error |
|---|---:|---:|---:|
| PP | — | — | — |
| PSOE | — | — | — |
| VOX | — | — | — |
| Frente Amplio | — | — | — |
| ERC | — | — | — |
| Junts | — | — | — |
| PNV | — | — | — |

## 4. Resumen de error

- MAE:
- Sesgo medio:
- Nº de partidos comparados:
- Lectura: sobrestimación / subestimación / mixta.
- Límite: el resultado oficial es el denominador; no se ajusta la media a posteriori.

## 5. Bloques

| Bloque | Media | Oficial | Error |
|---|---:|---:|---:|
| PP + VOX | — | — | — |
| PSOE + Frente Amplio + Podemos | — | — | — |

No es una proyección de escaños.

## 6. Casas

- Última pieza por casa frente al oficial.
- Solo PP y PSOE si están publicados.
- No se comparan casas sin ficha pre-electoral verificable.
- MAE por casa:

## 7. Qué se puede concluir

- Qué partidos/bloques quedaron dentro del rango.
- Qué casas se desviaron más.
- Si el error fue sistemático o disperso.
- Qué no se puede atribuir a la media.

## 8. Qué no se puede concluir

- No se evalúa la calidad de la democracia.
- No se evalúa la intención de voto individual.
- No se comparan escaños simulados con escaños oficiales.
- No se convierte el error en un ranking de casas.

## 9. Reproducibilidad

```bash
cd /home/deploy/elecciones29n-osint
.venv/bin/python scripts/import_resultados.py
./scripts/run_daily_server.sh
.venv/bin/python scripts/canary_live.py
/home/deploy/scripts/cf_purge.sh pruebapublica
```

## 10. Publicación

- Revisar `data/resultados_29n.json`.
- Revisar `/postelectoral.html` en staging.
- Confirmar fuente y fecha.
- Publicar y purgar Cloudflare.
- Registrar incidencia/corrección si cambia el escrutinio.
