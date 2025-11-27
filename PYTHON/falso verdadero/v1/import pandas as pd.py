import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog

# Función para leer el archivo Excel
def leer_preguntas(archivo_excel):
    df = pd.read_excel(archivo_excel)
    preguntas = df.to_dict(orient='records')
    return preguntas

# Función para abrir el cuadro de diálogo de selección de archivos
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(
        filetypes=[("Archivos Excel", "*.xlsx")],
        title="Selecciona el archivo de preguntas"
    )
    return archivo

# Mostrar la ventana de preguntas
class VentanaPreguntas(tk.Tk):
    def __init__(self, preguntas):
        super().__init__()
        self.preguntas = preguntas
        self.index_pregunta = 0
        self.title("Conociendo nuestros deberes y derechos")  # Título actualizado
        self.geometry("600x300")  # Tamaño de ventana ajustado para mayor contenido
        self.crear_widgets()
        self.mostrar_pregunta()

    def crear_widgets(self):
        # Configuración de fuente
        fuente_pregunta = ('Arial', 14)  # Fuente para las preguntas
        fuente_boton = ('Arial', 12)  # Fuente para los botones

        self.pregunta_label = tk.Label(self, text="", font=fuente_pregunta, wraplength=550)
        self.pregunta_label.pack(pady=20)

        self.boton_verdadero = tk.Button(self, text="Verdadero", font=fuente_boton, command=self.responder_verdadero)
        self.boton_verdadero.pack(side=tk.LEFT, padx=20)

        self.boton_falso = tk.Button(self, text="Falso", font=fuente_boton, command=self.responder_falso)
        self.boton_falso.pack(side=tk.RIGHT, padx=20)

    def mostrar_pregunta(self):
        if self.index_pregunta < len(self.preguntas):
            pregunta = self.preguntas[self.index_pregunta]['Pregunta']
            self.pregunta_label.config(text=pregunta)
        else:
            messagebox.showinfo("Fin", "Has respondido todas las preguntas.")
            self.destroy()

    def responder_verdadero(self):
        self.verificar_respuesta('V')

    def responder_falso(self):
        self.verificar_respuesta('F')

    def verificar_respuesta(self, respuesta_usuario):
        respuesta_correcta = self.preguntas[self.index_pregunta]['Respuesta']
        if respuesta_usuario == respuesta_correcta:
            messagebox.showinfo("Respuesta", "¡Correcto!")
        else:
            messagebox.showinfo("Respuesta", "Incorrecto.")
        self.index_pregunta += 1
        self.mostrar_pregunta()

# Crear una ventana para seleccionar el archivo y cargar las preguntas
def main():
    # Crear la ventana principal
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    # Seleccionar el archivo
    archivo_excel = seleccionar_archivo()
    if not archivo_excel:
        messagebox.showerror("Error", "No se seleccionó ningún archivo.")
        return

    # Leer las preguntas del archivo seleccionado
    try:
        preguntas = leer_preguntas(archivo_excel)
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el archivo: {e}")
        return

    # Crear y ejecutar la ventana de preguntas
    app = VentanaPreguntas(preguntas)
    app.mainloop()

if __name__ == "__main__":
    main()
