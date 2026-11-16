---
name: blender-en-vivo
description: "Control de un Blender abierto paso por paso para que el usuario vea el modelo 3D armándose en su pantalla (por ejemplo en el segundo monitor) mientras Claude trabaja: un corredor dentro de Blender ejecuta los scripts que van llegando a una cola, avisa en un log si salieron bien o con error, y saca capturas de la vista 3D para revisar el resultado. Trae recetas probadas en Blender 5.2 para vista de cámara, materiales emisivos animados, halos, brillo en el compositor, cortes con booleanos, etiquetas con líneas guía, render y animación. Usar cuando el usuario quiera ver en tiempo real cómo se modela algo en Blender, pida 'hacelo en vivo', 'quiero ver cómo lo armás', 'mostralo en la otra pantalla', o cuando Claude controle Blender desde la app con una terminal (sin servidor MCP)."
---

# Blender en vivo

Modelar todo de una vez y mostrar el render final esconde el proceso: si algo no le gusta al usuario, hay que rehacer. Con este método Blender queda abierto en la pantalla del usuario y cada paso aparece apenas se ejecuta: la esfera, el material, la luz, el corte, las etiquetas. El usuario corrige en el paso 2 y no al final.

Funciona desde Claude Code o desde cualquier lugar que pueda ejecutar comandos en la computadora (por ejemplo, la app de Claude con una terminal remota). No necesita un servidor MCP: si hay uno conectado (**conectar-programas-cad**), también sirve, y estas recetas valen igual.

## Cómo funciona

```
Claude ──vivo.py enviar paso.py──▶ cola/ ──▶ blender_vivo.py (dentro de Blender) ──▶ escena
   ▲                                                        │
   └──────────── blender.log ("ok" / "ERROR") y capturas/ ◀─┘
```

- `scripts/blender_vivo.py` corre dentro de Blender: un temporizador mira `cola/` cada 0,4 s y ejecuta los `.py` de a uno, en orden. Cada evento queda en `blender.log`, y el paso ya ejecutado pasa a `hechos/`.
- `scripts/vivo.py` (Python 3.9+, solo biblioteca estándar) es el lado de Claude: abre Blender con el corredor, pone cada paso en la cola de forma atómica, espera el `ok` o el `ERROR`, y pide capturas.

## Uso

```
python vivo.py --base CARPETA iniciar --blender "C:\...\blender.exe" [--escena modelo.blend] [--ventana=-1920,0,1920,1080 --maximizar]
python vivo.py --base CARPETA enviar 01_vista.py        (o: enviar --codigo "bpy.ops.mesh.primitive_uv_sphere_add()")
python vivo.py --base CARPETA captura vista_paso01 --demora 6
python vivo.py --base CARPETA estado
python vivo.py --base CARPETA cerrar [--guardar modelo.blend]
python vivo.py demo                                      (prueba el protocolo sin Blender)
```

- `--base` va antes del comando. Si se omite, se usa la variable `BLENDER_VIVO_BASE` o `~/blender_vivo`. Conviene una carpeta por trabajo.
- `--ventana=X,Y,ANCHO,ALTO` ubica Blender en otro monitor (solo Windows). Por ejemplo, un monitor de 1920 × 1080 a la izquierda del principal empieza en X = −1920. Con números negativos hay que escribir el `=`, porque si no el −1920 se lee como otra opción.
- Sin `--escena`, `iniciar` crea un `inicio.blend` vacío en la base y abre ese: con un archivo en la línea de comandos, Blender no muestra el cartel de bienvenida que tapa la vista.
- `enviar` devuelve 0 si el paso salió bien y 1 si dio error, e imprime el traceback.
- `cerrar` cierra el Blender que abrió `iniciar` (guarda antes si se pasa `--guardar`).
- `captura` deja un PNG en `capturas/`. Abrir esa imagen (con la herramienta de lectura de imágenes) es la forma de ver lo mismo que ve el usuario.

Dentro de cada paso quedan definidos `bpy`, `BASE`, `VENTANA`, `AREA` y `REGION` (la primera vista 3D), `log(texto)` (escribe en el log) y `captura(nombre, demora=6.0)`.

## Método

1. **Plan visible.** Partir el modelo en 5 a 10 pasos que cambien algo a la vista: base y cámara, forma, material, detalles, iluminación o brillo, cortes, etiquetas, render y animación. Contárselo al usuario en una línea.
2. **Primer paso: la vista.** Cámara, sombreado en modo render y vista desde la cámara, para que el usuario vea el resultado final desde el principio. Receta 1 en `references/recetas-blender.md`.
3. **Un paso, un archivo.** Cada `.py` hace una sola cosa y la deja visible. Si el paso puede repetirse, que primero borre lo que creó la vez anterior: así un paso corregido se vuelve a mandar sin duplicar objetos.
4. **Mirar antes de seguir.** Mandar el paso, leer el `ok` o el error, pedir `captura` y mirarla. Si el color quedó lavado, la forma rara o algo tapado, corregir con un paso chico de ajuste y no seguir apilando.
5. **Renders para entregar.** `bpy.ops.render.render(write_still=True)` dentro de un paso guarda la imagen final. Congela la interfaz unos segundos: avisar al usuario.
6. **Cierre.** Guardar el `.blend`, dejar la animación reproduciéndose si la hay, y decir dónde quedaron los archivos.

## Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `poll() failed, context is incorrect` | Operadores de la vista 3D sin contexto | `with bpy.context.temp_override(window=w, screen=w.screen, area=a, region=r):` con la región `WINDOW` del área |
| Colores lavados, casi blancos | AgX comprime los emisivos muy fuertes | Emisión con `Strength` entre 1 y 1,5 y el brillo con el nodo Glare del compositor |
| `modifiers.new()` devuelve `None` | Modificador de malla en un objeto curva (por ejemplo, Displace) | Convertir la curva a malla o lograr la irregularidad con varias curvas |
| Booleano con caras rotas o faltantes | Caras coplanares entre el objeto y el cortador (una esfera UV tiene aristas sobre x = 0, y = 0 y z = 0) | Girar la malla un ángulo mínimo antes del booleano |
| No existe `scene.node_tree` | Desde Blender 5.0 el compositor es un grupo de nodos | `scene.compositing_node_group = grupo`, con un socket de salida `Image` (receta 4) |
| Líneas guía de las etiquetas cortadas | La línea pasa por adentro del objeto | Poner las etiquetas por delante, del lado de la cámara (receta 6) |
| La cola no avanza | Blender no tiene el corredor o la base no es la misma | `vivo.py estado`; volver a cargar `blender_vivo.py` en Blender |
| Error de motor de render | El nombre del motor cambió entre versiones | Leer los nombres válidos en `bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items` (en 5.2, EEVEE es `BLENDER_EEVEE`) |

## Seguridad

El corredor ejecuta cualquier `.py` que aparezca en `cola/`, con los permisos del usuario. Por eso la carpeta base tiene que ser privada (no compartida ni sincronizada) y se borra o se cierra Blender al terminar. Este método no deja nada corriendo en segundo plano: el corredor vive mientras Blender esté abierto.

## Recetas y ejemplo completo

`references/recetas-blender.md` tiene los pasos probados para:
- preparar la vista;
- un material emisivo animado con drivers;
- un halo que mira a la cámara;
- el brillo del compositor en 5.x;
- un corte con booleanos y caras de corte de otro color;
- etiquetas con líneas guía;
- render, captura y animación.

Al final trae el ejemplo completo del Sol: fotosfera, manchas, cromosfera, corona, protuberancias, el corte con núcleo, zona radiativa y zona convectiva, y las etiquetas. Leerlo antes de un modelo con materiales emisivos, cortes o rótulos.

Skills relacionadas:
- **blender-verificacion**: medidas y cuatro vistas para controlar la forma.
- **render-presentacion-3d**: vueltas de cámara y renders lindos.
- **progreso-en-vivo**: tablero con el plan y las capturas (`init --vigilar CARPETA/capturas`).
- **informe-tecnico**: el informe que acompaña al modelo, escrito en vivo.

## Verificación

- `python vivo.py demo` prueba la cola, el aviso de error y la captura con un corredor simulado, y tiene que terminar en `DEMO OK`.
- Con Blender real (5.2.3, Windows 11), el método se usó para modelar el Sol en vivo en el segundo monitor mientras se escribía el informe: 12 pasos, dos renders y la animación.
