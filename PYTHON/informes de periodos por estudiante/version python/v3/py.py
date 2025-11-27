import pandas as pd
from datetime import datetime
from docxtpl import DocxTemplate, InlineImage
import matplotlib.pyplot as plt
from docx.shared import Inches
import io
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

# --- FUNCIONES DE INTERFAZ GRÁFICA ---
def seleccionar_plantilla():
    root = tk.Tk()
    root.withdraw() # Ocultar ventana principal
    root.attributes('-topmost', True)
    
    archivo = filedialog.askopenfilename(
        title="Selecciona la PLANTILLA Word (.docx)",
        filetypes=[("Documentos Word", "*.docx")]
    )
    if not archivo:
        messagebox.showwarning("Advertencia", "No seleccionaste ninguna plantilla. El programa se cerrará.")
        sys.exit()
    return archivo

def seleccionar_carpeta_destino():
    root = tk.Tk()
    root.withdraw()
    carpeta = filedialog.askdirectory(title="Selecciona dónde GUARDAR los informes")
    if not carpeta:
        return os.getcwd() # Si cancela, usa la carpeta actual
    return carpeta

# --- CONFIGURACIÓN INICIAL ---

# 1. Seleccionar la plantilla gráficamente
ruta_plantilla = seleccionar_plantilla()

# 2. Seleccionar dónde guardar
carpeta_salida = seleccionar_carpeta_destino()
print(f"Los archivos se guardarán en: {carpeta_salida}")

# Datos generales
nombre_docente = "Wilder Salas Mena"
fecha = datetime.today().strftime("%d/%m/%Y")

constantes = {
    "nombre": nombre_docente,
    "fecha": fecha
}

porcentajes = {
    "asistenciaP": "10%",
    "trasnP": "15%",
    "bonificacionP": "0%",
    "tallerP": "40%",
    "comportamientoP": "5%",
    "autoevaluacionP": "5%",
    "examenP": "25%",
}

# --- PROCESAMIENTO DE DATOS ---

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7DifwDwqGwxZr79KAAqeihjNbEbT3YeNGaYJgNsS4FKPu_QUWEcj3Y3gY-9xTZrxvoVEnMt4aK2mw/pub?gid=271012679&single=true&output=csv"

print("Descargando datos de Google Sheets...")
try:
    df2 = pd.read_csv(url)
except Exception as e:
    messagebox.showerror("Error de Conexión", f"No se pudo descargar el archivo CSV:\n{e}")
    sys.exit()

# Función de limpieza (Mantenida de tu código)
def convertir_a_float(valor):
    if pd.isna(valor) or valor == '':
        return 0.0
    # Convierte "4,5" a "4.5" y luego a float
    valor_str = str(valor).replace(',', '.')
    try:
        return float(valor_str)
    except ValueError:
        return 0.0

print(f"Procesando {len(df2)} registros...")

# --- CICLO PRINCIPAL ---
for indice, fila in df2.iterrows():
    
    # 1. Verificar palabra de control para detener
    if fila.astype(str).str.contains('CONTROL', case=False).any():
        print(f"--- Deteniendo: Palabra 'CONTROL' encontrada en fila {indice} ---")
        break 

    nombre_estudiante = fila["Nombre Completo"]
    print(f"Generando informe para: {nombre_estudiante}")

    # 2. CARGAR LA PLANTILLA (¡IMPORTANTE: HACERLO DENTRO DEL CICLO!)
    # Si lo haces fuera, las variables se sobrescriben y fallan los siguientes estudiantes
    doc = DocxTemplate(ruta_plantilla)

    contenido = {
        "nombre1": nombre_estudiante,
        "nota1": fila["asistencia1"],
        "nota2": fila["trasn1"],
        "nota3": fila["bonificacion1"],
        "nota4": fila["taller1"],
        "nota5": fila["comportamiento1"],
        "nota6": fila["autoevaluacion1"],
        "nota7": fila["examen1"],
        "nota8": fila["DEFINITIVA"],
        "Observaciones": fila["Observaciones"]
    }
    contenido.update(constantes)
    contenido.update(porcentajes)

    # 3. PREPARAR DATOS GRÁFICOS
    notas_raw = [
        fila["asistencia1"], fila["trasn1"], fila["bonificacion1"],
        fila["taller1"], fila["comportamiento1"], fila["autoevaluacion1"],
        fila["examen1"]
    ]
    
    notas = [convertir_a_float(x) for x in notas_raw]
    
    etiquetas = ["Asis", "Trans", "Boni", "Tall", "Comp", "Autoe", "Exa"]
    
    # Configuración matemática del radar chart
    num_vars = len(etiquetas)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    # Cerrar el círculo del gráfico
    notas_grafico = notas + [notas[0]]
    angles_grafico = angles + [angles[0]]

    # 4. GENERAR GRÁFICO CON MATPLOTLIB
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    
    # Ajustar el rango del gráfico (0 a 5.0 siempre, para que sea visualmente comparable)
    ax.set_ylim(0, 5)
    
    ax.fill(angles_grafico, notas_grafico, color='skyblue', alpha=0.4)
    ax.plot(angles_grafico, notas_grafico, color='blue', linewidth=2)

    ax.set_yticklabels([]) # Quitar etiquetas numéricas radiales para limpieza visual
    ax.set_xticks(angles)
    ax.set_xticklabels(etiquetas)
    plt.title('Desempeño Integral', y=1.08)

    # Guardar en memoria
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', bbox_inches='tight')
    plt.close(fig) # Importante: cerrar la figura para liberar memoria RAM
    img_stream.seek(0)

    # 5. INSERTAR ETIQUETA DE IMAGEN
    imagen = InlineImage(doc, img_stream, width=Inches(2.5))
    contenido["grafico"] = imagen

    # 6. RENDERIZAR Y GUARDAR
    try:
        doc.render(contenido)
        
        # Limpiar nombre de archivo (quitar caracteres prohibidos)
        nombre_archivo = "".join([c for c in nombre_estudiante if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        ruta_final = os.path.join(carpeta_salida, f"{nombre_archivo}_INFORME.docx")
        
        doc.save(ruta_final)
    except Exception as e:
        print(f"Error al guardar el archivo de {nombre_estudiante}: {e}")

print("\n¡Proceso finalizado con éxito!")
messagebox.showinfo("Éxito", "Se han generado todos los informes correctamente.")