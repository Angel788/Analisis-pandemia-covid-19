"""Descarga los puestos de trabajo asegurados del IMSS y conserva solo la CDMX.

El IMSS publica un CSV nacional por mes (~350 MB, separado por '|'). Para no ocupar decenas de GB,
el archivo se lee en streaming y solo se guardan las filas con cve_entidad = 9 (Ciudad de México),
comprimidas con gzip y en su codificación original (latin-1 o UTF-8, según el año).

Uso:
    .venv/bin/python -m src.download.imss                    # todos los meses 2016-01 → hoy
    .venv/bin/python -m src.download.imss --trimestral       # solo mar, jun, sep, dic
    .venv/bin/python -m src.download.imss --desde 2019 --hasta 2021
"""
from __future__ import annotations

import argparse
import calendar
import gzip
import time
from datetime import date

from .comun import PAUSA_S, RAW, registrar, sesion

URL = "http://datos.imss.gob.mx/sites/default/files/asg-{anio}-{mes:02d}-{dia:02d}.csv"
CVE_CDMX = "9"
DESTINO = RAW / "imss"


def meses(desde: int, hasta: int, trimestral: bool):
    hoy = date.today()
    for anio in range(desde, hasta + 1):
        for mes in (3, 6, 9, 12) if trimestral else range(1, 13):
            if (anio, mes) >= (hoy.year, hoy.month):
                return
            yield anio, mes


def descargar_mes(anio: int, mes: int) -> None:
    dia = calendar.monthrange(anio, mes)[1]
    url = URL.format(anio=anio, mes=mes, dia=dia)
    destino = DESTINO / f"asg_cdmx_{anio}_{mes:02d}.csv.gz"
    if destino.exists():
        print(f"  = ya existe  {destino.name}")
        registrar("datos.imss.gob.mx (filtrado cve_entidad=9)", destino, url)
        return

    parcial = destino.with_suffix(".gz.part")
    t0, n_total, n_cdmx = time.time(), 0, 0
    with sesion.get(url, stream=True, timeout=300) as r:
        if r.status_code == 404:
            print(f"  - no publicado {anio}-{mes:02d}")
            return
        r.raise_for_status()
        # Se filtra sobre bytes: la codificación cambia entre años (latin-1 en 2019, UTF-8 en 2025).
        with gzip.open(parcial, "wb") as salida:
            lineas = (l + b"\n" for l in r.iter_lines(chunk_size=1 << 20) if l)
            encabezado = next(lineas)
            salida.write(encabezado)
            idx = encabezado.split(b"|").index(b"cve_entidad")
            cve = CVE_CDMX.encode()
            n_malas = 0
            for linea in lineas:
                n_total += 1
                campos = linea.split(b"|", idx + 1)
                if len(campos) <= idx:  # línea truncada o mal formada en el archivo del IMSS
                    n_malas += 1
                    continue
                if campos[idx] == cve:
                    salida.write(linea)
                    n_cdmx += 1
    parcial.rename(destino)
    extra = f", {n_malas} líneas mal formadas omitidas" if n_malas else ""
    print(f"  ↓ {anio}-{mes:02d}: {n_cdmx:,} de {n_total:,} filas CDMX{extra}  ({time.time() - t0:.0f} s)")
    registrar("datos.imss.gob.mx (filtrado cve_entidad=9)", destino, url)
    time.sleep(PAUSA_S)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", type=int, default=2016)
    ap.add_argument("--hasta", type=int, default=date.today().year)
    ap.add_argument("--trimestral", action="store_true")
    a = ap.parse_args()
    DESTINO.mkdir(parents=True, exist_ok=True)
    print(f"\n# imss ({'trimestral' if a.trimestral else 'mensual'}, {a.desde}–{a.hasta})")
    for anio, mes in meses(a.desde, a.hasta, a.trimestral):
        descargar_mes(anio, mes)
