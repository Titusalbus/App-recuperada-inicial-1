# ==========================================
# AUTENTICACIÓN CON SUPABASE
# ==========================================

import streamlit as st
from .supabase_client import get_supabase_client


def registrar_usuario(email: str, password: str) -> dict:
    """
    Registra un nuevo usuario en Supabase.
    Retorna el usuario creado o lanza una excepción.
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            return {
                "success": True,
                "user": response.user,
                "message": "✅ Usuario registrado. Revisa tu email para confirmar."
            }
        else:
            return {
                "success": False,
                "message": "❌ Error al registrar usuario."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error: {str(e)}"
        }


def iniciar_sesion(email: str, password: str) -> dict:
    """
    Inicia sesión con email y contraseña.
    Guarda la sesión en st.session_state.
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Guardar en session_state
            st.session_state['user'] = response.user
            st.session_state['session'] = response.session
            st.session_state['authenticated'] = True
            
            return {
                "success": True,
                "user": response.user,
                "message": "✅ Sesión iniciada correctamente."
            }
        else:
            return {
                "success": False,
                "message": "❌ Credenciales inválidas."
            }
    except Exception as e:
        error_msg = str(e)
        if "Invalid login credentials" in error_msg:
            return {
                "success": False,
                "message": "❌ Email o contraseña incorrectos."
            }
        return {
            "success": False,
            "message": f"❌ Error: {error_msg}"
        }


def cerrar_sesion():
    """Cierra la sesión actual."""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except:
        pass
    
    # Limpiar session_state
    st.session_state['user'] = None
    st.session_state['session'] = None
    st.session_state['authenticated'] = False


def obtener_usuario_actual():
    """Retorna el usuario actual o None si no hay sesión."""
    return st.session_state.get('user', None)


def esta_autenticado() -> bool:
    """Verifica si hay un usuario autenticado."""
    return st.session_state.get('authenticated', False)


def inicializar_estado_auth():
    """Inicializa las variables de sesión para autenticación."""
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'session' not in st.session_state:
        st.session_state['session'] = None
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Verificar si hay una sesión activa en Supabase
    try:
        supabase = get_supabase_client()
        user_session = supabase.auth.get_session()
        
        if user_session and user_session.user:
            # Hay una sesión activa, actualizar estado
            st.session_state['user'] = user_session.user
            st.session_state['session'] = user_session
            st.session_state['authenticated'] = True
    except Exception as e:
        # Si hay error, mantener estado actual
        pass
