import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading
from pathlib import Path
import hashlib

class SyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sincronizador de Carpetas")
        self.root.geometry("700x500")
        
        self.source_folder = tk.StringVar()
        self.target_folder = tk.StringVar()
        self.sync_running = False

        self._create_widgets()

    def _create_widgets(self):
        """Crea la interfaz gráfica."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Carpeta origen
        ttk.Label(main_frame, text="Carpeta Origen:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(main_frame, textvariable=self.source_folder, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Seleccionar", command=self.select_source).grid(row=0, column=2, padx=5, pady=5)

        # Carpeta destino
        ttk.Label(main_frame, text="Carpeta Destino:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(main_frame, textvariable=self.target_folder, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Seleccionar", command=self.select_target).grid(row=1, column=2, padx=5, pady=5)

        # Botón de sincronización
        self.sync_button = ttk.Button(main_frame, text="Sincronizar", command=self.start_sync)
        self.sync_button.grid(row=2, column=0, columnspan=3, pady=10)

        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=3, column=0, columnspan=3, pady=5)

        # Área de log
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_area = tk.Text(log_frame, height=18, width=80, state='disabled', wrap='word')
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_area.yview)
        self.log_area.configure(yscrollcommand=scrollbar.set)
        
        self.log_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def log(self, message):
        """Añade un mensaje al área de texto de forma thread-safe."""
        def update_log():
            self.log_area.configure(state='normal')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_area.see(tk.END)
            self.log_area.configure(state='disabled')
        
        self.root.after(0, update_log)

    def select_source(self):
        """Selecciona la carpeta origen."""
        folder = filedialog.askdirectory(title="Seleccionar Carpeta Origen")
        if folder:
            self.source_folder.set(folder)

    def select_target(self):
        """Selecciona la carpeta destino."""
        folder = filedialog.askdirectory(title="Seleccionar Carpeta Destino")
        if folder:
            self.target_folder.set(folder)

    def get_file_hash(self, file_path, chunk_size=8192):
        """Calcula el hash SHA256 de un archivo para comparación exacta."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.log(f"Error calculando hash de {file_path}: {e}")
            return None

    def is_google_drive_file(self, file_path):
        """Detecta si es un archivo de acceso directo de Google Drive."""
        google_extensions = {'.gdoc', '.gsheet', '.gslides', '.gdraw', '.gtable', '.gform', '.gmaps', '.gsite'}
        return file_path.suffix.lower() in google_extensions
    
    def get_file_info(self, folder_path):
        """Obtiene información optimizada de archivos usando Path."""
        file_info = {}
        folder = Path(folder_path)
        
        try:
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    # Omitir archivos de acceso directo de Google Drive
                    if self.is_google_drive_file(file_path):
                        continue
                    
                    try:
                        stat = file_path.stat()
                        file_info[str(file_path)] = {
                            'mtime': stat.st_mtime,
                            'size': stat.st_size
                        }
                    except (PermissionError, OSError) as e:
                        self.log(f"⚠ Omitido (sin acceso): {file_path.name}")
        except Exception as e:
            self.log(f"Error escaneando carpeta {folder_path}: {e}")
        
        return file_info

    def should_copy_file(self, src_path, tgt_path, src_info, tgt_info):
        """Determina si un archivo debe copiarse usando comparación inteligente."""
        # Si el archivo destino no existe
        if tgt_info is None:
            return True
        
        # Comparar tamaños primero (más rápido)
        if src_info['size'] != tgt_info['size']:
            return src_info['mtime'] > tgt_info['mtime']
        
        # Si tienen el mismo tamaño y tiempo de modificación similar, comparar hash
        time_diff = abs(src_info['mtime'] - tgt_info['mtime'])
        if time_diff < 2:  # Menos de 2 segundos de diferencia
            src_hash = self.get_file_hash(src_path)
            tgt_hash = self.get_file_hash(tgt_path)
            return src_hash != tgt_hash and src_info['mtime'] > tgt_info['mtime']
        
        return src_info['mtime'] > tgt_info['mtime']

    def sync_folders(self, source_folder, target_folder):
        """Sincroniza dos carpetas de forma bidireccional optimizada."""
        self.log(f"Iniciando sincronización...")
        self.log(f"Origen: {source_folder}")
        self.log(f"Destino: {target_folder}")
        
        source_files = self.get_file_info(source_folder)
        target_files = self.get_file_info(target_folder)
        
        self.log(f"Archivos encontrados - Origen: {len(source_files)}, Destino: {len(target_files)}")
        
        copied_count = 0
        updated_count = 0
        errors = 0
        
        # Sincronizar de origen a destino
        for src_path, src_info in source_files.items():
            if not self.sync_running:
                self.log("Sincronización cancelada por el usuario.")
                return
            
            try:
                rel_path = str(Path(src_path).relative_to(source_folder))
                tgt_path = str(Path(target_folder) / rel_path)
                tgt_info = target_files.get(tgt_path)
                
                if self.should_copy_file(src_path, tgt_path, src_info, tgt_info):
                    Path(tgt_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, tgt_path)
                    
                    if tgt_info is None:
                        self.log(f"✓ Copiado: {rel_path}")
                        copied_count += 1
                    else:
                        self.log(f"↻ Actualizado: {rel_path}")
                        updated_count += 1
            except Exception as e:
                self.log(f"✗ Error con {rel_path}: {e}")
                errors += 1
        
        # Sincronizar de destino a origen
        for tgt_path, tgt_info in target_files.items():
            if not self.sync_running:
                self.log("Sincronización cancelada por el usuario.")
                return
            
            try:
                rel_path = str(Path(tgt_path).relative_to(target_folder))
                src_path = str(Path(source_folder) / rel_path)
                src_info = source_files.get(src_path)
                
                if self.should_copy_file(tgt_path, src_path, tgt_info, src_info):
                    Path(src_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(tgt_path, src_path)
                    
                    if src_info is None:
                        self.log(f"✓ Copiado (inverso): {rel_path}")
                        copied_count += 1
                    else:
                        self.log(f"↻ Actualizado (inverso): {rel_path}")
                        updated_count += 1
            except Exception as e:
                self.log(f"✗ Error con {rel_path}: {e}")
                errors += 1
        
        self.log(f"\n=== Resumen ===")
        self.log(f"Archivos copiados: {copied_count}")
        self.log(f"Archivos actualizados: {updated_count}")
        self.log(f"Errores: {errors}")

    def start_sync(self):
        """Inicia el proceso de sincronización."""
        if self.sync_running:
            self.log("Ya hay una sincronización en curso.")
            return
        
        source = self.source_folder.get()
        target = self.target_folder.get()

        if not source or not target:
            messagebox.showerror("Error", "Por favor, selecciona ambas carpetas.")
            return
        
        if not Path(source).exists():
            messagebox.showerror("Error", f"La carpeta origen no existe:\n{source}")
            return
        
        if not Path(target).exists():
            messagebox.showerror("Error", f"La carpeta destino no existe:\n{target}")
            return
        
        if Path(source).resolve() == Path(target).resolve():
            messagebox.showerror("Error", "Las carpetas origen y destino no pueden ser la misma.")
            return

        def sync_thread():
            self.sync_running = True
            self.root.after(0, lambda: self.sync_button.config(state='disabled'))
            self.root.after(0, lambda: self.progress.start(10))
            
            try:
                self.sync_folders(source, target)
                self.log("\n✓ Sincronización completada exitosamente.")
                self.root.after(0, lambda: messagebox.showinfo("Éxito", "Sincronización completada."))
            except Exception as e:
                self.log(f"\n✗ Error crítico: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error durante la sincronización:\n{e}"))
            finally:
                self.sync_running = False
                self.root.after(0, lambda: self.sync_button.config(state='normal'))
                self.root.after(0, lambda: self.progress.stop())

        threading.Thread(target=sync_thread, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncApp(root)
    root.mainloop()