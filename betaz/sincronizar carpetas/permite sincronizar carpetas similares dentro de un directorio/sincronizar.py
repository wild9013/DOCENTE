import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading

class SyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sincronizador de Carpetas en Directorio Raíz")
        self.root.geometry("700x500")

        # Variables
        self.root_dir = tk.StringVar()
        self.folder_name = tk.StringVar()
        self.folders = []  # Lista de carpetas encontradas

        # Interfaz gráfica
        tk.Label(root, text="Directorio Raíz:").pack(pady=5)
        tk.Entry(root, textvariable=self.root_dir, width=60).pack(padx=5, pady=5)
        tk.Button(root, text="Seleccionar", command=self.select_root_dir).pack(pady=5)

        tk.Label(root, text="Nombre de la Carpeta a Buscar:").pack(pady=5)
        tk.Entry(root, textvariable=self.folder_name, width=60).pack(padx=5, pady=5)

        tk.Button(root, text="Buscar Carpetas", command=self.search_folders).pack(pady=5)

        tk.Label(root, text="Carpetas Encontradas:").pack(pady=5)
        self.folder_list = ttk.Treeview(root, columns=("Folder"), show="headings", height=8)
        self.folder_list.heading("Folder", text="Ruta de la Carpeta")
        self.folder_list.column("Folder", width=600)
        self.folder_list.pack(padx=5, pady=5, fill=tk.BOTH)

        tk.Button(root, text="Sincronizar", command=self.start_sync).pack(pady=10)

        self.log_area = tk.Text(root, height=10, width=80, state='disabled')
        self.log_area.pack(padx=5, pady=5, fill=tk.BOTH)

    def log(self, message):
        """Añade un mensaje al área de texto."""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        self.root.update()

    def select_root_dir(self):
        """Abre un diálogo para seleccionar el directorio raíz."""
        directory = filedialog.askdirectory()
        if directory:
            self.root_dir.set(directory)
            self.log(f"Directorio raíz seleccionado: {directory}")

    def search_folders(self):
        """Busca la carpeta especificada en el directorio raíz y sus subdirectorios."""
        root_dir = self.root_dir.get()
        folder_name = self.folder_name.get()

        if not root_dir or not folder_name:
            messagebox.showerror("Error", "Por favor, selecciona un directorio raíz y especifica el nombre de la carpeta.")
            return

        if not os.path.exists(root_dir):
            messagebox.showerror("Error", f"El directorio raíz {root_dir} no existe.")
            return

        # Limpiar lista anterior
        self.folders = []
        for item in self.folder_list.get_children():
            self.folder_list.delete(item)

        # Buscar carpetas
        self.log(f"Buscando carpetas con nombre '{folder_name}' en {root_dir}")
        for root, dirs, _ in os.walk(root_dir):
            if folder_name in dirs:
                folder_path = os.path.join(root, folder_name)
                self.folders.append(folder_path)
                self.folder_list.insert("", tk.END, values=(folder_path,))
                self.log(f"Carpeta encontrada: {folder_path}")

        if not self.folders:
            self.log("No se encontraron carpetas con ese nombre.")
            messagebox.showwarning("Advertencia", f"No se encontraron carpetas con el nombre '{folder_name}'.")
        else:
            self.log(f"Se encontraron {len(self.folders)} carpetas.")

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
        """Sincroniza las carpetas encontradas propagando la versión más reciente de cada archivo."""
        if len(self.folders) < 2:
            self.log("Error: Se necesitan al menos dos carpetas para sincronizar.")
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
                
                if not os.path.exists(target_path):
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    shutil.copy2(latest_path, target_path)
                    self.log(f"Copiado: {latest_path} -> {target_path}")
                elif os.path.getmtime(target_path) < latest_time:
                    shutil.copy2(latest_path, target_path)
                    self.log(f"Actualizado: {latest_path} -> {target_path}")

    def start_sync(self):
        """Inicia el proceso de sincronización en un hilo separado."""
        if len(self.folders) < 2:
            messagebox.showerror("Error", "Se necesitan al menos dos carpetas para sincronizar.")
            return

        for folder in self.folders:
            if not os.path.exists(folder):
                messagebox.showerror("Error", f"La carpeta {folder} no existe.")
                return

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