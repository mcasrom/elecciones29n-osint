# Accesos 29N — medición semanal

## Definiciones

- **Humano probable:** clasificación del pipeline de accesos, sin dueño, interno, API, bot, crawler de IA ni datacenter.
- **Estricto (día):** IP humana con **≥2 páginas de contenido en un mismo día**.
- **Estricto recurrente:** IP humana con **≥2 páginas y presencia en ≥2 días** dentro de la ventana de 7 días.
- **Dominio externo:** host del `Referer` de una petición humana a contenido, excluyendo `pruebapublica.com`.
- **No son personas verificadas:** son IPs humanas probables. No hay cookies ni login.

## Comando

```bash
cd /home/deploy/elecciones29n-osint
/usr/bin/python3 scripts/accesos_29n.py --week          # última semana completa
/usr/bin/python3 scripts/accesos_29n.py --week --tg     # además Telegram
/usr/bin/python3 scripts/accesos_29n.py --week 2026-11-17
```

La tabla `weekly` guarda solo agregados: sin IP, sin user-agent y sin rutas completas con query.

## Corte 11–17 nov 2026

| Métrica | Valor |
|---|---:|
| IPs humanas con página | 866 |
| Estrictos únicos (≥2 páginas/día) | 131 |
| Estrictos recurrentes (≥2 días) | 13 |
| Dominios externos | 8 |

Dominios: `t.co` 86 · `www.google.com` 35 · `go.bsky.app` 3 · `github.com` 2 · `duckduckgo.com` 1 · `alice.yandex.ru` 1 · `www.linkedin.com` 1 · `www.facebook.com` 1.

UTM: `chatgpt.com` 65 · `bluesky` 43 · `x` 38 · `telegram` 7 · `mastodon` 2 · `analisis` 2 · `linkedin` 2 · `blu` 2.

## Lectura

- El objetivo de **3 dominios externos/semana** se cumple: 8.
- El objetivo de **20 lectores estrictos** se cumple solo con la definición amplia (131).
- Con la definición de recurrencia real, hay **13**, por debajo de 20.
- La métrica antigua de “3 lectores” no era comparable: contaba IPs que abrían contenido, no recurrencia.
- **GSC no está medido**: no hay export actual ni datos de consultas. No se puede afirmar nada sobre impresiones o clics de Google.

## Decisión

Cerrar el sprint como **parcial**, no como cumplido. La definición canónica para las próximas semanas será **estricto recurrente (≥2 días)**; el objetivo de 20 queda pendiente.

## Pendiente

- Export manual de GSC para la ventana, si se quiere incorporar esa fuente. GSC no se automatiza.
- Repetir la medición tras el 29N con la misma definición.
- Enlazar con `SPRINTS-PENDIENTES.md` §0.-29N-AUDIENCIA, que empieza el 1-dic.
