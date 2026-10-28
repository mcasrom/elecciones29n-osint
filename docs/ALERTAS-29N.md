# Alertas 29N y purga de caché

## 1. Aviso de Telegram (`alertas_29n.py`)

El aviso distingue tres situaciones para no presentar una salida de la ventana
de 14 días como si fuera un sondeo nuevo:

| Cambio | Texto |
|---|---|
| `n_polls` sube | `Nuevo sondeo` o `N sondeos nuevos` |
| `n_polls` baja | `Recalculo por ventana: sale un sondeo` / `salen N sondeos` |
| `n_polls` igual y cambia la media | `Recalculo de la media (sin sondeo nuevo)` |
| Sin cambios | No se envía |

Caso real 28-oct: la media pasó de 9 a 8 sondeos porque uno salió de la ventana
de 14 días. El mensaje correcto es **“sale un sondeo”**, no “datos actualizados”.

El estado se guarda en `/home/deploy/scripts/state/alertas_29n.json`.
Pruebas:

```bash
/usr/bin/python3 /home/deploy/scripts/alertas_29n.py --dry
/usr/bin/python3 /home/deploy/scripts/alertas_29n.py --test  # solo si se pide
```

## 2. Purga de Cloudflare

`run_daily_server.sh` intenta purgar la zona `pruebapublica` después del deploy.
Hasta el 28-oct avisaba de que faltaba el wrapper:

```
[run_daily_server] aviso: falta /home/deploy/scripts/cf_purge.sh; purgar CF a mano
```

Restaurado:

- Wrapper: `/home/deploy/scripts/cf_purge.sh` (`755`).
- Clave: `/home/deploy/.cloudflare_global_api_key.txt` (`600`, fuera del repo).
- Zonas: `fimi`/`viajeinteligencia` y `pruebapublica`.
- Uso manual: `/home/deploy/scripts/cf_purge.sh pruebapublica`.
- Verificado: `purge True []`.

No se guarda ninguna clave en el repositorio ni en la documentación pública.

## 3. Comprobación tras un deploy

```bash
curl -sS -A "Mozilla/5.0" -I https://elecciones29n.pruebapublica.com/ | \
  grep -iE "cf-cache-status|last-modified|cache-control"
```

Si `cf-cache-status` es `DYNAMIC` y `last-modified` es el build actual, el
origen está sirviendo lo nuevo. Si el navegador muestra una versión vieja,
probar ventana privada o borrar datos del sitio (service worker).


## 4. Un solo publicador

Desde el 28-oct-2026:

- **Servidor canónico:** cron `15 6 * * *` (`run_daily_server.sh`) y refrescos
  `15 14,20 * * *` (`refresh_polls_server.sh`).
- **Portátil:** se desactivaron `elecciones29n.timer` y
  `elecciones29n-refresh.timer` para no publicar dos builds distintos del mismo
  sitio. El portátil queda para editar y probar; si se ejecuta `run_daily.sh` a
  mano, hay que asumir que publica.
- El motivo: el 28-oct el build local de las 08:49 y el del servidor de las
  07:15 competían; los datos coincidían, pero `status.json`, alertas y caché
  podían desincronizarse.

## 5. Dedup del watcher

`scripts/watch_sondeos.py` deduplica ahora por **URL y título normalizado**, no
solo por URL. Google News cambia la URL de la misma pieza; el título es la clave
estable. El candidato de La Razón/NC Report del 26-oct quedó marcado como
`duplicado` y no se importó.

## 6. Versión del service worker

`gen/build.py` escribe `sw.js` con `CACHE = 'e29n-<build_ts>'` y la página con
`data-build`/`?v=<build_ts>`. No hay que editar `web/sw.js` a mano: el build
genera la versión. Si un navegador conserva una versión antigua, borrar datos
del sitio o usar ventana privada.
