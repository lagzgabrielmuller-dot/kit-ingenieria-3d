# Créditos: Electrónica y PCB con KiCad

Revisión de diseños electrónicos con KiCad (kicad-happy) y referencias de KiCad, LTspice, Altium y PlatformIO.

Skills escritas por otras personas y copiadas **sin modificaciones** desde sus repos, con permiso de sus licencias. Las licencias completas están en `licencias/`.

| Autor y repo | Licencia | Commit copiado |
|---|---|---|
| Andrew Klofas, [aklofas/kicad-happy](https://github.com/aklofas/kicad-happy) | MIT | `6a91aaaea124152b2923326c1cf77278e0999cd4` |
| o2scale, [o2scale/electronics-agent-kit](https://github.com/o2scale/electronics-agent-kit) | MIT | `705ba32a6d92c6182e1889d97a818ce73f3ee6f3` |
| Major AI Skills contributors, [alivirgo/Major-AI-Skills](https://github.com/alivirgo/Major-AI-Skills) | MIT | `17fb963bd185e23367d23b22f2ea5f3688d27f40` |

## Skills (16)

| Skill | Para qué sirve (descripción original) |
|---|---|
| `altium-designer` | Automate Altium Designer PCB workflows with DXP scripts, design-rule checks, OutJob fabrication outputs, and routing configuration. |
| `bom` | BOM (Bill of Materials) management for electronics projects — the workflow skill that coordinates DigiKey, Mouser, LCSC, element14, JLCPCB, PCBWay, and KiCad skills… |
| `datasheets` | Extract structured specifications from electronic component datasheet PDFs — pinouts, electrical characteristics, peripherals, topology, and features. Cache… |
| `digikey` | Search DigiKey for electronic components and download datasheets — primary source for prototype orders and the preferred API method for fetching datasheets. Find… |
| `element14` | Search Newark, Farnell, and element14 for electronic components — find parts by MPN or distributor part number, check pricing/stock, download datasheets, analyze… |
| `emc` | EMC pre-compliance risk analysis for KiCad PCB designs — 18 check categories, 44 rule IDs covering ground planes, decoupling, I/O filtering, switching harmonics,… |
| `jlcpcb` | JLCPCB PCB fabrication and assembly — BOM/CPL generation, basic vs extended parts, assembly constraints, design rules, ordering workflow. Use with KiCad for JLCPCB… |
| `kicad` | Analyze KiCad projects and PDF schematics: schematics, PCB layouts, Gerbers, footprints, symbols, netlists, and design rules. Reviews designs for bugs, traces nets,… |
| `kicad-cli` | KiCad command-line interface expertise. Complete reference for schematic/PCB exports, DRC/ERC validation, manufacturing outputs, and automation. |
| `kicad-file-format` | KiCad S-expression file format expertise. Complete reference for reading and writing .kicad_sch (schematic) and .kicad_pcb (PCB) files. |
| `lcsc` | Search LCSC Electronics for electronic components — find parts by LCSC number (Cxxxxx) or MPN, check stock/pricing, download datasheets, analyze specifications.… |
| `ltspice` | Build LTspice netlists, automate measurements, and investigate convergence or switching-converter simulation behavior. |
| `mouser` | Search Mouser Electronics for electronic components — secondary source for prototype orders. Find parts, check pricing/stock, download datasheets, analyze… |
| `pcbway` | PCBWay PCB fabrication and assembly — turnkey/consigned assembly, design rules, ordering workflow. Alternative to JLCPCB for manufacturing. Use with KiCad. Use this… |
| `platformio` | PlatformIO embedded development platform expertise. Project setup, configuration, building, debugging, and library management for Arduino, ESP-IDF, STM32, and more. |
| `spice` | Run automatic SPICE simulations on subcircuits detected from KiCad schematic analysis — validates filter frequencies, divider ratios, opamp gains, LC resonance, and… |

## Qué necesitan

- KiCad 8 o 9 (incluye `kicad-cli`). Python 3.8+ para los scripts de `kicad`, `emc`, `spice` y `datasheets` (casi todo con la biblioteca estándar).
- `spice`: ngspice, LTspice o Xyce instalado.
- `digikey`, `mouser`, `element14`: una clave de API gratuita de cada distribuidor en variables de entorno (las skills explican cuáles). `lcsc` y la búsqueda de JLCPCB no necesitan clave.
- `ltspice`, `altium-designer`: esos programas instalados.

## Revisión

Antes de copiarlas revisé licencia, estructura, scripts, llamadas de red, binarios, hooks y frases que intenten darle órdenes ocultas a Claude, sin encontrar problemas. Los scripts no se ejecutaron durante la revisión. Si un autor publica una versión nueva, se puede volver a copiar y actualizar el commit de la tabla. Las llamadas de red van solo a las API de los distribuidores (DigiKey, Mouser, element14, LCSC, jlcsearch de tscircuit) y mandan números de pieza. `export_issues.py` crea issues en GitHub con `gh` solo si se lo pide.
