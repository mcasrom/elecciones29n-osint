"""Definiciones únicas de las métricas derivadas del observatorio.

Regla: ninguna cifra derivada se calcula en una plantilla ni con expresiones
ad hoc. Cada métrica tiene aquí su función y su base. El build y el validador
usan las mismas funciones; los tests fijan el contrato.
"""
from __future__ import annotations

from datetime import datetime


def moving_average(points: list, days: int = 14) -> list[dict]:
    """Media móvil centrada de `days` días sobre los sondeos de un partido.

    `points`: [{"date": "YYYY-MM-DD", "value": float, ...}]
    Devuelve [{"date", "value"}] con una media por fecha (ventana ±days/2).
    """
    if not points:
        return []
    half = days // 2
    dates = sorted({p["date"] for p in points})
    out = []
    for d in dates:
        dt = datetime.strptime(d, "%Y-%m-%d")
        vals = [p["value"] for p in points
                if abs((datetime.strptime(p["date"], "%Y-%m-%d") - dt).days) <= half]
        if vals:
            out.append({"date": d, "value": sum(vals) / len(vals)})
    return out


def spark_summary(points: list, days: int = 14) -> dict:
    """Resumen de una serie para una tarjeta: MA, primer/último valor y delta.

    La cifra grande y el delta se calculan SIEMPRE sobre la media móvil, no
    sobre el último sondeo ni sobre el primer sondeo de otra casa.
    """
    ma = moving_average(points, days)
    if not ma:
        return {"ma": [], "first": None, "last": None, "delta": None}
    first = ma[0]["value"]
    last = ma[-1]["value"]
    return {"ma": ma, "first": first, "last": last, "delta": last - first}


def series_span(series: dict) -> str:
    """Periodo real (min–max) de todas las fechas de una serie larga."""
    dates = sorted({p["date"] for vals in series.values() for p in vals})
    return f"{dates[0]} – {dates[-1]}" if dates else ""
