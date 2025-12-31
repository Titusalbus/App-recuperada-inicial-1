# ==========================================
# UTILIDADES Y MOTORES LÓGICOS
# ==========================================

from pypdf import PdfReader

def rgb_pdf_a_hex(rgb_tuple):
    """Convierte tupla (0-1) a Hex string"""
    if not rgb_tuple:
        return "#000000"
    r = int(rgb_tuple[0] * 255)
    g = int(rgb_tuple[1] * 255)
    b = int(rgb_tuple[2] * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def escanear_colores_pdf(archivo_pdf):
    """Escanea el PDF en busca de anotaciones Highlight"""
    colores_encontrados = set()
    archivo_pdf.seek(0)
    reader = PdfReader(archivo_pdf)
    for page in reader.pages:
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()
                if obj.get("/Subtype") == "/Highlight":
                    color = obj.get("/C") or obj.get("/Color")
                    if color:
                        # Redondeo a 1 decimal para agrupar colores similares
                        color_normalizado = tuple(round(c, 1) for c in color)
                        colores_encontrados.add(color_normalizado)
    return list(colores_encontrados)

def obtener_mapa_capitulos(reader):
    """Extrae la estructura del TOC (Outline)"""
    mapa = {}
    def extraer_recursivo(lista_items, nivel=1):
        for item in lista_items:
            if isinstance(item, list):
                extraer_recursivo(item, nivel + 1)
            else:
                try:
                    titulo = item.title
                    pag_num = reader.get_destination_page_number(item) + 1
                    if titulo and pag_num:
                        mapa[pag_num] = (titulo, nivel)
                except: pass
    try:
        if reader.outline: extraer_recursivo(reader.outline)
    except: pass
    return mapa
