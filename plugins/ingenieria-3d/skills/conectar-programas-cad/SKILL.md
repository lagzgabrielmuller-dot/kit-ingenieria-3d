---
name: conectar-programas-cad
description: "Guía para conectar Claude con Blender (servidor comunitario MCP for Blender y el oficial de Blender Lab), Fusion 360 (servidor oficial de Autodesk) y FreeCAD mediante servidores MCP, para que Claude cree y modifique modelos directamente dentro de esos programas, con los cuidados de seguridad. Usar cuando se pida que Claude maneje Blender, Fusion 360 o FreeCAD, instalar o actualizar esos conectores, elegir entre el servidor oficial y el comunitario, o seguir editando en esos programas un modelo hecho con código."
---

# Conectar Claude con Blender, Fusion 360 y FreeCAD

Un servidor MCP es un puente: Claude le manda órdenes y el programa las ejecuta. Con estos dos, Claude puede crear objetos, cambiar medidas, aplicar materiales o renderizar directamente en Blender o FreeCAD, en la compu del usuario.

Los dos se instalan en la compu donde están los programas (no en la nube) y necesitan **uv**, el instalador de herramientas de Python. En Windows: `winget install --id=astral-sh.uv -e` y después abrir una terminal nueva.

## Blender: MCP for Blender ([ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp), licencia MIT)

El paquete se llama ahora `mcp-for-blender`; `uvx blender-mcp` sigue funcionando.

1. Con uv instalado, en PowerShell: `uvx mcp-for-blender setup`. Detecta Claude Desktop y Claude Code, agrega la entrada `blender` a su configuración (guarda una copia `.bak`) e instala el complemento de Blender.
2. Si se prefiere hacerlo a mano:
   - Claude Desktop: Settings → Developer → Edit Config y sumar:
     ```json
     { "mcpServers": { "blender": { "command": "uvx", "args": ["mcp-for-blender"] } } }
     ```
   - Claude Code: `claude mcp add blender uvx mcp-for-blender`
   - Complemento: `uvx mcp-for-blender install-addon` y en Blender, Edit → Preferences → Add-ons, activar **Interface: MCP for Blender**.
3. Cerrar Claude del todo (en Windows, también desde el ícono de la bandeja) y volver a abrirlo. Abrir Blender: el complemento arranca solo. Para comprobarlo: tecla `N` en la vista 3D → pestaña **MCP for Blender** → **Start MCP Server** si no está corriendo.
4. Usar un solo servidor de Blender a la vez (no abrirlo desde dos aplicaciones).
5. Mantenerlo actualizado: en 2026 se publicaron fallas de seguridad del servidor comunitario (CVE-2026-10661, inyección; CVE-2026-66004, rutas en las descargas de Poly Haven). Para traer la última versión: `uvx mcp-for-blender@latest install-addon` y reiniciar Blender ([CVE-2026-66004](https://cvefeed.io/vuln/detail/CVE-2026-66004)).

## Blender: servidor oficial de Blender Lab

Desde abril de 2026 hay un servidor MCP hecho por desarrolladores de Blender, que en la app de Claude aparece como el conector **Blender** (Customize → Connectors). Está pensado para inspeccionar y depurar escenas, escribir scripts que cambian muchas cosas a la vez y consultar la documentación de la API de esa versión ([Anthropic](https://www.anthropic.com/news/claude-for-creative-work), [Blender Lab](https://www.blender.org/lab/mcp-server/)).

- Pide **Blender 5.1 o más nuevo** según blender.org (verificar en la página antes de instalar).
- El complemento se instala desde el enlace de la página de Blender Lab, arrastrándolo a Blender: la primera vez agrega el repositorio "lab" y la segunda instala el complemento.
- El oficial y el comunitario usan el mismo puerto (9876): no tenerlos prendidos a la vez, o cambiar el puerto de uno (variable `BLENDER_PORT` y el mismo número en el panel del complemento).
- Reparto razonable: el oficial para la API, inspeccionar escenas y scripts en lote; el comunitario para capturas desde varios ángulos (`look`), bibliotecas de modelos y generación 3D.

## Fusion 360: servidor oficial de Autodesk

Con Fusion abierto, se activa en Preferences → General → API → **Fusion MCP Server** y queda escuchando en `http://127.0.0.1:27182/mcp`. En la app de Claude es el conector **Autodesk Fusion**; en Claude Code, `claude mcp add --scope user --transport http fusion http://127.0.0.1:27182/mcp` (verificar). Puede pedir una suscripción paga de Fusion: con licencia educativa, verificar antes ([Autodesk](https://help.autodesk.com/cloudhelp/ENU/ADSKMCP-FusionDesktopMcp/files/ADSKMCP_FusionDesktopMcp_connecting_to_the_fusion_mcp_server_html.html)).

## FreeCAD: FreeCAD MCP ([neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp), licencia MIT)

1. Bajar el repo: `git clone https://github.com/neka-nat/freecad-mcp.git`.
2. Copiar la carpeta `addon/FreeCADMCP` a la carpeta de complementos de FreeCAD (la ubicación según el sistema está en `docs/installation.md` del repo) y reiniciar FreeCAD.
3. En FreeCAD, elegir el banco de trabajo **MCP Addon** y tocar **Start RPC Server** en la barra **FreeCAD MCP**.
4. Conectar Claude:
   - Claude Desktop: en la configuración, `{ "mcpServers": { "freecad": { "command": "uvx", "args": ["freecad-mcp"] } } }` (si ya está la entrada de Blender, se agregan las dos dentro de `mcpServers`).
   - Claude Code: `claude mcp add freecad -- uvx freecad-mcp`.
5. Reiniciar Claude.

## Cómo combinarlo con el resto del kit

- Un modelo hecho con la skill **modelado-3d-cad** se abre en FreeCAD desde el `.step`, y ahí Claude lo puede seguir editando (chaflanes, agujeros, planos con TechDraw).
- El `.glb` se importa en Blender para hacer renders con materiales, luces y cámara, o animaciones de la máquina.
- Pedidos que funcionan bien: "importá soporte.step en FreeCAD y agregá un chaflán de 2 mm en las aristas superiores", "abrí ensamble.glb en Blender, poné el eje en acero pulido y sacá un render de 1920 × 1080".

## Seguridad

- Estos servidores dejan que Claude ejecute código Python dentro de Blender y FreeCAD: guardar el trabajo antes de empezar y mirar lo que va haciendo.
- Instalar solamente desde los repos oficiales de arriba.
- Ninguno tiene una zona aislada: el código corre con los permisos del usuario. El servidor, solo en la propia compu (localhost); trabajar sobre una copia del archivo.
- En Claude Code se puede pedir permiso antes de ejecutar código y dejar libres las consultas, en `.claude/settings.json`: `"permissions": {"allow": ["mcp__blender__get_scene_info"], "ask": ["mcp__blender__execute_blender_code"]}` (los nombres exactos de las herramientas se ven con `/mcp`).
- Después de cada cambio, controlar el resultado con **blender-verificacion** (medidas en mm y vistas de frente, lateral, planta e isométrica).
- Si algo no responde, cerrar y volver a abrir el programa y Claude; el servidor tiene que estar corriendo antes de pedir cosas.
