import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import gspread
from oauth2client.service_account import ServiceAccountCredentials


#pip install gspread oauth2client pandas


# Configuración de las credenciales y conexión con Google Sheets
def obtener_credenciales():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('ruta/a/tu/archivo/credenciales.json', scope)
    client = gspread.authorize(creds)
    return client

# Variable global para el DataFrame
df = pd.DataFrame()
sheet = None

# Función para cargar el archivo Google Sheets
def cargar_google_sheets():
    global df, sheet
    client = obtener_credenciales()
    hoja_url = filedialog.askstring("URL de Google Sheets", "Introduce la URL de Google Sheets:")
    if hoja_url:
        try:
            sheet = client.open_by_url(hoja_url).sheet1
            datos = sheet.get_all_records()
            df = pd.DataFrame(datos)
            actualizar_columnas(df)
            actualizar_tabla(df)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo.\n{e}")

# Función para guardar los cambios en Google Sheets
def guardar_google_sheets():
    global df, sheet
    if sheet is not None:
        try:
            sheet.clear()
            sheet.update([df.columns.tolist()] + df.values.tolist())
            messagebox.showinfo("Guardado", "Los datos se han guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo.\n{e}")
    else:
        messagebox.showwarning("Advertencia", "No hay ninguna hoja cargada.")

# Función para actualizar las columnas del Treeview
def actualizar_columnas(df):
    tabla["columns"] = list(df.columns)
    for col in tabla["columns"]:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center")

# Función para actualizar la tabla con los datos de Google Sheets
def actualizar_tabla(df):
    for i in tabla.get_children():
        tabla.delete(i)
    
    for _, fila in df.iterrows():
        tabla.insert("", "end", values=list(fila))

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
ventana.geometry("800x600")

# Configuración de la tabla
tabla = ttk.Treeview(ventana, show="headings")
tabla.pack(expand=True, fill="both")
tabla.bind("<Double-1>", editar_celda)

# Botones de carga y guardado
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

btn_cargar = tk.Button(frame_botones, text="Cargar Google Sheets", command=cargar_google_sheets)
btn_cargar.grid(row=0, column=0, padx=5)

btn_guardar = tk.Button(frame_botones, text="Guardar Google Sheets", command=guardar_google_sheets)
btn_guardar.grid(row=0, column=1, padx=5)

ventana.mainloop()
