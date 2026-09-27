"""Utilidades comunes de descarga.

- No vuelve a descargar un archivo que ya existe (caché local).
- Espera entre descargas para no saturar los servidores.
- Registra cada archivo en data/raw/MANIFEST.csv (fuente, URL, fecha, tamaño, SHA-256).
"""
from __future__ import annotations

import csv
import fcntl
import hashlib
import time
from datetime import datetime
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw"
MANIFEST = RAW / "MANIFEST.csv"
CAMPOS = ["fuente", "archivo", "url", "fecha_descarga", "bytes", "sha256"]
PAUSA_S = 2
USER_AGENT = "Mozilla/5.0 (proyecto escolar de mineria de datos; descarga de datos abiertos)"

sesion = requests.Session()
sesion.headers["User-Agent"] = USER_AGENT


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _manifest() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        return {fila["archivo"]: fila for fila in csv.DictReader(f)}


def registrar(fuente: str, ruta: Path, url: str) -> None:
    """Agrega o actualiza la fila del archivo en el MANIFEST (con candado: varios scripts pueden correr a la vez)."""
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST.with_suffix(".lock"), "w") as candado:
        fcntl.flock(candado, fcntl.LOCK_EX)
        _registrar(fuente, ruta, url)


def _registrar(fuente: str, ruta: Path, url: str) -> None:
    filas = _manifest()
    clave = str(ruta.relative_to(RAW))
    if clave in filas and filas[clave]["bytes"] == str(ruta.stat().st_size):
        return
    filas[clave] = {
        "fuente": fuente,
        "archivo": clave,
        "url": url,
        "fecha_descarga": datetime.fromtimestamp(ruta.stat().st_mtime).isoformat(timespec="seconds"),
        "bytes": ruta.stat().st_size,
        "sha256": sha256(ruta),
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(sorted(filas.values(), key=lambda r: r["archivo"]))


def descargar(url: str, destino: Path, fuente: str, reintentos: int = 3) -> Path:
    """Descarga `url` a `destino` si no existe y la registra en el MANIFEST."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0:
        print(f"  = ya existe  {destino.relative_to(RAIZ)}")
        registrar(fuente, destino, url)
        return destino

    parcial = destino.with_suffix(destino.suffix + ".part")
    for intento in range(1, reintentos + 1):
        try:
            with sesion.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(parcial, "wb") as f:
                    for bloque in r.iter_content(1 << 20):
                        f.write(bloque)
            parcial.rename(destino)
            mb = destino.stat().st_size / 1e6
            print(f"  ↓ {mb:7.1f} MB  {destino.relative_to(RAIZ)}")
            registrar(fuente, destino, url)
            time.sleep(PAUSA_S)
            return destino
        except requests.RequestException as e:
            print(f"  ! intento {intento}/{reintentos} falló: {e}")
            time.sleep(PAUSA_S * intento * 2)
    raise RuntimeError(f"No se pudo descargar {url}")
