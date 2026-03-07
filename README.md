# Métodos Numéricos – Resolución Paso a Paso

Aplicación web educativa desarrollada con **Python + Streamlit** para resolver ejercicios de métodos numéricos mostrando todo el proceso, no solo el resultado.

## Características

- Interfaz en español.
- Menú principal en `sidebar` con 5 ejercicios.
- Desarrollo paso a paso por método:
  - función original
  - validaciones de dominio
  - fases de búsqueda de intervalo
  - derivadas simbólicas (cuando aplica)
  - fórmulas matemáticas con `st.latex`
  - sustituciones numéricas
  - tablas iterativas completas
  - criterio de parada y error
  - resultado final destacado
  - gráficos con raíz aproximada marcada
- Código modular y reutilizable para uso académico.

## Estructura del proyecto

```text
calculo-tercer-semestre/
├── app.py
├── methods/
│   ├── __init__.py
│   ├── biseccion.py
│   ├── falsa_posicion.py
│   ├── newton_raphson.py
│   ├── secante.py
│   └── iterativo_lineal.py
├── utils/
│   ├── __init__.py
│   ├── math_helpers.py
│   ├── plotting.py
│   └── tables.py
├── requirements.txt
└── README.md
```

## Instalación

1. Crear y activar entorno virtual (opcional pero recomendado).
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Desde la raíz del proyecto:

```bash
streamlit run app.py
```

## Notas importantes

- **Ejercicio 4 (Secante):** en `methods/secante.py` se incluyen constantes editables al inicio:
  - `SECANT_EXERCISE_EXPR_STR`
  - `SECANT_SOLVER_EXPR_STR`

  Esto permite ajustar fácilmente la interpretación si el enunciado original tiene ambigüedad en la notación.

- **ACF en falsa posición:** se incluye una nota aclarando que puede variar por convención; en esta app se aplica redondeo a 3 cifras significativas.

