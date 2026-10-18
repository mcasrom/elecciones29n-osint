# Avisos locales (centro de pendientes)

El sistema no espera a que lo recuerdes: cada día revisa lo que necesita y lo anuncia.

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

- **08:00**: `run_daily.sh` termina y llama a `digest --if-due`.
- **08:20**: timer `elecciones29n-attention.timer` (si el de las 08:00 falló o no dejó aviso).
- **Al entrar**: autostart `check_laptop_on.sh` llama a `digest --if-due`; si el aviso de las 08:00 no se pudo mostrar (sin sesión gráfica), se muestra ahora.

`--if-due` muestra como máximo **un aviso por día**. Si no hay pendientes, no molesta. El aviso es una notificación de escritorio con el panel:

`~/.config/elecciones29n/needs.html`

También hay un acceso **29N - Pendientes** en el menú de aplicaciones.

## Límites

- No comprueba GSC ni el campo/método de las encuestas: eso es manual.
- No enciende el portátil: si está apagado, `Persistent=true` recupera al arrancar.
- El panel es local y no se publica.

## Extensión al resto de microservicios

El patrón es un `needs.json` por servicio + un `digest` diario. Para los ~20 servicios conviene un **único centro** que lea varios `needs.json` y avise en un solo mensaje (escritorio y/o Telegram). No está hecho todavía.
