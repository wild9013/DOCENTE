import pyperclip
import time
import datetime
import os
import json
from pathlib import Path

# Ruta para almacenar el historial del portapapeles
HISTORIAL_FILE = Path.home() / "portapapeles_historial.json"

def inicializar_historial():
    """Crea un archivo JSON vacío si no existe."""
    if not HISTORIAL_FILE.exists():
        with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def guardar_contenido_portapapeles(contenido):
    """Guarda el contenido del portapapeles con una marca de tiempo."""
    if not contenido:  # Ignora si está vacío
        return
    
    # Carga el historial existente
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        historial = []
    
    # Añade el nuevo contenido con timestamp
    entrada = {
        "timestamp": datetime.datetime.now().isoformat(),
        "contenido": contenido
    }
    historial.append(entrada)
    
    # Guarda el historial actualizado
    with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

def monitorear_portapapeles():
    """Monitorea el portapapeles y guarda cambios."""
    ultimo_contenido = None
    inicializar_historial()
    
    print("Monitoreando el portapapeles... Presiona Ctrl+C para detener.")
    while True:
        try:
            contenido = pyperclip.paste()
            if contenido != ultimo_contenido:
                guardar_contenido_portapapeles(contenido)
                ultimo_contenido = contenido
            time.sleep(1)  # Revisa cada segundo
        except KeyboardInterrupt:
            print("\nMonitoreo detenido.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

def leer_historial_ultimo_mes():
    """Lee y muestra el historial del portapapeles del último mes."""
    try:
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("No se encontró historial.")
        return
    
    # Fecha de hace un mes
    hace_un_mes = datetime.datetime.now() - datetime.timedelta(days=30)
    
    print("\nHistorial del portapapeles del último mes:")
    for entrada in historial:
        timestamp = datetime.datetime.fromisoformat(entrada["timestamp"])
        if timestamp >= hace_un_mes:
            print(f"[{timestamp}] {entrada['contenido'][:100]}{'...' if len(entrada['contenido']) > 100 else ''}")
        else:
            break  # Si las entradas están ordenadas, podemos salir

def main():
    print("1. Monitorear portapapeles (guardar contenido en tiempo real)")
    print("2. Ver historial del último mes")
    opcion = input("Selecciona una opción (1 o 2): ")
    
    if opcion == "1":
        monitorear_portapapeles()
    elif opcion == "2":
        leer_historial_ultimo_mes()
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    main()