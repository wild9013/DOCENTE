# ESTA VERSIÓN PERMITE CARGAR LISTAS DE ESTUDIANTES DESDE ARCHIVOS EXCEL,
#  PEGAR MANUALMENTE Y SELECCIONAR AL AZAR
# PERMITE COPIAR LA LISTA DE ESTUDIANTES SELECCIONADOS AL PORTAPAPELES
# REQUIERE INSTALAR PANDAS Y OPENPYXL PARA MANIPULAR ARCHIVOS EXCEL
# pip install pandas openpyxl, pandas, pyperclip



import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import pandas as pd
import random
import os

# Variable global para estudiantes, seleccionados y restantes
estudiantes = []
estudiantes_seleccionados = []
estudiantes_restantes = []

# Función para cargar archivo desde equipo
def cargar_archivo_excel():
    archivo = filedialog.askopenfilename(filetypes=[("Archivos de Excel", "*.xlsx *.xls")])
    if archivo:
        try:
            df = pd.read_excel(archivo)
            lista_estudiantes = df.iloc[:, 0].tolist()
            global estudiantes, estudiantes_restantes
            estudiantes = lista_estudiantes
            estudiantes_restantes = lista_estudiantes.copy()  # Copia inicial de estudiantes
            actualizar_estado_botones()
            actualizar_info()
            actualizar_lista_restantes()
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
            global estudiantes, estudiantes_restantes
            estudiantes = lista_estudiantes
            estudiantes_restantes = lista_estudiantes.copy()  # Copia inicial de estudiantes
            actualizar_estado_botones()
            actualizar_info()
            actualizar_lista_restantes()
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
            global estudiantes, estudiantes_restantes
            estudiantes = lista
            estudiantes_restantes = lista.copy()  # Copia inicial de estudiantes
            actualizar_estado_botones()
            actualizar_info()
            actualizar_lista_restantes()
            messagebox.showinfo("Éxito", f"Lista cargada correctamente.\n{len(estudiantes)} estudiantes agregados.")
        else:
            messagebox.showwarning("Advertencia", "No se ingresaron nombres válidos.")

# Función para seleccionar un estudiante al azar
def seleccionar_estudiante():
    if estudiantes_restantes:
        seleccionado = random.choice(estudiantes_restantes)
        estudiantes_seleccionados.append(seleccionado)
        estudiantes_restantes.remove(seleccionado)  # Eliminar de restantes
        actualizar_lista_seleccionados()
        actualizar_lista_restantes()
        etiqueta_resultado.config(text=f"Estudiante seleccionado:\n{seleccionado}", font=("Arial", 28, "bold"))
    else:
        messagebox.showwarning("Advertencia", "No hay estudiantes disponibles para seleccionar.")

# Función para actualizar la lista de seleccionados
def actualizar_lista_seleccionados():
    lista_seleccionados.delete(0, tk.END)
    for estudiante in estudiantes_seleccionados:
        lista_seleccionados.insert(tk.END, estudiante)
    actualizar_estado_boton_copiar()

# Función para actualizar la lista de estudiantes restantes
def actualizar_lista_restantes():
    lista_restantes.delete(0, tk.END)
    for estudiante in estudiantes_restantes:
        lista_restantes.insert(tk.END, estudiante)

# Función para copiar la lista al portapapeles usando tkinter
def copiar_al_portapapeles():
    if estudiantes_seleccionados:
        texto = "\n".join(estudiantes_seleccionados)
        ventana.clipboard_clear()  # Limpiar el portapapeles
        ventana.clipboard_append(texto)  # Agregar texto al portapapeles
        messagebox.showinfo("Éxito", "Lista de estudiantes seleccionados copiada al portapapeles.")
    else:
        messagebox.showwarning("Advertencia", "No hay estudiantes seleccionados para copiar.")

# Función para actualizar estado de botones
def actualizar_estado_botones():
    if estudiantes_restantes:
        boton_seleccionar.config(state=tk.NORMAL)
    else:
        boton_seleccionar.config(state=tk.DISABLED)
    actualizar_estado_boton_copiar()

# Función para actualizar estado del botón de copiar
def actualizar_estado_boton_copiar():
    if estudiantes_seleccionados:
        boton_copiar.config(state=tk.NORMAL)
    else:
        boton_copiar.config(state=tk.DISABLED)

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
boton_cargar.pack(pady=10)

# Botón para seleccionar al estudiante
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
etiqueta_resultado.pack(pady=10)

# Frame para la lista de seleccionados
frame_lista_seleccionados = tk.Frame(ventana)
frame_lista_seleccionados.pack(pady=10, fill=tk.BOTH, expand=True)

tk.Label(frame_lista_seleccionados, text="Estudiantes Seleccionados:", font=("Helvetica", 12, "bold")).pack()
scrollbar_seleccionados = tk.Scrollbar(frame_lista_seleccionados)
scrollbar_seleccionados.pack(side=tk.RIGHT, fill=tk.Y)

lista_seleccionados = tk.Listbox(frame_lista_seleccionados, height=8, width=50, yscrollcommand=scrollbar_seleccionados.set)
lista_seleccionados.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
scrollbar_seleccionados.config(command=lista_seleccionados.yview)

# Frame para la lista de estudiantes restantes
frame_lista_restantes = tk.Frame(ventana)
frame_lista_restantes.pack(pady=10, fill=tk.BOTH, expand=True)

tk.Label(frame_lista_restantes, text="Estudiantes por Seleccionar:", font=("Helvetica", 12, "bold")).pack()
scrollbar_restantes = tk.Scrollbar(frame_lista_restantes)
scrollbar_restantes.pack(side=tk.RIGHT, fill=tk.Y)

lista_restantes = tk.Listbox(frame_lista_restantes, height=8, width=50, yscrollcommand=scrollbar_restantes.set)
lista_restantes.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
scrollbar_restantes.config(command=lista_restantes.yview)

# Botón para copiar al portapapeles
boton_copiar = tk.Button(
    ventana, 
    text="Copiar Seleccionados", 
    state=tk.DISABLED, 
    command=copiar_al_portapapeles, 
    font=("Helvetica", 12),
    width=20
)
boton_copiar.pack(pady=10)

# Etiqueta para mostrar información de la lista actual
etiqueta_info = tk.Label(
    ventana,
    text="No hay lista cargada",
    font=("Helvetica", 10),
    fg="gray"
)
etiqueta_info.pack(pady=5)

# Función para actualizar la etiqueta de información
def actualizar_info():
    if estudiantes:
        etiqueta_info.config(text=f"Lista actual: {len(estudiantes)} estudiantes cargados, {len(estudiantes_restantes)} por seleccionar", fg="green")
    else:
        etiqueta_info.config(text="No hay lista cargada", fg="gray")

# Ejecutar la ventana principal
ventana.mainloop()