"""Resolución educativa del método de Newton-Raphson."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import sympy as sp

from utils.math_helpers import evaluate_expr
from utils.plotting import plot_function_with_root
from utils.tables import build_sign_scan_table, find_sign_change_interval, round_numeric_columns

X = sp.symbols("x")
F_EXPR = sp.exp(X) + 2 ** (-X) + 2 * sp.cos(X) - 6
F_DERIV_EXPR = sp.diff(F_EXPR, X)
EPS_DEFAULT = 1e-4


def run_newton(
    expr: sp.Expr,
    d_expr: sp.Expr,
    x0: float,
    eps: float,
    max_iter: int = 100,
) -> tuple[pd.DataFrame, float | None, str | None]:
    """Ejecuta Newton-Raphson y devuelve tabla, raíz y error opcional."""
    rows: list[dict] = []
    x_k = x0

    for k in range(max_iter):
        f_xk = evaluate_expr(expr, X, x_k)
        fp_xk = evaluate_expr(d_expr, X, x_k)
        if np.isnan(f_xk) or np.isnan(fp_xk):
            return pd.DataFrame(rows), None, "Apareció un valor indefinido durante las iteraciones."
        if abs(fp_xk) <= 1e-14:
            return pd.DataFrame(rows), None, "f'(x_k) es casi cero; Newton no puede continuar."

        x_next = x_k - f_xk / fp_xk
        error = abs(x_next - x_k)
        rows.append(
            {
                "k": k,
                "x_k": x_k,
                "f(x_k)": f_xk,
                "f'(x_k)": fp_xk,
                "x_(k+1)": x_next,
                "error": error,
            }
        )
        x_k = x_next

        if error < eps:
            break

    return pd.DataFrame(rows), x_k, None


def render() -> None:
    st.header("Método de Newton-Raphson")
    st.subheader("A. Enunciado completo")
    st.write(
        "Aplique el método de Newton para obtener soluciones con exactitud "
        r"$\varepsilon < 10^{-4}$ de la ecuación "
        r"$e^x + 2^{-x} + 2\cos(x) - 6 = 0$."
    )

    st.subheader("B. Función")
    st.latex(r"f(x)=e^x+2^{-x}+2\cos(x)-6")

    st.subheader("C. Derivada simbólica con SymPy")
    st.latex(r"f'(x)=" + sp.latex(F_DERIV_EXPR))

    st.subheader("D. Exploración previa y elección de x0")
    c1, c2, c3 = st.columns(3)
    explore_start = c1.number_input("Inicio exploración", value=0.0, step=0.1)
    explore_end = c2.number_input("Fin exploración", value=2.2, step=0.1)
    explore_step = c3.number_input("Paso exploración", value=0.2, min_value=0.05, step=0.05)
    explore_df = build_sign_scan_table(F_EXPR, X, explore_start, explore_end, explore_step)
    st.dataframe(round_numeric_columns(explore_df, 8), use_container_width=True)

    interval = find_sign_change_interval(explore_df)
    if interval:
        st.info(
            f"Se detecta cambio de signo cerca del intervalo [{interval[0]:.3f}, {interval[1]:.3f}], "
            "lo que ayuda a elegir un x0 razonable."
        )
    else:
        st.warning("No se detectó cambio de signo en la tabla de exploración; ajusta el rango si deseas.")

    x0 = st.number_input("Valor inicial x0", value=1.8, step=0.1, format="%.4f")
    eps = st.number_input("Tolerancia ε", value=EPS_DEFAULT, min_value=1e-7, format="%.6f")

    st.subheader("E. Fórmula de Newton")
    st.latex(r"x_{k+1}=x_k-\frac{f(x_k)}{f'(x_k)}")

    st.subheader("F. Tabla iterativa")
    iter_df, root_approx, error_msg = run_newton(F_EXPR, F_DERIV_EXPR, x0, eps)
    if error_msg:
        st.warning(error_msg)
        return
    if iter_df.empty or root_approx is None:
        st.warning("No se pudo obtener una aproximación con Newton.")
        return

    st.dataframe(round_numeric_columns(iter_df, 10), use_container_width=True)

    st.subheader("G. Criterio de parada")
    st.info(f"Se detiene cuando |x_(k+1) - x_k| < {eps}")

    st.subheader("H. Sustituciones numéricas (primeras iteraciones)")
    for _, row in iter_df.head(3).iterrows():
        k = int(row["k"])
        x_k = float(row["x_k"])
        f_k = float(row["f(x_k)"])
        fp_k = float(row["f'(x_k)"])
        x_next = float(row["x_(k+1)"])
        st.latex(
            rf"x_{{{k+1}}}=x_{{{k}}}-\frac{{f(x_{{{k}}})}}{{f'(x_{{{k}}})}}="
            rf"{x_k:.6f}-\frac{{{f_k:.6f}}}{{{fp_k:.6f}}}={x_next:.6f}"
        )

    st.subheader("I. Resultado final")
    st.success(f"Raíz aproximada con Newton-Raphson: x ≈ {root_approx:.10f}")
    st.info(
        "Si eliges otro x0, Newton puede converger a otra raíz (si existe) "
        "o incluso divergir según la forma de f(x)."
    )

    st.subheader("J. Gráfico de f(x) y raíz aproximada")
    x_min = min(explore_start, root_approx - 1.2)
    x_max = max(explore_end, root_approx + 1.2)
    fig = plot_function_with_root(
        F_EXPR,
        X,
        x_min,
        x_max,
        root=root_approx,
        title="Newton-Raphson: f(x) y aproximación",
    )
    st.pyplot(fig)
