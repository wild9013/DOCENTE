import re
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Image

def parsear_preguntas(archivo):
    """Lee el archivo y devuelve una lista de conjuntos de preguntas."""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no existe")
        return []
    
    conjuntos_raw = re.split(r'INTRODUCCION:', contenido, flags=re.IGNORECASE)
    conjuntos = []
    pregunta_contador = 1
    carpeta_imagenes = Path("archivos")
    
    for conjunto in conjuntos_raw[1:]:
        partes = re.split(r'\nPREGUNTA 1\n', conjunto, flags=re.IGNORECASE)
        if len(partes) < 2:
            continue
        
        introduccion = partes[0].strip().replace('\n', '<br/>')
        imagenes = {}
        
        for match in re.findall(r'\(\((.*?)\)\)', introduccion):
            ruta_imagen = carpeta_imagenes / match
            if ruta_imagen.exists():
                imagenes[match] = str(ruta_imagen)
            introduccion = introduccion.replace(f'(({match}))', '', 1)
        
        bloques_preguntas = re.split(r'\nPREGUNTA \d+\n', partes[1])
        preguntas = []
        
        for bloque in bloques_preguntas:
            if not bloque.strip():
                continue
            
            pregunta = {}
            lineas = [l.strip() for l in bloque.split('\n') if l.strip()]
            
            if len(lineas) < 2:
                continue
            
            pregunta['numero'] = pregunta_contador
            pregunta_contador += 1
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
        
        conjuntos.append({'introduccion': introduccion, 'imagenes': imagenes, 'preguntas': preguntas})
    
    return conjuntos

def generar_pdf(conjuntos, archivo_salida):
    """Genera un PDF con múltiples conjuntos de preguntas en dos columnas."""
    c = canvas.Canvas(archivo_salida, pagesize=letter)
    ancho, alto = letter
    estilos = getSampleStyleSheet()
    
    margen_x = 50
    margen_y = 50
    espacio_columnas = 20
    ancho_columna = (ancho - 2*margen_x - espacio_columnas) / 2
    y_position = alto - margen_y
    
    estilo_intro = ParagraphStyle('Introduccion', parent=estilos['BodyText'], fontSize=12, leading=14, spaceAfter=12)
    estilo_pregunta = ParagraphStyle('Pregunta', parent=estilos['BodyText'], fontName='Helvetica-Bold', fontSize=12, spaceAfter=6)
    estilo_opciones = ParagraphStyle('Opciones', parent=estilos['BodyText'], fontSize=10, leftIndent=12, spaceAfter=3)
    
    for conjunto in conjuntos:
        introduccion = conjunto['introduccion']
        imagenes = conjunto['imagenes']
        preguntas = conjunto['preguntas']
        
        if introduccion:
            p = Paragraph(introduccion.replace('<br/>', '<br/>'), estilo_intro)
            ancho_wrap, alto_wrap = p.wrap(ancho - 2*margen_x, alto)
            
            if y_position - alto_wrap < margen_y:
                c.showPage()
                y_position = alto - margen_y
            
            p.drawOn(c, margen_x, y_position - alto_wrap)
            y_position -= alto_wrap + 10
            
            for nombre, ruta in imagenes.items():
                c.drawImage(ruta, margen_x, y_position - 100, width=200, height=100)
                y_position -= 110
            
            y_position -= 30
        
        for i in range(0, len(preguntas), 2):
            preguntas_par = preguntas[i:i+2]
            alturas = []
            
            for pregunta in preguntas_par:
                texto = f"{pregunta['numero']}. {pregunta['pregunta']}"
                p = Paragraph(texto, estilo_pregunta)
                p.wrap(ancho_columna, alto)
                altura = p.height
                
                for letra, texto_opcion in pregunta['opciones'].items():
                    opcion = Paragraph(f"{letra}) {texto_opcion}", estilo_opciones)
                    opcion.wrap(ancho_columna - 20, alto)
                    altura += opcion.height + 3
                
                alturas.append(altura + 10)
            
            altura_max = max(alturas) if alturas else 0
            
            if y_position - altura_max < margen_y:
                c.showPage()
                y_position = alto - margen_y
            
            for j, pregunta in enumerate(preguntas_par):
                x = margen_x + j*(ancho_columna + espacio_columnas)
                texto = f"{pregunta['numero']}. {pregunta['pregunta']}"
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
    
    c.save()

archivo_preguntas = "preguntas.txt"
archivo_salida = "preguntas.pdf"
conjuntos = parsear_preguntas(archivo_preguntas)
generar_pdf(conjuntos, archivo_salida)