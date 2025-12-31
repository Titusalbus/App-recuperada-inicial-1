# ==========================================
# CONFIGURACIÓN Y CONSTANTES GLOBALES
# ==========================================

# Configuración de la página de Streamlit
PAGE_CONFIG = {
    'page_title': "PDF Genius",
    'page_icon': "⚡",
    'layout': "wide"
}

# Listas de opciones para la UI
LISTA_FUENTES = [
    "Arial", 
    "Calibri", 
    "Times New Roman", 
    "Courier New", 
    "Verdana", 
    "Georgia", 
    "Trebuchet MS", 
    "Helvetica"
]

LISTA_ALINEACIONES = [
    "Izquierda", 
    "Centrado", 
    "Derecha", 
    "Justificado"
]

LISTA_ACCIONES = [
    "Ignorar", 
    "Texto Normal", 
    "Título", 
    "Subtítulo", 
    "Dato Clave"
]

LISTA_ESTILOS_LISTA = [
    "Ninguna", 
    "Bullets (•)", 
    "Numerada (1.)"
]

LISTA_ESPACIADOS = [
    "Simple", 
    "1.15", 
    "1.5", 
    "Doble"
]

# Valores por defecto para opciones de color
DEFAULT_COLOR_OPTIONS = {
    'accion': 'Ignorar',
    'fuente': 'Arial',
    'tamano': 11,
    'alineacion': 'Izquierda',
    'interlineado': 'Simple',
    'lista': 'Ninguna',
    'autonumerar': False,
    'pag_en_linea': False
}

# Valores por defecto para TOC
DEFAULT_TOC_CONFIG = {
    'fuente': 'Arial',
    'tamano': 16
}

# Valores por defecto para ajustes globales
DEFAULT_GLOBAL_SETTINGS = {
    'usar_toc': True,
    'separar_paginas': True,
    'padding': 1
}
