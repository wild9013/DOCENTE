import re
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

def parsear_preguntas(archivo):
    """Lee el archivo y devuelve introducción y preguntas (igual que antes)"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no existe")
        return "", []

    partes = re.split(r'\nPREGUNTA 1\n', contenido, flags=re.IGNORECASE)
    introduccion = partes[0].replace('INTRODUCCION:\n', '').strip()
    
    bloques_preguntas = re.split(r'\nPREGUNTA \d+\n', partes[1])
    preguntas = []
    
    for bloque in bloques_preguntas:
        if not bloque.strip():
            continue
            
        pregunta = {}
        lineas = [l.strip() for l in bloque.split('\n') if l.strip()]
        
        if len(lineas) < 2:
            continue
        
        pregunta['pregunta'] = lineas[0]
        pregunta['opciones'] = {}
        
        for linea in lineas[1:-1]:
            if re.match(r'^[A-D]\)', linea):
                letra, texto = linea.split(')', 1)
                pregunta['opciones'][letra.strip()] = texto.strip()
        
        respuesta_linea = lineas[-1]
        if respuesta_linea.startswith('RESPUESTA:'):
            pregunta['respuesta'] = respuesta_linea.split(':')[1].strip()
        
        preguntas.append(pregunta)
    
    introduccion = introduccion.replace('\n', '<br/>')
    return introduccion, preguntas

def generar_pdf(introduccion, preguntas, archivo_salida):
    """Genera PDF con preguntas en dos columnas"""
    c = canvas.Canvas(archivo_salida, pagesize=letter)
    ancho, alto = letter
    estilos = getSampleStyleSheet()
    
    # Configuración de diseño
    margen_x = 50
    margen_y = 50
    espacio_columnas = 20
    ancho_columna = (ancho - 2*margen_x - espacio_columnas) / 2
    y_position = alto - margen_y

    # Estilos
    estilo_intro = ParagraphStyle(
        'Introduccion', parent=estilos['BodyText'],
        fontSize=12, leading=14, spaceAfter=12
    )
    
    estilo_pregunta = ParagraphStyle(
        'Pregunta', parent=estilos['BodyText'],
        fontName='Helvetica-Bold', fontSize=12, spaceAfter=6
    )
    
    estilo_opciones = ParagraphStyle(
        'Opciones', parent=estilos['BodyText'],
        fontSize=10, leftIndent=12, spaceAfter=3
    )

    # Dibujar introducción
    if introduccion:
        parrafos = introduccion.split('<br/><br/>')
        for parrafo in parrafos:
            p = Paragraph(parrafo.replace('<br/>', '<br/>'), estilo_intro)
            ancho_wrap, alto_wrap = p.wrap(ancho - 2*margen_x, alto)
            
            if y_position - alto_wrap < margen_y:
                c.showPage()
                y_position = alto - margen_y
                
            p.drawOn(c, margen_x, y_position - alto_wrap)
            y_position -= alto_wrap + 10
        
        y_position -= 30  # Espacio después de la introducción

    # Dibujar preguntas en dos columnas
    for i in range(0, len(preguntas), 2):
        preguntas_par = preguntas[i:i+2]
        alturas = []
        
        # Calcular alturas
        for j, pregunta in enumerate(preguntas_par):
            texto = f"{i+j+1}. {pregunta['pregunta']}"
            p = Paragraph(texto, estilo_pregunta)
            p.wrap(ancho_columna, alto)
            altura = p.height
            
            for letra, texto_opcion in pregunta['opciones'].items():
                opcion = Paragraph(f"{letra}) {texto_opcion}", estilo_opciones)
                opcion.wrap(ancho_columna - 20, alto)
                altura += opcion.height + 3
            
            alturas.append(altura + 10)  # Margen inferior
        
        altura_max = max(alturas) if alturas else 0
        
        # Cambio de página si es necesario
        if y_position - altura_max < margen_y:
            c.showPage()
            y_position = alto - margen_y
        
        # Dibujar par de preguntas
        for j, pregunta in enumerate(preguntas_par):
            x = margen_x + j*(ancho_columna + espacio_columnas)
            texto = f"{i+j+1}. {pregunta['pregunta']}"
            p = Paragraph(texto, estilo_pregunta)
            p.wrap(ancho_columna, alto)
            p.drawOn(c, x, y_position - p.height)
            current_y = y_position - p.height - 5
            
            for letra, texto_opcion in pregunta['opciones'].items():
                opcion = Paragraph(f"{letra}) {texto_opcion}", estilo_opciones)
                opcion.wrap(ancho_columna - 20, alto)
                opcion.drawOn(c, x + 12, current_y - opcion.height)
                current_y -= opcion.height + 3
        
        y_position -= altura_max + 15

    # Hoja de respuestas (igual que antes)
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(ancho/2, alto - 50, "Clave de Respuestas")
    
    c.setFont("Helvetica", 12)
    y_pos = alto - 100
    for i, pregunta in enumerate(preguntas):
        c.drawString(100, y_pos, f"{i+1}. {pregunta['respuesta']}")
        y_pos -= 25
        if y_pos < 100:
            c.showPage()
            y_pos = alto - 50
    
    c.save()

if __name__ == "__main__":
    archivo_preguntas = "preguntas.txt"
    archivo_examen = "examen.pdf"
    
    introduccion, preguntas = parsear_preguntas(archivo_preguntas)
    
    if preguntas:
        generar_pdf(introduccion, preguntas, archivo_examen)
        print(f"Examen generado en: {Path(archivo_examen).resolve()}")
    else:
        print("No se encontraron preguntas válidas")