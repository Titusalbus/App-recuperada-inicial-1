# ==========================================
# EXTRACTOR DE TEXTO RESALTADO DE PDF
# ==========================================

import streamlit as st
import pdfplumber
from pypdf import PdfReader
from docx import Document
import unicodedata

from .utils import obtener_mapa_capitulos
from .word_generator import (
    agregar_heading_toc,
    agregar_separador_pagina,
    agregar_texto_resaltado,
    guardar_documento_word
)


def extraer_caracteres_quads(quads, alto, all_chars):
    """Extrae caracteres usando QuadPoints (método preciso)"""
    valid_chars = []
    
    for q in range(0, len(quads), 8):
        if q + 7 >= len(quads):
            continue
        x1, y1, x2, y2, x3, y3, x4, y4 = [float(quads[q+j]) for j in range(8)]
        
        quad_top = alto - max(y1, y2)
        quad_bottom = alto - min(y3, y4)
        quad_left = min(x1, x4)
        quad_right = max(x2, x3)
        
        for char in all_chars:
            char_mid_y = (char['top'] + char['bottom']) / 2
            char_mid_x = (char['x0'] + char['x1']) / 2
            
            if (quad_top <= char_mid_y <= quad_bottom and
                quad_left <= char_mid_x <= quad_right):
                valid_chars.append(char)
    
    return valid_chars


def extraer_caracteres_rect(datos, alto, all_chars):
    """Extrae caracteres usando Rect (método fallback)"""
    valid_chars = []
    
    x0, y_bottom, x1, y_top = datos["/Rect"]
    rect_top = alto - float(y_top)
    rect_bottom = alto - float(y_bottom)
    rect_left = float(x0)
    rect_right = float(x1)
    
    for char in all_chars:
        char_mid_y = (char['top'] + char['bottom']) / 2
        char_mid_x = (char['x0'] + char['x1']) / 2
        
        if (rect_top <= char_mid_y <= rect_bottom and
            rect_left <= char_mid_x <= rect_right):
            valid_chars.append(char)
    
    return valid_chars


def reconstruir_texto(valid_chars):
    """Reconstruye el texto desde los caracteres detectando espacios"""
    # Deduplicar caracteres por posición
    valid_chars = list({(c['x0'], c['top']): c for c in valid_chars}.values())
    
    # Ordenar por posición (top primero, luego x0)
    valid_chars.sort(key=lambda c: (round(c['top'], 1), c['x0']))
    
    if not valid_chars:
        return ""
    
    partes = []
    ultima_linea = None
    ultimo_x1 = None
    
    for char in valid_chars:
        linea_actual = round(char['top'], 1)
        
        # Si cambiamos de línea, agregar espacio
        if ultima_linea is not None and linea_actual != ultima_linea:
            partes.append(' ')
        # Si hay gap horizontal significativo, agregar espacio
        elif ultimo_x1 is not None:
            gap = char['x0'] - ultimo_x1
            char_width = char['x1'] - char['x0']
            if gap > char_width * 0.3:
                partes.append(' ')
        
        partes.append(char['text'])
        ultima_linea = linea_actual
        ultimo_x1 = char['x1']
    
    texto = ''.join(partes)
    texto = unicodedata.normalize('NFC', texto)
    return texto


def procesar_highlight(datos, alto, all_chars):
    """Procesa un highlight individual y extrae su texto"""
    valid_chars = []
    
    # Usar QuadPoints (preciso) si está disponible
    quads = datos.get("/QuadPoints")
    if quads:
        valid_chars = extraer_caracteres_quads(quads, alto, all_chars)
    else:
        # Fallback a Rect si no hay QuadPoints
        valid_chars = extraer_caracteres_rect(datos, alto, all_chars)
    
    return reconstruir_texto(valid_chars)


def procesar_pdf(archivo_pdf, config):
    """Procesa el PDF y genera el documento Word con los resaltados"""
    reader = PdfReader(archivo_pdf)
    total_paginas = len(reader.pages)
    
    mapa_capitulos = {}
    if config['usar_toc']:
        mapa_capitulos = obtener_mapa_capitulos(reader)

    archivo_pdf.seek(0)
    plumber = pdfplumber.open(archivo_pdf)
    doc = Document()
    
    lista_datos_estructurados = [] 
    barra = st.progress(0)
    contadores = {k: 0 for k in config['mapa_colores'].keys()} 
    ultima_pag_registrada = 0

    for i, pypdf_page in enumerate(reader.pages):
        num_pag_real = i + 1
        barra.progress(num_pag_real / total_paginas)
        
        # --- TOC ---
        if num_pag_real in mapa_capitulos:
            titulo_toc, nivel_cap = mapa_capitulos[num_pag_real]
            nivel_word = min(nivel_cap, 9)
            
            conf_toc = config.get('config_toc', {})
            agregar_heading_toc(doc, titulo_toc, nivel_word, conf_toc)
            lista_datos_estructurados.append((f"CAPITULO_L{nivel_word}", titulo_toc, "TOC"))

        # --- RESALTADOS ---
        if "/Annots" in pypdf_page:
            plumber_page = plumber.pages[i]
            alto = plumber_page.height
            all_chars = plumber_page.chars
            
            anotaciones = [x.get_object() for x in pypdf_page["/Annots"]]
            highlights = [x for x in anotaciones if x.get("/Subtype") == "/Highlight" and "/Rect" in x]
            highlights.sort(key=lambda x: x["/Rect"][3], reverse=True)
            
            # Separador de página
            if highlights and config['separar_paginas'] and num_pag_real > ultima_pag_registrada:
                txt_sep = agregar_separador_pagina(doc, num_pag_real)
                ultima_pag_registrada = num_pag_real
                lista_datos_estructurados.append(("Separador", txt_sep, "SEP"))
            
            # Procesar cada highlight
            for datos in highlights:
                raw_color = datos.get("/C") or datos.get("/Color")
                if not raw_color: 
                    continue
                color_key = tuple(round(c, 1) for c in raw_color)
                
                conf = config['mapa_colores'].get(color_key)
                if not conf or conf['accion'] == "Ignorar": 
                    continue
                
                # Extraer texto del highlight
                texto = procesar_highlight(datos, alto, all_chars)
                
                if texto and len(texto.strip()) > 1:
                    texto_clean = texto.strip().replace("\n", " ")
                    
                    # Aplicar prefijo y sufijo
                    prefijo, sufijo = "", ""
                    if conf.get('autonumerar'):
                        contadores[color_key] += 1
                        prefijo = f"{contadores[color_key]}. " 
                    if conf.get('pag_en_linea'):
                        sufijo = f" (Pág. {num_pag_real})"
                    
                    texto_final = f"{prefijo}{texto_clean}{sufijo}"
                    lista_datos_estructurados.append((conf['accion'], texto_final, color_key))

                    # Escribir en Word
                    agregar_texto_resaltado(doc, texto_final, conf)

    plumber.close()
    
    # Guardar documento
    buffer = guardar_documento_word(doc)
    return buffer, lista_datos_estructurados
