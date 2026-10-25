# Parte matinal de campaña 29N

## Ventana

- **13–23 de noviembre de 2026**, 08:00 Europe/Madrid.
- **No** se ejecuta del 24 al 28 (blackout).
- El 29N es el flujo de noche electoral, no este parte.

## Regla: solo si hay cambio

Se publica únicamente si respecto al último parte enviado hay:

- nuevo sondeo (`n_polls` o `last_poll_date`);
- cambio de bloque o mayoría;
- Δ≥1,0 pp en PP, PSOE, VOX o SUMAR;
- Δ≥3 escaños en alguno de esos partidos.

Sin cambio: **silencio**, no se envía nada.

## Canales

- **Mastodon, Bluesky y Telegram** mediante `social-poster/social_queue.py`.
- **X manual**: la cola manda al dueño el texto listo por Telegram.
- Imagen: `https://elecciones29n.pruebapublica.com/og-hemiciclo.png` (se regenera en el build diario).

## Estado

`data/campaign_digest_state.json` guarda la última foto enviada. Si no hay cambio, no se actualiza: el siguiente parte compara con lo último publicado, no con el día anterior.

## Comandos

```bash
python3 scripts/campaign_digest.py --dry          # ver qué haría
python3 scripts/campaign_digest.py --dry --force  # probar fuera de campaña
python3 scripts/campaign_digest.py                # encolar si toca
```

Cron (servidor, TZ Europe/Madrid):

```cron
0 8 13-23 11 * cd /home/deploy/elecciones29n-osint && /usr/bin/python3 scripts/campaign_digest.py >> logs/campaign_digest.log 2>&1
```

## Límites

- No es un pronóstico: el texto repite “simulación, no pronóstico”.
- No sustituye la distribución editorial: hilo de provincias, embeds, outreach y GSC.
- Si no hay cambio real, no hay post. La frecuencia no se fuerza.


## Email segmentado por provincia (manual)

`scripts/newsletter_provincia.py` usa `page` de la suscripción para añadir un bloque provincial. No hay campo nuevo ni cron.

```bash
python3 scripts/newsletter_provincia.py --dry
python3 scripts/newsletter_provincia.py --test tu@email --province madrid
```

`--send` solo con OK expreso. Respeta blackout y doble opt-in.
