import tkinter as tk
from tkinter import messagebox
import pandas as pd

class Juego100Colombianos:
    def __init__(self, root):
        self.root = root
        self.root.title("100 Estudiantes Dicen")
        self.root.configure(bg="#ffcc00")
        
        # Leer preguntas desde un archivo de Excel
        self.preguntas = self.leer_preguntas_excel('C:/Users/swild/Desktop/preguntas.xlsx')
        self.score = 0
        self.num_preguntas = len(self.preguntas)  # Usar todas las preguntas disponibles
        self.preguntas_seleccionadas = self.preguntas  # Usar todas las preguntas directamente
        self.pregunta_actual = 0
        
        # Crear interfaz gráfica
        self.label_pregunta = tk.Label(root, text="", wraplength=1000, font=("Arial", 30), bg="#ffcc00", fg="#003366")
        self.label_pregunta.pack(pady=10)

        # Marco para las respuestas
        self.frame_respuestas = tk.Frame(root, bg="#ffcc00")
        self.frame_respuestas.pack(pady=10)

        self.label_a = tk.Label(self.frame_respuestas, text="", width=30, font=("Arial", 24), bg="#ffcc00", fg="#003366")
        self.label_b = tk.Label(self.frame_respuestas, text="", width=30, font=("Arial", 24), bg="#ffcc00", fg="#003366")
        self.label_c = tk.Label(self.frame_respuestas, text="", width=30, font=("Arial", 24), bg="#ffcc00", fg="#003366")
        self.label_d = tk.Label(self.frame_respuestas, text="", width=30, font=("Arial", 24), bg="#ffcc00", fg="#003366")

        self.label_a.pack(pady=2)
        self.label_b.pack(pady=2)
        self.label_c.pack(pady=2)
        self.label_d.pack(pady=2)

        # Marco para los botones de mostrar
        self.frame_botones = tk.Frame(root, bg="#ffcc00")
        self.frame_botones.pack(pady=10)

        # Botones de respuesta
        self.btn_mostrar_a = tk.Button(self.frame_botones, text="Mostrar A", command=lambda: self.mostrar_respuesta('A'), font=("Arial", 24), bg="#ff6666", fg="#ffffff")
        self.btn_mostrar_b = tk.Button(self.frame_botones, text="Mostrar B", command=lambda: self.mostrar_respuesta('B'), font=("Arial", 24), bg="#ff6666", fg="#ffffff")
        self.btn_mostrar_c = tk.Button(self.frame_botones, text="Mostrar C", command=lambda: self.mostrar_respuesta('C'), font=("Arial", 24), bg="#ff6666", fg="#ffffff")
        self.btn_mostrar_d = tk.Button(self.frame_botones, text="Mostrar D", command=lambda: self.mostrar_respuesta('D'), font=("Arial", 24), bg="#ff6666", fg="#ffffff")
        
        # Colocar los botones en una cuadrícula
        self.btn_mostrar_a.grid(row=0, column=0, padx=5, pady=2)
        self.btn_mostrar_b.grid(row=0, column=1, padx=5, pady=2)
        self.btn_mostrar_c.grid(row=1, column=0, padx=5, pady=2)
        self.btn_mostrar_d.grid(row=1, column=1, padx=5, pady=2)

        # Marco para los botones de avanzar y retroceder
        self.frame_nav = tk.Frame(root, bg="#ffcc00")
        self.frame_nav.pack(pady=10)

        self.btn_retroceder = tk.Button(self.frame_nav, text="Retroceder", command=self.retroceder_pregunta, font=("Arial", 24), bg="#66cc66", fg="#ffffff")
        self.btn_avanzar = tk.Button(self.frame_nav, text="Avanzar", command=self.avanzar_pregunta, font=("Arial", 24), bg="#66cc66", fg="#ffffff")
        
        # Colocar los botones de navegación en la misma fila
        self.btn_retroceder.grid(row=0, column=0, padx=10)
        self.btn_avanzar.grid(row=0, column=1, padx=10)

        self.mostrar_pregunta()

    def leer_preguntas_excel(self, archivo):
        try:
            df = pd.read_excel(archivo)
            preguntas = []
            for index, row in df.iterrows():
                pregunta = {
                    "pregunta": row['Pregunta'],
                    "respuestas": {
                        "A": (row['A'], row['A%']),
                        "B": (row['B'], row['B%']),
                        "C": (row['C'], row['C%']),
                        "D": (row['D'], row['D%']),
                    }
                }
                preguntas.append(pregunta)
            return preguntas
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
            self.root.quit()

    def mostrar_pregunta(self):
        if self.pregunta_actual < len(self.preguntas_seleccionadas):
            pregunta = self.preguntas_seleccionadas[self.pregunta_actual]
            self.label_pregunta.config(text=pregunta["pregunta"])
            self.label_a.config(text="")
            self.label_b.config(text="")
            self.label_c.config(text="")
            self.label_d.config(text="")
            self.btn_avanzar.config(state=tk.DISABLED)
            self.btn_retroceder.config(state=tk.NORMAL if self.pregunta_actual > 0 else tk.DISABLED)
        else:
            self.finalizar_juego()

    def mostrar_respuesta(self, seleccion):
        if seleccion in ['A', 'B', 'C', 'D']:
            pregunta = self.preguntas_seleccionadas[self.pregunta_actual]
            respuesta = pregunta['respuestas'][seleccion]
            if seleccion == 'A':
                self.label_a.config(text=f"{respuesta[0]} - {respuesta[1]}%")
            elif seleccion == 'B':
                self.label_b.config(text=f"{respuesta[0]} - {respuesta[1]}%")
            elif seleccion == 'C':
                self.label_c.config(text=f"{respuesta[0]} - {respuesta[1]}%")
            elif seleccion == 'D':
                self.label_d.config(text=f"{respuesta[0]} - {respuesta[1]}%")
            self.btn_avanzar.config(state=tk.NORMAL)

    def avanzar_pregunta(self):
        if self.pregunta_actual < len(self.preguntas_seleccionadas) - 1:
            self.pregunta_actual += 1
            self.mostrar_pregunta()

    def retroceder_pregunta(self):
        if self.pregunta_actual > 0:
            self.pregunta_actual -= 1
            self.mostrar_pregunta()

    def finalizar_juego(self):
        messagebox.showinfo("Fin del Juego", "Juego terminado.")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    juego = Juego100Colombianos(root)
    root.mainloop()
