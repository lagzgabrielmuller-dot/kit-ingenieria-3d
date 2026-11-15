---
name: progreso-en-vivo
description: "Tablero de progreso en vivo para trabajos largos: una página HTML que se actualiza sola mientras Claude trabaja, con el plan y sus pasos, el paso actual, las últimas imágenes (renders, vistas del modelo 3D, hojas de contacto), el borrador del texto que se va escribiendo, las preguntas para el usuario y la actividad. Usar cuando un trabajo tenga varios pasos (informe, modelo 3D, video, código, cálculos) y el usuario quiera ver cómo avanza, corregir sobre la marcha o dejar la pantalla mirando el progreso, o cuando pida 'mostrame cómo vas', 'quiero ver el avance' o 'no quiero que me lo entregues terminado sin verlo'."
---

# Tablero de progreso en vivo

Entregar todo terminado y que falte "una cosita" obliga a rehacer. `scripts/progreso.py` (Python 3.9+, solo biblioteca estándar) arma una página que el usuario deja abierta, por ejemplo en el segundo monitor, y que muestra el trabajo mientras se hace: así corrige el rumbo en el paso 2 y no al final.

## Cómo se usa

```
python progreso.py init "Informe del TP5" --plan "Consigna y datos|Cálculos|Gráficos|Redacción|Revisión" --carpeta TRABAJO --abrir
python progreso.py paso 1 --estado hecho --nota "datos de la placa: 4 kW, 1450 rpm"
python progreso.py imagen vistas/hoja_vistas.png --titulo "Modelo: frente, lateral, planta, iso"
python progreso.py texto borrador.md --titulo "Informe (borrador)"
python progreso.py pregunta "¿La cupla va en N·m o en kgm?"     (y después: responder)
python progreso.py fin --nota "entregado en PDF"
```

| Comando | Qué hace |
|---|---|
| `init "Título" --plan "A\|B\|C" [--carpeta] [--abrir]` | Crea `progreso.html` y la carpeta `.progreso/`, marca el tablero como activo y lo abre en el navegador |
| `paso N --estado en_curso\|hecho\|error\|pendiente [--nota]` | Actualiza un paso; al terminar uno, el siguiente pasa a "en curso" |
| `imagen RUTA [--titulo]` | Agrega una imagen a la galería (guarda las últimas 12; clic para agrandar) |
| `vigilar DIR` (o `init … --vigilar DIR`) | Cada imagen nueva que aparece en DIR (renders, vistas, gráficos) se suma sola al tablero; `vigilar --quitar` lo corta |
| `texto ARCHIVO` o `--texto "..."` | Muestra el borrador con Markdown simple (títulos, listas, negrita, código) |
| `pregunta "..."` / `responder` | Destaca en amarillo lo que se necesita del usuario / lo saca |
| `nota "..."` | Agrega una línea a la actividad |
| `fin`, `abrir`, `estado`, `demo` | Cerrar, volver a abrir, ver el estado, probar |

La página se refresca cada 1,5 s sin recargarse (no pierde el scroll). Funciona abierta como archivo local, sin servidor ni internet. Sin `--carpeta`, los comandos usan el tablero activo (guardado en `~/.progreso_activo`). El estado queda en `.progreso/`, que trae su propio `.gitignore`: si el tablero está dentro de un repositorio, no se sube.

## Qué mostrar en cada tipo de trabajo

| Trabajo | En cada paso |
|---|---|
| Informe o TP | `texto` con la sección recién escrita; los números y fórmulas en una `nota` del paso |
| Modelo 3D | `init … --vigilar <carpeta de renders>` y guardar ahí las vistas después de cada pieza (**blender-verificacion** arma la hoja de 4 vistas): aparecen solas |
| Video o render | `imagen` de la hoja de contacto o de un cuadro de la previa (**video-calidad**, **render-presentacion-3d**) |
| Cálculos o código | `nota` con el resultado de cada verificación y `texto` con la tabla de resultados |
| Planos | `imagen` del PDF o PNG del plano en cada revisión |

Reglas:
- El plan va al principio, con pasos chicos (4 a 8) que se puedan mostrar.
- Cada paso que produce algo visible deja una imagen o un texto: el tablero tiene que mostrar el trabajo, no solo decir "listo".
- Si hace falta una decisión del usuario, `pregunta` y seguir con lo que no dependa de esa respuesta.
- Al terminar, `fin`: el tablero queda como registro de cómo se hizo.

## Con Claude Code: actividad automática

Un hook `PostToolUse` agrega a la actividad cada archivo que Claude edita, cada comando y cada llamada a un servidor MCP (por ejemplo, Blender), y suma las imágenes nuevas de la carpeta vigilada, sin que Claude tenga que acordarse. Solo anota si hay un tablero activo con cambios en las últimas 12 h, tapa claves y tokens (`--clave ***`, `API_KEY=***`) y nunca frena ni hace fallar la sesión. En `~/.claude/settings.json`:

```json
"hooks": {
  "PostToolUse": [
    { "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash|mcp__.*",
      "hooks": [ { "type": "command", "command": "python RUTA/progreso.py hook", "timeout": 10 } ] }
  ]
}
```

En Windows, la ruta con barras `/` (Claude Code corre los hooks con Git Bash si está instalado).

## Otras formas de ver el trabajo en vivo

- En la app de Claude, un documento de Claude se llena sección por sección a la vista y se puede comentar mientras se escribe; un documento de Google Docs (con su conector) también se ve crecer en el navegador.
- Con Blender abierto y conectado por MCP (**conectar-programas-cad**), cada cambio aparece en la ventana de Blender en el momento.

## Verificación

`python progreso.py demo` arma un tablero de prueba (plan, paso hecho, imagen, borrador, pregunta) y tiene que terminar en `DEMO OK`. Probado en Chrome sin errores de JavaScript.
