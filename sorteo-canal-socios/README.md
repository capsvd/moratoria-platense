# Sorteo Canal Socios — Club Atlético Platense

Formulario web (Streamlit) con la identidad del Brandbook CAP26 para anotarse en el sorteo
exclusivo del canal de WhatsApp "Socios Club Atlético Platense". Solo puede participar quien
figura en el padrón de socios que sube el club. Todo queda en una planilla de Google Sheets.

## Qué hace

- **Formulario** (`/`): muestra título, premios, requisitos y fecha del anuncio, y pide nombre y
  apellido, DNI, WhatsApp, mail y la confirmación de que sigue el canal.
  - DNI fuera del padrón → *"No estás apto/a como socio/a para participar del sorteo"*, no se guarda.
  - DNI ya anotado → *"Ya estás participando del sorteo con este DNI"*.
  - Pasada la hora de `cierre` (opcional) el formulario deja de aceptar participantes.
- **Administración** (`/admin`, con contraseña): subir el padrón (.xlsx, .csv o .txt con DNIs),
  ver los participantes, abrir la planilla y descargar un Excel.

## Textos

Todos los textos del sorteo (título, premios, requisitos, fecha del anuncio, botón) están en
`core/contenido.py`. Para otra edición del sorteo alcanza con cambiar ese archivo.

## Google Sheets

La app usa una planilla con dos hojas que crea sola si no existen:

| Hoja | Contenido |
| --- | --- |
| `Participantes` | Una fila por persona: fecha, nombre y apellido, DNI, WhatsApp, mail, sigue el canal |
| `Padron` | Columna A con los DNIs de socios; C2 con la fecha de la última carga |

Configuración (una vez):

1. En [Google Cloud Console](https://console.cloud.google.com/) crear un proyecto y habilitar
   **Google Sheets API**.
2. Crear una cuenta de servicio y descargar su clave en formato JSON.
3. Crear una planilla vacía y **compartirla como Editor** con el mail de la cuenta de servicio.
4. Copiar el ID de la planilla (la parte de la URL entre `/d/` y `/edit`).
5. Completar los secrets (ver `.streamlit/secrets.toml.example`).

| Secret | Obligatorio | Para qué |
| --- | --- | --- |
| `admin_password` | Sí | Clave de `/admin` |
| `[sheets] spreadsheet_id` y `[gcp_service_account]` | Sí, para publicar | Guardar en Google Sheets |
| `link_canal` | No | Muestra el botón "Seguir el canal en WhatsApp" |
| `cierre` | No | Fecha y hora (Buenos Aires, `AAAA-MM-DD HH:MM`) en que se cierra la inscripción |

Sin credenciales de Google la app funciona en **modo prueba** guardando en `data/` (la página de
admin lo avisa). No publicar en ese modo: el disco de Streamlit Cloud se borra al reiniciar.

## Publicar en Streamlit Community Cloud

1. New app → este repo → *Main file path*: `app.py`.
2. En *Settings → Secrets* pegar los secrets.
3. Entrar a `/admin`, subir el padrón y tocar "Reemplazar padrón con este archivo".

## Correr local

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # completar los valores
streamlit run app.py
```

## Marca

Según el Brandbook CAP26: marrón principal `#4a2e15` (fondo), marrón secundario `#342011`
(paneles), dorado `#bea15e` (acentos y botones), escudo y logotipo en vector (`assets/logo_cap.svg`).
Tipografías web equivalentes: Playfair Display Italic (Awesome Serif), Oswald (Knockout) y Montserrat.

## Estructura

```
app.py                  navegación (formulario + admin)
vistas/formulario.py    sorteo público
vistas/admin.py         carga de padrón y descarga de participantes
core/contenido.py       textos del sorteo
core/validacion.py      normalización de DNI, lectura del padrón, validación de campos
core/almacenamiento.py  Google Sheets (y modo prueba local)
core/config.py          secrets, cierre y elección del almacenamiento
core/marca.py           colores, tipografías y componentes visuales
tests/                  pytest
```

## Tests

```bash
python -m pytest -q
```
