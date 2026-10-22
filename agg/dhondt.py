from __future__ import annotations

from fractions import Fraction
from typing import Iterable


def _candidaturas(candidaturas) -> list[tuple[str, int]]:
    out = []
    iterable = candidaturas.items() if isinstance(candidaturas, dict) else candidaturas
    for c in iterable:
        if isinstance(c, dict):
            out.append((str(c["etiqueta"]), int(c["votos"])))
        else:
            out.append((str(c[0]), int(c[1])))
    return sorted(out, key=lambda x: (-x[1], x[0]))


def reparto(candidaturas: Iterable, escanos: int, validos: int) -> dict[str, int]:
    items = _candidaturas(candidaturas)
    if escanos < 0:
        raise ValueError("escanos no puede ser negativo")
    if validos <= 0:
        raise ValueError("validos debe ser positivo")
    asignados = {label: 0 for label, _ in items}
    elegibles = [
        (label, votos) for label, votos in items
        if votos > 0 and Fraction(votos, validos) >= Fraction(3, 100)
    ]
    if not elegibles:
        return asignados
    for _ in range(escanos):
        mejor = None
        mejor_q = None
        for label, votos in elegibles:
            q = Fraction(votos, asignados[label] + 1)
            if mejor is None or q > mejor_q or (q == mejor_q and votos > dict(elegibles)[mejor]):
                mejor, mejor_q = label, q
        asignados[mejor] += 1
    return asignados


def marginal(candidaturas: Iterable, escanos: int, validos: int) -> dict:
    items = _candidaturas(candidaturas)
    if validos <= 0:
        raise ValueError("validos debe ser positivo")
    asignados = {label: 0 for label, _ in items}
    elegibles = [
        (label, votos) for label, votos in items
        if votos > 0 and Fraction(votos, validos) >= Fraction(3, 100)
    ]
    if not elegibles or escanos < 1:
        return {"ultimo": None, "siguiente": None, "margen_votos": None}
    ultimo = None
    for _ in range(escanos):
        mejor = None
        mejor_q = None
        for label, votos in elegibles:
            q = Fraction(votos, asignados[label] + 1)
            if mejor is None or q > mejor_q or (q == mejor_q and votos > dict(elegibles)[mejor]):
                mejor, mejor_q = label, q
        asignados[mejor] += 1
        ultimo = {
            "etiqueta": mejor,
            "votos": dict(elegibles)[mejor],
            "escanos_previos": asignados[mejor] - 1,
            "divisor": asignados[mejor],
            "cociente": mejor_q,
        }
    siguientes = [
        (label, votos) for label, votos in elegibles
        if label != ultimo["etiqueta"]
    ]
    if not siguientes:
        return {"ultimo": _json_round(ultimo), "siguiente": None, "margen_votos": None}
    sig_label, sig_votos = max(
        siguientes,
        key=lambda x: (Fraction(x[1], asignados[x[0]] + 1), x[1], x[0]),
    )
    sig_q = Fraction(sig_votos, asignados[sig_label] + 1)
    necesario = int(ultimo["cociente"] * (asignados[sig_label] + 1)) + 1
    margen = max(0, necesario - sig_votos)
    return {
        "ultimo": _json_round(ultimo),
        "siguiente": {
            "etiqueta": sig_label,
            "votos": sig_votos,
            "escanos": asignados[sig_label],
            "cociente": round(float(sig_q), 2),
        },
        "margen_votos": margen,
        "margen_pct": round(100.0 * margen / validos, 3) if validos else None,
    }


def _json_round(d: dict | None) -> dict | None:
    if not d:
        return None
    return {
        "etiqueta": d["etiqueta"],
        "votos": d["votos"],
        "escanos_previos": d["escanos_previos"],
        "divisor": d["divisor"],
        "cociente": round(float(d["cociente"]), 2),
    }
