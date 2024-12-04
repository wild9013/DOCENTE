import tkinter as tk
from tkinter import messagebox
import random

def generar_numero():
    try:
        min_val = int(entry_min.get())
        max_val = int(entry_max.get())
        if min_val >= max_val:
            messagebox.showerror("Error", "El valor mínimo debe ser menor que el valor máximo.")
            return
        numero_aleatorio = random.randint(min_val, max_val)
        label_resultado.config(text=f"Número aleatorio: {numero_aleatorio}")
    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese valores enteros válidos.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Generador de Número Aleatorio")

# Configurar la ventana en pantalla completa
ventana.attributes('-fullscreen', True)

# Configuración del tamaño del texto
fuente = ('Arial', 36)

# Crear y ubicar los widgets
label_min = tk.Label(ventana, text="Valor mínimo:", font=fuente)
label_min.pack(pady=10)

entry_min = tk.Entry(ventana, font=fuente)
entry_min.pack(pady=5)

label_max = tk.Label(ventana, text="Valor máximo:", font=fuente)
label_max.pack(pady=10)

entry_max = tk.Entry(ventana, font=fuente)
entry_max.pack(pady=5)

boton_generar = tk.Button(ventana, text="Generar Número", font=fuente, command=generar_numero)
boton_generar.pack(pady=20)

label_resultado = tk.Label(ventana, text="", font=fuente)
label_resultado.pack(pady=10)

# Ejecutar la ventana
ventana.mainloop()
