# Créditos: Blender: modelado, render y animación

Paquete *cc-blender-skill*: cómo dejar lindo un render y armar escenas, más un circuito para pasar de vistas o dibujos a un modelo 3D. No se copió `mascot-logo-reconstruction`, pensada para reconstruir mascotas y logos de marcas.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| RobLe3, [roble3/cc-blender-skill](https://github.com/roble3/cc-blender-skill) | MIT | `a2634b588e80265e796aa53f8ab178d75105c2af` |

## Skills (29)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `animation-quality-gate` | Validate Blender animation attempts before accepting them by rendering contact sheets, checking silhouette stability, flicker, framing, subject dominance, layer… |
| `atlas-uv-fitting` | Detect texture-atlas regions and map each source part to its own UV rectangle or projected UV surface. Use when a texture pack must fit a Blender model 1:1, when… |
| `blender-animation` | Animate objects, cameras, lights, and properties in Blender — keyframes, F-curves, easing (Bezier, Linear, Sine, Bounce, Elastic), shape keys (morph targets /… |
| `blender-cameras` | Set up Blender cameras with cinematic intent — focal length, depth of field (f-stop / focus object), composition (rule of thirds, leading lines), animated cameras… |
| `blender-export` | Export Blender scenes to glTF/GLB (web/AR), FBX (game engines), OBJ (universal), USD (VFX pipelines), STL (3D printing). Includes Unreal collision hulls and Multires… |
| `blender-lighting` | Light Blender scenes professionally — three-point setups, HDRI environments, studio/cinematic/dramatic configurations, light groups, color temperature, soft vs hard… |
| `blender-materials` | Create and assign PBR materials in Blender via Principled BSDF — metals, glass, plastic, fabric, skin, organics. Covers physically-based material recipes with… |
| `blender-modeling` | Create and edit 3D meshes in Blender — primitives, hard-surface modeling, mesh operators, modifier stacks (Bevel, Subdivision, Boolean, Mirror, Array, Solidify),… |
| `blender-pro-workflow` | End-to-end production workflow guidance for Blender — the order to assemble scenes (block-out → camera → light → forms → materials → detail → render → composite →… |
| `blender-rendering` | Render Blender scenes with the right engine and settings — Cycles for photoreal, EEVEE for speed/stylized, sample counts, denoising (OptiX/OIDN), light path tuning,… |
| `blender-skill-harmonizer` | Harmonize multiple Blender skills into a coherent pipeline with clear activation precedence, handoff artifacts, dependency gates, and conflict-resolution rules. Use… |
| `blender-uv-texturing` | UV unwrap, atlas-map, project textures, use alpha decals, bake maps/lightmaps, and prepare texture-driven Blender assets for glTF/GLB export. Use whenever the user… |
| `closed-surface-uv-coverage` | Ensure textures and decals cover all visible surfaces of a closed or extruded Blender asset, especially front/back caps and sidewalls, instead of relying on partial… |
| `contour-to-mesh` | Build Blender mesh surfaces directly from extracted 2D contours/masks instead of approximate primitives. Use for 1:1 mascot/logo reconstruction, exact leaf/petal… |
| `fit-repair-optimizer` | Turn multiview fit reports into a sequential or parallel repair queue for aligning Blender products to source-of-truth templates. Use after validation shows… |
| `landmark-fit-repair` | Validate and repair source-locked Blender models using named landmarks such as leaf tips, shell corners, eyes, smile, rim thickness, aura center/radius, and… |
| `multiview-constraint-solver` | Determine whether front/side/back/top reference templates can be satisfied by one rigid 3D Blender model, choose a canonical source policy, and emit constraints… |
| `multiview-fit-loop` | Closed-loop compare-adjust-repeat workflow for fitting Blender models to supplied front/side/back/top templates and originals. Use when the user asks to compare the… |
| `orbital-hud-motion` | Create tasteful circular/orbital HUD and aura animations around a Blender subject using source-derived arcs, dots, dashes, opacity, parallax, and restrained motion.… |
| `orthographic-registration` | Register front, side, back, and top orthographic reference views into a shared Blender coordinate contract. Use when a 3D model must match multi-view… |
| `quality-refinement-autoloop` | Run a self-refinement loop when a Blender result is subpar, user expectations are not met, validation fails, or repeated issues reveal missing skill depth. The loop… |
| `reference-analysis-validator` | Measure and validate supplied reference images, wireframes, texture atlases, and Blender renders before declaring a reconstruction 1:1. Use when an asset must match a… |
| `reference-look-calibration` | Calibrate Blender materials, lighting, camera crop, emission/glow, color management, and aura/HUD styling against supplied original/reference images using measurable… |
| `reference-to-3d` | Reconstruct Blender models from supplied reference sheets, branding templates, texture atlases, orthographic front/side/back/top views, or mascot/logo art where… |
| `source-part-segmentation` | Segment overlapping visual parts from source images, wireframes, texture atlases, and decals before mesh reconstruction. Use when a mascot/logo/template contains… |
| `text-to-blender` | Drive Blender from natural language: create or edit 3D models, materials, lighting, cameras, renders, animation, and exports through Blender MCP. Route complete… |
| `texture-driven-mesh-fitting` | Reshape source-locked mesh boundaries so the geometry fits texture-atlas or decal contours 1:1 before final UV/material work. Use when textures look off because the… |
| `texture-state-animation` | Design and validate texture-state transitions for Blender animations without ugly whole-image crossfades, texture popping, misregistered morphs, or… |
| `wireframe-to-3d` | Convert 2D orthographic wireframe PNG drawings to 3D Blender models exported as glTF/GLB. Use this skill whenever the user provides wireframe images (technical… |

## Qué necesitan

- Blender 4.x o 5.x. Para que Claude maneje Blender directamente, el servidor MCP de Blender (ver la skill `conectar-programas-cad` del plugin `ingenieria-3d`).
- Varias skills traen scripts de Python que se corren con el Python de Blender (`blender --background --python ...`).

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla.
