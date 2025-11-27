import pandas as pd
from docx import Document
import tkinter as tk
from tkinter import filedialog
import os

# Initialize tkinter
root = tk.Tk()
root.withdraw()  # Hide the main tkinter window

try:
    # Open file dialog for selecting Excel file
    archivo_excel = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not archivo_excel:
        raise FileNotFoundError("No Excel file selected.")

    # Open file dialog for selecting Word template
    plantilla_word = filedialog.askopenfilename(
        title="Select Word Template",
        filetypes=[("Word files", "*.docx")]
    )
    if not plantilla_word:
        raise FileNotFoundError("No Word template selected.")

    # Define the maximum grade
    nota_maxima = 5.0  # Adjust according to your grading system

    # Read the Excel file
    datos = pd.read_excel(archivo_excel, decimal=',')
    
    # Display the first few rows of the dataframe
    print("Datos leídos:")
    print(datos.head())

    # Assume the grade columns are as follows
    columnas_notas = ['asitencia1', 'tans1', 'bonificacion1', 'taller1', 
                      'comportamiento1', 'autoevaluacion1', 'examen1']

    # Calculate the average per column
    promedios_por_columna = datos[columnas_notas].mean()
    
    # Calculate averages as percentages
    promedios_por_columna_porcentaje = (promedios_por_columna / nota_maxima) * 100

    # Assume the minimum passing grade is 2.9 (adjust as needed)
    nota_minima = 2.9
    estudiantes_aprobados = datos[datos['definitiva'] >= nota_minima]
    estudiantes_reprobados = datos[datos['definitiva'] < nota_minima]

    # Count the number of students who passed and failed
    cantidad_aprobados = estudiantes_aprobados.shape[0]
    cantidad_reprobados = estudiantes_reprobados.shape[0]

    # Prepare the results for the report
    promedios_texto = "\n".join([f"{columna}: {promedio:.2f}%" for columna, promedio in promedios_por_columna_porcentaje.items()])

    # Get lost learning outcomes if there are students who failed
    aprendizajes_perdidos = datos['aprendizaje'].unique() if cantidad_reprobados > 0 else []
    aprendizajes_texto = "\n".join(map(str, aprendizajes_perdidos)) if len(aprendizajes_perdidos) > 0 else "No hay aprendizajes perdidos."

    # Load the Word document template
    doc = Document(plantilla_word)

    # Calculate approval percentage (fixing the formula)
    aprobacionporcentaja = (cantidad_aprobados / (cantidad_aprobados + cantidad_reprobados)) * 100 if (cantidad_aprobados + cantidad_reprobados) > 0 else 0

    # Replace placeholders in the document
    for paragraph in doc.paragraphs:
        if '{{promedios}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{promedios}}', promedios_texto)
        if '{{cantidad_aprobados}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{cantidad_aprobados}}', str(cantidad_aprobados))
        if '{{cantidad_reprobados}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{cantidad_reprobados}}', str(cantidad_reprobados))
        if '{{aprendizajes}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{aprendizajes}}', aprendizajes_texto)
        if '{{aprobacionporcentaja}}' in paragraph.text:
            paragraph.text = paragraph.text.replace('{{aprobacionporcentaja}}', f"{aprobacionporcentaja:.2f}%")

    # Open file dialog for saving the output document
    doc_path = filedialog.asksaveasfilename(
        title="Save Report As",
        defaultextension=".docx",
        filetypes=[("Word files", "*.docx")],
        initialfile="informe_notas.docx"
    )
    if not doc_path:
        raise FileNotFoundError("No save location selected.")

    # Save the document
    doc.save(doc_path)
    print(f"\nInforme guardado en: {doc_path}")

except FileNotFoundError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Ocurrió un error: {e}")
finally:
    root.destroy()  # Clean up tkinter