import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import re

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Buscador de DBA y Evidencias")
ventana.geometry("900x600")

# Variables globales
data = []
dba_filtrados = []
evidencias_actuales = []

# Función para cargar el archivo .txt o .json
def cargar_archivo():
    global data
    ruta = filedialog.askopenfilename(
        title="Selecciona el archivo de Evidencias",
        filetypes=[("Archivos JSON o TXT", "*.json *.txt")]
    )
    if ruta:
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()

                # Buscar la estructura del array [ ... ]
                match = re.search(r'(\[.*\])', contenido, re.DOTALL)
                if match:
                    array_texto = match.group(1)
                    data = json.loads(array_texto)  # Convertir a lista de Python

                    grados = sorted(set(entry['Grado'] for entry in data))
                    combo_grados['values'] = grados
                    combo_grados.set('')
                    combo_dba.set('')
                    combo_evidencias.set('')
                    texto_evidencias.delete("1.0", tk.END)
                    messagebox.showinfo("Éxito", "¡Archivo cargado correctamente!\nSelecciona un grado.")
                else:
                    messagebox.showerror("Error", "No se encontró una lista de evidencias válida en el archivo.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

# Mostrar DBA según grado
def mostrar_dba():
    grado_seleccionado = combo_grados.get()
    global dba_filtrados
    dba_filtrados = [d for d in data if d['Grado'] == grado_seleccionado]

    if dba_filtrados:
        combo_dba['values'] = [f"{d['DBA']}: {d['Enunciado_DBA']}" for d in dba_filtrados]
        combo_dba.set('')
        combo_evidencias.set('')
        texto_evidencias.delete("1.0", tk.END)
        messagebox.showinfo("Listo", f"{len(dba_filtrados)} DBA encontrados para {grado_seleccionado}.\nSelecciona uno.")
    else:
        combo_dba['values'] = []
        combo_evidencias['values'] = []
        texto_evidencias.delete("1.0", tk.END)
        messagebox.showinfo("Sin resultados", "No se encontraron DBA para este grado.")

# Mostrar evidencias cuando se elige un DBA
def mostrar_evidencias():
    seleccion = combo_dba.current()
    if seleccion != -1:
        global evidencias_actuales
        evidencias_actuales = dba_filtrados[seleccion]['Evidencias_de_Aprendizaje']
        combo_evidencias['values'] = evidencias_actuales
        combo_evidencias.set('')
        texto_evidencias.delete("1.0", tk.END)

# Mostrar detalle de evidencia seleccionada
def mostrar_texto_evidencia():
    seleccion = combo_evidencias.get()
    texto_evidencias.delete("1.0", tk.END)
    if seleccion:
        texto_evidencias.insert(tk.END, seleccion)

# Widgets
label_archivo = tk.Label(ventana, text="1️⃣ Cargar archivo de Evidencias:", font=("Arial", 14))
label_archivo.pack(pady=5)

boton_cargar = tk.Button(ventana, text="📂 Abrir archivo", command=cargar_archivo, font=("Arial", 12))
boton_cargar.pack(pady=5)

label_grados = tk.Label(ventana, text="2️⃣ Selecciona un grado:", font=("Arial", 14))
label_grados.pack(pady=10)

combo_grados = ttk.Combobox(ventana, font=("Arial", 12), state="readonly")
combo_grados.pack(pady=5)

boton_mostrar_dba = tk.Button(ventana, text="🔍 Buscar DBA", command=mostrar_dba, font=("Arial", 12))
boton_mostrar_dba.pack(pady=10)

label_dba = tk.Label(ventana, text="3️⃣ Selecciona un DBA:", font=("Arial", 14))
label_dba.pack(pady=10)

combo_dba = ttk.Combobox(ventana, font=("Arial", 12), state="readonly", width=100)
combo_dba.pack(pady=5)
combo_dba.bind("<<ComboboxSelected>>", lambda e: mostrar_evidencias())

label_evidencias = tk.Label(ventana, text="4️⃣ Selecciona una Evidencia:", font=("Arial", 14))
label_evidencias.pack(pady=10)

combo_evidencias = ttk.Combobox(ventana, font=("Arial", 12), state="readonly", width=100)
combo_evidencias.pack(pady=5)
combo_evidencias.bind("<<ComboboxSelected>>", lambda e: mostrar_texto_evidencia())

texto_evidencias = tk.Text(ventana, wrap=tk.WORD, font=("Arial", 11), height=10)
texto_evidencias.pack(padx=20, pady=10, expand=True, fill='both')

# Iniciar aplicación
ventana.mainloop()
