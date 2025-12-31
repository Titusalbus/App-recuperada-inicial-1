# ==========================================
# MÓDULO DE BASE DE DATOS (SUPABASE)
# ==========================================

from .supabase_client import get_supabase_client
from .auth import (
    registrar_usuario,
    iniciar_sesion,
    cerrar_sesion,
    obtener_usuario_actual,
    esta_autenticado
)

__all__ = [
    'get_supabase_client',
    'registrar_usuario',
    'iniciar_sesion', 
    'cerrar_sesion',
    'obtener_usuario_actual',
    'esta_autenticado'
]
