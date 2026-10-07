import hmac

import streamlit as st

from core import almacenamiento, marca
from core.validacion import leer_padron

marca.aplicar_estilos()
marca.encabezado("Administración", "Padrón de socios e inscripciones")

clave_configurada = st.secrets.get("admin_password", "")
if not clave_configurada:
    marca.caja("Falta configurar <b>admin_password</b> en los secrets de la app.", "error")
    st.stop()

if not st.session_state.get("admin_ok"):
    with st.form("login"):
        clave = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar", width="stretch"):
            if hmac.compare_digest(clave, clave_configurada):
                st.session_state["admin_ok"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()

st.subheader("1. Padrón de socios")
padron = almacenamiento.cargar_padron()
actualizado = almacenamiento.padron_actualizado()
if padron:
    marca.caja(f"Padrón activo: <b>{len(padron):,}</b> DNIs · actualizado el {actualizado:%d/%m/%Y %H:%M}".replace(",", "."), "ok")
else:
    marca.caja("Todavía no hay padrón cargado: el formulario no acepta solicitudes.", "error")

archivo = st.file_uploader("Subí el archivo con los DNIs de socios (.xlsx, .csv o .txt)", type=["xlsx", "xls", "csv", "txt"])
if archivo is not None:
    try:
        nuevos = leer_padron(archivo.name, archivo.getvalue())
    except Exception as error:  # archivo dañado o formato raro
        st.error(f"No pude leer el archivo: {error}")
    else:
        if not nuevos:
            st.error("El archivo no tiene DNIs válidos (7 u 8 números).")
        else:
            st.write(f"Encontré **{len(nuevos):,}** DNIs válidos en *{archivo.name}*.".replace(",", "."))
            if st.button("Reemplazar padrón con este archivo"):
                almacenamiento.guardar_padron(nuevos)
                st.success("Padrón actualizado.")
                st.rerun()

st.subheader("2. Inscripciones")
inscripciones = almacenamiento.leer_inscripciones()
st.write(f"Solicitudes recibidas: **{len(inscripciones)}**")
if not inscripciones.empty:
    st.dataframe(inscripciones, hide_index=True)
    st.download_button(
        "Descargar Excel",
        almacenamiento.inscripciones_excel(),
        file_name="inscripciones_beneficio.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if st.button("Cerrar sesión"):
    del st.session_state["admin_ok"]
    st.rerun()
