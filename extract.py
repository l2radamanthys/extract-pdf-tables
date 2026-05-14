import tabula
import os
import argparse
import sys
import re
import pandas as pd
from PyPDF2 import PdfReader


def extraer_fecha(archivo_pdf):
    try:
        reader = PdfReader(archivo_pdf)
        texto = ""
        for page in reader.pages:
            texto_pagina = page.extract_text()
            if texto_pagina:
                texto += texto_pagina + "\n"
        
        # Buscar "Fecha de muestreo" seguido por algo y luego una fecha dd/mm/yyyy
        match = re.search(r'Fecha de muestreo.*?(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    except Exception as e:
        print(f"Error extrayendo fecha: {e}")
    return "No encontrada"


def ajustar_ancho_columnas(worksheet):
    for col in worksheet.columns:
        max_length = 0
        column_letter = col[0].column_letter
        for cell in col:
            try:
                if cell.value is not None:
                    # Buscamos el texto más largo considerando posibles saltos de línea
                    longitud_celda = max(len(line) for line in str(cell.value).split('\n'))
                    if longitud_celda > max_length:
                        max_length = longitud_celda
            except:
                pass
        
        # Ajustar el ancho sumando un pequeño padding
        worksheet.column_dimensions[column_letter].width = max_length + 2


def extraer_tablas_pdf(archivo_entrada, carpeta_salida):
    # Crear la carpeta de salida si no existe
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f"Carpeta '{carpeta_salida}' creada.")

    try:
        print(f"Leyendo documento: {archivo_entrada}...")
        
        # Extraer la fecha primero
        fecha = extraer_fecha(archivo_entrada)
        print(f"Fecha de muestreo encontrada: {fecha}")

        # read_pdf devuelve una lista de DataFrames de Pandas
        # pages='all' procesa todo el documento
        # multiple_tables=True permite detectar varias tablas por página
        tablas = tabula.read_pdf(archivo_entrada, pages='all', multiple_tables=True)

        if not tablas:
            print("No se encontraron tablas en el documento.")
            # Incluso si no hay tablas, podríamos querer guardar la fecha, 
            # pero asumimos que el usuario quiere las tablas principalmente.
            return

        # Generar nombre del archivo de salida
        nombre_base = os.path.basename(archivo_entrada)
        nombre_sin_ext = os.path.splitext(nombre_base)[0]
        archivo_salida = os.path.join(carpeta_salida, f"{nombre_sin_ext}.xlsx")

        print(f"Se encontraron {len(tablas)} tablas. Iniciando exportación a {archivo_salida}...")

        # Escribir en un único Excel
        with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
            # 1. Guardar la fecha en la primera hoja
            df_fecha = pd.DataFrame([{"Fecha de muestreo": fecha}])
            df_fecha.to_excel(writer, sheet_name="Fecha", index=False)
            ajustar_ancho_columnas(writer.sheets["Fecha"])

            # 2. Guardar las tablas en las hojas siguientes
            for i, tabla in enumerate(tablas):
                nombre_hoja = f"Tabla_{i+1}"
                tabla.to_excel(writer, sheet_name=nombre_hoja, index=False)
                ajustar_ancho_columnas(writer.sheets[nombre_hoja])

        print("\nProceso finalizado con éxito.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


def procesar_entrada(entrada, carpeta_salida):
    if os.path.isdir(entrada):
        archivos_pdf = [f for f in os.listdir(entrada) if f.lower().endswith('.pdf')]
        if not archivos_pdf:
            print(f"No se encontraron archivos PDF en la carpeta '{entrada}'.")
            return
        
        print(f"Se encontraron {len(archivos_pdf)} archivos PDF en la carpeta '{entrada}'.")
        for archivo in archivos_pdf:
            ruta_pdf = os.path.join(entrada, archivo)
            print("-" * 50)
            extraer_tablas_pdf(ruta_pdf, carpeta_salida)
    elif os.path.isfile(entrada):
        if entrada.lower().endswith('.pdf'):
            extraer_tablas_pdf(entrada, carpeta_salida)
        else:
            print(f"Error: El archivo '{entrada}' no parece ser un archivo PDF.")
    else:
        print(f"Error: La entrada '{entrada}' no es un archivo ni una carpeta válida.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extractor de tablas de archivos PDF o carpetas con PDFs a Excel")
    
    # Argumento obligatorio: ruta del PDF o carpeta
    parser.add_argument("entrada", help="Ruta del archivo PDF o carpeta de PDFs a procesar")
    
    # Argumento opcional: carpeta de salida (por defecto 'output')
    parser.add_argument("-o", "--output", default="output", 
                        help="Carpeta de destino para los archivos Excel (default: output)")

    args = parser.parse_args()

    procesar_entrada(args.entrada, args.output)