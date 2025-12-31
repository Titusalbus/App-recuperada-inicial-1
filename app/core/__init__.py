# Core - Lógica de negocio (extracción, generación, utilidades)
from .utils import rgb_pdf_a_hex, escanear_colores_pdf, obtener_mapa_capitulos
from .pdf_extractor import procesar_pdf
from .pdf_preview import generar_preview_visual
from .word_generator import (
    aplicar_estilos_word,
    agregar_heading_toc,
    agregar_separador_pagina,
    agregar_texto_resaltado,
    guardar_documento_word
)
