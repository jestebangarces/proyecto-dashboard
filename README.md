# Intentos de suicidio notificados en Tunja (2020–2024)

**De los datos a la historia** · Proyecto integrador de primer semestre
Ingeniería de Datos e Inteligencia Artificial
Asignaturas: *Introducción a la Ingeniería de Datos e IA* y *Lógica Computacional*

**App desplegada:** https://intentos-suicidio-tunja.streamlit.app/

> **Tema sensible.** Los datos no contienen nombres ni documentos de identidad y se analizan
> solo de forma agregada. Si tú o alguien cercano necesita apoyo en Colombia: **Línea 192, opción 4**
> o **Línea 106**.

## Pregunta guía

> ¿Quiénes son las personas con intentos de suicidio notificados en Tunja entre 2020 y 2024,
> qué situaciones las rodean y cómo ha cambiado la cantidad de casos?

## Hallazgos principales

- El **65 %** de los casos son mujeres; la edad mediana es **21 años** y el **76 %** tiene entre 12 y 28 años.
- Los factores más registrados son **problemas familiares (43 %)** y **conflicto con la pareja (35 %)**.
- El **51 %** ya había tenido un intento previo y el **40 %** presentaba ideación suicida persistente.
- Entre 2020 y 2022 (años completos) los casos notificados aumentaron **79 %** (de 125 a 224).
- El 87 % fue remitido a psicología y el 91 % a psiquiatría.

## Dataset

| | |
|---|---|
| Fuente | Fichas de notificación del evento *intento de suicidio* (vigilancia en salud pública, Tunja). `COMPLETAR: entidad y enlace exacto de descarga` |
| Archivo | [`data/Tunja_intentos_datos_limpios.csv`](data/Tunja_intentos_datos_limpios.csv) |
| Tamaño | **818 registros** × **49 variables** (cumple R1: ≥100 registros y ≥5 variables) |
| Periodo | 02/01/2020 – 28/03/2024 |
| Variables | Fechas, edad, sexo, escolaridad, estrato, barrio, factores desencadenantes, antecedentes, mecanismo y remisiones (SI/NO) |
| Calidad | 17 % de vacíos en `NUMERO_INTENTOS`; 22 registros con fecha del hecho posterior a la notificación; 2023 sin datos de julio a septiembre y 2024 solo hasta marzo. Ver [`salidas/reporte_calidad.json`](salidas/reporte_calidad.json). |

## Estructura del repositorio

```
├── app.py                      # Dashboard en Streamlit (interfaz)
├── reporte.py                  # Genera los reportes JSON de calidad y estadística
├── src/
│   ├── datos.py                # Carga, validación, colecciones, lectura/escritura CSV y JSON
│   └── estadisticas.py         # Estadística descriptiva con NumPy
├── data/
│   └── Tunja_intentos_datos_limpios.csv
├── notebooks/
│   └── 01_exploracion_EDA.ipynb    # EDA en Google Colab (head, info, describe, NumPy, gráficos)
├── salidas/                    # JSON generados por reporte.py
├── .streamlit/config.toml      # Tema visual
└── requirements.txt
```

## Cómo ejecutarlo

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (en macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

Para regenerar los reportes JSON:

```bash
python reporte.py
```

Para el notebook: ábrelo en [Google Colab](https://colab.research.google.com/) (*Archivo → Subir
cuaderno*) y sube también el CSV con el panel de archivos.

## Qué incluye el dashboard

- **Filtros (barra lateral):** año, sexo, rango de edad, estrato, área de residencia y exclusión de
  fechas inconsistentes.
- **Pestañas:**
  - **Pregunta guía:** la historia completa en 4 actos, la respuesta a la pregunta, reflexión sobre
    datos e IA y limitaciones.
  - **Evolución**, **Perfil**, **Factores y antecedentes**, **Mecanismo y atención** y **Territorio**.
  - **Estadísticas (NumPy):** media, mediana, desviación, mínimo, máximo, cuartiles, coeficiente de
    variación y correlación, con comparación por grupos y descarga en JSON.
  - **Datos:** tabla con búsqueda y descarga en CSV.

## Cumplimiento de los requisitos técnicos

| # | Requisito | Dónde se cumple |
|---|---|---|
| R1 | Dataset real (≥100 registros, ≥5 variables) | 818 × 49 · `data/` |
| R2 | Código estructurado: funciones, condicionales, bucles, PEP 8, docstrings | `src/datos.py` (`clasificar_edad`, `validar_registros`, `contar_por`), `src/estadisticas.py`, `app.py` |
| R3 | Colecciones y archivos CSV/JSON | Listas de dicts con `csv.DictReader`, sets para duplicados, tuplas; escritura JSON en `reporte.py` y descargas CSV/JSON en la app |
| R4 | ≥5 estadísticas descriptivas con NumPy y pandas | 11 estadísticas en `resumen_numerico()`; pestaña Estadísticas y notebook |
| R5 | ≥3 widgets y ≥3 visualizaciones | 10+ widgets (pills, slider, multiselect, toggle, selectbox, text_input, botones) y 15+ gráficos (barras, líneas, mapas de calor, histograma, cajas, dona) |
| R6 | Despliegue en la nube | [intentos-suicidio-tunja.streamlit.app](https://intentos-suicidio-tunja.streamlit.app/) |
| R7 | Storytelling con pregunta guía | Pestaña Pregunta guía (historia en 4 actos y respuesta con datos) |
| R8 | Repositorio GitHub con código, datos y README | Este repositorio |

## Autor

Juan Esteban Garcés Ochoa
