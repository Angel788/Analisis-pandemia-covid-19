"""Agrupa los ~350 delitos de la FGJ en categorías estables entre años.

Se clasifica por palabras clave del delito (texto normalizado, sin acentos), no por su nombre exacto,
para que los cambios de denominación del catálogo (nota de reclasificación de feb-2020) no afecten.
El orden importa: gana la primera regla que coincide.
"""
from __future__ import annotations

import re

import pandas as pd

from .catalogos import normalizar

# (grupo, dimensión de análisis, regex sobre el delito normalizado)
REGLAS: list[tuple[str, str, str]] = [
    ("homicidio_doloso",        "violencia",   r"^HOMICIDIO(?!.*CULPOS)|FEMINICIDIO"),
    ("homicidio_culposo",       "vial",        r"HOMICIDIO CULPOS"),
    ("lesiones_arma_fuego",     "violencia",   r"LESIONES.*(ARMA DE FUEGO|DISPARO)"),
    ("secuestro_privacion",     "violencia",   r"SECUESTRO|PLAGIO|PRIVACION DE LA LIBERTAD"),
    ("delitos_sexuales",        "sexual",      r"VIOLACION|ABUSO SEXUAL|ACOSO SEXUAL|ESTUPRO|HOSTIGAMIENTO SEXUAL|PORNOGRAF|LENOCINIO|TRATA|EXHIBICIONES OBSCENAS|CONTRA LA INTIMIDAD SEXUAL"),
    ("violencia_familiar",      "familiar",    r"VIOLENCIA FAMILIAR"),
    ("robo_transporte_publico", "patrimonial", r"ROBO A (PASAJERO|TRANSEUNTE A BORDO)|ROBO A USUARIO"),
    ("robo_transeunte",         "patrimonial", r"ROBO A TRANSEUNTE"),
    ("robo_vehiculo",           "patrimonial", r"ROBO DE (VEHICULO|MOTOCICLETA)(?! DE PEDALES)|ROBO DE VEHICULO AUTOMOTOR"),
    ("robo_autopartes",         "patrimonial", r"ROBO DE (ACCESORIOS|OBJETOS DEL INTERIOR|PLACA|AUTOPARTES)"),
    ("robo_negocio",            "patrimonial", r"ROBO A (NEGOCIO|SUCURSAL|TIENDA)"),
    ("robo_casa",               "patrimonial", r"ROBO A CASA HABITACION"),
    ("robo_repartidor_transp",  "patrimonial", r"ROBO A (REPARTIDOR|TRANSPORTISTA)"),
    ("robo_otros",              "patrimonial", r"ROBO"),
    ("fraude_extorsion",        "patrimonial", r"FRAUDE|EXTORSION|USURPACION DE IDENTIDAD|ABUSO DE CONFIANZA|FALSIFICACION|COBRANZA ILEGITIMA|DESPOJO|ADMINISTRACION FRAUDULENTA"),
    ("lesiones_transito",       "vial",        r"(LESIONES|DANO EN PROPIEDAD AJENA) CULPOS.*TRANSITO|TRANSITO VEHICULAR"),
    ("lesiones_dolosas",        "violencia",   r"LESIONES"),
    ("amenazas",                "violencia",   r"AMENAZAS|INTIMIDACION"),
    ("narcomenudeo",            "otros",       r"NARCOMENUDEO|CONTRA LA SALUD"),
    ("dano_propiedad",          "patrimonial", r"DANO EN PROPIEDAD|DANO A LA PROPIEDAD"),
]
_COMPILADAS = [(g, d, re.compile(r)) for g, d, r in REGLAS]


def _grupo(delito: str | None) -> tuple[str, str]:
    if delito:
        for g, d, r in _COMPILADAS:
            if r.search(delito):
                return g, d
    return "otros", "otros"


def clasificar(delito: pd.Series, categoria: pd.Series) -> pd.DataFrame:
    """Devuelve grupo_delito y dimension por fila. Los 'hechos no delictivos' se separan aparte."""
    unicos = pd.Series(delito.unique())
    tabla = pd.DataFrame([_grupo(normalizar(x)) for x in unicos],
                         index=unicos, columns=["grupo_delito", "dimension_delito"])
    out = tabla.reindex(delito.values).set_index(delito.index)
    no_delictivo = categoria.map(normalizar).eq("HECHO NO DELICTIVO")
    out.loc[no_delictivo, ["grupo_delito", "dimension_delito"]] = ["hecho_no_delictivo", "no_delictivo"]
    return out
