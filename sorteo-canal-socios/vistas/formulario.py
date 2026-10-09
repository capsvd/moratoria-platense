from datetime import datetime
from html import escape

import streamlit as st

from core import contenido as c
from core import marca
from core.almacenamiento import ZONA
from core.config import cierre_sorteo, obtener_almacen, secret
from core.validacion import normalizar_dni, validar_participacion

marca.aplicar_estilos()
marca.portada(c.TITULO, c.SUBTITULO, c.INTRO)

link_canal = secret("link_canal", "")
boton_canal = (
    f"<a class='cap-canal' href='{escape(link_canal)}' target='_blank'>Seguir el canal en WhatsApp</a>"
    if link_canal
    else ""
)
marca.tarjeta(c.PREMIOS_TITULO, marca.lista(c.PREMIOS))
marca.tarjeta(c.REQUISITOS_TITULO, f"<p>{escape(c.REQUISITOS_INTRO)}</p>{marca.lista(c.REQUISITOS, numerada=True)}{boton_canal}")
marca.tarjeta(c.ANUNCIO_TITULO, f"<p>{escape(c.ANUNCIO)}</p>")

cierre = cierre_sorteo()
if cierre and datetime.now(ZONA) >= cierre:
    marca.caja("<b>La inscripción al sorteo ya cerró.</b><br>¡Gracias por sumarte al canal de socios! 🤎")
    st.stop()

if st.session_state.get("participacion_ok"):
    marca.caja(
        f"<b>¡Listo, {escape(st.session_state['participacion_ok'])}! Ya estás participando.</b><br>"
        f"{escape(c.ANUNCIO)} ¡Mucha suerte! 🤎",
    )
    if st.button("Anotar a otra persona", width="stretch"):
        del st.session_state["participacion_ok"]
        st.rerun()
    st.stop()

marca.cta(c.CIERRE)

with st.form("participacion"):
    marca.seccion("01", "Tus datos")
    nombre = st.text_input("Nombre y apellido")
    col1, col2 = st.columns(2)
    dni = col1.text_input("DNI", placeholder="Sin puntos")
    whatsapp = col2.text_input("WhatsApp", placeholder="11 2345 6789")
    mail = st.text_input("Mail", placeholder="nombre@mail.com")

    marca.seccion("02", "Canal de socios")
    sigue_canal = st.checkbox(c.CHECK_CANAL)
    enviado = st.form_submit_button(c.BOTON_ENVIAR, width="stretch")

if enviado:
    datos = {"nombre": nombre, "dni": dni, "whatsapp": whatsapp, "mail": mail, "sigue_canal": sigue_canal}
    errores = validar_participacion(datos)
    if errores:
        marca.caja("<b>Revisá estos datos:</b><br>" + "<br>".join(f"• {escape(e)}" for e in errores), "error")
        st.stop()

    almacen = obtener_almacen()
    padron = almacen.cargar_padron()
    if not padron:
        marca.caja("<b>El sorteo todavía no está habilitado.</b><br>Probá de nuevo en un rato.", "error")
    elif normalizar_dni(dni) not in padron:
        marca.caja(
            "<b>No estás apto/a como socio/a para participar del sorteo.</b><br>"
            "Tu DNI no figura en el padrón de socios. Si creés que es un error, acercate a la oficina de Socios.",
            "error",
        )
    elif almacen.ya_participa(dni):
        marca.caja("<b>Ya estás participando del sorteo con este DNI.</b><br>No hace falta que te anotes de nuevo.")
    else:
        almacen.guardar_participante(datos)
        st.session_state["participacion_ok"] = nombre.strip().split()[0]
        st.rerun()
