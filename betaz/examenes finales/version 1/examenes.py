import os
import random
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def cargar_preguntas_desde_archivos(rutas_archivos):
    """
    Carga preguntas desde una lista de archivos Markdown.

    Args:
        rutas_archivos (list): Una lista de rutas a los archivos .md.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa una pregunta.
    """
    preguntas = []
    for ruta_archivo in rutas_archivos:
        if not os.path.exists(ruta_archivo):
            print(f"Advertencia: El archivo {ruta_archivo} no fue encontrado.")
            continue

        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()

        bloques_preguntas = contenido.split('## ')[1:]

        for bloque in bloques_preguntas:
            lineas = bloque.strip().split('\n')
            pregunta_texto = lineas[0].strip()
            opciones = []
            respuesta_correcta = None

            for linea in lineas[1:]:
                linea = linea.strip()
                if linea.startswith('- '):
                    opcion = linea[2:].strip()
                    if opcion.startswith('*'):
                        opcion = opcion[1:].strip()
                        respuesta_correcta = opcion
                    opciones.append(opcion)

            if pregunta_texto and opciones and respuesta_correcta:
                preguntas.append({
                    'pregunta': pregunta_texto,
                    'opciones': opciones,
                    'respuesta': respuesta_correcta
                })
    return preguntas

def generar_examen(preguntas, numero_de_preguntas):
    """
    Genera un examen a partir de una lista de preguntas.

    Args:
        preguntas (list): La lista de todas las preguntas disponibles.
        numero_de_preguntas (int): El número de preguntas para el examen.

    Returns:
        tuple: Una tupla conteniendo el texto del examen y el texto de la hoja de respuestas.
    """
    # El número de preguntas ya se valida antes de llamar a esta función
    preguntas_seleccionadas = random.sample(preguntas, numero_de_preguntas)

    texto_examen = "EXAMEN\n\n"
    texto_respuestas = "HOJA DE RESPUESTAS\n\n"

    for i, pregunta in enumerate(preguntas_seleccionadas, 1):
        texto_examen += f"{i}. {pregunta['pregunta']}\n"
        opciones_mezcladas = random.sample(pregunta['opciones'], len(pregunta['opciones']))
        for j, opcion in enumerate(opciones_mezcladas, 1):
            texto_examen += f"   {chr(96+j)}) {opcion}\n"
        texto_examen += "\n"
        texto_respuestas += f"{i}. {pregunta['respuesta']}\n"

    return texto_examen, texto_respuestas

def guardar_archivo(nombre_archivo, contenido):
    """
    Guarda contenido en un archivo de texto.

    Args:
        nombre_archivo (str): El nombre del archivo a guardar.
        contenido (str): El contenido a escribir en el archivo.
    """
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)

# --- INICIO DEL PROGRAMA PRINCIPAL CON GUI ---

if __name__ == "__main__":
    # Configurar la ventana raíz de tkinter y ocultarla
    root = tk.Tk()
    root.withdraw()

    # 1. Abrir ventana para seleccionar los archivos de preguntas
    messagebox.showinfo("Generador de Exámenes", "Por favor, selecciona los archivos .md con las preguntas.")
    
    archivos_de_preguntas = filedialog.askopenfilenames(
        title="Selecciona los archivos de preguntas",
        filetypes=[("Archivos Markdown", "*.md"), ("Todos los archivos", "*.*")]
    )

    if not archivos_de_preguntas:
        messagebox.showwarning("Cancelado", "No se seleccionó ningún archivo. El programa se cerrará.")
        exit()

    # 2. Cargar las preguntas desde los archivos seleccionados
    todas_las_preguntas = cargar_preguntas_desde_archivos(archivos_de_preguntas)

    if not todas_las_preguntas:
        messagebox.showerror("Error", "No se encontraron preguntas válidas en los archivos seleccionados.")
        exit()

    # 3. Preguntar al usuario por el número de preguntas
    max_preguntas = len(todas_las_preguntas)
    numero_de_preguntas = simpledialog.askinteger(
        "Número de Preguntas",
        f"¿Cuántas preguntas deseas en el examen? (Máximo: {max_preguntas})",
        initialvalue=min(10, max_preguntas),
        minvalue=1,
        maxvalue=max_preguntas
    )

    if numero_de_preguntas is None:
        messagebox.showwarning("Cancelado", "No se especificó el número de preguntas. El programa se cerrará.")
        exit()
        
    # 4. Generar el examen y la hoja de respuestas
    examen, respuestas = generar_examen(todas_las_preguntas, numero_de_preguntas)

    # 5. Guardar el archivo del examen
    ruta_examen = filedialog.asksaveasfilename(
        title="Guardar el examen como...",
        defaultextension=".txt",
        filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")]
    )

    if ruta_examen:
        guardar_archivo(ruta_examen, examen)
    
        # 6. Guardar el archivo de la hoja de respuestas
        ruta_respuestas = filedialog.asksaveasfilename(
            title="Guardar la hoja de respuestas como...",
            defaultextension=".txt",
            filetypes=[("Archivos de Texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if ruta_respuestas:
            guardar_archivo(ruta_respuestas, respuestas)
            messagebox.showinfo("Éxito", "El examen y la hoja de respuestas han sido generados y guardados correctamente.")
        else:
             messagebox.showwarning("Cancelado", "El examen se guardó, pero la hoja de respuestas no.")
    else:
        messagebox.showwarning("Cancelado", "La operación fue cancelada. No se guardó ningún archivo.")