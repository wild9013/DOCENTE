import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

class CurriculumSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Selector de Currículo Matemático")
        self.root.geometry("800x600")
        self.df = None
        self.grade_var = tk.StringVar()
        self.topic_var = tk.StringVar()
        self.setup_ui()

    def setup_ui(self):
        # Frame para cargar archivo
        file_frame = ttk.LabelFrame(self.root, text="Cargar Archivo Excel", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(file_frame, text="Seleccionar Archivo", command=self.load_file).pack(pady=5)

        # Frame para selección de grado y temática
        selection_frame = ttk.LabelFrame(self.root, text="Selección", padding=10)
        selection_frame.pack(fill="x", padx=10, pady=5)

        # Selección de grado
        ttk.Label(selection_frame, text="Grado:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.grade_combo = ttk.Combobox(selection_frame, textvariable=self.grade_var, state="readonly")
        self.grade_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.grade_combo.bind("<<ComboboxSelected>>", self.update_topics)

        # Selección de temática
        ttk.Label(selection_frame, text="Eje Temático:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.topic_combo = ttk.Combobox(selection_frame, textvariable=self.topic_var, state="readonly")
        self.topic_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.topic_combo.bind("<<ComboboxSelected>>", self.display_data)

        # Botón de búsqueda
        ttk.Button(selection_frame, text="Buscar", command=self.display_data).grid(row=2, column=0, columnspan=2, pady=10)

        # Frame para mostrar resultados
        result_frame = ttk.LabelFrame(self.root, text="Resultados", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Campos de resultados
        self.result_fields = {}
        fields = [
            "Área", "Grado", "Período", "Semana", "Eje Temático", "DBA", "Descripción DBA",
            "Competencia/Afirmación", "Pensamiento", "Materiales",
            "Aprendizaje/Matriz de Referencia", "Evidencias/Matriz de Referencia"
        ]
        for i, field in enumerate(fields):
            ttk.Label(result_frame, text=f"{field}:").grid(row=i, column=0, padx=5, pady=2, sticky="e")
            text = tk.Text(result_frame, height=2, width=50, wrap="word")
            text.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            text.config(state="disabled")
            self.result_fields[field] = text

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return

        try:
            self.df = pd.read_excel(file_path)
            self.update_grades()
            messagebox.showinfo("Éxito", "Archivo cargado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")

    def update_grades(self):
        if self.df is not None:
            grades = sorted(self.df['grado'].dropna().unique())
            self.grade_combo['values'] = grades
            self.grade_var.set('')
            self.topic_combo['values'] = []
            self.topic_var.set('')
            self.clear_results()

    def update_topics(self, event=None):
        if self.df is not None and self.grade_var.get():
            grade = self.grade_var.get()
            topics = sorted(self.df[self.df['grado'] == grade]['eje tematico (numeros)'].dropna().unique())
            self.topic_combo['values'] = topics
            self.topic_var.set('')
            self.clear_results()

    def display_data(self, event=None):
        if self.df is None or not self.grade_var.get() or not self.topic_var.get():
            messagebox.showwarning("Advertencia", "Por favor, cargue un archivo y seleccione grado y eje temático.")
            return

        grade = self.grade_var.get()
        topic = self.topic_var.get()

        # Filtrar datos
        result = self.df[
            (self.df['grado'].astype(str).str.lower() == str(grade).lower()) &
            (self.df['eje tematico (numeros)'].astype(str).str.lower() == str(topic).lower())
        ]

        self.clear_results()

        if not result.empty:
            row = result.iloc[0]
            field_mapping = {
                "Área": "área",
                "Grado": "grado",
                "Período": "período",
                "Semana": "semana",
                "Eje Temático": "eje tematico (numeros)",
                "DBA": "dba",
                "Descripción DBA": "dba descripción",
                "Competencia/Afirmación": "competencia/afirmacion",
                "Pensamiento": "pensamiento",
                "Materiales": "materiales",
                "Aprendizaje/Matriz de Referencia": "aprendizaje / matriz de referencia",
                "Evidencias/Matriz de Referencia": "evidencias / matriz de referencia"
            }

            for display_field, col_name in field_mapping.items():
                text = self.result_fields[display_field]
                text.config(state="normal")
                text.delete("1.0", tk.END)
                value = str(row.get(col_name, "") if pd.notna(row.get(col_name)) else "")
                text.insert(tk.END, value)
                text.config(state="disabled")
        else:
            messagebox.showinfo("Sin Resultados", "No se encontraron datos para los criterios seleccionados.")

    def clear_results(self):
        for text in self.result_fields.values():
            text.config(state="normal")
            text.delete("1.0", tk.END)
            text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurriculumSelectorApp(root)
    root.mainloop()