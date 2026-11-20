# S10.7 — Informe de carga

Prueba real en localhost el 20 de noviembre de 2026. Los resultados proceden
de `s10_stats.csv` y `s10_failures.csv` de esta ejecución; dependen de la
máquina y de la configuración.

## Cómo se ha medido

| Dato | Valor |
| --- | --- |
| Comando de la API | `python -m uvicorn wine_api.main:app --host 127.0.0.1 --port 8000` (1 proceso) |
| Comando de Locust | `uv run --locked --group load locust -f locustfile.py --headless -u 20 -r 5 -t 1m --host http://127.0.0.1:8000 --csv reports/s10 --csv-full-history --only-summary` |
| Cliente usado | `front`, clave aleatoria leída de un `.env` local ignorado por Git; Locust la recibió por `LOCUST_API_KEY` |
| `rate_limit_per_minute` del cliente | 60, compartido por sus peticiones de predicción válidas e inválidas |
| Máquina | Windows, Intel Core i7-10750H; Python 3.12.14; API y Locust en la misma máquina |

Archivos generados por Locust y versionados junto a este informe:
`s10_stats.csv`, `s10_failures.csv`, `s10_stats_history.csv` y
`s10_exceptions.csv`. Este último solo contiene la cabecera: no hubo
excepciones de Locust.

## Resultados

| Endpoint | Peticiones | RPS | p50 (ms) | p95 (ms) | Fallos | % 429 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `POST /v1/predictions` | 677 | 11,98 | 4 | 9 | 624 | 92,17 % |
| `/v1/predictions [422]` | 89 | 1,58 | 4 | 7 | 82 | 92,13 % |
| `GET /health` | 114 | 2,02 | 3 | 6 | 0 | — |
| Aggregated | 880 | 15,58 | 4 | 8 | 706 | 80,23 % |

`% 429` = fallos `429` de `s10_failures.csv` / peticiones de la fila
correspondiente de `s10_stats.csv` × 100. Para `POST /v1/predictions`,
`624 / 677 × 100 = 92,17 %`; para el caso inválido, `82 / 89 × 100 = 92,13 %`.
Los 82 fallos de la fila `[422]` recibieron `429` antes de validar el cuerpo;
los otros 7 recibieron el `422` esperado y Locust los contó como éxito.

## Análisis (5–10 líneas)

La cuota permite 60 peticiones de predicción por ventana de un minuto para
`front`; Locust intentó 766 entre los dos tipos de POST durante esta prueba.
Solo 60 POST superaron autenticación, scope y cuota: 53 válidos y 7 inválidos.
Los 706 restantes recibieron `429`, de acuerdo con la cuota configurada.
`GET /health` tuvo p50 de 3 ms y p95 de 6 ms, frente a 4 y 9 ms en la
predicción válida; no consume cuota ni requiere clave.
Locust terminó con código 1 porque considera los `429` fallos, aunque aquí
demuestran que la política de consumo se aplica.
Con dos workers y un contador en memoria por proceso, cada worker aplicaría
su propia cuota; el límite efectivo podría aproximarse al doble.
Para medir capacidad del servicio usaría otro cliente de carga con cuota muy
alta, de modo que el rate limit no domine el resultado de latencia y RPS.
