---
name: conectar-programas-cad
description: "Guía para conectar Claude con Blender y FreeCAD instalados en la compu del usuario mediante servidores MCP (MCP for Blender y FreeCAD MCP), para que Claude cree y modifique modelos directamente dentro de esos programas. Usar cuando se pida que Claude maneje Blender o FreeCAD, instalar esos conectores, o seguir editando en esos programas un modelo hecho con código."
---

# Conectar Claude con Blender y FreeCAD

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
- Si algo no responde, cerrar y volver a abrir el programa y Claude; el servidor tiene que estar corriendo antes de pedir cosas.
