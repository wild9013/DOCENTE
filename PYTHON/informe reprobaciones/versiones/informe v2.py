import pandas as pd
from docx import Document

# Cambia la ruta al archivo Excel y la plantilla de Word a las ubicaciones correctas
archivo_excel = 'C:/Users/swild/Desktop/python/datos.xlsx'
plantilla_word = 'C:/Users/swild/Desktop/python/plantilla_informe.docx'

try:
    # Leer el archivo Excel
    datos = pd.read_excel(archivo_excel, decimal=',')

    # Mostrar las primeras filas del dataframe
    print("Datos leídos:")
    print(datos.head())

    # Asumimos que las columnas de notas son las siguientes
    columnas_notas = ['asitencia1', 'tans1', 'bonificacion1', 'taller1', 
                      'comportamiento1', 'autoevaluacion1', 'examen1']

    # Calcular el promedio por columna
    promedios_por_columna = datos[columnas_notas].mean()

    # Suponemos que la nota mínima para aprobar es 10 (ajusta según tus criterios)
    nota_minima = 3
    estudiantes_aprobados = datos[datos['definitiva'] >= nota_minima]
    estudiantes_reprobados = datos[datos['definitiva'] < nota_minima]

    # Contar la cantidad de estudiantes aprobados y reprobados
    cantidad_aprobados = estudiantes_aprobados.shape[0]
    cantidad_reprobados = estudiantes_reprobados.shape[0]

    # Preparar los resultados para el informe
    promedios_texto = "\n".join([f"{columna}: {promedio:.2f}" for columna, promedio in promedios_por_columna.items()])
    
    # Solo obtenemos aprendizajes perdidos si hay estudiantes reprobados
    aprendizajes_perdidos = datos['aprendizaje'].unique() if cantidad_reprobados > 0 else []
    aprendizajes_texto = "\n".join(aprendizajes_perdidos) if aprendizajes_perdidos.size > 0 else "No hay aprendizajes perdidos."

    # Crear el documento a partir de la plantilla
    doc = Document(plantilla_word)

    # Reemplazar los marcadores de posición
    for paragraph in doc.paragraphs:
        if '{{promedios}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{promedios}}', promedios_texto)
        if '{{cantidad_aprobados}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{cantidad_aprobados}}', str(cantidad_aprobados))
        if '{{cantidad_reprobados}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{cantidad_reprobados}}', str(cantidad_reprobados))
        if '{{aprendizajes}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{aprendizajes}}', aprendizajes_texto)

    # Guardar el documento
    doc_path = 'C:/Users/swild/Desktop/python/informe_notas.docx'
    doc.save(doc_path)
    print(f"\nInforme guardado en: {doc_path}")

except FileNotFoundError:
    print(f"Error: El archivo no se encontró en la ruta especificada.")
except Exception as e:
    print(f"Ocurrió un error: {e}")
