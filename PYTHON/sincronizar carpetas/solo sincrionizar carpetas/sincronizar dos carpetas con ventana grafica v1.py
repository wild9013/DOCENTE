import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import threading

class SyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sincronizador de Carpetas")
        self.root.geometry("600x400")

        # Variables para las rutas
        self.source_folder = tk.StringVar()
        self.target_folder = tk.StringVar()

        # Interfaz gráfica
        tk.Label(root, text="Carpeta Origen:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(root, textvariable=self.source_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Seleccionar", command=self.select_source).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(root, text="Carpeta Destino:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(root, textvariable=self.target_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="Seleccionar", command=self.select_target).grid(row=1, column=2, padx=5, pady=5)

        tk.Button(root, text="Sincronizar", command=self.start_sync).grid(row=2, column=0, columnspan=3, pady=10)

        self.log_area = tk.Text(root, height=15, width=70, state='disabled')
        self.log_area.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

    def log(self, message):
        """Añade un mensaje al área de texto."""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        self.root.update()

    def select_source(self):
        """Abre un diálogo para seleccionar la carpeta origen."""
        folder = filedialog.askdirectory()
        if folder:
            self.source_folder.set(folder)

    def select_target(self):
        """Abre un diálogo para seleccionar la carpeta destino."""
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder.set(folder)

    def get_file_info(self, folder_path):
        """Obtiene información de archivos en una carpeta: ruta y fecha de modificación."""
        file_info = {}
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                mod_time = os.path.getmtime(file_path)
                file_info[file_path] = mod_time
        return file_info

    def sync_folders(self, source_folder, target_folder):
        """Sincroniza dos carpetas manteniendo la versión más reciente de cada archivo."""
        self.log(f"Sincronizando: {source_folder} <-> {target_folder}")
        
        source_files = self.get_file_info(source_folder)
        target_files = self.get_file_info(target_folder)
        
        # Sincronizar de source a target
        for src_path, src_time in source_files.items():
            rel_path = os.path.relpath(src_path, source_folder)
            tgt_path = os.path.join(target_folder, rel_path)
            
            if tgt_path not in target_files:
                os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
                shutil.copy2(src_path, tgt_path)
                self.log(f"Copiado: {src_path} -> {tgt_path}")
            elif src_time > target_files[tgt_path]:
                shutil.copy2(src_path, tgt_path)
                self.log(f"Actualizado: {src_path} -> {tgt_path}")
        
        # Sincronizar de target a source
        for tgt_path, tgt_time in target_files.items():
            rel_path = os.path.relpath(tgt_path, target_folder)
            src_path = os.path.join(source_folder, rel_path)
            
            if src_path not in source_files:
                os.makedirs(os.path.dirname(src_path), exist_ok=True)
                shutil.copy2(tgt_path, src_path)
                self.log(f"Copiado: {tgt_path} -> {src_path}")
            elif tgt_time > source_files[src_path]:
                shutil.copy2(tgt_path, src_path)
                self.log(f"Actualizado: {tgt_path} -> {src_path}")

    def start_sync(self):
        """Inicia el proceso de sincronización en un hilo separado."""
        source_folder = self.source_folder.get()
        target_folder = self.target_folder.get()

        if not source_folder or not target_folder:
            messagebox.showerror("Error", "Por favor, selecciona ambas carpetas.")
            return
        
        if not os.path.exists(source_folder):
            messagebox.showerror("Error", f"La carpeta origen {source_folder} no existe.")
            return
        if not os.path.exists(target_folder):
            messagebox.showerror("Error", f"La carpeta destino {target_folder} no existe.")
            return

        # Ejecutar sincronización en un hilo separado para no bloquear la UI
        def sync_thread():
            try:
                self.sync_folders(source_folder, target_folder)
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