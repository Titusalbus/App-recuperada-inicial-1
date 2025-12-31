# ==========================================
# GENERADOR DE VISTA PREVIA PDF (FPDF)
# ==========================================

import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os


def cargar_fuentes_pdf(pdf):
    """Carga las fuentes personalizadas para el PDF"""
    ruta_arial = os.path.join("assets", "arial.ttf")
    ruta_arial_bold = os.path.join("assets", "arialbd.ttf")
    ruta_arial_italic = os.path.join("assets", "ariali.ttf")

    fuente_cargada = False
    font_main = "Arial"
    
    if os.path.exists(ruta_arial) and os.path.exists(ruta_arial_bold):
        try:
            pdf.add_font("CustomArial", "", ruta_arial)
            pdf.add_font("CustomArial", "B", ruta_arial_bold)

            if os.path.exists(ruta_arial_italic):
                pdf.add_font("CustomArial", "I", ruta_arial_italic)
            else:
                st.warning("⚠️ No se encontró 'ariali.ttf'. Usando fuente regular en lugar de itálica.")

            font_main = "CustomArial"
            fuente_cargada = True
        except Exception as e:
            st.error(f"Error cargando fuentes: {e}")
    else:
        st.warning("⚠️ No se encontraron las fuentes en 'assets'. Usando Arial estándar.")
    
    return font_main, fuente_cargada


def renderizar_toc(pdf, tipo, txt_safe, config_toc, font_main, fuente_cargada):
    """Renderiza un elemento TOC en el PDF"""
    pdf.ln(2)
    nivel = int(tipo[-1])
    font_size = config_toc.get('tamano', 14)
    if nivel > 1: 
        font_size -= 2
    
    is_bold = 'B'
    pdf.set_text_color(31, 73, 125)
    
    if not fuente_cargada:
        txt_safe = txt_safe.encode('latin-1', 'replace').decode('latin-1')
    
    return txt_safe, is_bold, font_size


def renderizar_separador(pdf, txt_safe, font_main, fuente_cargada):
    """Renderiza un separador de página en el PDF"""
    pdf.ln(5)
    pdf.set_font(font_main, 'I', 9)
    pdf.set_text_color(150, 150, 150)
    
    if not fuente_cargada:
        txt_safe = txt_safe.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.cell(0, 5, txt_safe, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')


def renderizar_resaltado(txt_safe, ref, config_colores_final, fuente_cargada):
    """Procesa un elemento resaltado para el PDF"""
    font_size = 11
    is_bold = ''
    align = 'L'
    
    if ref in config_colores_final:
        conf = config_colores_final[ref]
        font_size = conf.get('tamano', 11)
        
        if conf['accion'] in ["Título", "Dato Clave"]: 
            is_bold = 'B'
        
        align_map = {"Izquierda": 'L', "Centrado": 'C', "Derecha": 'R', "Justificado": 'J'}
        align = align_map.get(conf.get('alineacion', 'Izquierda'), 'L')
        
        # Listas simuladas
        if conf.get('lista') == "Bullets (•)":
            txt_safe = f"• {txt_safe}"
        elif conf.get('lista') == "Numerada (1.)":
            txt_safe = f"1. {txt_safe}"
        
        if not fuente_cargada:
            txt_safe = txt_safe.encode('latin-1', 'replace').decode('latin-1')
    
    return txt_safe, is_bold, font_size, align


def generar_preview_visual(lista_datos, config_colores_final, config_toc):
    """Genera PDF visual usando FPDF con soporte Unicode"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Cargar fuentes
    font_main, fuente_cargada = cargar_fuentes_pdf(pdf)
    
    pdf.add_page()
    
    for tipo, texto, ref in lista_datos:
        txt_safe = texto 
        pdf.set_text_color(0, 0, 0)
        is_bold = ''
        font_size = 11
        align = 'L'

        # CASO A: TOC
        if "CAPITULO_L" in tipo:
            txt_safe, is_bold, font_size = renderizar_toc(
                pdf, tipo, txt_safe, config_toc, font_main, fuente_cargada
            )

        # CASO B: Separador
        elif tipo == "Separador":
            renderizar_separador(pdf, txt_safe, font_main, fuente_cargada)
            continue

        # CASO C: Resaltados
        else:
            txt_safe, is_bold, font_size, align = renderizar_resaltado(
                txt_safe, ref, config_colores_final, fuente_cargada
            )

        # Renderizar celda
        pdf.set_font(font_main, is_bold, font_size)
        try:
            pdf.multi_cell(0, font_size/2 + 2, txt_safe, align=align)
        except:
            pdf.multi_cell(0, font_size/2 + 2, "Error de codificación.", align=align)
            
        pdf.ln(1)

    return bytes(pdf.output())
