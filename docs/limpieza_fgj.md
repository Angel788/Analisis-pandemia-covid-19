# Limpieza de carpetas de investigación FGJ

Generado por `src/clean/fgj.py`.

## Pasos

| Paso | Registros | Nota |
|---|---:|---|
| Registros leídos (9 archivos anuales) | 1,987,424 |  |
|   de ellos, idénticos en las 21 columnas (se marcan) | 3,824 |  |
| Sin fecha del hecho (se descartan) | 545 |  |
| Hecho anterior a 2016 (se descartan) | 32,223 | registro incompleto |
| Hecho posterior al inicio de la carpeta (se descartan) | 110 | fecha inconsistente |
| Hecho fuera de la CDMX (se descartan) | 16,734 |  |
| Alcaldía recuperada por coordenadas | 2 |  |
| En la CDMX sin alcaldía identificable (se conservan) | 18,595 | cuentan solo para el total de la ciudad |
| Hechos no delictivos (se marcan) | 66,960 |  |
| Delitos de alto impacto según la FGJ | 290,100 |  |
| En los últimos 2 meses (subregistro, se marcan) | 30,814 | corte: 2024-07 |
| Registros en la base limpia | 1,937,812 |  |

## Carpetas por año del hecho (sin no delictivos ni duplicados)

| Año | Carpetas |
|---|---:|
| 2016 | 180,182 |
| 2017 | 206,784 |
| 2018 | 244,728 |
| 2019 | 239,390 |
| 2020 | 200,067 |
| 2021 | 220,512 |
| 2022 | 229,774 |
| 2023 | 227,702 |
| 2024 | 118,213 |

## Carpetas por grupo de delito

| Grupo | Dimensión | Carpetas |
|---|---|---:|
| fraude_extorsion | patrimonial | 306,014 |
| violencia_familiar | familiar | 241,042 |
| robo_otros | patrimonial | 156,326 |
| robo_transeunte | patrimonial | 140,002 |
| robo_autopartes | patrimonial | 132,945 |
| robo_negocio | patrimonial | 132,478 |
| otros | otros | 129,967 |
| amenazas | violencia | 125,766 |
| robo_vehiculo | patrimonial | 84,467 |
| hecho_no_delictivo | no_delictivo | 66,960 |
| robo_transporte_publico | patrimonial | 62,574 |
| lesiones_transito | vial | 61,942 |
| delitos_sexuales | sexual | 59,244 |
| dano_propiedad | patrimonial | 58,087 |
| lesiones_dolosas | violencia | 49,510 |
| robo_casa | patrimonial | 43,730 |
| narcomenudeo | otros | 38,023 |
| robo_repartidor_transp | patrimonial | 16,897 |
| lesiones_arma_fuego | violencia | 10,033 |
| homicidio_doloso | violencia | 9,817 |
| secuestro_privacion | violencia | 6,176 |
| homicidio_culposo | vial | 5,812 |

Base agregada: 34,683 filas (alcaldía × mes × grupo).
