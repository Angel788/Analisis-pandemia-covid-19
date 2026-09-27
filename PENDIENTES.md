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
- [ ] **SESNSP (manual, te toca a ti):** bajar desde el navegador "2015 - 2025 (Fuero Común - Delitos). Incidencia delictiva municipal" en https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva, guardarlo en `data/raw/sesnsp/` y registrarlo con `.venv/bin/python -m src.download.registrar_manual data/raw/sesnsp/<archivo> "<url>"`

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
- [ ] 911: unificar los formatos de fecha (≈60 % no se interpreta con un solo formato desde 2020-S1)
- [ ] 911: revisar los traslapes entre semestres (cada archivo trae fechas de otros semestres) y quitar duplicados
- [ ] Hechos de tránsito: documentar el salto 2021–2022 de la serie ampliada (cambio de registro) y decidir si se usa solo como indicador relativo
- [ ] Definir la ventana post-pandemia común (2023-01 → 2024-07) por el corte de FGJ, Ecobici y hoteles
- [ ] Semáforo: rellenar las semanas 2020-W53 y 2022-W01 (no vienen en el archivo) y documentar las diferencias con el semáforo local de la CDMX

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
- [x] **FGJ** (`src/clean/fgj.py`): 1,987,424 → 1,937,812 carpetas; fecha del hecho; 22 grupos de delito estables; duplicados y últimos 2 meses marcados
- [x] **Metrobús** (`src/clean/metrobus.py`): líneas unificadas (14 → 7), 2 errores anulados, 57 valores estimados marcados, 30 días atípicos reales conservados
- [x] Notebook `01_limpieza_datasets.ipynb` con los resultados de FGJ y Metrobús (reportes, faltantes, gráficas)
- [ ] Semáforo (notebook 01): ya está en formato largo y guardado; falta rellenar 2020-W53 y 2022-W01
- [ ] Metro: pasar a script la limpieza del notebook (mojibake, `LÃ­nea N`/`Linea N`) y marcar los cierres de L12 (2021-05 → 2023) y L1 (2022-07 → 2024)
- [ ] Ecobici
- [ ] Hechos de tránsito (unificar formatos de fecha entre la ampliada y 2024)
- [ ] 911: unificar los formatos de fecha, revisar traslapes entre semestres y homologar los tipos de incidente
- [ ] IMSS: sumar `ta` (puestos de trabajo) por mes para toda la CDMX, con desglose por sector, sexo y rango salarial. **No hay desglose por alcaldía** (`cve_municipio` vacío en toda la CDMX). Detectar la codificación por archivo y aceptar `.csv` y `.csv.gz`
- [x] Descargar el diccionario oficial del IMSS (`data/raw/imss/diccionario_de_datos_imss.xlsx`)
- [ ] ENOE (calcular desocupación e informalidad de la CDMX con factores de expansión)
- [ ] DENUE, ocupación hotelera, casos COVID, semáforo (rellenar 2022-W01), Censo 2020
- [ ] Catálogo de estaciones de Metro y Metrobús con alcaldía (GTFS) — opcional, para bajar la movilidad a nivel alcaldía

### Decisiones tomadas en la limpieza (26-sep-2026)
- FGJ: se analiza por **fecha del hecho**; se descartan hechos anteriores a 2016 (32,223) y fuera de la CDMX (16,734).
- FGJ: las filas idénticas (3,824; 0.19 %) se **marcan, no se borran** (parecen denuncias múltiples de un mismo fraude).
- FGJ: los 2 meses finales (jun–jul 2024) se marcan como **incompletos** por denuncia tardía.
- Metrobús: los días bajos por eventos reales (19-S, elecciones, festivos) **se conservan**.

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
