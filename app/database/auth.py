# ==========================================
# AUTENTICACIÓN CON SUPABASE
# ==========================================

import streamlit as st
from .supabase_client import get_supabase_client
import re
import time


def _password_policy_ok(password: str) -> tuple[bool, str]:
    """Valida política de contraseña.
    Reglas: mínimo 12 caracteres, al menos 1 mayúscula, 1 minúscula, 1 dígito y 1 símbolo.
    Retorna (ok, mensaje_error_si_corresponde).
    """
    if len(password) < 12:
        return False, "La contraseña debe tener al menos 12 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe incluir al menos una letra mayúscula."
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe incluir al menos una letra minúscula."
    if not re.search(r"\d", password):
        return False, "La contraseña debe incluir al menos un número."
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "La contraseña debe incluir al menos un símbolo."
    return True, ""


def enviar_reset_password(email: str) -> dict:
    """Envía correo para restablecer contraseña usando Supabase."""
    try:
        supabase = get_supabase_client()
        # En Supabase Python v2
        supabase.auth.reset_password_email(email)
        return {"success": True, "message": "Hemos enviado un email para restablecer tu contraseña."}
    except Exception as e:
        return {"success": False, "message": f"Error al enviar email de recuperación: {e}"}


def ensure_profile(user_id: str) -> None:
    """Crea (si no existe) el perfil del usuario con rol 'user'.
    Requiere que exista la tabla public.profiles con RLS que permita upsert del propio id.
    """
    try:
        supabase = get_supabase_client()
        # upsert id + default role on conflict
        supabase.table("profiles").upsert({"id": user_id, "role": "user"}).execute()
    except Exception:
        # Silencioso: si la tabla aún no existe, no rompemos el login
        pass


def registrar_usuario(email: str, password: str) -> dict:
    """
    Registra un nuevo usuario en Supabase.
    Retorna el usuario creado o lanza una excepción.
    """
    supabase = get_supabase_client()

    # Política de contraseña
    ok, msg = _password_policy_ok(password)
    if not ok:
        return {"success": False, "message": f"❌ {msg}"}
    
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Crear/asegurar perfil
            try:
                ensure_profile(response.user.id)
            except Exception:
                pass
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

    # Rate limiting / bloqueo tras intentos fallidos
    max_intentos = 5
    ventana_segundos = 10 * 60  # 10 minutos ventana
    lockout_segundos = 15 * 60  # bloqueo 15 minutos

    if 'failed_attempts' not in st.session_state:
        st.session_state['failed_attempts'] = []  # lista de timestamps
    if 'lockout_until' not in st.session_state:
        st.session_state['lockout_until'] = 0.0

    now = time.time()
    if st.session_state['lockout_until'] and now < st.session_state['lockout_until']:
        restante = int(st.session_state['lockout_until'] - now)
        return {
            "success": False,
            "message": f"⛔ Cuenta temporalmente bloqueada por intentos fallidos. Intenta en {restante//60} min o usa 'Olvidé mi contraseña'."
        }
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Verificar confirmación de email
            try:
                confirmed = bool(getattr(response.user, 'email_confirmed_at', None))
            except Exception:
                confirmed = True  # Si no podemos leer el atributo, no bloqueamos

            if not confirmed:
                # Cerrar sesión y solicitar confirmación
                try:
                    supabase.auth.sign_out()
                except Exception:
                    pass
                return {
                    "success": False,
                    "message": "⚠️ Debes confirmar tu email antes de acceder. Revisa tu bandeja y confirma la cuenta."
                }

            # Guardar en session_state
            st.session_state['user'] = response.user
            st.session_state['session'] = response.session
            st.session_state['authenticated'] = True

            # Limpiar intentos fallidos tras éxito
            st.session_state['failed_attempts'] = []

            # Asegurar perfil existente
            try:
                ensure_profile(response.user.id)
            except Exception:
                pass
            
            return {
                "success": True,
                "user": response.user,
                "message": "✅ Sesión iniciada correctamente."
            }
        else:
            # Registrar intento fallido
            st.session_state['failed_attempts'].append(now)
            # Filtrar a ventana
            st.session_state['failed_attempts'] = [t for t in st.session_state['failed_attempts'] if now - t <= ventana_segundos]
            if len(st.session_state['failed_attempts']) >= max_intentos:
                st.session_state['lockout_until'] = now + lockout_segundos
                return {
                    "success": False,
                    "message": "⛔ Demasiados intentos fallidos. Te bloqueamos por 15 minutos. Usa 'Olvidé mi contraseña'."
                }
            return {
                "success": False,
                "message": "❌ Email o contraseña incorrectos."
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
