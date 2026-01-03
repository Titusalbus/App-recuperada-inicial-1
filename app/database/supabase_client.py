# ==========================================
# CLIENTE DE SUPABASE
# ==========================================

import streamlit as st
from supabase import create_client, Client
from app.environment import get_supabase_url, get_supabase_key


def get_supabase_client() -> Client:
    """
    Crea y retorna un cliente de Supabase.
    Lee SUPABASE_URL y SUPABASE_KEY de tus secretos.
    """
    url = get_supabase_url()
    key = get_supabase_key()
    
    return create_client(url, key)
