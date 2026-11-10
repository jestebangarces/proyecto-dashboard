"""Genera los reportes JSON del proyecto (calidad de datos + resumen estadístico).

Uso:
    python reporte.py

Crea en la carpeta ``salidas/``:
    * ``reporte_calidad.json``   -> validación hecha con Python puro (csv, listas, dicts, sets).
    * ``resumen_estadistico.json`` -> estadísticas descriptivas calculadas con NumPy.
"""

from src.datos import (
    cargar_datos, contar_por, guardar_json, leer_csv_nativo, meses_faltantes, validar_registros,
)
from src.estadisticas import NOMBRES_ESTADISTICAS, resumen_general


def main() -> None:
    """Ejecuta la validación, calcula el resumen y guarda ambos archivos JSON."""
    registros = leer_csv_nativo()
    calidad = validar_registros(registros)
    calidad["casos_por_sexo"] = contar_por(registros, "SEXO")
    calidad["casos_por_anio"] = contar_por(registros, "AÑO")

    df = cargar_datos()
    calidad["meses_sin_notificaciones"] = meses_faltantes(df)
    ruta_calidad = guardar_json(calidad, "reporte_calidad.json")

    resumen = resumen_general(df)
    ruta_resumen = guardar_json(resumen, "resumen_estadistico.json")

    print(f"Registros: {calidad['total_registros']} | Variables: {calidad['total_variables']}")
    print(f"Cumple R1 (>=100 registros y >=5 variables): {calidad['cumple_minimo_R1']}")
    print("\nEdad:")
    for clave, valor in resumen["edad"].items():
        print(f"  {NOMBRES_ESTADISTICAS[clave]:<30} {valor}")
    print(f"\nArchivos creados:\n  {ruta_calidad}\n  {ruta_resumen}")


if __name__ == "__main__":
    main()
