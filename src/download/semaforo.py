"""Descarga el historial semanal del semáforo epidemiológico federal por entidad.

Fuente: paquete de R `semaforos` (Hugo Gruson), que recopila los semáforos publicados por la
Secretaría de Salud en https://coronavirus.gob.mx/semaforo/. Es una compilación secundaria:
el semáforo local de la CDMX a veces se adelantó al federal (p. ej. rojo decretado el
18-dic-2020 y federal desde el 21-dic-2020); esas diferencias se documentan en la limpieza.

Uso:
    .venv/bin/python -m src.download.semaforo
"""
from .comun import RAW, descargar

URL = "https://raw.githubusercontent.com/Bisaloo/semaforos/main/inst/extdata/semaforos.csv"

if __name__ == "__main__":
    print("\n# semáforo epidemiológico (federal, por entidad y semana)")
    descargar(URL, RAW / "semaforo" / "semaforos_federal.csv", fuente="github.com/Bisaloo/semaforos")
