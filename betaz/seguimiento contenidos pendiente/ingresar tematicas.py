import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import operator
import uuid

class MathTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Seguimiento de Contenidos Matemáticos")
        self.root.geometry("900x700")

        # Directorio para guardar datos
        script_dir = os.path.dirname(__file__)
        self.save_folder_name = "avance"
        self.save_filename = "math_progress_v4.json"
        self.full_save_folder = os.path.join(script_dir, self.save_folder_name)
        self.save_path = os.path.join(self.full_save_folder, self.save_filename)

        # Estructura de datos
        self.data = {"grades": []}
        self.load_data()

        # Crear interfaz
        self.create_widgets()

    def create_widgets(self):
        # Frame para entrada de datos
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        # Campos de entrada
        tk.Label(input_frame, text="Grado:").grid(row=0, column=0, padx=5, pady=2, sticky='e')
        self.grade_entry = tk.Entry(input_frame, width=15)
        self.grade_entry.grid(row=0, column=1, padx=5, pady=2, sticky='w')

        tk.Label(input_frame, text="Periodo:").grid(row=0, column=2, padx=5, pady=2, sticky='e')
        self.period_entry = tk.Entry(input_frame, width=15)
        self.period_entry.grid(row=0, column=3, padx=5, pady=2, sticky='w')

        tk.Label(input_frame, text="Área:").grid(row=1, column=0, padx=5, pady=2, sticky='e')
        self.area_name_entry = tk.Entry(input_frame, width=30)
        self.area_name_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=2, sticky='w')

        tk.Label(input_frame, text="Tema (Orden):").grid(row=1, column=3, padx=5, pady=2, sticky='e')
        self.topic_order_entry = tk.Entry(input_frame, width=8)
        self.topic_order_entry.grid(row=1, column=4, padx=5, pady=2, sticky='w')

        tk.Label(input_frame, text="Tema a trabajar:").grid(row=2, column=0, padx=5, pady=2, sticky='e')
        self.topic_name_entry = tk.Entry(input_frame, width=50)
        self.topic_name_entry.grid(row=2, column=1, columnspan=4, padx=5, pady=2, sticky='w')

        # Botón de agregar
        tk.Button(input_frame, text="Agregar Tema", command=self.add_topic).grid(row=0, column=5, rowspan=3, padx=10, pady=5, sticky='ns')

        # Frame para vista jerárquica
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Treeview
        columns = ("Orden", "Tema a trabajar", "Estado")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings")
        self.tree.heading("#0", text="Grado / Periodo / Área")
        self.tree.heading("Orden", text="Orden")
        self.tree.heading("Tema a trabajar", text="Tema")
        self.tree.heading("Estado", text="Estado")

        self.tree.column("#0", width=250)
        self.tree.column("Orden", width=60, anchor='center')
        self.tree.column("Tema a trabajar", width=300)
        self.tree.column("Estado", width=80, anchor='center')

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones de acción
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Marcar/Desmarcar Completado", command=self.toggle_completed).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Eliminar Elemento", command=self.delete_element).pack(side=tk.LEFT, padx=5)

        # Cargar datos iniciales
        self.update_treeview()

    def add_topic(self):
        # Obtener y validar entradas
        grade_name = self.grade_entry.get().strip()
        period_name = self.period_entry.get().strip()
        area_name = self.area_name_entry.get().strip()
        topic_order_str = self.topic_order_entry.get().strip()
        topic_name = self.topic_name_entry.get().strip()

        if not all([grade_name, period_name, area_name, topic_order_str, topic_name]):
            messagebox.showwarning("Advertencia", "Complete todos los campos.")
            return

        try:
            topic_order = int(topic_order_str)
            if topic_order <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Advertencia", "El campo 'Tema (Orden)' debe ser un número entero positivo.")
            return

        # Encontrar o crear grado
        grade_data = next((g for g in self.data["grades"] if g["name"] == grade_name), None)
        if not grade_data:
            grade_data = {"id": str(uuid.uuid4()), "name": grade_name, "periods": []}
            self.data["grades"].append(grade_data)
            self.data["grades"].sort(key=operator.itemgetter("name"))

        # Encontrar o crear periodo
        period_data = next((p for p in grade_data["periods"] if p["name"] == period_name), None)
        if not period_data:
            period_data = {"id": str(uuid.uuid4()), "name": period_name, "areas": []}
            grade_data["periods"].append(period_data)
            try:
                grade_data["periods"].sort(key=lambda x: int(x["name"].replace("Periodo ", "").strip()) if x["name"].lower().startswith("periodo ") else x["name"])
            except:
                grade_data["periods"].sort(key=operator.itemgetter("name"))

        # Encontrar o crear área
        area_data = next((a for a in period_data["areas"] if a["name"] == area_name), None)
        if not area_data:
            area_data = {"id": str(uuid.uuid4()), "name": area_name, "topics": []}
            period_data["areas"].append(area_data)
            period_data["areas"].sort(key=operator.itemgetter("name"))

        # Validar tema
        if any(t["order"] == topic_order or t["name"] == topic_name for t in area_data["topics"]):
            messagebox.showwarning("Advertencia", f"Ya existe un tema con el orden {topic_order} o el nombre '{topic_name}' en esta área.")
            return

        # Agregar tema
        area_data["topics"].append({"id": str(uuid.uuid4()), "order": topic_order, "name": topic_name, "completed": False})

        # Limpiar campos de tema
        self.topic_order_entry.delete(0, tk.END)
        self.topic_name_entry.delete(0, tk.END)

        self.save_data()
        self.update_treeview()

    def toggle_completed(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un Tema para cambiar su estado.")
            return

        item_id = selected_item[0]
        item_tags = self.tree.item(item_id, 'tags')

        if not item_tags or len(item_tags) < 2 or item_tags[0] != "topic_data":
            messagebox.showwarning("Advertencia", "Seleccione un nodo de Tema válido.")
            return

        topic_data = item_tags[1]
        if not isinstance(topic_data, dict) or "id" not in topic_data or "completed" not in topic_data:
            # Intenta localizar el tema usando el ID
            topic_id = topic_data.get("id") if isinstance(topic_data, dict) else None
            if topic_id:
                for grade in self.data["grades"]:
                    for period in grade["periods"]:
                        for area in period["areas"]:
                            for topic in area["topics"]:
                                if topic["id"] == topic_id:
                                    topic_data = topic
                                    break
                            if topic_data is topic: break
                        if topic_data is topic: break
                    if topic_data is topic: break

            if not isinstance(topic_data, dict) or "completed" not in topic_data:
                messagebox.showerror("Error", f"Datos del tema inválidos: {topic_data}")
                return

        # Cambiar estado
        topic_data["completed"] = not topic_data["completed"]
        new_status = "Completado" if topic_data["completed"] else "Pendiente"

        # Actualizar Treeview
        current_values = list(self.tree.item(item_id, 'values'))
        current_values[2] = new_status
        self.tree.item(item_id, values=current_values)

        self.save_data()

    def delete_element(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un elemento para eliminar.")
            return

        item_id = selected_item[0]
        item_tags = self.tree.item(item_id, 'tags')
        if not item_tags or len(item_tags) < 2:
            messagebox.showwarning("Advertencia", "No se pudo obtener la información del elemento.")
            return

        item_type, element_data = item_tags
        if not messagebox.askyesno("Confirmar", f"¿Eliminar este {item_type.replace('_data', '').capitalize()} y su contenido?"):
            return

        parent_id = self.tree.parent(item_id)

        if item_type == "topic_data":
            if parent_id:
                area_data = self.tree.item(parent_id, 'tags')[1]
                area_data["topics"] = [t for t in area_data["topics"] if t["id"] != element_data["id"]]
            else:
                messagebox.showerror("Error", "No se encontró el área padre.")
                return
        elif item_type == "area":
            if parent_id:
                period_data = self.tree.item(parent_id, 'tags')[1]
                period_data["areas"] = [a for a in period_data["areas"] if a["id"] != element_data["id"]]
            else:
                messagebox.showerror("Error", "No se encontró el periodo padre.")
                return
        elif item_type == "period":
            if parent_id:
                grade_data = self.tree.item(parent_id, 'tags')[1]
                grade_data["periods"] = [p for p in grade_data["periods"] if p["id"] != element_data["id"]]
            else:
                messagebox.showerror("Error", "No se encontró el grado padre.")
                return
        elif item_type == "grade":
            self.data["grades"] = [g for g in self.data["grades"] if g["id"] != element_data["id"]]

        self.save_data()
        self.update_treeview()

    def update_treeview(self):
        # Guardar estado de expansión basado en IDs
        expanded = set()
        def save_expanded(item):
            tags = self.tree.item(item, 'tags')
            if tags and len(tags) > 1 and self.tree.item(item, 'open'):
                expanded.add(tags[1]["id"])
                for child in self.tree.get_children(item):
                    save_expanded(child)
        for item in self.tree.get_children():
            save_expanded(item)

        # Limpiar Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Rellenar Treeview
        for grade_data in self.data.get("grades", []):
            grade_id = self.tree.insert("", tk.END, text=grade_data["name"], open=grade_data["id"] in expanded, tags=("grade", grade_data))
            for period_data in sorted(grade_data.get("periods", []), key=lambda x: int(x["name"].replace("Periodo ", "").strip()) if x["name"].lower().startswith("periodo ") else x["name"]):
                period_id = self.tree.insert(grade_id, tk.END, text=period_data["name"], open=period_data["id"] in expanded, tags=("period", period_data))
                for area_data in sorted(period_data.get("areas", []), key=operator.itemgetter("name")):
                    area_id = self.tree.insert(period_id, tk.END, text=area_data["name"], open=area_data["id"] in expanded, tags=("area", area_data))
                    for topic_data in sorted(area_data.get("topics", []), key=operator.itemgetter("order")):
                        self.tree.insert(area_id, tk.END, values=(topic_data["order"], topic_data["name"], "Completado" if topic_data["completed"] else "Pendiente"), tags=("topic_data", topic_data))

    def save_data(self):
        try:
            os.makedirs(self.full_save_folder, exist_ok=True)
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos: {e}")

    def load_data(self):
        if not os.path.exists(self.save_path):
            self.data = {"grades": []}
            return

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, dict) and "grades" in loaded_data:
                    self.data = loaded_data
                    for grade in self.data["grades"]:
                        grade.setdefault("id", str(uuid.uuid4()))
                        grade.setdefault("name", "Grado Desconocido")
                        grade.setdefault("periods", [])
                        for period in grade["periods"]:
                            period.setdefault("id", str(uuid.uuid4()))
                            period.setdefault("name", "Periodo Desconocido")
                            period.setdefault("areas", [])
                            for area in period["areas"]:
                                area.setdefault("id", str(uuid.uuid4()))
                                area.setdefault("name", "Área Desconocida")
                                area.setdefault("topics", [])
                                for topic in area["topics"]:
                                    topic.setdefault("id", str(uuid.uuid4()))
                                    topic.setdefault("order", 0)
                                    topic.setdefault("name", "Tema sin nombre")
                                    topic.setdefault("completed", False)
                else:
                    self.data = {"grades": []}
                    messagebox.showwarning("Advertencia", "Formato de datos inválido. Iniciando con datos vacíos.")
        except (json.JSONDecodeError, IOError) as e:
            self.data = {"grades": []}
            messagebox.showwarning("Advertencia", f"Error al cargar datos: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MathTrackerApp(root)
    root.mainloop()