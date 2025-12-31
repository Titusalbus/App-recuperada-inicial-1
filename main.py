# ==========================================
# MAIN - PUNTO DE ENTRADA DE LA APLICACIÓN
# ==========================================

import streamlit as st

# Configuración
from app.config import PAGE_CONFIG

# Core - Lógica de negocio
from app.core import escanear_colores_pdf, procesar_pdf, generar_preview_visual

# UI - Componentes de interfaz
from app.ui import (
    render_tab_home,
    render_tab_pricing,
    render_color_config,
    render_toc_config,
    render_global_settings,
    render_preview,
    render_download_button
)

# Auth - Autenticación
from app.ui.auth_ui import render_login_page, render_user_header
from app.database.auth import esta_autenticado, inicializar_estado_auth

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================

st.set_page_config(**PAGE_CONFIG)

# ==========================================
# ESTADO DE SESIÓN
# ==========================================

inicializar_estado_auth()

if 'colores_detectados' not in st.session_state: 
    st.session_state['colores_detectados'] = []
if 'last_file_hash' not in st.session_state: 
    st.session_state['last_file_hash'] = 0

# ==========================================
# VERIFICAR AUTENTICACIÓN
# ==========================================

if not esta_autenticado():
    render_login_page()
else:
    # Usuario autenticado - mostrar app completa
    render_user_header()
    
    # ==========================================
    # TABS PRINCIPALES
    # ==========================================

    tab_home, tab_app, tab_pricing = st.tabs(["🏠 Inicio", "🚀 App", "💳 Planes"])

    # --- TAB INICIO ---
    with tab_home:
        render_tab_home()

    # --- TAB APP ---
    with tab_app:
        st.markdown("## ⚡ Panel de Extracción")
        archivo_subido = st.file_uploader("Subí tu documento PDF", type="pdf")

        if archivo_subido:
            file_hash = archivo_subido.size 
            if st.session_state['last_file_hash'] != file_hash:
                with st.spinner("Escaneando colores y estructura..."):
                    st.session_state['colores_detectados'] = escanear_colores_pdf(archivo_subido)
                    st.session_state['last_file_hash'] = file_hash

            colores = st.session_state['colores_detectados']

            if colores:
                st.success(f"Se encontraron {len(colores)} colores de resaltado.")
                
                # Renderizar componentes de configuración
                config_final = render_color_config(colores)
                config_toc = render_toc_config()
                usar_toc, separar_paginas, padding = render_global_settings()

                # --- PROCESAR ---
                if st.button("🚀 PROCESAR DOCUMENTO", type="primary", use_container_width=True):
                    config_total = {
                        'padding': padding,
                        'usar_toc': usar_toc,
                        'separar_paginas': separar_paginas,
                        'mapa_colores': config_final,
                        'config_toc': config_toc
                    }
                    
                    with st.spinner("Generando documentos..."):
                        word_buffer, lista_datos = procesar_pdf(archivo_subido, config_total)
                        pdf_bytes = generar_preview_visual(lista_datos, config_final, config_toc)
                    
                    if lista_datos:
                        st.success("¡Extracción completada con éxito!")
                        render_download_button(word_buffer)
                        render_preview(pdf_bytes)
                    else:
                        st.warning("No se ha extraído contenido. Verifica que no hayas marcado todo como 'Ignorar'.")
            else:
                st.info("El documento no contiene resaltados legibles.")

    # --- TAB PLANES ---
    with tab_pricing:
        render_tab_pricing()
