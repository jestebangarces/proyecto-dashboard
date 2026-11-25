# Intentos de suicidio notificados en Tunja (2020-2024)

Proyecto integrador de primer semestre de Ingeniería de Datos e Inteligencia Artificial, para las materias Introducción a la Ingeniería de Datos e IA y Lógica Computacional.

App: [https://intentos-suicidio-tunja.streamlit.app/](https://suicidios-tunja-dashboard.streamlit.app/)

> Este es un tema sensible. Los datos no tienen nombres ni documentos y solo los analicé de forma agregada. Si tú o alguien cercano necesita ayuda en Colombia, puedes llamar a la Línea 192 (opción 4) o a la Línea 106.

## De qué trata

Escogí este tema porque los intentos de suicidio en jóvenes son algo de lo que se habla poco, y quería saber qué dicen los datos de mi ciudad. La pregunta que guió todo el proyecto fue:

**¿Quiénes son las personas con intentos de suicidio notificados en Tunja entre 2020 y 2024, qué situaciones las rodean y cómo ha cambiado la cantidad de casos?**

## Lo que encontramos

- La mayoría de los casos son mujeres (65 %). La edad mediana es 21 años y 3 de cada 4 casos tienen entre 12 y 28 años.
- Lo que más aparece registrado son los problemas familiares (43 %) y los conflictos con la pareja o expareja (35 %).
- Más de la mitad (51 %) ya había tenido un intento antes y el 40 % tenía ideación suicida persistente.
- Comparando solo los años completos, los casos pasaron de 125 en 2020 a 224 en 2022, un aumento del 79 %. Eso no quiere decir necesariamente que haya más casos; también puede ser que ahora se notifiquen mejor.
- Casi todos fueron remitidos a psicología (87 %) o a psiquiatría (91 %).

## Los datos

- **Fuente:** fichas de notificación del evento "intento de suicidio" del sistema de vigilancia en salud pública de Tunja. [ESCRIBE AQUÍ LA ENTIDAD Y EL ENLACE DE DONDE LO DESCARGASTE]
- **Archivo:** `data/Tunja_intentos_datos_limpios.csv`
- **Tamaño:** 818 registros y 49 variables.
- **Periodo:** del 2 de enero de 2020 al 28 de marzo de 2024.
- **Variables:** fechas, edad, sexo, escolaridad, estrato, barrio, factores desencadenantes, antecedentes, mecanismo y remisiones (la mayoría son columnas de SI/NO).

Cosas que hay que tener en cuenta de los datos:

- 2023 no tiene notificaciones de julio a septiembre y 2024 solo llega hasta marzo. Por eso, para comparar años, solo usé 2020, 2021 y 2022.
- El 17 % de los registros no tiene el número de intentos.
- Hay 22 registros donde la fecha del hecho es posterior a la fecha de notificación. En el dashboard se pueden excluir con un filtro.

El detalle de la revisión de calidad está en `salidas/reporte_calidad.json`.

## Cómo está organizado

```
app.py              -> el dashboard en Streamlit
reporte.py          -> genera los reportes de calidad y estadística en JSON
src/
  datos.py          -> carga del CSV, validación, listas de columnas, funciones de CSV y JSON
  estadisticas.py   -> estadísticas descriptivas con NumPy
data/               -> el dataset limpio
notebooks/          -> análisis exploratorio en Google Colab
salidas/            -> los JSON que genera reporte.py
.streamlit/         -> colores y tema de la app
requirements.txt    -> librerías necesarias
```

Separamos el código así para que `app.py` solo se encargue de la parte visual y los cálculos queden en `src/`, donde se pueden reutilizar en el notebook y en `reporte.py`.

## Cómo correrlo

Necesitas Python 3.10 o más reciente.

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

En macOS o Linux:

```bash
source .venv/bin/activate
```

Después:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre solo en el navegador (normalmente en http://localhost:8501).

Para volver a generar los reportes JSON:

```bash
python reporte.py
```

El notebook se puede abrir en Google Colab.

## Qué tiene el dashboard

En la barra lateral se puede filtrar por año, sexo, rango de edad, estrato y área de residencia, y también excluir los registros con fechas inconsistentes. Todo lo demás se recalcula con los filtros.

Arriba hay unos indicadores generales y un resumen con lo más importante. Después vienen estas pestañas:

- **Pregunta guía:** la historia del análisis contada en cuatro partes, la respuesta a la pregunta, una reflexión sobre el papel de los datos y la IA, y las limitaciones.
- **Evolución:** casos por año, por mes y un mapa de calor para ver en qué meses hubo más casos.
- **Perfil:** edad, grupo de edad, escolaridad, estado civil, estrato y afiliación a salud.
- **Factores y antecedentes:** los factores desencadenantes y los antecedentes, con la opción de comparar mujeres y hombres.
- **Mecanismo y atención:** el mecanismo registrado y las remisiones a servicios.
- **Territorio:** los barrios con más casos y el área de residencia.
- **Estadísticas (NumPy):** media, mediana, desviación estándar, mínimo, máximo, cuartiles, coeficiente de variación y correlación, con la opción de comparar por grupos y descargar el resumen en JSON.
- **Datos:** la tabla con buscador y descarga en CSV.

## Requisitos del proyecto

- **R1, dataset real:** 818 registros y 49 variables (`data/`).
- **R2, código estructurado:** funciones con docstrings, condicionales y bucles en `src/datos.py` (por ejemplo `clasificar_edad`, `validar_registros` y `contar_por`), `src/estadisticas.py` y `app.py`.
- **R3, colecciones y archivos:** listas, diccionarios, sets y tuplas; lectura del CSV con `csv.DictReader` y escritura de JSON en `reporte.py`. La app también permite descargar CSV y JSON.
- **R4, estadísticas con NumPy y pandas:** 11 estadísticas en `resumen_numerico()`, que se ven en la pestaña de Estadísticas y en el notebook.
- **R5, widgets y visualizaciones:** más de 10 widgets (botones de selección, slider, multiselect, toggle, selectbox, buscador y botones de descarga) y más de 15 gráficos (barras, líneas, histograma, mapas de calor, diagrama de cajas y dona).
- **R6, despliegue:** está publicado en Streamlit Community Cloud, en el enlace del principio.
- **R7, storytelling:** la pestaña Pregunta guía responde la pregunta con los datos.
- **R8, repositorio:** este repositorio.

## Limitaciones

- Son casos **notificados**, no todos los intentos que pasaron en la ciudad. Muchos nunca llegan a un servicio de salud.
- Los factores son lo que quedó registrado en la ficha, no causas comprobadas.
- No tengo datos de población por barrio ni por edad, así que comparo conteos y porcentajes, no tasas.
- Algunos años están incompletos, como expliqué arriba.

## Uso ético

Como son datos de salud mental, los manejé con cuidado: no tienen nombres ni documentos, solo los presento de forma agregada y en la app evité colores alarmantes. La idea del proyecto es entender el problema para apoyar la prevención, no señalar a nadie.
