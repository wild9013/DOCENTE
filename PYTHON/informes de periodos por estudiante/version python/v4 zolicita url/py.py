import pandas as pd
from datetime import datetime
from docxtpl import DocxTemplate, InlineImage
import matplotlib.pyplot as plt
from docx.shared import Inches
import io
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys

# --- FUNCIONES DE INTERFAZ Y VALIDACIÓN ---

def solicitar_y_validar_url():
    """Solicita la URL y verifica que sea un CSV legible antes de continuar."""
    root = tk.Tk()
    root.withdraw() # Ocultar ventana principal
    
    while True:
        url = simpledialog.askstring(
            "Paso 1: Fuente de Datos", 
            "Por favor, pega la URL del CSV de Google Sheets:\n\n(Asegúrate de que termine en 'output=csv' o sea un enlace de descarga directa)"
        )
        
        # Si el usuario presiona Cancelar o cierra la ventana
        if url is None:
            return None

        if not url.strip():
            messagebox.showwarning("Aviso", "La URL no puede estar vacía.")
            continue

        try:
            # VALIDACIÓN: Intentamos leer solo 1 fila para ver si el link funciona
            # Esto evita esperar a descargar todo si el link está roto
            pd.read_csv(url, nrows=1)
            return url # Si no falla, retornamos la URL válida
        except Exception as e:
            respuesta = messagebox.askretrycancel(
                "Error de Enlace", 
                f"No se pudo leer el archivo de la URL proporcionada.\n\nPosibles causas:\n1. El enlace no es público.\n2. No es formato CSV.\n3. No hay internet.\n\nError técnico: {e}\n\n¿Quieres intentar otra vez?"
            )
            if not respuesta:
                return None

def seleccionar_plantilla():
    """Abre buscador para elegir el Word"""
    archivo = filedialog.askopenfilename(
        title="Paso 2: Selecciona la PLANTILLA Word (.docx)",
        filetypes=[("Documentos Word", "*.docx")]
    )
    return archivo

def seleccionar_carpeta_destino():
    """Abre buscador para elegir dónde guardar"""
    carpeta = filedialog.askdirectory(title="Paso 3: Selecciona dónde GUARDAR los informes")
    return carpeta

# --- CONFIGURACIÓN E INICIO ---

def main():
    # 1. SOLICITAR URL (Con validación previa)
    print("Solicitando URL...")
    url = solicitar_y_validar_url()
    
    if not url:
        print("Proceso cancelado por el usuario en la selección de URL.")
        sys.exit()

    # 2. SELECCIONAR PLANTILLA
    ruta_plantilla = seleccionar_plantilla()
    if not ruta_plantilla:
        print("Proceso cancelado: Sin plantilla.")
        sys.exit()

    # 3. SELECCIONAR CARPETA DE SALIDA
    carpeta_salida = seleccionar_carpeta_destino()
    if not carpeta_salida:
        print("Proceso cancelado: Sin carpeta de destino.")
        sys.exit()

    print(f"URL Validada: {url}")
    print(f"Guardando en: {carpeta_salida}")

    # Datos constantes (Docente/Fecha)
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

    print("Descargando datos completos...")
    try:
        df2 = pd.read_csv(url)
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Ocurrió un error al descargar los datos completos:\n{e}")
        sys.exit()

    # Función auxiliar para limpiar números
    def convertir_a_float(valor):
        if pd.isna(valor) or valor == '':
            return 0.0
        valor_str = str(valor).replace(',', '.')
        try:
            return float(valor_str)
        except ValueError:
            return 0.0

    print(f"Procesando {len(df2)} registros...")

    # --- CICLO PRINCIPAL ---
    contador_generados = 0
    
    for indice, fila in df2.iterrows():
        
        # Verificar palabra de control para detener
        if fila.astype(str).str.contains('CONTROL', case=False).any():
            print(f"--- Deteniendo: Palabra 'CONTROL' encontrada en fila {indice} ---")
            break 

        nombre_estudiante = fila["Nombre Completo"]
        print(f"Generando informe {indice + 1}: {nombre_estudiante}")

        # IMPORTANTE: Cargar plantilla NUEVA en cada iteración
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

        # Preparar datos gráficos
        notas_raw = [
            fila["asistencia1"], fila["trasn1"], fila["bonificacion1"],
            fila["taller1"], fila["comportamiento1"], fila["autoevaluacion1"],
            fila["examen1"]
        ]
        
        notas = [convertir_a_float(x) for x in notas_raw]
        etiquetas = ["Asis", "Trans", "Boni", "Tall", "Comp", "Autoe", "Exa"]
        
        # Configurar Radar Chart
        num_vars = len(etiquetas)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        notas_grafico = notas + [notas[0]]
        angles_grafico = angles + [angles[0]]

        fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
        ax.set_ylim(0, 5) # Escala fija de 0 a 5
        ax.fill(angles_grafico, notas_grafico, color='skyblue', alpha=0.4)
        ax.plot(angles_grafico, notas_grafico, color='blue', linewidth=2)
        ax.set_yticklabels([])
        ax.set_xticks(angles)
        ax.set_xticklabels(etiquetas)
        plt.title('Desempeño Integral', y=1.08)

        # Guardar gráfico en memoria
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png', bbox_inches='tight')
        plt.close(fig)
        img_stream.seek(0)

        # Insertar imagen en Word
        imagen = InlineImage(doc, img_stream, width=Inches(2.5))
        contenido["grafico"] = imagen

        # Guardar Word
        try:
            doc.render(contenido)
            
            # Limpiar nombre de archivo
            nombre_archivo = "".join([c for c in str(nombre_estudiante) if c.isalpha() or c.isdigit() or c==' ']).strip()
            if not nombre_archivo: nombre_archivo = f"Estudiante_{indice}"
            
            ruta_final = os.path.join(carpeta_salida, f"{nombre_archivo}_INFORME.docx")
            doc.save(ruta_final)
            contador_generados += 1
        except Exception as e:
            print(f"Error al guardar el archivo de {nombre_estudiante}: {e}")

    # Mensaje final
    print("\n¡Proceso finalizado!")
    messagebox.showinfo("Reporte Final", f"Se han generado {contador_generados} informes correctamente.\nUbicación: {carpeta_salida}")

if __name__ == "__main__":
    main()