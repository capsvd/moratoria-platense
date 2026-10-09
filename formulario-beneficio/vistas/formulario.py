from html import escape

import streamlit as st

from core import marca
from core.config import obtener_almacen
from core.validacion import normalizar_dni, validar_inscripcion

TEXTO_CONSENTIMIENTO = "Al aceptar me comprometo a utilizar la entrada de invitado para el fin asignado."

marca.aplicar_estilos()
marca.encabezado("Beneficio Socios", "Entrada de invitado")

if st.session_state.get("inscripcion_ok"):
    marca.caja(
        f"<b>¡Listo, {escape(st.session_state['inscripcion_ok'])}!</b><br>"
        "Recibimos tu solicitud. Te vamos a contactar por WhatsApp o mail.",
    )
    if st.button("Cargar otra solicitud", width="stretch"):
        del st.session_state["inscripcion_ok"]
        st.rerun()
    st.stop()

with st.form("inscripcion"):
    marca.seccion("01", "Tus datos")
    nombre = st.text_input("Nombre y apellido")
    col1, col2 = st.columns(2)
    dni = col1.text_input("DNI", placeholder="Sin puntos")
    whatsapp = col2.text_input("WhatsApp", placeholder="11 2345 6789")
    mail = st.text_input("Mail", placeholder="nombre@mail.com")

    marca.seccion("02", "Datos de tu madre")
    madre_nombre = st.text_input("Nombre y apellido de la madre")
    col3, col4 = st.columns(2)
    madre_dni = col3.text_input("DNI de la madre", placeholder="Sin puntos")
    madre_whatsapp = col4.text_input("WhatsApp de la madre", placeholder="11 2345 6789")
    madre_mail = st.text_input("Mail de la madre", placeholder="nombre@mail.com")

    marca.seccion("03", "Consentimiento")
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
    if errores:
        marca.caja("<b>Revisá estos datos:</b><br>" + "<br>".join(f"• {escape(e)}" for e in errores), "error")
        st.stop()

    almacen = obtener_almacen()
    padron = almacen.cargar_padron()
    if not padron:
        marca.caja("<b>El formulario todavía no está habilitado.</b><br>Probá de nuevo más tarde.", "error")
    elif normalizar_dni(dni) not in padron:
        marca.caja(
            "<b>No estás apto/a como socio/a para recibir el beneficio.</b><br>"
            "Tu DNI no figura en el padrón de socios. Si creés que es un error, acercate a la oficina de Socios.",
            "error",
        )
    elif almacen.ya_inscripto(dni):
        marca.caja("<b>Ya tenemos una solicitud con este DNI.</b><br>No hace falta que la envíes de nuevo.")
    else:
        almacen.guardar_inscripcion(datos)
        st.session_state["inscripcion_ok"] = nombre.strip().split()[0]
        st.rerun()
