import re
import random
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from PIL import Image as PILImage  # Para obtener dimensiones reales de la imagen

# ---------------------------
# FUNCIONES DE UTILIDAD
# ---------------------------

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
    Dada la ruta de la imagen y el ancho máximo permitido, obtiene sus dimensiones
    y calcula el escalado proporcional para que el ancho no supere max_width.
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

# ---------------------------
# PARSERS DE ARCHIVOS
# ---------------------------

def parsear_encabezado(archivo):
    """
    Lee el archivo de encabezado y extrae su contenido y las imágenes (buscándolas en "archivos").
    Se espera que el archivo pueda contener marcas de imagen del tipo ((nombre_imagen.ext)).
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
    """
    Lee el archivo de preguntas y devuelve una lista de "conjuntos" de preguntas.
    Cada conjunto puede tener una introducción y un grupo de preguntas.
    Cada pregunta es un diccionario que puede contener:
      - 'numero': número (se asigna posteriormente)
      - 'pregunta': enunciado sin marcas de imagen
      - 'imagenes': imágenes extraídas del enunciado
      - 'opciones': diccionario con las opciones (cada opción es un diccionario con 'texto' e 'imagenes')
      - 'respuesta': la respuesta correcta (obtenida de la línea "RESPUESTA:")
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {archivo} no existe")
        return []
    
    carpeta_imagenes = Path("archivos")
    # Separamos el contenido por "INTRODUCCION:" (ignorando mayúsculas)
    conjuntos_raw = re.split(r'INTRODUCCION:', contenido, flags=re.IGNORECASE)
    conjuntos = []
    pregunta_contador = 1

    for conjunto in conjuntos_raw[1:]:
        # Se asume que la parte de preguntas comienza con "PREGUNTA 1"
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

# ---------------------------
# GENERACIÓN DEL PDF (VARIANTE)
# ---------------------------

def generar_pdf_aleatorio(lista_preguntas, header_info, archivo_salida, archivo_fondo, alpha_fondo=0.3):
    """
    Genera un PDF en el que el orden de las preguntas se mezcla aleatoriamente.
    Al final del documento se incluye una página que lista las respuestas correctas
    de las preguntas en el orden aleatorio.
    
    Parámetros:
      - lista_preguntas: lista de diccionarios de preguntas (cada una con 'pregunta', 'opciones', 'respuesta', etc.)
      - header_info: diccionario con información del encabezado (texto e imágenes)
      - archivo_fondo: ruta de la imagen de fondo para cada página
      - alpha_fondo: nivel de opacidad para la imagen de fondo (0: transparente, 1: opaco)
    """
    c = canvas.Canvas(archivo_salida, pagesize=letter)
    ancho, alto = letter
    estilos = getSampleStyleSheet()
    
    # Márgenes y columnas
    margen_x = 50
    margen_y = 50   # margen inferior
    espacio_columnas = 20
    ancho_columna = (ancho - 2 * margen_x - espacio_columnas) / 2

    # Estilos
    estilo_encabezado = ParagraphStyle('Encabezado',
                                       parent=estilos['Heading2'],
                                       fontSize=14,
                                       leading=16)
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
    estilo_respuestas = ParagraphStyle('Respuestas',
                                       parent=estilos['BodyText'],
                                       fontSize=10,
                                       leading=14)
    
    espacio_imagen = 10  # espacio entre imágenes
    
    # Variable de control de página
    y_position = None  
    page_number = 1

    def draw_background(c, fondo_path, ancho, alto, alpha):
        """Dibuja la imagen de fondo (con transparencia) ocupando toda la página."""
        if fondo_path and Path(fondo_path).exists():
            c.saveState()
            c.setFillAlpha(alpha)
            c.drawImage(fondo_path, 0, 0, width=ancho, height=alto)
            c.restoreState()

    def draw_header(c, header_info, ancho, alto, margen_x):
        """Dibuja el encabezado (texto e imágenes) en la parte superior y devuelve la altura ocupada."""
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
        """Dibuja el número de página en el pie."""
        c.setFont("Helvetica", 10)
        footer_text = f"Página {page_num}"
        c.drawRightString(ancho - margen_x, margen_y / 2, footer_text)

    def new_page():
        """Dibuja el pie, salta a nueva página y vuelve a dibujar fondo y encabezado."""
        nonlocal page_number, y_position
        draw_footer(c, ancho, margen_x, margen_y, page_number)
        c.showPage()
        page_number += 1
        draw_background(c, archivo_fondo, ancho, alto, alpha_fondo)
        header_height = draw_header(c, header_info, ancho, alto, margen_x)
        y_position = alto - margen_y - header_height - 10

    # Primera página: fondo, encabezado y posición inicial del contenido
    draw_background(c, archivo_fondo, ancho, alto, alpha_fondo)
    header_height = draw_header(c, header_info, ancho, alto, margen_x)
    y_position = alto - margen_y - header_height - 10

    # Dibujar las preguntas en dos columnas (dos por renglón)
    for i in range(0, len(lista_preguntas), 2):
        preguntas_par = lista_preguntas[i:i+2]
        alturas = []
        for pregunta in preguntas_par:
            altura_total = 0
            texto_preg = f"{pregunta['numero']}. {pregunta['pregunta']}"
            p_enunciado = Paragraph(texto_preg, estilo_pregunta)
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
            texto_preg = f"{pregunta['numero']}. {pregunta['pregunta']}"
            p_enunciado = Paragraph(texto_preg, estilo_pregunta)
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

    # Agregar una página con la lista de respuestas correctas (en el orden aleatorio)
    new_page()
    titulo_respuestas = Paragraph("Lista de Respuestas Correctas", estilo_encabezado)
    w, h = titulo_respuestas.wrap(ancho - 2 * margen_x, alto)
    titulo_respuestas.drawOn(c, margen_x, y_position - h)
    y_position -= h + 10

    for pregunta in lista_preguntas:
        linea = f"{pregunta['numero']}. {pregunta.get('respuesta', 'Sin respuesta')}"
        p_linea = Paragraph(linea, estilo_respuestas)
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

# Rutas de archivos
archivo_preguntas = "preguntas.txt"
archivo_encabezado = "encabezado.txt"   # Encabezado (texto e imágenes)
archivo_fondo = "fondo.jpg"             # Imagen de fondo para cada página

# Número de variantes (PDFs) a generar
N_VARIANTES = 3

# Procesar encabezado y preguntas
conjuntos = parsear_preguntas(archivo_preguntas)
header_info = parsear_encabezado(archivo_encabezado)

# Combinar todas las preguntas de todos los conjuntos en una lista única
todas_preguntas = []
for conjunto in conjuntos:
    todas_preguntas.extend(conjunto['preguntas'])

# Generar cada variante (PDF)
for i in range(1, N_VARIANTES+1):
    # Se hace una copia de la lista completa y se mezcla de forma aleatoria
    preguntas_variant = todas_preguntas.copy()
    random.shuffle(preguntas_variant)
    # Reasignar la numeración según el nuevo orden
    for idx, pregunta in enumerate(preguntas_variant, start=1):
        pregunta['numero'] = idx
    salida = f"preguntas_variant_{i}.pdf"
    generar_pdf_aleatorio(preguntas_variant, header_info, salida, archivo_fondo, alpha_fondo=0.3)
    print(f"PDF generado: {salida}")
