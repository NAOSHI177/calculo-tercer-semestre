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

## Instalación y ejecución con entorno virtual (venv)

Estas instrucciones están pensadas para PowerShell, desde la carpeta del proyecto `calculo-tercer-semestre`.

1. Crear el entorno virtual:

```powershell
python -m venv .venv
```

2. Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Actualizar `pip` e instalar dependencias:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Ejecutar la aplicación:

```powershell
streamlit run app.py
```

5. Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

6. Salir del entorno virtual:

```powershell
deactivate
```

### Linux (bash)

Desde la raíz del proyecto:

1. Crear el entorno virtual:

```bash
python3 -m venv .venv
```

2. Activar el entorno virtual:

```bash
source .venv/bin/activate
```

3. Actualizar `pip` e instalar dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Ejecutar la aplicación:

```bash
streamlit run app.py
```

5. Salir del entorno virtual:

```bash
deactivate
```

## Notas importantes

- **Ejercicio 4 (Secante):** en `methods/secante.py` se incluyen constantes editables al inicio:
  - `SECANT_EXERCISE_EXPR_STR`
  - `SECANT_SOLVER_EXPR_STR`

  Esto permite ajustar fácilmente la interpretación si el enunciado original tiene ambigüedad en la notación.

- **ACF en falsa posición:** se incluye una nota aclarando que puede variar por convención; en esta app se aplica redondeo a 3 cifras significativas.
