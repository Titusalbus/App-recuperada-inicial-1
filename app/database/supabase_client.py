# ==========================================
# CLIENTE DE SUPABASE
# ==========================================

import os
import streamlit as st
from supabase import create_client, Client


def get_supabase_client() -> Client:
    """
    Crea y retorna un cliente de Supabase.
    Busca las credenciales en:
    1. Streamlit secrets (para producción en Streamlit Cloud)
    2. Variables de entorno (para desarrollo local)
    """
    
    # Intentar obtener de Streamlit secrets primero (producción)
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        # Fallback a variables de entorno (desarrollo local)
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError(
            "❌ Faltan las credenciales de Supabase.\n"
            "Configura SUPABASE_URL y SUPABASE_KEY en:\n"
            "- Streamlit Cloud: Settings > Secrets\n"
            "- Local: archivo .streamlit/secrets.toml"
        )
    
    return create_client(url, key)
