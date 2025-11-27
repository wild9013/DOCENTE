import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.enter_id = None
        self.widget.bind("<Enter>", self.schedule_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        
    def schedule_tooltip(self, event=None):
        if hasattr(self.widget, "cget") and self.widget.cget("state") == "disabled":
            return
        self.enter_id = self.widget.after(500, self.show_tooltip)
        
    def show_tooltip(self):
        if self.tooltip:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, bg="#ffffe0", fg="#000000", relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack()
        
    def hide_tooltip(self, event=None):
        if self.enter_id:
            self.widget.after_cancel(self.enter_id)
            self.enter_id = None
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DBA Explorer - Matemáticas")
        self.datos = None
        self.root.geometry("1000x750")
        
        # Estilo para widgets ttk
        style = ttk.Style()
        style.configure("TButton", padding=6, font=("Arial", 10), background="#15803d", foreground="#ffffff")  # Changed to green
        style.map("TButton", 
                  background=[("active", "#16a34a"), ("disabled", "#d1d5db")],  # Lighter green for active, gray for disabled
                  foreground=[("active", "#ffffff"), ("disabled", "#6b7280")])  # White text, gray for disabled
        style.configure("TLabel", font=("Arial", 11), foreground="#1f2937")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), foreground="#1f2937")
        style.configure("Treeview", rowheight=30, font=("Arial", 10), foreground="#1f2937")
        style.configure("Title.TLabel", font=("Arial", 14, "bold"), foreground="#1e40af")
        style.configure("Subtitle.TLabel", font=("Arial", 11, "italic"), foreground="#1f2937")
        style.configure("Main.TFrame", background="#f3f4f6")
        style.configure("TCombobox", font=("Arial", 10), foreground="#1f2937")
        style.configure("TEntry", font=("Arial", 10), foreground="#1f2937")
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding=15, style="Main.TFrame")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Título principal
        self.title_label = ttk.Label(self.main_frame, text="DBA Explorer", style="Title.TLabel")
        self.title_label.grid(row=0, column=0, pady=(0, 5))
        self.subtitle_label = ttk.Label(self.main_frame, text="Gestión de Derechos Básicos de Aprendizaje", style="Subtitle.TLabel")
        self.subtitle_label.grid(row=1, column=0, pady=(0, 15))
        
        # Frame superior
        self.top_frame = ttk.Frame(self.main_frame, relief="groove", borderwidth=3)
        self.top_frame.grid(row=2, column=0, sticky="ew", pady=15)
        
        self.top_title = ttk.Label(self.top_frame, text="Selección de Grado y Búsqueda", font=("Arial", 12, "bold"), foreground="#1e40af")
        self.top_title.grid(row=0, column=0, columnspan=5, pady=10)
        
        # Botón Abrir archivo
        self.btn_abrir = ttk.Button(self.top_frame, text="Abrir JSON", command=self.abrir_archivo)
        self.btn_abrir.grid(row=1, column=0, padx=10, pady=5)
        Tooltip(self.btn_abrir, "Cargar archivo JSON con DBAs")
        
        # Selección de Grado
        self.label_grado = ttk.Label(self.top_frame, text="Grado:")
        self.label_grado.grid(row=1, column=1, padx=10, pady=5)
        self.grado_var = tk.StringVar()
        self.grado_combo = ttk.Combobox(self.top_frame, textvariable=self.grado_var, state="readonly", width=10)
        self.grado_combo.grid(row=1, column=2, padx=10, pady=5)
        self.grado_combo.bind("<<ComboboxSelected>>", self.actualizar_dbas)
        Tooltip(self.grado_combo, "Seleccionar grado para filtrar DBAs")
        
        # Campo de búsqueda
        self.label_buscar = ttk.Label(self.top_frame, text="Buscar:")
        self.label_buscar.grid(row=1, column=3, padx=10, pady=5)
        self.buscar_var = tk.StringVar()
        self.buscar_var.trace("w", self.debounce_search)
        self.entry_buscar = ttk.Entry(self.top_frame, textvariable=self.buscar_var, font=("Arial", 10))
        self.entry_buscar.grid(row=1, column=4, padx=10, pady=5, sticky="ew")
        self.entry_buscar.insert(0, "Escriba para buscar...")
        self.entry_buscar.bind("<FocusIn>", lambda e: self.entry_buscar.delete(0, tk.END) if self.entry_buscar.get() == "Escriba para buscar..." else None)
        self.entry_buscar.bind("<FocusOut>", lambda e: self.entry_buscar.insert(0, "Escriba para buscar...") if not self.entry_buscar.get() else None)
        self.top_frame.grid_columnconfigure(4, weight=1)
        Tooltip(self.entry_buscar, "Buscar en enunciados o evidencias")
        
        # Separador
        self.sep1 = ttk.Separator(self.main_frame, orient="horizontal")
        self.sep1.grid(row=3, column=0, sticky="ew", pady=10)
        
        # Frame para Treeview de DBAs
        self.dba_frame = ttk.Frame(self.main_frame, relief="groove", borderwidth=3)
        self.dba_frame.grid(row=4, column=0, sticky="nsew", pady=15)
        self.main_frame.grid_rowconfigure(4, weight=2)
        
        self.dba_title = ttk.Label(self.dba_frame, text="Lista de DBAs", font=("Arial", 12, "bold"), foreground="#1e40af")
        self.dba_title.grid(row=0, column=0, pady=10)
        
        # Treeview para DBAs
        self.dba_tree = ttk.Treeview(self.dba_frame, columns=("DBA", "Enunciado"), show="headings")
        self.dba_tree.heading("DBA", text="DBA")
        self.dba_tree.heading("Enunciado", text="Enunciado DBA")
        self.dba_tree.column("DBA", width=100, anchor="center")
        self.dba_tree.column("Enunciado", width=700)
        self.dba_tree.grid(row=1, column=0, sticky="nsew")
        self.dba_frame.grid_rowconfigure(1, weight=1)
        self.dba_frame.grid_columnconfigure(0, weight=1)
        self.dba_tree.bind("<<TreeviewSelect>>", self.mostrar_evidencias)
        
        self.dba_scroll = ttk.Scrollbar(self.dba_frame, orient="vertical", command=self.dba_tree.yview)
        self.dba_scroll.grid(row=1, column=1, sticky="ns")
        self.dba_tree.configure(yscrollcommand=self.dba_scroll.set)
        
        # Separador
        self.sep2 = ttk.Separator(self.main_frame, orient="horizontal")
        self.sep2.grid(row=5, column=0, sticky="ew", pady=10)
        
        # Frame para evidencias
        self.evid_frame = ttk.Frame(self.main_frame, relief="groove", borderwidth=3)
        self.evid_frame.grid(row=6, column=0, sticky="nsew", pady=15)
        self.main_frame.grid_rowconfigure(6, weight=3)
        
        self.evid_title = ttk.Label(self.evid_frame, text="Evidencias de Aprendizaje", font=("Arial", 12, "bold"), foreground="#1e40af")
        self.evid_title.grid(row=0, column=0, pady=10)
        
        # Treeview para evidencias
        self.evid_tree = ttk.Treeview(self.evid_frame, columns=("Evidencia",), show="headings")
        self.evid_tree.heading("Evidencia", text="Evidencias")
        self.evid_tree.column("Evidencia", width=800)
        self.evid_tree.grid(row=1, column=0, sticky="nsew")
        self.evid_frame.grid_rowconfigure(1, weight=1)
        self.evid_frame.grid_columnconfigure(0, weight=1)
        self.evid_tree.bind("<Double-1>", self.copiar_evidencia_seleccionada)
        self.evid_tree.bind("<<TreeviewSelect>>", self.actualizar_boton_evidencia)
        
        self.evid_scroll = ttk.Scrollbar(self.evid_frame, orient="vertical", command=self.evid_tree.yview)
        self.evid_scroll.grid(row=1, column=1, sticky="ns")
        self.evid_tree.configure(yscrollcommand=self.evid_scroll.set)
        
        # Frame para botones de copiar
        self.copy_frame = ttk.Frame(self.main_frame)
        self.copy_frame.grid(row=7, column=0, sticky="ew", pady=15)
        
        self.btn_copy_dba = ttk.Button(self.copy_frame, text="Copiar DBA", command=self.copiar_dba, state="disabled")
        self.btn_copy_dba.grid(row=0, column=0, padx=10)
        Tooltip(self.btn_copy_dba, "Copiar el enunciado del DBA seleccionado")
        
        self.btn_copy_evid = ttk.Button(self.copy_frame, text="Copiar Todas las Evidencias", command=self.copiar_evidencias, state="disabled")
        self.btn_copy_evid.grid(row=0, column=1, padx=10)
        Tooltip(self.btn_copy_evid, "Copiar todas las evidencias del DBA")
        
        self.btn_copy_evid_one = ttk.Button(self.copy_frame, text="Copiar Evidencia Seleccionada", command=self.copiar_evidencia_seleccionada, state="disabled")
        self.btn_copy_evid_one.grid(row=0, column=2, padx=10)
        Tooltip(self.btn_copy_evid_one, "Copiar la evidencia seleccionada")
        
        self.btn_copy_all = ttk.Button(self.copy_frame, text="Copiar Todo", command=self.copiar_todo, state="disabled")
        self.btn_copy_all.grid(row=0, column=3, padx=10)
        Tooltip(self.btn_copy_all, "Copiar DBA y todas sus evidencias")
        
        # Variables para búsqueda
        self.search_timer = None
        self.selected_dba = None
        
        # Atajos de teclado
        self.root.bind("<Control-o>", lambda e: self.abrir_archivo())
        self.root.bind("<Control-c>", lambda e: self.copiar_evidencia_seleccionada())
        
    def debounce_search(self, *args):
        if self.search_timer:
            self.root.after_cancel(self.search_timer)
        self.search_timer = self.root.after(300, self.actualizar_dbas)
        
    def abrir_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if archivo:
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    self.datos = json.load(f)
                if not isinstance(self.datos, list):
                    raise ValueError("El archivo JSON debe contener una lista de objetos.")
                grados = sorted(set(item["Grado"] for item in self.datos))
                self.grado_combo["values"] = grados
                self.grado_var.set(grados[0] if grados else "")
                self.actualizar_dbas()
                self.entry_buscar.focus_set()
                messagebox.showinfo("Éxito", "Archivo cargado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")
                self.datos = None
                self.grado_combo["values"] = []
                self.grado_var.set("")
                self.dba_tree.delete(*self.dba_tree.get_children())
                self.evid_tree.delete(*self.evid_tree.get_children())
                self.btn_copy_dba["state"] = "disabled"
                self.btn_copy_evid["state"] = "disabled"
                self.btn_copy_evid_one["state"] = "disabled"
                self.btn_copy_all["state"] = "disabled"
                
    def actualizar_dbas(self, event=None):
        if not self.datos or not isinstance(self.datos, list):
            return
        self.dba_tree.delete(*self.dba_tree.get_children())
        self.evid_tree.delete(*self.evid_tree.get_children())
        self.btn_copy_dba["state"] = "disabled"
        self.btn_copy_evid["state"] = "disabled"
        self.btn_copy_evid_one["state"] = "disabled"
        self.btn_copy_all["state"] = "disabled"
        grado = self.grado_var.get()
        buscar = self.buscar_var.get().lower()
        
        dbas = [item for item in self.datos if item["Grado"] == grado]
        if buscar and buscar != "escriba para buscar...":
            dbas = [
                item for item in dbas
                if buscar in item["Enunciado_DBA"].lower() or
                any(buscar in ev.lower() for ev in item["Evidencias_de_Aprendizaje"])
            ]
        
        if not dbas:
            self.dba_tree.insert("", tk.END, values=("", "No se encontraron DBAs para los criterios seleccionados."))
        else:
            for item in sorted(dbas, key=lambda x: int(x["DBA"])):
                self.dba_tree.insert("", tk.END, values=(f"DBA {item['DBA']}", item["Enunciado_DBA"]))
                
    def mostrar_evidencias(self, event):
        seleccion = self.dba_tree.selection()
        self.evid_tree.delete(*self.evid_tree.get_children())
        self.btn_copy_dba["state"] = "disabled"
        self.btn_copy_evid["state"] = "disabled"
        self.btn_copy_evid_one["state"] = "disabled"
        self.btn_copy_all["state"] = "disabled"
        
        if not seleccion:
            return
            
        item = self.dba_tree.item(seleccion[0])
        dba_num = item["values"][0].split()[1] if item["values"][0].startswith("DBA") else None
        if not dba_num:
            return
            
        grado = self.grado_var.get()
        self.selected_dba = next(
            (item for item in self.datos if item["Grado"] == grado and item["DBA"] == dba_num),
            None
        )
        
        if self.selected_dba:
            evidencias = self.selected_dba["Evidencias_de_Aprendizaje"]
            if evidencias:
                for i, evidencia in enumerate(evidencias, 1):
                    self.evid_tree.insert("", tk.END, values=(f"{i}. {evidencia}",))
                self.btn_copy_dba["state"] = "normal"
                self.btn_copy_evid["state"] = "normal"
                self.btn_copy_all["state"] = "normal"
            else:
                self.evid_tree.insert("", tk.END, values=("No hay evidencias disponibles para este DBA.",))
        else:
            self.evid_tree.insert("", tk.END, values=("Error al cargar las evidencias.",))
            
    def actualizar_boton_evidencia(self, event):
        seleccion = self.evid_tree.selection()
        self.btn_copy_evid_one["state"] = "normal" if seleccion and not self.evid_tree.item(seleccion[0])["values"][0].startswith(("No hay", "Error")) else "disabled"
        
    def copiar_dba(self):
        if self.selected_dba:
            texto = f"DBA {self.selected_dba['DBA']}: {self.selected_dba['Enunciado_DBA']}"
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            messagebox.showinfo("Copiado", f"DBA {self.selected_dba['DBA']} copiado al portapapeles.")
            
    def copiar_evidencias(self):
        if self.selected_dba and self.selected_dba["Evidencias_de_Aprendizaje"]:
            texto = "Evidencias de Aprendizaje:\n" + "\n".join(
                f"- {ev}" for ev in self.selected_dba["Evidencias_de_Aprendizaje"]
            )
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            messagebox.showinfo("Copiado", "Todas las evidencias copiadas al portapapeles.")
            
    def copiar_evidencia_seleccionada(self, event=None):
        seleccion = self.evid_tree.selection()
        if not seleccion:
            return
        item = self.evid_tree.item(seleccion[0])
        texto = item["values"][0]
        if texto.startswith(("No hay", "Error")):
            return
        texto = texto.split(". ", 1)[1] if ". " in texto else texto
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        messagebox.showinfo("Copiado", f"Evidencia '{texto[:20]}...' copiada al portapapeles.")
        
    def copiar_todo(self):
        if self.selected_dba:
            texto = (
                f"DBA {self.selected_dba['DBA']}: {self.selected_dba['Enunciado_DBA']}\n\n"
                "Evidencias de Aprendizaje:\n" + "\n".join(
                    f"- {ev}" for ev in self.selected_dba["Evidencias_de_Aprendizaje"]
                )
            )
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            messagebox.showinfo("Copiado", f"DBA {self.selected_dba['DBA']} y evidencias copiados al portapapeles.")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()