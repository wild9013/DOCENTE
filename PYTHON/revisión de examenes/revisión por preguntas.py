import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns  # Importar Seaborn

class ExamAnalysisApp:
    """
    Clase principal para la aplicación de análisis de exámenes.
    Gestiona la interfaz de usuario, la carga de datos y la visualización de resultados.
    """
    # --- Constantes para la estructura del archivo Excel ---
    # Esto hace que el código sea más fácil de mantener si el formato del Excel cambia.
    NAMES_COLUMN = 0
    CORRECT_ANSWERS_ROW = 1
    START_DATA_ROW = 2
    START_QUESTIONS_COL = 1

    def __init__(self, root):
        """
        Inicializa la aplicación.
        Args:
            root (tk.Tk): La ventana principal de la aplicación.
        """
        self.root = root
        self.root.title("Herramienta de Análisis de Exámenes (Optimizada con Seaborn)")
        self.root.geometry("900x650")

        # --- Atributos de datos ---
        self.df_students = None
        self.correct_answers = None
        self.results = []
        self.total_students = 0
        self.num_questions = 20
        self.easiest_question = None  # Almacenará la pregunta más fácil (optimización)
        self.hardest_question = None  # Almacenará la pregunta más difícil (optimización)

        # --- Estado y Estilos de la interfaz ---
        self.current_question = 0
        self.canvas = None
        self.setup_styles()

        # --- Construir la interfaz de usuario ---
        self.create_interface()
        
    def setup_styles(self):
        """Configura los estilos para los widgets ttk."""
        self.style = ttk.Style()
        self.style.theme_use('clam') # Un tema moderno
        self.style.configure("TButton", padding=6, font=('Segoe UI', 10))
        self.style.configure("TLabel", font=('Segoe UI', 11))
        self.style.configure("Header.TLabel", font=('Segoe UI', 12, 'bold'))
        self.style.configure("Summary.TLabel", font=('Segoe UI', 10, 'bold'))

    def create_interface(self):
        """Crea y organiza todos los widgets de la interfaz gráfica."""
        # --- Frame principal ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Frame de controles (botones y etiquetas superiores) ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        ttk.Button(control_frame, text="Cargar Archivo Excel", command=self.load_excel).pack(side=tk.LEFT, padx=5)
        self.btn_prev = ttk.Button(control_frame, text="← Anterior", command=self.previous_question, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, padx=5)
        self.btn_next = ttk.Button(control_frame, text="Siguiente →", command=self.next_question, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, padx=5)
        self.btn_all_charts = ttk.Button(control_frame, text="Mostrar Todos los Gráficos", command=self.show_all_charts, state=tk.DISABLED)
        self.btn_all_charts.pack(side=tk.LEFT, padx=5)
        self.lbl_question = ttk.Label(control_frame, text=f"Pregunta: 0/{self.num_questions}", style="Header.TLabel")
        self.lbl_question.pack(side=tk.LEFT, padx=20)

        # --- Frame de estadísticas ---
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        self.lbl_summary = ttk.Label(stats_frame, text="Resumen: No hay datos cargados", style="Summary.TLabel")
        self.lbl_summary.pack(anchor=tk.W, pady=2)
        self.lbl_correct = ttk.Label(stats_frame, text="Respuesta Correcta: -")
        self.lbl_correct.pack(anchor=tk.W, pady=2)
        self.lbl_correct_count = ttk.Label(stats_frame, text="Respuestas Correctas: - (-%)")
        self.lbl_correct_count.pack(anchor=tk.W, pady=2)
        self.lbl_distribution = ttk.Label(stats_frame, text="Distribución: -")
        self.lbl_distribution.pack(anchor=tk.W, pady=2)

        # --- Barra de progreso ---
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=10)

        # --- Frame inferior (lista y gráfico) ---
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        listbox_frame = ttk.Frame(bottom_frame)
        listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.question_listbox = tk.Listbox(listbox_frame, height=20, width=30, font=('Segoe UI', 10), borderwidth=0, highlightthickness=0)
        self.question_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.question_listbox.bind('<<ListboxSelect>>', self.on_question_select)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.question_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.question_listbox.config(yscrollcommand=scrollbar.set)

        self.chart_frame = ttk.Frame(bottom_frame)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def load_excel(self):
        """Abre un diálogo para seleccionar un archivo Excel y procesa los datos."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Archivo Excel",
            filetypes=[("Archivos de Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            self.df_students, self.correct_answers = self.read_exam(file_path)
            self.analyze_questions() # El análisis ahora también calcula las estadísticas de resumen

            self.current_question = 0
            self.update_interface()
            self.update_listbox()
            self.enable_controls()

            messagebox.showinfo("Éxito", "¡Archivo Excel cargado exitosamente!")

        except Exception as e:
            messagebox.showerror("Error", f"Fallo al cargar el archivo: {str(e)}")

    def read_exam(self, file_path):
        """
        Lee el archivo Excel usando las constantes de clase para mayor claridad.
        """
        df = pd.read_excel(file_path, header=None, engine='openpyxl')

        if df.shape[1] < self.num_questions + 1:
            raise ValueError(f"El archivo Excel debe contener al menos {self.num_questions + 1} columnas de preguntas.")

        names = df.iloc[self.START_DATA_ROW:, self.NAMES_COLUMN].dropna().tolist()
        correct_answers = df.iloc[self.CORRECT_ANSWERS_ROW, self.START_QUESTIONS_COL : self.START_QUESTIONS_COL + self.num_questions].tolist()
        student_responses = df.iloc[self.START_DATA_ROW:, self.START_QUESTIONS_COL : self.START_QUESTIONS_COL + self.num_questions]

        df_students = pd.DataFrame(
            student_responses.values,
            index=names,
            columns=[f"Q{i+1}" for i in range(self.num_questions)]
        )
        return df_students, correct_answers

    def analyze_questions(self):
        """
        Analiza las respuestas y calcula todas las estadísticas necesarias,
        incluyendo las preguntas más fáciles y difíciles (optimización).
        """
        self.total_students = len(self.df_students)
        self.results = []
        responses = self.df_students.astype(str).apply(lambda x: x.str.strip())

        for i in range(self.num_questions):
            question_col = f"Q{i+1}"
            correct_answer = str(self.correct_answers[i]).strip()

            response_counts = Counter(responses[question_col])
            for option in ['1', '2', '3', '4']:
                response_counts.setdefault(option, 0)

            correct_count = response_counts.get(correct_answer, 0)
            percentage = (correct_count / self.total_students * 100) if self.total_students > 0 else 0

            self.results.append({
                'number': i + 1,
                'correct': correct_answer,
                'correct_count': correct_count,
                'percentage': percentage,
                'distribution': dict(sorted(response_counts.items())),
            })
        
        # --- OPTIMIZACIÓN: Calcular estadísticas de resumen una sola vez ---
        if self.results:
            self.easiest_question = max(self.results, key=lambda x: x['percentage'])['number']
            self.hardest_question = min(self.results, key=lambda x: x['percentage'])['number']


    def create_chart_with_seaborn(self, question):
        """
        Crea un gráfico de barras estéticamente mejorado usando Seaborn.
        """
        distribution = question['distribution']
        correct_answer = question['correct']
        
        # --- Prepara los datos para Seaborn ---
        df_chart = pd.DataFrame(list(distribution.items()), columns=['Opción', 'Conteo'])
        
        # --- Crea una paleta de colores para resaltar la respuesta correcta ---
        palette = {opt: '#2ecc71' if opt == correct_answer else '#3498db' for opt in df_chart['Opción']}

        # --- Crea la figura y el eje de Matplotlib ---
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # --- Usa Seaborn para crear el gráfico ---
        sns.barplot(x='Opción', y='Conteo', data=df_chart, ax=ax, palette=palette, dodge=False)

        ax.set_title(f"Pregunta {question['number']} - Distribución de Respuestas", fontsize=12)
        ax.set_xlabel("Opciones de Respuesta", fontsize=10)
        ax.set_ylabel("Número de Estudiantes", fontsize=10)
        
        # Asegura que el eje Y comience en 0 y tenga algo de espacio arriba
        if not df_chart['Conteo'].empty:
            ax.set_ylim(0, df_chart['Conteo'].max() * 1.15)
        
        # --- Añade etiquetas de texto encima de cada barra ---
        for bar in ax.patches:
            ax.annotate(f'{int(bar.get_height())}',
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                        ha='center', va='bottom',
                        size=10, xytext=(0, 5),
                        textcoords='offset points')
                        
        sns.despine() # Remueve los bordes superior y derecho del gráfico
        plt.tight_layout()
        return fig

    def update_chart(self):
        """Actualiza el widget del gráfico en la interfaz."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if not self.results:
            return

        question = self.results[self.current_question]
        # --- Llama a la nueva función de creación de gráficos ---
        fig = self.create_chart_with_seaborn(question)
        
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def show_all_charts(self):
        """Muestra todos los gráficos en ventanas separadas."""
        if not self.results: return
        for question in self.results:
            fig = self.create_chart_with_seaborn(question)
            fig.show()

    def update_interface(self):
        """Actualiza todas las etiquetas y widgets con los datos actuales."""
        if not self.results: return

        question = self.results[self.current_question]
        
        # --- Usa las estadísticas pre-calculadas ---
        summary_text = f"Resumen: {self.total_students} estudiantes | Más Fácil: P{self.easiest_question} | Más Difícil: P{self.hardest_question}"
        self.lbl_summary.config(text=summary_text)
        
        self.lbl_question.config(text=f"Pregunta: {question['number']}/{self.num_questions}")
        self.lbl_correct.config(text=f"Respuesta Correcta: Opción {question['correct']}")
        self.lbl_correct_count.config(text=f"Respuestas Correctas: {question['correct_count']} ({question['percentage']:.1f}%)")
        dist_text = " | ".join([f"Opción {k}: {v}" for k, v in question['distribution'].items()])
        self.lbl_distribution.config(text=f"Distribución: {dist_text}")

        self.progress['value'] = (self.current_question + 1) / self.num_questions * 100
        
        self.update_chart()

    def update_listbox(self):
        """Actualiza la lista de preguntas."""
        self.question_listbox.delete(0, tk.END)
        for i, res in enumerate(self.results):
            self.question_listbox.insert(tk.END, f"Pregunta {res['number']}: {res['percentage']:.1f}%")
            # Colorea la entrada de la lista basado en el % de acierto
            if res['percentage'] >= 75:
                self.question_listbox.itemconfig(i, {'bg':'#e8f5e9'}) # Verde claro
            elif res['percentage'] <= 40:
                self.question_listbox.itemconfig(i, {'bg':'#ffebee'}) # Rojo claro
        
        self.question_listbox.select_set(self.current_question)

    def on_question_select(self, event):
        selection = self.question_listbox.curselection()
        if selection and self.current_question != selection[0]:
            self.current_question = selection[0]
            self.update_interface()
            self.update_navigation_buttons()

    def next_question(self):
        if self.current_question < self.num_questions - 1:
            self.current_question += 1
            self.update_selection_and_interface()

    def previous_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.update_selection_and_interface()
            
    def update_selection_and_interface(self):
        """Centraliza la lógica para actualizar la selección y la UI."""
        self.question_listbox.select_clear(0, tk.END)
        self.question_listbox.select_set(self.current_question)
        self.question_listbox.see(self.current_question) # Asegura que la selección sea visible
        self.update_interface()
        self.update_navigation_buttons()
    
    def enable_controls(self):
        """Habilita los controles de navegación."""
        self.btn_all_charts.config(state=tk.NORMAL)
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Actualiza el estado de los botones 'Anterior' y 'Siguiente'."""
        self.btn_prev.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_question < self.num_questions - 1 else tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExamAnalysisApp(root)
    root.mainloop()