"""Resolución educativa del Método de la Bisección."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import sympy as sp

from utils.math_helpers import evaluate_expr
from utils.plotting import plot_function_with_root
from utils.tables import build_sign_scan_table, find_sign_change_interval, round_numeric_columns

X = sp.symbols("x")
F_EXPR = X**3 - 7 * X**2 + 14 * X - 6
EPS_DEFAULT = 1e-2


def run_bisection(
    expr: sp.Expr,
    a0: float,
    b0: float,
    eps: float,
    max_iter: int = 200,
) -> tuple[pd.DataFrame, float | None, tuple[float, float] | None, str | None]:
    """Ejecuta bisección y devuelve tabla, raíz aproximada e intervalo final."""
    fa0 = evaluate_expr(expr, X, a0)
    fb0 = evaluate_expr(expr, X, b0)
    if np.isnan(fa0) or np.isnan(fb0):
        return pd.DataFrame(), None, None, "No se pudo evaluar f(x) en los extremos."
    if fa0 * fb0 > 0:
        return pd.DataFrame(), None, None, "El intervalo inicial no presenta cambio de signo."

    rows: list[dict] = []
    a, b = a0, b0
    fa, fb = fa0, fb0

    for k in range(1, max_iter + 1):
        a_k, b_k = a, b
        x_k = (a_k + b_k) / 2.0
        f_xk = evaluate_expr(expr, X, x_k)
        width = abs(b_k - a_k)

        if np.isnan(f_xk):
            return pd.DataFrame(rows), None, (a, b), "f(x_k) resultó indefinida."

        if abs(f_xk) <= 1e-14:
            decision = "Raíz exacta en x_k"
            new_interval = (x_k, x_k)
            rows.append(
                {
                    "k": k,
                    "a_k": a_k,
                    "b_k": b_k,
                    "x_k": x_k,
                    "f(x_k)": f_xk,
                    "|b_k-a_k|": width,
                    "Actualización": decision,
                }
            )
            return pd.DataFrame(rows), x_k, new_interval, None

        if fa * f_xk < 0:
            decision = "Se conserva [a_k, x_k]"
            b = x_k
            fb = f_xk
        else:
            decision = "Se conserva [x_k, b_k]"
            a = x_k
            fa = f_xk

        new_interval = (a, b)
        rows.append(
            {
                "k": k,
                "a_k": a_k,
                "b_k": b_k,
                "x_k": x_k,
                "f(x_k)": f_xk,
                "|b_k-a_k|": width,
                "Actualización": decision,
            }
        )

        if abs(b - a) < eps:
            break

    approx = (a + b) / 2.0
    return pd.DataFrame(rows), approx, new_interval, None


def render() -> None:
    st.header("Método de la Bisección")
    st.subheader("A. Enunciado completo")
    st.write(
        "Hallar un intervalo que contiene la raíz de "
        r"$x^3 - 7x^2 + 14x - 6 = 0$, en fase 1 y fase 2, y calcular la raíz "
        r"aproximada con $\varepsilon < 10^{-2}$."
    )

    st.subheader("B. Función definida")
    st.latex(r"f(x)=x^3-7x^2+14x-6")
    st.info("Usaremos el criterio de parada: |b_k-a_k| < ε")

    eps = st.number_input("Tolerancia ε", min_value=1e-6, value=EPS_DEFAULT, format="%.6f")

    st.subheader("C. Fase 1: búsqueda inicial de intervalo")
    c1, c2, c3 = st.columns(3)
    phase1_start = c1.number_input("Inicio fase 1", value=0.0, step=1.0)
    phase1_end = c2.number_input("Fin fase 1", value=5.0, step=1.0)
    phase1_step = c3.number_input("Paso fase 1", min_value=0.1, value=1.0, step=0.1)

    phase1_df = build_sign_scan_table(F_EXPR, X, phase1_start, phase1_end, phase1_step)
    st.dataframe(round_numeric_columns(phase1_df, 6), use_container_width=True)
    interval_1 = find_sign_change_interval(phase1_df)

    if interval_1 is None:
        st.warning("No se detectó cambio de signo en fase 1. Ajusta el rango de exploración.")
        return

    if interval_1[0] == interval_1[1]:
        root = interval_1[0]
        st.success(f"Se detectó raíz exacta en fase 1: x = {root:.6f}")
        fig = plot_function_with_root(
            F_EXPR,
            X,
            root - 2,
            root + 2,
            root=root,
            title="f(x) y raíz exacta encontrada en fase 1",
            highlight_interval=(root, root),
        )
        st.pyplot(fig)
        return

    st.success(f"Intervalo encontrado en fase 1: [{interval_1[0]:.6f}, {interval_1[1]:.6f}]")

    st.subheader("D. Fase 2: refinamiento del intervalo")
    phase2_step = st.number_input(
        "Paso fase 2 (más fino)",
        min_value=0.01,
        value=0.1,
        step=0.01,
        format="%.2f",
    )

    phase2_df = build_sign_scan_table(F_EXPR, X, interval_1[0], interval_1[1], phase2_step)
    st.dataframe(round_numeric_columns(phase2_df, 6), use_container_width=True)
    interval_2 = find_sign_change_interval(phase2_df)

    if interval_2 is None:
        st.warning(
            "No se detectó cambio de signo en fase 2 con el paso elegido. "
            "Se usará el intervalo de fase 1."
        )
        interval_2 = interval_1

    st.success(f"Intervalo refinado: [{interval_2[0]:.6f}, {interval_2[1]:.6f}]")

    st.subheader("E. Cálculo por bisección")
    st.latex(r"x_k=\frac{a_k+b_k}{2}")
    iter_df, root_approx, final_interval, error_msg = run_bisection(F_EXPR, interval_2[0], interval_2[1], eps)

    if error_msg:
        st.warning(error_msg)
        return

    st.dataframe(round_numeric_columns(iter_df, 8), use_container_width=True)

    st.markdown("**Sustitución numérica (primeras iteraciones):**")
    for _, row in iter_df.head(3).iterrows():
        st.latex(
            rf"x_{{{int(row['k'])}}}=\frac{{{row['a_k']:.6f}+{row['b_k']:.6f}}}{{2}}={row['x_k']:.6f}"
        )
        st.write(f"Decisión: {row['Actualización']}")

    st.info(f"Criterio usado: |b_k-a_k| < {eps}")
    if root_approx is None or final_interval is None:
        st.warning("No se pudo completar el proceso de bisección.")
        return

    st.success(
        f"Raíz aproximada por bisección: x ≈ {root_approx:.8f} "
        f"(intervalo final [{final_interval[0]:.8f}, {final_interval[1]:.8f}])"
    )

    st.subheader("F. Gráfico de la función y raíz aproximada")
    span_left = min(final_interval[0], final_interval[1]) - 1.0
    span_right = max(final_interval[0], final_interval[1]) + 1.0
    fig = plot_function_with_root(
        F_EXPR,
        X,
        span_left,
        span_right,
        root=root_approx,
        title="Bisección: f(x) y raíz aproximada",
        highlight_interval=final_interval,
    )
    st.pyplot(fig)

