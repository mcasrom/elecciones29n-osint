# Pizarra y eventos de campaña 29N

## Ventana

- **9–23 de noviembre de 2026**, 08:00 Europe/Madrid.
- **No** se ejecuta del 24 al 28 (blackout).
- El 29N es el flujo de noche electoral, no este parte.

## Regla: pizarra semanal + eventos

- **Lunes y viernes, 08:00:** pizarra semanal (media, IQR, sondeos/casas y último sondeo), aunque no haya novedad.
- **Cualquier día:** post de evento si hay nuevo sondeo (`n_polls`/`last_poll_date`) o Δ≥0,5 pp en PP, PSOE, VOX o SUMAR.
- **Resto de días sin evento:** silencio.
- No se incluyen bloques, escaños ni simulación.

## Canales

- **Mastodon, Bluesky y Telegram** mediante `social-poster/social_queue.py`.
- **Bluesky específico del proceso 29N:** **Hub Electoral | Prueba Pública** · `@electoraldatahub.bsky.social`. Se reserva para mensajes electorales; no mezclar con la cuenta general. La cola lo selecciona con `--account electoralhub` (claves `BSKY_ELECTORALHUB_*`), sin cambiar la cuenta global. Credenciales privadas del servidor, nunca en Git.
- **X manual**: la cola manda al dueño el texto listo por Telegram.
- Imagen: `https://elecciones29n.pruebapublica.com/og-robustez.png` (se regenera en el build diario).

## Estado

`data/campaign_digest_state.json` guarda la última foto enviada. Si no hay cambio, no se actualiza: el siguiente parte compara con lo último publicado, no con el día anterior.

## Calendario recomendado

- **Lunes y viernes, 08:00:** pizarra semanal con media, IQR, número de sondeos/casas y último sondeo; sin interpretación si no hay novedad.
- **Evento:** nuevo sondeo o cambio ≥0,5 pp; post adicional con la novedad y la fuente.
- **20–23 nov:** solo eventos reales; no rellenar por calendario.
- **24–28 nov:** silencio de agregaciones; contenido educativo sustitutivo.
- **29–30 nov:** resultados oficiales y calibración; nunca pronóstico previo.

## Comandos

```bash
python3 scripts/campaign_digest.py --dry          # ver qué haría
python3 scripts/campaign_digest.py --dry --force  # probar fuera de campaña
python3 scripts/campaign_digest.py                # encolar si toca
```

Cron (servidor, TZ Europe/Madrid):

```cron
0 8 9-23 11 * cd /home/deploy/elecciones29n-osint && /usr/bin/python3 scripts/campaign_digest.py >> logs/campaign_digest.log 2>&1
```

## Límites

- No es un pronóstico: el texto usa media, IQR y último sondeo; no incluye simulación de escaños.
- No sustituye la distribución editorial: hilo de provincias, embeds, outreach y GSC.
- Si no hay cambio real, no hay post. La frecuencia no se fuerza.


## Email segmentado por provincia (manual)

`scripts/newsletter_provincia.py` usa `page` de la suscripción para añadir un bloque provincial. No hay campo nuevo ni cron.

```bash
python3 scripts/newsletter_provincia.py --dry
python3 scripts/newsletter_provincia.py --test tu@email --province madrid
```

`--send` solo con OK expreso. Respeta blackout y doble opt-in.
