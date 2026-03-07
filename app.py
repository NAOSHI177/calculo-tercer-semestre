"""Aplicación principal de Métodos Numéricos en Streamlit."""

from __future__ import annotations

import streamlit as st

from methods.biseccion import render as render_biseccion
from methods.falsa_posicion import render as render_falsa_posicion
from methods.newton_raphson import render as render_newton_raphson
from methods.secante import render as render_secante
from methods.iterativo_lineal import render as render_iterativo_lineal


st.set_page_config(
    page_title="Métodos Numéricos – Resolución Paso a Paso",
    page_icon="📘",
    layout="wide",
)

st.title("Métodos Numéricos – Resolución Paso a Paso")
st.markdown(
    "Selecciona un ejercicio en el menú lateral para ver el proceso completo y educativo."
)

EXERCISES = {
    "1 - Hallar un intervalo que contiene la raíz de x^3 - 7x^2 + 14x - 6 = 0, en el intervalo de la fase 1 y 2 y calcular la raíz aproximada dentro de dicho intervalo, con ε < 10^-2. (Método de la Bisección)": render_biseccion,
    "2 - Utiliza el método de la falsa posición para calcular la raíz aproximada de la función y = e^(-x^2) - ln(x). Expresa el resultado en ACF con 3 cifras significativas. Obs.: ε < 10^-2. (Método de la Falsa Posición)": render_falsa_posicion,
    "3 - Aplique el método de Newton para obtener soluciones con exactitud de ε < 10^-4 de:\n"
    "e^x + 2^(-x) + 2 cos(x) - 6 = 0\n"
    "(Método de Newton-Raphson)": render_newton_raphson,
    "4 - Por el método de la secante calcule la raíz aproximada de la ecuación:\n"
    "(2e^x - x^2)^(1/3) = 0\n"
    "con ε < 10^-3.\n"
    "(Método de la Secante)": render_secante,
    "5 - Encuentra las soluciones reales positivas de la siguiente ecuación, por el método iterativo lineal realizando 6 iteraciones:\n"
    "f(x) = 4 cos(x) - e^(2x)\n"
    "(Método Iterativo Lineal)": render_iterativo_lineal,
}

st.sidebar.header("Menú principal")
selected_exercise = st.sidebar.radio("Elige un ejercicio:", list(EXERCISES.keys()))
st.sidebar.info("La app muestra proceso, fórmulas, tablas iterativas y gráficos.")

render_fn = EXERCISES[selected_exercise]
render_fn()
