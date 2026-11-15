---
name: equipo-de-modelos
description: "Trabajar con varios modelos de IA a la vez: Claude lidera y hace el trabajo, y otros modelos (guías: Codex o ChatGPT, Gemini, otra sesión de Claude, modelos locales de Ollama o cualquiera de OpenRouter) revisan, proponen alternativas o dan una segunda opinión, de a uno o en paralelo, con un informe para comparar. Trae guias.py (estado, preguntar, consejo y claves para PAL) y explica PAL y los subagentes de Claude Code. Usar cuando el usuario pida que trabajen varios modelos o varias IA, una segunda opinión, un consejo o consenso de modelos, comparar respuestas, sumar Gemini u otro modelo, usar un modelo local, o cuando un resultado importante merezca un control independiente antes de entregarlo."
---

# Equipo de modelos: Claude lidera, los guías revisan

Un solo modelo se equivoca sin darse cuenta; otro modelo, que no vio la conversación, encuentra errores que el primero no ve. El reparto es fijo: **Claude planifica, escribe, decide y verifica**; los guías leen, critican y proponen. Para el detalle de Codex, ver **trabajar-con-codex**.

## Quién hace qué

| Guía | Para qué conviene | Costo y límites |
|---|---|---|
| `codex` (Codex CLI, cuenta de ChatGPT) | Revisión independiente de cálculos, código y diseños; segunda opinión fuerte | Cupo del plan de ChatGPT |
| `gemini` (Gemini CLI) | Documentos largos, mucho contexto, otra familia de modelos | Gratis con cuenta personal de Google: 60 pedidos por minuto y 1000 por día (README de google-gemini/gemini-cli) |
| `gemini-api:<modelo>` (API de Gemini) | Lo mismo que Gemini sin instalar nada | Clave de Google AI Studio, con el límite de su plan gratuito; `guias.py estado` lista los modelos |
| `claude:opus`, `claude:haiku` (otra sesión de Claude Code) | Una mirada sin el sesgo de la charla actual: `opus` para lo difícil, `haiku` para lo rápido | El mismo cupo que Claude |
| `ollama:<modelo>` (local) | Borradores, resúmenes, textos y datos privados que no deben salir de la compu | Gratis, pero ocupa la GPU; más flojo en cálculos |
| `openrouter:<id>` | Cientos de modelos con una sola clave | Los `:free` no cobran: 20 pedidos por minuto y 50 por día (1000 por día después de comprar 10 créditos) (openrouter.ai/docs, Limits) |

## Reglas

- **Un solo escritor.** Los guías nunca modifican archivos: Codex corre con `--sandbox read-only`, Gemini con `--approval-mode plan` y Claude con `--permission-mode plan`, que son los modos de solo lectura de cada uno.
- **Las claves van en la cabecera o en la configuración, nunca en la URL ni en el comando.** `pal-clave` las pide ocultas.
- **Nada secreto.** No mandar claves, contraseñas, datos personales de otras personas ni datos de clientes. `guias.py` tapa claves y tokens con `***` antes de enviar y se niega a adjuntar `.env`, claves o credenciales, pero qué se manda lo decide Claude.
- **Un guía opina, no decide.** Si hay diferencias en números, se recalcula con código; no se promedia ni se elige por mayoría.
- **Decir de dónde viene cada cosa** al usuario: "Codex encontró…", "según Gemini…".
- **Con un juego abierto no se usa la GPU.** `guias.py` no usa un modelo local si hay un juego abierto, ni carga uno nuevo si la GPU ya usa más de 3500 MB (salvo `--forzar`).

Conviene consultar a los guías antes de entregar algo importante (una memoria de cálculo, la selección de un equipo, un plano, código grande), cuando hay dos caminos posibles y cuando el usuario lo pide. Para preguntas simples, no: gasta cupo y tiempo.

## guias.py

```
python guias.py estado                                    # qué guías hay, sesiones, modelos locales, claves y GPU
python guias.py preguntar codex "pedido" --archivo memoria.md
python guias.py consejo --pedido-archivo pedido.md --guias codex,gemini,ollama:gemma3 --salida informe.md
python guias.py pal-clave gemini                          # guarda la clave para PAL; la pide oculta
python guias.py demo                                      # prueba completa sin gastar cuota
```

| Opción | Qué hace |
|---|---|
| `--rol revisor` (por defecto) | Veredicto, errores con su corrección, supuestos dudosos y resultado propio |
| `--rol alternativa` / `libre` | Otra forma de resolverlo, con ventajas y riesgos / solo el pedido, sin instrucciones |
| `--archivo F` (se repite) | Adjunta archivos de texto (hasta 150 000 caracteres en total) |
| `--carpeta DIR` | Los CLI pueden leer esa carpeta (solo lectura) |
| `--salida F.md`, `--tiempo S`, `--forzar` | Dónde guardar, tiempo máximo por guía (600 s), usar la GPU igual |

`consejo` consulta a todos en paralelo (los modelos locales, de a uno) y arma un informe con el pedido, la respuesta de cada guía con su tiempo, los que no respondieron y por qué, y los pasos para combinar. Sale con 0 si respondió al menos uno, 1 si no respondió ninguno y 2 si hubo un error de uso. Si `ollama` no tenía el modelo cargado, lo descarga al terminar para liberar la GPU.

## Cómo armar el pedido

El guía no ve la conversación: el pedido tiene que traer todo.

1. Contexto: qué es, para qué, datos de partida con unidades.
2. Lo que hizo Claude: supuestos, método, fórmulas y resultado.
3. La pregunta concreta: "¿está bien el cálculo de la corriente?", no "revisá todo".
4. Archivos con `--archivo` (informe, script, tabla) o la carpeta con `--carpeta`.

Ejemplo de pedido corto: "Motor trifásico de 4 kW útiles, 380 V, cos φ = 0,85 y η = 88 %: I = P / (√3 · U · cos φ · η) = 8,1 A. ¿Está bien?". Codex respondió con el veredicto "de acuerdo" y I = 4000 / 492,3 = 8,12 A.

## Cómo combinar las respuestas

1. Comparar punto por punto con la solución propia: qué coincide, qué falta y qué se contradice.
2. Diferencias en números: recalcular con código (por ejemplo con **calculos-ingenieria**) y quedarse con lo que da la cuenta.
3. Corregir el entregable si un guía encontró un error real, y decirlo.
4. Contarle al usuario en pocas líneas qué coincidió, qué aportó cada guía y la conclusión.

Con un tablero abierto (**progreso-en-vivo**), dejar el resultado en una nota del paso: `nota "Consejo: Codex de acuerdo; Gemini marcó el factor de servicio"`.

## En Claude Code

- **PAL** (servidor MCP `pal-mcp-server`): herramientas `chat`, `thinkdeep`, `consensus` (varias opiniones con postura a favor o en contra), `codereview`, `precommit`, `debug`, `challenge`, `planner`, `apilookup` y `clink`, que trae a Gemini CLI, Codex CLI o Claude Code como subagentes. Los proveedores se prenden con variables en el `env` del servidor: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, y `CUSTOM_API_URL` con `CUSTOM_MODEL_NAME` para Ollama (README de BeehiveInnovations/pal-mcp-server). `guias.py pal-clave <proveedor>` guarda la clave en `~/.claude.json` con una copia de antes; hay que reiniciar Claude Code.
- **Subagentes con otro modelo**: en `.claude/agents/<nombre>.md`, el campo `model:` acepta `sonnet`, `opus`, `haiku` o `inherit` (docs.claude.com, Subagents). Un revisor en `opus` con `tools: Read, Grep, Glob` es un guía que no gasta otra cuenta.
- **Comando `/consejo`**: un archivo `~/.claude/commands/consejo.md` que arme el pedido, corra `guias.py consejo` y combine el informe con los pasos de arriba.

## Sumar guías

| Guía | Cómo se suma |
|---|---|
| Gemini CLI | `npm install -g @google/gemini-cli`, correr `gemini` una vez y elegir "Sign in with Google" (el usuario inicia sesión) |
| Gemini por API | Crear una clave en Google AI Studio y guardarla con `guias.py pal-clave gemini` (sirve también para PAL) |
| OpenRouter | Crear una clave en openrouter.ai y guardarla con `guias.py pal-clave openrouter`; elegir un modelo terminado en `:free` |
| Modelo local | `ollama pull <modelo>` (avisar el tamaño antes de bajar); probar con `guias.py preguntar ollama:<modelo> "..."` |

## Errores frecuentes

- Mandar un pedido sin contexto: el guía contesta otra cosa.
- Tomar el número del guía sin recalcular, o promediar dos resultados distintos.
- Pegar una clave en un comando: queda en el historial de la terminal. `pal-clave` la pide oculta.
- Consultar a varios modelos locales a la vez: no entran juntos en la GPU (`guias.py` los pone en fila).
- Usar a los guías para todo: son un control, no reemplazan verificar con código.

## Verificación

`python guias.py demo` tiene que terminar en `DEMO OK`. Prueba sin gastar cuota: adjuntos prohibidos, informe, claves tapadas sin tocar el texto técnico, descarga del modelo local (con un Ollama simulado) y `pal-clave` sobre una copia. Probado en Windows 11 con respuestas reales de Codex CLI 0.166 (15 s), Claude Code 2.1 y un Gemma 4 de 12B en Ollama (45 s con la carga; se descargó solo al terminar), y con el freno de la GPU con un juego abierto. Gemini (CLI y API) y OpenRouter siguen su documentación oficial (la API de Gemini, además, con un servidor simulado en el demo): confirmar con `guias.py estado` y una consulta corta en el primer uso.
