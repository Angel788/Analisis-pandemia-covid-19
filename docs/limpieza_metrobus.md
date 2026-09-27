# Limpieza de afluencia del Metrobús

Generado por `src/clean/metrobus.py`.

## Pasos

| Paso | Resultado |
|---|---|
| Registros leídos (fecha × línea) | 53,732 |
| Nombres de línea distintos → unificados | 14 → 7 |
| Filas antes de la inauguración de su línea (no son faltantes) | 17,227 |
| Faltantes con la línea operando | 0 |
| Duplicados fecha × línea | 0 |
| Días atípicos (> 2.5× o < 0.2× la mediana de 29 días) | 30 (se conservan salvo errores evidentes) |
| Errores evidentes anulados | 2 |
| Valores con decimales (probables estimaciones; se redondean y marcan) | 57 |

## Errores anulados

| Fecha | Línea | Motivo |
|---|---|---|
| 2005-07-26 | Línea 1 | 3.03 M: ~13 veces un día normal; probable acumulado desde la inauguración |
| 2017-09-20 | Línea 2 | 9 pasajeros el día posterior al sismo 19-S; dato imposible o servicio suspendido |

## Días atípicos conservados (eventos reales)

| Fecha | Línea | Afluencia | × mediana |
|---|---|---:|---:|
| 2006-01-01 | Línea 1 | 28080 | 0.17 |
| 2006-01-15 | Línea 1 | 42586 | 0.189 |
| 2006-01-22 | Línea 1 | 43662 | 0.188 |
| 2006-01-29 | Línea 1 | 40194 | 0.17 |
| 2006-04-14 | Línea 1 | 37144 | 0.154 |
| 2012-12-01 | Línea 4 | 4930 | 0.092 |
| 2013-02-03 | Línea 4 | 3149 | 0.063 |
| 2013-06-02 | Línea 4 | 8599 | 0.192 |
| 2013-06-30 | Línea 4 | 9954 | 0.199 |
| 2013-07-07 | Línea 4 | 8266 | 0.188 |
| 2013-07-14 | Línea 4 | 5798 | 0.152 |
| 2013-07-21 | Línea 4 | 5446 | 0.151 |
| 2013-07-28 | Línea 4 | 5381 | 0.149 |
| 2013-08-04 | Línea 4 | 4944 | 0.134 |
| 2013-09-01 | Línea 4 | 2865 | 0.099 |
| 2013-09-08 | Línea 4 | 2748 | 0.106 |
| 2013-09-15 | Línea 4 | 6102 | 0.186 |
| 2016-02-12 | Línea 4 | 9395 | 0.164 |
| 2016-02-13 | Línea 4 | 6385 | 0.112 |
| 2017-09-20 | Línea 6 | 22550 | 0.11 |
| 2018-07-01 | Línea 7 | 14427 | 0.142 |
| 2019-09-16 | Línea 4 | 10854 | 0.15 |
| 2020-09-16 | Línea 4 | 6238 | 0.148 |
| 2020-12-25 | Línea 4 | 7544 | 0.191 |
| 2021-01-01 | Línea 4 | 7756 | 0.197 |
| 2023-12-31 | Línea 7 | 25208 | 0.198 |
| 2024-10-01 | Línea 4 | 12394 | 0.124 |
| 2026-01-01 | Línea 4 | 12697 | 0.155 |

## Afluencia diaria promedio por año

| Año | Viajes/día | Índice 2019=100 |
|---|---:|---:|
| 2005 | 194,766 | 16.0 |
| 2006 | 203,388 | 16.7 |
| 2007 | 212,749 | 17.5 |
| 2008 | 245,220 | 20.1 |
| 2009 | 348,482 | 28.6 |
| 2010 | 375,214 | 30.8 |
| 2011 | 512,607 | 42.1 |
| 2012 | 601,831 | 49.4 |
| 2013 | 630,223 | 51.8 |
| 2014 | 710,356 | 58.3 |
| 2015 | 757,588 | 62.2 |
| 2016 | 957,497 | 78.6 |
| 2017 | 1,009,578 | 82.9 |
| 2018 | 1,128,730 | 92.7 |
| 2019 | 1,217,528 | 100.0 |
| 2020 | 659,216 | 54.1 |
| 2021 | 846,008 | 69.5 |
| 2022 | 1,199,583 | 98.5 |
| 2023 | 1,374,622 | 112.9 |
| 2024 | 1,447,743 | 118.9 |
| 2025 | 1,397,520 | 114.8 |
| 2026 | 1,370,420 | 112.6 |

Nota: la red creció (Línea 6 en 2016, Línea 7 en 2018 y ampliaciones posteriores), así que
parte del aumento posterior a 2022 refleja más cobertura y no solo más demanda.
