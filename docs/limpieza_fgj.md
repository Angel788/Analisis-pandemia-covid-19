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
| En la CDMX sin alcaldía identificable (se descartan) | 18,595 | no se pueden asignar a ninguna de las 16 alcaldías |
| Hechos no delictivos (se marcan) | 65,430 |  |
| Delitos de alto impacto según la FGJ | 286,727 |  |
| En los últimos 2 meses (subregistro, se marcan) | 29,600 | corte: 2024-07 |
| Registros en la base limpia | 1,919,217 |  |

## Carpetas por año del hecho (sin no delictivos ni duplicados)

| Año | Carpetas |
|---|---:|
| 2016 | 179,927 |
| 2017 | 206,425 |
| 2018 | 242,749 |
| 2019 | 239,258 |
| 2020 | 199,878 |
| 2021 | 219,583 |
| 2022 | 228,534 |
| 2023 | 220,401 |
| 2024 | 113,541 |

## Carpetas por grupo de delito

| Grupo | Dimensión | Carpetas |
|---|---|---:|
| fraude_extorsion | patrimonial | 302,983 |
| violencia_familiar | familiar | 239,518 |
| robo_otros | patrimonial | 156,018 |
| robo_transeunte | patrimonial | 139,649 |
| robo_autopartes | patrimonial | 132,830 |
| robo_negocio | patrimonial | 132,448 |
| otros | otros | 126,157 |
| amenazas | violencia | 125,612 |
| robo_vehiculo | patrimonial | 83,776 |
| hecho_no_delictivo | no_delictivo | 65,430 |
| lesiones_transito | vial | 61,235 |
| robo_transporte_publico | patrimonial | 61,112 |
| dano_propiedad | patrimonial | 58,031 |
| delitos_sexuales | sexual | 57,850 |
| lesiones_dolosas | violencia | 47,140 |
| robo_casa | patrimonial | 43,718 |
| narcomenudeo | otros | 37,998 |
| robo_repartidor_transp | patrimonial | 16,793 |
| homicidio_doloso | violencia | 9,636 |
| lesiones_arma_fuego | violencia | 9,488 |
| secuestro_privacion | violencia | 6,117 |
| homicidio_culposo | vial | 5,678 |

Base agregada: 33,478 filas (alcaldía × mes × grupo).
