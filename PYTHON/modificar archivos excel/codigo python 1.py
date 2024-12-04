import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Variable global para el DataFrame
df = pd.DataFrame()

# Función para cargar el archivo Excel
def cargar_excel():
    global df
    archivo = filedialog.askopenfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx;*.xls")])
    if archivo:
        try:
            df = pd.read_excel(archivo)
            actualizar_columnas(df)
            actualizar_tabla(df)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo.\n{e}")

# Función para actualizar las columnas del Treeview
def actualizar_columnas(df):
    # Limpiar las columnas existentes
    tabla["columns"] = list(df.columns)
    for col in tabla["columns"]:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center")

# Función para actualizar la tabla con los datos de la hoja de Excel
def actualizar_tabla(df):
    # Limpiar la tabla
    for i in tabla.get_children():
        tabla.delete(i)
    
    # Insertar nuevas filas
    for _, fila in df.iterrows():
        tabla.insert("", "end", values=list(fila))

# Función para guardar los cambios al archivo Excel
def guardar_excel():
    global df
    archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx;*.xls")])
    if archivo:
        try:
            # Guardar el DataFrame actual en el archivo Excel
            df.to_excel(archivo, index=False)
            messagebox.showinfo("Guardado", "Los datos se han guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo.\n{e}")

# Función para editar una celda
def editar_celda(event):
    global df
    item = tabla.selection()[0]
    columna = tabla.identify_column(event.x)
    columna_index = int(columna.replace('#', '')) - 1

    def guardar_edicion(event):
        nuevo_valor = entry.get()
        tabla.set(item, column=columna, value=nuevo_valor)
        fila_index = tabla.index(item)
        df.iat[fila_index, columna_index] = nuevo_valor  # Actualiza el DataFrame
        entry.destroy()

    x, y, width, height = tabla.bbox(item, column=columna)
    entry = tk.Entry(ventana)
    entry.place(x=x, y=y, width=width, height=height)
    entry.insert(0, tabla.set(item, column=columna))
    entry.bind("<Return>", guardar_edicion)
    entry.focus()

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Notas de Estudiantes")
ventana.geometry("800x600")  # Aumentamos el tamaño de la ventana para mayor visibilidad

# Configuración de la tabla
tabla = ttk.Treeview(ventana, show="headings")
tabla.pack(expand=True, fill="both")
tabla.bind("<Double-1>", editar_celda)

# Botones de carga y guardado
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

btn_cargar = tk.Button(frame_botones, text="Cargar Excel", command=cargar_excel)
btn_cargar.grid(row=0, column=0, padx=5)

btn_guardar = tk.Button(frame_botones, text="Guardar Excel", command=guardar_excel)
btn_guardar.grid(row=0, column=1, padx=5)

ventana.mainloop()
