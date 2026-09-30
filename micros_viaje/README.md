# Micros gratis para socios: inscripción + reporte de inscriptos

Todo corre en Google (Forms + Sheets + Apps Script), no hace falta servidor.

- **Formulario** con: Nombre y apellido, DNI (solo números, 7 u 8 dígitos), Teléfono de contacto y Mail de contacto (con validación de formato).
- **Planilla** con dos hojas: las respuestas del formulario y `Padron`, con el padrón de socios activos.
- **Reporte web**: es un link para compartir con el presidente y el tesorero. Cruza las respuestas con el padrón por DNI y muestra:
  - total de inscriptos (se cuenta una vez por DNI, aunque se anote dos veces),
  - socios inscriptos **con cuota al día**,
  - socios inscriptos **sin cuota al día**,
  - inscriptos que **no figuran en el padrón**,
  - inscripciones por día y listado filtrable (nombre, DNI, nro de socio, estado).

  Se actualiza solo cada 1 minuto y también con el botón "Actualizar". El teléfono y el mail no se muestran en el reporte: quedan solo en la planilla.

## Puesta en marcha (unos 10 minutos)

1. **Crear la planilla.** En Google Drive, crear una hoja de cálculo nueva, por ejemplo "Micros socios – Inscripciones".
2. **Pegar el código.** En la planilla: *Extensiones > Apps Script*.
   - Reemplazar el contenido de `Código.gs` por el de [`Codigo.gs`](Codigo.gs).
   - Hacer clic en *+ > HTML*, llamarlo **`Reporte`** (exacto, sin `.html`) y pegar el contenido de [`Reporte.html`](Reporte.html).
   - Revisar el bloque `CONFIG` al principio de `Codigo.gs` (título, `CUPO` de asientos, `CLAVE_ACCESO`) y guardar.
3. **Crear el formulario.** En el editor, elegir la función `crearFormulario` y darle a *Ejecutar*. Google pide permisos la primera vez; aceptarlos.
   - Se crea el Form vinculado a la planilla, la hoja de respuestas y la hoja `Padron` con los encabezados.
   - El link del formulario para publicar aparece en el *Registro de ejecución*. También se ve desde la planilla con el menú **Micros > Ver links**.
4. **Cargar el padrón.** En la hoja `Padron`, pegar los socios activos debajo de los encabezados:

   | DNI | Nombre y apellido | Nro de socio | Cuota al día |
   |---|---|---|---|
   | 30123456 | Juan Pérez | 1234 | Sí |
   | 28.765.432 | María Gómez | 5678 | No |

   - El DNI puede ir con o sin puntos.
   - En "Cuota al día" se toman como **al día**: `Sí`, `Si`, `X`, `OK`, `Al día`, `Pagada` o una casilla de verificación tildada. Cualquier otro valor, o la celda vacía, cuenta como **sin cuota al día**.
   - Las columnas se reconocen por el nombre del encabezado, no por la posición. Solo son obligatorias **DNI** y **Cuota al día**.
   - Para actualizar el padrón durante la inscripción, alcanza con volver a pegarlo: el reporte lo toma en el momento.
5. **Publicar el reporte.** En Apps Script: *Implementar > Nueva implementación > tipo: App web*.
   - *Ejecutar como*: **Yo**.
   - *Quién tiene acceso*: **Cualquier persona**. Así el presidente y el tesorero lo abren sin permisos extra. Si todos tienen cuenta de Google, también sirve "Cualquier persona con cuenta de Google".
   - Copiar la URL que termina en `/exec` y compartirla. Si se configuró `CLAVE_ACCESO`, agregar `?k=LA_CLAVE` al final del link. Sin la clave, el reporte no abre.

> **Privacidad:** el reporte muestra nombres y DNI de los inscriptos. Se recomienda completar `CLAVE_ACCESO` y compartir el link solo con el presidente y el tesorero.

## Cambios posteriores

- Si se modifica `Codigo.gs` o `Reporte.html`, hay que actualizar la implementación: *Implementar > Gestionar implementaciones > editar (lápiz) > Versión: Nueva versión*. Así la URL del reporte no cambia.
- Para cerrar la inscripción, en el Form desactivar *Respuestas > Aceptando respuestas*.
- Los avisos amarillos arriba del reporte indican problemas de datos, por ejemplo que falta la hoja `Padron` o la columna de cuota.
