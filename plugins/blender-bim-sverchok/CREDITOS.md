# Créditos: Blender por código, BIM (Bonsai e IfcOpenShell) y Sverchok

Paquete de 73 skills de OpenAEC Foundation, con su estructura de carpetas original (blender, bonsai, ifcopenshell, sverchok, aec) para que funcionen los enlaces entre skills. El `plugin.json` lista cada skill.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| OpenAEC Foundation, [Impertio-Studio/Blender-Bonsai-ifcOpenshell-Sverchok-Claude-Skill-Package](https://github.com/Impertio-Studio/Blender-Bonsai-ifcOpenshell-Sverchok-Claude-Skill-Package) | MIT | `dc56112d81b25b64d3e1c7b765673a035981543f` |

## Skills (73)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `aec-agents-workflow-orchestrator` | Use when a task spans multiple AEC technologies (Blender, IfcOpenShell, Bonsai, Sverchok) and you need to decide which tool handles which step, or when orchestrating… |
| `aec-core-bim-workflows` | Use when implementing end-to-end BIM workflows that combine IfcOpenShell, Bonsai, and Blender -- such as IFC creation from scratch, model enrichment, validation… |
| `blender-agents-code-validator` | Use when reviewing, validating, or auditing Blender Python code for correctness. Runs systematic checks for deprecated API usage, context errors, version… |
| `blender-agents-version-migrator` | Use when migrating, porting, or upgrading Blender Python scripts and addons across major versions (3.x to 4.x to 5.x). Provides a systematic migration process… |
| `blender-core-api` | Use when writing Blender Python scripts that access bpy module structure, RNA data, the context system, dependency graph, or operator invocation. Prevents the common… |
| `blender-core-gpu` | Use when drawing custom overlays, viewport visualizations, or offscreen renders in Blender Python. Prevents the critical mistake of using the deprecated bgl module… |
| `blender-core-runtime` | Use when dealing with Blender Python runtime behavior -- mathutils, threading, handlers, timers, or crashes after undo/redo. Prevents the #1 runtime crash: using… |
| `blender-core-versions` | Use when writing Blender Python code that must work across multiple versions (3.x/4.x/5.x), or when migrating scripts between Blender versions. Prevents breakage from… |
| `blender-errors-context` | Use when debugging Blender RuntimeError from restricted context, operator poll() failures, or wrong context for bpy.ops calls. Prevents the #1 Blender Python error:… |
| `blender-errors-data` | Use when debugging Blender ReferenceError from removed objects, undo-invalidated bpy.data references, or stale ID pointers. Prevents the common crash of caching… |
| `blender-errors-version` | Use when debugging Blender AttributeError from removed APIs, ImportError from deprecated modules (bgl in 5.0), or breaking changes in operator signatures between… |
| `blender-impl-addons` | Use when building a production Blender addon -- project structure, testing, CI/CD, or packaging for extensions.blender.org. Prevents the common mistake of hardcoding… |
| `blender-impl-animation` | Use when implementing AEC-specific animations -- construction sequences, camera walkthroughs, solar studies, or phasing visualizations in Blender. Prevents the common… |
| `blender-impl-automation` | Use when automating Blender workflows -- batch rendering, headless processing via blender --background, file format conversion, or pipeline integration. Prevents the… |
| `blender-impl-mesh` | Use when generating mesh geometry for AEC applications -- buildings from vertices, IFC geometry visualization, parametric elements, or custom mesh tools. Prevents the… |
| `blender-impl-nodes` | Use when building Geometry Nodes or Shader Nodes setups programmatically for AEC applications -- parametric modeling, material generation, or procedural geometry.… |
| `blender-impl-operators` | Use when implementing complex Blender operators -- modal operators with timer callbacks, file browsers, batch processing, or multi-step workflows. Prevents the common… |
| `blender-syntax-addons` | Use when creating a Blender addon or extension, or migrating from legacy bl_info to blender_manifest.toml (required in 5.0). Prevents the common mistake of using… |
| `blender-syntax-animation` | Use when creating animations programmatically in Blender -- keyframes, FCurves, Actions, NLA strips, drivers, or armature operations. Prevents the breaking change… |
| `blender-syntax-data` | Use when managing Blender data blocks -- collections, linked libraries, library overrides, or the asset system. Prevents the common mistake of not handling fake users… |
| `blender-syntax-materials` | Use when creating or modifying Blender materials and shader nodes via Python. Prevents the breaking change of using old Principled BSDF input names (e.g.,… |
| `blender-syntax-mesh` | Use when creating or editing mesh geometry in Blender Python -- vertices, edges, faces, BMesh operations, or bulk data access. Prevents the performance mistake of… |
| `blender-syntax-modifiers` | Use when working with Blender modifiers via Python -- adding, configuring, or applying modifiers, or accessing Geometry Nodes inputs. Prevents the common mistake of… |
| `blender-syntax-nodes` | Use when building node trees via Python -- Geometry Nodes, Shader Nodes, or Compositor Nodes. Prevents the breaking change of using node.inputs/outputs by index… |
| `blender-syntax-operators` | Use when creating custom Blender operators -- bpy.types.Operator subclasses with execute, invoke, or modal methods. Prevents the common mistake of not implementing… |
| `blender-syntax-panels` | Use when creating custom Blender UI panels, menus, or UIList elements. Prevents the common mistake of using wrong bl_space_type/bl_region_type combinations (panel… |
| `blender-syntax-properties` | Use when adding custom properties to Blender objects -- BoolProperty, IntProperty, FloatProperty, EnumProperty, PointerProperty, or PropertyGroup. Prevents the common… |
| `blender-syntax-rendering` | Use when configuring render settings or automating renders in Blender Python. Prevents the version pitfall of using 'BLENDER_EEVEE' (renamed to 'BLENDER_EEVEE_NEXT'… |
| `bonsai-agents-ifc-validator` | Use when validating, auditing, or verifying IFC model quality in Bonsai projects. Provides systematic checks for spatial hierarchy completeness, property set… |
| `bonsai-core-architecture` | Use when developing Bonsai (formerly BlenderBIM) extensions, scripting BIM workflows in Blender, or understanding the Bonsai addon architecture. Prevents the common… |
| `bonsai-errors-common` | Use when debugging Bonsai errors -- IFC schema violations, spatial hierarchy errors, property set failures, geometry representation issues, or operator poll failures.… |
| `bonsai-impl-bcf` | Use when working with BIM Collaboration Format (BCF) files in Bonsai -- creating topics, adding viewpoints, managing comments, or importing/exporting BCF files (v2.1… |
| `bonsai-impl-clash` | Use when performing clash detection, interference checking, or spatial coordination in BIM models using Bonsai and IfcClash. Prevents the common mistake of running… |
| `bonsai-impl-classification` | Use when classifying IFC elements in Bonsai with systems like Uniclass 2015, OmniClass, NL-SfB, or CCI. Prevents the common mistake of assigning classifications… |
| `bonsai-impl-drawing` | Use when generating 2D drawings from IFC models in Bonsai -- plans, sections, elevations, annotations, or sheet layouts. Prevents the common mistake of creating views… |
| `bonsai-impl-modeling` | Use when placing building elements (walls, slabs, columns, beams) in Bonsai or assigning IFC types and materials. Prevents the common mistake of creating geometry… |
| `bonsai-impl-project` | Use when creating, opening, or configuring Bonsai IFC projects -- schema selection (IFC2X3/IFC4/IFC4X3), unit configuration, georeference setup, or project templates.… |
| `bonsai-impl-qto` | Use when calculating quantities from IFC elements in Bonsai -- area, length, volume, weight, or custom quantity sets. Prevents the common mistake of manually… |
| `bonsai-syntax-elements` | Use when accessing IFC elements from Blender objects in Bonsai -- getting the IFC entity behind a selected object, or finding which Blender object represents an IFC… |
| `bonsai-syntax-geometry` | Use when creating or editing IFC geometry representations in Bonsai -- profile extrusions, boolean operations, mesh-to-IFC conversion, or geometry context setup.… |
| `bonsai-syntax-properties` | Use when creating, reading, or editing IFC property sets (Pset) and quantity sets (Qto) in Bonsai. Prevents the common mistake of creating property sets without… |
| `bonsai-syntax-spatial` | Use when creating or managing IFC spatial hierarchy in Bonsai -- IfcSite, IfcBuilding, IfcBuildingStorey, IfcSpace, and their containment relationships. Prevents the… |
| `ifcos-agents-code-validator` | Use when reviewing, validating, or auditing IfcOpenShell Python code for correctness. Runs systematic checks for schema compatibility errors, incorrect API usage… |
| `ifcos-core-concepts` | Use when learning IFC data model fundamentals or navigating IFC entity relationships. Prevents the common mistake of creating flat element structures without proper… |
| `ifcos-core-runtime` | Use when debugging IfcOpenShell crashes, entity reference errors, or performance issues. Prevents the common pitfall of comparing entities with == instead of checking… |
| `ifcos-errors-patterns` | Use when debugging IfcOpenShell errors -- RuntimeError on invalid entities, AttributeError from wrong PascalCase, TypeError from wrong parameter types, or entity… |
| `ifcos-errors-performance` | Use when processing large IFC files (100MB+) or optimizing slow IfcOpenShell scripts. Prevents the #1 performance mistake: calling create_shape() per element instead… |
| `ifcos-errors-schema` | Use when encountering IFC schema errors or migrating between IFC2X3, IFC4, and IFC4X3. Prevents the common mistake of using IFC4-only entities (e.g.,… |
| `ifcos-impl-cost` | Use when implementing cost estimation or 5D BIM workflows in IFC models -- cost schedules, cost items, cost values, or linking quantities to costs. Prevents the… |
| `ifcos-impl-creation` | Use when building IFC models from scratch -- creating projects, spatial structure, walls, slabs, columns, openings, property sets, and type assignments. Prevents the… |
| `ifcos-impl-geometry` | Use when extracting 3D geometry from IFC files, creating geometric representations, or processing IFC geometry for visualization. Prevents the performance mistake of… |
| `ifcos-impl-materials` | Use when assigning materials to IFC elements -- single materials, layer sets (walls), profile sets (beams/columns), or constituent sets (IFC4+). Prevents the common… |
| `ifcos-impl-mep` | Use when modeling MEP (Mechanical, Electrical, Plumbing) systems in IFC -- HVAC, piping, electrical circuits, distribution elements, ports, and connections. Prevents… |
| `ifcos-impl-profiles` | Use when creating structural cross-sections or profile-based extrusions in IFC -- I-beams, C-channels, rectangles, circles, or arbitrary polyline profiles. Prevents… |
| `ifcos-impl-relationships` | Use when managing IFC element relationships -- spatial containment, aggregation, type assignment, property association, material association, or void relationships.… |
| `ifcos-impl-sequence` | Use when implementing construction schedules or 4D BIM timelines in IFC -- work schedules, tasks, task dependencies, and Gantt chart data extraction. Prevents the… |
| `ifcos-impl-validation` | Use when validating IFC files for schema compliance, IDS conformance, or custom quality rules. Prevents the common mistake of only checking schema validity without… |
| `ifcos-syntax-api` | Use when writing IfcOpenShell Python code that creates, modifies, or deletes IFC entities. Prevents the #1 AI mistake: using create_entity() or direct attribute… |
| `ifcos-syntax-elements` | Use when querying, traversing, or extracting data from IFC elements -- by_type, by_id, by_guid, inverse references, or property extraction. Prevents the common… |
| `ifcos-syntax-fileio` | Use when opening, creating, writing, or serializing IFC files with IfcOpenShell. Prevents the common mistake of not using transactions for multi-step operations (no… |
| `ifcos-syntax-util` | Use when extracting data from IFC models using utility functions -- element properties, selector syntax, placement calculations, unit conversion, or cost/schedule… |
| `sverchok-agents-code-validator` | Use when reviewing, validating, or auditing Sverchok node code for correctness. Runs 19 automated checks covering data nesting correctness, updateNode callbacks, list… |
| `sverchok-core-concepts` | Use when learning Sverchok fundamentals or debugging node tree execution issues. Prevents the common mistake of expecting immediate execution (Sverchok uses deferred… |
| `sverchok-errors-common` | Use when debugging Sverchok node code errors -- silent data corruption, missing updateNode callbacks, socket data mutation, or IfcSverchok entity management issues.… |
| `sverchok-impl-custom-nodes` | Use when developing a custom Sverchok node -- creating new node types, packaging as addons, or integrating with BMesh. Prevents the critical mistake of not calling… |
| `sverchok-impl-extensions` | Use when working with Sverchok-Extra (advanced geometry, SDF, surfaces, fields, solids), Open3d integration, or developing custom Sverchok extensions. Prevents the… |
| `sverchok-impl-ifcsverchok` | Use when generating IFC files from Sverchok geometry using IfcSverchok nodes. Prevents the critical mistake of not understanding SvIfcStore transient file management… |
| `sverchok-impl-parametric` | Use when designing parametric AEC geometry in Sverchok -- structural grids, facade panels, parametric stairs, roof geometry, MEP routing, or terrain from data.… |
| `sverchok-impl-topologic` | Use when working with TopologicSverchok for building topology analysis -- CellComplex workflows, space adjacency graphs, dual graphs, or energy simulation… |
| `sverchok-syntax-api` | Use when automating Sverchok from Python -- creating node trees programmatically, connecting sockets, setting parameters, or running batch parametric studies.… |
| `sverchok-syntax-data` | Use when Sverchok data looks wrong, vertices are flattened, or list lengths don't match. Prevents the #1 Sverchok error: wrong data nesting levels (vertices MUST be… |
| `sverchok-syntax-scripting` | Use when writing SNLite scripts, Formula Mk5 expressions, Profile Mk3 definitions, or embedding custom Python logic in Sverchok node trees. Prevents the common… |
| `sverchok-syntax-sockets` | Use when connecting Sverchok nodes, debugging socket compatibility errors, or choosing the right socket type. Prevents the common mistake of connecting incompatible… |

## Qué necesitan

- Blender 4.x o 5.x. Bonsai (extensión de Blender) para BIM, `pip install ifcopenshell` para trabajar IFC fuera de Blender y la extensión Sverchok para lo paramétrico.

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla.
