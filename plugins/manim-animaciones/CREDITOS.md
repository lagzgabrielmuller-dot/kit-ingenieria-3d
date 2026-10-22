# Créditos: Animaciones y video (Manim, FFmpeg, Remotion)

Para presentaciones animadas y videos explicativos de temas técnicos.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| Adithya S Kolavi, [adithya-s-k/manim_skill](https://github.com/adithya-s-k/manim_skill) | MIT | `cef045011722d285692e3381d12d4d637da56e18` |
| Yusuke Miyashita, [yusuke710/manim-skill](https://github.com/yusuke710/manim-skill) | MIT | `a0048d9e265499038f34a9aa58ff16d306b5034c` |
| Major AI Skills contributors, [alivirgo/Major-AI-Skills](https://github.com/alivirgo/Major-AI-Skills) | MIT | `17fb963bd185e23367d23b22f2ea5f3688d27f40` |

## Skills (6)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `ffmpeg` | Transcode and compress video with FFmpeg, inspect streams with ffprobe, build filtergraphs and HLS outputs, and diagnose codec or hardware-encoder failures. |
| `manim-composer` | Trigger when: (1) User wants to create an educational/explainer video, (2) User has a vague concept they want visualized, (3) User mentions "3b1b style" or "explain… |
| `manim-skill` | Create mathematical animations with Manim Community Edition(manimce), with optional TTS voiceover and synced subtitles. Generates distinctive, production-grade… |
| `manimce-best-practices` | Trigger when: (1) User mentions "manim" or "Manim Community" or "ManimCE", (2) Code contains `from manim import *`, (3) User runs `manim` CLI commands, (4) Working… |
| `manimgl-best-practices` | Trigger when: (1) User mentions "manimgl" or "ManimGL" or "3b1b manim", (2) Code contains `from manimlib import *`, (3) User runs `manimgl` CLI commands, (4) Working… |
| `remotion` | Create React video compositions with Remotion, parameterize timelines with props, and configure CLI or server-side rendering. |

## Qué necesitan

- `pip install manim` (y LaTeX para fórmulas) o ManimGL. FFmpeg.
- Voz en off de `manim-skill`: el paquete local `kokoro` (`uv add "kokoro>=0.9.4" soundfile`); sin él, la skill hace el video mudo.
- Remotion: Node.js; su licencia es gratuita para personas y empresas chicas.

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla. La voz en off se genera en la propia compu (sin servicios externos).
