# NOTAS DEL AUTOR: esta versión solo sincroniza dos carpetas y todos sus archivos 


import os
import shutil
import time
from datetime import datetime

def get_file_info(folder_path):
    """Obtiene información de archivos en una carpeta: ruta y fecha de modificación."""
    file_info = {}
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Obtener fecha de última modificación
            mod_time = os.path.getmtime(file_path)
            file_info[file_path] = mod_time
    return file_info

def sync_folders(source_folder, target_folder):
    """Sincroniza dos carpetas manteniendo la versión más reciente de cada archivo."""
    print(f"Sincronizando: {source_folder} <-> {target_folder}")
    
    # Obtener información de archivos de ambas carpetas
    source_files = get_file_info(source_folder)
    target_files = get_file_info(target_folder)
    
    # Sincronizar de source a target
    for src_path, src_time in source_files.items():
        # Calcular la ruta equivalente en la carpeta destino
        rel_path = os.path.relpath(src_path, source_folder)
        tgt_path = os.path.join(target_folder, rel_path)
        
        if tgt_path not in target_files:
            # El archivo no existe en target, copiarlo
            os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
            shutil.copy2(src_path, tgt_path)
            print(f"Copiado: {src_path} -> {tgt_path}")
        elif src_time > target_files[tgt_path]:
            # El archivo en source es más reciente, sobrescribirlo
            shutil.copy2(src_path, tgt_path)
            print(f"Actualizado: {src_path} -> {tgt_path}")
    
    # Sincronizar de target a source
    for tgt_path, tgt_time in target_files.items():
        # Calcular la ruta equivalente en la carpeta origen
        rel_path = os.path.relpath(tgt_path, target_folder)
        src_path = os.path.join(source_folder, rel_path)
        
        if src_path not in source_files:
            # El archivo no existe en source, copiarlo
            os.makedirs(os.path.dirname(src_path), exist_ok=True)
            shutil.copy2(tgt_path, src_path)
            print(f"Copiado: {tgt_path} -> {src_path}")
        elif tgt_time > source_files[src_path]:
            # El archivo en target es más reciente, sobrescribirlo
            shutil.copy2(tgt_path, src_path)
            print(f"Actualizado: {tgt_path} -> {src_path}")

def main():
    # Configurar las rutas de las carpetas
    source_folder = r"D:\descargas\uno"  # Cambiar por la ruta de la primera carpeta
    target_folder = r"C:\Users\swild\OneDrive\Desktop\Nueva carpeta (3)"  # Cambiar por la ruta de la segunda carpeta
    
    # Verificar que las carpetas existan
    if not os.path.exists(source_folder):
        print(f"Error: La carpeta {source_folder} no existe.")
        return
    if not os.path.exists(target_folder):
        print(f"Error: La carpeta {target_folder} no existe.")
        return
    
    # Ejecutar sincronización
    try:
        sync_folders(source_folder, target_folder)
        print("Sincronización completada.")
    except Exception as e:
        print(f"Error durante la sincronización: {e}")

if __name__ == "__main__":
    main()