import re
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from PIL import Image as PILImage  # Para obtener dimensiones reales de la imagen

def extraer_imagenes(texto, carpeta_imagenes):
    """
    Busca todas las marcas de imagen en el texto (entre (( y )))
    y las elimina. Devuelve una tupla (texto_limpio, imagenes) donde
    imagenes es un diccionario con la clave (nombre de archivo) y la ruta completa.
    """
    imagenes = {}
    for match in re.findall(r'\(\((.*?)\)\)', texto):
        ruta_imagen = carpeta_imagenes / match
        if ruta_imagen.exists():
            imagenes[match] = str(ruta_imagen)
        texto = texto.replace(f'(({match}))', '', 1)
    return texto, imagenes

def get_scaled_dimensions(ruta_imagen, max_width):
    """
    Dada la ruta de la imagen y el ancho máximo permitido, se
    obtienen las dimensiones originales y se calcula el escalado
    proporcional para que el ancho no supere el valor max_width.
    Devuelve una tupla (nuevo_ancho, nuevo_alto).
    """
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

def parsear_encabezado(archivo):
    """
    Lee el archivo de encabezado y extrae el texto y las imágenes.
    Se asume que el contenido del encabezado puede tener marcas del tipo ((nombre_imagen.ext))
    y se buscan dichas imágenes en la carpeta "archivos".
    """
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
    """Lee el archivo y devuelve una lista de conjuntos de preguntas."""
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
            
            pregunta = {}
            lineas = [l.strip() for l in bloque.split('\n') if l.strip()]
            if len(lineas) < 2:
                continue
            
            pregunta['numero'] = pregunta_contador
            pregunta_contador += 1
            
            enunciado, imagenes_pregunta = extraer_imagenes(lineas[0], carpeta_imagenes)
            pregunta['pregunta'] = enunciado
            pregunta['imagenes'] = imagenes_pregunta
            
            pregunta['opciones'] = {}
            for linea in lineas[1:-1]:
                if re.match(r'^[A-D]\)', linea):
                    opcion_texto, imagenes_opcion = extraer_imagenes(linea, carpeta_imagenes)
                    if ')' in opcion_texto:
                        letra, texto = opcion_texto.split(')', 1)
                        pregunta['opciones'][letra.strip()] = {
                            'texto': texto.strip(),
                            'imagenes': imagenes_opcion
                        }
            respuesta_linea = lineas[-1]
            if respuesta_linea.startswith('RESPUESTA:'):
                pregunta['respuesta'] = respuesta_linea.split(':', 1)[1].strip()
            
            preguntas.append(pregunta)
        
        conjuntos.append({
            'introduccion': introduccion,
            'imagenes': imagenes_introduccion,
            'preguntas': preguntas
        })
    
    return conjuntos

def generar_pdf(conjuntos, header_info, archivo_salida, archivo_fondo, alpha_fondo=0.3):
    """Genera un PDF con múltiples conjuntos de preguntas en dos columnas,
    incluyendo un encabezado (cargado desde un archivo de texto con imágenes),
    números de página en el pie y una imagen de fondo con transparencia en cada página.
    
    Parámetros:
      - archivo_fondo: ruta de la imagen que se usará de fondo.
      - alpha_fondo: nivel de opacidad para la imagen de fondo (0: transparente, 1: opaco).
    """
    c = canvas.Canvas(archivo_salida, pagesize=letter)
    ancho, alto = letter
    estilos = getSampleStyleSheet()
    
    # Márgenes y configuración de columnas
    margen_x = 50
    margen_y = 50  # margen inferior
    espacio_columnas = 20
    ancho_columna = (ancho - 2 * margen_x - espacio_columnas) / 2

    # Estilos para textos
    estilo_encabezado = ParagraphStyle('Encabezado',
                                       parent=estilos['Heading2'],
                                       fontSize=14,
                                       leading=16)
    estilo_intro = ParagraphStyle('Introduccion',
                                  parent=estilos['BodyText'],
                                  fontSize=12,
                                  leading=14,
                                  spaceAfter=12)
    estilo_pregunta = ParagraphStyle('Pregunta',
                                     parent=estilos['BodyText'],
                                     fontName='Helvetica-Bold',
                                     fontSize=12,
                                     spaceAfter=6)
    estilo_opciones = ParagraphStyle('Opciones',
                                     parent=estilos['BodyText'],
                                     fontSize=10,
                                     leftIndent=12,
                                     spaceAfter=3)
    
    espacio_imagen = 10  # espacio después de cada imagen

    y_position = None  
    page_number = 1

    def draw_background(c, fondo_path, ancho, alto, alpha):
        """Dibuja la imagen de fondo con transparencia en la página completa."""
        if fondo_path and Path(fondo_path).exists():
            c.saveState()
            # Establece la transparencia para el relleno (alpha: 0 transparente, 1 opaco)
            c.setFillAlpha(alpha)
            c.drawImage(fondo_path, 0, 0, width=ancho, height=alto)
            c.restoreState()

    def draw_header(c, header_info, ancho, alto, margen_x):
        """
        Dibuja el encabezado en la parte superior de la página usando el contenido
        e imágenes definidos en header_info. Devuelve la altura total ocupada.
        """
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
        """Dibuja el número de página en el pie de la página."""
        c.setFont("Helvetica", 10)
        footer_text = f"Página {page_num}"
        c.drawRightString(ancho - margen_x, margen_y / 2, footer_text)

    def new_page():
        """Dibuja el pie de página, salta a una nueva página,
        dibuja la imagen de fondo (con transparencia), el encabezado y reposiciona el contenido.
        """
        nonlocal page_number, y_position
        draw_footer(c, ancho, margen_x, margen_y, page_number)
        c.showPage()
        page_number += 1
        draw_background(c, archivo_fondo, ancho, alto, alpha_fondo)
        header_height = draw_header(c, header_info, ancho, alto, margen_x)
        y_position = alto - margen_y - header_height - 10

    # Primera página: dibujar fondo, encabezado y definir posición de inicio del contenido
    draw_background(c, archivo_fondo, ancho, alto, alpha_fondo)
    header_height = draw_header(c, header_info, ancho, alto, margen_x)
    y_position = alto - margen_y - header_height - 10

    # --- Dibujo de la introducción y sus imágenes ---
    for conjunto in conjuntos:
        introduccion = conjunto['introduccion']
        imagenes_introduccion = conjunto['imagenes']
        preguntas = conjunto['preguntas']
        
        if introduccion:
            p_intro = Paragraph(introduccion, estilo_intro)
            ancho_wrap, alto_wrap = p_intro.wrap(ancho - 2 * margen_x, alto)
            if y_position - alto_wrap < margen_y:
                new_page()
            p_intro.drawOn(c, margen_x, y_position - alto_wrap)
            y_position -= alto_wrap + 10
            
            for nombre, ruta in imagenes_introduccion.items():
                max_width_intro = ancho - 2 * margen_x
                new_width, new_height = get_scaled_dimensions(ruta, max_width_intro)
                if y_position - new_height < margen_y:
                    new_page()
                c.drawImage(ruta, margen_x, y_position - new_height, width=new_width, height=new_height)
                y_position -= new_height + espacio_imagen
            
            y_position -= 30
        
        # --- Dibujar las preguntas en dos columnas ---
        for i in range(0, len(preguntas), 2):
            preguntas_par = preguntas[i:i+2]
            alturas = []
            
            for pregunta in preguntas_par:
                altura_total = 0
                texto_pregunta = f"{pregunta['numero']}. {pregunta['pregunta']}"
                p_enunciado = Paragraph(texto_pregunta, estilo_pregunta)
                p_enunciado.wrap(ancho_columna, alto)
                altura_total += p_enunciado.height
                
                for letra, datos_opcion in pregunta['opciones'].items():
                    texto_opcion = f"{letra}) {datos_opcion['texto']}"
                    p_opcion = Paragraph(texto_opcion, estilo_opciones)
                    p_opcion.wrap(ancho_columna - 20, alto)
                    altura_opcion = p_opcion.height + 3
                    if datos_opcion['imagenes']:
                        for nom_img, ruta in datos_opcion['imagenes'].items():
                            _, new_height = get_scaled_dimensions(ruta, ancho_columna - 20)
                            altura_opcion += new_height + espacio_imagen
                    altura_total += altura_opcion
                
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
                texto_pregunta = f"{pregunta['numero']}. {pregunta['pregunta']}"
                p_enunciado = Paragraph(texto_pregunta, estilo_pregunta)
                p_enunciado.wrap(ancho_columna, alto)
                p_enunciado.drawOn(c, x, y_position - p_enunciado.height)
                current_y = y_position - p_enunciado.height - 5
                
                for letra, datos_opcion in pregunta['opciones'].items():
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

    draw_footer(c, ancho, margen_x, margen_y, page_number)
    c.save()

# Archivos de entrada y salida
archivo_preguntas = "preguntas.txt"
archivo_encabezado = "encabezado.txt"   # Encabezado (texto e imágenes)
archivo_fondo = "fondo.jpg"             # Imagen de fondo para cada página
archivo_salida = "preguntas.pdf"

# Procesar encabezado y preguntas, y generar el PDF
header_info = parsear_encabezado(archivo_encabezado)
conjuntos = parsear_preguntas(archivo_preguntas)
generar_pdf(conjuntos, header_info, archivo_salida, archivo_fondo, alpha_fondo=0.04)
