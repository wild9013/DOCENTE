import os
import random
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from fpdf import FPDF # Importar la nueva biblioteca

def cargar_preguntas_desde_archivos(rutas_archivos):
    """
    Carga preguntas desde una lista de archivos Markdown.
    (Esta función no cambia)
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
    (Esta función no cambia)
    """
    preguntas_seleccionadas = random.sample(preguntas, numero_de_preguntas)

    texto_examen = ""
    texto_respuestas = ""

    for i, pregunta in enumerate(preguntas_seleccionadas, 1):
        texto_examen += f"{i}. {pregunta['pregunta']}\n"
        opciones_mezcladas = random.sample(pregunta['opciones'], len(pregunta['opciones']))
        for j, opcion in enumerate(opciones_mezcladas, 1):
            texto_examen += f"   {chr(96+j)}) {opcion}\n"
        texto_examen += "\n"
        texto_respuestas += f"{i}. {pregunta['respuesta']}\n"

    return texto_examen, texto_respuestas

def guardar_como_pdf(nombre_archivo, titulo, contenido):
    """
    Guarda el contenido en un archivo PDF.

    Args:
        nombre_archivo (str): La ruta completa para guardar el archivo PDF.
        titulo (str): El título del documento (ej. "EXAMEN").
        contenido (str): El cuerpo del texto a incluir en el PDF.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Establecer la fuente. 'Arial' es estándar, 'B' es negrita, 16 es el tamaño.
    pdf.set_font('Arial', 'B', 16)
    # Crear una celda para el título. w=0 significa ancho completo. ln=1 significa salto de línea. 'C' es centrado.
    pdf.cell(0, 10, titulo, ln=1, align='C')
    pdf.ln(10) # Añadir un espacio vertical de 10 unidades

    # Establecer la fuente para el cuerpo del texto
    pdf.set_font('Arial', '', 12)
    # Usamos multi_cell para manejar automáticamente los saltos de línea del texto.
    # Es importante decodificar el texto para manejar caracteres especiales (tildes, ñ).
    pdf.multi_cell(0, 7, contenido.encode('latin-1', 'replace').decode('latin-1'))
    
    try:
        pdf.output(nombre_archivo)
    except Exception as e:
        messagebox.showerror("Error al Guardar PDF", f"No se pudo guardar el archivo PDF.\nError: {e}")


# --- INICIO DEL PROGRAMA PRINCIPAL CON GUI Y GENERACIÓN DE PDF ---

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

    # 2. Cargar las preguntas
    todas_las_preguntas = cargar_preguntas_desde_archivos(archivos_de_preguntas)

    if not todas_las_preguntas:
        messagebox.showerror("Error", "No se encontraron preguntas válidas en los archivos seleccionados.")
        exit()

    # 3. Preguntar por el número de preguntas
    max_preguntas = len(todas_las_preguntas)
    numero_de_preguntas = simpledialog.askinteger(
        "Número de Preguntas",
        f"¿Cuántas preguntas deseas en el examen? (Máximo: {max_preguntas})",
        initialvalue=min(10, max_preguntas),
        minvalue=1,
        maxvalue=max_preguntas
    )

    if numero_de_preguntas is None:
        messagebox.showwarning("Cancelado", "Operación cancelada.")
        exit()
        
    # 4. Generar el contenido del examen y las respuestas
    examen_texto, respuestas_texto = generar_examen(todas_las_preguntas, numero_de_preguntas)

    # 5. Guardar el archivo del examen en PDF
    ruta_examen = filedialog.asksaveasfilename(
        title="Guardar el examen como...",
        defaultextension=".pdf",
        filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
    )

    if ruta_examen:
        guardar_como_pdf(ruta_examen, "EXAMEN", examen_texto)
    
        # 6. Guardar la hoja de respuestas en PDF
        ruta_respuestas = filedialog.asksaveasfilename(
            title="Guardar la hoja de respuestas como...",
            defaultextension=".pdf",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")]
        )
        if ruta_respuestas:
            guardar_como_pdf(ruta_respuestas, "HOJA DE RESPUESTAS", respuestas_texto)
            messagebox.showinfo("Éxito", "El examen y la hoja de respuestas han sido generados y guardados en formato PDF.")
        else:
             messagebox.showwarning("Cancelado", "El examen se guardó, pero la hoja de respuestas no.")
    else:
        messagebox.showwarning("Cancelado", "La operación fue cancelada. No se guardó ningún archivo.")