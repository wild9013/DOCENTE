import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ast
import re

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Buscador de DBA por Grado")
ventana.geometry("800x600")

# Variable global para guardar los DBA
dba_por_grado = {}

# Función para cargar el archivo .txt
def cargar_archivo():
    global dba_por_grado
    ruta = filedialog.askopenfilename(
        title="Selecciona el archivo con los DBA",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    if ruta:
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()

                # Buscar el primer '{' hasta el último '}' — extraer solo el diccionario
                match = re.search(r'(\{.*\})', contenido, re.DOTALL)
                if match:
                    diccionario_texto = match.group(1)
                    dba_por_grado = ast.literal_eval(diccionario_texto)  # Convertir texto a diccionario
                    
                    combo_grados['values'] = list(dba_por_grado.keys())  # Cargar grados al combo
                    messagebox.showinfo("Éxito", "¡Archivo cargado correctamente!\nSelecciona un grado para ver los DBA.")
                else:
                    messagebox.showerror("Error", "El archivo no contiene un diccionario válido.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")

# Función para mostrar los DBA según el grado seleccionado
def mostrar_dba():
    grado = combo_grados.get()
    texto_resultado.delete("1.0", tk.END)  # Limpiar texto anterior
    resultado = dba_por_grado.get(grado, None)
    if resultado:
        for i, dba in enumerate(resultado, 1):
            texto_resultado.insert(tk.END, f"{i}. {dba}\n\n")
    else:
        messagebox.showinfo("Información", "Por favor, selecciona un grado válido.")

# Widgets
label_archivo = tk.Label(ventana, text="Cargar archivo de DBA por grado:", font=("Arial", 14))
label_archivo.pack(pady=10)

boton_cargar = tk.Button(ventana, text="Abrir archivo .txt", command=cargar_archivo, font=("Arial", 12))
boton_cargar.pack(pady=5)

label_grados = tk.Label(ventana, text="Selecciona un grado:", font=("Arial", 14))
label_grados.pack(pady=10)

combo_grados = ttk.Combobox(ventana, font=("Arial", 12), state="readonly")
combo_grados.pack(pady=5)

boton_buscar = tk.Button(ventana, text="Buscar DBA", command=mostrar_dba, font=("Arial", 12))
boton_buscar.pack(pady=10)

texto_resultado = tk.Text(ventana, wrap=tk.WORD, font=("Arial", 11))
texto_resultado.pack(padx=20, pady=10, expand=True, fill='both')

# Iniciar aplicación
ventana.mainloop()
