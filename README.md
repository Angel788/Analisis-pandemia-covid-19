# Proyecto — CDMX antes, durante y después del COVID-19

Proyecto de minería de datos. **Fase actual: recolección y limpieza de datos** (el modelado predictivo es una fase posterior).

## Cómo reproducir los datos
Los datos crudos (`data/raw/`, unos 3 GB) **no están en este repositorio** porque GitHub no admite archivos de más de 100 MB. Se regeneran con los scripts de descarga, y `data/raw/MANIFEST.csv` registra la URL, la fecha y el SHA-256 de cada archivo original, para verificar que son los mismos.

```bash
python -m venv .venv
.venv/bin/pip install pandas requests matplotlib ftfy pyarrow geopandas openpyxl jupyter

# 1. Descargar (tarda ~3 h, sobre todo el IMSS)
.venv/bin/python -m src.download.portal_cdmx
.venv/bin/python -m src.download.inegi
.venv/bin/python -m src.download.imss
.venv/bin/python -m src.download.semaforo
# SESNSP: descarga manual (ver PENDIENTES.md)

# 2. Limpiar (genera data/interim/)
.venv/bin/python -m src.clean.fgj
.venv/bin/python -m src.clean.metrobus
```

Los datos limpios pequeños (`data/interim/*.csv`) sí están en el repositorio. La base de carpetas de la FGJ a nivel de carpeta (`fgj_carpetas`, 495 MB) se regenera con `src.clean.fgj`.

El informe entregable está en `informe/main.pdf`; el contexto actualizado, en `CONTEXTO.md`, y las tareas, en `PENDIENTES.md`.

## 1. Pregunta de investigación

> ¿Cómo cambiaron los patrones de **movilidad**, **seguridad** y **actividad económica** de la Ciudad de México durante la pandemia de COVID-19, y qué diferencias se observan en su **recuperación** posterior respecto al periodo previo a 2020?

## 2. Definición del problema

### 2.1 Planteamiento
La pandemia (primer caso en México: 28-feb-2020; Jornada Nacional de Sana Distancia: 23-mar-2020) provocó un choque abrupto sobre la vida urbana de la CDMX. Los datos para medirlo existen, pero están **dispersos** en distintas instituciones (Gobierno CDMX, FGJ, SSC, C5, INEGI, IMSS, Secretaría de Salud), con **granularidades distintas** (diaria / mensual / trimestral; estación / colonia / alcaldía / entidad), formatos y calidades heterogéneas. No hay una base integrada que permita comparar las tres dimensiones sobre un mismo eje temporal y territorial.

El problema a resolver en esta fase es **construir un dataset integrado, limpio y documentado** que permita:
1. Medir la magnitud de la caída de cada dimensión en 2020.
2. Medir la velocidad y el nivel de recuperación (¿volvió a la línea base?, ¿cuándo?, ¿a un nuevo equilibrio?).
3. Relacionar las dimensiones entre sí y con la intensidad de la pandemia (casos, semáforo).
4. Servir de insumo a un modelo predictivo en la fase siguiente.

### 2.2 Periodos de análisis
| Periodo | Rango | Uso |
|---|---|---|
| Pre-pandemia (línea base) | 2016-01-01 → 2020-02-29 | Tendencia y estacionalidad "normal" |
| Confinamiento / choque | 2020-03-01 → 2021-06-30 | Caída y semáforo rojo/naranja |
| Transición | 2021-07-01 → 2022-12-31 | Reapertura gradual, vacunación |
| Post-pandemia | 2023-01-01 → último dato disponible | Recuperación / "nueva normalidad" |

> Los cortes son una propuesta inicial; se pueden ajustar con base en el semáforo epidemiológico de la CDMX.

### 2.3 Unidades de análisis
- **Temporal:** diaria donde exista; la base integrada se agregará a **semanal y mensual** (unidad común).
- **Territorial:** **alcaldía (16)** como unidad común; colonia/estación solo donde el dato lo permita.

### 2.4 Variables objetivo candidatas (para la fase predictiva)
- Afluencia mensual total en transporte público (Metro + Metrobús + STE + RTP).
- Delitos de alto impacto por alcaldía y mes.
- Empleo formal (asegurados IMSS) en la CDMX por mes.
- Índice de "recuperación" = valor observado / valor esperado sin pandemia (contrafactual estimado con la tendencia pre-2020).

### 2.5 Hipótesis de trabajo
- H1: La movilidad en transporte masivo cayó más de 50 % en abril–mayo 2020 y **no** recuperó el nivel previo al mismo ritmo que el tránsito vehicular.
- H2: Los delitos patrimoniales en vía pública (robo a transeúnte, en transporte) cayeron junto con la movilidad; la violencia familiar no bajó (o subió).
- H3: El empleo formal se recuperó antes que la movilidad en transporte público (efecto teletrabajo).
- H4: La recuperación fue desigual entre alcaldías (centrales vs. periféricas).

### 2.6 Alcance y limitaciones
- Fuera de alcance en esta fase: modelado, inferencia causal, pronósticos.
- Las carpetas de investigación miden **denuncias**, no delitos ocurridos (cifra negra ~90 % según ENVIPE). Complementar con 911 y ENVIPE/ENSU.
- Varias series COVID-específicas (Google Mobility, índice de movilidad CDMX) **no tienen línea base anterior a 2020**: sirven para el periodo pandémico, no para la comparación pre/post.
- Cobertura desigual: FGJ, Ecobici y ocupación hotelera terminan en 2024-07; el 911 en 2022-S1; la ENOE no tiene 2017 ni 2020-T2. La ventana post-pandemia común es 2023-01 → 2024-07.
- Los hechos de tránsito de la serie ampliada no son comparables entre años (cambió la forma de registro en 2021–2022).
- Cambios metodológicos: la FGJ reclasificó delitos y el portal distingue la serie "PGJ (archivo)" de "FGJ". Hay que documentarlo al unir.

## 3. Fuentes de información

### 3.0 Selección de datasets (decisión del 26-sep-2026)
De las 29 fuentes identificadas se seleccionaron **14**. Criterios: que tengan datos **antes de 2020** (línea base), que lleguen **hasta 2024–2025**, que sean **mensuales o más finas** (idealmente por alcaldía) y que se puedan **descargar sin registro**. El resto queda como **opcional**, por si hace falta ampliar.

| # | Dimensión | Dataset seleccionado | Granularidad | Desde | Aporta |
|---|---|---|---|---|---|
| 1 | Movilidad | Afluencia diaria del Metro ✅ descargado | día × estación | 2010 | Serie principal de movilidad |
| 2 | Movilidad | Afluencia diaria de Metrobús | día × línea | 2005 | Segundo sistema más usado |
| 3 | Movilidad | Viajes Ecobici | día / hora × género × edad | 2010 | Movilidad activa; cambio de hábitos |
| 4 | Movilidad | Hechos de tránsito SSC (serie ampliada + 2024) | evento × alcaldía | 2018 | Movilidad vehicular y seguridad vial |
| 5 | Seguridad | Carpetas de investigación FGJ | evento georreferenciado | 2016 | Delitos por tipo y alcaldía |
| 6 | Seguridad | Llamadas al 911 (C5) | llamada × alcaldía | 2019 | Emergencias, incluidas las no denunciadas |
| 7 | Seguridad | Incidencia delictiva municipal (SESNSP) | mes × municipio | 2015 | Validación oficial de la FGJ |
| 8 | Economía | Puestos de trabajo asegurados (IMSS) | mes × municipio × sector | 1997 | Empleo formal |
| 9 | Economía | ENOE (INEGI) | trimestre × entidad | 2005 | Desocupación e informalidad |
| 10 | Economía | DENUE (cortes anuales) | establecimiento georreferenciado | 2019 | Apertura y cierre de negocios |
| 11 | Economía | Ocupación hotelera | mes | 2018-10 | Turismo y servicios |
| 12 | Pandemia | Casos, pruebas y positividad CDMX | día | 2020-03 | Intensidad de la pandemia |
| 13 | Pandemia | Semáforo epidemiológico federal (compilación `semaforos`, GitHub) | semana | 2020-06 | Restricciones vigentes |
| 14 | Referencia | Población por alcaldía (Censo 2020) + Marco Geoestadístico | alcaldía | — | Tasas y llaves geográficas |

**Opcionales:** STE, RTP, afluencia preliminar, movilidad histórico COVID, GTFS, Google Mobility, víctimas FGJ, ENSU, ENVIPE, ITAEE (requiere token INEGI), directorio de unidades económicas CDMX, seguro de desempleo, Monitor Estadístico, SINAVE, casos por colonia y capacidad hospitalaria.

Las tablas siguientes conservan el inventario completo de fuentes identificadas.

### 3.0.1 Cobertura real de lo descargado (26-sep-2026)
Scripts en `src/download/`. Cada archivo queda registrado en `data/raw/MANIFEST.csv` con su URL, fecha, tamaño y SHA-256.

| Dataset | Carpeta `data/raw/` | Cobertura real | Registros | Observaciones |
|---|---|---|---|---|
| Metro (simple) | `metro/` | 2010-01 → 2026-07 | 1,180,920 | Mojibake; nombres de línea inconsistentes 2021–2023 |
| Metro (desglosada) | `metro/` | 2021-01 → 2026-07 | 1,192,230 | Solo desde 2021: no sirve para la línea base |
| Metrobús (simple) | `metrobus/` | 2005-07 → 2026-07 | 53,732 | Desglosada solo desde 2021 |
| Ecobici | `ecobici/` | 2010-02 → **2024-07** | 12,261 diarios | Termina en 2024-07 |
| Hechos de tránsito (comparable) | `hechos_transito/` | **2018 → 2019** | 30,758 | ⚠️ No cubre la pandemia; se reemplaza por la ampliada |
| Hechos de tránsito (ampliada) | `hechos_transito_ampliada/` | 2018 → 2023 | 134,079 | ⚠️ Salto 2021–2022 (17 mil → 30 mil/año): cambio de registro, "no comparable" |
| Hechos de tránsito 2024 | `hechos_transito_2024/` | 2024 | 30,655 | Fechas en formato dd/mm/aaaa |
| Carpetas FGJ | `fgj/` | 2016-01 → **2024-07** | 1,987,424 | 2024 incompleto (hasta julio); se descartó el acumulado (duplica los anuales) |
| Llamadas 911 | `911/` | 2019-S1 → **2022-S1** | 4,117,932 | ⚠️ No llega al post-pandemia; formatos de fecha mezclados |
| SESNSP municipal | `sesnsp/` | 2015 → 2025 | — | ⚠️ **Descarga manual**: SharePoint bloquea scripts |
| IMSS asegurados | `imss/` | 2016-01 → último mes | ~430–550 mil filas CDMX/mes | Se filtra la CDMX al vuelo (6 MB/mes en vez de 350 MB); latin-1 o UTF-8 según el año |
| ENOE | `enoe/` | 2016; 2018-T3 → 2020-T1; 2020-T3 → 2026-T2 | microdatos nacionales | Faltan 2017, 2018-T1/T2 y 2020-T2 (encuesta suspendida por COVID) |
| DENUE | `denue/` | cortes nov-2019 → nov-2024 + vigente (2026-09) | ~45 MB/corte | No hay corte nov-2025 publicado |
| Ocupación hotelera | `hoteles/` | 2018-10 → **2024-07** | 70 meses | Solo 16 meses de línea base |
| Casos COVID CDMX | `covid/` | 2020-03 → 2023-04 | 1,113 días | — |
| Semáforo | `semaforo/` | 2020-W22 → 2023-W24 | 32 estados | Falta la semana 2022-W01; es el semáforo federal (el local de la CDMX a veces se adelantó) |
| Censo 2020 (ITER) | `censo2020/` | 2020 | — | — |
| Marco Geoestadístico 2020 | `marco_geo/` | 2020 | — | Capas de alcaldías, colonias y AGEB |

**Consecuencia para el análisis:** varias series del portal (FGJ, Ecobici, ocupación hotelera) **terminan en julio de 2024**, y el 911 en junio de 2022. El periodo post-pandemia común a todas las fuentes es **2023-01 → 2024-07**. Metro, Metrobús e IMSS llegan hasta 2026.

**Inventario completo.** Estado: ✅ verificado en el catálogo CKAN de datos.cdmx.gob.mx (26-sep-2026) · 🔎 falta verificar/descargar.

### 3.1 Movilidad
| Dataset | Fuente | Granularidad | Cobertura | Estado | Enlace |
|---|---|---|---|---|---|
| Afluencia diaria del Metro (simple y desglosada) | STC Metro / Portal CDMX | Día × estación × línea | 2010-01 → 2026-07 | ✅ | https://datos.cdmx.gob.mx/dataset/afluencia-diaria-del-metro-cdmx |
| Afluencia diaria de Metrobús (simple y desglosada) | Metrobús | Día × línea | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/afluencia-diaria-de-metrobus-cdmx |
| Afluencia diaria STE (Trolebús, Tren Ligero, Cablebús) | STE | Día × línea | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/afluencia-diaria-servicio-de-transportes-electricos |
| Afluencia diaria RTP | RTP | Día × ruta | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/afluencia-diaria-de-la-red-de-transporte-de-pasajeros |
| Afluencia preliminar en transporte público (histórico) | SEMOVI | Día × sistema | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/afluencia-preliminar-en-transporte-publico |
| Viajes del sistema Ecobici | Ecobici | Viaje individual | 🔎 (cambio de sistema en 2022) | ✅ | https://datos.cdmx.gob.mx/dataset/afluencia-diaria-del-sistema-ecobici |
| Datos de movilidad (histórico COVID-19): tránsito vehicular, índices Metro/Metrobús, Suburbano | Gobierno CDMX | Día / semana | 2020 → ~2022 | ✅ | https://datos.cdmx.gob.mx/dataset/movilidad-historico-covid-19 |
| Hechos de tránsito SSC (serie comparable interanual) | SSC | Evento | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/hechos-de-transito-reportados-por-ssc-base-comparativa |
| Google COVID-19 Community Mobility Reports | Google | Día × entidad | 2020-02 → 2022-10 | 🔎 | https://www.google.com/covid19/mobility/ |
| GTFS estático CDMX (geometría de rutas y estaciones) | SEMOVI | Estático | — | ✅ | https://datos.cdmx.gob.mx/dataset/gtfs |

### 3.2 Seguridad
| Dataset | Fuente | Granularidad | Cobertura | Estado | Enlace |
|---|---|---|---|---|---|
| Carpetas de investigación FGJ (CSV anuales + acumulado) | FGJ CDMX | Evento con coordenadas, colonia, alcaldía | 2016 → 2024+ | ✅ | https://datos.cdmx.gob.mx/dataset/carpetas-de-investigacion-fgj-de-la-ciudad-de-mexico |
| Víctimas en carpetas de investigación FGJ | FGJ CDMX | Víctima (sexo, edad) | 2019 → | ✅ | https://datos.cdmx.gob.mx/dataset/victimas-en-carpetas-de-investigacion-fgj |
| Llamadas al 911 (semestrales) | C5 CDMX | Llamada × incidente × alcaldía | 2019-S1 → 2022+ | ✅ | https://datos.cdmx.gob.mx/dataset/llamadas-numero-de-atencion-a-emergencias-911 |
| Incidencia delictiva del fuero común (municipal) | SESNSP | Mes × municipio × delito | 2015 → | 🔎 | https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva |
| ENSU — percepción de inseguridad | INEGI | Trimestre × ciudad | 2013 → | 🔎 | https://www.inegi.org.mx/programas/ensu/ |
| ENVIPE — victimización y cifra negra | INEGI | Anual × entidad | 2011 → | 🔎 | https://www.inegi.org.mx/programas/envipe/ |

### 3.3 Actividad económica
| Dataset | Fuente | Granularidad | Cobertura | Estado | Enlace |
|---|---|---|---|---|---|
| Puestos de trabajo asegurados (datos abiertos IMSS) | IMSS | Mes × entidad × municipio × sector | 1997 → | 🔎 | http://datos.imss.gob.mx/ |
| ENOE / ETOE — ocupación, desocupación, informalidad | INEGI | Trimestre × entidad | 2005 → | 🔎 | https://www.inegi.org.mx/programas/enoe/15ymas/ |
| ITAEE — Indicador Trimestral de la Actividad Económica Estatal | INEGI (BIE) | Trimestre × entidad × sector | 2003 → | 🔎 | https://www.inegi.org.mx/temas/itaee/ |
| DENUE — unidades económicas (cortes anuales) | INEGI | Establecimiento con coordenadas | cortes 2019 → | 🔎 | https://www.inegi.org.mx/app/descarga/?ti=6 |
| Directorio estadístico de unidades económicas CDMX | Portal CDMX | Establecimiento | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/directorio-estadistico-de-unidades-economicas-ciudad-de-mexico |
| Solicitudes al Seguro de Desempleo CDMX | STyFE | 🔎 | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/solicitudes-seguro-de-desempleo |
| Ocupación hotelera en la CDMX | SECTUR CDMX | Mes | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/ocupacion-hotelera-en-la-ciudad-de-mexico |
| Indicadores Monitor Estadístico CDMX | Gobierno CDMX | 🔎 | 🔎 | ✅ | https://datos.cdmx.gob.mx/dataset/indicadores-monitor-estadistico-de-la-ciudad-de-mexico |

### 3.4 Pandemia (variables de control / exógenas)
| Dataset | Fuente | Granularidad | Estado | Enlace |
|---|---|---|---|---|
| Casos positivos, pruebas y positividad CDMX | Portal CDMX | Día | ✅ | https://datos.cdmx.gob.mx/dataset/total-de-pruebas-total-de-positivos-y-tasa-de-positividad |
| Base SINAVE COVID-19 (CDMX) | SINAVE | Caso individual | ✅ | https://datos.cdmx.gob.mx/dataset/base-covid-sinave |
| Histórico de casos a nivel colonia | SINAVE / CDMX | Colonia | ✅ | https://datos.cdmx.gob.mx/dataset/covid-19-sinave-ciudad-de-mexico-a-nivel-colonia |
| Capacidad hospitalaria ZMVM | Portal CDMX | Día × hospital | ✅ | https://datos.cdmx.gob.mx/dataset/capacidad-hospitalaria |
| Semáforo epidemiológico CDMX (color por semana) | Gobierno CDMX | Semana | 🔎 construir tabla a mano desde comunicados | https://covid19.cdmx.gob.mx/ |
| Datos abiertos COVID-19 nacional | Secretaría de Salud | Caso individual | 🔎 | https://www.gob.mx/salud/documentos/datos-abiertos-152127 |

### 3.5 Referencias territoriales y de población
| Dataset | Fuente | Uso |
|---|---|---|
| Marco Geoestadístico (alcaldías, colonias, AGEB) | INEGI | Llaves geográficas y shapefiles |
| Censo de Población y Vivienda 2020 | INEGI | Población por alcaldía → tasas por 100 mil hab. |
| Proyecciones de población | CONAPO | Denominadores anuales |
| Calendario de días festivos / vacaciones SEP | — | Control de estacionalidad |

## 4. Estructura de carpetas
```
Metro/
├── CONTEXTO.md, PENDIENTES.md
├── .venv/                       ← entorno de Python
├── data/
│   ├── raw/                     ← descargas originales, sin tocar (una carpeta por fuente)
│   │   ├── MANIFEST.csv         ← URL, fecha, tamaño y SHA-256 de cada archivo
│   │   └── descarga_*.log       ← bitácora de cada corrida
│   ├── interim/                 ← limpios por fuente (Parquet)
│   └── processed/               ← base integrada (alcaldía × mes, CDMX × semana)
├── docs/                        ← diccionarios y notas metodológicas
├── informe/                     ← informe LaTeX entregable
├── notebooks/
│   └── 00_contexto_y_datasets.ipynb
└── src/
    ├── download/
    │   ├── comun.py             ← caché, pausas entre descargas, MANIFEST con candado
    │   ├── portal_cdmx.py       ← API CKAN de datos.cdmx.gob.mx
    │   ├── inegi.py             ← DENUE, Censo, Marco Geoestadístico, ENOE
    │   ├── imss.py              ← asegurados IMSS filtrados a la CDMX
    │   ├── semaforo.py          ← semáforo federal (GitHub)
    │   └── registrar_manual.py  ← registra en el MANIFEST lo bajado a mano (SESNSP)
    └── clean/                   ← (siguiente paso)
```

## 5. Criterios de limpieza (comunes a todas las fuentes)
- **Codificación:** forzar UTF-8. Ej.: el CSV del Metro muestra `Isabel la CatÃ³lica` (texto mal codificado: mojibake) → reparar con `ftfy` o re-decodificar.
- **Fechas:** a `datetime` ISO; revisar fecha de hecho vs. fecha de inicio/registro (carpetas FGJ).
- **Alcaldías:** catálogo único con clave INEGI (`09002` … `09017`); normalizar acentos, mayúsculas y nombres viejos ("Delegación").
- **Estaciones / líneas:** catálogo único (nombres cambian: p. ej. estaciones renombradas, Línea 12 cerrada 2021-05-03 → 2023/2024, Línea 1 cerrada por modernización desde 2022-07).
- **Faltantes y ceros:** distinguir "sin servicio" (cierre) de "dato faltante".
- **Duplicados** y registros fuera de la CDMX (carpetas con coordenadas fuera del polígono).
- **Categorías de delito:** mapear a un catálogo estable (alto impacto, patrimonial, violencia familiar, etc.) que sobreviva a las reclasificaciones de la FGJ.
- **Agregación:** toda serie se entrega también a nivel `alcaldía × mes` y `CDMX × semana`.
- **Trazabilidad:** registrar para cada archivo raw la URL, la fecha de descarga y el hash (`data/raw/MANIFEST.csv`).
