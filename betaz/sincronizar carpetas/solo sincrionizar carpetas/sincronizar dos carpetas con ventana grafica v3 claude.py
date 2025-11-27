import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import threading
from pathlib import Path
import hashlib
import json
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class SyncMode(Enum):
    """Modos de sincronización disponibles."""
    BIDIRECTIONAL = "bidirectional"
    SOURCE_TO_TARGET = "source_to_target"
    TARGET_TO_SOURCE = "target_to_source"
    MIRROR = "mirror"

@dataclass
class FileMetadata:
    """Información de un archivo."""
    path: str
    mtime: float
    size: int
    hash: Optional[str] = None

@dataclass
class SyncStats:
    """Estadísticas de sincronización."""
    copied: int = 0
    updated: int = 0
    deleted: int = 0
    skipped: int = 0
    errors: int = 0

class ConfigManager:
    """Gestiona la configuración persistente."""
    CONFIG_FILE = "sync_config.json"
    
    @staticmethod
    def save_config(source: str, target: str, mode: str, delete_sync: bool):
        """Guarda la última configuración."""
        try:
            config = {
                "last_source": source,
                "last_target": target,
                "last_mode": mode,
                "delete_sync": delete_sync
            }
            with open(ConfigManager.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
    
    @staticmethod
    def load_config() -> Dict:
        """Carga la última configuración."""
        try:
            if Path(ConfigManager.CONFIG_FILE).exists():
                with open(ConfigManager.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

class FileScanner:
    """Escanea y analiza archivos en carpetas."""
    
    GOOGLE_DRIVE_EXTENSIONS = {'.gdoc', '.gsheet', '.gslides', '.gdraw', '.gtable', '.gform', '.gmaps', '.gsite'}
    HASH_CHUNK_SIZE = 65536  # 64KB chunks para mejor rendimiento
    
    @staticmethod
    def is_google_drive_file(file_path: Path) -> bool:
        """Detecta archivos de Google Drive."""
        return file_path.suffix.lower() in FileScanner.GOOGLE_DRIVE_EXTENSIONS
    
    @staticmethod
    def calculate_hash(file_path: str) -> Optional[str]:
        """Calcula hash SHA256 de forma eficiente."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(FileScanner.HASH_CHUNK_SIZE):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def scan_folder(folder_path: str, log_callback=None) -> Dict[str, FileMetadata]:
        """Escanea una carpeta y retorna metadatos de archivos."""
        file_info = {}
        folder = Path(folder_path)
        
        try:
            for file_path in folder.rglob('*'):
                if not file_path.is_file():
                    continue
                
                if FileScanner.is_google_drive_file(file_path):
                    continue
                
                try:
                    stat = file_path.stat()
                    file_info[str(file_path)] = FileMetadata(
                        path=str(file_path),
                        mtime=stat.st_mtime,
                        size=stat.st_size
                    )
                except (PermissionError, OSError) as e:
                    if log_callback:
                        log_callback(f"⚠ Sin acceso: {file_path.name}")
        except Exception as e:
            if log_callback:
                log_callback(f"Error escaneando {folder_path}: {e}")
        
        return file_info

class SyncEngine:
    """Motor de sincronización."""
    
    def __init__(self, log_callback, check_running_callback):
        self.log = log_callback
        self.is_running = check_running_callback
    
    def should_copy(self, src_meta: FileMetadata, tgt_meta: Optional[FileMetadata], 
                    mode: SyncMode) -> bool:
        """Determina si un archivo debe copiarse."""
        if tgt_meta is None:
            return True
        
        if mode == SyncMode.MIRROR:
            return (src_meta.mtime != tgt_meta.mtime or 
                   src_meta.size != tgt_meta.size)
        
        # Comparar tamaños primero (más rápido)
        if src_meta.size != tgt_meta.size:
            return src_meta.mtime > tgt_meta.mtime
        
        # Si tienen tamaño similar y tiempo cercano, comparar hash
        time_diff = abs(src_meta.mtime - tgt_meta.mtime)
        if time_diff < 2:  # Menos de 2 segundos
            if src_meta.hash is None:
                src_meta.hash = FileScanner.calculate_hash(src_meta.path)
            if tgt_meta.hash is None:
                tgt_meta.hash = FileScanner.calculate_hash(tgt_meta.path)
            
            if src_meta.hash and tgt_meta.hash:
                return (src_meta.hash != tgt_meta.hash and 
                       src_meta.mtime > tgt_meta.mtime)
        
        return src_meta.mtime > tgt_meta.mtime
    
    def copy_file(self, src_path: str, tgt_path: str, stats: SyncStats, 
                  is_new: bool, direction: str = "→") -> bool:
        """Copia un archivo y actualiza estadísticas."""
        try:
            Path(tgt_path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, tgt_path)
            
            rel_path = Path(src_path).name
            if is_new:
                self.log(f"✓ Copiado {direction}: {rel_path}")
                stats.copied += 1
            else:
                self.log(f"↻ Actualizado {direction}: {rel_path}")
                stats.updated += 1
            return True
        except Exception as e:
            self.log(f"✗ Error copiando {Path(src_path).name}: {e}")
            stats.errors += 1
            return False
    
    def delete_file(self, file_path: str, stats: SyncStats, location: str) -> bool:
        """Elimina un archivo y actualiza estadísticas."""
        try:
            file_obj = Path(file_path)
            if file_obj.exists():
                file_obj.unlink()
                self.log(f"🗑 Eliminado en {location}: {file_obj.name}")
                stats.deleted += 1
                
                # Limpiar carpetas vacías
                self._cleanup_empty_dirs(file_obj.parent)
                return True
        except Exception as e:
            self.log(f"✗ Error eliminando {Path(file_path).name}: {e}")
            stats.errors += 1
        return False
    
    def _cleanup_empty_dirs(self, directory: Path):
        """Elimina carpetas vacías recursivamente."""
        try:
            if directory.exists() and not any(directory.iterdir()):
                directory.rmdir()
                self._cleanup_empty_dirs(directory.parent)
        except Exception:
            pass
    
    def sync(self, source_folder: str, target_folder: str, 
             mode: SyncMode, delete_sync: bool) -> SyncStats:
        """Ejecuta la sincronización completa."""
        stats = SyncStats()
        
        # Escanear carpetas
        self.log("📂 Escaneando carpetas...")
        source_files = FileScanner.scan_folder(source_folder, self.log)
        target_files = FileScanner.scan_folder(target_folder, self.log)
        
        self.log(f"Archivos encontrados - Origen: {len(source_files)}, Destino: {len(target_files)}")
        
        # Sincronizar origen → destino
        if mode in [SyncMode.BIDIRECTIONAL, SyncMode.SOURCE_TO_TARGET, SyncMode.MIRROR]:
            self._sync_direction(source_files, target_files, source_folder, 
                               target_folder, stats, mode, "→")
        
        # Sincronizar destino → origen
        if mode in [SyncMode.BIDIRECTIONAL, SyncMode.TARGET_TO_SOURCE]:
            self._sync_direction(target_files, source_files, target_folder, 
                               source_folder, stats, mode, "←")
        
        # Gestionar eliminaciones
        if delete_sync or mode == SyncMode.MIRROR:
            self._handle_deletions(source_files, target_files, source_folder, 
                                  target_folder, stats, mode, delete_sync)
        
        return stats
    
    def _sync_direction(self, src_files: Dict, tgt_files: Dict, 
                       src_folder: str, tgt_folder: str, 
                       stats: SyncStats, mode: SyncMode, direction: str):
        """Sincroniza archivos en una dirección."""
        for src_path, src_meta in src_files.items():
            if not self.is_running():
                return
            
            try:
                rel_path = str(Path(src_path).relative_to(src_folder))
                tgt_path = str(Path(tgt_folder) / rel_path)
                tgt_meta = tgt_files.get(tgt_path)
                
                if self.should_copy(src_meta, tgt_meta, mode):
                    self.copy_file(src_path, tgt_path, stats, 
                                 tgt_meta is None, direction)
            except Exception as e:
                self.log(f"✗ Error procesando {Path(src_path).name}: {e}")
                stats.errors += 1
    
    def _handle_deletions(self, src_files: Dict, tgt_files: Dict,
                         src_folder: str, tgt_folder: str,
                         stats: SyncStats, mode: SyncMode, delete_sync: bool):
        """Gestiona eliminación de archivos."""
        # Eliminar en destino archivos no presentes en origen
        if mode in [SyncMode.BIDIRECTIONAL, SyncMode.SOURCE_TO_TARGET, SyncMode.MIRROR]:
            for tgt_path in list(tgt_files.keys()):
                if not self.is_running():
                    return
                
                rel_path = str(Path(tgt_path).relative_to(tgt_folder))
                src_path = str(Path(src_folder) / rel_path)
                
                if src_path not in src_files:
                    self.delete_file(tgt_path, stats, "destino")
        
        # Eliminar en origen archivos no presentes en destino
        if delete_sync and mode in [SyncMode.BIDIRECTIONAL, SyncMode.TARGET_TO_SOURCE]:
            for src_path in list(src_files.keys()):
                if not self.is_running():
                    return
                
                rel_path = str(Path(src_path).relative_to(src_folder))
                tgt_path = str(Path(tgt_folder) / rel_path)
                
                if tgt_path not in tgt_files:
                    self.delete_file(src_path, stats, "origen")

class SyncApp:
    """Aplicación principal de sincronización."""
    
    MODE_NAMES = {
        SyncMode.BIDIRECTIONAL: "Bidireccional",
        SyncMode.SOURCE_TO_TARGET: "Origen → Destino",
        SyncMode.TARGET_TO_SOURCE: "Destino → Origen",
        SyncMode.MIRROR: "Espejo"
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sincronizador de Carpetas Pro")
        self.root.geometry("750x550")
        
        self.source_folder = tk.StringVar()
        self.target_folder = tk.StringVar()
        self.sync_mode = tk.StringVar(value=SyncMode.BIDIRECTIONAL.value)
        self.delete_sync = tk.BooleanVar(value=False)
        self.sync_running = False
        
        self._load_last_config()
        self._create_widgets()
        self._apply_styles()
    
    def _load_last_config(self):
        """Carga la última configuración guardada."""
        config = ConfigManager.load_config()
        if config:
            self.source_folder.set(config.get("last_source", ""))
            self.target_folder.set(config.get("last_target", ""))
            self.sync_mode.set(config.get("last_mode", SyncMode.BIDIRECTIONAL.value))
            self.delete_sync.set(config.get("delete_sync", False))
    
    def _apply_styles(self):
        """Aplica estilos personalizados."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('Title.TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('Warning.TLabel', foreground='#d32f2f', font=('Segoe UI', 9))
        style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'))
    
    def _create_widgets(self):
        """Crea la interfaz gráfica."""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Carpetas
        self._create_folder_selectors(main_frame)
        
        # Modos de sincronización
        self._create_sync_modes(main_frame)
        
        # Opciones de eliminación
        self._create_delete_options(main_frame)
        
        # Controles
        self._create_controls(main_frame)
        
        # Log
        self._create_log_area(main_frame)
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(8, weight=1)
    
    def _create_folder_selectors(self, parent):
        """Crea selectores de carpetas."""
        ttk.Label(parent, text="Carpeta Origen:", style='Title.TLabel').grid(
            row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(parent, textvariable=self.source_folder, width=55).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(parent, text="📁 Buscar", command=self.select_source).grid(
            row=0, column=2, padx=5, pady=5)
        
        ttk.Label(parent, text="Carpeta Destino:", style='Title.TLabel').grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(parent, textvariable=self.target_folder, width=55).grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(parent, text="📁 Buscar", command=self.select_target).grid(
            row=1, column=2, padx=5, pady=5)
    
    def _create_sync_modes(self, parent):
        """Crea selector de modo de sincronización."""
        ttk.Separator(parent, orient='horizontal').grid(
            row=2, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Label(parent, text="Modo:", style='Title.TLabel').grid(
            row=3, column=0, padx=5, pady=5, sticky="ne")
        
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        
        modes = [
            (SyncMode.BIDIRECTIONAL, "🔄 Bidireccional - Sincroniza cambios en ambas direcciones"),
            (SyncMode.SOURCE_TO_TARGET, "→ Origen → Destino - Solo copia del origen al destino"),
            (SyncMode.TARGET_TO_SOURCE, "← Destino → Origen - Solo copia del destino al origen"),
            (SyncMode.MIRROR, "🪞 Espejo - Destino = copia exacta del origen (elimina extras)")
        ]
        
        for mode, text in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.sync_mode, 
                          value=mode.value).pack(anchor="w", pady=2)
    
    def _create_delete_options(self, parent):
        """Crea opciones de sincronización de eliminaciones."""
        ttk.Separator(parent, orient='horizontal').grid(
            row=4, column=0, columnspan=3, sticky='ew', pady=10)
        
        delete_frame = ttk.Frame(parent)
        delete_frame.grid(row=5, column=0, columnspan=3, sticky="w", padx=5)
        
        self.delete_checkbox = ttk.Checkbutton(
            delete_frame,
            text="⚠️ Sincronizar eliminaciones (si un archivo se elimina en una carpeta, eliminarlo en la otra)",
            variable=self.delete_sync,
            command=self.toggle_delete_sync
        )
        self.delete_checkbox.pack(anchor="w")
        
        self.delete_warning = ttk.Label(
            delete_frame,
            text="⛔ ADVERTENCIA: Esta opción eliminará archivos permanentemente. Úsala con precaución.",
            style='Warning.TLabel'
        )
        
        if self.delete_sync.get():
            self.delete_warning.pack(anchor="w", pady=(5, 0))
    
    def _create_controls(self, parent):
        """Crea controles de acción."""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.sync_button = ttk.Button(
            control_frame, text="▶ Iniciar Sincronización", 
            command=self.start_sync, style='Action.TButton')
        self.sync_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="🗑 Limpiar Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(parent, mode='indeterminate', length=500)
        self.progress.grid(row=7, column=0, columnspan=3, pady=5)
    
    def _create_log_area(self, parent):
        """Crea área de log."""
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(log_frame, text="Registro de Actividad:", style='Title.TLabel').pack(
            anchor="w", pady=(0, 5))
        
        self.log_area = tk.Text(log_frame, height=15, width=85, 
                               state='disabled', wrap='word', 
                               bg='#f5f5f5', relief=tk.FLAT, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', 
                                 command=self.log_area.yview)
        self.log_area.configure(yscrollcommand=scrollbar.set)
        
        self.log_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def log(self, message: str):
        """Añade mensaje al log de forma thread-safe."""
        def update():
            self.log_area.configure(state='normal')
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_area.see(tk.END)
            self.log_area.configure(state='disabled')
        
        self.root.after(0, update)
    
    def clear_log(self):
        """Limpia el área de log."""
        self.log_area.configure(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state='disabled')
    
    def toggle_delete_sync(self):
        """Muestra/oculta advertencia de eliminación."""
        if self.delete_sync.get():
            self.delete_warning.pack(anchor="w", pady=(5, 0))
        else:
            self.delete_warning.pack_forget()
    
    def select_source(self):
        """Selecciona carpeta origen."""
        folder = filedialog.askdirectory(
            title="Seleccionar Carpeta Origen",
            initialdir=self.source_folder.get() or None)
        if folder:
            self.source_folder.set(folder)
    
    def select_target(self):
        """Selecciona carpeta destino."""
        folder = filedialog.askdirectory(
            title="Seleccionar Carpeta Destino",
            initialdir=self.target_folder.get() or None)
        if folder:
            self.target_folder.set(folder)
    
    def validate_inputs(self) -> bool:
        """Valida las entradas del usuario."""
        source = self.source_folder.get()
        target = self.target_folder.get()
        
        if not source or not target:
            messagebox.showerror("Error", "Selecciona ambas carpetas.")
            return False
        
        if not Path(source).exists():
            messagebox.showerror("Error", f"La carpeta origen no existe:\n{source}")
            return False
        
        if not Path(target).exists():
            messagebox.showerror("Error", f"La carpeta destino no existe:\n{target}")
            return False
        
        if Path(source).resolve() == Path(target).resolve():
            messagebox.showerror("Error", "Las carpetas no pueden ser la misma.")
            return False
        
        return True
    
    def start_sync(self):
        """Inicia la sincronización."""
        if self.sync_running:
            self.log("⚠ Ya hay una sincronización en curso.")
            return
        
        if not self.validate_inputs():
            return
        
        # Guardar configuración
        ConfigManager.save_config(
            self.source_folder.get(),
            self.target_folder.get(),
            self.sync_mode.get(),
            self.delete_sync.get()
        )
        
        def sync_thread():
            self.sync_running = True
            self.root.after(0, lambda: self.sync_button.config(state='disabled', text='⏳ Sincronizando...'))
            self.root.after(0, lambda: self.progress.start(10))
            
            try:
                mode = SyncMode(self.sync_mode.get())
                self.log(f"\n{'='*60}")
                self.log(f"🚀 Iniciando sincronización - Modo: {self.MODE_NAMES[mode]}")
                if self.delete_sync.get() and mode != SyncMode.MIRROR:
                    self.log(f"⚠️ Sincronización de eliminaciones: ACTIVADA")
                self.log(f"📂 Origen: {self.source_folder.get()}")
                self.log(f"📂 Destino: {self.target_folder.get()}")
                self.log(f"{'='*60}\n")
                
                engine = SyncEngine(self.log, lambda: self.sync_running)
                stats = engine.sync(
                    self.source_folder.get(),
                    self.target_folder.get(),
                    mode,
                    self.delete_sync.get()
                )
                
                self.log(f"\n{'='*60}")
                self.log("📊 RESUMEN DE SINCRONIZACIÓN")
                self.log(f"{'='*60}")
                self.log(f"✅ Archivos copiados: {stats.copied}")
                self.log(f"🔄 Archivos actualizados: {stats.updated}")
                if stats.deleted > 0:
                    self.log(f"🗑️ Archivos eliminados: {stats.deleted}")
                if stats.errors > 0:
                    self.log(f"❌ Errores: {stats.errors}")
                self.log(f"{'='*60}\n")
                self.log("✅ Sincronización completada exitosamente.\n")
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "Éxito", 
                    f"Sincronización completada.\n\n"
                    f"Copiados: {stats.copied}\n"
                    f"Actualizados: {stats.updated}\n"
                    f"Eliminados: {stats.deleted}\n"
                    f"Errores: {stats.errors}"
                ))
            except Exception as e:
                self.log(f"\n❌ Error crítico: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", f"Error durante la sincronización:\n{e}"))
            finally:
                self.sync_running = False
                self.root.after(0, lambda: self.sync_button.config(
                    state='normal', text='▶ Iniciar Sincronización'))
                self.root.after(0, lambda: self.progress.stop())
        
        threading.Thread(target=sync_thread, daemon=True).start()

def main():
    """Función principal."""
    root = tk.Tk()
    app = SyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()