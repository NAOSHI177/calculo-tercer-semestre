"""Funciones matemáticas auxiliares."""

from __future__ import annotations

from typing import Callable

import numpy as np
import sympy as sp


def sympy_to_callable(expr: sp.Expr, symbol: sp.Symbol) -> Callable:
    """Convierte una expresión de SymPy a función evaluable con NumPy."""
    raw_callable = sp.lambdify(symbol, expr, modules=["numpy"])

    def wrapped(x):
        try:
            return raw_callable(x)
        except Exception:
            if np.isscalar(x):
                return np.nan
            x_arr = np.asarray(x, dtype=float)
            return np.full_like(x_arr, np.nan, dtype=float)

    return wrapped


def evaluate_expr(expr: sp.Expr, symbol: sp.Symbol, x_value: float) -> float:
    """Evalúa una expresión en un punto numérico y devuelve float."""
    fn = sympy_to_callable(expr, symbol)
    value = fn(x_value)
    try:
        complex_value = complex(value)
        if abs(complex_value.imag) > 1e-10:
            return float("nan")
        return float(complex_value.real)
    except Exception:
        return float("nan")


def sign_text(value: float, tol: float = 1e-12) -> str:
    """Etiqueta de signo para mostrar en tablas."""
    if np.isnan(value):
        return "indefinido"
    if abs(value) <= tol:
        return "0"
    return "+" if value > 0 else "-"


def generate_range(start: float, end: float, step: float) -> np.ndarray:
    """Genera rango inclusivo [start, end] con paso fijo."""
    if step <= 0:
        raise ValueError("El paso debe ser positivo.")
    if end < start:
        return np.array([], dtype=float)

    count = int(np.floor((end - start) / step)) + 1
    values = start + np.arange(count + 1, dtype=float) * step
    clipped = values[values <= end + 1e-12]
    return np.round(clipped, 12)

