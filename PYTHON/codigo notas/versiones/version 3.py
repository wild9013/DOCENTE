import pandas as pd
from docx import Document
from docx.shared import Pt
from datetime import datetime
import os

# Cargar los datos de los estudiantes y respuestas correctas
ruta_estudiantes = 'estudiantes.xlsx'
ruta_respuestas_correctas = 'respuestas_correctas.xlsx'
ruta_plantilla = 'plantilla_informe.docx'  # Ruta a tu plantilla

df_estudiantes = pd.read_excel(ruta_estudiantes)
df_respuestas_correctas = pd.read_excel(ruta_respuestas_correctas)

# Crear un set para almacenar todas las áreas
todas_las_areas = set(df_estudiantes['area'])

# Convertir set en lista ordenada
lista_areas = sorted(list(todas_las_areas))

# Obtener la fecha actual
fecha_generacion = datetime.now().strftime("%Y-%m-%d")

# Definir el nombre del docente
nombre_docente = "Nombre del Docente"  # Cambia esto por el nombre real

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
    notas_por_area = {area: '' for area in lista_areas}

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
        else:
            print(f"No se encontraron respuestas correctas para el área: {area}")

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

    # Guardar el documento de Word para el estudiante
    # documento.save(f'informe_{nombre.replace(" ", "_")}.docx')
    documento.save(os.path.join(carpeta_informes, f'informe_{nombre.replace(" ", "_")}.docx'))

print("Informes generados exitosamente.")
