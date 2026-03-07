"""Utilidades para construir y formatear tablas con pandas."""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd
import sympy as sp

from utils.math_helpers import evaluate_expr, generate_range, sign_text


def build_sign_scan_table(
    expr: sp.Expr,
    symbol: sp.Symbol,
    start: float,
    end: float,
    step: float,
    domain_fn: Callable[[float], bool] | None = None,
) -> pd.DataFrame:
    """Construye tabla x, f(x), signo para exploración de intervalos."""
    rows = []
    x_values = generate_range(start, end, step)

    for x_val in x_values:
        x_float = float(x_val)
        if domain_fn and not domain_fn(x_float):
            rows.append({"x": x_float, "f(x)": np.nan, "signo": "fuera de dominio"})
            continue

        fx = evaluate_expr(expr, symbol, x_float)
        rows.append({"x": x_float, "f(x)": fx, "signo": sign_text(fx)})

    return pd.DataFrame(rows)


def find_sign_change_interval(
    df: pd.DataFrame,
    x_col: str = "x",
    f_col: str = "f(x)",
    tol: float = 1e-12,
) -> tuple[float, float] | None:
    """Busca el primer intervalo con cambio de signo o raíz exacta."""
    valid = df[[x_col, f_col]].dropna().reset_index(drop=True)
    if valid.empty:
        return None

    for i in range(len(valid) - 1):
        x1 = float(valid.loc[i, x_col])
        x2 = float(valid.loc[i + 1, x_col])
        f1 = float(valid.loc[i, f_col])
        f2 = float(valid.loc[i + 1, f_col])

        if abs(f1) <= tol:
            return (x1, x1)
        if abs(f2) <= tol:
            return (x2, x2)
        if f1 * f2 < 0:
            return (x1, x2)

    return None


def round_numeric_columns(df: pd.DataFrame, decimals: int = 8) -> pd.DataFrame:
    """Redondea solo columnas numéricas para una visualización limpia."""
    out = df.copy()
    num_cols = out.select_dtypes(include=[np.number]).columns
    out[num_cols] = out[num_cols].round(decimals)
    return out

