---
name: planos-tecnicos
description: "Planos técnicos 2D de nivel profesional según normas IRAM (vistas, cortes, despieces, layouts de planta, esquemas eléctricos unifilares, neumáticos y diagramas de flujo), entregados en DXF para AutoCAD y en PDF A3 vectorial listo para imprimir, con recuadro, rótulo y tabla de revisiones. Usar cuando se pidan planos, láminas, vistas acotadas, esquemas, un juego de planos de un proyecto, archivos DXF o DWG, o corregir planos existentes."
---

# Planos técnicos (DXF + PDF A3)

Una lámina = un plano. Por cada lámina se entrega:
- **DXF**: AutoCAD lo abre directo (si piden DWG, se abre el DXF en AutoCAD y se guarda como DWG); Fusion 360 y SolidWorks lo importan como croquis.
- **PDF A3 vectorial**: una lámina por página, más el juego completo en un solo PDF.
- **PNG** de control, para revisar antes de entregar.

## Herramienta base

`scripts/lamina_a3.py` (en la carpeta de esta skill) arma la hoja normalizada y exporta todo. Requiere `pip install ezdxf pymupdf`. Para ver un ejemplo completo: `python scripts/lamina_a3.py demo salida`.

```python
import sys; sys.path.insert(0, "<carpeta de esta skill>/scripts")
from lamina_a3 import nueva_lamina, cota, cota_diametro, texto, globo, factor, exportar, unir_pdfs

doc, msp, zonas = nueva_lamina("Layout general", "P01", "1:100",
                               proyecto="Planta de secado", autor="Apellido N.", reviso="Docente",
                               revisiones=[("A", "21/10/2026", "Emisión original")])
k = factor("1:100")                      # 0.01: mm reales -> mm de papel
x0, y0, x1, y1 = zonas["dibujo"]         # interior del marco; no tapar zonas["reservado"]
msp.add_lwpolyline([(x0 + 10, y0 + 60), (x0 + 10 + 24000 * k, y0 + 60),
                    (x0 + 10 + 24000 * k, y0 + 60 + 12000 * k), (x0 + 10, y0 + 60 + 12000 * k)],
                   close=True, dxfattribs={"layer": "CONTORNO"})
cota(msp, (x0 + 10, y0 + 60), (x0 + 10 + 24000 * k, y0 + 60), distancia=-10, escala=k)  # dice 24000
exportar(doc, "salida/P01")              # P01.dxf, P01.pdf, P01.png
unir_pdfs(["salida/P01.pdf", "salida/P02.pdf"], "salida/Planos_completos.pdf")
```

- Coordenadas en **milímetros de papel**: la hoja A3 apaisada va de (0, 0) a (420, 297).
- Para dibujar a escala 1:N se multiplican las medidas reales por `k = factor("1:N")` y se pasa `escala=k` a las cotas, así muestran la medida real.
- `texto()` acepta varias líneas, ancho fijo y `fondo=True` (texto sobre rayados o líneas). `globo()` dibuja la referencia con la línea cortada en el borde del círculo.
- `exportar(doc, base, color=True)` respeta colores de capa (útil en esquemas); por defecto imprime en negro, como un plano normalizado.
- Las vistas de una pieza o máquina modelada en 3D salen solas con `vistas_dxf(..., msp=msp)` de la skill **modelado-3d-cad**.

## Normas (IRAM) y convenciones

- Formatos y plegado: IRAM 4504. A3 = 420 × 297 mm. Márgenes por defecto: 25 mm a la izquierda para encarpetar y 10 mm en el resto.
- Líneas: IRAM 4502 (tabla de capas abajo); relación gruesa:fina ≈ 2:1.
- Escalas: IRAM 4505. Reducción 1:2, 1:5, 1:10, 1:20, 1:50, 1:100, 1:200, 1:500; ampliación 2:1, 5:1, 10:1.
- Vistas: método ISO E (europeo, IRAM 4501). La planta va **debajo** del frente y la vista lateral izquierda **a la derecha** del frente.
- Cortes y secciones: IRAM 4507; rayado fino a 45°. Grafismos normalizados: IRAM 4509.
- Acotación: IRAM 4513 (mecánica) e IRAM 4511 (construcciones civiles). En mecánica, cotas en mm sin unidad; en edificios, la unidad que use la cátedra.
- Esquemas eléctricos con símbolos IEC 60617; neumáticos e hidráulicos con ISO 1219.
- Si la consigna o la cátedra dan su propio rótulo, márgenes o escalas, mandan esos.

## Capas que crea la lámina

| Capa | Uso | Línea | Espesor |
|---|---|---|---|
| CONTORNO | aristas y contornos visibles | continua gruesa | 0,50 mm |
| OCULTAS | aristas ocultas | de trazos | 0,25 mm |
| EJES | ejes y líneas de simetría | de trazo y punto | 0,18 mm |
| COTAS | cotas, referencias, globos | continua fina | 0,25 mm |
| RAYADO | rayado de cortes | continua fina | 0,18 mm |
| TEXTO | notas y títulos | — | 0,25 mm |
| RECUADRO / ROTULO | marco y rótulo | continua | 0,70 / 0,35 mm |
| AUXILIAR | líneas de construcción | continua fina | 0,13 mm |

## Qué tiene que tener cada lámina

- Número (P01, P02…), título, escala, fecha, autor, revisión y tabla de revisiones que diga qué cambió (Rev. A emisión original, Rev. B…).
- Cotas totales y parciales; en plantas, ejes de columnas con letras y números, niveles y norte.
- Referencias (globos) que coincidan con la lista de equipos o de materiales de la memoria.
- Unifilar: cada circuito con su protección (interruptor, diferencial, guardamotor o térmico), sección de conductor y potencia de la carga.
- Diagrama de flujo: equipos con código, corrientes numeradas y tabla de balance.

## Errores que hay que evitar

- **PDF que en el celular se ve en blanco**: líneas demasiado finas u hoja mal dimensionada. Cada página tiene que ser A3 real (`pdfinfo` → 1190 x 841 pts) y ninguna línea por debajo de 0,13 mm.
- **Textos encimados**, rótulos tapados, cotas que se salen del marco, líneas que cruzan los números de los globos. Dejar aire alrededor de cada texto y revisar las zonas densas.
- **Cotas con la medida del papel** en vez de la real: falta `escala=k`.
- **Rehacer de cero** un plano que había que mejorar: si piden correcciones, editar las láminas existentes, conservar la numeración y subir la letra de revisión.

## Verificación antes de entregar

1. `exportar()` informa los errores del auditor del DXF: tienen que ser 0.
2. Mirar cada PNG completo y con zoom al rótulo y a las zonas densas: nada encimado, todo dentro del marco, textos de 2,5 mm o más en el papel.
3. Confirmar el tamaño de página de cada PDF y que el juego completo tenga todas las láminas en orden.
4. Si el plano sale de un modelo 3D o de un cálculo, comprobar dos o tres medidas contra el modelo o la memoria.
