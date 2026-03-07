"""Resolución educativa del Método de la Secante."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import sympy as sp

from utils.math_helpers import evaluate_expr
from utils.plotting import plot_function_with_root
from utils.tables import build_sign_scan_table, find_sign_change_interval, round_numeric_columns

X = sp.symbols("x")

# NOTA IMPORTANTE:
# Si la notación original del ejercicio 4 es distinta, modifica esta cadena.
SECANT_EXERCISE_EXPR_STR = "(2*exp(x) - x**2)**(1/3)"

# Para evitar ambigüedad de rama compleja en potencia 1/3, resolvemos la forma equivalente:
# (2*e^x - x^2)^(1/3)=0  <=>  2*e^x - x^2 = 0
# Si tu docente exige otra interpretación, ajusta esta constante.
SECANT_SOLVER_EXPR_STR = "2*exp(x) - x**2"

F_EXERCISE_EXPR = sp.sympify(SECANT_EXERCISE_EXPR_STR, locals={"x": X, "exp": sp.exp})
F_SOLVER_EXPR = sp.sympify(SECANT_SOLVER_EXPR_STR, locals={"x": X, "exp": sp.exp})
EPS_DEFAULT = 1e-3


def run_secant(
    expr: sp.Expr,
    x0: float,
    x1: float,
    eps: float,
    max_iter: int = 200,
) -> tuple[pd.DataFrame, float | None, str | None]:
    """Ejecuta secante y devuelve tabla de iteraciones."""
    rows: list[dict] = []
    x_prev, x_curr = x0, x1

    for k in range(1, max_iter + 1):
        f_prev = evaluate_expr(expr, X, x_prev)
        f_curr = evaluate_expr(expr, X, x_curr)
        if np.isnan(f_prev) or np.isnan(f_curr):
            return pd.DataFrame(rows), None, "Se obtuvo valor indefinido en f(x)."

        den = f_curr - f_prev
        if abs(den) <= 1e-14:
            return pd.DataFrame(rows), None, "Denominador casi cero en fórmula de secante."

        x_next = x_curr - f_curr * (x_curr - x_prev) / den
        error = abs(x_next - x_curr)
        rows.append(
            {
                "k": k,
                "x_(k-1)": x_prev,
                "x_k": x_curr,
                "f(x_(k-1))": f_prev,
                "f(x_k)": f_curr,
                "x_(k+1)": x_next,
                "error": error,
            }
        )

        x_prev, x_curr = x_curr, x_next
        if error < eps:
            break

    return pd.DataFrame(rows), x_curr, None


def render() -> None:
    st.header("Método de la Secante")
    st.subheader("A. Enunciado completo")
    st.write(
        "Por el método de la secante, calcule la raíz aproximada de "
        r"$(2e^x - x^2)^{1/3}=0$ con $\varepsilon < 10^{-3}$."
    )

    st.subheader("B. Función definida claramente")
    st.latex(r"f(x)=\left(2e^x-x^2\right)^{1/3}")
    st.info(
        "Para el cálculo numérico se usa la ecuación equivalente "
        r"$\phi(x)=2e^x-x^2=0$, que tiene la misma raíz y evita ambigüedad en la potencia 1/3."
    )
    st.latex(r"\phi(x)=2e^x-x^2")

    eps = st.number_input("Tolerancia ε", value=EPS_DEFAULT, min_value=1e-6, format="%.6f")

    st.subheader("C. Exploración previa y elección de x0, x1")
    c1, c2, c3 = st.columns(3)
    explore_start = c1.number_input("Inicio exploración", value=-1.5, step=0.1)
    explore_end = c2.number_input("Fin exploración", value=0.2, step=0.1)
    explore_step = c3.number_input("Paso exploración", value=0.1, min_value=0.05, step=0.05)
    explore_df = build_sign_scan_table(F_SOLVER_EXPR, X, explore_start, explore_end, explore_step)
    st.dataframe(round_numeric_columns(explore_df, 8), use_container_width=True)

    interval = find_sign_change_interval(explore_df)
    if interval:
        st.info(
            f"La tabla muestra cambio de signo cerca de [{interval[0]:.3f}, {interval[1]:.3f}], "
            "útil para elegir los dos valores iniciales."
        )
    else:
        st.warning("No se detectó cambio de signo en la tabla. Puedes ajustar el rango.")

    c4, c5 = st.columns(2)
    x0 = c4.number_input("Valor inicial x0", value=-1.0, step=0.1, format="%.4f")
    x1 = c5.number_input("Valor inicial x1", value=-0.5, step=0.1, format="%.4f")

    st.subheader("D. Fórmula de la secante")
    st.latex(
        r"x_{k+1}=x_k-\frac{f(x_k)\left(x_k-x_{k-1}\right)}{f(x_k)-f(x_{k-1})}"
    )

    st.subheader("E. Tabla iterativa")
    iter_df, root_approx, error_msg = run_secant(F_SOLVER_EXPR, x0, x1, eps)
    if error_msg:
        st.warning(error_msg)
        return
    if iter_df.empty or root_approx is None:
        st.warning("No fue posible obtener aproximación por secante.")
        return

    st.dataframe(round_numeric_columns(iter_df, 10), use_container_width=True)

    st.subheader("F. Criterio de parada")
    st.info(f"Se detiene cuando |x_(k+1)-x_k| < {eps}")

    st.subheader("G. Sustituciones numéricas (primeras iteraciones)")
    for _, row in iter_df.head(3).iterrows():
        k = int(row["k"])
        st.latex(
            rf"x_{{{k+1}}}={row['x_k']:.6f}-\frac{{{row['f(x_k)']:.6f}({row['x_k']:.6f}-"
            rf"{row['x_(k-1)']:.6f})}}{{{row['f(x_k)']:.6f}-{row['f(x_(k-1))']:.6f}}}"
            rf"={row['x_(k+1)']:.6f}"
        )

    st.success(f"Raíz aproximada por secante: x ≈ {root_approx:.10f}")

    st.subheader("H. Gráfico de la función y raíz aproximada")
    x_min = min(explore_start, root_approx - 1.0)
    x_max = max(explore_end, root_approx + 1.0)
    fig = plot_function_with_root(
        F_SOLVER_EXPR,
        X,
        x_min,
        x_max,
        root=root_approx,
        title="Secante sobre φ(x)=2e^x-x^2",
    )
    st.pyplot(fig)

    with st.expander("Configuración editable del ejercicio 4"):
        st.code(
            "SECANT_EXERCISE_EXPR_STR = '(2*exp(x) - x**2)**(1/3)'\n"
            "SECANT_SOLVER_EXPR_STR = '2*exp(x) - x**2'",
            language="python",
        )
        st.write(
            "Si el enunciado original usa otra notación, modifica esas constantes al inicio "
            "del archivo `methods/secante.py`."
        )

