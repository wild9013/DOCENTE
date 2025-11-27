import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading
from pathlib import Path
import queue
import json
import time

class SyncApp:
    CONFIG_FILE = "sync_config.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Sincronizador Maestro v3.0")
        self.root.geometry("780x650")
        
        # Estilos
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("Segoe UI", 9, "bold"))
        
        # Cola de mensajes
        self.msg_queue = queue.Queue()
        
        # Variables
        self.source_folder = tk.StringVar()
        self.target_folder = tk.StringVar()
        self.sync_mode = tk.StringVar(value="bidirectional")
        self.delete_sync = tk.BooleanVar(value=False)
        self.is_running = False
        self.cancel_flag = False

        # Interfaz
        self._create_widgets()
        
        # Cargar configuración previa
        self.load_config()
        
        # Iniciar monitor de cola
        self.process_queue()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- 1. Rutas ---
        grp_folders = ttk.LabelFrame(main_frame, text=" Rutas de Archivos ", padding="15")
        grp_folders.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(grp_folders, text="Carpeta Origen:", style="Bold.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(grp_folders, textvariable=self.source_folder).grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(0, 10))
        ttk.Button(grp_folders, text="Examinar...", command=self.select_source).grid(row=1, column=1, pady=(0, 10))

        ttk.Label(grp_folders, text="Carpeta Destino:", style="Bold.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Entry(grp_folders, textvariable=self.target_folder).grid(row=3, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(grp_folders, text="Examinar...", command=self.select_target).grid(row=3, column=1)
        
        grp_folders.columnconfigure(0, weight=1)

        # --- 2. Configuración ---
        grp_opts = ttk.LabelFrame(main_frame, text=" Configuración de Sincronización ", padding="15")
        grp_opts.pack(fill=tk.X, pady=5)

        modes = [
            ("Bidireccional (A ↔ B)", "bidirectional"),
            ("Origen → Destino (Backup)", "source_to_target"),
            ("Destino → Origen (Restaurar)", "target_to_source"),
            ("Espejo Exacto (Mirror)", "mirror")
        ]

        for i, (text, mode) in enumerate(modes):
            col = 0 if i < 2 else 1
            row = i if i < 2 else i - 2
            ttk.Radiobutton(grp_opts, text=text, variable=self.sync_mode, value=mode).grid(row=row, column=col, sticky="w", padx=10, pady=2)

        ttk.Separator(grp_opts, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        
        chk_del = ttk.Checkbutton(grp_opts, text="Habilitar Eliminación (Borrar archivos en destino si no existen en origen)", 
                                variable=self.delete_sync, command=self.toggle_delete_warning)
        chk_del.grid(row=3, column=0, columnspan=2, sticky="w")
        
        self.lbl_warning = ttk.Label(grp_opts, text="⚠ CUIDADO: Esta opción es destructiva.", foreground="red")

        # --- 3. Acciones ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15, fill=tk.X)

        self.btn_sync = ttk.Button(btn_frame, text="▶ INICIAR PROCESO", command=self.start_sync_thread)
        self.btn_sync.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.btn_cancel = ttk.Button(btn_frame, text="⏹ DETENER", command=self.cancel_sync, state="disabled")
        self.btn_cancel.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # --- 4. Estado y Log ---
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.lbl_status = ttk.Label(main_frame, text="Listo.", font=("Segoe UI", 8))
        self.lbl_status.pack(anchor="w")

        self.log_area = tk.Text(main_frame, height=10, state='disabled', font=("Consolas", 9), bg="#f4f4f4", relief="flat")
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Tags de colores
        self.log_area.tag_config("info", foreground="#333")
        self.log_area.tag_config("success", foreground="#2e7d32")
        self.log_area.tag_config("error", foreground="#c62828")
        self.log_area.tag_config("warning", foreground="#ef6c00")
        self.log_area.tag_config("header", foreground="#000", background="#e0e0e0", font=("Consolas", 9, "bold"))

    # --- Persistencia (Guardar/Cargar Config) ---
    def save_config(self):
        data = {
            "source": self.source_folder.get(),
            "target": self.target_folder.get(),
            "mode": self.sync_mode.get(),
            "delete": self.delete_sync.get()
        }
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(data, f)
        except Exception: pass

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.source_folder.set(data.get("source", ""))
                    self.target_folder.set(data.get("target", ""))
                    self.sync_mode.set(data.get("mode", "bidirectional"))
                    self.delete_sync.set(data.get("delete", False))
                    self.toggle_delete_warning()
            except Exception: pass

    # --- Funciones de GUI ---
    def process_queue(self):
        try:
            while True:
                msg_type, content = self.msg_queue.get_nowait()
                if msg_type == "log":
                    text, tag = content
                    self.log_area.configure(state='normal')
                    ts = datetime.now().strftime('%H:%M:%S')
                    self.log_area.insert(tk.END, f"[{ts}] {text}\n", tag)
                    self.log_area.see(tk.END)
                    self.log_area.configure(state='disabled')
                elif msg_type == "progress":
                    val, txt = content
                    self.progress_var.set(val)
                    if txt: self.lbl_status.config(text=txt)
                elif msg_type == "finish":
                    self.toggle_ui_state(True)
                    messagebox.showinfo("Reporte", content)
        except queue.Empty: pass
        finally: self.root.after(100, self.process_queue)

    def log(self, message, tag="info"): self.msg_queue.put(("log", (message, tag)))
    def update_progress(self, val, txt=None): self.msg_queue.put(("progress", (val, txt)))
    
    def toggle_ui_state(self, enabled):
        state = "normal" if enabled else "disabled"
        self.btn_sync.config(state=state)
        self.btn_cancel.config(state="disabled" if enabled else "normal")
        if enabled: self.progress_bar.config(mode='determinate')

    def toggle_delete_warning(self):
        if self.delete_sync.get(): self.lbl_warning.grid(row=4, column=0, columnspan=2, sticky="w", pady=(2,0))
        else: self.lbl_warning.grid_forget()

    def select_source(self):
        path = filedialog.askdirectory()
        if path: self.source_folder.set(path)
    def select_target(self):
        path = filedialog.askdirectory()
        if path: self.target_folder.set(path)
    def cancel_sync(self):
        if self.is_running:
            self.cancel_flag = True
            self.log("Cancelando...", "warning")

    # --- Helpers ---
    def format_bytes(self, size):
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels.get(n, '')}"

    # --- Lógica Core ---
    def scan_folder(self, folder_path):
        file_map = {}
        base = Path(folder_path)
        google_ext = {'.gdoc', '.gsheet', '.gslides', '.gdraw', '.gtable', '.gform', '.shortcut'}
        
        try:
            for p in base.rglob('*'):
                if self.cancel_flag: break
                if p.is_file():
                    if p.name.startswith(('~$', '.tmp')): continue
                    if p.suffix.lower() in google_ext: continue
                    try:
                        stat = p.stat()
                        rel = p.relative_to(base)
                        file_map[rel] = {'mtime': stat.st_mtime, 'size': stat.st_size, 'abs': p}
                    except OSError: pass
        except Exception as e: self.log(f"Error lectura: {e}", "error")
        return file_map

    def get_tasks(self, src_map, tgt_map, mode, delete):
        tasks = []
        all_files = set(src_map.keys()) | set(tgt_map.keys())
        tgt_base = Path(self.target_folder.get())

        for rel in all_files:
            src, tgt = src_map.get(rel), tgt_map.get(rel)
            action = None

            if src and not tgt: # Solo en Origen
                if mode in ["bidirectional", "source_to_target", "mirror"]: action = "copy_src"
                elif mode == "target_to_source" and delete: action = "del_src"
            
            elif tgt and not src: # Solo en Destino
                if mode in ["bidirectional", "target_to_source"]: action = "copy_tgt"
                elif mode in ["source_to_target", "mirror"] and delete: action = "del_tgt"
            
            elif src and tgt: # En ambos
                diff_time = src['mtime'] - tgt['mtime']
                diff_size = src['size'] != tgt['size']
                if diff_size or abs(diff_time) > 2:
                    if mode == "mirror" or (mode == "source_to_target" and src['mtime'] > tgt['mtime']): action = "copy_src"
                    elif mode == "target_to_source" and tgt['mtime'] > src['mtime']: action = "copy_tgt"
                    elif mode == "bidirectional":
                        action = "copy_src" if src['mtime'] > tgt['mtime'] else "copy_tgt"
            
            if action:
                tasks.append({'act': action, 'rel': rel, 'src': src['abs'] if src else None, 'tgt': tgt_base / rel})
        return tasks

    def start_sync_thread(self):
        s, t = self.source_folder.get(), self.target_folder.get()
        if not s or not t or Path(s) == Path(t):
            messagebox.showwarning("Error", "Rutas inválidas."); return
        
        self.save_config() # Guardar configuración antes de empezar
        self.is_running = True; self.cancel_flag = False
        self.toggle_ui_state(False)
        self.log_area.configure(state='normal'); self.log_area.delete(1.0, tk.END); self.log_area.configure(state='disabled')
        threading.Thread(target=self.run_process, args=(s, t), daemon=True).start()

    def run_process(self, source, target):
        start_time = time.time()
        transferred_size = 0
        try:
            mode, delete = self.sync_mode.get(), self.delete_sync.get()
            self.log(f"--- Iniciando: {mode} ---", "header")
            self.update_progress(0, "Escaneando...")

            src_map = self.scan_folder(source)
            tgt_map = self.scan_folder(target)
            if self.cancel_flag: return

            tasks = self.get_tasks(src_map, tgt_map, mode, delete)
            total = len(tasks)
            if total == 0:
                self.msg_queue.put(("finish", "Carpetas sincronizadas. Sin cambios."))
                self.update_progress(100, "Finalizado."); return

            self.log(f"Tareas pendientes: {total}", "info")
            
            for i, t in enumerate(tasks):
                if self.cancel_flag: break
                rel, act = t['rel'], t['act']
                self.update_progress(((i+1)/total)*100, f"Procesando: {rel.name}")

                try:
                    if act == "copy_src":
                        t['tgt'].parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(t['src'], t['tgt'])
                        transferred_size += t['src'].stat().st_size
                        self.log(f"➡ Copiado: {rel}", "success")
                    elif act == "copy_tgt":
                        dest = Path(source) / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(t['tgt'], dest)
                        transferred_size += t['tgt'].stat().st_size
                        self.log(f"⬅ Copiado: {rel}", "success")
                    elif act == "del_tgt":
                        if t['tgt'].exists(): 
                            if t['tgt'].is_dir(): shutil.rmtree(t['tgt'])
                            else: t['tgt'].unlink()
                            self.log(f"🗑 Eliminado Destino: {rel}", "warning")
                    elif act == "del_src":
                        src_f = Path(source) / rel
                        if src_f.exists(): src_f.unlink(); self.log(f"🗑 Eliminado Origen: {rel}", "warning")
                except Exception as e: self.log(f"Error {rel}: {e}", "error")

            self.cleanup_empty_dirs(source); self.cleanup_empty_dirs(target)
            
            duration = time.time() - start_time
            size_fmt = self.format_bytes(transferred_size)
            msg = f"Completado en {duration:.1f}s.\nDatos transferidos: {size_fmt}"
            self.log(f"--- {msg} ---", "header")
            self.msg_queue.put(("finish", msg))

        except Exception as e: self.msg_queue.put(("finish", f"Error Crítico: {e}"))
        finally: self.is_running = False

    def cleanup_empty_dirs(self, folder):
        for d, _, _ in os.walk(folder, topdown=False):
            if d == folder: continue
            try: 
                if not os.listdir(d): os.rmdir(d)
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncApp(root)
    root.mainloop()