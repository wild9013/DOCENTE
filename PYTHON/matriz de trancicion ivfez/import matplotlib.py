import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

# --- 1. Importar Tkinter para la ventana de diálogo ---
import tkinter as tk
from tkinter import filedialog

# --- 2. Definir Nombres de Columnas ---
# !!! TODAVÍA DEBES EDITAR ESTOS NOMBRES
# Asegúrate de que coincidan con los nombres de las columnas en tu archivo
COLUMNA_INICIAL = 'Clasificacion_2014'
COLUMNA_FINAL = 'Clasificacion_2024'

# --- 3. Crear Ventana Gráfica para Seleccionar Archivo ---
print("Abriendo ventana para seleccionar archivo...")

# Configurar la ventana raíz de tkinter y ocultarla
root = tk.Tk()
root.withdraw()

# Mostrar la ventana de "Abrir archivo"
archivo_path = filedialog.askopenfilename(
    title="Selecciona tu archivo de datos (CSV o Excel)",
    filetypes=[
        ("Archivos de Excel", "*.xlsx *.xls"),
        ("Archivos CSV", "*.csv"),
        ("Todos los archivos", "*.*")
    ]
)

# Salir del script si el usuario presiona "Cancelar"
if not archivo_path:
    print("Operación cancelada. No se seleccionó ningún archivo.")
    exit()

print(f"Archivo seleccionado: {archivo_path}")

# --- 4. Cargar y Procesar los Datos (Auto-detección) ---
try:
    if archivo_path.endswith('.csv'):
        df = pd.read_csv(archivo_path)
    elif archivo_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(archivo_path)
    else:
        print(f"Error: Tipo de archivo no soportado: {archivo_path}")
        print("Por favor, selecciona un archivo .csv o .xlsx")
        exit()

except ImportError:
    print("\nERROR: Para leer archivos Excel (.xlsx), necesitas 'openpyxl'.")
    print("Por favor, instálalo con: pip install openpyxl")
    exit()
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    exit()

# --- 5. Calcular la Matriz de Transición ---
try:
    matrix = pd.crosstab(
        df[COLUMNA_INICIAL], 
        df[COLUMNA_FINAL],
        normalize='index'
    ) * 100
except KeyError:
    print("\n--- ERROR DE COLUMNA ---")
    print(f"No se encontraron las columnas: '{COLUMNA_INICIAL}' o '{COLUMNA_FINAL}' en tu archivo.")
    print("Por favor, abre el script de Python y edita esas variables al inicio.")
    print("Columnas disponibles en tu archivo:", df.columns.tolist())
    exit()


# --- 6. Asegurar Orden de Filas/Columnas ---
y_labels_order = ['A+', 'A', 'B', 'C', 'D']
x_labels_order = ['D', 'C', 'B', 'A', 'A+']
matrix = matrix.reindex(index=y_labels_order, columns=x_labels_order, fill_value=np.nan)

# --- 7. Crear Etiquetas Personalizadas ---
annot_labels = []
for row in matrix.itertuples(index=False):
    new_row = []
    for val in pd.Series(row): # Asegurarse de que sea una Serie de pandas
        if pd.isna(val):
            new_row.append('-')
        else:
            new_row.append(f'{val:.0f}%') 
    annot_labels.append(new_row)

# --- 8. Mapa de Color Personalizado ---
cmap_blues = plt.get_cmap('Blues', 256)
new_colors = cmap_blues(np.linspace(0, 1, 256))
new_colors[0, :] = np.array([1, 1, 1, 1])
custom_cmap = ListedColormap(new_colors)

# --- 9. Preparar Matriz para Gráfico (Corrección compatibilidad) ---
matrix_for_heatmap = matrix.fillna(0)

# --- 10. Generar el Gráfico ---
plt.figure(figsize=(10, 7))
ax = sns.heatmap(
    matrix_for_heatmap,
    annot=annot_labels,
    fmt='',                  
    cmap=custom_cmap,        
    xticklabels=x_labels_order,
    yticklabels=y_labels_order,
    linewidths=1.5,
    linecolor='white',
    cbar=True,
    cbar_kws={'label': '% dentro de la fila'},
    vmin=0,                  
    vmax=100,                
    annot_kws={"size": 12}
)

# --- 11. Títulos y Etiquetas ---
ax.set_title(f'Matriz de Transición ({COLUMNA_INICIAL} vs {COLUMNA_FINAL})', fontsize=16, pad=20)
ax.set_xlabel(COLUMNA_FINAL, fontsize=12)
ax.set_ylabel(COLUMNA_INICIAL, fontsize=12)

plt.tight_layout()
plt.savefig("matriz_transicion_auto.png")
plt.show()

print("¡Gráfico generado exitosamente desde el archivo seleccionado!")