import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import customtkinter as ctk
from tkinter.font import Font

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class CurriculumSelectorApp:
    """Application for selecting mathematical curriculum data with customtkinter styling."""

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
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        self.df = None
        self.grade_var = tk.StringVar()
        self.period_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.search_results_data = []
        self.result_labels = {}
        self.status_var = tk.StringVar(value="Cargue un archivo Excel.")
        self.search_timer = None
        self.tree_font = Font(family="Arial", size=10)
        self.setup_ui()

    def setup_ui(self):
        """Initialize the user interface."""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        main_frame.columnconfigure(0, weight=1)

        # Top Section (File Selection and Filters)
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill="x", pady=(0, 20))
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=2)

        # File Selection
        file_frame = ctk.CTkFrame(top_frame, border_width=2)
        file_frame.grid(row=0, column=0, padx=(0, 15), pady=10, sticky="ew")
        ctk.CTkLabel(file_frame, text="Archivo", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=(5, 0), anchor="w")
        ctk.CTkButton(file_frame, text="Seleccionar Excel", command=self.load_file).pack(fill="x", padx=10, pady=(0, 8))

        # Filters
        filter_frame = ctk.CTkFrame(top_frame, border_width=2)
        filter_frame.grid(row=0, column=1, padx=(15, 0), pady=10, sticky="ew")
        filter_frame.columnconfigure(1, weight=1)
        ctk.CTkLabel(filter_frame, text="Filtros", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=(5, 0), anchor="w")
        ctk.CTkLabel(filter_frame, text="Grado:").grid(row=1, column=0, sticky="e", padx=(10, 5), pady=5)
        self.grade_combo = ctk.CTkComboBox(filter_frame, values=[], variable=self.grade_var, state="readonly")
        self.grade_combo.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=5)
        self.grade_combo.bind("<<ComboboxSelected>>", self.update_periods)
        ctk.CTkLabel(filter_frame, text="Período:").grid(row=2, column=0, sticky="e", padx=(10, 5), pady=5)
        self.period_combo = ctk.CTkComboBox(filter_frame, values=[], variable=self.period_var, state="readonly")
        self.period_combo.grid(row=2, column=1, sticky="ew", padx=(5, 10), pady=5)
        self.period_combo.bind("<<ComboboxSelected>>", self.search_data)
        ctk.CTkLabel(filter_frame, text="Buscar:").grid(row=3, column=0, sticky="e", padx=(10, 5), pady=5)
        self.search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_var)
        self.search_entry.grid(row=3, column=1, sticky="ew", padx=(5, 10), pady=5)
        self.search_entry.insert(0, "Escriba para buscar...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "Escriba para buscar..." else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "Escriba para buscar...") if not self.search_entry.get() else None)
        self.search_var.trace("w", self.debounce_search)

        # Search Results Listbox
        search_results_frame = ctk.CTkFrame(main_frame)
        search_results_frame.pack(fill="x", pady=(0, 20))
        search_results_frame.columnconfigure(0, weight=1)
        search_results_frame.rowconfigure(0, weight=1)
        self.search_results = tk.Listbox(search_results_frame, font=("Arial", 10), height=5)
        self.search_results.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.search_scroll_y = ctk.CTkScrollbar(search_results_frame, orientation="vertical", command=self.search_results.yview)
        self.search_scroll_y.grid(row=0, column=1, sticky="ns", padx=(0, 5), pady=5)
        self.search_scroll_x = ctk.CTkScrollbar(search_results_frame, orientation="horizontal", command=self.search_results.xview)
        self.search_scroll_x.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.search_results.configure(yscrollcommand=self.search_scroll_y.set, xscrollcommand=self.search_scroll_x.set)
        self.search_results.bind("<<ListboxSelect>>", self.on_result_select)

        # Results Section
        result_frame = ctk.CTkFrame(main_frame, border_width=2)
        result_frame.pack(fill="both", expand=True, pady=(0, 20))
        ctk.CTkLabel(result_frame, text="Resultados", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=(5, 0), anchor="w")
        self.results_grid = ctk.CTkFrame(result_frame)
        self.results_grid.pack(fill="both", expand=True, padx=10, pady=10)
        self.results_grid.columnconfigure(1, weight=1)

        for i, field in enumerate(self.FIELD_MAPPING_DISPLAYED):
            ctk.CTkLabel(self.results_grid, text=f"{field}:", anchor="e").grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            label = ctk.CTkLabel(self.results_grid, text="", wraplength=550, anchor="w", justify="left")
            label.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.result_labels[field] = label

        # Status Bar
        self.status_label = ctk.CTkLabel(main_frame, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill="x", pady=(10, 0))

        self.root.bind("<Configure>", self.resize_search_results)

    def get_text_width(self, text):
        """Calculate text width in pixels."""
        return self.tree_font.measure(text) + 10

    def resize_search_results(self, event=None):
        """Adjust Listbox size."""
        width = max(self.search_results.winfo_width(), 200)
        max_width = 200
        for item in self.search_results_data:
            text = f"Grado {item['grado']} - Período {item['período']} - Eje: {item['eje tematico (numeros)'][:50]}..."
            max_width = max(max_width, self.get_text_width(text))
        listbox_width = min(max_width, int(width * 0.9)) // 8
        listbox_height = max(5, min(len(self.search_results_data), 10)) if self.search_results_data else 5
        self.search_results.configure(width=listbox_width, height=listbox_height)

    def debounce_search(self, *args):
        """Debounce search input."""
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        self.search_timer = self.root.after(300, self.search_data)

    def load_file(self):
        """Load Excel file."""
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            self.status_var.set("No se seleccionó archivo.")
            return
        try:
            self.df = pd.read_excel(file_path)
            self.update_grades()
            self.status_var.set("Archivo cargado.")
            self.search_entry.focus_set()
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"No se pudo cargar: {e}")

    def update_grades(self):
        """Update grade dropdown."""
        self.search_results.delete(0, tk.END)
        self.search_results_data = []
        self.grade_var.set('')
        self.period_var.set('')
        self.search_var.set('')
        if self.df is not None:
            grades = sorted(self.df['grado'].dropna().astype(str).unique())
            self.grade_combo.configure(values=grades)
            self.period_combo.configure(values=[])
            self.status_var.set("Seleccione un grado.")
        else:
            self.grade_combo.configure(values=[])
            self.status_var.set("Cargue un archivo.")

    def update_periods(self, event):
        """Update period dropdown."""
        self.search_results.delete(0, tk.END)
        self.search_results_data = []
        self.period_var.set('')
        if self.df is not None and self.grade_var.get():
            grade = self.grade_var.get()
            periods = sorted(self.df[self.df['grado'].astype(str) == grade]['período'].dropna().astype(str).unique())
            self.period_combo.configure(values=periods)
            self.search_data()
            self.status_var.set("Seleccione período o busque.")
        else:
            self.period_combo.configure(values=[])
            self.status_var.set("Seleccione un grado.")

    def search_data(self):
        """Search DataFrame and populate Listbox."""
        self.search_results.delete(0, tk.END)
        self.search_results_data = []
        self.clear_results()
        if self.df is None or not self.grade_var.get():
            self.status_var.set("Cargue archivo y seleccione grado.")
            return

        search_query = self.search_var.get().lower()
        if search_query == "escriba para buscar...":
            search_query = ""
        grade = self.grade_var.get()
        period = self.period_var.get()

        query = self.df['grado'].astype(str).str.lower() == grade.lower()
        if period:
            query &= self.df['período'].astype(str).str.lower() == period.lower()

        filtered_df = self.df[query]
        if search_query:
            search_fields = [
                'eje tematico (numeros)',
                'dba descripción',
                'competencia/afirmacion',
                'aprendizaje / matriz de referencia',
                'evidencias / matriz de referencia'
            ]
            mask = filtered_df[search_fields].astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            filtered_df = filtered_df[mask]

        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                text = f"Grado {row['grado']} - Período {row['período']} - Eje: {row['eje tematico (numeros)'][:50]}..."
                self.search_results.insert(tk.END, text)
                self.search_results_data.append(row.to_dict())
            self.status_var.set(f"{len(filtered_df)} resultados.")
        else:
            self.search_results.insert(tk.END, "Sin resultados.")
            self.status_var.set("Sin resultados.")

        self.resize_search_results()

    def on_result_select(self, event):
        """Update result labels from Listbox selection."""
        selection = self.search_results.curselection()
        if not selection or selection[0] >= len(self.search_results_data):
            return

        row_data = self.search_results_data[selection[0]]
        for field, col_name in self.FIELD_MAPPING_DISPLAYED.items():
            value = str(row_data.get(col_name, "") if pd.notna(row_data.get(col_name)) else "")
            self.result_labels[field].configure(text=value)
        self.status_var.set("Datos cargados.")

    def clear_results(self):
        """Clear result fields."""
        for label in self.result_labels.values():
            label.configure(text="")

if __name__ == "__main__":
    root = ctk.CTk()
    app = CurriculumSelectorApp(root)
    root.mainloop()