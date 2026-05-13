import tabula
import os
import argparse
import sys


def extraer_tablas_pdf(archivo_entrada, carpeta_salida):
    # Crear la carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"Carpeta '{carpeta_salida}' creada.")

    try:
        print(f"Leyendo tablas de: {archivo_entrada}...")
        
        # read_pdf devuelve una lista de DataFrames de Pandas
        # pages='all' procesa todo el documento
        # multiple_tables=True permite detectar varias tablas por página
        tablas = tabula.read_pdf(archivo_entrada, pages='all', multiple_tables=True)

        if not tablas:
            print("No se encontraron tablas en el documento.")
            return

        print(f"Se encontraron {len(tablas)} tablas. Iniciando exportación...")

        for i, tabla in enumerate(tablas):
            nombre_archivo = f"tabla_extraida_{i+1}.csv"
            ruta_completa = os.path.join(carpeta_salida, nombre_archivo)
            
            # Exportar cada tabla a CSV
            tabla.to_csv(ruta_completa, index=False, encoding='utf-8-sig')
            print(f"Guardada: {nombre_archivo}")

        print("\nProceso finalizado con éxito.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extractor de tablas de PDF a CSV")
    
    # Argumento obligatorio: ruta del PDF
    parser.add_argument("entrada", help="Ruta del archivo PDF a procesar")
    
    # Argumento opcional: carpeta de salida (por defecto 'output')
    parser.add_argument("-o", "--output", default="output", 
                        help="Carpeta de destino para los CSV (default: output)")

    args = parser.parse_args()

    extraer_tablas_pdf(args.entrada, args.output)