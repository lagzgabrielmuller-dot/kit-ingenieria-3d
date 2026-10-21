---
name: trabajar-con-codex
description: "Hacer que Claude y ChatGPT trabajen juntos: Claude le consulta a Codex (el agente de OpenAI, instalado en la compu del usuario con su cuenta de ChatGPT) para una segunda opinión, una revisión independiente de un cálculo, un diseño, un informe o un código, o una forma alternativa de resolver algo, y después compara y combina las respuestas. Usar cuando el usuario pida preguntarle a ChatGPT o a Codex, que trabajen los dos, una doble verificación, o cuando un resultado importante merezca un control independiente."
---

# Trabajar con Codex (ChatGPT)

En la compu del usuario está instalado **Codex CLI** (`npm install -g @openai/codex`) con su cuenta de ChatGPT. Claude lo usa desde la terminal de esa compu (Desktop Commander o la terminal disponible en la sesión, con PowerShell). Codex no ve esta conversación: hay que pasarle todo el contexto en el pedido.

## Cuándo consultarlo

- El usuario lo pide ("preguntale a ChatGPT", "que lo revise Codex", "trabajen los dos").
- Un resultado importante merece un control independiente: un cálculo de una memoria, la selección de un equipo, un plano o un modelo antes de entregarlo.
- Hay dos caminos posibles y conviene una segunda opinión sobre cuál elegir.

No hace falta para preguntas simples: cada consulta consume el cupo del plan de ChatGPT del usuario.

## Cómo consultarlo

En PowerShell (Windows PowerShell 5.1 necesita la primera línea para que pasen bien los acentos):

```powershell
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$pedido = @'
Sos un revisor técnico independiente. Contexto: <datos, supuestos y resultado completos>.
Tarea: <qué revisar o resolver>.
Respondé en español con: 1) si estás de acuerdo o no, 2) errores encontrados con su corrección,
3) supuestos dudosos, 4) tu resultado si difiere, con el cálculo.
'@
$salida = Join-Path $env:TEMP "codex_respuesta.md"
$pedido | codex exec --skip-git-repo-check --sandbox read-only --ephemeral -o $salida -
Get-Content $salida -Encoding UTF8
```

- `--sandbox read-only`: Codex puede leer archivos pero no modificar nada. Es el modo por defecto para consultas.
- `-C "C:\ruta\del\proyecto"`: para que lea los archivos de un proyecto (planos, scripts, informe) en lugar de pasárselos en el texto.
- `-o archivo`: guarda solo la respuesta final; el progreso sale por la terminal.
- Para revisar cambios de código dentro de un repositorio git: `codex review` (opciones en `codex review --help`).
- Puede tardar de 30 segundos a varios minutos: usar un tiempo de espera largo y leer la salida cuando termine.

Solo usar `--sandbox workspace-write` (y siempre con `-C` apuntando a una carpeta concreta) si el usuario pide expresamente que Codex modifique archivos. Nunca usar las opciones `--dangerously-...`.

## Cómo combinar las dos respuestas

1. Comparar punto por punto la respuesta de Codex con la propia.
2. Si hay diferencias en números, recalcular con código para decidir quién tiene razón; no promediar ni elegir por autoridad.
3. Presentar al usuario qué coincidió, qué corrigió cada uno y la conclusión final, dejando claro qué vino de Codex ("según Codex…").
4. Si Codex encontró un error real, corregirlo en el entregable y decirlo.

## Cuidados

- No pasarle a Codex contraseñas, claves de API ni datos personales de otras personas.
- Codex también puede equivocarse: su respuesta es una opinión más, no la verdad final.

## Si algo falla

- `codex login status` muestra si la sesión de ChatGPT está activa. Si dice "Not logged in", correr `codex login --device-auth` y pasarle al usuario el link y el código para que inicie sesión él.
- `codex doctor` diagnostica la instalación.
- `codex update` actualiza a la última versión.
