import hmac
from html import escape

import streamlit as st

from core import contenido as c
from core import marca
from core.config import obtener_almacen, secret
from core.socios import leer_padron, meses_adeudados, nombre_mes, plantilla_excel


def resumen(socios) -> str:
    al_dia = sum(1 for s in socios.values() if s.ultima_cuota and not meses_adeudados(s, c.MES_REQUERIDO))
    debito = sum(1 for s in socios.values() if s.debito)
    sin_dato = sum(1 for s in socios.values() if s.ultima_cuota is None)
    texto = (
        f"<b>{len(socios):,}</b> socios · <b>{al_dia:,}</b> con {nombre_mes(c.MES_REQUERIDO)} pago · "
        f"<b>{debito:,}</b> con débito automático"
    )
    if sin_dato:
        texto += f" · <b>{sin_dato:,}</b> sin dato de cuota"
    return texto.replace(",", ".")


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
    marca.caja(f"Padrón activo: {resumen(padron)}<br>Actualizado el {almacen.padron_actualizado()}")
else:
    marca.caja("Todavía no hay padrón cargado: el formulario no acepta participantes.", "error")

st.markdown(
    "El archivo necesita tres columnas: <b>DNI</b>, <b>Última cuota paga</b> (por ejemplo 10/2026) y "
    "<b>Débito automático</b> (Sí / No).",
    unsafe_allow_html=True,
)
st.download_button(
    "Descargar plantilla del padrón",
    plantilla_excel(),
    file_name="plantilla_padron_sorteo.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

archivo = st.file_uploader("Archivo del padrón (.xlsx, .csv o .txt)", type=["xlsx", "xls", "csv", "txt"])
if archivo is not None:
    try:
        nuevos = leer_padron(archivo.name, archivo.getvalue())
    except Exception as error:  # archivo dañado o formato raro
        st.error(f"No pude leer el archivo: {error}")
    else:
        if not nuevos:
            st.error("El archivo no tiene DNIs válidos (7 u 8 números).")
        else:
            marca.caja(f"En <i>{escape(archivo.name)}</i> encontré: {resumen(nuevos)}")
            if not any(s.debito for s in nuevos.values()):
                st.warning("Ningún socio figura con débito automático: revisá que el archivo tenga esa columna.")
            if all(s.ultima_cuota is None for s in nuevos.values()):
                st.error("No pude leer ninguna fecha de última cuota paga: revisá esa columna antes de cargarlo.")
            elif st.button("Reemplazar padrón con este archivo", width="stretch"):
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
