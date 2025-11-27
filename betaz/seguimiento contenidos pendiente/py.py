import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

class MathTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Seguimiento de Contenidos Matemáticos")
        self.root.geometry("700x500") # Ampliar la ventana un poco

        # Obtener el directorio del script actual
        script_dir = os.path.dirname(__file__)
        # Definir la carpeta de guardado relativa al script
        self.save_folder_name = "avance" # Nombre de la subcarpeta
        self.save_filename = "math_topics.json" # Nombre del archivo
        # Construir la ruta completa de la carpeta de guardado
        self.full_save_folder = os.path.join(script_dir, self.save_folder_name)
        # Construir la ruta completa del archivo de guardado
        self.save_path = os.path.join(self.full_save_folder, self.save_filename)

        # Lista para almacenar temas (ahora con más datos)
        self.topics = []
        self.load_topics() # Cargar temas al iniciar la aplicación

        # Crear elementos de la interfaz
        self.create_widgets()

    def create_widgets(self):
        # Frame para entrada de datos (ahora con 4 campos)
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        # Etiquetas y campos para Grado, Periodo, Temática y Tema
        tk.Label(input_frame, text="Grado:").grid(row=0, column=0, padx=5, pady=2, sticky='e')
        self.grade_entry = tk.Entry(input_frame, width=15)
        self.grade_entry.grid(row=0, column=1, padx=5, pady=2, sticky='w')

        tk.Label(input_frame, text="Periodo:").grid(row=0, column=2, padx=5, pady=2, sticky='e')
        self.period_entry = tk.Entry(input_frame, width=15)
        self.period_entry.grid(row=0, column=3, padx=5, pady=2, sticky='w')

        tk.Label(input_frame, text="Temática:").grid(row=1, column=0, padx=5, pady=2, sticky='e')
        self.subject_entry = tk.Entry(input_frame, width=40)
        self.subject_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=2, sticky='w') # Expandir Temática

        tk.Label(input_frame, text="Tema:").grid(row=2, column=0, padx=5, pady=2, sticky='e')
        self.topic_entry = tk.Entry(input_frame, width=40)
        self.topic_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=2, sticky='w') # Expandir Tema

        # Botón de agregar
        tk.Button(input_frame, text="Agregar Tema", command=self.add_topic).grid(row=0, column=4, rowspan=3, padx=10, pady=5, sticky='ns') # Abarcar varias filas

        # Frame para la lista de temas
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Treeview para mostrar temas (columnas actualizadas)
        columns = ("Grado", "Periodo", "Temática", "Tema", "Estado")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        self.tree.heading("Grado", text="Grado")
        self.tree.heading("Periodo", text="Periodo")
        self.tree.heading("Temática", text="Temática")
        self.tree.heading("Tema", text="Tema")
        self.tree.heading("Estado", text="Estado")

        # Ajustar anchos de columna (aproximados)
        self.tree.column("Grado", width=50, anchor='center')
        self.tree.column("Periodo", width=60, anchor='center')
        self.tree.column("Temática", width=150)
        self.tree.column("Tema", width=200)
        self.tree.column("Estado", width=80, anchor='center')


        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) # Treeview a la izquierda
        
        # Agregar Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        # Botones de acción
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Marcar Completado", command=self.mark_completed).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Eliminar Tema", command=self.delete_topic).pack(side=tk.LEFT, padx=5)

        # Cargar temas en el Treeview
        self.update_treeview()

    def add_topic(self):
        # Obtener datos de todos los campos
        grade = self.grade_entry.get().strip()
        period = self.period_entry.get().strip()
        subject = self.subject_entry.get().strip()
        topic = self.topic_entry.get().strip()

        # Validar que al menos el Tema no esté vacío
        if not topic:
             messagebox.showwarning("Advertencia", "Por favor, ingrese el nombre del Tema.")
             return
        # Puedes añadir validación para otros campos si son obligatorios
        # if not grade or not period or not subject:
        #     messagebox.showwarning("Advertencia", "Por favor, complete los campos Grado, Periodo y Temática.")
        #     return

        # Agregar el nuevo tema a la lista con todos los datos
        self.topics.append({
            "grade": grade,
            "period": period,
            "subject": subject,
            "topic": topic,
            "completed": False
        })

        # Limpiar todos los campos de entrada
        self.grade_entry.delete(0, tk.END)
        self.period_entry.delete(0, tk.END)
        self.subject_entry.delete(0, tk.END)
        self.topic_entry.delete(0, tk.END)

        self.save_topics() # Guardar después de agregar
        self.update_treeview()

    # mark_completed y delete_topic no cambian mucho, ya que operan en la lista self.topics
    # y luego llaman a save_topics y update_treeview, que se han actualizado.
    def mark_completed(self):
        selected_item = self.tree.selection()
        if selected_item:
            # El índice en Treeview corresponde al índice en la lista si no hay filtros/ordenación
            item_index = self.tree.index(selected_item[0])
            if 0 <= item_index < len(self.topics): # Verificar rango
                 self.topics[item_index]["completed"] = True
                 self.save_topics() # Guardar después de marcar como completado
                 self.update_treeview()
            else:
                 # Esto no debería ocurrir si el Treeview está sincronizado
                 messagebox.showerror("Error", "Índice de tema no válido.")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un tema para marcar como completado.")

    def delete_topic(self):
        selected_item = self.tree.selection()
        if selected_item:
            # El índice en Treeview corresponde al índice en la lista si no hay filtros/ordenación
            item_index = self.tree.index(selected_item[0])
            if 0 <= item_index < len(self.topics): # Verificar rango
                 # Confirmar antes de eliminar (opcional pero recomendado)
                 if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar este tema?"):
                     self.topics.pop(item_index)
                     self.save_topics() # Guardar después de eliminar
                     self.update_treeview()
            else:
                 # Esto no debería ocurrir si el Treeview está sincronizado
                 messagebox.showerror("Error", "Índice de tema no válido.")
        else:
            messagebox.showwarning("Advertencia", "Seleccione un tema para eliminar.")

    def update_treeview(self):
        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Agregar temas al Treeview con la nueva estructura de datos
        for topic_data in self.topics:
            status = "Completado" if topic_data.get("completed", False) else "Pendiente" # Usar .get con default por seguridad
            # Obtener los nuevos campos. Usar .get() con un valor por defecto ('') para evitar errores si el archivo viejo no los tiene.
            grade = topic_data.get("grade", "")
            period = topic_data.get("period", "")
            subject = topic_data.get("subject", "")
            topic = topic_data.get("topic", "") # El tema sí debería existir

            # Insertar fila en el Treeview
            self.tree.insert("", tk.END, values=(grade, period, subject, topic, status))

    def save_topics(self):
        # Crear la carpeta de guardado completa si no existe
        os.makedirs(self.full_save_folder, exist_ok=True)
        # Guardar en la ruta completa del archivo
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.topics, f, ensure_ascii=False, indent=4)

    def load_topics(self):
        # Cargar desde la ruta completa del archivo si existe
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    # Opcional: Validar que la data cargada sea una lista para evitar errores
                    if isinstance(loaded_data, list):
                         self.topics = loaded_data
                    else:
                         self.topics = []
                         messagebox.showwarning("Advertencia", f"El archivo de datos en '{self.save_path}' tiene un formato inesperado. Se ha iniciado con una lista vacía.")

            except json.JSONDecodeError:
                # Manejar el caso de un archivo JSON corrupto o vacío
                self.topics = []
                messagebox.showwarning("Advertencia", f"El archivo de datos en '{self.save_path}' estaba corrupto o vacío. Se ha iniciado con una lista vacía.")
            except FileNotFoundError:
                 # Esto no debería ocurrir si os.path.exists() es True, pero como manejo de errores
                 self.topics = []
                 messagebox.showwarning("Advertencia", f"El archivo de datos en '{self.save_path}' no se encontró (después de verificar su existencia). Se ha iniciado con una lista vacía.")
        else:
            self.topics = [] # Si el archivo o la carpeta no existen, iniciar con lista vacía

if __name__ == "__main__":
    root = tk.Tk()
    app = MathTrackerApp(root)
    root.mainloop()