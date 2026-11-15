---
name: video-calidad
description: "Control de calidad y exportación de videos con ffmpeg antes de entregarlos: resolución y cuadros por segundo, color BT.709 con etiquetas (rojos corridos al naranja), pantallas negras o congeladas, silencios, volumen en LUFS (EBU R128), costura de loops y hoja de contacto para revisar mirando cuadros. Arregla el volumen en dos pasadas y el color sin rehacer el render. Usar cuando se pida revisar, terminar, exportar o entregar un video, un render o recorrido de Blender, una animación, un fondo animado en loop o un clip para YouTube, redes o una exposición, o cuando un video se vea con colores raros, suene bajo o salte al repetirse."
---

# Control de calidad de video

Un video se da por terminado cuando pasa un chequeo que se puede correr, no cuando parece estar bien. `scripts/video_calidad.py` (Python 3.9+, solo biblioteca estándar, necesita `ffmpeg` y `ffprobe`) revisa, arregla y vuelve a revisar.

## Flujo

1. Exportar con los ajustes de [Exportar bien](#exportar-bien).
2. Revisar: `python scripts/video_calidad.py revisar VIDEO --perfil PERFIL --hoja --salida CARPETA`. Código 0: sin errores; 1: con errores; 2: no se pudo leer.
3. Corregir lo que marque (cada hallazgo trae el arreglo) y volver al paso 2.
4. Abrir `hoja.jpg` como imagen y mirarla: cortes, títulos legibles, tomas negras o quietas, colores.
5. Entregar con 0 errores y los avisos explicados (un fundido a negro a propósito es un aviso válido).

## La herramienta

| Subcomando | Qué hace |
|---|---|
| `revisar VIDEO` | Formato, color, contenedor, cuadros negros y congelados, silencios, volumen integrado y pico verdadero, costura del loop; informe `revision.md` y `revision.json`, y con `--hoja`, `hoja.jpg` con 12 cuadros rotulados |
| `audio VIDEO --lufs -14` | Normaliza el volumen en dos pasadas (`loudnorm` lineal) y copia el video sin recodificar |
| `color VIDEO --desde bt601` | Convierte a BT.709 y etiqueta un video ya exportado sin matriz (recodifica; `--gpu` usa NVENC) |
| `color VIDEO --desde bt709` | Solo etiqueta, sin recodificar (H.264 o HEVC que ya estaban en BT.709) |
| `demo` | Arma un video con fallas, lo revisa, lo arregla y lo vuelve a revisar: debe terminar en `DEMO OK` |

Opciones de `revisar`: `--ancho`, `--alto` y `--fps` exigen esos valores; `--loop` mide la costura; `--lufs` cambia el objetivo; `--rapido` saltea el escaneo de cuadros y volumen; `--gpu` decodifica con NVIDIA; `--json` imprime el informe en JSON. Sin `--salida`, el informe va a una carpeta temporal (la ruta se imprime al final).

| Perfil | Códec y píxel | Volumen (integrado) | Además |
|---|---|---|---|
| `youtube` | H.264, HEVC, AV1 o VP9; yuv420p o 10 bits | −14 LUFS ±1,5 LU; pico ≤ −1 dBTP | Índice al principio (faststart) |
| `presentacion` | H.264, yuv420p | −16 LUFS ±2 LU; pico ≤ −1 dBTP | Abre en cualquier compu del aula |
| `vertical` | H.264, yuv420p, 1080 × 1920 | −14 LUFS ±1,5 LU | Para redes |
| `wallpaper` | H.264, yuv420p | — | Mide la costura del loop |
| `libre` | — | — | Solo formato, color y escaneo |

## Exportar bien

### Color: BT.709 con etiquetas

Al pasar cuadros RGB (PNG, render de Blender, compositor propio) a yuv420p, ffmpeg usa la matriz BT.601 si no se le indica otra y no etiqueta el archivo. YouTube, los navegadores y los reproductores de Windows leen un video HD sin etiqueta como BT.709, así que los colores se corren. Medición con `h264_nvenc` y `libx264` (ffmpeg, noviembre de 2026):

| Color RGB original | Exportado sin matriz, visto en un reproductor | Con BT.709 y etiquetas |
|---|---|---|
| Rojo 255, 0, 0 | 255, 23, 0 (anaranjado) | 254, 0, 0 |
| Carmesí 178, 24, 44 | 190, 38, 42 | 178, 23, 43 |
| Verde 0, 255, 0 | 0, 215, 0 | 0, 254, 0 |

La vista previa no lo muestra: ffmpeg y PyAV leen un archivo sin etiqueta como BT.601 y lo ven bien. Por eso la verificación es la etiqueta (`revisar` la exige en HD), no el ojo.

```
ffmpeg -framerate 30 -i cuadros/%05d.png ^
  -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv" ^
  -c:v libx264 -preset slow -crf 18 ^
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -movflags +faststart salida.mp4
```

`setparams` hace falta: las versiones de ffmpeg de 2026 toman primarios y transferencia de cada cuadro y descartan las opciones `-color_primaries` y `-color_trc` (medido: sin `setparams` quedan "unknown"). En `^` va el corte de línea de Windows (`\` en Linux).

Recetas completas y probadas para YouTube, vertical 9:16 con fondo desenfocado y fondo animado en loop: [references/recetas-exportacion.md](references/recetas-exportacion.md).

### Codificador

| Opción | Cuándo |
|---|---|
| `libx264 -preset slow -crf 18` | Entrega final cuando importa el tamaño: mejor calidad por bit |
| `h264_nvenc -preset p6 -tune hq -rc vbr -cq 17 -b:v 0` | Rápido, con placa NVIDIA; archivos más pesados |
| `hevc_nvenc ... -tag:v hvc1` | Más liviano; no todos los programas lo abren |

Para YouTube, la ayuda oficial pide H.264 High, 4:2:0, `+faststart`, 2 cuadros B, GOP de medio segundo, AAC a 48 kHz y subir con los mismos cuadros por segundo de la fuente; como mínimo 8 Mb/s en 1080p hasta 30 cuadros/s, 12 Mb/s a 48–60, y 16 y 24 Mb/s en 1440p ([YouTube](https://support.google.com/youtube/answer/1722171?hl=en)). Para la entrega final con NVENC, NVIDIA sugiere `-preset p7 -tune hq -multipass fullres` ([NVIDIA](https://docs.nvidia.com/video-technologies/video-codec-sdk/13.1/ffmpeg-with-nvidia-gpu/index.html)). Wallpaper Engine recomienda H.264 en `.mp4` a 30 o 60 cuadros/s y no publica un bitrate.

En un tramo de 6 s de animación con grano a 2560 × 1440 y 60 cuadros/s, NVENC a CQ 17 pidió unos 74 Mb/s (VMAF 79,4) y libx264 slow a CRF 18, 34 Mb/s (VMAF 77,2). Activar `-spatial-aq` y `-temporal-aq` en NVENC no mejoró el VMAF (79,0). El grano y el ruido son lo que más bits consume: si el archivo queda pesado, bajar el grano antes que la calidad.

### Audio

- Objetivos: −14 LUFS integrados para YouTube y redes (Spotify lo documenta así con pico ≤ −1 dBTP; YouTube no publica su valor y −14 es lo que miden terceros), −16 LUFS para pasar en un aula; pico verdadero ≤ −1 dBTP para dejar margen a la compresión del audio ([Spotify](https://support.spotify.com/artists/article/loudness-normalization/), [filtro loudnorm](https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Audio/loudnorm.html)).
- `video_calidad.py audio VIDEO --lufs -14` mide y aplica ganancia lineal, sin comprimir la dinámica. Si avisa "modo dinámico", el pico no entraba con ganancia lineal: probar `--tp -2` o bajar picos en la mezcla.
- Tomas de distintas fuentes van al mismo volumen antes de mezclar; la música por debajo de la voz (unos 10 dB menos que la voz es un punto de partida, ajustar de oído).

### Loops sin salto

La costura (último cuadro → primero) tiene que parecerse a un paso normal entre cuadros. `revisar --perfil wallpaper` la mide: menos de 1,8 veces un paso normal está bien; más de 3 es un salto visible.

- **Mismo cuadro de inicio y fin** (por ejemplo, generación con primer y último cuadro): después sacar el último, porque si no, ese cuadro se ve dos veces y el loop "se traba". `revisar` lo detecta ("repite al primero").
- **Fundido cruzado** para cerrar un clip que no loopea. Para un clip de duración D y un fundido de X segundos, la salida dura D − X:

```
ffmpeg -i clip.mp4 -filter_complex "[0:v]split[a][b];[a]trim=start=X,setpts=PTS-STARTPTS[cuerpo];[b]trim=end=X,setpts=PTS-STARTPTS[cabeza];[cuerpo][cabeza]xfade=transition=fade:duration=X:offset=D-2X[v]" -map "[v]" ...
```

  (Reemplazar X, D y D − 2X por números: con D = 8 y X = 1, `trim=start=1`, `trim=end=1`, `duration=1:offset=6`. Probado: la costura pasó de 99,6 a 0,9 veces un paso normal.)
- **Ping-pong** (ida y vuelta con el filtro `reverse`) solo para movimientos que se pueden invertir (humo, agua, respiración); con caminatas o caídas se nota.
- La costura en un momento con poco movimiento.

## Revisión visual

- La hoja de contacto (`--hoja`) muestra 12 cuadros repartidos con su tiempo. Mirar que no haya tomas negras, cortes en mal lugar, deformaciones de la IA ni títulos cortados.
- Títulos: que se lean en la hoja achicada (si no se leen ahí, en un celular tampoco). Para video vertical de 1080 × 1920, dejar libres unos 240 px arriba, 660 abajo y 120 a los costados (más una franja a la derecha), donde las apps ponen botones y textos (medido por terceros sobre la plantilla de TikTok; verificar en la app de destino).
- Parpadeo de luz típico de los videos generados con difusión: `deflicker=s=5:m=am` antes de codificar.
- Para mirar un momento puntual: `ffmpeg -ss 12.5 -i VIDEO -frames:v 1 cuadro.png`.

## Errores frecuentes

| Error | Cómo se evita |
|---|---|
| Rojos anaranjados, verdes apagados en YouTube | Matriz BT.709 + `setparams` al exportar; `color --desde bt601` para lo ya hecho |
| Medidas impares con yuv420p | Ancho y alto pares |
| Cambiar los cuadros por segundo con `-r` y que cambie la velocidad | Interpolar (RIFE) o cambiar la tasa en la salida sin tocar la duración |
| El loop se traba un instante | Sacar el último cuadro repetido |
| El volumen salta entre tomas | Normalizar cada fuente antes de mezclar y el final con `audio` |
| Tarda en empezar en la web | `-movflags +faststart` |
| Confiar en la vista previa del programa | Revisar la etiqueta de color y la hoja de contacto |

## Verificación

`python scripts/video_calidad.py demo` tiene que terminar en `DEMO OK` (2 errores antes, 0 después). Para un video real, guardar el `revision.md` junto con la entrega.
