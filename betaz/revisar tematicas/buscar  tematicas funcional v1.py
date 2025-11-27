import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd


class CurriculumSelectorApp:
    """Application for selecting mathematical curriculum data from an Excel file."""

    FIELD_MAPPING_DISPLAYED = {
        "Área": "área",
        "Grado": "grado",
        "Período": "período",
        "Eje Temático": "eje tematico (numeros)",
        "Descripción DBA": "dba descripción",
        "Competencia/Afirmación": "competencia/afirmacion",
        "Pensamiento": "pensamiento",
        "Materiales": "materiales",
        "Aprendizaje/Matriz de Referencia": "aprendizaje / matriz de referencia",
        "Evidencias/Matriz de Referencia": "evidencias / matriz de referencia",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Selector de Currículo Matemático")
        self.root.geometry("850x600")  # Further adjusted initial size
        self.root.minsize(750, 500)
        self.df = None
        self.grade_var = tk.StringVar()
        self.period_var = tk.StringVar()
        self.topic_var = tk.StringVar()
        self.available_topics = []
        self.result_labels = {}
        self.status_var = tk.StringVar(value="Cargue un archivo Excel para comenzar.")
        self.style = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize and configure the user interface with refined aesthetics and layout."""
        self.root.configure(bg="#f0f0f0")  # Light gray background
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Modern theme
        self.style.configure("TButton", padding=8, font=("Segoe UI", 10), relief="raised")
        self.style.configure("TLabel", font=("Segoe UI", 10), background="#f0f0f0")
        self.style.configure("TLabelframe", background="#f0f0f0", borderwidth=2, relief="groove", padding=10)
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), background="#f0f0f0")
        self.style.configure("TCombobox", font=("Segoe UI", 10), state="readonly")
        self.style.configure("TEntry", font=("Segoe UI", 10))

        # Main container with more padding
        main_frame = ttk.Frame(self.root, padding=20, style="TFrame")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)

        # --- Top Section (File Selection and Filters - Horizontal Layout) ---
        top_frame = ttk.Frame(main_frame, style="TFrame")
        top_frame.pack(fill="x", pady=(0, 15))
        top_frame.columnconfigure(0, weight=1)  # File selection area
        top_frame.columnconfigure(1, weight=2)  # Filters area

        # File Selection
        file_frame = ttk.LabelFrame(top_frame, text="Archivo", padding=10)
        file_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="ew")
        ttk.Button(file_frame, text="Seleccionar Archivo Excel", command=self.load_file, style="TButton").pack(
            fill="x", padx=5, pady=5
        )

        # Filters
        filter_frame = ttk.LabelFrame(top_frame, text="Filtros", padding=10)
        filter_frame.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="ew")
        filter_frame.columnconfigure(0, weight=0)  # Label column
        filter_frame.columnconfigure(1, weight=1)  # Input column

        ttk.Label(filter_frame, text="Grado:").grid(row=0, column=0, padx=5, pady=3, sticky="ew")
        self.grade_combo = ttk.Combobox(filter_frame, textvariable=self.grade_var)
        self.grade_combo.grid(row=0, column=1, padx=5, pady=3, sticky="ew")
        self.grade_combo.bind("<<ComboboxSelected>>", self.update_periods_and_topics)

        ttk.Label(filter_frame, text="Período:").grid(row=1, column=0, padx=5, pady=3, sticky="ew")
        self.period_combo = ttk.Combobox(filter_frame, textvariable=self.period_var)
        self.period_combo.grid(row=1, column=1, padx=5, pady=3, sticky="ew")
        self.period_combo.bind("<<ComboboxSelected>>", self.update_topics)

        ttk.Label(filter_frame, text="Eje Temático:").grid(row=2, column=0, padx=5, pady=3, sticky="ew")
        topic_input_frame = ttk.Frame(filter_frame, style="TFrame")
        topic_input_frame.grid(row=2, column=1, padx=5, pady=3, sticky="ew")
        topic_input_frame.columnconfigure(0, weight=1)
        topic_input_frame.columnconfigure(1, weight=0)

        self.topic_entry = ttk.Entry(topic_input_frame, textvariable=self.topic_var)
        self.topic_entry.grid(row=0, column=0, sticky="ew")
        self.topic_combo = ttk.Combobox(topic_input_frame, textvariable=self.topic_var)
        self.topic_combo.grid(row=0, column=1, padx=5, sticky="ew")
        self.topic_combo.bind("<<ComboboxSelected>>", self.display_data)
        self.topic_var.trace("w", self.filter_topics)

        ttk.Button(filter_frame, text="Buscar", command=self.display_data, style="TButton").grid(
            row=3, column=0, columnspan=2, pady=10, sticky="ew", padx=5
        )

        # --- Results Section (Grid Layout) ---
        result_frame = ttk.LabelFrame(main_frame, text="Resultados", padding=10)
        result_frame.pack(fill="both", expand=True, pady=(0, 10))
        self.results_grid = ttk.Frame(result_frame, style="TFrame")
        self.results_grid.pack(fill="both", expand=True)
        self.results_grid.columnconfigure(0, weight=0)  # Label column
        self.results_grid.columnconfigure(1, weight=1)  # Value column

        # Initialize result labels
        for i, field in enumerate(self.FIELD_MAPPING_DISPLAYED.keys()):
            ttk.Label(self.results_grid, text=f"{field}:", anchor="e").grid(
                row=i, column=0, padx=5, pady=3, sticky="ew"
            )
            label = ttk.Label(self.results_grid, text="", wraplength=400, anchor="w", justify="left")
            label.grid(row=i, column=1, padx=5, pady=3, sticky="ew")
            self.result_labels[field] = label

        # --- Status Bar ---
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken", anchor="w", padding=5)
        status_bar.pack(fill="x", pady=(5, 0))

    def load_file(self):
        """Load an Excel file and update grade options."""
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return

        try:
            self.df = pd.read_excel(file_path)
            self.update_grades()
            self.status_var.set("Archivo cargado correctamente.")
            messagebox.showinfo("Éxito", "Archivo cargado correctamente.")
        except Exception as e:
            self.status_var.set("Error al cargar el archivo.")
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")

    def update_grades(self):
        """Update grade dropdown with unique values from the DataFrame."""
        if self.df is not None:
            grades = sorted(self.df['grado'].dropna().unique())
            self.grade_combo['values'] = grades
            self.grade_var.set("")
            self.period_combo['values'] = []
            self.period_var.set("")
            self.topic_combo['values'] = []
            self.topic_var.set("")
            self.available_topics = []
            self.clear_results()
            self.status_var.set("Seleccione un grado para continuar.")

    def update_periods_and_topics(self, event=None):
        """Update period and topic dropdowns based on selected grade."""
        if self.df is not None and self.grade_var.get():
            grade = self.grade_var.get()
            periods = sorted(self.df[self.df['grado'] == grade]['período'].dropna().unique())
            self.period_combo['values'] = periods
            self.period_var.set("")
            self.update_topics()
        else:
            self.period_combo['values'] = []
            self.period_var.set("")
            self.topic_combo['values'] = []
            self.topic_var.set("")
            self.available_topics = []
            self.clear_results()
            self.status_var.set("Seleccione un grado para continuar.")

    def update_topics(self, event=None):
        """Update topic dropdown based on selected grade and period."""
        if self.df is not None and self.grade_var.get():
            grade = self.grade_var.get()
            query = self.df['grado'] == grade
            if self.period_var.get():
                period = self.period_var.get()
                query &= (self.df['período'] == period)
            topics = sorted(self.df[query]['eje tematico (numeros)'].dropna().unique())
            self.available_topics = topics
            self.topic_combo['values'] = topics
            if not self.topic_var.get():
                self.topic_var.set("")
            self.clear_results()
            self.status_var.set("Seleccione o ingrese un eje temático.")
        else:
            self.topic_combo['values'] = []
            self.topic_var.set("")
            self.available_topics = []
            self.clear_results()
            self.status_var.set("Seleccione un grado para continuar.")

    def filter_topics(self, *args):
        """Filter topics in the Combobox based on typed text."""
        if self.df is not None and self.grade_var.get():
            typed_text = self.topic_var.get().strip().lower()
            if typed_text:
                typed_words = typed_text.split()
                filtered_topics = [
                    topic for topic in self.available_topics if any(word in str(topic).lower() for word in typed_words)
                ]
                self.topic_combo['values'] = filtered_topics
            else:
                self.topic_combo['values'] = self.available_topics
        else:
            self.topic_combo['values'] = []
            self.topic_combo.set("")

    def display_data(self, event=None):
        """Display data for the selected or typed topic."""
        if self.df is None or not self.grade_var.get():
            self.status_var.set("Cargue un archivo y seleccione un grado.")
            messagebox.showwarning("Advertencia", "Por favor, cargue un archivo y seleccione un grado.")
            return

        topic = self.topic_var.get().strip()
        if not topic:
            self.status_var.set("Ingrese o seleccione un eje temático.")
            messagebox.showwarning("Advertencia", "Por favor, ingrese o seleccione un eje temático.")
            return

        self.status_var.set("Buscando datos...")
        grade = self.grade_var.get()
        period = self.period_var.get() if self.period_var.get() else None

        # Filter data
        query = (self.df["grado"].astype(str).str.lower() == str(grade).lower()) & (
            self.df["eje tematico (numeros)"].astype(str).str.lower() == str(topic).lower()
        )
        if period:
            query &= self.df["período"].astype(str).str.lower() == str(period).lower()

        result = self.df[query]

        self.clear_results()

        if not result.empty:
            row_data = result.iloc[0].to_dict()
            for i, (display_field, col_name) in enumerate(self.FIELD_MAPPING_DISPLAYED.items()):
                value = str(row_data.get(col_name, "") if pd.notna(row_data.get(col_name)) else "")
                self.result_labels[display_field].configure(text=value)
            self.status_var.set("Datos cargados correctamente.")
        else:
            self.status_var.set("No se encontraron datos.")
            messagebox.showinfo("Sin Resultados", "No se encontraron datos para los criterios seleccionados.")

    def clear_results(self):
        """Clear all result fields in the results grid."""
        for label in self.result_labels.values():
            label.configure(text="")
        self.status_var.set("Seleccione o ingrese un eje temático.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CurriculumSelectorApp(root)
    root.mainloop()