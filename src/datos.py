"""Carga, validación y estructuración de los datos.

Este módulo reúne lo trabajado en Lógica Computacional:

* lectura y escritura de archivos CSV y JSON,
* colecciones nativas de Python (listas, diccionarios, sets, tuplas),
* estructuras de control (condicionales y bucles),
* funciones modulares y documentadas.

pandas se usa solo donde simplifica el trabajo (carga final para el dashboard).
"""

import csv
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DATOS = RAIZ / "data" / "Tunja_intentos_datos_limpios.csv"
CARPETA_SALIDAS = RAIZ / "salidas"

# --------------------------------------------------------------------------- catálogos
GRUPOS_EDAD = [
    "Niñez (6-11)", "Adolescencia (12-17)", "Juventud (18-28)", "Adultez (29-59)", "Mayores (60+)",
]

FACTORES = [
    "PROBLEMAS_FAMILIARES", "CONFLICTO_CON_PAREJA_O_EX_PAREJA", "ESCOLAR_EDUCATIVA",
    "PROBLEMAS_ECONOMICOS", "MALTRATO_FISICO_SICOLOGICO_SEXUAL", "PROBLEMAS_LABORALES",
    "MUERTE_DE_UN_FAMILIAR", "ENFERMEDAD_CRONICA_DOLOROSA_O_DISCAPACITANTE",
    "SUICIDIO_DE_UN_FAMILIAR", "PROBLEMAS_JURIDICOS",
]
ANTECEDENTES = [
    "ANTECEDENTE_TRASTORNO_PSIQUIATRICO", "TRASTORNO_DEPRESIVO", "TRASTORNO_DE_PERSONALIDAD",
    "TRASTORNO_BIPOLAR", "ESQUIZOFRENIA", "CONSUMO_DE_SPA", "ABUSO_DE_ALCOHOL",
    "ANTECEDENTE_VIOLENCIA_O_ABUSO", "ANTECEDENTES_FAMILIARES_DE_CONDUCTA_SUICIDA",
]
MECANISMOS = [
    "INTOXICACIONES", "ARMA_CORTOPUNZANTE", "AHORCAMIENTO", "LANZAMIENTO_A_VEHICULO",
    "LANZAMIENTO_AL_VACIO", "ARMA_DE_FUEGO", "INMOLACION", "LANZAMIENTO_AL_AGUA",
]
REMISIONES = ["REMITIDO_A_PSIQUIATRIA", "REMITIDO_A_PSICOLOGIA", "REMITIDO_A_TRABAJO_SOCIAL"]
SENALES = ["IDEACION_SUICIDA_PERSISTENTE", "PLAN_ORGANIZADO_DE_SUICIDIO", "INTENTOS_PREVIOS"]

# Columnas binarias y los valores que admiten (tupla y set: no deben modificarse)
COLUMNAS_SI_NO = tuple(FACTORES + ANTECEDENTES + MECANISMOS + REMISIONES + SENALES)
VALORES_VALIDOS = {"SI", "NO", "NO APLICA"}

ETIQUETAS = {
    "CONFLICTO_CON_PAREJA_O_EX_PAREJA": "Conflicto con pareja o ex pareja",
    "ESCOLAR_EDUCATIVA": "Problemas escolares / educativos",
    "MALTRATO_FISICO_SICOLOGICO_SEXUAL": "Maltrato físico, psicológico o sexual",
    "ENFERMEDAD_CRONICA_DOLOROSA_O_DISCAPACITANTE": "Enfermedad crónica, dolorosa o discapacitante",
    "ANTECEDENTE_TRASTORNO_PSIQUIATRICO": "Antecedente de trastorno psiquiátrico",
    "ANTECEDENTES_FAMILIARES_DE_CONDUCTA_SUICIDA": "Antecedentes familiares de conducta suicida",
    "ANTECEDENTE_VIOLENCIA_O_ABUSO": "Antecedente de violencia o abuso",
    "CONSUMO_DE_SPA": "Consumo de sustancias psicoactivas",
    "ARMA_CORTOPUNZANTE": "Arma cortopunzante",
    "LANZAMIENTO_A_VEHICULO": "Lanzamiento a vehículo",
    "LANZAMIENTO_AL_VACIO": "Lanzamiento al vacío",
    "INMOLACION": "Inmolación",
    "REMITIDO_A_PSIQUIATRIA": "Psiquiatría",
    "REMITIDO_A_PSICOLOGIA": "Psicología",
    "REMITIDO_A_TRABAJO_SOCIAL": "Trabajo social",
    "IDEACION_SUICIDA_PERSISTENTE": "Ideación suicida persistente",
    "PLAN_ORGANIZADO_DE_SUICIDIO": "Plan organizado de suicidio",
    "INTENTOS_PREVIOS": "Intentos previos",
}


def etiqueta(columna: str) -> str:
    """Devuelve un nombre legible para una columna del dataset.

    Args:
        columna: nombre técnico, p. ej. ``"CONSUMO_DE_SPA"``.

    Returns:
        Texto para mostrar, p. ej. ``"Consumo de sustancias psicoactivas"``.
    """
    if columna in ETIQUETAS:
        return ETIQUETAS[columna]
    return columna.replace("_", " ").capitalize()


def clasificar_edad(edad: float) -> str:
    """Asigna una etapa del ciclo de vida a una edad (estructura condicional).

    Args:
        edad: edad en años.

    Returns:
        Uno de los valores de ``GRUPOS_EDAD`` o ``"Sin dato"``.
    """
    if edad is None or pd.isna(edad):
        return "Sin dato"
    if edad <= 11:
        return GRUPOS_EDAD[0]
    elif edad <= 17:
        return GRUPOS_EDAD[1]
    elif edad <= 28:
        return GRUPOS_EDAD[2]
    elif edad <= 59:
        return GRUPOS_EDAD[3]
    else:
        return GRUPOS_EDAD[4]


# --------------------------------------------------------------------------- Python "puro"
def leer_csv_nativo(ruta: Path = RUTA_DATOS) -> list[dict]:
    """Lee el CSV con el módulo ``csv`` y devuelve una lista de diccionarios.

    Cada diccionario es un registro: ``{"ID_REGISTRO": "1", "EDAD": "27", ...}``.
    """
    registros = []
    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            registros.append(fila)
    return registros


def contar_por(registros: list[dict], columna: str) -> dict:
    """Cuenta cuántos registros hay por cada valor de una columna usando un bucle.

    Returns:
        Diccionario ``{valor: cantidad}`` ordenado de mayor a menor.
    """
    conteo = {}
    for fila in registros:
        valor = fila.get(columna, "")
        conteo[valor] = conteo.get(valor, 0) + 1
    return dict(sorted(conteo.items(), key=lambda par: par[1], reverse=True))


def validar_registros(registros: list[dict]) -> dict:
    """Revisa la calidad del dataset recorriendo cada registro.

    Comprueba:
        * IDs duplicados (con un ``set``),
        * edades vacías o fuera del rango 0-110,
        * valores distintos de SI / NO / NO APLICA en las columnas binarias,
        * cuántas veces aparece "NO APLICA" en cada columna binaria,
        * celdas vacías por columna,
        * fechas del hecho posteriores a la notificación.

    Returns:
        Diccionario con el resumen de problemas encontrados (listo para guardar en JSON).
    """
    ids_vistos = set()
    duplicados = []
    edades_invalidas = []
    valores_no_validos = {}
    no_aplica = {}
    vacios = {}
    fechas_inconsistentes = 0

    for fila in registros:
        id_registro = fila["ID_REGISTRO"]
        if id_registro in ids_vistos:
            duplicados.append(id_registro)
        ids_vistos.add(id_registro)

        try:
            edad = float(fila["EDAD"])
            if edad < 0 or edad > 110:
                edades_invalidas.append(id_registro)
        except ValueError:
            edades_invalidas.append(id_registro)

        for columna, valor in fila.items():
            if valor.strip() == "":
                vacios[columna] = vacios.get(columna, 0) + 1
            elif columna in COLUMNAS_SI_NO:
                if valor not in VALORES_VALIDOS:
                    valores_no_validos[columna] = valores_no_validos.get(columna, 0) + 1
                elif valor == "NO APLICA":
                    no_aplica[columna] = no_aplica.get(columna, 0) + 1

        # Las fechas ISO (AAAA-MM-DD) se pueden comparar como texto
        if fila["FECHA_HECHO"] > fila["FECHA_NOTIFICACION"]:
            fechas_inconsistentes += 1

    total = len(registros)
    return {
        "total_registros": total,
        "total_variables": len(registros[0]) if registros else 0,
        "ids_duplicados": duplicados,
        "edades_invalidas": edades_invalidas,
        "celdas_vacias_por_columna": vacios,
        "porcentaje_vacio_por_columna": {c: round(n / total * 100, 1) for c, n in vacios.items()},
        "valores_no_validos_si_no": valores_no_validos,
        "no_aplica_por_columna": no_aplica,
        "fechas_hecho_posteriores_a_notificacion": fechas_inconsistentes,
        "cumple_minimo_R1": total >= 100 and (len(registros[0]) if registros else 0) >= 5,
    }


def guardar_json(datos: dict, nombre_archivo: str, carpeta: Path = CARPETA_SALIDAS) -> Path:
    """Guarda un diccionario como archivo JSON legible (UTF-8, con sangría).

    Returns:
        Ruta del archivo creado.
    """
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre_archivo
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2, default=str)
    return ruta


def leer_json(ruta: Path) -> dict:
    """Lee un archivo JSON y lo devuelve como diccionario."""
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


# --------------------------------------------------------------------------- pandas
def cargar_datos(origen=RUTA_DATOS) -> pd.DataFrame:
    """Carga el CSV limpio con pandas y agrega columnas derivadas.

    Columnas agregadas:
        * ``MES``: mes de notificación (1-12).
        * ``PERIODO``: primer día del mes de notificación (para series de tiempo).
        * ``GRUPO_EDAD``: etapa de vida calculada con :func:`clasificar_edad`.

    Args:
        origen: ruta al CSV o archivo subido por el usuario.
    """
    df = pd.read_csv(origen, parse_dates=["FECHA_NOTIFICACION", "FECHA_HECHO"])
    df = df.rename(columns={"ANIO": "AÑO"})  # algunas versiones del CSV usan ANIO
    df["MES"] = df["FECHA_NOTIFICACION"].dt.month
    df["PERIODO"] = df["FECHA_NOTIFICACION"].dt.to_period("M").dt.to_timestamp()
    df["GRUPO_EDAD"] = df["EDAD"].map(clasificar_edad)
    return df


def pct_si(datos: pd.DataFrame, columnas: list[str], por: str | None = None) -> pd.DataFrame:
    """Porcentaje de registros con "SI" en cada columna, opcionalmente por grupo.

    Args:
        datos: DataFrame filtrado.
        columnas: columnas binarias SI/NO a resumir.
        por: columna de agrupación (p. ej. ``"SEXO"``) o ``None``.

    Returns:
        DataFrame con columnas ``Variable``, ``Grupo``, ``Porcentaje`` y ``Casos``.
    """
    filas = []
    grupos = [(None, datos)] if por is None else datos.groupby(por, observed=True)
    for nombre, sub in grupos:
        for columna in columnas:
            casos = int((sub[columna] == "SI").sum())
            filas.append({
                "Variable": etiqueta(columna),
                "Grupo": nombre,
                "Porcentaje": casos / len(sub) * 100 if len(sub) else 0,
                "Casos": casos,
            })
    return pd.DataFrame(filas)


def meses_faltantes(datos: pd.DataFrame) -> dict[int, list[int]]:
    """Meses (1-12) sin ninguna notificación en cada año.

    Returns:
        Diccionario ``{año: [meses sin datos]}``; la lista está vacía si el año está completo.
    """
    faltantes = {}
    for anio, sub in datos.groupby("AÑO"):
        presentes = set(sub["MES"])
        faltantes[int(anio)] = [mes for mes in range(1, 13) if mes not in presentes]
    return faltantes


def anios_completos(datos: pd.DataFrame) -> list[int]:
    """Años con notificaciones en los 12 meses (para comparar años sin sesgo)."""
    return [anio for anio, meses in meses_faltantes(datos).items() if not meses]
