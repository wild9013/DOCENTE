import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog
import random

class AplicacionPreguntas:
    def __init__(self, root, preguntas):
        self.root = root
        self.preguntas = preguntas
        self.total_preguntas = len(preguntas)
        self.puntaje = 0
        self.index_pregunta = 0
        self.bloquear_botones = False # Para evitar doble clic mientras se espera

        # Configuración de la ventana principal
        self.root.title("Quiz Educativo: Deberes y Derechos")
        self.root.geometry("800x500")
        self.root.configure(bg="#f0f0f0") # Fondo gris suave
        
        # Centrar ventana en pantalla
        self.centrar_ventana()
        
        # Crear interfaz
        self.crear_widgets()
        self.mostrar_pregunta()

    def centrar_ventana(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def crear_widgets(self):
        # Fuentes
        fuente_pregunta = ('Helvetica', 24, 'bold')
        fuente_boton = ('Helvetica', 18)
        fuente_info = ('Helvetica', 12)

        # Panel Superior (Info de progreso)
        self.frame_info = tk.Frame(self.root, bg="#f0f0f0")
        self.frame_info.pack(pady=10, fill='x', padx=20)
        
        self.lbl_progreso = tk.Label(self.frame_info, text="", font=fuente_info, bg="#f0f0f0", fg="#555")
        self.lbl_progreso.pack(side=tk.LEFT)
        
        self.lbl_puntaje = tk.Label(self.frame_info, text="Puntaje: 0", font=fuente_info, bg="#f0f0f0", fg="#333")
        self.lbl_puntaje.pack(side=tk.RIGHT)

        # Pregunta
        self.lbl_pregunta = tk.Label(self.root, text="", font=fuente_pregunta, 
                                     wraplength=700, justify="center", bg="#f0f0f0")
        self.lbl_pregunta.pack(pady=40, expand=True)

        # Feedback (Mensaje de correcto/incorrecto)
        self.lbl_feedback = tk.Label(self.root, text="", font=('Helvetica', 16, 'bold'), bg="#f0f0f0")
        self.lbl_feedback.pack(pady=10)

        # Botones
        self.frame_botones = tk.Frame(self.root, bg="#f0f0f0")
        self.frame_botones.pack(pady=40)

        # Botón Verdadero (Verde)
        self.btn_verdadero = tk.Button(self.frame_botones, text="Verdadero", font=fuente_boton, 
                                       bg="#4CAF50", fg="white", activebackground="#45a049",
                                       width=12, command=lambda: self.verificar_respuesta('V'))
        self.btn_verdadero.pack(side=tk.LEFT, padx=30)

        # Botón Falso (Rojo)
        self.btn_falso = tk.Button(self.frame_botones, text="Falso", font=fuente_boton, 
                                   bg="#f44336", fg="white", activebackground="#d32f2f",
                                   width=12, command=lambda: self.verificar_respuesta('F'))
        self.btn_falso.pack(side=tk.RIGHT, padx=30)

    def mostrar_pregunta(self):
        if self.index_pregunta < len(self.preguntas):
            # Actualizar datos
            pregunta_actual = self.preguntas[self.index_pregunta]
            texto_pregunta = pregunta_actual.get('Pregunta', 'Error en pregunta')
            
            # Actualizar UI
            self.lbl_pregunta.config(text=texto_pregunta)
            self.lbl_progreso.config(text=f"Pregunta {self.index_pregunta + 1} de {self.total_preguntas}")
            self.lbl_feedback.config(text="", fg="black") # Limpiar feedback
            self.bloquear_botones = False
        else:
            self.mostrar_resumen()

    def verificar_respuesta(self, respuesta_usuario):
        if self.bloquear_botones: return
        self.bloquear_botones = True

        respuesta_correcta = str(self.preguntas[self.index_pregunta].get('Respuesta', '')).strip().upper()
        
        # Lógica de validación (soporta V/F o Verdadero/Falso en el excel)
        es_correcto = False
        if respuesta_usuario == 'V' and respuesta_correcta in ['V', 'VERDADERO', 'TRUE']:
            es_correcto = True
        elif respuesta_usuario == 'F' and respuesta_correcta in ['F', 'FALSO', 'FALSE']:
            es_correcto = True

        if es_correcto:
            self.puntaje += 1
            self.lbl_puntaje.config(text=f"Puntaje: {self.puntaje}")
            self.lbl_feedback.config(text="¡Correcto!", fg="green")
            self.root.configure(bg="#e8f5e9") # Flash verde suave
        else:
            self.lbl_feedback.config(text="Incorrecto", fg="red")
            self.root.configure(bg="#ffebee") # Flash rojo suave

        self.index_pregunta += 1
        # Esperar 1.5 segundos antes de mostrar la siguiente pregunta
        self.root.after(1500, self.restaurar_y_avanzar)

    def restaurar_y_avanzar(self):
        self.root.configure(bg="#f0f0f0") # Restaurar fondo
        self.mostrar_pregunta()

    def mostrar_resumen(self):
        # Limpiar ventana para mostrar resultados
        for widget in self.root.winfo_children():
            widget.destroy()
            
        frame_resumen = tk.Frame(self.root, bg="#f0f0f0")
        frame_resumen.pack(expand=True)
        
        tk.Label(frame_resumen, text="¡Juego Terminado!", font=('Helvetica', 30, 'bold'), bg="#f0f0f0", fg="#333").pack(pady=20)
        
        porcentaje = (self.puntaje / self.total_preguntas) * 100
        color_nota = "green" if porcentaje >= 60 else "red"
        
        tk.Label(frame_resumen, text=f"Tu puntaje final:", font=('Helvetica', 20), bg="#f0f0f0").pack()
        tk.Label(frame_resumen, text=f"{self.puntaje} / {self.total_preguntas}", font=('Helvetica', 40, 'bold'), fg=color_nota, bg="#f0f0f0").pack(pady=10)
        
        btn_salir = tk.Button(frame_resumen, text="Salir", font=('Helvetica', 16), command=self.root.quit, bg="#555", fg="white")
        btn_salir.pack(pady=30)

# --- Funciones Auxiliares ---

def leer_preguntas(archivo_excel):
    df = pd.read_excel(archivo_excel)
    # Validar columnas
    columnas_necesarias = ['Pregunta', 'Respuesta']
    if not all(col in df.columns for col in columnas_necesarias):
        raise ValueError(f"El Excel debe tener las columnas: {columnas_necesarias}")
    
    preguntas = df.to_dict(orient='records')
    random.shuffle(preguntas)
    return preguntas

def main():
    root = tk.Tk()
    root.withdraw() # Ocultar ventana inicial

    archivo_excel = filedialog.askopenfilename(
        filetypes=[("Archivos Excel", "*.xlsx")],
        title="Selecciona el archivo de preguntas"
    )

    if not archivo_excel:
        return # Usuario canceló

    try:
        preguntas = leer_preguntas(archivo_excel)
        root.deiconify() # Mostrar ventana
        app = AplicacionPreguntas(root, preguntas)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")
        root.destroy()

if __name__ == "__main__":
    main()