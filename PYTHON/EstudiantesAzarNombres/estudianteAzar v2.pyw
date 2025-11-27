import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import random
import os

# Variable global para estudiantes
estudiantes = []

# Función para cargar archivo desde equipo
def cargar_archivo_excel():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de Excel", "*.xlsx *.xls")])
    if archivo:
        try:
            df = pd.read_excel(archivo)
            lista_estudiantes = df.iloc[:, 0].tolist()
            global estudiantes
            estudiantes = lista_estudiantes
            actualizar_estado_botones()
            messagebox.showinfo("Éxito", f"Archivo cargado correctamente.\n{len(estudiantes)} estudiantes encontrados.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

# Función para cargar archivo desde carpeta base
def cargar_archivo_local():
    archivo = filedialog.askopenfilename(
        initialdir=os.getcwd(),
        filetypes=[("Archivos de Excel", "*.xlsx *.xls")]
    )
    if archivo:
        try:
            df = pd.read_excel(archivo)
            lista_estudiantes = df.iloc[:, 0].tolist()
            global estudiantes
            estudiantes = lista_estudiantes
            actualizar_estado_botones()
            messagebox.showinfo("Éxito", f"Archivo cargado correctamente.\n{len(estudiantes)} estudiantes encontrados.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

# Función para pegar lista manualmente
def pegar_lista_manual():
    texto = simpledialog.askstring("Pegar lista", "Ingrese los nombres de los estudiantes (separados por comas o saltos de línea):")
    if texto:
        # Procesar el texto ingresado
        lista = []
        for linea in texto.split('\n'):
            for item in linea.split(','):
                item_limpio = item.strip()
                if item_limpio:
                    lista.append(item_limpio)
        
        if lista:
            global estudiantes
            estudiantes = lista
            actualizar_estado_botones()
            messagebox.showinfo("Éxito", f"Lista cargada correctamente.\n{len(estudiantes)} estudiantes agregados.")
        else:
            messagebox.showwarning("Advertencia", "No se ingresaron nombres válidos.")

# Función para seleccionar un estudiante al azar
def seleccionar_estudiante():
    if estudiantes:
        seleccionado = random.choice(estudiantes)
        etiqueta_resultado.config(text=f"Estudiante seleccionado:\n{seleccionado}", font=("Arial", 28, "bold"))
    else:
        messagebox.showwarning("Advertencia", "No hay estudiantes en la lista.")

# Función para actualizar estado de botones
def actualizar_estado_botones():
    if estudiantes:
        boton_seleccionar.config(state=tk.NORMAL)
    else:
        boton_seleccionar.config(state=tk.DISABLED)

# Crear menú de opciones de carga
def mostrar_menu_carga():
    menu = tk.Toplevel(ventana)
    menu.title("Opciones de Carga")
    menu.geometry("400x250")
    
    tk.Label(menu, text="Seleccione cómo desea cargar la lista:", font=("Helvetica", 12)).pack(pady=10)
    
    tk.Button(menu, text="Buscar archivo en equipo", command=lambda: [cargar_archivo_excel(), menu.destroy()], 
              font=("Helvetica", 12), width=25).pack(pady=5)
    
    tk.Button(menu, text="Buscar archivo en carpeta base", command=lambda: [cargar_archivo_local(), menu.destroy()], 
              font=("Helvetica", 12), width=25).pack(pady=5)
    
    tk.Button(menu, text="Pegar lista manualmente", command=lambda: [pegar_lista_manual(), menu.destroy()], 
              font=("Helvetica", 12), width=25).pack(pady=5)
    
    tk.Button(menu, text="Cancelar", command=menu.destroy, font=("Helvetica", 12), width=15).pack(pady=10)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Seleccionar Estudiante al Azar")
ventana.geometry("800x600")

# Encabezado con texto en la parte superior
etiqueta_encabezado = tk.Label(
    ventana, 
    text="Sistema de Selección de Estudiantes\nINSTITUCION EDUCATIVA", 
    font=("Arial", 30, "bold")
)
etiqueta_encabezado.pack(pady=20)

# Botón para cargar la lista (ahora abre menú de opciones)
boton_cargar = tk.Button(
    ventana, 
    text="Cargar lista de estudiantes", 
    command=mostrar_menu_carga, 
    font=("Helvetica", 14),
    width=25
)
boton_cargar.pack(pady=20)

# Botón para seleccionar al estudiante (inicialmente deshabilitado)
boton_seleccionar = tk.Button(
    ventana, 
    text="Seleccionar Estudiante", 
    state=tk.DISABLED, 
    command=seleccionar_estudiante, 
    font=("Helvetica", 14),
    width=25
)
boton_seleccionar.pack(pady=10)

# Etiqueta para mostrar el resultado
etiqueta_resultado = tk.Label(
    ventana, 
    text="", 
    font=("Helvetica", 14),
    wraplength=700,
    justify="center"
)
etiqueta_resultado.pack(pady=20)

# Etiqueta para mostrar información de la lista actual
etiqueta_info = tk.Label(
    ventana,
    text="No hay lista cargada",
    font=("Helvetica", 10),
    fg="gray"
)
etiqueta_info.pack()

# Función para actualizar la etiqueta de información
def actualizar_info():
    if estudiantes:
        etiqueta_info.config(text=f"Lista actual: {len(estudiantes)} estudiantes cargados", fg="green")
    else:
        etiqueta_info.config(text="No hay lista cargada", fg="gray")

# Ejecutar la ventana principal
ventana.mainloop()