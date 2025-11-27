import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd

# --- CONFIGURACIÓN VISUAL ---
ESTILO = {
    "bg_fondo": "#002b5c",
    "bg_respuesta": "#004080",
    "fg_texto": "#ffffff",
    "fg_puntos": "#ffcc00",
    "font_pregunta": ("Arial", 28, "bold"),
    "font_respuesta": ("Helvetica", 22, "bold"),
    "font_botones": ("Arial", 12, "bold")
}

class Juego100Colombianos:
    def __init__(self, root):
        self.root = root
        self.root.title("100 Estudiantes Dicen")
        self.root.configure(bg=ESTILO["bg_fondo"])
        self.root.state('zoomed') 
        
        # Teclas Flecha Derecha e Izquierda para mover
        self.root.bind('<Right>', lambda event: self.avanzar_pregunta())
        self.root.bind('<Left>', lambda event: self.retroceder_pregunta())

        self.preguntas = []
        self.pregunta_actual = 0
        self.respuestas_widgets = []
        
        # --- CARGAR ARCHIVO ---
        self.cargar_archivo()

        if not self.preguntas:
            return 

        # --- INTERFAZ ---
        self.frame_top = tk.Frame(root, bg=ESTILO["bg_fondo"])
        self.frame_top.pack(pady=20, fill='x')
        
        # CONTADOR
        self.lbl_contador = tk.Label(self.frame_top, text="Cargando...", font=("Arial", 16), bg="black", fg="#00ff00")
        self.lbl_contador.pack(side=tk.TOP, pady=5)

        self.label_pregunta = tk.Label(self.frame_top, text="", wraplength=1200, 
                                       font=ESTILO["font_pregunta"], bg=ESTILO["bg_fondo"], fg=ESTILO["fg_texto"])
        self.label_pregunta.pack(pady=10)

        self.frame_respuestas = tk.Frame(root, bg=ESTILO["bg_fondo"])
        self.frame_respuestas.pack(pady=10)
        self.crear_tablero_respuestas(4)

        self.frame_controles = tk.Frame(root, bg=ESTILO["bg_fondo"])
        self.frame_controles.pack(pady=20)
        
        self.botones_revelar = []
        for i, letra in enumerate(['A', 'B', 'C', 'D']):
            btn = tk.Button(self.frame_controles, text=f"Revelar {letra}", 
                            command=lambda idx=i: self.revelar_respuesta(idx),
                            font=ESTILO["font_botones"], bg="#28a745", fg="white", width=12)
            btn.grid(row=0, column=i, padx=10)
            self.botones_revelar.append(btn)

        btn_err = tk.Button(self.frame_controles, text="❌ ERROR", command=self.mostrar_error,
                           font=ESTILO["font_botones"], bg="#dc3545", fg="white")
        btn_err.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")

        self.frame_nav = tk.Frame(root, bg=ESTILO["bg_fondo"])
        self.frame_nav.pack(side=tk.BOTTOM, pady=30)

        tk.Button(self.frame_nav, text="⬅ Anterior", command=self.retroceder_pregunta, 
                  font=ESTILO["font_botones"], bg="orange").pack(side=tk.LEFT, padx=20)
        
        tk.Button(self.frame_nav, text="Siguiente ➡", command=self.avanzar_pregunta, 
                  font=ESTILO["font_botones"], bg="orange").pack(side=tk.LEFT, padx=20)

        self.mostrar_pregunta()

    def cargar_archivo(self):
        archivo = filedialog.askopenfilename(title="Seleccionar Excel", filetypes=[("Archivos Excel", "*.xlsx")])
        if not archivo:
            self.root.destroy()
            return
        try:
            df = pd.read_excel(archivo)
            
            # 1. Limpieza básica
            df = df.dropna(how='all') # Quitar filas vacías
            df = df.fillna('---')     # Rellenar celdas vacías
            
            # Limpiar nombres de columnas (quitar espacios extra: "usar " -> "usar")
            df.columns = df.columns.str.strip().str.lower() 

            # 2. VERIFICAR SI EXISTE LA COLUMNA 'usar'
            if 'usar' not in df.columns:
                messagebox.showerror("Error", "No se encontró la columna 'usar' en el Excel.\nPor favor agrégala y pon 'si' en las preguntas que quieras.")
                self.root.destroy()
                return

            # 3. FILTRADO: Solo dejar las que digan "si"
            # Convertimos a texto, minúsculas y quitamos espacios para asegurar que "Si ", "SI", "si" funcionen igual.
            df['usar'] = df['usar'].astype(str).str.lower().str.strip()
            df_filtrado = df[df['usar'] == 'si']

            print(f"Total filas en Excel: {len(df)}")
            print(f"Filas con 'si': {len(df_filtrado)}")

            if len(df_filtrado) == 0:
                messagebox.showwarning("Atención", "El archivo tiene la columna 'usar', pero ninguna fila dice 'si'.")
                self.root.destroy()
                return

            # 4. Cargar datos filtrados
            for index, row in df_filtrado.iterrows():
                # Nota: como pasamos las columnas a minúsculas, usamos 'pregunta', 'a', etc.
                # Si tus columnas en Excel son mayúsculas, pandas las convirtió a minúsculas arriba.
                try:
                    # Intentamos leer con nombres en minúscula (por la limpieza de arriba)
                    t_pregunta = row['pregunta']
                    resps = [
                        (row['a'], row['a%']), 
                        (row['b'], row['b%']), 
                        (row['c'], row['c%']), 
                        (row['d'], row['d%'])
                    ]
                except KeyError:
                    # Si falla, intentamos con Mayúscula inicial (por si acaso pandas no lo bajó)
                    # Pero como hicimos df.columns.str.lower(), deberían ser minúsculas.
                    # Asumimos estructura estándar:
                    t_pregunta = row.iloc[0] # Primera columna asumiendo es Pregunta
                    # Esto es un fallback arriesgado, mejor confiar en nombres.
                    messagebox.showerror("Error Columnas", "Asegúrate que las columnas se llamen: Pregunta, A, A%, B, B%...")
                    return

                pregunta = {
                    "pregunta": t_pregunta,
                    "respuestas": resps
                }
                self.preguntas.append(pregunta)
                
        except Exception as e:
            messagebox.showerror("Error Crítico", f"Error leyendo archivo: {e}")

    def crear_tablero_respuestas(self, cantidad):
        for i in range(cantidad):
            frame = tk.Frame(self.frame_respuestas, bg="white", bd=2)
            frame.pack(pady=5, padx=10, fill='x')
            lbl_t = tk.Label(frame, text="", width=40, font=ESTILO["font_respuesta"], 
                             bg=ESTILO["bg_respuesta"], fg=ESTILO["fg_texto"], anchor="w", padx=20)
            lbl_t.pack(side=tk.LEFT, fill='both', expand=True)
            lbl_p = tk.Label(frame, text="0", width=5, font=ESTILO["font_respuesta"], 
                             bg=ESTILO["bg_respuesta"], fg=ESTILO["fg_puntos"])
            lbl_p.pack(side=tk.RIGHT, fill='y')
            self.respuestas_widgets.append((lbl_t, lbl_p))

    def mostrar_pregunta(self):
        if not self.preguntas: return

        total = len(self.preguntas)
        actual = self.pregunta_actual + 1
        self.lbl_contador.config(text=f"PREGUNTA {actual} DE {total}")

        data = self.preguntas[self.pregunta_actual]
        self.label_pregunta.config(text=data["pregunta"])
        
        for i, (lbl_t, lbl_p) in enumerate(self.respuestas_widgets):
            lbl_t.config(text=f"{i+1} . [ OCULTO ]")
            lbl_p.config(text="--")
            
        for btn in self.botones_revelar:
            btn.config(state=tk.NORMAL, bg="#28a745")

    def revelar_respuesta(self, indice):
        data = self.preguntas[self.pregunta_actual]
        lbl_t, lbl_p = self.respuestas_widgets[indice]
        lbl_t.config(text=str(data['respuestas'][indice][0]).upper())
        lbl_p.config(text=str(data['respuestas'][indice][1]))
        self.botones_revelar[indice].config(state=tk.DISABLED, bg="gray")

    def avanzar_pregunta(self):
        if self.pregunta_actual < len(self.preguntas) - 1:
            self.pregunta_actual += 1
            self.mostrar_pregunta()
        else:
            messagebox.showinfo("Info", "¡Es la última pregunta marcada con 'si'!")

    def retroceder_pregunta(self):
        if self.pregunta_actual > 0:
            self.pregunta_actual -= 1
            self.mostrar_pregunta()

    def mostrar_error(self):
        top = tk.Toplevel(self.root)
        top.geometry("300x300")
        top.overrideredirect(True)
        top.geometry(f"+{self.root.winfo_x()+400}+{self.root.winfo_y()+200}")
        tk.Label(top, text="❌", font=("Arial", 150), fg="red", bg="black").pack(fill='both', expand=True)
        self.root.after(1000, top.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = Juego100Colombianos(root)
    root.mainloop()