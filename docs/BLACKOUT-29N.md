# Blackout 29N — protocolo operativo (24–28 nov 2026)

> Objetivo: retirar el origen de los sondeos y reducir copias residuales sin prometer lo que no se puede controlar. La obligación legal es no publicar, difundir ni reproducir sondeos (LOREG art. 69.7).

## T-7 días (17 nov)

- [ ] Congelar el calendario social: no programar tarjetas con cifras para 24–28 nov.
- [ ] Revisar el aviso legal y el texto de la página de blackout.
- [ ] Comprobar que `agg/blackout.py` cubre 24–28 y que el build de staging retira datos.
- [ ] Backup del vhost nginx y del `web/` actual.

## Estado de la preparación (25-oct)

- **Pausa social automática**: `social-poster/social_queue.py` no publica del 24 al 28 (probado con `E29N_BLACKOUT_TEST=1`; hay 6 elementos aprobados que quedarán bloqueados).
- **Recordatorios Archive.org**: 23, 24 y 28 nov a las 08:05 Europe/Madrid en `scripts/recordatorios.json`.
- **Prueba con navegador ya usado**: perfil cálido → `/data/latest.json` 200; con marcador de blackout → **410**; sin marcador → **200**. Marcador y página de prueba eliminados.
- **Purga**: sigue siendo manual. El servidor solo tiene credenciales de Certbot, no la clave global de Cloudflare; `run_daily_server.sh` avisa si falta el wrapper.

## T0 (24 nov, 00:00 Europe/Madrid)

- [ ] `run_daily_server.sh` en modo blackout: páginas de aviso, sin JSON, sin `og.png`/`og-hemiciclo.png`/`og-robustez.png`.
- [ ] `nginx -t` y reload. El 410 condicional ya está en `/etc/nginx/snippets/blackout-410-29n.conf`.
- [ ] Purga Cloudflare (`pruebapublica`) inmediatamente después del build.
- [ ] Comprobar con `curl` y con un navegador que ya visitó la web:
  - `/` → 200 y aviso.
  - `/data/latest.json`, `/data/robustez.json`, `/og.png`, `/og-hemiciclo.png`, `/og-robustez.png` → 410.
  - `sw.js` nuevo y sin caché de datos.
- [ ] Parar cualquier cola social pendiente y no publicar capturas con cifras.

## Durante el cierre

- [ ] Monitorizar búsquedas, Archive.org y menciones de copias antiguas.
- [ ] Si aparece una copia: no reamplificarla; responder con el aviso legal y el enlace a la página de blackout.
- [ ] No usar `robots.txt` como herramienta de borrado: no elimina copias ya indexadas.

## Archive.org

- Comprobación automatizada: `python3 scripts/archive_check.py` (0 = sin capturas, 1 = hay capturas, 2 = consulta incompleta).
- **25-oct**: CDX sin capturas en las URLs comprobadas; una consulta de disponibilidad dio error intermitente. **Recheck 23, 24 y 28 nov**.
- Texto de solicitud y alcance: `demo/archive_org_29n_20261025.md` (privado). **No enviar sin OK expreso.**

- [ ] Solicitar exclusión/eliminación de las instantáneas con datos, usando el procedimiento de Archive.org. **No se puede garantizar**: es un tercero y puede rechazar o tardar.
- [ ] Guardar el identificador de la solicitud y la fecha.
- [ ] No enviar la solicitud sin OK expreso del titular (regla 31).

## T+1 (29 nov)

- [ ] Restaurar el build normal, purgar Cloudflare y verificar 200 en datos/OG.
- [ ] Publicar la comparación sondeo vs escrutinio y el informe de calibración.
- [ ] Registrar incidencias y copias residuales en el changelog.

## Límite

Se puede retirar el origen y reducir cachés propias. **No se puede borrar internet**: capturas, posts y archivos de terceros quedan fuera de control. La comunicación debe decir “hemos retirado el origen”, no “hemos borrado las copias”.
