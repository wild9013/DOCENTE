import pandas as pd
from datetime import datetime
from docxtpl import DocxTemplate
import matplotlib.pyplot as plt
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
import io
import numpy as np

doc = DocxTemplate("plantilla.docx")

nombre="Wilder Salas Mena"
fecha = datetime.today().strftime("%d/%m/%Y")

constantes= {
    "nombre": nombre,
    "fecha": fecha
    }
print(constantes)

porcentajes = {
        "asistenciaP": "10%",
        "trasnP": "15%",
        "bonificacionP": "0%",
        "tallerP": "40%",
        "comportamientoP": "5%",
        "autoevaluacionP": "5%",
        "examenP": "25%",
}


# La URL debe estar entre comillas para que sea una cadena de texto válida
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7DifwDwqGwxZr79KAAqeihjNbEbT3YeNGaYJgNsS4FKPu_QUWEcj3Y3gY-9xTZrxvoVEnMt4aK2mw/pub?gid=271012679&single=true&output=csv"

# Leer el CSV desde la URL
df2 = pd.read_csv(url)

# Mostrar las primeras filas del DataFrame
# print(df2.head())


# Iterar sobre las filas del DataFrame
for indice, fila in df2.iterrows():
    contenido = {
        "nombre1": fila["Nombre Completo"],
        "nota1": fila["asistencia1"],
        "nota2": fila["trasn1"],
        "nota3": fila["bonificacion1"],
        "nota4": fila["taller1"],
        "nota5": fila["comportamiento1"],
        "nota6": fila["autoevaluacion1"],
        "nota7": fila["examen1"],
        "nota8": fila["DEFINITIVA"],
        "Observaciones": fila["Observaciones"]
    }
    contenido.update(constantes)
    contenido.update(porcentajes)

     # Verificar si la palabra "control" está en alguna de las columnas
    if fila.astype(str).str.contains('CONTROL', case=False).any():
        print(f"Palabra 'control' encontrada en la fila con índice {indice}. Deteniendo el ciclo.")
        break  # Detener el ciclo si se encuentra la palabra "control"

    # Crear el gráfico 
    notas = [
        fila["asistencia1"],
        fila["trasn1"],
        fila["bonificacion1"],
        fila["taller1"],
        fila["comportamiento1"],
        fila["autoevaluacion1"],
        fila["examen1"]
    ]

    # Convertir a flotantes y reemplazar valores NaN, espacios en blanco y comas por 0
    def convertir_a_float(valor):
        if pd.isna(valor) or valor == '':
            return 0
        valor_str = str(valor).replace(',', '.')
        try:
            return float(valor_str)
        except ValueError:
            return 0
    
    notas = [convertir_a_float(x) for x in notas]

    
    etiquetas = [
        "Asis", "Trans", "Boni", "Tall", "Comp", "Autoe", "Exa"
    ]
    
   # Crear el gráfico radial
    num_vars = len(etiquetas)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    notas = notas + [notas[0]]  # Añadir el primer valor al final para cerrar el círculo
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, notas, color='skyblue', alpha=0.4)
    ax.plot(angles, notas, color='blue', linewidth=2)

    # Añadir etiquetas en el gráfico radial
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(etiquetas)

    plt.title('Resultados del Estudiante')

    # Guardar el gráfico en un objeto BytesIO
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    plt.close()
    img_stream.seek(0)


    # Insertar el gráfico en el documento
    imagen = InlineImage(doc, img_stream, width=Inches(2.3))
    contenido["grafico"] = imagen

    # Renderizar y guardar el documento
    doc.render(contenido)
    doc.save(f"{fila['Nombre Completo']}_INFORME_.docx")

    print(contenido)