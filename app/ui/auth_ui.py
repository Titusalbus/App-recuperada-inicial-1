# ==========================================
# COMPONENTES DE UI PARA AUTENTICACIÓN
# ==========================================

import streamlit as st
from app.database.auth import (
    registrar_usuario,
    iniciar_sesion,
    cerrar_sesion,
    esta_autenticado,
    obtener_usuario_actual,
    inicializar_estado_auth
)
from app.database.supabase_client import get_supabase_client


def render_login_page():
    """Renderiza la página de login/registro"""
    
    # Inicializar estado
    inicializar_estado_auth()
    
    # Centrar contenido
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔐 PDF Genius</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Accede a tu cuenta</p>", unsafe_allow_html=True)
        
        # --- BOTÓN GOOGLE (DESACTIVADO TEMPORALMENTE) ---
        st.button("🔵 Acceder con Google", use_container_width=True, disabled=True)
        st.caption("⚠️ Google OAuth disponible después del deploy a producción")
        
        st.divider()
        
        # --- FORMULARIO EMAIL/CONTRASEÑA ---
        st.markdown("<p style='text-align: center; color: gray; font-size: 14px;'>O usa tu email</p>", unsafe_allow_html=True)
        
        # Usar radio buttons para seleccionar modo
        modo = st.radio("", ["🔑 Iniciar Sesión", "📝 Crear Cuenta Nueva"], horizontal=True, label_visibility="collapsed")
        
        with st.form("auth_form"):
            email = st.text_input("📧 Email", placeholder="tu@email.com")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            
            # Campo adicional solo para registro
            if modo == "📝 Crear Cuenta Nueva":
                confirmar_password = st.text_input("🔑 Confirmar Contraseña", type="password", placeholder="Repite tu contraseña")
            
            # Botón dinámico según el modo
            if modo == "🔑 Iniciar Sesión":
                submit = st.form_submit_button("Iniciar Sesión", use_container_width=True, type="primary")
                
                if submit and email and password:
                    with st.spinner("Verificando credenciales..."):
                        resultado = iniciar_sesion(email, password)
                    
                    if resultado["success"]:
                        st.success(resultado["message"])
                        st.rerun()
                    else:
                        st.error(resultado["message"])
                        
            else:  # Modo registro
                submit = st.form_submit_button("Crear Cuenta", use_container_width=True, type="primary")
                
                if submit and email and password:
                    if 'confirmar_password' in locals() and password != confirmar_password:
                        st.error("❌ Las contraseñas no coinciden.")
                    elif len(password) < 6:
                        st.error("❌ La contraseña debe tener al menos 6 caracteres.")
                    else:
                        with st.spinner("Creando cuenta..."):
                            resultado = registrar_usuario(email, password)
                        
                        if resultado["success"]:
                            st.success(resultado["message"])
                        else:
                            st.error(resultado["message"])
            
            if submit and (not email or not password):
                st.warning("Por favor completa todos los campos.")


def render_user_header():
    """Renderiza el header con info del usuario y botón logout"""
    user = obtener_usuario_actual()
    
    if user:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"👤 **{user.email}**")
        with col2:
            if st.button("🚪 Salir", type="secondary"):
                cerrar_sesion()
                st.rerun()
