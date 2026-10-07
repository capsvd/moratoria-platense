from html import escape

import streamlit as st

from core import almacenamiento, marca
from core.validacion import normalizar_dni, validar_inscripcion

TEXTO_CONSENTIMIENTO = (
    "Acepto que el Club Atlético Platense use estos datos para gestionar el beneficio y contactarme, "
    "conforme a la Ley 25.326 de Protección de Datos Personales."
)

marca.aplicar_estilos()
marca.encabezado("Beneficio Socios", "Completá tus datos para solicitar el beneficio")

if st.session_state.get("inscripcion_ok"):
    marca.caja(
        f"<b>¡Listo, {escape(st.session_state['inscripcion_ok'])}!</b><br>"
        "Recibimos tu solicitud. Te vamos a contactar por WhatsApp o mail.",
        "ok",
    )
    if st.button("Cargar otra solicitud"):
        del st.session_state["inscripcion_ok"]
        st.rerun()
    marca.pie()
    st.stop()

with st.form("inscripcion"):
    st.subheader("Tus datos")
    nombre = st.text_input("Nombre y apellido")
    col1, col2 = st.columns(2)
    dni = col1.text_input("DNI", placeholder="Sin puntos")
    whatsapp = col2.text_input("WhatsApp", placeholder="11 2345 6789")
    mail = st.text_input("Mail", placeholder="nombre@mail.com")

    st.subheader("Datos de tu madre")
    madre_nombre = st.text_input("Nombre y apellido de la madre")
    col3, col4 = st.columns(2)
    madre_dni = col3.text_input("DNI de la madre", placeholder="Sin puntos")
    madre_whatsapp = col4.text_input("WhatsApp de la madre", placeholder="11 2345 6789")
    madre_mail = st.text_input("Mail de la madre", placeholder="nombre@mail.com")

    st.markdown("<br>", unsafe_allow_html=True)
    consentimiento = st.checkbox(TEXTO_CONSENTIMIENTO)
    enviado = st.form_submit_button("Enviar solicitud", width="stretch")

if enviado:
    datos = {
        "nombre": nombre,
        "dni": dni,
        "whatsapp": whatsapp,
        "mail": mail,
        "madre_nombre": madre_nombre,
        "madre_dni": madre_dni,
        "madre_whatsapp": madre_whatsapp,
        "madre_mail": madre_mail,
        "consentimiento": consentimiento,
    }
    errores = validar_inscripcion(datos)
    padron = almacenamiento.cargar_padron()

    if errores:
        marca.caja("<b>Revisá estos datos:</b><br>" + "<br>".join(f"• {escape(e)}" for e in errores), "error")
    elif not padron:
        marca.caja("<b>El formulario todavía no está habilitado.</b><br>Probá de nuevo más tarde.", "error")
    elif normalizar_dni(dni) not in padron:
        marca.caja(
            "<b>No estás apto/a como socio/a para recibir el beneficio.</b><br>"
            "Tu DNI no figura en el padrón de socios. Si creés que es un error, "
            "acercate a la oficina de Socios.",
            "error",
        )
    elif almacenamiento.ya_inscripto(dni):
        marca.caja("<b>Ya tenemos una solicitud con este DNI.</b><br>No hace falta que la envíes de nuevo.", "ok")
    else:
        almacenamiento.guardar_inscripcion(datos)
        st.session_state["inscripcion_ok"] = nombre.strip().split()[0]
        st.rerun()

marca.pie()
