"""Ejecuta la extracción, transformación y carga de datos de energía."""

import argparse
from pathlib import Path

import pandas as pd

from Extract import procesar_datos_energia
from Load import cargar_datos


def main():
    directorio = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--energia", type=Path, default=directorio / "O3-export.csv")
    parser.add_argument(
        "--agricola", type=Path,
        default=directorio / "Agricultura_y_Desarrollo_Rural_-_Evaluación_Agrícola_Departamento_de_Bolívar._20261109.csv",
    )
    parser.add_argument("--base-datos", type=Path, default=directorio / "alumbrado.db")
    parser.add_argument("--tabla", default="energia")
    parser.add_argument(
        "--si-existe", choices=["fail", "append", "replace"], default="fail",
        help="Acción si la tabla existe: fallar, agregar filas o reemplazarla (predeterminado: fail).",
    )
    args = parser.parse_args()

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1500)

    datos = procesar_datos_energia(args.energia, args.agricola)
    print("--- ESTRUCTURA FINAL DE LA TABLA ---")
    datos.info()
    print("\n--- MUESTRA DE DATOS (PRIMERAS 3 FILAS) ---")
    print(datos.head(3))
    nulos_codigos = datos["codigo_oficial"].isnull().sum()
    print(f"\nTotal de municipios sin código oficial (debe ser 0): {nulos_codigos}")

    filas = cargar_datos(datos, args.base_datos, args.tabla, args.si_existe)
    print(f"\nSe cargaron {filas} filas en {args.base_datos}, tabla '{args.tabla}'.")


if __name__ == "__main__":
    main()
