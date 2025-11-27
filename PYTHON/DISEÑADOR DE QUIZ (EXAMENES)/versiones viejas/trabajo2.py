import re
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

def parsear_preguntas(archivo):
    """
    Lee un archivo de preguntas y devuelve una introducción y lista de preguntas
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no existe")
        return "", []

    # Dividir introducción y preguntas
    partes = re.split(r'\nPREGUNTA 1\n', contenido, flags=re.IGNORECASE)
    introduccion = partes[0].replace('INTRODUCCION:\n', '').strip()
    
    # Procesar preguntas
    bloques_preguntas = re.split(r'\nPREGUNTA \d+\n', partes[1])
    preguntas = []
    
    for bloque in bloques_preguntas:
        if not bloque.strip():
            continue
            
        pregunta = {}
        lineas = [l.strip() for l in bloque.split('\n') if l.strip()]
        
        if len(lineas) < 2:
            continue
        
        # Extraer elementos de la pregunta
        pregunta['pregunta'] = lineas[0]
        pregunta['opciones'] = {}
        
        for linea in lineas[1:-1]:
            if re.match(r'^[A-D]\)', linea):
                letra, texto = linea.split(')', 1)
                pregunta['opciones'][letra.strip()] = texto.strip()
        
        # Extraer respuesta
        respuesta_linea = lineas[-1]
        if respuesta_linea.startswith('RESPUESTA:'):
            pregunta['respuesta'] = respuesta_linea.split(':')[1].strip()
        
        preguntas.append(pregunta)
    
    # Conservar saltos de línea y párrafos
    introduccion = introduccion.replace('\n', '<br/>')
    return introduccion, preguntas

def generar_pdf(introduccion, preguntas, archivo_salida):
    """Genera un examen en PDF con introducción formateada"""
    c = canvas.Canvas(archivo_salida, pagesize=letter)
    ancho, alto = letter
    estilos = getSampleStyleSheet()
    
    # Configurar estilos
    estilo_intro = ParagraphStyle(
        'Introduccion',
        parent=estilos['BodyText'],
        fontSize=12,
        leading=14,
        spaceAfter=12,
        allowWidows=1,
        allowOrphans=0
    )
    
    estilo_pregunta = ParagraphStyle(
        'Pregunta',
        parent=estilos['BodyText'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=10
    )
    
    estilo_opciones = ParagraphStyle(
        'Opciones',
        parent=estilos['BodyText'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=5
    )
    
    margen_x = 50
    margen_y = 50
    y_position = alto - margen_y
    
    # Dibujar introducción con saltos de línea
    if introduccion:
        # Dividir en párrafos usando doble salto de línea
        parrafos = introduccion.split('<br/><br/>')
        for parrafo in parrafos:
            p = Paragraph(parrafo.replace('<br/>', '<br/>'), estilo_intro)
            ancho_wrap, alto_wrap = p.wrap(ancho - 2*margen_x, alto)
            
            if y_position - alto_wrap < margen_y:
                c.showPage()
                y_position = alto - margen_y
                
            p.drawOn(c, margen_x, y_position - alto_wrap)
            y_position -= alto_wrap + 15
        
        y_position -= 30  # Espacio después de la introducción
    
    # Dibujar preguntas
    for i, pregunta in enumerate(preguntas):
        texto_pregunta = f"{i+1}. {pregunta['pregunta']}"
        p_pregunta = Paragraph(texto_pregunta, estilo_pregunta)
        opciones = [Paragraph(f"{letra}) {texto}", estilo_opciones) 
                   for letra, texto in pregunta['opciones'].items()]
        
        # Calcular espacio necesario
        espacio_total = p_pregunta.wrap(ancho - 2*margen_x, alto)[1]
        espacio_total += sum(o.wrap(ancho - 2*margen_x, alto)[1] + 5 for o in opciones)
        
        # Manejar saltos de página
        if y_position - espacio_total < margen_y:
            c.showPage()
            y_position = alto - margen_y
        
        # Dibujar pregunta
        p_pregunta.drawOn(c, margen_x, y_position - p_pregunta.height)
        y_position -= p_pregunta.height + 10
        
        # Dibujar opciones
        for opcion in opciones:
            if y_position - opcion.height < margen_y:
                c.showPage()
                y_position = alto - margen_y
                
            opcion.drawOn(c, margen_x + 20, y_position - opcion.height)
            y_position -= opcion.height + 5
        
        y_position -= 15  # Espacio entre preguntas
    
    # Hoja de respuestas
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