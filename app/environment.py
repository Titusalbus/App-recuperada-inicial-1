# ==========================================
# CONFIGURACIÓN SIMPLE DE AMBIENTE
# ==========================================

import os
import streamlit as st
from typing import Optional


def _get_secret(key: str, default: str = None) -> Optional[str]:
    """Obtiene un secreto de Streamlit secrets o variables de entorno"""
    # Primero intenta Streamlit secrets
    try:
        return st.secrets.get(key)
    except (KeyError, FileNotFoundError, AttributeError):
        pass
    
    # Luego variables de entorno
    return os.environ.get(key, default)


def get_supabase_url() -> str:
    """Obtiene la URL de Supabase"""
    url = _get_secret("SUPABASE_URL")
    if not url:
        raise ValueError("❌ Falta SUPABASE_URL en tus secretos")
    return url


def get_supabase_key() -> str:
    """Obtiene la clave de Supabase"""
    key = _get_secret("SUPABASE_KEY") 
    if not key:
        raise ValueError("❌ Falta SUPABASE_KEY en tus secretos")
    return key


def is_dev() -> bool:
    """Verifica si estás en desarrollo local"""
    env = _get_secret("ENVIRONMENT", "dev").lower()
    return env == "dev"


def is_prod() -> bool:
    """Verifica si estás en producción"""
    env = _get_secret("ENVIRONMENT", "dev").lower()
    return env == "prod"


def show_environment_badge():
    """Muestra un badge de desarrollo cuando no estés en producción"""
    if is_dev():
        st.sidebar.markdown(
            '<div style="background-color:orange;color:white;padding:5px 10px;'
            'border-radius:5px;text-align:center;font-weight:bold;margin-bottom:10px;">'
            '🔧 DESARROLLO</div>',
            unsafe_allow_html=True
        )
