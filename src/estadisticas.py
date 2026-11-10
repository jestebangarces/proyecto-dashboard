"""Cálculos estadísticos con NumPy (requisito R4).

Todas las funciones reciben datos "crudos" (listas, Series o arreglos) y los convierten a
``numpy.ndarray`` para calcular las estadísticas descriptivas.
"""

import numpy as np
import pandas as pd

NOMBRES_ESTADISTICAS = {
    "n": "Registros con dato",
    "media": "Media",
    "mediana": "Mediana",
    "desviacion": "Desviación estándar",
    "minimo": "Mínimo",
    "maximo": "Máximo",
    "rango": "Rango",
    "q1": "Percentil 25 (Q1)",
    "q3": "Percentil 75 (Q3)",
    "rango_intercuartil": "Rango intercuartílico",
    "coef_variacion": "Coef. de variación (%)",
}


def a_arreglo(valores) -> np.ndarray:
    """Convierte una lista/Series en arreglo de NumPy de tipo float sin valores vacíos."""
    arreglo = np.asarray(valores, dtype=float)
    return arreglo[~np.isnan(arreglo)]


def resumen_numerico(valores) -> dict:
    """Calcula 11 estadísticas descriptivas de una variable numérica con NumPy.

    Args:
        valores: lista, Series o arreglo con números (los NaN se ignoran).

    Returns:
        Diccionario con n, media, mediana, desviación estándar muestral, mínimo, máximo,
        rango, Q1, Q3, rango intercuartílico y coeficiente de variación.
        Si no hay datos, todas las estadísticas valen ``None``.
    """
    x = a_arreglo(valores)
    if x.size == 0:
        return {clave: None for clave in NOMBRES_ESTADISTICAS} | {"n": 0}

    media = float(np.mean(x))
    desviacion = float(np.std(x, ddof=1)) if x.size > 1 else 0.0
    q1, q3 = np.percentile(x, [25, 75])
    return {
        "n": int(x.size),
        "media": round(media, 2),
        "mediana": float(np.median(x)),
        "desviacion": round(desviacion, 2),
        "minimo": float(np.min(x)),
        "maximo": float(np.max(x)),
        "rango": float(np.ptp(x)),
        "q1": float(q1),
        "q3": float(q3),
        "rango_intercuartil": float(q3 - q1),
        "coef_variacion": round(desviacion / media * 100, 1) if media else None,
    }


def resumen_por_grupo(datos: pd.DataFrame, variable: str, grupo: str) -> pd.DataFrame:
    """Aplica :func:`resumen_numerico` a cada grupo (bucle sobre los grupos).

    Returns:
        DataFrame con una fila por grupo y una columna por estadística.
    """
    filas = []
    for nombre, sub in datos.groupby(grupo, observed=True):
        fila = {"Grupo": nombre}
        fila.update(resumen_numerico(sub[variable]))
        filas.append(fila)
    return pd.DataFrame(filas)


def variacion_porcentual(conteos) -> np.ndarray:
    """Cambio porcentual entre valores consecutivos: (actual - anterior) / anterior * 100."""
    x = np.asarray(conteos, dtype=float)
    if x.size < 2:
        return np.array([])
    return np.diff(x) / x[:-1] * 100


def correlacion(x, y) -> float | None:
    """Coeficiente de correlación de Pearson entre dos variables (pares sin NaN)."""
    a = np.asarray(x, dtype=float)
    b = np.asarray(y, dtype=float)
    validos = ~(np.isnan(a) | np.isnan(b))
    if validos.sum() < 3:
        return None
    return round(float(np.corrcoef(a[validos], b[validos])[0, 1]), 3)


def proporcion(valores_si_no) -> float:
    """Porcentaje de "SI" en una columna binaria, calculado con un arreglo booleano."""
    arreglo = np.asarray(valores_si_no) == "SI"
    return round(float(np.mean(arreglo) * 100), 1) if arreglo.size else 0.0


def resumen_general(datos: pd.DataFrame) -> dict:
    """Resumen estadístico del dataset completo, pensado para exportar a JSON.

    Incluye edad, número de intentos, casos por año con su variación porcentual,
    proporciones clave y la correlación edad / número de intentos.
    """
    casos_anio = datos.groupby("AÑO").size()
    variacion = variacion_porcentual(casos_anio.values)
    return {
        "registros": int(len(datos)),
        "edad": resumen_numerico(datos["EDAD"]),
        "numero_intentos": resumen_numerico(datos["NUMERO_INTENTOS"]),
        "casos_por_anio": {int(a): int(c) for a, c in casos_anio.items()},
        "variacion_anual_pct": {
            int(anio): round(float(v), 1) for anio, v in zip(casos_anio.index[1:], variacion)
        },
        "porcentaje_mujeres": proporcion(np.where(datos["SEXO"] == "FEMENINO", "SI", "NO")),
        "porcentaje_intentos_previos": proporcion(datos["INTENTOS_PREVIOS"]),
        "porcentaje_ideacion_persistente": proporcion(datos["IDEACION_SUICIDA_PERSISTENTE"]),
        "correlacion_edad_numero_intentos": correlacion(datos["EDAD"], datos["NUMERO_INTENTOS"]),
    }
