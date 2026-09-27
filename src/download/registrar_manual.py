"""Registra en data/raw/MANIFEST.csv los archivos descargados a mano desde el navegador.

Se usa para fuentes que bloquean descargas automáticas (p. ej. el SESNSP publica en SharePoint,
que rechaza scripts). Coloca el archivo en data/raw/<carpeta>/ y ejecuta:

    .venv/bin/python -m src.download.registrar_manual data/raw/sesnsp/<archivo> "<URL de donde se bajó>"
"""
import sys
from pathlib import Path

from .comun import registrar

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    ruta, url = Path(sys.argv[1]).resolve(), sys.argv[2]
    registrar("descarga manual (navegador)", ruta, url)
    print(f"Registrado: {ruta.name}")
