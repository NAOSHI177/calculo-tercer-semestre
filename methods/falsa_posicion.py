"""Resolución educativa del Método de la Falsa Posición."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import sympy as sp

from utils.math_helpers import evaluate_expr
from utils.plotting import plot_function_with_root
from utils.tables import build_sign_scan_table, find_sign_change_interval, round_numeric_columns

X = sp.symbols("x")
F_EXPR = sp.exp(-X**2) - sp.log(X)
EPS_DEFAULT = 1e-2


def domain_positive(x_value: float) -> bool:
    """Dominio de ln(x): x > 0."""
    return x_value > 0


def run_false_position(
    expr: sp.Expr,
    a0: float,
    b0: float,
    eps: float,
    max_iter: int = 200,
) -> tuple[pd.DataFrame, float | None, tuple[float, float] | None, str | None]:
    """Ejecuta falsa posición con tabla iterativa completa."""
    fa = evaluate_expr(expr, X, a0)
    fb = evaluate_expr(expr, X, b0)
    if np.isnan(fa) or np.isnan(fb):
        return pd.DataFrame(), None, None, "No se pudo evaluar en los extremos del intervalo."
    if fa * fb > 0:
        return pd.DataFrame(), None, None, "No hay cambio de signo en el intervalo inicial."

    rows: list[dict] = []
    xr_prev: float | None = None
    a, b = a0, b0

    for k in range(1, max_iter + 1):
        a_k, b_k = a, b
        fa = evaluate_expr(expr, X, a_k)
        fb = evaluate_expr(expr, X, b_k)
        den = fb - fa
        if abs(den) <= 1e-14:
            return pd.DataFrame(rows), None, (a, b), "Denominador casi cero en fórmula de falsa posición."

        xr = (a_k * fb - b_k * fa) / den
        fxr = evaluate_expr(expr, X, xr)
        err = np.nan if xr_prev is None else abs(xr - xr_prev)

        if np.isnan(fxr):
            return pd.DataFrame(rows), None, (a, b), "f(x_r) resultó indefinida."

        if fa * fxr < 0:
            decision = "Se reemplaza b_k por x_r (intervalo [a_k, x_r])"
            next_a, next_b = a_k, xr
        elif fa * fxr > 0:
            decision = "Se reemplaza a_k por x_r (intervalo [x_r, b_k])"
            next_a, next_b = xr, b_k
        else:
            decision = "Raíz exacta en x_r"
            rows.append(
                {
                    "k": k,
                    "a_k": a_k,
                    "b_k": b_k,
                    "f(a_k)": fa,
                    "f(b_k)": fb,
                    "x_r": xr,
                    "f(x_r)": fxr,
                    "error": err,
                    "Actualización": decision,
                }
            )
            return pd.DataFrame(rows), xr, (xr, xr), None

        rows.append(
            {
                "k": k,
                "a_k": a_k,
                "b_k": b_k,
                "f(a_k)": fa,
                "f(b_k)": fb,
                "x_r": xr,
                "f(x_r)": fxr,
                "error": err,
                "Actualización": decision,
            }
        )

        xr_prev = xr
        a, b = next_a, next_b
        if not np.isnan(err) and err < eps:
            break

    return pd.DataFrame(rows), xr_prev, (a, b), None


def render() -> None:
    st.header("Método de la Falsa Posición")
    st.subheader("A. Enunciado completo")
    st.write(
        "Utiliza el método de la falsa posición para calcular la raíz aproximada de "
        r"$y=e^{-x^2}-\ln(x)$ con $\varepsilon<10^{-2}$ y expresar el resultado en ACF "
        "(3 cifras significativas)."
    )

    st.subheader("B. Función")
    st.latex(r"f(x)=e^{-x^2}-\ln(x)")

    st.subheader("C. Validación de dominio")
    st.warning("Dominio: x > 0, porque ln(x) solo está definida para x positivos.")

    eps = st.number_input("Tolerancia ε", min_value=1e-6, value=EPS_DEFAULT, format="%.6f")

    st.subheader("D. Búsqueda de intervalo inicial")
    c1, c2, c3 = st.columns(3)
    start = c1.number_input("Inicio de exploración", value=0.2, min_value=0.01, step=0.1)
    end = c2.number_input("Fin de exploración", value=3.0, min_value=0.1, step=0.1)
    step = c3.number_input("Paso de exploración", value=0.2, min_value=0.01, step=0.01)

    scan_df = build_sign_scan_table(F_EXPR, X, start, end, step, domain_fn=domain_positive)
    st.dataframe(round_numeric_columns(scan_df, 8), use_container_width=True)
    interval = find_sign_change_interval(scan_df)

    if interval is None:
        st.warning("No se encontró cambio de signo en el rango dado. Ajusta la exploración.")
        return

    if interval[0] == interval[1]:
        st.success(f"Se encontró raíz exacta en la exploración: x = {interval[0]:.8f}")
        return

    st.success(f"Intervalo con cambio de signo: [{interval[0]:.6f}, {interval[1]:.6f}]")

    st.subheader("E. Fórmula de falsa posición")
    st.latex(r"x_r=\frac{a_k f(b_k)-b_k f(a_k)}{f(b_k)-f(a_k)}")

    st.subheader("F. Tabla iterativa completa")
    iter_df, root_approx, final_interval, error_msg = run_false_position(F_EXPR, interval[0], interval[1], eps)
    if error_msg:
        st.warning(error_msg)
        return
    if iter_df.empty or root_approx is None:
        st.warning("No se pudo completar el método de falsa posición.")
        return

    st.dataframe(round_numeric_columns(iter_df, 8), use_container_width=True)
    st.info(f"Criterio de parada: error = |x_r^(k) - x_r^(k-1)| < {eps}")

    st.subheader("G. Reemplazo de intervalo por signos")
    for _, row in iter_df.head(4).iterrows():
        st.latex(
            rf"x_r=\frac{{({row['a_k']:.6f})({row['f(b_k)']:.6f})-({row['b_k']:.6f})({row['f(a_k)']:.6f})}}"
            rf"{{{row['f(b_k)']:.6f}-({row['f(a_k)']:.6f})}}={row['x_r']:.6f}"
        )
        st.write(row["Actualización"])

    st.subheader("H. Resultado final")
    root_3_sig = f"{root_approx:.3g}"
    st.success(
        f"Raíz aproximada: x ≈ {root_approx:.8f}. "
        f"Con 3 cifras significativas: {root_3_sig}"
    )

    st.subheader("I. Nota sobre ACF")
    st.info(
        "ACF puede variar según el curso (cifras fijas o cifras significativas). "
        "Aquí se aplica el redondeo a 3 cifras significativas como pediste."
    )

    st.subheader("J. Gráfico de la función y raíz aproximada")
    plot_left = max(0.01, min(interval[0], interval[1]) - 0.6)
    plot_right = max(interval[0], interval[1]) + 0.8
    fig = plot_function_with_root(
        F_EXPR,
        X,
        plot_left,
        plot_right,
        root=root_approx,
        title="Falsa posición: f(x)=e^{-x^2}-ln(x)",
        highlight_interval=final_interval,
    )
    st.pyplot(fig)
