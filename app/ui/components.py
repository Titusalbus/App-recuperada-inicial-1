# ==========================================
# COMPONENTES DE UI (STREAMLIT)
# ==========================================

import streamlit as st
import base64

from app.config import (
    LISTA_FUENTES, 
    LISTA_ALINEACIONES, 
    LISTA_ACCIONES,
    LISTA_ESTILOS_LISTA,
    LISTA_ESPACIADOS,
    DEFAULT_COLOR_OPTIONS,
    DEFAULT_TOC_CONFIG,
    DEFAULT_GLOBAL_SETTINGS
)
from app.core.utils import rgb_pdf_a_hex


def render_color_config(colores):
    """Renderiza el expander de configuración de colores"""
    config_final = {}
    
    with st.expander("🎨 Configurar Colores", expanded=True):
        for i, color_tuple in enumerate(colores):
            hex_color = rgb_pdf_a_hex(color_tuple)
            
            c1, c2 = st.columns([1, 6])
            with c1:
                st.color_picker(f"Color {i}", value=hex_color, disabled=True, key=f"pk_{i}")
            with c2:
                cols = st.columns(4)
                accion = cols[0].selectbox("Acción", LISTA_ACCIONES, key=f"act_{i}")
                
                opts = DEFAULT_COLOR_OPTIONS.copy()
                opts['accion'] = accion
                
                if accion != "Ignorar":
                    opts['fuente'] = cols[1].selectbox("Fuente", LISTA_FUENTES, key=f"font_{i}")
                    opts['tamano'] = cols[2].number_input("Tamaño (pt)", 8, 48, 11 if accion!="Título" else 16, key=f"sz_{i}")
                    opts['alineacion'] = cols[3].selectbox("Alineación", LISTA_ALINEACIONES, key=f"al_{i}")
                    
                    c_adv = st.columns(4)
                    opts['lista'] = c_adv[0].selectbox("Estilo de Lista", LISTA_ESTILOS_LISTA, key=f"lst_{i}")
                    opts['autonumerar'] = c_adv[1].checkbox("Enumerar ítems (1, 2...)", key=f"n_{i}", help="Agrega un número correlativo al inicio.")
                    opts['pag_en_linea'] = c_adv[2].checkbox("Agregar N° Pág. al final", key=f"p_{i}", help="Añade '(Pág. X)' al final del párrafo.")
                    opts['interlineado'] = c_adv[3].selectbox("Espaciado", LISTA_ESPACIADOS, key=f"spac_{i}")
                
                config_final[color_tuple] = opts
                st.divider()
    
    return config_final


def render_toc_config():
    """Renderiza el expander de configuración del TOC"""
    with st.expander("📑 Configuración del Índice (TOC)", expanded=False):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.info("Configura cómo se verán los títulos del índice original del PDF en tu Word.")
        with col_t2:
            toc_fuente = st.selectbox("Fuente del Índice", LISTA_FUENTES, key="toc_f")
            toc_tamano = st.number_input("Tamaño Título Principal (L1)", 10, 36, DEFAULT_TOC_CONFIG['tamano'], key="toc_s")
    
    return {'fuente': toc_fuente, 'tamano': toc_tamano}


def render_global_settings():
    """Renderiza el expander de ajustes globales"""
    with st.expander("⚙️ Ajustes Globales de Exportación", expanded=False):
        gc1, gc2, gc3 = st.columns(3)
        with gc1: 
            usar_toc = st.toggle("Incluir Índice (TOC)", value=DEFAULT_GLOBAL_SETTINGS['usar_toc'])
        with gc2: 
            separar_paginas = st.toggle("Insertar Separador de Páginas", value=DEFAULT_GLOBAL_SETTINGS['separar_paginas'])
        with gc3: 
            padding = st.slider("Margen de Captura (Padding)", 0, 5, DEFAULT_GLOBAL_SETTINGS['padding'], help="Aumenta el área de recorte si el texto sale cortado.")
    
    return usar_toc, separar_paginas, padding


def render_preview(pdf_bytes):
    """Renderiza la vista previa del PDF generado"""
    st.divider()
    st.subheader("👀 Vista Previa del Resultado")
    
    # Asegurarse de que pdf_bytes sea de tipo bytes
    if not isinstance(pdf_bytes, bytes):
        if isinstance(pdf_bytes, str):
            pdf_bytes = bytes(pdf_bytes, encoding='latin-1')
        else:
            raise ValueError("El objeto pdf_bytes no es ni bytes ni str, no se puede convertir.")
    
    b64 = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{b64}" width="100%" height="800" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)


def render_download_button(word_buffer):
    """Renderiza el botón de descarga del documento Word"""
    st.download_button(
        label="📥 Descargar Documento Word (.docx)",
        data=word_buffer,
        file_name="Resumen_PDF_Genius.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )


# ==========================================
# PÁGINAS / TABS
# ==========================================

def render_tab_home():
    """Renderiza el contenido del tab Inicio"""
    st.markdown("<h1 style='text-align: center;'>PDF Genius</h1>", unsafe_allow_html=True)
    st.info("👋 Si quieres soporte para tildes, asegúrate de tener la carpeta 'assets' con 'arial.ttf'.")


def render_tab_pricing():
    """Renderiza el contenido del tab Planes"""
    st.header("Planes Disponibles")
    st.write("Contenido de precios...")
