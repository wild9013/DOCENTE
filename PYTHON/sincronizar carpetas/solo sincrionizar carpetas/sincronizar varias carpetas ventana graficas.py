import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading

# permite sincronizar varias carpetas propagando la version mas reciente de cada archivo


class SyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sincronizador de Múltiples Carpetas")
        self.root.geometry("700x500")

        # Lista para almacenar las carpetas seleccionadas
        self.folders = []

        # Interfaz gráfica
        tk.Label(root, text="Carpetas Seleccionadas:").pack(pady=5)

        # Treeview para mostrar las carpetas
        self.folder_list = ttk.Treeview(root, columns=("Folder"), show="headings", height=10)
        self.folder_list.heading("Folder", text="Ruta de la Carpeta")
        self.folder_list.column("Folder", width=600)
        self.folder_list.pack(padx=5, pady=5, fill=tk.BOTH)

        # Botones
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Agregar Carpeta", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Eliminar Carpeta", command=self.remove_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sincronizar", command=self.start_sync).pack(side=tk.LEFT, padx=5)

        # Área de log
        self.log_area = tk.Text(root, height=15, width=80, state='disabled')
        self.log_area.pack(padx=5, pady=5, fill=tk.BOTH)

    def log(self, message):
        """Añade un mensaje al área de texto."""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        self.root.update()

    def add_folder(self):
        """Abre un diálogo para seleccionar una carpeta y la agrega a la lista."""
        folder = filedialog.askdirectory()
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.folder_list.insert("", tk.END, values=(folder,))
            self.log(f"Carpeta agregada: {folder}")

    def remove_folder(self):
        """Elimina la carpeta seleccionada de la lista."""
        selected = self.folder_list.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona una carpeta para eliminar.")
            return
        for item in selected:
            folder = self.folder_list.item(item)["values"][0]
            self.folders.remove(folder)
            self.folder_list.delete(item)
            self.log(f"Carpeta eliminada: {folder}")

    def get_file_info(self, folder_path):
        """Obtiene información de archivos en una carpeta: ruta relativa y fecha de modificación."""
        file_info = {}
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, folder_path)
                mod_time = os.path.getmtime(file_path)
                file_info[rel_path] = (file_path, mod_time)
        return file_info

    def sync_folders(self):
        """Sincroniza múltiples carpetas propagando la versión más reciente de cada archivo."""
        if len(self.folders) < 2:
            self.log("Error: Selecciona al menos dos carpetas.")
            raise ValueError("Se necesitan al menos dos carpetas para sincronizar.")

        self.log(f"Sincronizando {len(self.folders)} carpetas: {', '.join(self.folders)}")

        # Obtener información de archivos de todas las carpetas
        all_files = {}
        for folder in self.folders:
            files = self.get_file_info(folder)
            for rel_path, (abs_path, mod_time) in files.items():
                if rel_path not in all_files or mod_time > all_files[rel_path][1]:
                    all_files[rel_path] = (abs_path, mod_time, folder)

        # Sincronizar archivos: copiar la versión más reciente a todas las demás carpetas
        for rel_path, (latest_path, latest_time, source_folder) in all_files.items():
            for target_folder in self.folders:
                if target_folder == source_folder:
                    continue
                target_path = os.path.join(target_folder, rel_path)
                
                # Verificar si el archivo existe en la carpeta destino y su fecha
                if not os.path.exists(target_path):
                    # Copiar archivo si no existe
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.copy2(latest_path, target_path)
                    self.log(f"Copiado: {latest_path} -> {target_path}")
                elif os.path.getmtime(target_path) < latest_time:
                    # Actualizar archivo si es más antiguo
                    shutil.copy2(latest_path, target_path)
                    self.log(f"Actualizado: {latest_path} -> {target_path}")

    def start_sync(self):
        """Inicia el proceso de sincronización en un hilo separado."""
        if len(self.folders) < 2:
            messagebox.showerror("Error", "Selecciona al menos dos carpetas para sincronizar.")
            return

        # Verificar que todas las carpetas existan
        for folder in self.folders:
            if not os.path.exists(folder):
                messagebox.showerror("Error", f"La carpeta {folder} no existe.")
                return

        # Ejecutar sincronización en un hilo separado
        def sync_thread():
            try:
                self.sync_folders()
                self.log("Sincronización completada.")
                self.root.after(0, lambda: messagebox.showinfo("Éxito", "Sincronización completada."))
            except Exception as e:
                self.log(f"Error durante la sincronización: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error durante la sincronización: {e}"))

        threading.Thread(target=sync_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncApp(root)
    root.mainloop()