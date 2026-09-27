"""Descarga los productos de INEGI seleccionados (solo CDMX cuando INEGI lo permite).

- DENUE: cortes de noviembre 2019–2024 más el corte vigente (CDMX, entidad 09).
- Censo 2020: resultados por localidad (ITER) de la CDMX.
- Marco Geoestadístico 2020: capas de la CDMX (alcaldías, colonias/AGEB).
- ENOE: microdatos trimestrales (nacionales; INEGI no los publica por entidad).

Uso:
    .venv/bin/python -m src.download.inegi                 # todo
    .venv/bin/python -m src.download.inegi denue censo     # solo algunos
"""
from __future__ import annotations

import sys
from datetime import date

from .comun import RAW, descargar, sesion

BASE = "https://www.inegi.org.mx/contenidos"
FUENTE = "inegi.org.mx"


def existe(url: str) -> bool:
    """INEGI responde 200 con una página de error de ~2 KB cuando el archivo no existe."""
    r = sesion.head(url, allow_redirects=True, timeout=60)
    return r.ok and int(r.headers.get("Content-Length", 0)) > 100_000


def denue() -> None:
    print("\n# denue")
    for anio in range(2019, date.today().year + 1):
        url = f"{BASE}/masiva/denue/{anio}_11/denue_09_11{anio % 100:02d}_csv.zip"
        if existe(url):
            descargar(url, RAW / "denue" / f"denue_09_{anio}_11.zip", FUENTE)
    # Corte vigente (se sobrescribe en el servidor con cada actualización).
    hoy = date.today().isoformat()[:7]
    descargar(f"{BASE}/masiva/denue/denue_09_csv.zip", RAW / "denue" / f"denue_09_vigente_{hoy}.zip", FUENTE)


def censo() -> None:
    print("\n# censo 2020")
    descargar(f"{BASE}/programas/ccpv/2020/datosabiertos/iter/iter_09_cpv2020_csv.zip",
              RAW / "censo2020" / "iter_09_cpv2020_csv.zip", FUENTE)


def marco_geo() -> None:
    print("\n# marco geoestadístico 2020")
    descargar(f"{BASE}/productos/prod_serv/contenidos/espanol/bvinegi/productos/geografia/"
              "marcogeo/889463807469/09_ciudaddemexico.zip",
              RAW / "marco_geo" / "09_ciudaddemexico_mg2020.zip", FUENTE)


def enoe() -> None:
    """ENOE clásica ('enoe') y ENOE nueva de la pandemia ('enoen', 2020-T3 a 2022-T4).

    No existen en datos abiertos: 2017, 2018-T1/T2 y 2020-T2 (encuesta suspendida por COVID-19).
    """
    print("\n# enoe")
    for anio in range(2016, date.today().year + 1):
        for trim in range(1, 5):
            for prefijo in ("enoe", "enoen"):
                url = (f"{BASE}/programas/enoe/15ymas/datosabiertos/{anio}/"
                       f"conjunto_de_datos_{prefijo}_{anio}_{trim}t_csv.zip")
                destino = RAW / "enoe" / f"enoe_{anio}_t{trim}.zip"
                if destino.exists() or existe(url):
                    descargar(url, destino, FUENTE)
                    break


PASOS = {"denue": denue, "censo": censo, "marco_geo": marco_geo, "enoe": enoe}

if __name__ == "__main__":
    for nombre in sys.argv[1:] or PASOS:
        PASOS[nombre]()
