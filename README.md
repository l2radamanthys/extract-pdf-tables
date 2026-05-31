# Extractor de tablas de PDF

Este script extrae tablas de un archivo PDF y las guarda en un archivo Excel.

## Requisitos

- Python 3.10 o superior
- uv (para gestionar dependencias)
- PyPDF2
- tabula-py
- openpyxl
- pandas

## Instalación

Instalar las dependencias:

```
uv sync
```

## Uso

Para ejecutar el script, debes tener Python 3.x instalado en tu sistema.

### Procesar archivos PDF en una carpeta:

```
uv run python extract.py './input'
```

### Procesar archivos PDF en una carpeta y guardar en una carpeta diferente:

```
uv run python extract.py './input' -o './salida'
```
