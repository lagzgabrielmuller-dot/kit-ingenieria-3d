# Escribir el informe en vivo en Google Docs

Procedimiento probado con un informe de 6 páginas: texto, fórmulas, tabla de 15 × 3, dos figuras y fuentes. El usuario vio el documento llenarse sección por sección mientras se armaba, en paralelo, el modelo 3D con **blender-en-vivo**. Leer esto antes de escribir en un Google Doc con el conector de Google Docs.

## Cuándo conviene

- El usuario quiere ver el informe mientras se escribe, y corregir sobre la marcha.
- No tiene Word, o el trabajo es grupal y se comparte por Google Drive.
- Hace falta entregar en Word o PDF: Google Docs lo descarga en esos formatos (Archivo > Descargar).

## Pasos

1. **Crear el documento** con `create_file` de Drive, con `contentMimeType: application/vnd.google-apps.document` y el título del informe.
2. **Abrirlo en el navegador del usuario.**
   - Si su Chrome tiene más de una cuenta de Google, el documento puede abrirse con la cuenta equivocada y no verse. Para forzar la cuenta, agregar `?authuser=CORREO` a la dirección.
   - Si el usuario ya abrió un documento en blanco pero el conector no lo encuentra (por ejemplo, con `search_files` filtrando por `createdTime`), seguramente lo creó con otra cuenta. Crear uno nuevo con la cuenta del conector y avisarle.
3. **Escribir sección por sección**, con un pedido por sección (o por dos secciones cortas) para que el usuario las vea aparecer.
   1. `read_doc`, para tener el `revisionId` y el `endIndex` del último párrafo.
   2. Escribir la sección en un texto con las marcas de `docs_bloques.py` (la portada, la introducción, un capítulo).
   3. `python docs_bloques.py texto seccion.txt --inicio <endIndex − 1> --rev <revisionId>`. Agregar `--doc-vacio` en la primera sección de un documento nuevo, y `--despues-de-lista` si el último párrafo es un ítem de lista.
   4. Mandar el JSON que imprime a `update_doc`, en `requests` y `writeControl`.
4. **Tablas al final.**
   - Cada tabla agranda mucho la respuesta de `read_doc`. En la prueba, una tabla de 15 × 3 la llevó de unos 70 KB a 370 KB.
   - Conviene escribir antes todo el texto, dejando el párrafo que presenta la tabla, e insertar las tablas en el último pedido: `python docs_bloques.py tabla --en <endIndex − 1 de ese párrafo> --filas filas.json --rev R --color-encabezado 0.99,0.89,0.78 --anchos 140,226,85`.
   - Si en el mismo pedido se agrega texto al final, ese texto va primero en la lista de `requests`, porque los índices más altos van antes.
5. **Figuras.**
   - `insertInlineImage` solo acepta una dirección que Google pueda leer. Lo que sí funcionó sin compartir nada en público:
     1. Subir la imagen (JPG de 1600 × 900, de unos 100 KB) con `create_file` de Drive.
     2. Drive la convierte en un documento de Google que contiene la imagen.
     3. Leer ese documento con `read_doc` y copiar `inlineObjects.*.imageProperties.contentUri`, que dura unos 30 minutos.
   - Después: `python docs_bloques.py figuras --datos figuras.json --rev R`, donde cada figura lleva el `startIndex` de su epígrafe y su `uri`. La imagen queda en su propio párrafo, pegada a su epígrafe.
   - Al terminar, preguntar al usuario si se mandan a la papelera los documentos temporales con las imágenes. No borrarlos sin su permiso. Las figuras del informe no se pierden: Docs guarda su propia copia de la imagen al insertarla (probado: después de mandar los temporales a la papelera, el informe siguió con sus dos figuras).
6. **Verificar.**
   - El texto: `read_file_content` de Drive. Devuelve Markdown corto, donde los superíndices aparecen como números comunes; no es un error.
   - Lo visual: exportar a PDF con `download_file_content` (`exportMimeType: application/pdf`), pasar las páginas a imágenes (`pdftoppm -r 45 -png`) y mirarlas en una sola hoja. Revisar títulos solos al pie de una página, tablas cortadas y figuras separadas de su epígrafe.

## Marcas del texto

Va un párrafo por línea; las líneas vacías se ignoran.

| Marca | Resultado |
|---|---|
| `TITULO: …` / `SUBTITULO: …` | Título y subtítulo del documento (`--color-titulo r,g,b` para darle color al título) |
| `# …`, `## …`, `### …` | Títulos 1, 2 y 3 con los estilos del documento, que aparecen en el índice |
| `- …` | Viñeta; varias seguidas forman una lista |
| `1. …` | Lista numerada |
| `$$ …` | Fórmula centrada |
| `EPIGRAFE: Figura 1. …` | Epígrafe centrado, en cursiva gris de 9,5 pt |
| `**negrita**`, `*cursiva*` | Negrita, cursiva |
| `10^{26}`, `ν_{e}` | Superíndice, subíndice |
| `[[texto|https://…]]` | Enlace |
| `695~700~km` | Espacio que no corta la línea entre el número y la unidad |

## Lo que resuelve el script (y por qué)

- **Índices en UTF-16.** Google Docs cuenta así; las letras con tilde y el espacio que no corta valen 1.
- **Herencia de estilos.** Un párrafo nuevo copia el del párrafo que se partió: la viñeta, la sangría, el espacio inferior y hasta el estilo de título. Por eso el script vuelve a poner el estilo de cada párrafo, devuelve el espacio al de su estilo y, con `--despues-de-lista`, saca la viñeta y la sangría.
- **Espacio entre párrafos.** Un documento nuevo trae 0 pt de espacio. El script pone 8 pt debajo de cada párrafo de texto y del último ítem de cada lista; los títulos usan el suyo.
- **Orden de los pedidos.** Primero se inserta todo el texto, después van los estilos, al final el espacio. Las tablas se llenan de la última celda a la primera, y las figuras se insertan de abajo hacia arriba.

## Errores frecuentes

| Problema | Causa | Solución |
|---|---|---|
| 400: `required revision ID does not match` | El documento cambió (lo editó el usuario o un pedido anterior) | Volver a leer con `read_doc` y rearmar el pedido con la revisión nueva; nunca sacar la protección |
| La sección nueva sale con viñetas | Se agregó después de un ítem de lista | `--despues-de-lista` |
| La imagen subida aparece como documento de Google | `create_file` convierte los JPG a documento si no se pide lo contrario | Para guardar el JPG tal cual, usar `disableConversionToGoogleType: true`. Para insertar figuras, esa conversión es justamente lo que se quiere |
| Un número largo cortado entre renglones | Espacio común entre el número y la unidad | `~` en el texto |
| `read_doc` devuelve un resultado enorme | Tablas o muchos párrafos | Insertar las tablas al final; con un documento grande, usar `docs_bloques.py indices lectura.json --buscar "Figura 1."` sobre la lectura guardada |
