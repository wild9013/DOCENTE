import pandas as pd
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def seleccionar_archivo():
    """Abre un diálogo para seleccionar archivo Excel"""
    root = tk.Tk()
    root.withdraw()
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
    )
    return archivo

def leer_examen(archivo_excel):
    """Lee el archivo Excel con el formato especificado"""
    try:
        df = pd.read_excel(archivo_excel, header=None)
        
        # Extraer componentes
        nombres = df.iloc[2:, 0].tolist()
        resp_correctas = df.iloc[1, 1:21].tolist()
        resp_estudiantes = df.iloc[2:, 1:21]
        
        # Crear DataFrame
        df_estudiantes = pd.DataFrame(
            resp_estudiantes.values,
            index=nombres,
            columns=[f"P{i+1}" for i in range(20)]
        )
        
        return df_estudiantes, resp_correctas
    
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def analizar_preguntas(df, correctas):
    """Analiza el rendimiento por pregunta"""
    resultados = []
    
    for i in range(20):
        pregunta = f"P{i+1}"
        respuestas = df[pregunta].values
        correcta = correctas[i]
        
        # Contar respuestas
        conteo = Counter(respuestas)
        total = len(respuestas)
        aciertos = conteo.get(correcta, 0)
        porcentaje = (aciertos / total) * 100
        
        # Opciones de respuesta presentes
        opciones = sorted(conteo.keys())
        
        resultados.append({
            'pregunta': i+1,
            'correcta': correcta,
            'aciertos': aciertos,
            'porcentaje': porcentaje,
            'distribucion': conteo,
            'opciones': opciones
        })
    
    return resultados

def graficar_resultados(resultados):
    """Genera gráficos de análisis por pregunta"""
    plt.style.use('ggplot')
    
    # Gráfico 1: Porcentaje de aciertos por pregunta
    plt.figure(figsize=(12, 6))
    preguntas = [r['pregunta'] for r in resultados]
    porcentajes = [r['porcentaje'] for r in resultados]
    
    bars = plt.bar(preguntas, porcentajes, color='skyblue')
    plt.axhline(y=50, color='red', linestyle='--', alpha=0.5)
    
    # Añadir etiquetas
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom')
    
    plt.title('Porcentaje de aciertos por pregunta')
    plt.xlabel('Número de pregunta')
    plt.ylabel('Porcentaje de aciertos')
    plt.xticks(preguntas)
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()
    
    # Gráfico 2: Distribución de respuestas para 4 preguntas ejemplo
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    preguntas_ejemplo = [0, 5, 10, 15]  # Preguntas 1, 6, 11, 16
    
    for i, idx in enumerate(preguntas_ejemplo):
        r = resultados[idx]
        ax = axs[i//2, i%2]
        
        labels = [str(op) for op in r['opciones']]
        sizes = [r['distribucion'].get(op, 0) for op in r['opciones']]
        explode = [0.1 if op == r['correcta'] else 0 for op in r['opciones']]
        
        ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
              shadow=True, startangle=90)
        ax.set_title(f'Pregunta {r["pregunta"]} (Correcta: {r["correcta"]})')
    
    plt.suptitle('Distribución de respuestas en preguntas seleccionadas')
    plt.tight_layout()
    plt.show()

def main():
    print("ANÁLISIS DE RESULTADOS DE EXAMEN")
    archivo = seleccionar_archivo()
    
    if not archivo:
        print("Operación cancelada")
        return
    
    df, correctas = leer_examen(archivo)
    
    if df is None:
        return
    
    # Análisis de resultados
    resultados = analizar_preguntas(df, correctas)
    
    # Mostrar resumen estadístico
    print("\nRESUMEN ESTADÍSTICO")
    print(f"Total estudiantes: {len(df)}")
    print(f"Pregunta más fácil: {max(resultados, key=lambda x: x['porcentaje'])['pregunta']}")
    print(f"Pregunta más difícil: {min(resultados, key=lambda x: x['porcentaje'])['pregunta']}")
    
    # Generar gráficos
    graficar_resultados(resultados)

if __name__ == "__main__":
    main()