---
name: visor-3d-interactivo
description: "Visor 3D interactivo en una sola página HTML con three.js, donde el modelo se rota, se acerca y se recorre con el mouse o el dedo, con capas que se prenden y apagan, vistas guiadas, etiquetas, datos de cada equipo al hacer clic y animaciones (cintas, motores, vehículos, operarios). Usar cuando se pida ver en 3D una planta, instalación, máquina o pieza, una maqueta o simulación 3D, algo 'que se pueda mover con el cursor', o mostrar en el navegador un modelo GLB o STEP."
---

# Visor 3D interactivo (three.js)

Partir siempre de `plantilla/visor.html` (en la carpeta de esta skill): ya trae cámara orbital, luces y sombras, piso con grilla, panel de capas con botón "solo", vistas con transición suave, etiquetas, panel de datos al hacer clic, animación con pausa y velocidad, captura PNG, pantalla completa y diseño que anda en el celular.

## Cómo adaptarla

La plantilla tiene cuatro secciones; normalmente solo se editan la 1 y la 3.

1. **Datos del proyecto**: título y subtítulo.
2. **Motor del visor**: no hace falta tocarlo. Funciones disponibles:
   - `capa(nombre)` → grupo con su casilla en el panel.
   - `caja([x, y, z], color, capa, [px, py, pz], 'datos')` → apoyada en el punto (centro de la cara inferior).
   - `cilindro(r, largo, color, capa, [px, py, pz], 'x' | 'y' | 'z', 'datos')` → centrado en el punto.
   - `operario(capa, [x, 0, z], 'Nombre')`, `etiqueta('texto', objeto, [dx, dy, dz])`.
   - `vista('Nombre', [posición de la cámara], [punto mirado])`.
   - `animar((t, dt) => { ... })` → se llama en cada cuadro; `dt` en segundos (ya incluye la velocidad elegida).
   - `await cargarGLB('modelo.glb', capa, { posicion, escala, rotacionY })` → modelos de la skill modelado-3d-cad.
   - `material(color, {...})` para materiales a medida.
3. **Escena del proyecto**: reemplazar el ejemplo de la cinta transportadora por el modelo real.
4. **Arranque**: encuadra la cámara y las sombras al tamaño del modelo.

## Reglas del modelo

- **Medidas reales en metros** (1 unidad = 1 m), Y hacia arriba. Si los datos vienen en mm, dividir por 1000.
- Una capa por sistema: estructura, equipos, cañerías, eléctrico, circulación, personal, etc.; nombres iguales a los de los planos y la memoria.
- Cada equipo con su texto de datos (código, nombre, potencia, capacidad, medidas), el mismo que en la lista de equipos.
- Animar lo que se mueve de verdad: cintas y rodillos, tornillos, ventiladores, tambores, camiones que entran, descargan y salen, flujos de material. Velocidades reales o proporcionales.
- Mostrar operarios en sus puestos, zonas de circulación y accesos cuando sea una planta.
- Si piden que sea "lo más completo posible": más detalle real (barandas, escaleras, tableros, protecciones, señalización), sin dejar de ser legible.
- Si ya hay un visor del proyecto, mejorarlo sobre ese archivo en lugar de rehacerlo.

## Entrega

- Como página publicada (artefacto) o archivo `.html`: las librerías vienen de jsDelivr (permitido en los artefactos de Claude).
- **Para abrir sin internet**: copiar `three/build/three.module.js` y la carpeta `three/examples/jsm` (de `npm install three@0.170.0`) a `./lib`, cambiar las dos rutas del `importmap` por `./lib/three.module.js` y `./lib/jsm/`, y entregar la carpeta en un `.zip` con instrucciones ("descomprimir y abrir `index.html` con Chrome, Edge o Firefox").
- Modelos GLB pesados: cargarlos desde un archivo al lado del HTML; los livianos se pueden incrustar en base64. Apuntar a menos de 15 MB en total.
- Rendimiento: `InstancedMesh` o `mergeGeometries` para cientos de piezas iguales; sombras solo del sol.

## Verificación

Abrir el visor en un Chromium sin pantalla (Playwright) antes de entregar. Sin internet, servir una copia con el `importmap` apuntando a un `three` instalado con npm (`python3 -m http.server` en esa carpeta). Revisar:
- La consola, sin errores.
- Capturas de dos o tres vistas: nada flotando, nada metido dentro de otra cosa, sombras y etiquetas en su lugar.
- Que los botones de capas, "solo", vistas y animación hagan lo que dicen.
