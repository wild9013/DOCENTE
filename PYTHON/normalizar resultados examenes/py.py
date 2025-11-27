import pandas as pd
import numpy as np
from scipy.stats import norm
from fpdf import FPDF
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tempfile
import os

def normalizacion_lineal(notas):
    nota_min = notas.min()
    nota_max = notas.max()
    notas_normalizadas = 1 + ((notas - nota_min) / (nota_max - nota_min)) * 4
    return notas_normalizadas

def campana_gauss(notas):
    mu = np.mean(notas)
    sigma = np.std(notas)
    cdf_notas = norm.cdf(notas, mu, sigma)
    notas_normalizadas = 1 + 4 * (cdf_notas - min(cdf_notas)) / (max(cdf_notas) - min(cdf_notas))
    return notas_normalizadas

def guardar_grafica_gauss(notas):
    mu = np.mean(notas)
    sigma = np.std(notas)
    
    x = np.linspace(min(notas), max(notas), 100)
    y = norm.pdf(x, mu, sigma)

    plt.figure(figsize=(8, 5))
    plt.hist(notas, bins=10, density=True, alpha=0.6, color='skyblue', edgecolor='black', label='Datos')
    plt.plot(x, y, 'r--', label='Distribución Normal')
    plt.title('Distribución de Notas - Método Gauss')
    plt.xlabel('Notas')
    plt.ylabel('Densidad')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, bbox_inches='tight', dpi=300)
    plt.close()
    return temp_file.name

def generar_pdf(df, metodo, ruta_salida, imagen_grafica=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Título
    pdf.cell(200, 10, txt="Resultados de Normalización de Notas", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Método utilizado: {metodo}", ln=True, align="C")
    pdf.ln(10)
    
    # Columnas
    pdf.cell(60, 10, txt="Nombre", border=1, align="C")
    pdf.cell(40, 10, txt="Nota Inicial", border=1, align="C")
    pdf.cell(40, 10, txt="Nota Final (1-5)", border=1, align="C", ln=True)
    
    # Datos
    for index, row in df.iterrows():
        pdf.cell(60, 10, txt=str(row['nombre']), border=1)
        pdf.cell(40, 10, txt=f"{row['nota_inicial']:.2f}", border=1, align="C")
        pdf.cell(40, 10, txt=f"{row['nota_final']:.2f}", border=1, align="C", ln=True)

    # Agregar imagen de la gráfica si está disponible
    if imagen_grafica and os.path.exists(imagen_grafica):
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Distribución de Notas (Gráfica)", ln=True, align="C")
        image_width = 180  # mm
        x_pos = (210 - image_width) / 2  # centrar en A4
        pdf.image(imagen_grafica, x=x_pos, y=30, w=image_width)
        os.remove(imagen_grafica)  # eliminar imagen temporal

    pdf.output(ruta_salida)
    messagebox.showinfo("PDF Generado", f"📄 Archivo PDF guardado en:\n{ruta_salida}")

def seleccionar_metodo(df):
    def aplicar_metodo(opcion):
        imagen_grafica = None
        if opcion == "1":
            df['nota_final'] = normalizacion_lineal(df['nota_inicial'])
            metodo = "Normalización Lineal"
        else:
            df['nota_final'] = campana_gauss(df['nota_inicial'])
            metodo = "Campana de Gauss"
            imagen_grafica = guardar_grafica_gauss(df['nota_inicial'])

        # Guardar archivo PDF
        ruta_pdf = asksaveasfilename(
            title="Guardar archivo PDF",
            defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
            initialfile=f"notas_normalizadas_{metodo.lower().replace(' ', '_')}.pdf"
        )
        if ruta_pdf:
            generar_pdf(df, metodo, ruta_pdf, imagen_grafica)
        ventana.destroy()

    ventana = tk.Tk()
    ventana.title("Seleccionar Método de Normalización")
    ventana.geometry("400x200")
    
    tk.Label(ventana, text="Seleccione el método de normalización:", font=("Arial", 12)).pack(pady=20)
    
    tk.Button(ventana, text="Normalización Lineal (Escala directa)", width=40, command=lambda: aplicar_metodo("1")).pack(pady=5)
    tk.Button(ventana, text="Campana de Gauss (Distribución normal)", width=40, command=lambda: aplicar_metodo("2")).pack(pady=5)

    ventana.mainloop()

def main():
    root = tk.Tk()
    root.withdraw()

    archivo_excel = askopenfilename(
        title="Seleccione el archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )

    if not archivo_excel:
        messagebox.showerror("Error", "No se seleccionó ningún archivo.")
        return

    try:
        df = pd.read_excel(archivo_excel, engine='openpyxl')
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
        return

    if 'nombre' not in df.columns or 'nota_inicial' not in df.columns:
        messagebox.showerror("Error", "El archivo debe contener las columnas 'nombre' y 'nota_inicial'.")
        return

    seleccionar_metodo(df)

if __name__ == "__main__":
    main()
