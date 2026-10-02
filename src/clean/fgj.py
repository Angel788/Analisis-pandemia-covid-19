"""Limpieza de las carpetas de investigación de la FGJ (2016–2024).

Entrada:  data/raw/fgj/carpetasFGJ_<año>.csv   (carpetas INICIADAS en ese año)
Salidas:  data/interim/fgj_carpetas.csv / .parquet     (una fila por carpeta, limpia)
          data/interim/fgj_alcaldia_mes.csv / .parquet (conteos por alcaldía × mes del hecho × grupo de delito)
          docs/limpieza_fgj.md                  (reporte de cada paso con conteos)

Decisiones (ver docs/limpieza_fgj.md):
- El análisis temporal usa la FECHA DEL HECHO, no la de inicio de la carpeta.
- Se descartan hechos anteriores a 2016 (su registro está incompleto: solo aparecen si se denunciaron
  desde 2016) y los hechos fuera de la CDMX.
- La alcaldía se toma de `alcaldia_hecho`; si falta, se infiere de las coordenadas. Las
  "CDMX (indeterminada)" se conservan para el total de la ciudad, sin alcaldía.
- Las filas idénticas en todas las columnas se MARCAN (`duplicado_exacto`), no se borran.
- Los últimos meses están subregistrados: un hecho se denuncia con retraso (p90 = 70 días) y el
  archivo termina en la fecha de corte. Se marca con `mes_incompleto`.

Uso:
    .venv/bin/python -m src.clean.fgj
"""
from __future__ import annotations

import glob

import pandas as pd

from .catalogos import RAIZ, RAW, cve_por_coordenadas, guardar, cve_por_nombre, nombre_alcaldia, normalizar
from .grupos_delito import clasificar

INICIO = pd.Timestamp("2016-01-01")
# Meses finales con subregistro por denuncia tardía (≈10 % de los hechos se denuncian después de 70 días)
MESES_INCOMPLETOS = 2

reporte: list[tuple[str, int, str]] = []


def paso(nombre: str, n: int, nota: str = "") -> None:
    reporte.append((nombre, n, nota))
    print(f"  {nombre:<55} {n:>10,}  {nota}")


def cargar() -> pd.DataFrame:
    partes = []
    for p in sorted(glob.glob(str(RAW / "fgj" / "carpetasFGJ_*.csv"))):
        d = pd.read_csv(p, low_memory=False, dtype=str)
        d["archivo_origen"] = p.rsplit("/", 1)[-1]
        partes.append(d)
    return pd.concat(partes, ignore_index=True)


def limpiar(d: pd.DataFrame) -> pd.DataFrame:
    paso("Registros leídos (9 archivos anuales)", len(d))

    # --- duplicados: se marcan con todas las columnas originales
    originales = [c for c in d.columns if c != "archivo_origen"]
    d["duplicado_exacto"] = d.duplicated(subset=originales, keep="first")
    paso("  de ellos, idénticos en las 21 columnas (se marcan)", int(d.duplicado_exacto.sum()))

    # --- fechas
    d["fecha_hecho"] = pd.to_datetime(d["fecha_hecho"], errors="coerce")
    d["fecha_inicio"] = pd.to_datetime(d["fecha_inicio"], errors="coerce")
    sin_fecha = d.fecha_hecho.isna()
    paso("Sin fecha del hecho (se descartan)", int(sin_fecha.sum()))
    d = d[~sin_fecha]
    viejos = d.fecha_hecho < INICIO
    paso("Hecho anterior a 2016 (se descartan)", int(viejos.sum()), "registro incompleto")
    d = d[~viejos]
    futuros = d.fecha_hecho > d.fecha_inicio
    paso("Hecho posterior al inicio de la carpeta (se descartan)", int(futuros.sum()), "fecha inconsistente")
    d = d[~futuros]

    # --- territorio
    fuera = d["alcaldia_hecho"].map(normalizar).eq("FUERA DE CDMX")
    paso("Hecho fuera de la CDMX (se descartan)", int(fuera.sum()))
    d = d[~fuera].copy()
    d["latitud"] = pd.to_numeric(d["latitud"], errors="coerce")
    d["longitud"] = pd.to_numeric(d["longitud"], errors="coerce")
    d["cve_alcaldia"] = cve_por_nombre(d["alcaldia_hecho"])
    faltan = d.cve_alcaldia.isna()
    recuperadas = cve_por_coordenadas(d.loc[faltan, "latitud"], d.loc[faltan, "longitud"])
    d.loc[faltan, "cve_alcaldia"] = recuperadas
    paso("Alcaldía recuperada por coordenadas", int(recuperadas.notna().sum()))
    paso("En la CDMX sin alcaldía identificable (se conservan)", int(d.cve_alcaldia.isna().sum()),
         "cuentan solo para el total de la ciudad")
    d["alcaldia"] = nombre_alcaldia(d["cve_alcaldia"])

    # --- delitos
    d = d.join(clasificar(d["delito"], d["categoria_delito"]))
    cat = d["categoria_delito"].map(normalizar)
    d["alto_impacto"] = ~cat.isin(["DELITO DE BAJO IMPACTO", "HECHO NO DELICTIVO"])
    paso("Hechos no delictivos (se marcan)", int(d.grupo_delito.eq("hecho_no_delictivo").sum()))
    paso("Delitos de alto impacto según la FGJ", int(d.alto_impacto.sum()))

    # --- meses con subregistro al final de la serie
    ultimo_mes = d.fecha_inicio.max().to_period("M")
    d["mes"] = d.fecha_hecho.dt.to_period("M").dt.to_timestamp()
    d["mes_incompleto"] = d.fecha_hecho.dt.to_period("M") > ultimo_mes - MESES_INCOMPLETOS
    paso(f"En los últimos {MESES_INCOMPLETOS} meses (subregistro, se marcan)", int(d.mes_incompleto.sum()),
         f"corte: {ultimo_mes}")

    columnas = ["fecha_hecho", "hora_hecho", "mes", "fecha_inicio", "delito", "categoria_delito",
                "grupo_delito", "dimension_delito", "alto_impacto", "cve_alcaldia", "alcaldia",
                "colonia_catalogo", "latitud", "longitud", "fiscalia", "duplicado_exacto",
                "mes_incompleto", "archivo_origen"]
    d = d[columnas].sort_values("fecha_hecho").reset_index(drop=True)
    paso("Registros en la base limpia", len(d))
    return d


def agregar(d: pd.DataFrame) -> pd.DataFrame:
    """Conteos por alcaldía × mes × grupo (sin hechos no delictivos ni duplicados)."""
    base = d[~d.duplicado_exacto & d.grupo_delito.ne("hecho_no_delictivo")]
    ag = (base.assign(cve_alcaldia=base.cve_alcaldia.fillna("09000"))  # 09000 = CDMX sin alcaldía
              .groupby(["cve_alcaldia", "mes", "grupo_delito", "dimension_delito"], observed=True)
              .size().rename("carpetas").reset_index())
    ag["mes_incompleto"] = ag.mes.isin(d.loc[d.mes_incompleto, "mes"].unique())
    ag.insert(1, "alcaldia", nombre_alcaldia(ag.cve_alcaldia).fillna("CDMX (sin alcaldía)"))
    return ag


def escribir_reporte(d: pd.DataFrame, ag: pd.DataFrame) -> None:
    anual = d[~d.duplicado_exacto & d.grupo_delito.ne("hecho_no_delictivo")]
    anual = anual.groupby(anual.fecha_hecho.dt.year).size()
    lineas = ["# Limpieza de carpetas de investigación FGJ", "",
              "Generado por `src/clean/fgj.py`.", "", "## Pasos", "",
              "| Paso | Registros | Nota |", "|---|---:|---|"]
    lineas += [f"| {p} | {n:,} | {nota} |" for p, n, nota in reporte]
    lineas += ["", "## Carpetas por año del hecho (sin no delictivos ni duplicados)", "",
               "| Año | Carpetas |", "|---|---:|"]
    lineas += [f"| {a} | {n:,} |" for a, n in anual.items()]
    lineas += ["", "## Carpetas por grupo de delito", "", "| Grupo | Dimensión | Carpetas |", "|---|---|---:|"]
    g = d.groupby(["grupo_delito", "dimension_delito"]).size().sort_values(ascending=False)
    lineas += [f"| {a} | {b} | {n:,} |" for (a, b), n in g.items()]
    lineas += ["", f"Base agregada: {len(ag):,} filas (alcaldía × mes × grupo)."]
    (RAIZ / "docs").mkdir(exist_ok=True)
    (RAIZ / "docs" / "limpieza_fgj.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    print("# Limpieza FGJ")
    d = limpiar(cargar())
    ag = agregar(d)
    guardar(d, "fgj_carpetas")
    guardar(ag, "fgj_alcaldia_mes")
    escribir_reporte(d, ag)
    print("  → docs/limpieza_fgj.md")
