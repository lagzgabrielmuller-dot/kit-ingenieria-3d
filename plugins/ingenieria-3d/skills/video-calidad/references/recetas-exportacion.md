# Recetas de exportación probadas

Leer cuando haya que exportar el video final desde cuadros PNG (render de Blender, compositor propio, generación con IA) o desde un video sin pérdida. Las tres recetas se probaron con ffmpeg y `libx264` sobre un video de prueba, y las tres salidas pasaron `video_calidad.py revisar` con el perfil correspondiente sin errores ni avisos.

En todas, `VF709` es la conversión de color correcta (ver la skill):

```
VF709 = scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv
ETIQUETAS = -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv
```

En Windows (cmd), la continuación de línea es `^`; en PowerShell, conviene escribir todo en una línea o pasar el filtro por archivo con `-filter_complex_script`.

## YouTube o una exposición (16:9)

```
ffmpeg -framerate 30 -i cuadros/%05d.png -i mix.wav -vf "VF709" ^
  -c:v libx264 -preset slow -crf 18 -profile:v high -bf 2 -g 15 ETIQUETAS ^
  -c:a aac -b:a 384k -ar 48000 -shortest -movflags +faststart youtube.mp4
```

- `-g` igual a la mitad de los cuadros por segundo y 2 cuadros B, como pide la ayuda de YouTube; AAC a 48 kHz.
- Con placa NVIDIA, en lugar de libx264: `-c:v h264_nvenc -preset p7 -tune hq -multipass fullres -rc vbr -cq 18 -b:v 0` (más rápido, archivos más pesados).
- Antes, normalizar el audio: `video_calidad.py audio` sobre el video, o `loudnorm` en dos pasadas sobre `mix.wav`.

## Vertical 9:16 para redes, con el mismo video desenfocado de fondo

```
ffmpeg -framerate 30 -i cuadros/%05d.png -i mix.wav -filter_complex ^
  "[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:2[fondo];[b]scale=1080:-2:flags=lanczos[frente];[fondo][frente]overlay=(W-w)/2:(H-h)/2,VF709[v]" ^
  -map "[v]" -map 1:a -c:v libx264 -preset slow -crf 18 -profile:v high ETIQUETAS ^
  -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart vertical.mp4
```

- El video horizontal queda centrado y el fondo es el mismo video agrandado y desenfocado: no hay franjas negras.
- Textos y logos lejos de los bordes de arriba y abajo, donde las apps ponen botones (ver la skill).

## Fondo animado en loop (Wallpaper Engine)

```
ffmpeg -framerate 30 -i loop/%05d.png -vf "VF709" ^
  -c:v libx264 -preset slow -crf 17 -profile:v high ETIQUETAS -an -movflags +faststart wallpaper.mp4
```

- H.264 en `.mp4`, como recomienda Wallpaper Engine; sin audio (`-an`) salvo que el fondo lo use.
- Antes de exportar, cerrar el loop (fundido cruzado o primer cuadro = último, sacando el repetido) y revisar con `video_calidad.py revisar --perfil wallpaper`.
- A 60 cuadros/s se ve más fluido, pero la compu trabaja más para decodificarlo; 30 alcanza para movimientos lentos.
