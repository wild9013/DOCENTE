import re
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

def parsear_preguntas(archivo):
    """
    Lee un archivo de preguntas y devuelve una introducción y lista de preguntas
    Formato del archivo:
        INTRODUCCION:
        Texto de introducción...
        [Línea en blanco]
        PREGUNTA 1
        ¿Texto de la pregunta?
        A) Opción 1
        B) Opción 2
        C) Opción 3
        D) Opción 4
        RESPUESTA: A
        [Línea en blanco]
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no existe")
        return "", []

    bloques = re.split(r'\n\s*\n', contenido)
    introduccion = ""
    preguntas = []

    # Procesar introducción si existe
    if bloques and bloques[0].startswith('INTRODUCCION:'):
        intro_lines = bloques[0].split('\n')
        introduccion = '\n'.join([line.strip() for line in intro_lines[1:] if line.strip()])
        bloques = bloques[1:]

    # Procesar preguntas
    for bloque in bloques:
        if not bloque.strip():
            continue
            
        pregunta = {}
        lineas = [l.strip() for l in bloque.split('\n') if l.strip()]
        
        if len(lineas) < 3:  # Validación mínima de estructura
            continue
        
        # Extraer elementos
        pregunta['pregunta'] = lineas[1]
        pregunta['opciones'] = {}
        
        for linea in lineas[2:-1]:
            if linea.startswith(('A)', 'B)', 'C)', 'D)')):
                letra, texto = linea.split(')', 1)
                pregunta['opciones'][letra.strip()] = texto.strip()
        
        respuesta_linea = lineas[-1]
        if respuesta_linea.startswith('RESPUESTA:'):
            pregunta['respuesta'] = respuesta_linea.split(':')[1].strip()
        
        preguntas.append(pregunta)
    
    return introduccion, preguntas

def generar_pdf(introduccion, preguntas, archivo_salida):
    """Genera un examen en PDF con introducción, preguntas y respuestas"""
    c = canvas.Canvas(archivo_salida, pagesize=letter)
    ancho, alto = letter
    estilos = getSampleStyleSheet()
    
    # Estilos
    estilo_intro = ParagraphStyle(
        'Introduccion',
        parent=estilos['BodyText'],
        fontSize=12,
        leading=14,
        spaceAfter=20
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
    
    # Dibujar introducción
    if introduccion:
        p_intro = Paragraph(introduccion, estilo_intro)
        intro_w, intro_h = p_intro.wrap(ancho - 2*margen_x, alto)
        
        if y_position - intro_h < margen_y:
            c.showPage()
            y_position = alto - margen_y
            
        p_intro.drawOn(c, margen_x, y_position - intro_h)
        y_position -= intro_h + 30
    
    # Dibujar preguntas
    for i, pregunta in enumerate(preguntas):
        texto_pregunta = f"{i+1}. {pregunta['pregunta']}"
        p_pregunta = Paragraph(texto_pregunta, estilo_pregunta)
        opciones = [Paragraph(f"{letra}) {texto}", estilo_opciones) 
                   for letra, texto in pregunta['opciones'].items()]
        
        # Calcular espacio
        espacio_necesario = p_pregunta.wrap(ancho - 2*margen_x, alto)[1]
        espacio_necesario += sum(o.wrap(ancho - 2*margen_x, alto)[1] + 5 for o in opciones)
        
        # Cambio de página si es necesario
        if y_position - espacio_necesario < margen_y:
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
        
        y_position -= 20  # Espacio entre preguntas
    
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