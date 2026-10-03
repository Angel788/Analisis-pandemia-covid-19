# Actividades pendientes — Fase 1: recolección y limpieza

Ver contexto y fuentes en [CONTEXTO.md](CONTEXTO.md).

> Cada actividad realizada se documenta en el informe LaTeX: `informe/secciones/04_bitacora.tex` (compilar con `latexmk -pdf main.tex` dentro de `informe/`).

## 0. Preparación
- [x] Definir la pregunta y el problema
- [x] Identificar las fuentes de información (ver CONTEXTO.md §3)
- [ ] Crear la estructura de carpetas (`data/raw`, `data/interim`, `data/processed`, `docs`, `src`, `notebooks`)
- [x] Crear el entorno de Python (`.venv`: pandas, pyarrow, ftfy, requests, matplotlib, jupyter; falta geopandas)
- [x] Notebook de contexto `notebooks/00_contexto_y_datasets.ipynb`
- [ ] Inicializar git y agregar `data/raw/` al `.gitignore` (los CSV pesan cientos de MB)
- [ ] Crear `data/raw/MANIFEST.csv` (fuente, url, fecha_descarga, sha256)
- [ ] Confirmar los cortes de periodos (pre / choque / transición / post)
- [x] Seleccionar los datasets a usar: 14 seleccionados y el resto opcionales (26-sep-2026)
- [x] **Selección final: 8 datasets** — Metro, Metrobús, hechos de tránsito, FGJ, IMSS, ocupación hotelera + COVID y semáforo como control. Descartados: Ecobici, 911, ENOE, SESNSP, DENUE (ver CONTEXTO.md §3.0.0)

- [x] Repositorio en GitHub: `.gitignore` excluye `data/raw/` (3 GB) y `fgj_carpetas` (495 MB); se suben el código, los notebooks, el informe, el MANIFEST y los CSV limpios pequeños (commit de 6 MB)

## 1. Descarga (14 datasets seleccionados — ver CONTEXTO.md §3.0 y §3.0.1)
Scripts en `src/download/`; cada archivo queda en `data/raw/MANIFEST.csv`.

### Movilidad
- [x] Metro: simple + desglosada + diccionarios
- [x] Metrobús: simple (desde 2005) + desglosada (desde 2021) + diccionarios
- [x] Ecobici: diarios y mensuales desglosados (termina en 2024-07)
- [x] Hechos de tránsito SSC: comparable (solo 2018–2019) + **ampliada 2018–2023** + 2024

### Seguridad
- [x] Carpetas FGJ: CSV anuales 2016–2024 (2024 hasta julio) + 3 notas PDF
- [x] Llamadas 911: 2019-S1 → 2022-S1 (no hay más en el portal)
- [~] ~~SESNSP~~ (descartado en la selección final)

### Economía
- [x] IMSS: 128 meses (2016-01 → 2026-08) filtrados a la CDMX, 717 MB en `.csv.gz` (1 línea mal formada omitida en 2025-01)
- [x] ENOE: 35 trimestres de microdatos, 1.5 GB (no existen 2017, 2018-T1/T2 ni 2020-T2)
- [x] DENUE: cortes nov-2019 → nov-2024 + vigente 2026-09
- [x] Ocupación hotelera (2018-10 → 2024-07)

### Pandemia y referencias
- [x] Casos, pruebas y positividad CDMX (2020-03 → 2023-04)
- [x] Semáforo federal semanal (compilación `semaforos` en GitHub; ya no hace falta construirlo a mano)
- [x] Censo 2020 (ITER CDMX)
- [x] Marco Geoestadístico 2020 CDMX (83 MB)

### Problemas encontrados en la descarga → tareas nuevas
- [ ] Hechos de tránsito: documentar el salto 2021–2022 de la serie ampliada (cambio de registro) y decidir si se usa solo como indicador relativo
- [ ] Definir la ventana post-pandemia común (2023-01 → 2024-07) por el corte de FGJ, Ecobici y hoteles
- [x] Semáforo: rellenar las semanas 2020-W53 y 2022-W01 (mismo color que la semana anterior y la siguiente; columna `imputado`) (2-oct-2026)
- [ ] Semáforo: documentar las diferencias con el semáforo local de la CDMX

### Opcionales (solo si hace falta ampliar)
- [ ] STE, RTP, afluencia preliminar, movilidad histórico COVID, GTFS, Google Mobility
- [ ] Víctimas FGJ, ENSU, ENVIPE
- [ ] ITAEE (token INEGI), directorio de unidades económicas, seguro de desempleo, Monitor Estadístico
- [ ] SINAVE, casos por colonia, capacidad hospitalaria, calendario de festivos

## 2. Exploración inicial (por dataset)
- [ ] Para cada dataset: filas, columnas, rango de fechas, % de nulos, tipos, valores únicos de las categóricas
- [ ] Guardar el resumen en `docs/perfil_<fuente>.md`
- [ ] Anotar los cambios metodológicos conocidos (PGJ→FGJ, reclasificaciones, Ecobici nuevo sistema, cierres de la L12 y la L1)

## 3. Limpieza (un script por fuente en `src/clean/`; reporte de cada una en `docs/limpieza_<fuente>.md`)
### Comunes
- [x] Catálogo único de alcaldías con clave INEGI y polígonos del Marco Geoestadístico (`src/clean/catalogos.py`)
- [x] Función de normalización de texto (acentos, mayúsculas, mojibake) y asignación de alcaldía por coordenadas
- [x] Guardar las salidas limpias en `data/interim/` en CSV (principal) y Parquet (respaldo), con `guardar()` de `catalogos.py`

### Por fuente
- [x] **FGJ** (`src/clean/fgj.py`): 1,987,424 → 1,919,217 carpetas (sin las 18,595 sin alcaldía, 2-oct-2026); fecha del hecho; 22 grupos de delito estables; duplicados y últimos 2 meses marcados
- [x] **Metrobús** (`src/clean/metrobus.py`): líneas unificadas (14 → 7), 2 errores anulados, 57 valores estimados marcados, 30 días atípicos reales conservados
- [x] Notebook `01_limpieza_datasets.ipynb` con los resultados de FGJ y Metrobús (reportes, faltantes, gráficas)
- [x] Notebook 01: limpieza explícita paso a paso de FGJ y Metrobús (comprobada contra la salida de los scripts), y explicación de cada paso del semáforo, el IMSS y los hoteles (2-oct-2026)
- [x] Informe: separadores de miles con coma (1,180,920) en lugar de espacio fino (2-oct-2026)
- [x] Verificación de todas las cifras del informe contra `data/interim/`; 5 correcciones (FGJ p90 = 56 días, hora 00:00:00 en duplicados, mínimo IMSS = mar-2021, excepciones por alcaldía, Línea B) (2-oct-2026)
- [x] Estandarización (2-oct-2026): FGJ sin carpetas sin alcaldía (solo 16 alcaldías); clave de alcaldía en `metro_estacion_mes` + nueva `metro_alcaldia_mes`; Metrobús y COVID sin vacíos (ver CONTEXTO §3.0.2)
- [ ] Decidir si los 10 días sin conteo del Metro (servicio gratuito; 120 vacíos en `metro_linea_dia`) se imputan en el paso de completar
- [x] Versión en Word: `informe/informe.docx`, generada con `informe/a_word.py` (requiere pandoc o `pip install pypandoc_binary`) (2-oct-2026)
- [x] Semáforo (notebook 01): formato largo, 160 semanas completas; 2020-W53 (rojo) y 2022-W01 (verde) rellenadas y marcadas con `imputado`
- [x] Metro (notebook 01): mojibake, 24 → 12 líneas, 2 estaciones con doble escritura, duplicado Oceanía/Deportivo Oceanía, columna `estado` (abierta / cerrada / no_existia / sin_registro), cierres de L12 y L1 marcados → `metro_linea_dia`, `metro_estacion_mes`, `metro_mes`; tabla de errores y 3 gráficas (27-sep-2026)
- [ ] Metro: en la integración usar `afluencia_diaria_promedio` y una variante **sin L1 ni L12** (2021-05 → 2025-12) para separar obras de pandemia
- [ ] Metro (opcional): pasar la limpieza del notebook a `src/clean/metro.py`, como la del Metrobús
- [~] ~~Ecobici~~ (descartado)
- [x] Hechos de tránsito (notebook 01): fechas unificadas, 28 duplicados eliminados, alcaldías a clave INEGI, agregado mes × alcaldía × tipo con lesionados y fallecidos → `transito_alcaldia_mes.csv`; errores documentados en el notebook
- [x] Tránsito: gráficas (tipos, peatones/ciclistas, mapa de calor por alcaldía, fallecidos) en el notebook 01 y en el informe
- [x] Tránsito: tabla diaria `transito_alcaldia_dia` (día × alcaldía × tipo, 245,472 filas); 7 días con registro bajo marcados con `registro_bajo` (27-sep-2026)
- [ ] Tránsito: si se analiza por día o semana, excluir o imputar los 7 días con `registro_bajo`
- [ ] Tránsito: usar **atropellados** como indicador principal y **2019** como línea base; no usar caídas de ciclista (corte de registro en feb-2020) ni el 1er semestre de 2018 (incompleto)
- [~] ~~911~~ (descartado)
- [x] IMSS (notebook 01): `imss_subdelegacion_mes.csv` con 128 meses × 10 subdelegaciones; validado (sexo y rangos suman igual a puestos; dic-2019 = 3,470,048)
- [x] IMSS: gráficas de top subdelegaciones, rangos UMA y salario (notebook 01) agregadas al informe
- [ ] IMSS: San Ángel tiene saltos de ±60 mil puestos mes a mes desde 2025-10 (probables reasignaciones administrativas): no usar subdelegaciones para conclusiones de empleo
- [ ] IMSS: quitar el espacio final en `delegacion` (`.str.strip()`)
- [ ] IMSS: deflactar `salario_promedio` con el INPC (INEGI) para compararlo en términos reales
- [ ] IMSS: revisar los grupos de UMA ("hasta 2 UMA" se vacía desde 2023 porque el salario mínimo ≈ 2.3 UMA); decidir cortes más útiles o usar solo el salario promedio
- [ ] IMSS (opcional): tabla aparte por `sector_economico_1` para ver qué sectores perdieron empleo
- [x] Descargar el diccionario oficial del IMSS (`data/raw/imss/diccionario_de_datos_imss.xlsx`)
- [~] ~~ENOE~~ (descartado)
- [ ] Ocupación hotelera: **backcasting 2016 → 2018-09 con regresión** sobre el empleo IMSS del sector de hoteles y restaurantes (confirmar el código en el catálogo)
- [ ] FGJ: factor de completitud para jun–jul 2024 (denuncias tardías), en lugar de solo marcarlos
- [x] Ocupación hotelera (notebook 01): redondeo a 2 decimales, fecha al día 1, `ocupacion_pct` → `data/interim/hoteles_mes.csv`
- [ ] Ocupación hotelera: columna `imputado` + backcasting 2016 → 2018-09 (paso de completar)
- [x] Casos COVID (notebook 01): días faltantes de mar-2020 → 0, inconsistencia del 29-mar-2020 corregida, tasas recalculadas, promedio móvil 7 días → `covid_dia`, `covid_semana`, `covid_mes` (27-sep-2026)
- [x] FGJ: `fgj_alcaldia_mes` ahora incluye el nombre de la alcaldía (27-sep-2026)
- [ ] Censo 2020: población por alcaldía (para tasas de FGJ y tránsito por 100 mil hab.)
- [ ] Catálogo de estaciones de Metro y Metrobús con alcaldía (GTFS) — opcional, para bajar la movilidad a nivel alcaldía

### Decisiones tomadas en la limpieza (26-sep-2026)
- FGJ: se analiza por **fecha del hecho**; se descartan hechos anteriores a 2016 (32,223) y fuera de la CDMX (16,734).
- FGJ: las filas idénticas (3,824; 0.19 %) se **marcan, no se borran** (parecen denuncias múltiples de un mismo fraude).
- FGJ: los 2 meses finales (jun–jul 2024) se marcan como **incompletos** por denuncia tardía.
- Metrobús: los días bajos por eventos reales (19-S, elecciones, festivos) **se conservan**.
- Metro (27-sep-2026): los días de servicio gratuito sin conteo (16–17 mar 2016, 20–27 sep 2017) quedan **vacíos**, no en 0; los ceros de estaciones cerradas **se conservan** como 0 real; los atípicos altos (12-dic en Deportivo 18 de Marzo, eventos en Zócalo, reaperturas) **se conservan**.

- [ ] Reformular H4 en el informe: solo se evalúa con FGJ y hechos de tránsito

## 4. Integración
- [ ] Definir las llaves comunes: `fecha` (día/semana/mes) + `cve_alcaldia`
- [ ] Agregar cada fuente a `alcaldía × mes` y a `CDMX × semana`
- [ ] Unir en `data/processed/cdmx_mensual_alcaldia.parquet` y `cdmx_semanal.parquet`
- [ ] Calcular tasas por 100 mil habitantes e índices base 100 = promedio de 2019
- [ ] Añadir las variables de periodo (`pre`, `choque`, `transicion`, `post`) y el color del semáforo
- [ ] Validar: totales agregados contra las cifras oficiales publicadas (muestreo)

## 5. Documentación y entrega de la fase
- [ ] Diccionario de datos de la base integrada (`docs/diccionario_base_integrada.md`)
- [ ] Registro de las decisiones de limpieza y sus supuestos
- [ ] Notebook con gráficas descriptivas pre/durante/post por dimensión
- [ ] Revisión final: ¿la base responde la pregunta? ¿Hay huecos que cubrir antes del modelado?

## Siguiente fase (fuera de alcance por ahora)
- Contrafactual "sin pandemia" con la tendencia pre-2020 (SARIMA / Prophet)
- Modelo predictivo (gradient boosting / series de tiempo) sobre las variables objetivo definidas en CONTEXTO.md §2.4
