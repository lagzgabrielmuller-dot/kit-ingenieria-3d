# kit-ingenieria-3d: instrucciones para Claude

Marketplace **público** de plugins de Claude con skills para electromecánica, diseño 3D, electrónica y automatización, en español. Lo arma Gabriel (estudiante de Técnico Electromecánico) y cualquiera lo puede instalar.

## Estructura
- `.claude-plugin/marketplace.json`: lista de plugins (nombre, carpeta, descripción, categoría, tags).
- `plugins/ingenieria-3d/`: el plugin **propio**. Cada skill en `skills/<nombre>/SKILL.md`, con `scripts/`, `references/` o `plantilla/` si hacen falta.
- `plugins/<otro>/`: skills de la comunidad, copiadas **sin modificar**, con `CREDITOS.md` (repo, commit, licencia, requisitos, revisión) y `licencias/`.
- `CATALOGO.md`: recursos que no se copiaron, con el motivo.
- `scripts/validar_kit.py`: revisa todo (lo corre GitHub Actions en cada push, `.github/workflows/validar.yml`).

## Reglas
- **Repo público**: nada personal (nombres de personas, escuela, profesores, direcciones), ni claves, ni `.zip`, ni `.env`.
- Skills propias:
  - `name` igual a la carpeta, en minúsculas con guiones, sin "claude" ni "anthropic".
  - `description` entre comillas, de 1024 caracteres como máximo, sin `<` ni `>`: qué hace y "Usar cuando …" con las palabras que usaría un alumno. Es lo que decide cuándo se carga.
  - Cuerpo en español técnico de Argentina: coma decimal, unidades SI con espacio, impersonal. Método, fórmulas con símbolos y unidades, tablas con fuente, errores frecuentes, verificación. SKILL.md de hasta ~260 líneas; lo demás en `references/`, linkeado diciendo cuándo leerlo.
  - Fórmulas y valores verificados con código; números de normas, leyes y catálogos con su fuente. Lo que no se pudo confirmar va marcado "(verificar en la norma vigente)". Nunca inventar.
  - Scripts: Python 3.9+, solo biblioteca estándar si se puede, con `--help` y `demo` que reproduce el ejemplo del SKILL.md.
  - Las skills se referencian entre sí por su nombre en negrita (por ejemplo **calculos-ingenieria**) en vez de repetir contenido.
- Skills de la comunidad: no se editan. Si hay que hacer un arreglo de compatibilidad (por ejemplo, comillas en el frontmatter), se anota en el `CREDITOS.md` de ese plugin. Para actualizarlas: volver a copiarlas desde su repo y anotar el commit nuevo.
- Antes de commitear: `python scripts/validar_kit.py --conteo` sin errores, y actualizar en el `README.md` la tabla de plugins, el total de skills y la tabla de skills propias; en `marketplace.json`, la descripción del plugin que cambió.
- Los plugins no tienen número de versión: cada push a `main` es una actualización (en Claude Code se baja con `/plugin marketplace update kit-ingenieria-3d`).
- Commits en español, cortos: qué cambió y por qué.
