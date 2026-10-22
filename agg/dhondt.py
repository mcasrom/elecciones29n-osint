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


def _reparto_con_traza(
    items: list[tuple[str, int]], escanos: int, validos: int
) -> tuple[dict[str, int], dict | None, list[tuple[str, int]]]:
    if escanos < 0:
        raise ValueError("escanos no puede ser negativo")
    if validos <= 0:
        raise ValueError("validos debe ser positivo")
    asignados = {label: 0 for label, _ in items}
    elegibles = [
        (label, votos) for label, votos in items
        if votos > 0 and Fraction(votos, validos) >= Fraction(3, 100)
    ]
    if not elegibles or escanos < 1:
        return asignados, None, elegibles
    votos_por_label = dict(elegibles)
    ultimo = None
    for _ in range(escanos):
        mejor = None
        mejor_q = None
        for label, votos in elegibles:
            q = Fraction(votos, asignados[label] + 1)
            if (
                mejor is None
                or q > mejor_q
                or (q == mejor_q and votos > votos_por_label[mejor])
            ):
                mejor, mejor_q = label, q
        asignados[mejor] += 1
        ultimo = {
            "etiqueta": mejor,
            "votos": votos_por_label[mejor],
            "escanos_previos": asignados[mejor] - 1,
            "divisor": asignados[mejor],
            "cociente": mejor_q,
        }
    return asignados, ultimo, elegibles


def reparto(candidaturas: Iterable, escanos: int, validos: int) -> dict[str, int]:
    asignados, _, _ = _reparto_con_traza(_candidaturas(candidaturas), escanos, validos)
    return asignados


def _margen_para_escaro(
    items: list[tuple[str, int]], escanos: int, validos: int, label: str
) -> int | None:
    """Votos adicionales mínimos para que `label` obtenga escaño.

    Se recalcula D'Hondt añadiendo esos votos a la candidatura y al total de
    válidos (el resto de candidaturas no cambia). Así se contempla también el
    efecto del umbral del 3 %. No es una diferencia de cocientes.
    """
    base = dict(items)

    def gana(extra: int) -> bool:
        candidaturas = dict(base)
        candidaturas[label] += extra
        return reparto(candidaturas, escanos, validos + extra).get(label, 0) > 0

    if gana(0):
        return 0
    hi = max(1, validos)
    for _ in range(40):
        if gana(hi):
            break
        hi *= 2
        if hi > 50_000_000:
            return None
    else:
        return None
    lo = 0
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if gana(mid):
            hi = mid
        else:
            lo = mid
    return hi


def marginal(candidaturas: Iterable, escanos: int, validos: int) -> dict:
    """Último escaño y primera candidatura que se quedó sin escaño.

    `siguiente` es la primera candidatura *sin escaño* entre las que superan el
    3 %, ordenada por su cociente final. `margen_votos` son los votos
    adicionales que necesitaba para obtener escaño, recalculando D'Hondt y el
    umbral con el resto de candidaturas constante.
    """
    items = _candidaturas(candidaturas)
    if validos <= 0:
        raise ValueError("validos debe ser positivo")
    if escanos < 1:
        return {"ultimo": None, "siguiente": None, "margen_votos": None}
    asignados, ultimo, elegibles = _reparto_con_traza(items, escanos, validos)
    if ultimo is None:
        return {"ultimo": None, "siguiente": None, "margen_votos": None}

    fuera = [
        (label, votos) for label, votos in elegibles
        if asignados[label] == 0
    ]
    if not fuera:
        return {"ultimo": _json_round(ultimo), "siguiente": None, "margen_votos": None}

    sig_label, sig_votos = max(
        fuera,
        key=lambda x: (Fraction(x[1], asignados[x[0]] + 1), x[1], x[0]),
    )
    margen = _margen_para_escaro(items, escanos, validos, sig_label)
    return {
        "ultimo": _json_round(ultimo),
        "siguiente": {
            "etiqueta": sig_label,
            "votos": sig_votos,
            "escanos": asignados[sig_label],
            "cociente": round(float(Fraction(sig_votos, asignados[sig_label] + 1)), 2),
        },
        "margen_votos": margen,
        "margen_pct": round(100.0 * margen / validos, 3) if margen is not None else None,
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
