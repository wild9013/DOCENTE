import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Diccionario que mapea extensiones a nombres de carpetas
EXTENSIONES_MAP = {
    # Documentos
    ".pdf": "Documentos PDF",
    ".docx": "Documentos de Word",
    ".doc": "Documentos de Word",
    ".txt": "Documentos de Texto",
    ".pptx": "Presentaciones",
    ".xlsx": "Hojas de Cálculo",
    ".csv": "Archivos CSV",
    ".json": "Archivos JSON",
    ".md": "Documentos Markdown",

    # Imágenes
    ".jpg": "Imágenes",
    ".jpeg": "Imágenes",
    ".png": "Imágenes",
    ".gif": "Imágenes",
    ".bmp": "Imágenes",
    ".svg": "Imágenes",

    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",

    # Video
    ".mp4": "Videos",
    ".mov": "Videos",
    ".avi": "Videos",
    ".mkv": "Videos",

    # Comprimidos
    ".zip": "Archivos Comprimidos",
    ".rar": "Archivos Comprimidos",
    ".7z": "Archivos Comprimidos",

    # Ejecutables e Instaladores
    ".exe": "Ejecutables",
    ".msi": "Instaladores",

    # Otros
    ".iso": "Imágenes de Disco",
    ".ini": "Archivos de Configuración",
}

def organizar_archivos(directorio):
    """
    Organiza los archivos en el directorio especificado,
    moviéndolos a carpetas según su extensión.
    """
    print(f"Organizando archivos en: {directorio}")
    
    # Obtener la lista de archivos en el directorio
    archivos = [f for f in os.listdir(directorio) if os.path.isfile(os.path.join(directorio, f))]

    for archivo in archivos:
        # Ignorar el propio script
        if archivo == os.path.basename(__file__) or archivo.endswith(".exe"):
            continue

        # Obtener la extensión del archivo
        nombre, extension = os.path.splitext(archivo)
        extension = extension.lower()

        # Determinar la carpeta de destino
        carpeta_destino = EXTENSIONES_MAP.get(extension, "Otros")

        # Crear la carpeta de destino si no existe
        ruta_carpeta_destino = os.path.join(directorio, carpeta_destino)
        if not os.path.exists(ruta_carpeta_destino):
            os.makedirs(ruta_carpeta_destino)
            print(f"Carpeta creada: {carpeta_destino}")

        # Mover el archivo
        ruta_origen = os.path.join(directorio, archivo)
        ruta_destino = os.path.join(ruta_carpeta_destino, archivo)
        
        try:
            shutil.move(ruta_origen, ruta_destino)
            print(f"Movido: {archivo} -> {carpeta_destino}")
        except Exception as e:
            print(f"No se pudo mover {archivo}. Error: {e}")

def seleccionar_carpeta():
    """Muestra un diálogo para seleccionar la carpeta a organizar"""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal
    
    # Mostrar el diálogo para seleccionar carpeta
    carpeta = filedialog.askdirectory(
        title="Seleccione la carpeta a organizar",
        initialdir=os.path.expanduser("~")  # Comenzar en el directorio de usuario
    )
    
    if not carpeta:  # Si el usuario cancela
        print("Operación cancelada por el usuario.")
        return None
    
    return carpeta

if __name__ == "__main__":
    # Solicitar la carpeta a organizar mediante interfaz gráfica
    directorio_a_organizar = seleccionar_carpeta()
    
    if directorio_a_organizar:
        # Organizar los archivos
        organizar_archivos(directorio_a_organizar)
        
        # Mostrar mensaje de finalización
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Organización completada",
            f"Se han organizado los archivos en:\n{directorio_a_organizar}"
        )