import tkinter as tk
from tkinter import font, messagebox
import random

# Base de datos de preguntas
preguntas = {
    "3x + 5 = 2x - 1": "Lineal",
    "x² - 4x + 4 = 0": "Cuadrática",
    "2ˣ = 16": "Exponencial",
    "√(x + 3) = 5": "Radical",
    "2/x + 1 = x": "Racional",
    "log₂(x) = 3": "Logarítmica",
    "sin(x) = 0.5": "Trigonométrica",
    "3x³ - 2x = 0": "Polinómica",
    "|x - 5| = 2": "Valor absoluto",
    "eˣ = 10": "Exponencial",
    "x + y = 5": "Lineal (2 variables)",
    "tan(x) = 1": "Trigonométrica"
}

class MillionaireGame:
    def __init__(self, root):
        self.root = root
        self.root.title("¿Quién quiere ser millonario? - Matemáticas")
        self.root.configure(bg="#2c3e50")
        self.root.attributes('-fullscreen', True)  # Modo pantalla completa
        self.root.bind('<Escape>', lambda event: self.salir_pantalla_completa())  # Salir con Escape

        # Fuentes personalizadas más grandes
        self.font_title = font.Font(family="Helvetica", size=32, weight="bold")
        self.font_question = font.Font(family="Courier New", size=28)
        self.font_button = font.Font(family="Arial", size=20)
        self.font_counter = font.Font(family="Arial", size=20, weight="bold")

        # Variables del juego
        self.vidas = 5
        self.premio = 0
        self.preguntas_restantes = list(preguntas.items())
        self.ecuacion_actual = None
        self.respuesta_correcta = None
        self.botones_opciones = []

        self.setup_ui()
        self.nueva_pregunta()

    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(pady=50, padx=40, fill="both", expand=True)

        # Título
        self.label_titulo = tk.Label(
            main_frame, 
            text="IDENTIFICA EL TIPO DE ECUACIÓN", 
            font=self.font_title, 
            fg="#ffffff",
            bg="#2c3e50"
        )
        self.label_titulo.pack(pady=30)

        # Ecuación
        self.label_ecuacion = tk.Label(
            main_frame, 
            text="", 
            font=self.font_question, 
            fg="#ffffff",
            bg="#2c3e50",
            wraplength=900  # Mayor wraplength para pantallas grandes
        )
        self.label_ecuacion.pack(pady=50)

        # Botones de opciones
        self.frame_opciones = tk.Frame(main_frame, bg="#2c3e50")
        self.frame_opciones.pack(pady=30)

        self.botones_opciones = []
        for i in range(4):
            btn = tk.Button(
                self.frame_opciones, 
                text="", 
                font=self.font_button, 
                width=25,  # Reducido para pantallas grandes
                bg="#3498db",
                fg="#ffffff",
                activebackground="#2980b9",
                relief=tk.RAISED,
                command=lambda idx=i: self.verificar_respuesta(idx)
            )
            btn.grid(row=i//2, column=i%2, pady=20, padx=20, sticky="ew")
            self.botones_opciones.append(btn)

        # Contadores
        self.frame_contadores = tk.Frame(main_frame, bg="#2c3e50")
        self.frame_contadores.pack(pady=40)

        self.label_vidas = tk.Label(
            self.frame_contadores, 
            text=f"Vidas: {self.vidas}", 
            font=self.font_counter, 
            fg="#ff6666",
            bg="#2c3e50"
        )
        self.label_vidas.grid(row=0, column=0, padx=50)

        self.label_premio = tk.Label(
            self.frame_contadores, 
            text=f"Premio: ${self.premio}", 
            font=self.font_counter, 
            fg="#66ff66",
            bg="#2c3e50"
        )
        self.label_premio.grid(row=0, column=1, padx=50)

        # Botón para reiniciar
        self.btn_reiniciar = tk.Button(
            main_frame,
            text="Reiniciar Juego",
            font=self.font_button,
            bg="#e67e22",
            fg="#ffffff",
            activebackground="#d35400",
            relief=tk.RAISED,
            command=self.reiniciar_juego
        )
        self.btn_reiniciar.pack(pady=40)

    def salir_pantalla_completa(self):
        self.root.attributes('-fullscreen', False)

    def nueva_pregunta(self):
        if not self.preguntas_restantes or self.vidas <= 0:
            mensaje_final = f"¡Juego terminado!\nAcumulaste: ${self.premio}"
            messagebox.showinfo("Fin del juego", mensaje_final)
            self.btn_reiniciar.config(state=tk.NORMAL)
            return

        self.ecuacion_actual, self.respuesta_correcta = random.choice(self.preguntas_restantes)
        self.preguntas_restantes.remove((self.ecuacion_actual, self.respuesta_correcta))
        
        self.label_ecuacion.config(text=f"Ecuación:\n{self.ecuacion_actual}")
        
        # Generar opciones
        tipos = list(set(preguntas.values()) - {self.respuesta_correcta})
        opciones = random.sample(tipos, 3) + [self.respuesta_correcta]
        random.shuffle(opciones)
        
        for i, btn in enumerate(self.botones_opciones):
            btn.config(text=opciones[i], state=tk.NORMAL, bg="#3498db")

    def verificar_respuesta(self, idx):
        respuesta_seleccionada = self.botones_opciones[idx].cget("text")
        
        # Resaltar respuesta seleccionada
        for btn in self.botones_opciones:
            btn.config(bg="#3498db")
        self.botones_opciones[idx].config(bg="#f1c40f")

        if respuesta_seleccionada == self.respuesta_correcta:
            self.premio += 1000
            self.label_premio.config(text=f"Premio: ${self.premio}")
            self.botones_opciones[idx].config(bg="#2ecc71")
            messagebox.showinfo("¡Correcto!", f"¡Respuesta correcta!\n+ $1000")
        else:
            self.vidas -= 1
            self.label_vidas.config(text=f"Vidas: {self.vidas}")
            self.botones_opciones[idx].config(bg="#e74c3c")
            messagebox.showerror("Incorrecto", f"La respuesta correcta era:\n{self.respuesta_correcta}")
        
        # Deshabilitar botones temporalmente
        for btn in self.botones_opciones:
            btn.config(state=tk.DISABLED)
        
        # Siguiente pregunta después de 1.5 segundos
        self.root.after(1500, self.nueva_pregunta)

    def reiniciar_juego(self):
        self.vidas = 5
        self.premio = 0
        self.preguntas_restantes = list(preguntas.items())
        self.label_vidas.config(text=f"Vidas: {self.vidas}")
        self.label_premio.config(text=f"Premio: ${self.premio}")
        self.btn_reiniciar.config(state=tk.DISABLED)
        self.nueva_pregunta()

# Iniciar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    game = MillionaireGame(root)
    root.mainloop()