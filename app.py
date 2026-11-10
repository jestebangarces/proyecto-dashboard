"""Dashboard interactivo: intentos de suicidio notificados en Tunja (2020-2024).

Proyecto integrador de primer semestre - Ingeniería de Datos e IA.
Ejecutar con:  streamlit run app.py

Organización del código:
    * src/datos.py         -> carga, validación, colecciones y archivos CSV/JSON.
    * src/estadisticas.py  -> estadísticas descriptivas con NumPy.
    * app.py (este archivo) -> interfaz en Streamlit: filtros, gráficos y narrativa.
"""

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from src.datos import (
    ANTECEDENTES, FACTORES, GRUPOS_EDAD, MECANISMOS, REMISIONES, RUTA_DATOS,
    anios_completos, cargar_datos, etiqueta, meses_faltantes, pct_si,
)
from src.estadisticas import (
    NOMBRES_ESTADISTICAS, correlacion, resumen_general, resumen_numerico, resumen_por_grupo,
    variacion_porcentual,
)

# ------------------------------------------------------------------ configuración
st.set_page_config(
    page_title="Intentos de suicidio · Tunja",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# Paleta sobria (azul pizarra / verde azulado), sin rojos
AZUL, TEAL, AMBAR, GRIS = "#3E5C76", "#2A7F8E", "#D08C2E", "#8A97A6"
TEXTO, TEXTO_SUAVE, REJILLA = "#1F2A37", "#5B6B7C", "#E6EBF0"
COLOR_SEXO = {"FEMENINO": TEAL, "MASCULINO": AZUL}
NOMBRE_SEXO = {"FEMENINO": "Mujeres", "MASCULINO": "Hombres"}
ESCALA = ["#EEF5F7", "#B9D9DF", "#6FAFBA", TEAL, "#1D4F5A"]

ORDEN_ESCOLARIDAD = [
    "NINGUNO", "PREESCOLAR", "BASICA PRIMARIA", "BASICA SECUNDARIA", "MEDIA TECNICA",
    "TECNICA PROFESIONAL", "TECNOLOGICA O TECNICA", "PROFESIONAL", "ESPECIALIZACION", "MAESTRIA",
    "SIN INFORMACION",
]

# ------------------------------------------------------------------ estilo visual
pio.templates["tunja"] = go.layout.Template(
    layout=dict(
        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=TEXTO),
        colorway=[TEAL, AZUL, AMBAR, GRIS],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor=REJILLA, linecolor=REJILLA, zeroline=False,
                   tickfont=dict(color=TEXTO_SUAVE), title_font=dict(color=TEXTO_SUAVE)),
        yaxis=dict(gridcolor=REJILLA, linecolor=REJILLA, zeroline=False,
                   tickfont=dict(color=TEXTO_SUAVE), title_font=dict(color=TEXTO_SUAVE)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                    title_text="", font=dict(color=TEXTO_SUAVE)),
        hoverlabel=dict(bgcolor="white", bordercolor=REJILLA,
                        font=dict(family="Inter, Segoe UI, sans-serif", size=13, color=TEXTO)),
        margin=dict(l=0, r=10, t=10, b=0),
        bargap=0.25,
    )
)
pio.templates.default = "plotly_white+tunja"
CONFIG_GRAFICO = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="st-"], .stMarkdown, button, input { font-family: 'Inter', 'Segoe UI', sans-serif; }
/* Los íconos de Streamlit son ligaduras de texto: necesitan su propia fuente */
[data-testid="stIconMaterial"], [data-testid="stExpanderToggleIcon"] {
  font-family: 'Material Symbols Rounded' !important;
}
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1400px; }

/* Encabezado */
.hero {
  background: linear-gradient(120deg, #1D4F5A 0%, #2A7F8E 55%, #3E5C76 100%);
  color: #fff; border-radius: 16px; padding: 1.5rem 1.8rem 1.3rem; margin-bottom: 1.1rem;
  box-shadow: 0 6px 20px rgba(29, 79, 90, .18);
}
.hero h1 { color: #fff; font-size: 1.85rem; font-weight: 700; margin: 0 0 .25rem; padding: 0; }
.hero p { color: rgba(255,255,255,.85); margin: 0 0 .8rem; font-size: .98rem; }
.chip {
  display: inline-block; background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.25);
  color: #fff; border-radius: 999px; padding: .18rem .75rem; margin: .15rem .35rem .15rem 0;
  font-size: .82rem; font-weight: 500;
}

/* Tarjetas: contenedores con borde y métricas */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]),
div[data-testid="stVerticalBlock"][class*="border"] {
  background: #fff;
}
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px !important; }
[data-testid="stMetric"] {
  background: #fff; border-radius: 14px !important; padding: .9rem 1rem !important;
  box-shadow: 0 1px 3px rgba(31,42,55,.06);
}
[data-testid="stMetricLabel"] p { color: #5B6B7C; font-weight: 600; font-size: .85rem; }
[data-testid="stMetricValue"] { color: #1D4F5A; font-weight: 700; }

/* Títulos de cada panel */
.panel-titulo { font-size: 1.02rem; font-weight: 650; color: #1F2A37; margin: 0 0 .1rem; }
.panel-sub { font-size: .84rem; color: #5B6B7C; margin: 0 0 .3rem; }
.seccion { font-size: 1.15rem; font-weight: 700; color: #1F2A37; margin: .6rem 0 .4rem; }

/* Hallazgos */
.hallazgos { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: .7rem; }
.hallazgo {
  background: #fff; border: 1px solid #E1E7ED; border-left: 4px solid #2A7F8E;
  border-radius: 12px; padding: .75rem .9rem; font-size: .9rem; color: #1F2A37; line-height: 1.4;
}
.hallazgo b { color: #1D4F5A; }

/* Pestañas */
.stTabs [data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid #DCE3EA; }
.stTabs [data-baseweb="tab"] {
  height: 2.6rem; padding: 0 1.1rem; border-radius: 10px 10px 0 0; font-weight: 600; color: #5B6B7C;
}
.stTabs [aria-selected="true"] { background: #fff; color: #1D4F5A !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: #2A7F8E; height: 3px; }

/* Barra lateral */
[data-testid="stSidebar"] { background: #fff; border-right: 1px solid #E1E7ED; }
[data-testid="stSidebar"] h2 { font-size: 1.15rem; }
.leer { font-size: .82rem; color: #5B6B7C; margin-top: -.3rem; }

/* Storytelling */
.pregunta {
  background: #fff; border: 1px solid #E1E7ED; border-left: 6px solid #D08C2E; border-radius: 12px;
  padding: 1rem 1.2rem; font-size: 1.15rem; font-weight: 600; color: #1F2A37; margin-bottom: .4rem;
}
.pregunta span {
  display: block; font-size: .78rem; text-transform: uppercase; letter-spacing: .06em;
  color: #D08C2E; margin-bottom: .25rem;
}
.acto { font-size: 1.02rem; font-weight: 700; color: #1D4F5A; margin: 0 0 .3rem; }
</style>
""",
    unsafe_allow_html=True,
)


def bonito(valor) -> str:
    """'BASICA SECUNDARIA' -> 'Basica secundaria' para ejes y leyendas."""
    return str(valor).capitalize()


# ------------------------------------------------------------------ carga de datos
@st.cache_data(show_spinner="Cargando datos…")
def cargar(origen) -> pd.DataFrame:
    """Versión en caché de :func:`src.datos.cargar_datos` (evita releer el CSV en cada clic)."""
    return cargar_datos(origen)


if RUTA_DATOS.exists():
    df = cargar(RUTA_DATOS)
else:
    st.title("Intentos de suicidio · Tunja")
    st.info(
        "No encontré `data/Tunja_intentos_datos_limpios.csv`. "
        "Cópialo a la misma carpeta o súbelo aquí."
    )
    subido = st.file_uploader("Base limpia (CSV)", type="csv")
    if subido is None:
        st.stop()
    df = cargar(subido)


# ------------------------------------------------------------------ utilidades
def renombrar_sexo(fig):
    """Leyendas 'Mujeres' / 'Hombres' en lugar de FEMENINO / MASCULINO."""
    fig.for_each_trace(lambda t: t.update(name=NOMBRE_SEXO.get(t.name, t.name)))
    return fig


def panel(titulo: str, fig=None, leer: str | None = None, sub: str | None = None):
    """Tarjeta blanca con título, gráfico y una línea de 'cómo leerlo'."""
    caja = st.container(border=True)
    with caja:
        st.markdown(f'<p class="panel-titulo">{titulo}</p>', unsafe_allow_html=True)
        if sub:
            st.markdown(f'<p class="panel-sub">{sub}</p>', unsafe_allow_html=True)
        if fig is not None:
            st.plotly_chart(fig, width="stretch", config=CONFIG_GRAFICO)
        if leer:
            st.markdown(f'<p class="leer"><b>Cómo leerlo:</b> {leer}</p>', unsafe_allow_html=True)
    return caja


def barras_pct(datos, columnas, por_sexo=False, alto=380):
    """Barras horizontales con el % de casos con "SI" en cada columna (opcional por sexo)."""
    t = pct_si(datos, columnas, "SEXO" if por_sexo else None)
    orden = t.groupby("Variable")["Porcentaje"].max().sort_values().index.tolist()
    fig = px.bar(
        t, x="Porcentaje", y="Variable", orientation="h",
        color="Grupo" if por_sexo else None,
        color_discrete_map=COLOR_SEXO, barmode="group",
        text=t["Porcentaje"].map("{:.1f}%".format),
        category_orders={"Variable": orden},
        custom_data=["Casos"],
    )
    if not por_sexo:
        fig.update_traces(marker_color=TEAL)
    fig.update_traces(
        textposition="outside", cliponaxis=False, textfont=dict(color=TEXTO_SUAVE, size=12),
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% de los casos (%{customdata[0]} casos)<extra></extra>",
        marker_cornerradius=4,
    )
    fig.update_layout(height=alto, margin=dict(l=0, r=45, t=30 if por_sexo else 10, b=0),
                      yaxis_title=None, xaxis_title="% de casos", xaxis_ticksuffix="%")
    fig.update_xaxes(range=[0, t["Porcentaje"].max() * 1.18 + 1])
    return renombrar_sexo(fig)


def barras_cat(datos, col, orden=None, horizontal=True, alto=340, color=AZUL):
    """Barras con el conteo y el % de cada categoría de una columna."""
    t = datos[col].astype(str).value_counts().rename_axis(col).reset_index(name="Casos")
    t["%"] = t["Casos"] / t["Casos"].sum() * 100
    if orden:
        t[col] = pd.Categorical(t[col], categories=[o for o in orden if o in set(t[col])], ordered=True)
        t = t.sort_values(col, ascending=not horizontal)
    else:
        t = t.sort_values("Casos")
    t["Etiqueta"] = t[col].astype(str).map(bonito)
    x, y = ("Casos", "Etiqueta") if horizontal else ("Etiqueta", "Casos")
    fig = px.bar(t, x=x, y=y, orientation="h" if horizontal else "v",
                 text=t.apply(lambda r: f"{r['Casos']} ({r['%']:.0f}%)", axis=1),
                 custom_data=["%"])
    fig.update_traces(
        marker_color=color, textposition="outside", cliponaxis=False,
        textfont=dict(color=TEXTO_SUAVE, size=12), marker_cornerradius=4,
        hovertemplate=f"<b>%{{{y}}}</b><br>%{{{x}}} casos (%{{customdata[0]:.1f}}%)<extra></extra>",
    )
    fig.update_layout(height=alto, margin=dict(l=0, r=60 if horizontal else 0, t=20, b=0),
                      xaxis_title="Casos" if horizontal else None, yaxis_title=None)
    if horizontal:
        fig.update_yaxes(categoryorder="array", categoryarray=t["Etiqueta"].tolist())
    else:
        fig.update_xaxes(categoryorder="array", categoryarray=t["Etiqueta"].tolist())
    return fig


def mapa_calor(valores, x, y, alto, etiqueta_color, formato="d"):
    """Mapa de calor con la paleta del tablero y el valor escrito en cada celda."""
    fig = go.Figure(go.Heatmap(
        z=valores, x=x, y=y, colorscale=ESCALA, xgap=3, ygap=3,
        texttemplate=f"%{{z:{formato}}}" if formato != "d" else "%{z}",
        textfont=dict(size=12),
        colorbar=dict(title=etiqueta_color, thickness=12, outlinewidth=0),
        hovertemplate="<b>%{y}</b> · %{x}<br>%{z:" + (formato if formato != "d" else "") + "} "
                      + etiqueta_color.lower() + "<extra></extra>",
    ))
    fig.update_layout(height=alto, margin=dict(l=0, r=0, t=10, b=0))
    fig.update_xaxes(showgrid=False, side="top")
    fig.update_yaxes(showgrid=False, autorange="reversed")
    return fig


def hallazgos(datos: pd.DataFrame) -> list[str]:
    """Resumen automático en lenguaje sencillo de lo más llamativo en la selección actual."""
    por_anio = datos["AÑO"].value_counts()
    grupo = datos["GRUPO_EDAD"].value_counts()
    top_factor = pct_si(datos, FACTORES).sort_values("Porcentaje", ascending=False).iloc[0]
    top_mec = pct_si(datos, MECANISMOS).sort_values("Porcentaje", ascending=False).iloc[0]
    mujeres = (datos["SEXO"] == "FEMENINO").mean() * 100
    return [
        (f"<b>{por_anio.idxmax()}</b> es el año con más casos notificados ({por_anio.max():,})."),
        (f"El grupo de edad más frecuente es <b>{grupo.idxmax()}</b>, con el "
               f"{grupo.max() / len(datos) * 100:.0f}% de los casos."),
        (f"Las mujeres son el <b>{mujeres:.0f}%</b> de los casos y los hombres el "
               f"<b>{100 - mujeres:.0f}%</b>."),
        (f"El factor desencadenante más registrado es <b>{top_factor['Variable'].lower()}</b> "
               f"({top_factor['Porcentaje']:.0f}% de los casos)."),
        (f"El mecanismo más registrado es <b>{top_mec['Variable'].lower()}</b> "
               f"({top_mec['Porcentaje']:.0f}% de los casos)."),
    ]


# ------------------------------------------------------------------ filtros (barra lateral)
anios = sorted(df["AÑO"].unique().tolist())
sexos = sorted(df["SEXO"].unique().tolist())
estratos = sorted(df["ESTRATO"].unique().tolist())
areas = sorted(df["AREA_RESIDENCIA"].unique().tolist())
e_min, e_max = int(df["EDAD"].min()), int(df["EDAD"].max())

FILTROS_INICIALES = {
    "f_anio": anios, "f_sexo": sexos, "f_estrato": estratos, "f_area": areas,
    "f_edad": (e_min, e_max), "f_flag": False,
}
for clave, valor in FILTROS_INICIALES.items():
    st.session_state.setdefault(clave, valor)


def restablecer():
    for clave, valor in FILTROS_INICIALES.items():
        st.session_state[clave] = valor


with st.sidebar:
    st.header("Filtros")
    st.caption("Si dejas un filtro vacío se incluyen todas sus opciones.")
    f_anio = st.pills("Año", anios, selection_mode="multi", key="f_anio")
    f_sexo = st.pills("Sexo", sexos, selection_mode="multi", key="f_sexo",
                      format_func=lambda s: NOMBRE_SEXO.get(s, s))
    f_edad = st.slider("Edad", e_min, e_max, key="f_edad", format="%d años")
    f_estrato = st.pills("Estrato", estratos, selection_mode="multi", key="f_estrato")
    f_area = st.multiselect("Área de residencia", areas, key="f_area", format_func=bonito,
                            placeholder="Todas")
    st.divider()
    excluir_flag = st.toggle(
        "Excluir fechas inconsistentes", key="f_flag",
        help="Registros donde la fecha del hecho es posterior a la de notificación.",
    )
    st.button("Restablecer filtros", on_click=restablecer, width="stretch")
    st.divider()
    st.caption(
        "**Uso ético de los datos:** el dataset no contiene nombres ni documentos; "
        "se analiza solo de forma agregada."
    )
    st.info(
        "Si tú o alguien cercano necesita apoyo, en Colombia puedes llamar a la "
        "**Línea 192, opción 4** (salud mental) o a la **Línea 106**.",
    )

d = df[
    df["AÑO"].isin(f_anio or anios)
    & df["SEXO"].isin(f_sexo or sexos)
    & df["EDAD"].between(*f_edad)
    & df["AREA_RESIDENCIA"].isin(f_area or areas)
    & df["ESTRATO"].isin(f_estrato or estratos)
]
if excluir_flag:
    d = d[d["FLAG_FECHA_INCONSISTENTE"] == "NO"]

# ------------------------------------------------------------------ encabezado
chips = [
    f"{df['FECHA_NOTIFICACION'].min():%d/%m/%Y} – {df['FECHA_NOTIFICACION'].max():%d/%m/%Y}",
    f"{len(d):,} de {len(df):,} registros",
]
if f_anio and set(f_anio) != set(anios):
    chips.append("Años: " + ", ".join(map(str, sorted(f_anio))))
if f_sexo and set(f_sexo) != set(sexos):
    chips.append("Sexo: " + ", ".join(NOMBRE_SEXO.get(s, s) for s in f_sexo))
if tuple(f_edad) != (e_min, e_max):
    chips.append(f"Edad: {f_edad[0]}–{f_edad[1]}")
if f_estrato and set(f_estrato) != set(estratos):
    chips.append("Estrato: " + ", ".join(map(str, sorted(f_estrato))))
if f_area and set(f_area) != set(areas):
    chips.append("Área: " + ", ".join(bonito(a) for a in f_area))
if excluir_flag:
    chips.append("Sin fechas inconsistentes")

st.markdown(
    f"""
<div class="hero">
  <h1>Intentos de suicidio notificados en Tunja</h1>
  <p>Vigilancia en salud pública · resumen interactivo de los casos notificados</p>
  {''.join(f'<span class="chip">{c}</span>' for c in chips)}
</div>
""",
    unsafe_allow_html=True,
)

if d.empty:
    st.warning("Ningún registro cumple los filtros. Amplía la selección en la barra lateral.")
    st.stop()

# ------------------------------------------------------------------ indicadores
casos_anio = d.groupby("AÑO").size().reindex(sorted(d["AÑO"].unique()))
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Casos", f"{len(d):,}", border=True, help="Total de registros con los filtros actuales. "
          "La mini-gráfica muestra los casos por año.",
          chart_data=casos_anio.tolist() if len(casos_anio) > 1 else None, chart_type="bar")
c2.metric("Edad mediana", f"{d['EDAD'].median():.0f} años", border=True,
          help="La mitad de los casos es más joven que esta edad y la otra mitad es mayor.")
c3.metric("Mujeres", f"{(d['SEXO'] == 'FEMENINO').mean() * 100:.0f}%", border=True,
          help="Porcentaje de casos de sexo femenino.")
c4.metric("Con intentos previos", f"{(d['INTENTOS_PREVIOS'] == 'SI').mean() * 100:.0f}%", border=True,
          help="Porcentaje de personas que ya habían tenido al menos un intento antes.")
c5.metric("Con ideación persistente", f"{(d['IDEACION_SUICIDA_PERSISTENTE'] == 'SI').mean() * 100:.0f}%",
          border=True, help="Porcentaje con pensamientos de suicidio que se repiten en el tiempo.")

st.markdown('<p class="seccion">Lo más importante con los filtros actuales</p>', unsafe_allow_html=True)
st.markdown(
    '<div class="hallazgos">'
    + "".join(f'<div class="hallazgo">{t}</div>' for t in hallazgos(d))
    + "</div>",
    unsafe_allow_html=True,
)

st.write("")
(tab_historia, tab_tiempo, tab_perfil, tab_factores, tab_mecanismo, tab_territorio,
 tab_stats, tab_datos) = st.tabs(
    ["Pregunta guía", "Evolución", "Perfil", "Factores y antecedentes",
     "Mecanismo y atención", "Territorio", "Estadísticas (NumPy)", "Datos"]
)

# ------------------------------------------------------------------ storytelling
PREGUNTA_GUIA = (
    "¿Quiénes son las personas con intentos de suicidio notificados en Tunja entre 2020 y 2024, "
    "qué situaciones las rodean y cómo ha cambiado la cantidad de casos?"
)

with tab_historia:
    st.markdown(f'<div class="pregunta"><span>Pregunta guía</span>{PREGUNTA_GUIA}</div>',
                unsafe_allow_html=True)
    st.caption("La historia se recalcula con los filtros de la barra lateral.")

    # Acto 1: ¿cuántos y cuándo? -> solo años completos, para no comparar con un año parcial
    # La completitud se mide sobre la base entera: un subgrupo pequeño puede no tener casos
    # en algún mes sin que eso signifique que el año esté incompleto.
    por_anio = d.groupby("AÑO").size()
    completos = [a for a in anios_completos(df) if a in por_anio.index]
    with st.container(border=True):
        st.markdown('<p class="acto">1 · ¿Cuántos casos hay y cómo han cambiado?</p>',
                    unsafe_allow_html=True)
        if len(completos) >= 2:
            serie = por_anio.loc[completos]
            cambio = variacion_porcentual([serie.iloc[0], serie.iloc[-1]])[0]
            parciales = {a: m for a, m in meses_faltantes(df).items() if m and a in por_anio.index}
            texto_parcial = ""
            if parciales:
                partes = []
                for a, meses in parciales.items():
                    if meses == list(range(meses[0], 13)):  # faltan solo los meses finales
                        partes.append(f"**{a}** solo llega hasta {MESES[meses[0] - 2].lower()}")
                    else:
                        nombres = ", ".join(MESES[m - 1].lower() for m in meses)
                        partes.append(f"**{a}** no tiene notificaciones en {nombres}")
                detalle = "; ".join(partes)
                texto_parcial = (f" No se comparan los años incompletos: {detalle}. Esos vacíos "
                                 "parecen deberse a la base de datos, no a ausencia de casos.")
            st.markdown(
                f"Entre **{completos[0]}** y **{completos[-1]}** los casos notificados pasaron de "
                f"**{serie.iloc[0]}** a **{serie.iloc[-1]}**, un cambio de **{cambio:+.0f}%**."
                f"{texto_parcial} Un aumento en las notificaciones puede significar más casos, pero "
                "también una mejor búsqueda y registro por parte del sistema de salud."
            )
            var = variacion_porcentual(serie.values)
            t = pd.DataFrame({"Año": serie.index.astype(str), "Casos": serie.values,
                              "Cambio": ["—"] + [f"{v:+.0f}%" for v in var]})
            t["Etiqueta"] = [f"<b>{c}</b>" if v == "—" else f"<b>{c}</b> ({v})"
                             for c, v in zip(t["Casos"], t["Cambio"])]
            fig = px.bar(t, x="Año", y="Casos", text="Etiqueta", custom_data=["Cambio"])
            fig.update_traces(marker_color=TEAL, marker_cornerradius=4, textposition="outside",
                              cliponaxis=False, textfont=dict(color=TEXTO),
                              hovertemplate="<b>%{x}</b><br>%{y} casos<br>Cambio vs. año anterior: "
                                            "%{customdata[0]}<extra></extra>")
            fig.update_yaxes(range=[0, t["Casos"].max() * 1.2])
            fig.update_layout(height=280, margin=dict(l=0, r=0, t=20, b=0), xaxis_title=None)
            fig.update_xaxes(type="category", showgrid=False)  # "2020" no debe leerse como fecha
            st.plotly_chart(fig, width="stretch", config=CONFIG_GRAFICO)
            st.markdown('<p class="leer"><b>Cómo leerlo:</b> casos por año completo; entre '
                        'paréntesis, el cambio frente al año anterior (calculado con NumPy).</p>',
                        unsafe_allow_html=True)
        else:
            st.markdown("Con los filtros actuales no hay al menos dos años completos para comparar.")

    # Acto 2: ¿quiénes?
    mujeres = (d["SEXO"] == "FEMENINO").mean() * 100
    jovenes = d["GRUPO_EDAD"].isin(GRUPOS_EDAD[1:3]).mean() * 100
    edad = resumen_numerico(d["EDAD"])
    with st.container(border=True):
        st.markdown('<p class="acto">2 · ¿Quiénes son?</p>', unsafe_allow_html=True)
        st.markdown(
            f"El **{mujeres:.0f}%** de los casos son mujeres. La edad mediana es "
            f"**{edad['mediana']:.0f} años** y la mitad de los casos está entre "
            f"**{edad['q1']:.0f} y {edad['q3']:.0f} años**. Adolescentes y jóvenes (12 a 28 años) "
            f"suman el **{jovenes:.0f}%** de los casos."
        )

    # Acto 3: ¿qué los rodea?
    top_f = pct_si(d, FACTORES).nlargest(3, "Porcentaje")
    top_a = pct_si(d, ANTECEDENTES).nlargest(2, "Porcentaje")
    previos = (d["INTENTOS_PREVIOS"] == "SI").mean() * 100
    ideacion = (d["IDEACION_SUICIDA_PERSISTENTE"] == "SI").mean() * 100
    with st.container(border=True):
        st.markdown('<p class="acto">3 · ¿Qué situaciones los rodean?</p>', unsafe_allow_html=True)
        lista_f = "; ".join(f"**{r.Variable.lower()}** ({r.Porcentaje:.0f}%)" for r in top_f.itertuples())
        lista_a = " y ".join(f"**{r.Variable.lower()}** ({r.Porcentaje:.0f}%)" for r in top_a.itertuples())
        st.markdown(
            f"Los factores desencadenantes más registrados son: {lista_f}. Entre los antecedentes "
            f"destacan {lista_a}. Además, el **{previos:.0f}%** ya había tenido un intento previo y el "
            f"**{ideacion:.0f}%** presentaba ideación suicida persistente: muchos casos no son "
            "eventos aislados, sino parte de una historia que se repite."
        )

    # Acto 4: ¿qué atención reciben?
    rem = pct_si(d, REMISIONES).set_index("Variable")["Porcentaje"]
    sin_remision = (~d[REMISIONES].eq("SI").any(axis=1)).mean() * 100
    with st.container(border=True):
        st.markdown('<p class="acto">4 · ¿Qué atención reciben?</p>', unsafe_allow_html=True)
        st.markdown(
            f"El **{rem['Psicología']:.0f}%** fue remitido a psicología, el "
            f"**{rem['Psiquiatría']:.0f}%** a psiquiatría y el **{rem['Trabajo social']:.0f}%** a "
            f"trabajo social. Aun así, el **{sin_remision:.0f}%** de los casos no registra ninguna "
            "remisión."
        )

    st.markdown('<p class="seccion">Respuesta a la pregunta guía</p>', unsafe_allow_html=True)
    st.success(
        f"Los intentos de suicidio notificados en Tunja afectan sobre todo a **mujeres "
        f"({mujeres:.0f}%)** y a **personas jóvenes** (edad mediana {edad['mediana']:.0f} años). "
        f"Suelen estar ligados a **{top_f.iloc[0]['Variable'].lower()}** y a "
        f"**{top_f.iloc[1]['Variable'].lower()}**, y el **{previos:.0f}%** ya lo había intentado "
        "antes. Esto sugiere enfocar la prevención en población joven, en esas situaciones de "
        "conflicto y en el seguimiento cercano a quienes ya tuvieron un intento.",
    )

    with st.expander("Reflexión: el papel de los datos y la inteligencia artificial"):
        st.markdown(
            """
- **Los datos hacen visible un problema silencioso.** La notificación obligatoria al sistema de
  vigilancia en salud pública permite medir el fenómeno y orientar recursos de salud mental.
- **Lo que no se registra no existe en los datos.** Hay sub-registro: muchos intentos nunca llegan
  a un servicio de salud. Un aumento de casos puede reflejar mejor registro y no solo más intentos.
- **La IA podría ayudar** a detectar combinaciones de riesgo (ideación persistente, intentos
  previos, problemas familiares) para priorizar el seguimiento.
- **Pero implica riesgos éticos:** etiquetar a alguien como "de riesgo" puede estigmatizar; los
  modelos heredan los sesgos de los datos y la información de salud mental es muy sensible.
  Cualquier uso debe ser anónimo, transparente y con decisión humana.
"""
        )
    with st.expander("Limitaciones del análisis"):
        st.markdown(
            """
- Son **casos notificados**, no el total real de intentos en la ciudad.
- Los factores son **situaciones registradas en la ficha**, no causas comprobadas.
- Algunos años tienen meses sin notificaciones (vacíos de la base), por eso solo se comparan
  años completos.
- No hay datos de población por barrio o edad, así que se comparan conteos y porcentajes, no tasas.
"""
        )

# ------------------------------------------------------------------ evolución
with tab_tiempo:
    izq, der = st.columns([2, 3])
    with izq:
        t = d.groupby(["AÑO", "SEXO"]).size().reset_index(name="Casos")
        fig = px.bar(t, x="AÑO", y="Casos", color="SEXO", color_discrete_map=COLOR_SEXO,
                     text="Casos", barmode="stack", labels={"AÑO": "Año"})
        totales = t.groupby("AÑO")["Casos"].sum()
        fig.add_trace(go.Scatter(x=totales.index, y=totales.values, mode="text",
                                 text=[f"<b>{v}</b>" for v in totales.values], textposition="top center",
                                 textfont=dict(color=TEXTO), showlegend=False, hoverinfo="skip"))
        fig.update_traces(selector=dict(type="bar"), textfont=dict(color="white"),
                          hovertemplate="<b>%{x}</b><br>%{y} casos<extra></extra>")
        fig.update_xaxes(type="category", title=None, showgrid=False)
        fig.update_yaxes(range=[0, totales.max() * 1.15])
        fig.update_layout(height=370, margin=dict(l=0, r=0, t=30, b=0))
        panel("Casos por año", renombrar_sexo(fig),
              "cada barra es un año; los colores separan mujeres y hombres y arriba está el total.")
    with der:
        t = d.groupby("PERIODO").size().reset_index(name="Casos")
        t["Tendencia"] = t["Casos"].rolling(3, min_periods=1, center=True).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t["PERIODO"], y=t["Casos"], name="Casos del mes", mode="lines+markers",
                                 line=dict(color=TEAL, width=1.5), marker=dict(size=5),
                                 fill="tozeroy", fillcolor="rgba(42,127,142,0.10)",
                                 hovertemplate="%{x|%b %Y}: <b>%{y}</b> casos<extra></extra>"))
        fig.add_trace(go.Scatter(x=t["PERIODO"], y=t["Tendencia"], name="Promedio de 3 meses",
                                 mode="lines", line=dict(color=AMBAR, width=2.5),
                                 hovertemplate="Promedio 3 meses: %{y:.1f}<extra></extra>"))
        fig.update_layout(height=370, margin=dict(l=0, r=0, t=30, b=0), hovermode="x unified",
                          yaxis_title="Casos")
        fig.update_xaxes(title=None, showgrid=False, dtick="M6", tickformat="%b\n%Y")
        panel("Casos por mes de notificación", fig,
              "cada punto es un mes; la línea naranja suaviza los altibajos para ver la tendencia.")

    piv = (d.pivot_table(index="AÑO", columns="MES", values="ID_REGISTRO", aggfunc="count", fill_value=0)
             .reindex(columns=range(1, 13), fill_value=0))
    panel("Estacionalidad: casos por mes y año",
          mapa_calor(piv.values, MESES, piv.index.astype(str).tolist(), 60 + 50 * len(piv), "Casos"),
          "cuanto más oscuro es el cuadro, más casos hubo en ese mes de ese año. "
          "Los meses sin datos al final de la serie pueden reflejar un año incompleto, no ausencia de casos.")

# ------------------------------------------------------------------ perfil
with tab_perfil:
    a, b = st.columns(2)
    with a:
        fig = px.histogram(d, x="EDAD", color="SEXO", nbins=40, barmode="overlay",
                           opacity=0.75, color_discrete_map=COLOR_SEXO)
        fig.add_vline(x=d["EDAD"].median(), line_dash="dot", line_color=TEXTO_SUAVE,
                      annotation_text=f"Mediana: {d['EDAD'].median():.0f}",
                      annotation_font_color=TEXTO_SUAVE)
        fig.update_traces(hovertemplate="Edad %{x}<br>%{y} casos<extra></extra>")
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0),
                          xaxis_title="Edad (años)", yaxis_title="Casos")
        panel("Distribución por edad", renombrar_sexo(fig),
              "cada barra cuenta cuántas personas hay en ese rango de edad.")
    with b:
        panel("Grupo de edad",
              barras_cat(d, "GRUPO_EDAD", orden=GRUPOS_EDAD, horizontal=False, alto=350, color=TEAL),
              "las mismas edades agrupadas por etapa de vida; entre paréntesis, el % del total.")

    a, b = st.columns(2)
    with a:
        panel("Escolaridad", barras_cat(d, "ESCOLARIDAD", orden=ORDEN_ESCOLARIDAD, alto=400))
    with b:
        panel("Estado civil", barras_cat(d, "ESTADO_CIVIL", alto=400))

    a, b = st.columns(2)
    with a:
        t = d.assign(ESTRATO=d["ESTRATO"].astype(str))
        panel("Estrato socioeconómico",
              barras_cat(t, "ESTRATO", orden=["1", "2", "3", "4", "5"], horizontal=False, color=TEAL),
              "el estrato 1 es el más bajo y el 5 el más alto.")
    with b:
        panel("Afiliación a salud", barras_cat(d, "SEGURIDAD_SOCIAL"))

# ------------------------------------------------------------------ factores
with tab_factores:
    por_sexo = st.toggle("Comparar mujeres y hombres", value=False)
    a, b = st.columns(2)
    with a:
        panel("Factores desencadenantes", barras_pct(d, FACTORES, por_sexo, alto=480),
              sub="Situaciones registradas en la ficha, no causas comprobadas.")
    with b:
        panel("Antecedentes y salud mental", barras_pct(d, ANTECEDENTES, por_sexo, alto=480),
              sub="Un caso puede tener varios a la vez, por eso no suman 100%.")

    senales = ["IDEACION_SUICIDA_PERSISTENTE", "PLAN_ORGANIZADO_DE_SUICIDIO", "INTENTOS_PREVIOS",
               "PROBLEMAS_FAMILIARES", "CONFLICTO_CON_PAREJA_O_EX_PAREJA", "ESCOLAR_EDUCATIVA",
               "CONSUMO_DE_SPA", "ANTECEDENTE_TRASTORNO_PSIQUIATRICO"]
    t = pct_si(d, senales, "GRUPO_EDAD")
    piv = t.pivot(index="Variable", columns="Grupo", values="Porcentaje")
    piv = piv[[g for g in GRUPOS_EDAD if g in piv.columns]]
    panel("Señales de riesgo por grupo de edad",
          mapa_calor(piv.values, list(piv.columns), list(piv.index), 420, "% de casos", ".0f"),
          "cada cuadro muestra qué % de las personas de ese grupo de edad presenta esa señal; "
          "más oscuro significa más frecuente.")

# ------------------------------------------------------------------ mecanismo y atención
with tab_mecanismo:
    a, b = st.columns(2)
    with a:
        panel("Mecanismo registrado", barras_pct(d, MECANISMOS, alto=470),
              "porcentaje de casos con cada mecanismo. Un mismo evento puede registrar más de uno, "
              "por eso los porcentajes pueden sumar más de 100%.")
    with b:
        panel("Remisión a servicios", barras_pct(d, REMISIONES, alto=170),
              "porcentaje de casos que fueron enviados a cada servicio de atención.")
        t = pct_si(d, REMISIONES, "AÑO")
        fig = px.line(t, x="Grupo", y="Porcentaje", color="Variable", markers=True,
                      color_discrete_sequence=[TEAL, AZUL, AMBAR], custom_data=["Variable", "Casos"])
        fig.update_traces(line_width=2.5, marker_size=8,
                          hovertemplate="<b>%{customdata[0]}</b> · %{x}<br>"
                                        "%{y:.1f}% (%{customdata[1]} casos)<extra></extra>")
        fig.update_xaxes(type="category", title=None, showgrid=False)
        fig.update_layout(height=230, margin=dict(l=0, r=0, t=30, b=0),
                          yaxis_title="% remitidos", yaxis_ticksuffix="%")
        panel("Remisión por año", fig)

# ------------------------------------------------------------------ territorio
with tab_territorio:
    a, b = st.columns([3, 2])
    with a:
        with st.container(border=True):
            n = st.slider("Barrios a mostrar", 5, 30, 15)
            st.markdown(f'<p class="panel-titulo">Los {n} barrios con más casos</p>', unsafe_allow_html=True)
            t = d["BARRIO_RESIDENCIA"].value_counts().head(n).sort_values().reset_index()
            t.columns = ["Barrio", "Casos"]
            t["Barrio"] = t["Barrio"].map(lambda s: str(s).title())
            fig = px.bar(t, x="Casos", y="Barrio", orientation="h", text="Casos")
            fig.update_traces(marker_color=TEAL, textposition="outside", cliponaxis=False,
                              textfont=dict(color=TEXTO_SUAVE), marker_cornerradius=4,
                              hovertemplate="<b>%{y}</b><br>%{x} casos<extra></extra>")
            fig.update_layout(height=max(360, n * 26), margin=dict(l=0, r=30, t=10, b=0), yaxis_title=None)
            st.plotly_chart(fig, width="stretch", config=CONFIG_GRAFICO)
            st.markdown('<p class="leer"><b>Cómo leerlo:</b> barrio de residencia de la persona, '
                        'ordenado de mayor a menor número de casos.</p>', unsafe_allow_html=True)
    with b:
        t = d["AREA_RESIDENCIA"].value_counts().reset_index()
        t.columns = ["Área", "Casos"]
        t["Área"] = t["Área"].map(bonito)
        fig = px.pie(t, names="Área", values="Casos", hole=0.62,
                     color_discrete_sequence=[TEAL, AMBAR, GRIS])
        fig.update_traces(textinfo="percent", textfont_size=13, sort=False,
                          marker=dict(line=dict(color="white", width=2)),
                          hovertemplate="<b>%{label}</b><br>%{value} casos (%{percent})<extra></extra>")
        fig.update_layout(height=320, margin=dict(l=0, r=0, t=30, b=0),
                          annotations=[dict(text=f"<b>{len(d):,}</b><br>casos", showarrow=False,
                                            font=dict(size=18, color=TEXTO))])
        panel("Área de residencia", fig)
        st.info("Los barrios con pocos casos pueden variar por la forma en que se registró el nombre; "
                "la hoja *Mapeo_Barrios* del Excel documenta cómo se unificaron.")

# ------------------------------------------------------------------ estadísticas (NumPy)
VARIABLES_NUMERICAS = {"EDAD": "Edad (años)", "NUMERO_INTENTOS": "Número de intentos"}
AGRUPACIONES = {"Ninguna": None, "Sexo": "SEXO", "Año": "AÑO", "Grupo de edad": "GRUPO_EDAD",
                "Estrato": "ESTRATO"}


def formatear(valor) -> str:
    """Número con hasta 2 decimales, sin ceros sobrantes ('21.00' -> '21')."""
    if valor is None:
        return "—"
    return f"{valor:,.2f}".rstrip("0").rstrip(".")


with tab_stats:
    st.caption("Estadísticas descriptivas calculadas con NumPy (`src/estadisticas.py`) sobre los "
               "datos filtrados.")
    c_var, c_grupo = st.columns(2)
    variable = c_var.selectbox("Variable numérica", list(VARIABLES_NUMERICAS),
                               format_func=VARIABLES_NUMERICAS.get)
    agrupar = c_grupo.selectbox("Comparar por", list(AGRUPACIONES))
    columna_grupo = AGRUPACIONES[agrupar]

    resumen = resumen_numerico(d[variable])
    claves = ["media", "mediana", "desviacion", "minimo", "maximo", "q1", "q3", "coef_variacion"]
    for fila in (claves[:4], claves[4:]):
        for col, clave in zip(st.columns(4), fila):
            col.metric(NOMBRES_ESTADISTICAS[clave], formatear(resumen[clave]), border=True)
    if resumen["n"] < len(d):
        st.caption(f"Se usan {resumen['n']} de {len(d)} registros; los vacíos se excluyen del cálculo.")

    a, b = st.columns([3, 2])
    with a:
        datos_box = d.dropna(subset=[variable])
        if columna_grupo:
            datos_box = datos_box.assign(**{columna_grupo: datos_box[columna_grupo].astype(str)})
        fig = px.box(datos_box, x=columna_grupo, y=variable, points="outliers",
                     color=columna_grupo if columna_grupo == "SEXO" else None,
                     color_discrete_map=COLOR_SEXO,
                     category_orders={"GRUPO_EDAD": GRUPOS_EDAD})
        if columna_grupo != "SEXO":
            fig.update_traces(marker_color=TEAL, line_color=TEAL)
        fig.update_layout(height=380, margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
                          yaxis_title=VARIABLES_NUMERICAS[variable],
                          xaxis_title=agrupar if columna_grupo else None)
        panel(f"Distribución de {VARIABLES_NUMERICAS[variable].lower()}", renombrar_sexo(fig),
              "la caja va de Q1 a Q3 (la mitad central de los datos), la línea interior es la "
              "mediana y los puntos sueltos son valores atípicos.")
    with b:
        with st.container(border=True):
            st.markdown('<p class="panel-titulo">¿Qué significa cada estadística?</p>',
                        unsafe_allow_html=True)
            st.markdown(
                """
- **Media:** el promedio.
- **Mediana:** el valor del medio; no se deja afectar por extremos.
- **Desviación estándar:** qué tan dispersos están los datos alrededor de la media.
- **Q1 / Q3:** el 25% de los datos está por debajo de Q1 y el 75% por debajo de Q3.
- **Coeficiente de variación:** desviación ÷ media × 100; permite comparar dispersión.
"""
            )
            r = correlacion(d["EDAD"], d["NUMERO_INTENTOS"])
            if r is not None:
                if abs(r) < 0.3:
                    fuerza = "débil: la edad casi no explica cuántos intentos tiene una persona"
                elif abs(r) < 0.7:
                    fuerza = "moderada"
                else:
                    fuerza = "fuerte"
                st.metric("Correlación edad ↔ n.º de intentos", f"{r:.2f}",
                          help="Coeficiente de Pearson con np.corrcoef: va de -1 a 1; "
                               "cerca de 0 = sin relación lineal.")
                st.caption(f"Relación lineal {fuerza}.")

    if columna_grupo:
        tabla_g = resumen_por_grupo(d, variable, columna_grupo)
        if columna_grupo == "SEXO":
            tabla_g["Grupo"] = tabla_g["Grupo"].map(NOMBRE_SEXO)
        if columna_grupo == "GRUPO_EDAD":
            tabla_g["Grupo"] = pd.Categorical(tabla_g["Grupo"], GRUPOS_EDAD, ordered=True)
            tabla_g = tabla_g.sort_values("Grupo")
        with st.container(border=True):
            st.markdown(f'<p class="panel-titulo">Estadísticas por {agrupar.lower()}</p>',
                        unsafe_allow_html=True)
            st.dataframe(tabla_g.rename(columns=NOMBRES_ESTADISTICAS | {"Grupo": agrupar}),
                         hide_index=True, width="stretch")

    st.download_button(
        "Descargar resumen estadístico (JSON)",
        json.dumps(resumen_general(d), ensure_ascii=False, indent=2, default=str).encode("utf-8"),
        file_name="resumen_estadistico.json",
        mime="application/json",
    )

# ------------------------------------------------------------------ datos
with tab_datos:
    tabla = d.drop(columns=["MES", "PERIODO", "GRUPO_EDAD"])
    izq, der = st.columns([3, 1], vertical_alignment="bottom")
    with izq:
        buscar = st.text_input("Buscar en la tabla", placeholder="Ej.: un barrio, escolaridad, estado civil…")
    with der:
        st.download_button(
            "Descargar CSV filtrado",
            tabla.to_csv(index=False).encode("utf-8-sig"),
            file_name="tunja_datos_filtrados.csv",
            mime="text/csv",
            width="stretch",
        )
    if buscar:
        texto = tabla.astype(str).apply(lambda col: col.str.contains(buscar, case=False, regex=False))
        tabla = tabla[texto.any(axis=1)]
    st.caption(f"{len(tabla):,} registros. Haz clic en el encabezado de una columna para ordenar.")
    st.dataframe(
        tabla, width="stretch", height=520, hide_index=True,
        column_config={
            "ID_REGISTRO": st.column_config.NumberColumn("ID", format="%d"),
            "AÑO": st.column_config.NumberColumn("Año", format="%d"),
            "FECHA_NOTIFICACION": st.column_config.DateColumn("Fecha notificación", format="DD/MM/YYYY"),
            "FECHA_HECHO": st.column_config.DateColumn("Fecha del hecho", format="DD/MM/YYYY"),
            "EDAD": st.column_config.NumberColumn("Edad", format="%d años"),
            "NUMERO_INTENTOS": st.column_config.NumberColumn("N.º intentos", format="%d"),
        },
    )
