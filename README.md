# Intentos de suicidio notificados en Tunja (2020–2024)

**De los datos a la historia** · Proyecto integrador de primer semestre
Ingeniería de Datos e Inteligencia Artificial
Asignaturas: *Introducción a la Ingeniería de Datos e IA* y *Lógica Computacional*

🔗 **App desplegada:** `PENDIENTE: pega aquí el enlace de Streamlit Cloud`

> ⚠️ **Tema sensible.** Los datos no contienen nombres ni documentos de identidad y se analizan
> solo de forma agregada. Si tú o alguien cercano necesita apoyo en Colombia: **Línea 192, opción 4**
> o **Línea 106**.

## Pregunta guía

> ¿Quiénes son las personas con intentos de suicidio notificados en Tunja entre 2020 y 2024,
> qué situaciones las rodean y cómo ha cambiado la cantidad de casos?

## Hallazgos principales

| | Hallazgo |
|---|---|
| 👥 | El **65 %** de los casos son mujeres; la edad mediana es **21 años** y el **76 %** tiene entre 12 y 28 años. |
| 🧩 | Los factores más registrados son **problemas familiares (43 %)** y **conflicto con la pareja (35 %)**. |
| 🔁 | El **51 %** ya había tenido un intento previo y el **40 %** presentaba ideación suicida persistente. |
| 📈 | Entre 2020 y 2022 (años completos) los casos notificados aumentaron **79 %** (125 → 224). |
| 🩺 | El 87 % fue remitido a psicología y el 91 % a psiquiatría. |

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
├── docs/
│   ├── propuesta.md            # Propuesta del proyecto (1 página)
│   ├── algoritmo.md            # Pseudocódigo y diagrama de flujo
│   ├── guion_pitch.md          # Storytelling del pitch de 5 minutos
│   └── informe_tecnico.md      # Borrador del informe en normas APA
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
  - ❓ **Pregunta guía:** la historia completa en 4 actos, la respuesta a la pregunta, reflexión sobre
    datos e IA y limitaciones.
  - 📈 Evolución · 👤 Perfil · 🧩 Factores y antecedentes · 🩺 Mecanismo y atención · 📍 Territorio.
  - 📐 **Estadísticas (NumPy):** media, mediana, desviación, mínimo, máximo, cuartiles, coeficiente de
    variación y correlación, con comparación por grupos y descarga en JSON.
  - 🗃️ Datos: tabla con búsqueda y descarga en CSV.

## Cumplimiento de los requisitos técnicos

| # | Requisito | Dónde se cumple |
|---|---|---|
| R1 | Dataset real (≥100 registros, ≥5 variables) | 818 × 49 · `data/` |
| R2 | Código estructurado: funciones, condicionales, bucles, PEP 8, docstrings | `src/datos.py` (`clasificar_edad`, `validar_registros`, `contar_por`), `src/estadisticas.py`, `app.py` |
| R3 | Colecciones y archivos CSV/JSON | Listas de dicts con `csv.DictReader`, sets para duplicados, tuplas; escritura JSON en `reporte.py` y descargas CSV/JSON en la app |
| R4 | ≥5 estadísticas descriptivas con NumPy y pandas | 11 estadísticas en `resumen_numerico()`; pestaña 📐 y notebook |
| R5 | ≥3 widgets y ≥3 visualizaciones | 10+ widgets (pills, slider, multiselect, toggle, selectbox, text_input, botones) y 15+ gráficos (barras, líneas, mapas de calor, histograma, cajas, dona) |
| R6 | Despliegue en la nube | Streamlit Cloud (ver abajo) |
| R7 | Storytelling con pregunta guía | Pestaña ❓ y [`docs/guion_pitch.md`](docs/guion_pitch.md) |
| R8 | Repositorio GitHub con código, datos y README | Este repositorio |

## Despliegue en Streamlit Cloud

1. Sube este repositorio a GitHub (público).
2. Entra a [share.streamlit.io](https://share.streamlit.io), inicia sesión con GitHub y pulsa **Create app**.
3. Elige el repositorio, la rama `main` y el archivo principal `app.py`.
4. Pulsa **Deploy** y copia el enlace en la parte superior de este README.

## Autor(es)

`COMPLETAR: nombre(s), docentes, fecha`
