import pandas as pd
from docx import Document
from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def generar_informes():
    # Obtener el nombre del docente
    nombre_docente = entry_docente.get()
    if not nombre_docente:
        messagebox.showerror("Error", "Por favor, ingrese el nombre del docente.")
        return

    # Obtener las rutas de los archivos
    ruta_estudiantes = entry_estudiantes.get()
    ruta_respuestas_correctas = entry_respuestas.get()
    ruta_plantilla = entry_plantilla.get()

    # Cargar los datos de los estudiantes y respuestas correctas
    try:
        df_estudiantes = pd.read_excel(ruta_estudiantes)
        df_respuestas_correctas = pd.read_excel(ruta_respuestas_correctas)
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer los archivos: {e}")
        return

    # Crear un set para almacenar todas las áreas
    todas_las_areas = set(df_estudiantes['area'])

    # Convertir set en lista ordenada
    lista_areas = sorted(list(todas_las_areas))

    # Obtener la fecha actual
    fecha_generacion = datetime.now().strftime("%Y-%m-%d")

    # Crear una carpeta para los informes
    carpeta_informes = "Informes_Estudiantes"
    os.makedirs(carpeta_informes, exist_ok=True)  # Crea la carpeta si no existe

    # Agrupar por estudiante
    estudiantes_grupo = df_estudiantes.groupby('nombre estudiante')

    # Recorrer cada estudiante y generar un documento individual
    for nombre, grupo_estudiante in estudiantes_grupo:
        # Cargar la plantilla
        documento = Document(ruta_plantilla)

        # Crear un diccionario para almacenar las notas por área del estudiante
        notas_por_area = {area: 'N/A' for area in lista_areas}  # Inicializar con N/A

        # Recorrer cada área en la que el estudiante tiene exámenes
        for index, fila_estudiante in grupo_estudiante.iterrows():
            area = fila_estudiante['area']
            
            # Verificar si el área tiene respuestas correctas
            if not df_respuestas_correctas[df_respuestas_correctas['area'] == area].empty:
                respuestas_correctas = df_respuestas_correctas[df_respuestas_correctas['area'] == area].iloc[0]

                # Contador de respuestas correctas
                respuestas_correctas_contador = 0

                # Comparar respuestas
                for i in range(1, 11):
                    if fila_estudiante[f'pregunta {i}'] == respuestas_correctas[f'pregunta {i}']:
                        respuestas_correctas_contador += 1
                
                # Calcular la nota final sobre 5
                definitiva = (respuestas_correctas_contador / 10) * 5
                # Guardar la nota en el diccionario para el área correspondiente
                notas_por_area[area] = f'{definitiva:.2f}'

        # Reemplazar marcadores en la plantilla
        for paragraph in documento.paragraphs:
            if '{{nombre}}' in paragraph.text:
                paragraph.text = paragraph.text.replace('{{nombre}}', nombre)
            if '{{nombre_docente}}' in paragraph.text:
                paragraph.text = paragraph.text.replace('{{nombre_docente}}', nombre_docente)
            if '{{fecha_generacion}}' in paragraph.text:
                paragraph.text = paragraph.text.replace('{{fecha_generacion}}', fecha_generacion)
            for area in lista_areas:
                if f'{{{{{area}}}}}' in paragraph.text:
                    paragraph.text = paragraph.text.replace(f'{{{{{area}}}}}', notas_por_area[area])

        # Guardar el documento de Word en la carpeta de informes
        documento.save(os.path.join(carpeta_informes, f'informe_{nombre.replace(" ", "_")}.docx'))

    messagebox.showinfo("Éxito", f"Informes generados exitosamente en la carpeta: {carpeta_informes}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Generador de Informes de Estudiantes")

# Etiquetas y entradas
tk.Label(ventana, text="Nombre del Docente:").grid(row=0, column=0, padx=10, pady=10)
entry_docente = tk.Entry(ventana, width=30)
entry_docente.grid(row=0, column=1, padx=10, pady=10)

tk.Label(ventana, text="Archivo de Estudiantes:").grid(row=1, column=0, padx=10, pady=10)
entry_estudiantes = tk.Entry(ventana, width=30)
entry_estudiantes.grid(row=1, column=1, padx=10, pady=10)
tk.Button(ventana, text="Seleccionar", command=lambda: entry_estudiantes.insert(0, filedialog.askopenfilename(title="Seleccionar Archivo de Estudiantes", filetypes=[("Excel files", "*.xlsx")]))).grid(row=1, column=2, padx=10, pady=10)

tk.Label(ventana, text="Archivo de Respuestas Correctas:").grid(row=2, column=0, padx=10, pady=10)
entry_respuestas = tk.Entry(ventana, width=30)
entry_respuestas.grid(row=2, column=1, padx=10, pady=10)
tk.Button(ventana, text="Seleccionar", command=lambda: entry_respuestas.insert(0, filedialog.askopenfilename(title="Seleccionar Archivo de Respuestas Correctas", filetypes=[("Excel files", "*.xlsx")]))).grid(row=2, column=2, padx=10, pady=10)

tk.Label(ventana, text="Archivo de Plantilla:").grid(row=3, column=0, padx=10, pady=10)
entry_plantilla = tk.Entry(ventana, width=30)
entry_plantilla.grid(row=3, column=1, padx=10, pady=10)
tk.Button(ventana, text="Seleccionar", command=lambda: entry_plantilla.insert(0, filedialog.askopenfilename(title="Seleccionar Archivo de Plantilla", filetypes=[("Word files", "*.docx")]))).grid(row=3, column=2, padx=10, pady=10)

# Botón para generar informes
tk.Button(ventana, text="Generar Informes", command=generar_informes).grid(row=4, columnspan=3, padx=10, pady=20)

# Ejecutar la ventana
ventana.mainloop()
