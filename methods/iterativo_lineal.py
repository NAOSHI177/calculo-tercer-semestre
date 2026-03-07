"""Resolución educativa del método iterativo lineal (punto fijo)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import sympy as sp

from utils.math_helpers import evaluate_expr
from utils.plotting import plot_fixed_point_curves, plot_function_with_root
from utils.tables import round_numeric_columns

X = sp.symbols("x")
F_EXPR = 4 * sp.cos(X) - sp.exp(2 * X)
G_EXPR = sp.log(4 * sp.cos(X)) / 2
G_DERIV_EXPR = sp.diff(G_EXPR, X)
ITERATIONS = 6


def domain_g(x_value: float) -> bool:
    """Dominio de g(x)=0.5*ln(4cos(x)): requiere 4cos(x) > 0."""
    return 4 * np.cos(x_value) > 0


def run_fixed_point(
    g_expr: sp.Expr,
    x0: float,
    iterations: int,
) -> tuple[pd.DataFrame, float | None, str | None]:
    """Ejecuta iteraciones de punto fijo con cantidad exacta de pasos."""
    rows: list[dict] = []
    x_k = x0

    for k in range(iterations):
        if not domain_g(x_k):
            return pd.DataFrame(rows), None, (
                "x_k salió del dominio de g(x). Revisa el valor inicial."
            )

        gx_k = evaluate_expr(g_expr, X, x_k)
        if np.isnan(gx_k):
            return pd.DataFrame(rows), None, "Se obtuvo valor indefinido al evaluar g(x_k)."

        error = abs(gx_k - x_k)
        rows.append(
            {
                "k": k,
                "x_k": x_k,
                "g(x_k)": gx_k,
                "error": error,
            }
        )
        x_k = gx_k

    return pd.DataFrame(rows), x_k, None


def render() -> None:
    st.header("Método Iterativo Lineal (Punto Fijo)")
    st.subheader("A. Enunciado completo")
    st.write(
        "Encuentra las soluciones reales positivas de "
        r"$f(x)=4\cos(x)-e^{2x}$ por método iterativo lineal, "
        f"realizando exactamente {ITERATIONS} iteraciones."
    )

    st.subheader("B. Función original")
    st.latex(r"f(x)=4\cos(x)-e^{2x}")

    st.subheader("C. Reescritura en forma iterativa")
    st.write(
        "De la ecuación $4\\cos(x)=e^{2x}$ se obtiene la forma de punto fijo:"
    )
    st.latex(r"x=g(x)=\frac{1}{2}\ln\!\left(4\cos(x)\right)")
    st.write(
        "Se elige esta forma porque conserva la solución positiva y permite verificar "
        "convergencia con la derivada de g."
    )

    st.subheader("D. Función iterativa y derivada")
    st.latex(r"g(x)=\frac{1}{2}\ln(4\cos(x))")
    st.latex(r"g'(x)=" + sp.latex(G_DERIV_EXPR))
    st.info("Condición local típica de convergencia: |g'(x*)| < 1 cerca de la raíz.")

    st.subheader("E. Valor inicial")
    x0 = st.number_input(
        "Valor inicial x0 (positivo y en dominio de g)",
        value=0.5,
        min_value=0.0,
        max_value=1.4,
        step=0.05,
        format="%.4f",
    )

    gp_x0 = evaluate_expr(G_DERIV_EXPR, X, x0)
    if np.isnan(gp_x0):
        st.warning("No se pudo evaluar g'(x0). Revisa x0.")
    else:
        st.write(f"|g'(x0)| = {abs(gp_x0):.6f}")

    st.subheader(f"F. {ITERATIONS} iteraciones (se ejecutan siempre)")
    iter_df, final_value, error_msg = run_fixed_point(G_EXPR, x0, ITERATIONS)
    if error_msg:
        st.warning(error_msg)
        return
    if iter_df.empty or final_value is None:
        st.warning("No fue posible completar las iteraciones.")
        return

    st.subheader("G. Tabla iterativa")
    st.dataframe(round_numeric_columns(iter_df, 10), use_container_width=True)

    st.subheader("H. Valor final después de 6 iteraciones")
    st.success(f"x_{ITERATIONS} ≈ {final_value:.10f}")

    st.subheader("I. Comentario de convergencia")
    errors = iter_df["error"].to_numpy(dtype=float)
    decreasing = np.all(np.diff(errors) <= 1e-12) if len(errors) > 1 else True
    gp_final = evaluate_expr(G_DERIV_EXPR, X, final_value)
    if not np.isnan(gp_final) and abs(gp_final) < 1 and decreasing:
        st.success(
            "Los errores decrecen y |g'(x)|<1 cerca del valor final: la iteración parece convergente."
        )
    else:
        st.warning(
            "La convergencia no es totalmente clara con este x0 (o |g'(x)| no es menor que 1). "
            "Prueba otro valor inicial."
        )

    st.subheader("J. Gráficos")
    iter_points = [x0] + iter_df["g(x_k)"].tolist()
    x_min = max(0.0, min(iter_points) - 0.2)
    x_max = max(iter_points) + 0.2

    fig_fp = plot_fixed_point_curves(G_EXPR, X, x_min, x_max, iterates=iter_points)
    st.pyplot(fig_fp)

    fig_f = plot_function_with_root(
        F_EXPR,
        X,
        0.0,
        max(1.0, x_max + 0.2),
        root=final_value,
        title="Función original f(x)=4cos(x)-e^{2x}",
    )
    st.pyplot(fig_f)

