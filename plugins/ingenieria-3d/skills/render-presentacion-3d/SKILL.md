---
name: render-presentacion-3d
description: "Render de presentación de una máquina, pieza o conjunto en Blender con un solo comando: estudio con piso y fondo, tres luces escaladas al modelo, cámara encuadrada, foto principal y video girando 360° (turntable) en MP4 con color BT.709, desde un .blend o importando GLB, STL, OBJ o FBX. Usar cuando se pida mostrar un modelo 3D en una exposición, defensa o video del proyecto, hacer un render lindo de una pieza o máquina, una vuelta de 360°, o una imagen para la carátula o el informe."
---

# Render de presentación con Blender

`scripts/estudio_turntable.py` corre dentro de Blender y, sin tocar el archivo original, arma un estudio alrededor del modelo y saca una foto y un video que gira. Sirve para exposiciones, defensas, informes y videos de proyecto; el loop cierra solo (el último cuadro empalma con el primero).

## Uso

En segundo plano (desde PowerShell, envolver en `cmd /c "..."` para que no se pierda el `--`):

```
blender -b maquina.blend -P estudio_turntable.py -- SALIDA --previa
blender -b maquina.blend -P estudio_turntable.py -- SALIDA --motor cycles --muestras 128
blender -b --factory-startup -P estudio_turntable.py -- SALIDA --importar pieza.glb
```

| Opción | Por defecto | Para qué |
|---|---|---|
| `--segundos`, `--fps` | 8, 30 | Duración de la vuelta completa y cuadros por segundo |
| `--tam` | 1920x1080 | Resolución (ancho x alto; vertical: `1080x1920`) |
| `--motor` | eevee | `eevee` es rápido; `cycles` usa la placa (OptiX o CUDA) y da sombras y reflejos más reales |
| `--muestras` | 64 | Calidad del render (más = menos grano, más lento) |
| `--previa` | — | Mitad de tamaño, un cuadro de cada tres y menos muestras: para revisar encuadre y luz en segundos |
| `--contorno` | — | Líneas de contorno (Freestyle), aspecto de dibujo técnico |
| `--altura` | 20 | Ángulo de la cámara sobre el horizonte, en grados |
| `--solo COLECCION` | todo lo visible | Mostrar solo una parte del conjunto |
| `--importar ARCHIVO` | — | GLB, STL (se toma en mm), OBJ o FBX en lugar del `.blend` |
| `--sin-video` | — | Solo la foto |

Deja en `SALIDA`: `foto.png` (cuadro 1), `cuadros/0001.png…`, `turntable.mp4` (H.264, BT.709 etiquetado, inicio rápido) y `estudio.txt` con lo que se usó. Para el video hace falta `ffmpeg` en el PATH o en la variable `FFMPEG`; sin ffmpeg quedan los cuadros PNG.

## Cómo arma el estudio

- **Piso y fondo** grises, del mismo tono, para que no se vea el horizonte.
- **Tres luces de área** (principal, relleno y contraluz) con potencia proporcional al tamaño del modelo, así una pieza de 50 mm y una planta de 20 m salen con la misma exposición.
- **Cámara de 50 mm** a 35° del frente y `--altura` grados de elevación, a la distancia justa para que el modelo entre en todo el giro (usa el radio horizontal, que no cambia al girar, y el alto proyectado).
- **Giro** con un driver `2*pi*(frame-1)/N` sobre un pivote en el centro: no depende de la API de animación, que cambió en Blender 5.0.
- Color con la vista AgX y más contraste (Punchy) cuando la versión lo trae; en EEVEE prende el trazado de rayos si existe.

## Flujo recomendado

1. Antes, controlar el modelo con **blender-verificacion** (medidas y errores).
2. `--previa` y mirar `foto.png`: encuadre, luz, que no falte ninguna pieza.
3. Final: `--motor cycles --muestras 128` para la entrega, o EEVEE si no hay tiempo.
4. Revisar el video con **video-calidad** (`--perfil presentacion --loop`): sin errores y con la costura cerca de 1 paso normal.
5. Usarlo en la exposición (**exposicion-oral**) en loop mientras se habla, o la foto en la carátula.

## Errores frecuentes

| Síntoma | Causa | Arreglo |
|---|---|---|
| El modelo sale diminuto o gigante al importar | Unidades: el STL se toma en mm; el GLB viene en metros | Importar el formato correcto o escalar el modelo antes |
| Falta una pieza | Está oculta en el render o en otra colección | Revisar el ojo y la cámara de cada objeto, o usar `--solo` |
| Todo blanco o lavado | Materiales muy claros con mucha luz | Bajar `--muestras` no cambia la luz: oscurecer los materiales o usar `--motor cycles` |
| Grano en las superficies | Pocas muestras (en la previa es normal) | Subir `--muestras` |
| El video no se generó | No hay ffmpeg | Instalar ffmpeg o definir `FFMPEG`; los cuadros quedan en `cuadros/` |

## Verificación

`blender -b --factory-startup -P estudio_turntable.py -- demo CARPETA` arma una máquina simple de cuatro piezas, hace la previa (EEVEE, 640 × 360, 4 s) y tiene que terminar en `DEMO OK`. Medido con Blender 5.2.3 en una RTX 4070 SUPER: 4 s en total; el video pasó **video-calidad** sin errores, con BT.709 y la costura del loop a 1,02 veces un paso normal.
