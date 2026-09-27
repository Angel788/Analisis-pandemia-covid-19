"""Limpieza de la afluencia diaria del Metrobús (2005–2026).

Entrada:  data/raw/metrobus/afluencia_diaria_del_metrobus_simple.csv
Salidas:  data/interim/metrobus_linea_dia.csv / .parquet  (fecha × línea)
          data/interim/metrobus_mes.csv / .parquet        (total mensual y por línea)
          docs/limpieza_metrobus.md

Decisiones:
- Los vacíos antes de la inauguración de cada línea NO son faltantes: la línea no existía
  (el diccionario lo confirma). Se marcan con `linea_operando = False`.
- En 2023 las líneas vienen como "linea N" y en el resto como "Línea N": se unifican a "Línea N".
- Valores atípicos: se comparan contra la mediana móvil de 29 días de la misma línea. Los días bajos
  explicables (domingos, festivos, sismo 19-S, elecciones, visita papal) se conservan. Solo se anulan
  los errores evidentes listados en ERRORES.
- 57 valores con decimales (Línea 4, ene–feb 2025) se tratan como estimaciones: se redondean y se marcan.
- La desglosada (por tipo de pago, desde 2021) suma exactamente lo mismo que la simple, así que no se
  usa para la serie; queda en raw para análisis de gratuidad.

Uso:
    .venv/bin/python -m src.clean.metrobus
"""
from __future__ import annotations

import pandas as pd

from .catalogos import RAIZ, RAW, guardar

ENTRADA = RAW / "metrobus" / "afluencia_diaria_del_metrobus_simple.csv"

# (fecha, línea) → motivo. Se anulan (NaN) y se marcan.
ERRORES = {
    ("2005-07-26", "Línea 1"): "3.03 M: ~13 veces un día normal; probable acumulado desde la inauguración",
    ("2017-09-20", "Línea 2"): "9 pasajeros el día posterior al sismo 19-S; dato imposible o servicio suspendido",
}
UMBRAL_ALTO, UMBRAL_BAJO = 2.5, 0.2

reporte: list[tuple[str, str]] = []


def limpiar() -> pd.DataFrame:
    d = pd.read_csv(ENTRADA, parse_dates=["fecha"])
    reporte.append(("Registros leídos (fecha × línea)", f"{len(d):,}"))
    antes = d.linea.nunique()
    d["linea"] = d["linea"].str.strip().str.replace(r"^[Ll][ií]nea", "Línea", regex=True)
    reporte.append(("Nombres de línea distintos → unificados", f"{antes} → {d.linea.nunique()}"))

    inicio = d.dropna(subset=["afluencia"]).groupby("linea").fecha.min()
    d["linea_operando"] = d.fecha >= d.linea.map(inicio)
    reporte.append(("Filas antes de la inauguración de su línea (no son faltantes)", f"{(~d.linea_operando).sum():,}"))
    reporte.append(("Faltantes con la línea operando", f"{(d.linea_operando & d.afluencia.isna()).sum():,}"))

    dup = d.duplicated(["fecha", "linea"])
    reporte.append(("Duplicados fecha × línea", f"{dup.sum():,}"))
    d = d[~dup]

    # atípicos respecto a la mediana móvil
    d = d.sort_values(["linea", "fecha"])
    mediana = d.groupby("linea").afluencia.transform(
        lambda x: x.rolling(29, center=True, min_periods=10).median())
    d["ratio_mediana"] = (d.afluencia / mediana).round(3)
    d["atipico"] = (d.ratio_mediana > UMBRAL_ALTO) | (d.ratio_mediana < UMBRAL_BAJO)
    reporte.append((f"Días atípicos (> {UMBRAL_ALTO}× o < {UMBRAL_BAJO}× la mediana de 29 días)",
                    f"{d.atipico.sum():,} (se conservan salvo errores evidentes)"))

    d["error_corregido"] = ""
    for (fecha, linea), motivo in ERRORES.items():
        m = d.fecha.eq(fecha) & d.linea.eq(linea)
        d.loc[m, "afluencia"] = pd.NA
        d.loc[m, "error_corregido"] = motivo
    reporte.append(("Errores evidentes anulados", f"{len(ERRORES)}"))

    # 57 valores con decimales (Línea 4, ene–feb 2025 y 1 en 2026): probablemente estimados por el
    # Metrobús, no conteos. Se redondean y se marcan.
    d["valor_estimado"] = d.afluencia.notna() & (d.afluencia % 1 != 0)
    reporte.append(("Valores con decimales (probables estimaciones; se redondean y marcan)", f"{d.valor_estimado.sum():,}"))
    d["afluencia"] = d["afluencia"].round().astype("Int64")
    return d[["fecha", "linea", "afluencia", "linea_operando", "atipico", "ratio_mediana", "valor_estimado",
              "error_corregido"]] \
        .sort_values(["fecha", "linea"]).reset_index(drop=True)


def mensual(d: pd.DataFrame) -> pd.DataFrame:
    op = d[d.linea_operando]
    por_linea = (op.assign(mes=op.fecha.dt.to_period("M").dt.to_timestamp())
                   .pivot_table(index="mes", columns="linea", values="afluencia", aggfunc="sum"))
    dias = op.groupby(op.fecha.dt.to_period("M").dt.to_timestamp()).fecha.nunique()
    m = pd.DataFrame({
        "afluencia_total": por_linea.sum(axis=1),
        "lineas_operando": op.groupby(op.fecha.dt.to_period("M").dt.to_timestamp()).linea.nunique(),
        "dias_con_dato": dias,
    })
    m["afluencia_diaria_promedio"] = (m.afluencia_total / m.dias_con_dato).round(0)
    por_linea.columns = [c.lower().replace("í", "i").replace(" ", "_") for c in por_linea.columns]
    return m.join(por_linea).reset_index(names="mes")


def escribir_reporte(d: pd.DataFrame, m: pd.DataFrame) -> None:
    anual = m.groupby(m.mes.dt.year).afluencia_diaria_promedio.mean().round(0)
    base = anual.get(2019)
    at = d[d.atipico].sort_values("fecha")
    lineas = ["# Limpieza de afluencia del Metrobús", "", "Generado por `src/clean/metrobus.py`.", "",
              "## Pasos", "", "| Paso | Resultado |", "|---|---|"]
    lineas += [f"| {a} | {b} |" for a, b in reporte]
    lineas += ["", "## Errores anulados", "", "| Fecha | Línea | Motivo |", "|---|---|---|"]
    lineas += [f"| {f} | {l} | {mo} |" for (f, l), mo in ERRORES.items()]
    lineas += ["", "## Días atípicos conservados (eventos reales)", "",
               "| Fecha | Línea | Afluencia | × mediana |", "|---|---|---:|---:|"]
    lineas += [f"| {r.fecha.date()} | {r.linea} | {r.afluencia if pd.notna(r.afluencia) else '—'} | {r.ratio_mediana} |"
               for r in at.itertuples() if not r.error_corregido]
    lineas += ["", "## Afluencia diaria promedio por año", "", "| Año | Viajes/día | Índice 2019=100 |", "|---|---:|---:|"]
    lineas += [f"| {a} | {v:,.0f} | {v / base * 100:.1f} |" for a, v in anual.items()]
    lineas += ["", "Nota: la red creció (Línea 6 en 2016, Línea 7 en 2018 y ampliaciones posteriores), así que",
               "parte del aumento posterior a 2022 refleja más cobertura y no solo más demanda."]
    (RAIZ / "docs" / "limpieza_metrobus.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    print("# Limpieza Metrobús")
    d = limpiar()
    m = mensual(d)
    for a, b in reporte:
        print(f"  {a:<75} {b}")
    guardar(d, "metrobus_linea_dia")
    guardar(m, "metrobus_mes")
    escribir_reporte(d, m)
    print("  → docs/limpieza_metrobus.md")
