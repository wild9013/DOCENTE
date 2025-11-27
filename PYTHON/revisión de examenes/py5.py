import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class ExamAnalysisApp:
    """
    Clase principal para la aplicación de análisis de exámenes.
    Gestiona la interfaz de usuario, la carga de datos y la visualización de resultados.
    """
    def __init__(self, root):
        """
        Inicializa la aplicación.
        Args:
            root (tk.Tk): La ventana principal de la aplicación.
        """
        self.root = root
        self.root.title("Herramienta de Análisis de Exámenes")
        self.root.geometry("850x600")

        # --- Atributos de datos ---
        self.df_students = None  # DataFrame para almacenar las respuestas de los estudiantes.
        self.correct_answers = None  # Lista con las respuestas correctas.
        self.results = []  # Lista de diccionarios con el análisis por pregunta.
        self.total_students = 0
        self.num_questions = 20  # Número de preguntas a analizar.

        # --- Estado de la interfaz ---
        self.current_question = 0  # Pregunta actualmente seleccionada.
        self.canvas = None  # Canvas para el gráfico de Matplotlib.

        # --- Estilos de la interfaz ---
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Arial', 10))
        self.style.configure("TLabel", font=('Arial', 11))

        # --- Construir la interfaz de usuario ---
        self.create_interface()

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
        self.lbl_question = ttk.Label(control_frame, text=f"Pregunta: 0/{self.num_questions}", font=('Arial', 12, 'bold'))
        self.lbl_question.pack(side=tk.LEFT, padx=20)

        # --- Frame de estadísticas (información de la pregunta) ---
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        self.lbl_summary = ttk.Label(stats_frame, text="Resumen: No hay datos cargados", font=('Arial', 10, 'bold'))
        self.lbl_summary.pack(anchor=tk.W, pady=2)
        self.lbl_correct = ttk.Label(stats_frame, text="Respuesta Correcta: -", font=('Arial', 10))
        self.lbl_correct.pack(anchor=tk.W, pady=2)
        self.lbl_correct_count = ttk.Label(stats_frame, text="Respuestas Correctas: - (-%)", font=('Arial', 10))
        self.lbl_correct_count.pack(anchor=tk.W, pady=2)
        self.lbl_distribution = ttk.Label(stats_frame, text="Distribución: -", font=('Arial', 10))
        self.lbl_distribution.pack(anchor=tk.W, pady=2)

        # --- Barra de progreso ---
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=10)

        # --- Frame inferior (lista de preguntas y gráfico) ---
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # --- Lista de preguntas ---
        listbox_frame = ttk.Frame(bottom_frame)
        listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.question_listbox = tk.Listbox(listbox_frame, height=20, width=30, font=('Arial', 10))
        self.question_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.question_listbox.bind('<<ListboxSelect>>', self.on_question_select)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.question_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.question_listbox.config(yscrollcommand=scrollbar.set)

        # --- Frame para el gráfico ---
        self.chart_frame = ttk.Frame(bottom_frame)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def load_excel(self):
        """Abre un diálogo para seleccionar un archivo Excel y carga los datos."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Archivo Excel",
            filetypes=[("Archivos de Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return  # El usuario canceló la selección.

        try:
            self.df_students, self.correct_answers = self.read_exam(file_path)
            self.results, self.total_students = self.analyze_questions()

            # --- Resetea y actualiza la interfaz con los nuevos datos ---
            self.current_question = 0
            self.update_interface()
            self.update_listbox()

            # --- Habilita los botones de navegación ---
            self.btn_prev.config(state=tk.NORMAL)
            self.btn_next.config(state=tk.NORMAL)
            self.btn_all_charts.config(state=tk.NORMAL)

            messagebox.showinfo("Éxito", "¡Archivo Excel cargado exitosamente!")

        except Exception as e:
            messagebox.showerror("Error", f"Fallo al cargar el archivo: {str(e)}")

    def read_exam(self, file_path):
        """
        Lee el archivo Excel y lo procesa en un DataFrame de pandas.
        Args:
            file_path (str): La ruta del archivo Excel.
        Returns:
            tuple: Un DataFrame con las respuestas de los estudiantes y una lista de respuestas correctas.
        """
        df = pd.read_excel(file_path, header=None, engine='openpyxl')

        if df.shape[1] < self.num_questions + 1:
            raise ValueError(f"El archivo Excel debe contener al menos {self.num_questions + 1} columnas.")

        # --- Extrae los nombres, respuestas correctas y respuestas de los estudiantes ---
        names = df.iloc[2:, 0].dropna().tolist()
        correct_answers = df.iloc[1, 1:self.num_questions + 1].tolist()
        student_responses = df.iloc[2:, 1:self.num_questions + 1]

        # --- Crea un DataFrame limpio y estructurado ---
        df_students = pd.DataFrame(
            student_responses.values,
            index=names,
            columns=[f"Q{i+1}" for i in range(self.num_questions)]
        )
        return df_students, correct_answers

    def analyze_questions(self):
        """Analiza las respuestas de cada pregunta para calcular estadísticas."""
        total_students = len(self.df_students)
        results = []

        # --- Limpia y estandariza las respuestas (elimina espacios y convierte a string) ---
        responses = self.df_students.astype(str).apply(lambda x: x.str.strip())

        for i in range(self.num_questions):
            question_col = f"Q{i+1}"
            correct_answer = str(self.correct_answers[i]).strip()

            # --- Cuenta la frecuencia de cada respuesta usando Counter ---
            response_counts = Counter(responses[question_col])
            
            # --- Asegura que todas las opciones posibles (1, 2, 3, 4) estén en el contador ---
            for option in ['1', '2', '3', '4']:
                response_counts.setdefault(option, 0)

            # --- Calcula el número y porcentaje de respuestas correctas ---
            correct_count = response_counts.get(correct_answer, 0)
            percentage = (correct_count / total_students * 100) if total_students > 0 else 0

            results.append({
                'number': i + 1,
                'correct': correct_answer,
                'correct_count': correct_count,
                'percentage': percentage,
                'distribution': dict(sorted(response_counts.items())),
                'options': sorted(response_counts.keys())
            })
        return results, total_students

    def create_chart(self, question):
        """
        Crea un gráfico de barras para la distribución de respuestas de una pregunta.
        Args:
            question (dict): Diccionario con los datos de la pregunta.
        Returns:
            matplotlib.figure.Figure: La figura del gráfico generado.
        """
        options = question['options']
        counts = [question['distribution'].get(opt, 0) for opt in options]
        # --- Colorea la barra de la respuesta correcta de un color diferente ---
        colors = ['#4CAF50' if opt == question['correct'] else '#2196F3' for opt in options]

        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(options, counts, color=colors)
        ax.set_title(f"Pregunta {question['number']} - Distribución de Respuestas")
        ax.set_xlabel("Opciones de Respuesta")
        ax.set_ylabel("Número de Estudiantes")
        ax.set_ylim(0, max(counts) * 1.2 if counts else 1)

        # --- Añade etiquetas de texto encima de cada barra ---
        for i, v in enumerate(counts):
            ax.text(i, v + 0.1, str(v), ha='center')

        plt.tight_layout()
        return fig

    def update_chart(self):
        """Actualiza el gráfico que se muestra en la interfaz principal."""
        # --- Limpia el gráfico anterior si existe ---
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        if not self.results:
            return

        # --- Crea y muestra el nuevo gráfico ---
        question = self.results[self.current_question]
        fig = self.create_chart(question)
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)  # Cierra la figura para liberar memoria.

    def show_all_charts(self):
        """Muestra todos los gráficos de las preguntas en ventanas separadas."""
        if not self.results:
            return
        for i in range(self.num_questions):
            question = self.results[i]
            fig = self.create_chart(question)
            fig.show()  # Muestra la figura en una nueva ventana.

    def update_interface(self):
        """Actualiza todas las etiquetas y widgets de la interfaz con los datos de la pregunta actual."""
        if not self.results:
            return

        question = self.results[self.current_question]

        # --- Encuentra la pregunta más fácil y la más difícil ---
        easiest = max(self.results, key=lambda x: x['percentage'])['number']
        hardest = min(self.results, key=lambda x: x['percentage'])['number']

        # --- Actualiza las etiquetas de texto ---
        self.lbl_summary.config(text=f"Resumen: {self.total_students} estudiantes | Más Fácil: P{easiest} | Más Difícil: P{hardest}")
        self.lbl_question.config(text=f"Pregunta: {question['number']}/{self.num_questions}")
        self.lbl_correct.config(text=f"Respuesta Correcta: Opción {question['correct']}")
        self.lbl_correct_count.config(text=f"Respuestas Correctas: {question['correct_count']} ({question['percentage']:.1f}%)")
        dist_text = " | ".join([f"Opción {k}: {v}" for k, v in question['distribution'].items()])
        self.lbl_distribution.config(text=f"Distribución: {dist_text}")

        # --- Actualiza la barra de progreso ---
        self.progress['value'] = (self.current_question + 1) / self.num_questions * 100

        # --- Habilita o deshabilita los botones de navegación ---
        self.btn_prev.config(state=tk.NORMAL if self.current_question > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_question < self.num_questions - 1 else tk.DISABLED)

        # --- Actualiza el gráfico ---
        self.update_chart()

    def update_listbox(self):
        """Actualiza la lista de preguntas con sus porcentajes de acierto."""
        self.question_listbox.delete(0, tk.END)
        for i in range(self.num_questions):
            percentage = self.results[i]['percentage'] if self.results else 0
            self.question_listbox.insert(tk.END, f"Pregunta {i + 1}: {percentage:.1f}%")
        
        # --- Selecciona la pregunta actual en la lista ---
        self.question_listbox.select_set(self.current_question)

    def on_question_select(self, event):
        """
        Se ejecuta cuando el usuario selecciona una pregunta de la lista.
        Args:
            event: El evento de selección de la Listbox.
        """
        selection = self.question_listbox.curselection()
        if selection:
            self.current_question = selection[0]
            self.update_interface()

    def next_question(self):
        """Navega a la siguiente pregunta."""
        if self.current_question < self.num_questions - 1:
            self.current_question += 1
            self.question_listbox.select_clear(0, tk.END)
            self.question_listbox.select_set(self.current_question)
            self.update_interface()

    def previous_question(self):
        """Navega a la pregunta anterior."""
        if self.current_question > 0:
            self.current_question -= 1
            self.question_listbox.select_clear(0, tk.END)
            self.question_listbox.select_set(self.current_question)
            self.update_interface()

if __name__ == "__main__":
    """
    Punto de entrada principal de la aplicación.
    Crea la ventana raíz de Tkinter y la instancia de la aplicación.
    """
    root = tk.Tk()
    app = ExamAnalysisApp(root)
    root.mainloop()