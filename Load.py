"""Carga de los datos transformados en una base de datos SQLite."""

import sqlite3
from pathlib import Path


def cargar_datos(datos, ruta_base_datos, tabla="energia", si_existe="fail"):
    """Guarda el DataFrame y devuelve el número de filas cargadas.

    si_existe admite 'fail', 'append' o 'replace'. Por defecto, evita
    modificar una tabla existente accidentalmente.
    """
    if si_existe not in {"fail", "append", "replace"}:
        raise ValueError("si_existe debe ser 'fail', 'append' o 'replace'.")

    ruta = Path(ruta_base_datos)
    with sqlite3.connect(str(ruta)) as conexion:
        datos.to_sql(tabla, conexion, if_exists=si_existe, index=False)

    return len(datos)
