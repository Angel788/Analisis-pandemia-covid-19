"""Catálogos compartidos por todos los scripts de limpieza.

- Alcaldías de la CDMX con su clave INEGI (Marco Geoestadístico 2020).
- Normalización de texto (mayúsculas, sin acentos, sin espacios dobles, reparando mojibake).
- Asignación de alcaldía a partir de coordenadas (punto en polígono).
"""
from __future__ import annotations

import re
import unicodedata
from functools import cache
from pathlib import Path

import ftfy
import geopandas as gpd
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw"
INTERIM = RAIZ / "data" / "interim"
MARCO_GEO = RAW / "marco_geo" / "09_ciudaddemexico_mg2020.zip"


def guardar(df: pd.DataFrame, nombre: str) -> None:
    """Guarda en data/interim/ como CSV (utf-8-sig: Excel muestra bien los acentos) y como Parquet."""
    INTERIM.mkdir(parents=True, exist_ok=True)
    df.to_csv(INTERIM / f"{nombre}.csv", index=False, encoding="utf-8-sig")
    df.to_parquet(INTERIM / f"{nombre}.parquet", index=False)
    print(f"  → data/interim/{nombre}.csv / .parquet ({len(df):,} filas)")


def normalizar(texto) -> str | None:
    """'Álvaro  Obregón' / 'ALVARO OBREGON' / 'Ã\x81lvaro ObregÃ³n' → 'ALVARO OBREGON'."""
    if texto is None or (isinstance(texto, float) and pd.isna(texto)):
        return None
    t = ftfy.fix_text(str(texto))
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"\s+", " ", t).strip().upper()
    return t or None


@cache
def alcaldias() -> gpd.GeoDataFrame:
    """16 alcaldías: cve_alcaldia (p. ej. '09015'), alcaldia (nombre oficial), geometry (EPSG:4326)."""
    g = gpd.read_file(f"zip://{MARCO_GEO}!conjunto_de_datos/09mun.shp")
    g = g.rename(columns={"CVEGEO": "cve_alcaldia", "NOMGEO": "alcaldia"})[["cve_alcaldia", "alcaldia", "geometry"]]
    return g.to_crs(4326)


# Variantes que aparecen en las fuentes → nombre normalizado del catálogo
_ALIAS = {
    "CUAJIMALPA": "CUAJIMALPA DE MORELOS",
    "MAGDALENA CONTRERAS": "LA MAGDALENA CONTRERAS",
    "GUSTAVO A MADERO": "GUSTAVO A. MADERO",
    "GAM": "GUSTAVO A. MADERO",
}


@cache
def _mapa_nombres() -> dict[str, str]:
    return {normalizar(n): c for c, n in alcaldias()[["cve_alcaldia", "alcaldia"]].itertuples(index=False)}


def cve_por_nombre(nombres: pd.Series) -> pd.Series:
    """Serie de nombres de alcaldía (cualquier escritura) → clave INEGI; None si no es una alcaldía."""
    mapa = _mapa_nombres()
    norm = nombres.map(normalizar).replace(_ALIAS)
    norm = norm.str.replace(r"^(ALCALDIA|DELEGACION)\s+", "", regex=True)
    return norm.map(mapa)


def cve_por_coordenadas(lat: pd.Series, lon: pd.Series) -> pd.Series:
    """Asigna la alcaldía que contiene cada punto (None si cae fuera de la CDMX o no hay coordenadas)."""
    puntos = gpd.GeoDataFrame(index=lat.index, geometry=gpd.points_from_xy(lon, lat), crs=4326)
    validos = puntos[lat.notna() & lon.notna()]
    unidos = gpd.sjoin(validos, alcaldias()[["cve_alcaldia", "geometry"]], how="left", predicate="within")
    unidos = unidos[~unidos.index.duplicated()]  # puntos exactamente en un límite
    return unidos["cve_alcaldia"].reindex(lat.index)


def nombre_alcaldia(cves: pd.Series) -> pd.Series:
    return cves.map(dict(alcaldias()[["cve_alcaldia", "alcaldia"]].itertuples(index=False)))
