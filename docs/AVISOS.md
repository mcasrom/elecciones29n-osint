# Avisos locales (fuente de 29N)

> **El aviso diario lo manda el centro único `~/Desktop/atencion`** (un solo panel y un solo aviso). `scripts/needs.py` es la **fuente de 29N** que lee ese centro; su timer propio está retirado para no duplicar.

## Qué revisa solo

- **Cron**: si no hay marca de hoy y no hay error, avisa de que no ha corrido.
- **Datos**: `latest.json` ausente, desactualizado (>30 h; crítico >48 h) o salud distinta de `ok`.
- **Muestra**: menos de 4 sondeos o menos de 2 casas; último sondeo de más de 7 días (salvo periodo de reflexión).
- **Inbox**: filas pendientes en `data/entrada_sondeos.csv` o `data/entrada_resultados.csv` (ignora `EJEMPLO`).
- **Errores**: `last_error` de la última ejecución (build, validación o canario).

## Tareas manuales

`needs.json` (en `~/.config/elecciones29n/`) guarda las tareas que dependen de ti. Seeds actuales:

- `gsc-index`: comprobar indexación en GSC (vence 21-oct-2026).
- `irdp-review`: revisión del índice IRDP, sin publicar.
- `social-card`: decidir/publicar la tarjeta social del 29N.

Comandos:

```bash
python3 scripts/needs.py list
python3 scripts/needs.py done gsc-index
python3 scripts/needs.py snooze social-card --days 7
python3 scripts/needs.py add --id mi-tarea --title "..." --due 2026-10-25
python3 scripts/needs.py panel --open
```

## Cuándo avisa

- **08:25**: `atencion.timer` del centro único, después del run de 29N.
- **Al entrar**: autostart del centro; si el aviso de las 08:25 no se pudo mostrar, se muestra ahora.
- El centro lee esta fuente con `scripts/needs.py list --json`; no hay timer propio de 29N.

El panel de 29N sigue disponible en `~/.config/elecciones29n/needs.html`.

## Límites

- No comprueba GSC ni el campo/método de las encuestas: eso es manual.
- No enciende el portátil: si está apagado, `Persistent=true` recupera al arrancar.
- El panel es local y no se publica.

## Centro único

`~/Desktop/atencion` lee esta fuente, comprueba 21 servicios y manda un solo aviso; ver su `README.md`. Para que un servicio aporte tareas propias, el siguiente paso es que publique su `needs.json` y el centro lo lea.
