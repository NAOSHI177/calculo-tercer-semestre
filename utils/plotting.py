"""Funciones de graficación con Matplotlib."""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from utils.math_helpers import sympy_to_callable


def _to_real_array(values) -> np.ndarray:
    arr = np.asarray(values, dtype=np.complex128)
    real_mask = np.abs(arr.imag) < 1e-10
    out = np.full(arr.shape, np.nan, dtype=float)
    out[real_mask] = arr.real[real_mask]
    return out


def plot_function_with_root(
    expr: sp.Expr,
    symbol: sp.Symbol,
    x_min: float,
    x_max: float,
    root: float | None = None,
    title: str = "",
    highlight_interval: tuple[float, float] | None = None,
):
    """Grafica f(x) y marca la raíz aproximada."""
    fn = sympy_to_callable(expr, symbol)
    x_vals = np.linspace(x_min, x_max, 800)
    y_vals = _to_real_array(fn(x_vals))

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(x_vals, y_vals, label="f(x)", color="#0A66C2")
    ax.axhline(0, color="black", linewidth=1)

    if highlight_interval:
        a, b = highlight_interval
        ax.axvspan(min(a, b), max(a, b), color="#FFD166", alpha=0.25, label="Intervalo final")

    if root is not None:
        root_y = _to_real_array(fn(np.array([root])))[0]
        ax.scatter([root], [root_y], color="#D62828", s=55, zorder=5, label="Raíz aproximada")
        ax.axvline(root, color="#D62828", linestyle="--", linewidth=1)

    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig


def plot_fixed_point_curves(
    g_expr: sp.Expr,
    symbol: sp.Symbol,
    x_min: float,
    x_max: float,
    iterates: Iterable[float] | None = None,
):
    """Grafica y=x y y=g(x) para análisis de punto fijo."""
    g_fn = sympy_to_callable(g_expr, symbol)
    x_vals = np.linspace(x_min, x_max, 800)
    g_vals = _to_real_array(g_fn(x_vals))

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(x_vals, x_vals, label="y = x", color="#1B4332", linewidth=2)
    ax.plot(x_vals, g_vals, label="y = g(x)", color="#9D0208", linewidth=2)

    if iterates:
        it = np.asarray(list(iterates), dtype=float)
        ax.scatter(it, it, color="#F77F00", s=28, label="Iteraciones sobre y=x", zorder=5)

    ax.set_title("Comparación de y=x y y=g(x)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig

