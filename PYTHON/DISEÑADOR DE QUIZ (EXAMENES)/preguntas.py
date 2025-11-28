# import re
import random
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from PIL import Image as PILImage

# ---------------------------
# FUNCIONES DE UTILIDAD
# ---------------------------
def extraer_imagenes(texto, carpeta_imagenes):
    imagenes = {}
    for match in re.findall(r'\(\((.*?)\)\)', texto):
        ruta_imagen = carpeta_imagenes / match
        if ruta_imagen.exists():
            imagenes[match] = str(ruta_imagen)
        texto = texto.replace(f'(({match}))', '', 1)
    return texto, imagenes

def get_scaled_dimensions(ruta_imagen, max_width):
    try:
        with PILImage.open(ruta_imagen) as img:
            orig_width, orig_height = img.size
    except Exception as e:
        return max_width, max_width * 0.75
    if orig_width > max_width:
        scale = max_width / orig_width
        return max_width, orig_height * scale
    else:
        return orig_width, orig_height

# ---------------------------
# PARSERS DE ARCHIVOS (CORREGIDO)
# ---------------------------
def parsear_encabezado(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no existe")
        return {"texto": "", "imagenes": {}}
    
    carpeta_imagenes = Path("archivos")
    contenido = contenido.strip().replace('\n', '<br/>')
    contenido, imagenes = extraer_imagenes(contenido, carpeta_imagenes)
    return {"texto": contenido, "imagenes": imagenes}

def parsear_preguntas(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no existe")
        return []
    
    carpeta_imagenes = Path("archivos")
    conjuntos_raw = re.split(r'INTRODUCCION:', contenido, flags=re.IGNORECASE)
    conjuntos = []
    pregunta_contador = 1

    for conjunto in conjuntos_raw[1:]:
        partes = re.split(r'\nPREGUNTA 1\n', conjunto, flags=re.IGNORECASE)
        if len(partes) < 2:
            continue
        
        introduccion = partes[0].strip().replace('\n', '<br/>')
        introduccion, imagenes_introduccion = extraer_imagenes(introduccion, carpeta_imagenes)
        bloques_preguntas = re.split(r'\nPREGUNTA \d+\n', partes[1])
        
        preguntas = []
        for bloque in bloques_preguntas:
            if not bloque.strip():
                continue
                
            # Procesamiento multilínea
            lineas = [l.rstrip() for l in bloque.split('\n') if l.strip()]
            if len(lineas) < 2:
                continue

            enunciado_lines = []
            opciones_lines = []
            respuesta_line = None
            en_opciones = False

            for linea in lineas:
                if re.match(r'^[A-D]\)', linea):
                    en_opciones = True
                    opciones_lines.append(linea)
                elif linea.startswith("RESPUESTA:"):
                    respuesta_line = linea
                else:
                    if en_opciones:
                        opciones_lines[-1] += '\n' + linea
                    else:
                        enunciado_lines.append(linea)

            # Construir pregunta
            enunciado = '<br/>'.join(enunciado_lines)
            enunciado, imagenes_pregunta = extraer_imagenes(enunciado, carpeta_imagenes)
            
            pregunta = {
                'numero': pregunta_contador,
                'pregunta': enunciado,
                'imagenes': imagenes_pregunta,
                'opciones': {},
                'correcta': None
            }
            pregunta_contador += 1

            # Procesar opciones
            for linea in opciones_lines:
                tiene_marcador = '((x))' in linea
                opcion_texto, imagenes_opcion = extraer_imagenes(linea, carpeta_imagenes)
                if tiene_marcador:
                    opcion_texto = opcion_texto.replace('((x))', '')
                
                if ')' in opcion_texto:
                    letra, texto = opcion_texto.split(')', 1)
                    letra = letra.strip()
                    texto = texto.strip().replace('\n', '<br/>')
                    
                    if tiene_marcador:
                        pregunta['correcta'] = letra
                    pregunta['opciones'][letra] = {
                        'texto': texto,
                        'imagenes': imagenes_opcion
                    }

            # Procesar respuesta final
            if not pregunta['correcta'] and respuesta_line:
                respuesta = respuesta_line.split(":", 1)[1].strip()
                pregunta['correcta'] = respuesta
                
            preguntas.append(pregunta)
            
        conjuntos.append({
            'introduccion': introduccion,
            'imagenes': imagenes_introduccion,
            'preguntas': preguntas
        })
        
    return conjuntos

# ---------------------------
# GENERACIÓN DEL PDF (ACTUALIZADO)
# ---------------------------
def generar_pdf(conjuntos, header_info, archivo_salida, archivo_fondo, alpha_fondo=0.3):
    c = canvas.Canvas(archivo_salida, pagesize=letter)
    ancho, alto = letter
    estilos = getSampleStyleSheet()
    
    margen_x = 50
    margen_y = 50
    espacio_columnas = 20
    ancho_columna = (ancho - 2 * margen_x - espacio_columnas) / 2

    estilo_encabezado = ParagraphStyle('Encabezado', parent=estilos['Heading2'], fontSize=14, leading=16)
    estilo_intro = ParagraphStyle('Introduccion', parent=estilos['BodyText'], fontSize=12, leading=14, spaceAfter=12)
    estilo_pregunta = ParagraphStyle('Pregunta', parent=estilos['BodyText'], fontName='Helvetica-Bold', fontSize=12, spaceAfter=6)
    estilo_opciones = ParagraphStyle('Opciones', parent=estilos['BodyText'], fontSize=10, leftIndent=12, spaceAfter=3)
    estilo_respuestas = ParagraphStyle('Respuestas', parent=estilos['BodyText'], fontSize=10, leading=14)
    
    espacio_imagen = 10
    y_position = None
    page_number = 1

    def draw_background(c, fondo_path, ancho, alto, alpha):
        if fondo_path and Path(fondo_path).exists():
            c.saveState()
            c.setFillAlpha(alpha)
            c.drawImage(fondo_path, 0, 0, width=ancho, height=alto)
            c.restoreState()

    def draw_header(c, header_info, ancho, alto, margen_x):
        y = alto - margen_y
        total_height = 0
        p_header = Paragraph(header_info['texto'], estilo_encabezado)
        w, h = p_header.wrap(ancho - 2 * margen_x, alto)
        p_header.drawOn(c, margen_x, y - h)
        total_height += h
        y -= h + 5
        for nom_img, ruta in header_info['imagenes'].items():
            new_width, new_height = get_scaled_dimensions(ruta, ancho - 2 * margen_x)
            if y - new_height < margen_y:
                break
            c.drawImage(ruta, margen_x, y - new_height, width=new_width, height=new_height)
            total_height += new_height + 5
            y -= new_height + 5
        return total_height

    def draw_footer(c, ancho, margen_x, margen_y, page_num):
        c.setFont("Helvetica", 10)
        footer_text = f"Página {page_num}"
        c.drawRightString(ancho - margen_x, margen_y / 2, footer_text)

    def new_page():
        nonlocal page_number, y_position
        draw_footer(c, ancho, margen_x, margen_y, page_number)
        c.showPage()
        page_number += 1
        draw_background(c, archivo_fondo, ancho, alto, alpha_fondo)
        header_height = draw_header(c, header_info, ancho, alto, margen_x)
        y_position = alto - margen_y - header_height - 10

    draw_background(c, archivo_fondo, ancho, alto, alpha_fondo)
    header_height = draw_header(c, header_info, ancho, alto, margen_x)
    y_position = alto - margen_y - header_height - 10

    for conjunto in conjuntos:
        introduccion = conjunto['introduccion']
        imagenes_introduccion = conjunto['imagenes']
        preguntas = conjunto['preguntas']
        
        if introduccion:
            p_intro = Paragraph(introduccion, estilo_intro)
            w, h = p_intro.wrap(ancho - 2 * margen_x, alto)
            if y_position - h < margen_y:
                new_page()
            p_intro.drawOn(c, margen_x, y_position - h)
            y_position -= h + 10
            
            for nombre, ruta in imagenes_introduccion.items():
                max_width = ancho - 2 * margen_x
                new_width, new_height = get_scaled_dimensions(ruta, max_width)
                if y_position - new_height < margen_y:
                    new_page()
                c.drawImage(ruta, margen_x, y_position - new_height, width=new_width, height=new_height)
                y_position -= new_height + espacio_imagen
            y_position -= 30
        
        for i in range(0, len(preguntas), 2):
            preguntas_par = preguntas[i:i+2]
            alturas = []
            for pregunta in preguntas_par:
                altura_total = 0
                texto_preg = f"{pregunta['numero']}. {pregunta['pregunta']}"
                p_enunciado = Paragraph(texto_preg, estilo_pregunta)
                p_enunciado.wrap(ancho_columna, alto)
                altura_total += p_enunciado.height
                
                if 'shuffled_opciones' not in pregunta:
                    opciones_originales = list(pregunta['opciones'].items())
                    random.shuffle(opciones_originales)
                    
                    nuevas_opciones = []
                    nueva_letra = 'A'
                    for opcion in opciones_originales:
                        nuevas_opciones.append((nueva_letra, opcion[1]))
                        nueva_letra = chr(ord(nueva_letra) + 1)
                    pregunta['shuffled_opciones'] = nuevas_opciones
                    
                    original_correcta = pregunta['correcta']
                    for idx, (letra_orig, datos) in enumerate(opciones_originales):
                        if letra_orig == original_correcta:
                            pregunta['correcta'] = chr(65 + idx)
                            break

                for letra, datos_opcion in pregunta['shuffled_opciones']:
                    texto_opcion = f"{letra}) {datos_opcion['texto']}"
                    p_opcion = Paragraph(texto_opcion, estilo_opciones)
                    p_opcion.wrap(ancho_columna - 20, alto)
                    altura_total += p_opcion.height + 3
                
                if 'imagenes' in pregunta and pregunta['imagenes']:
                    for nom_img, ruta in pregunta['imagenes'].items():
                        _, new_height = get_scaled_dimensions(ruta, ancho_columna)
                        altura_total += new_height + espacio_imagen
                alturas.append(altura_total + 10)
            
            altura_max = max(alturas) if alturas else 0
            if y_position - altura_max < margen_y:
                new_page()
            
            for j, pregunta in enumerate(preguntas_par):
                x = margen_x + j * (ancho_columna + espacio_columnas)
                texto_preg = f"{pregunta['numero']}. {pregunta['pregunta']}"
                p_enunciado = Paragraph(texto_preg, estilo_pregunta)
                p_enunciado.wrap(ancho_columna, alto)
                p_enunciado.drawOn(c, x, y_position - p_enunciado.height)
                current_y = y_position - p_enunciado.height - 5
                
                for letra, datos_opcion in pregunta['shuffled_opciones']:
                    texto_opcion = f"{letra}) {datos_opcion['texto']}"
                    p_opcion = Paragraph(texto_opcion, estilo_opciones)
                    p_opcion.wrap(ancho_columna - 20, alto)
                    p_opcion.drawOn(c, x + 12, current_y - p_opcion.height)
                    current_y -= p_opcion.height + 3
                    
                    if datos_opcion['imagenes']:
                        for nom_img, ruta in datos_opcion['imagenes'].items():
                            new_width, new_height = get_scaled_dimensions(ruta, ancho_columna - 20)
                            if current_y - new_height < margen_y:
                                new_page()
                                x = margen_x
                                current_y = alto - margen_y - header_height - 10 - new_height
                            c.drawImage(ruta, x + 12, current_y - new_height, width=new_width, height=new_height)
                            current_y -= new_height + espacio_imagen
                
                if 'imagenes' in pregunta and pregunta['imagenes']:
                    for nom_img, ruta in pregunta['imagenes'].items():
                        new_width, new_height = get_scaled_dimensions(ruta, ancho_columna)
                        if current_y - new_height < margen_y:
                            new_page()
                            x = margen_x
                            current_y = alto - margen_y - header_height - 10 - new_height
                        c.drawImage(ruta, x, current_y - new_height, width=new_width, height=new_height)
                        current_y -= new_height + espacio_imagen
            
            y_position -= altura_max + 15

    new_page()
    titulo_respuestas = Paragraph("Lista de Respuestas Correctas", estilo_encabezado)
    w, h = titulo_respuestas.wrap(ancho - 2 * margen_x, alto)
    titulo_respuestas.drawOn(c, margen_x, y_position - h)
    y_position -= h + 10

    for conjunto in conjuntos:
        for pregunta in conjunto['preguntas']:
            correcta = pregunta.get('correcta', 'Sin marcar')
            texto_correcto = next(
                (f"{letra}) {datos['texto']}" 
                 for letra, datos in pregunta['shuffled_opciones'] 
                 if letra == correcta),
                'Sin respuesta'
            )
            linea = f"{pregunta['numero']}. {texto_correcto}"
            p_linea = Paragraph(f"<b>{linea}</b>", estilo_respuestas)
            w, h = p_linea.wrap(ancho - 2 * margen_x, alto)
            if y_position - h < margen_y:
                new_page()
            p_linea.drawOn(c, margen_x, y_position - h)
            y_position -= h + 5

    draw_footer(c, ancho, margen_x, margen_y, page_number)
    c.save()

# ---------------------------
# PROGRAMA PRINCIPAL
# ---------------------------
archivo_preguntas = "preguntas.txt"
archivo_encabezado = "encabezado.txt"
archivo_fondo = "fondo.jpg"
archivo_salida = "preguntas.pdf"

header_info = parsear_encabezado(archivo_encabezado)
conjuntos = parsear_preguntas(archivo_preguntas)

generar_pdf(conjuntos, header_info, archivo_salida, archivo_fondo, alpha_fondo=0.04)
print(f"PDF generado: {archivo_salida}")