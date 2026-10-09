import hmac

import streamlit as st

from core import marca
from core.config import obtener_almacen, secret
from core.validacion import leer_padron

marca.aplicar_estilos()
marca.encabezado("Administración", "Sorteo canal socios · padrón y participantes")

clave_configurada = secret("admin_password", "")
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

almacen = obtener_almacen()
marca.caja(f"Los datos se guardan en {almacen.descripcion}.")

marca.seccion("01", "Padrón de socios")
padron = almacen.cargar_padron()
if padron:
    marca.caja(f"Padrón activo: <b>{len(padron):,}</b> DNIs · actualizado el {almacen.padron_actualizado()}".replace(",", "."))
else:
    marca.caja("Todavía no hay padrón cargado: el formulario no acepta participantes.", "error")

archivo = st.file_uploader("Archivo con los DNIs de socios (.xlsx, .csv o .txt)", type=["xlsx", "xls", "csv", "txt"])
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
            if st.button("Reemplazar padrón con este archivo", width="stretch"):
                almacen.guardar_padron(nuevos)
                st.success("Padrón actualizado.")
                st.rerun()

marca.seccion("02", "Participantes")
participantes = almacen.leer_participantes()
st.write(f"Participantes anotados: **{len(participantes)}**")
if not participantes.empty:
    st.dataframe(participantes, hide_index=True)
    st.download_button(
        "Descargar Excel",
        almacen.participantes_excel(),
        file_name="sorteo_participantes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
    )

if st.button("Cerrar sesión"):
    del st.session_state["admin_ok"]
    st.rerun()
