import tkinter as tk
from tkinter import messagebox
import random

class GeneradorNumeros:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Generador de Número Aleatorio")
        self.ventana.attributes('-fullscreen', True)
        
        self.resultados = []

        # Configuración del tamaño del texto
        fuente = ('Arial',36)
        
        # Crear un marco para la parte central (entrada y botón)
        marco_central = tk.Frame(self.ventana)
        marco_central.pack(side=tk.LEFT, padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Crear y ubicar los widgets en el marco central
        self.label_min = tk.Label(marco_central, text="Valor mínimo:", font=fuente)
        self.label_min.pack(pady=10)

        self.entry_min = tk.Entry(marco_central, font=fuente)
        self.entry_min.pack(pady=5)

        self.label_max = tk.Label(marco_central, text="Valor máximo:", font=fuente)
        self.label_max.pack(pady=10)

        self.entry_max = tk.Entry(marco_central, font=fuente)
        self.entry_max.pack(pady=5)

        self.boton_generar = tk.Button(marco_central, text="Generar Número", font=fuente, command=self.generar_numero)
        self.boton_generar.pack(pady=20)

        self.label_resultado = tk.Label(marco_central, text="", font=fuente)
        self.label_resultado.pack(pady=10)

        # Crear un marco para la parte derecha (resultados recientes)
        marco_derecha = tk.Frame(self.ventana)
        marco_derecha.pack(side=tk.RIGHT, padx=20, pady=20)

        self.label_resultados_recientes = tk.Label(marco_derecha, text="Últimos Resultados:", font=fuente)
        self.label_resultados_recientes.pack(pady=10)

        self.lista_resultados = tk.Listbox(marco_derecha, font=fuente, width=20, height=15)
        self.lista_resultados.pack(pady=10)

    def generar_numero(self):
        try:
            min_val = int(self.entry_min.get())
            max_val = int(self.entry_max.get())
            if min_val >= max_val:
                messagebox.showerror("Error", "El valor mínimo debe ser menor que el valor máximo.")
                return
            numero_aleatorio = random.randint(min_val, max_val)
            self.label_resultado.config(text=f"Número aleatorio: {numero_aleatorio}")
            self.agregar_resultado(numero_aleatorio)
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingrese valores enteros válidos.")

    def agregar_resultado(self, numero):
        if len(self.resultados) >= 15:
            self.resultados.pop(0)
            self.lista_resultados.delete(0)
        self.resultados.append(numero)
        self.lista_resultados.insert(tk.END, numero)

# Crear la ventana principal
ventana = tk.Tk()
app = GeneradorNumeros(ventana)

# Ejecutar la ventana
ventana.mainloop()
