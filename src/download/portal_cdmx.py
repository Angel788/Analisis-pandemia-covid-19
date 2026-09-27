"""Descarga los datasets seleccionados del Portal de Datos Abiertos de la CDMX.

Las URL se obtienen en cada ejecución desde la API CKAN del portal (package_show),
así que si el portal publica un archivo nuevo, el script lo descarga.

Uso:
    .venv/bin/python -m src.download.portal_cdmx            # todos
    .venv/bin/python -m src.download.portal_cdmx metro fgj  # solo algunos
"""
from __future__ import annotations

import re
import sys
import unicodedata

from .comun import RAW, descargar, sesion

CKAN = "https://datos.cdmx.gob.mx/api/3/action/package_show"

# carpeta destino -> (id CKAN, regex de los recursos a incluir; None = todos)
DATASETS = {
    "metro":           ("afluencia-diaria-del-metro-cdmx", None),
    "metrobus":        ("afluencia-diaria-de-metrobus-cdmx", None),
    "ecobici":         ("afluencia-diaria-del-sistema-ecobici", None),
    # La serie "comparable" solo cubre 2018-2019; la "ampliada" (no comparable con ella) cubre la pandemia.
    "hechos_transito": ("hechos-de-transito-reportados-por-ssc-base-comparativa", None),
    "hechos_transito_ampliada": ("hechos-de-transito-reportados-por-ssc-base-ampliada-no-comparativa",
                                 r"^(Hechos de tr|Diferencias)"),
    "hechos_transito_2024": ("hechos-de-transito-registrados-por-la-ssc-2024-serie-de-datos-ampliada-no-comparativa",
                             r"^Hechos de tr"),
    # Solo los CSV anuales + notas PDF; el acumulado (560 MB) repite los mismos datos.
    "fgj":             ("carpetas-de-investigacion-fgj-de-la-ciudad-de-mexico", r"^(?!.*acumulado)"),
    "911":             ("llamadas-numero-de-atencion-a-emergencias-911", None),
    "hoteles":         ("ocupacion-hotelera-en-la-ciudad-de-mexico", None),
    "covid":           ("total-de-pruebas-total-de-positivos-y-tasa-de-positividad", None),
}

# Nombres fijos para archivos que ya se descargaron antes con otro nombre.
NOMBRES_FIJOS = {
    "0e8ffe58-28bb-4dde-afcd-e5f5b4de4ccb": "afluencia_metro_simple.csv",
}


def nombre_archivo(recurso: dict) -> str:
    rid = recurso["id"]
    if rid in NOMBRES_FIJOS:
        return NOMBRES_FIJOS[rid]
    ext = (recurso.get("format") or "bin").lower()
    url_nombre = recurso["url"].rsplit("/", 1)[-1]
    # Los archivos del servidor "archivo.datos.cdmx.gob.mx" ya tienen nombre descriptivo.
    if not re.fullmatch(r"[0-9a-f-]{36}\.\w+", url_nombre):
        return url_nombre
    sin_acentos = unicodedata.normalize("NFKD", recurso["name"]).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-z0-9]+", "_", sin_acentos.lower().strip()).strip("_")
    return f"{base[:80]}.{ext}"


def descargar_dataset(carpeta: str) -> None:
    pid, patron = DATASETS[carpeta]
    print(f"\n# {carpeta}  ({pid})")
    paquete = sesion.get(CKAN, params={"id": pid}, timeout=60).json()["result"]
    for rec in paquete["resources"]:
        if patron and not re.search(patron, rec["name"], flags=re.I):
            continue
        descargar(rec["url"], RAW / carpeta / nombre_archivo(rec), fuente=f"datos.cdmx.gob.mx/{pid}")


if __name__ == "__main__":
    elegidos = sys.argv[1:] or list(DATASETS)
    for c in elegidos:
        descargar_dataset(c)
