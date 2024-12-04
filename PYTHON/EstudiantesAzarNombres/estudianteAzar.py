import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import random

# Función para seleccionar un archivo de Excel
def cargar_archivo_excel():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de Excel", "*.xlsx *.xls")])
    if archivo:
        try:
            df = pd.read_excel(archivo)  # Leer el archivo Excel
            lista_estudiantes = df.iloc[:, 0].tolist()  # Suponemos que los nombres están en la primera columna
            boton_seleccionar.config(state=tk.NORMAL)
            global estudiantes
            estudiantes = lista_estudiantes
            messagebox.showinfo("Éxito", "Archivo cargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")
    else:
        messagebox.showwarning("Advertencia", "No seleccionaste ningún archivo.")

# Función para seleccionar un estudiante al azar
def seleccionar_estudiante():
    if estudiantes:
        seleccionado = random.choice(estudiantes)
        etiqueta_resultado.config(text=f"Estudiante: {seleccionado}", font=("Arial", 28, "bold"))
    else:
        messagebox.showwarning("Advertencia", "No hay estudiantes en la lista.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Seleccionar Estudiante al Azar")
ventana.geometry("800x550")

# Cargar el logotipo (icono de la ventana)
#logotipo = tk.PhotoImage(file="icco.png")  # El archivo logotipo.png debe estar en la misma carpeta
#ventana.iconphoto(False, logotipo)  # Asigna el logotipo a la ventana



# Encabezado con texto en la parte superior
etiqueta_encabezado = tk.Label(ventana, text="Sistema de Selección de Estudiantes \n INSTITUCION EDUCATIVA", font=("Arial", 30, "bold"))
etiqueta_encabezado.pack(pady=10)  # Añadir el texto debajo de la imagen

# Ajustar tamaño de fuente para los botones y etiquetas
fuente_boton = ("Helvetica", 14)
fuente_etiqueta = ("Helvetica", 14)

# Botón para cargar el archivo Excel
boton_cargar = tk.Button(ventana, text="Cargar lista de estudiantes", command=cargar_archivo_excel, font=fuente_boton)
boton_cargar.pack(pady=20)

# Botón para seleccionar al estudiante (inicialmente deshabilitado)
boton_seleccionar = tk.Button(ventana, text="Seleccionar Estudiante", state=tk.DISABLED, command=seleccionar_estudiante, font=fuente_boton)
boton_seleccionar.pack(pady=10)

# Etiqueta para mostrar el resultado
etiqueta_resultado = tk.Label(ventana, text="", font=("Helvetica", 14))
etiqueta_resultado.pack(pady=10)

# Ejecutar la ventana principal
ventana.mainloop()
