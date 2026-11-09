---
name: revision-tecnica
description: "Control independiente de un trabajo técnico terminado antes de entregarlo: trabajo práctico, informe, memoria de cálculo, presentación, plano, simulador o programa CNC. Rehace cada cuenta con código (incluye un script que recalcula los números de un informe a partir de sus datos y fórmulas), revisa unidades, órdenes de magnitud, límites de norma, citas contra la fuente, coherencia entre informe, planos y presentación, y que esté respondida toda la consigna. Devuelve una tabla de correcciones por gravedad y preguntas probables para la defensa. Usar cuando se pida revisar, controlar, corregir o verificar un trabajo, una doble verificación, un control antes de entregar, buscar errores en un informe o en cálculos, o cuando el trabajo es importante y conviene que lo mire alguien que no lo hizo."
---

# Revisión técnica independiente

El que hizo el trabajo no ve sus propios errores: da por buenas las cuentas que ya hizo y las suposiciones que tomó. Esta revisión se hace **como si fuera otra persona**, con desconfianza sana: nada está bien hasta comprobarlo.

## Independencia
- Si el entorno permite delegar en un agente nuevo (subagente), mandale **solo** la consigna, los entregables finales y el material de la cátedra, sin las conclusiones ni "lo que ya está verificado". Con eso trabaja de cero.
- Si no se puede delegar: hacerlo en una pasada aparte, con esta lista, recalculando todo desde los datos de partida y no desde resultados intermedios del trabajo.
- Para una segunda opinión de otro modelo, ver la skill **trabajar-con-codex**.

## Método
1. **Inventario.** Consigna con sus puntos numerados, entregables (informe, presentación, planos, simulador, programa) y fuentes usadas (libro, apunte, catálogo, norma).
2. **Cobertura de la consigna.** Tabla: punto de la consigna → dónde se responde (sección, página, diapositiva) → completo / incompleto / falta. Lo que falta es un hallazgo importante.
3. **Recalcular los números.** Cada resultado con su fórmula y los datos de partida, con código. Para un informe con muchos números, cargarlos en un JSON y correr `scripts/verificar_numeros.py` (ver abajo). Diferencia mayor que 1 % → revisar; si cambia una decisión (sección, potencia, modelo adoptado) es **crítico**.
4. **Unidades y magnitudes.** Coherencia dimensional, unidades SI, orden de magnitud contra valores típicos (ver la tabla de trampas). Un resultado "raro" se recalcula por otro camino.
5. **Criterio técnico y normas.** Valores adoptados normalizados y del lado seguro; límites de norma (caída de tensión, iluminación, ruido, sección mínima) según la skill **normas-tecnicas-ar** o lo que fije la cátedra. Supuestos escritos y razonables.
6. **Citas y fuentes.** Que lo citado diga eso (comparar con el libro o el apunte por página o sección), que no haya referencias inventadas, que precios y datos de catálogo tengan fuente y fecha, y el formato pedido (APA 7 u otro).
7. **Coherencia entre entregables.** Los mismos valores, códigos de equipos y nombres en informe, planos, presentación, simulador y guion.
8. **Forma.** Carátula, índice real, numeración de figuras y tablas citadas en el texto, ecuaciones con símbolos explicados, PDF sin páginas en blanco ni tablas cortadas (la skill **informe-tecnico** tiene la lista de verificación del archivo). Correr `scripts/revisar_documento.py` sobre **los archivos finales** (los que se van a mandar, no los borradores): marca lo que más baja la nota y nadie revisa al final:
   - marcadores sin completar ("(completar)", "A completar", "Haga clic aquí…", "Untitled", TODO);
   - un mismo nombre escrito de dos formas (la empresa del caso, la central, un autor);
   - tablas con columnas vacías (por ejemplo, quién expone cada parte);
   - texto que quedó de una prueba o un chiste, y palabras repetidas.
   Además, confirmar el **formato de entrega** que pidió el profesor: si pidió un solo PDF, va todo en un PDF (no Word y Excel por separado).
9. **Defensa.** De lo revisado salen las preguntas probables del profesor: por qué se adoptó cada valor clave, qué pasaría si cambia un dato, de dónde sale cada fórmula.

## Gravedad
| Gravedad | Qué es | Ejemplos |
|---|---|---|
| **Crítico** | Cambia un resultado o una decisión, o es un error conceptual | Sección de cable que no verifica; cupla de arranque mal comparada; fórmula equivocada |
| **Importante** | Número mal que no cambia la decisión, punto de la consigna incompleto, cita que no dice eso | Corriente con 3 % de error; falta el punto 4.b; página del libro equivocada |
| **Menor** | Forma, redondeo, redacción | Figura sin número; coma y punto mezclados; unidad sin espacio |

## Trampas frecuentes en electromecánica
| Tema | Trampa |
|---|---|
| Motores | p pares de polos ≠ polos (ns = 60·f/p con p en pares); la potencia de placa es la útil en el eje: la corriente lleva η y cos φ |
| Arranques | Estrella-triángulo solo si el motor está en triángulo a la tensión de red; con la misma corriente de línea, el autotransformador da la misma cupla que la estrella-triángulo; el arrancador suave limitando corriente baja la cupla con el cuadrado |
| Protección | En estrella-triángulo el relé térmico va en las fases del triángulo y se ajusta a ≈ 0,58·In |
| Cuplas | kgm ≠ N·m (1 kgm = 9,81 N·m) |
| Conductores | Monofásica: ΔU = 2·I·L·(…); trifásica: √3·I·L·(…), con L de ida; no mezclar caída en V y en %; corregir ρ por temperatura |
| Transformadores | Rendimiento máximo cuando pérdidas en el cobre = pérdidas en el hierro; Pcc es a corriente nominal |
| Iluminación | N se redondea hacia arriba y se verifica E con el N adoptado; factor de mantenimiento y coeficiente de utilización del fabricante |
| Neumática | Retroceso con área anular; consumo en aire libre (presión absoluta / atmosférica); manométrica ≠ absoluta |
| Ensayos | Brinell: F en N con el 0,102 o en kgf sin él; huella válida 0,24·D a 0,6·D |
| CNC | En torno X va en diámetro; G96 siempre con límite de rpm; F en mm/vuelta o mm/min según el modo |
| General | Redondear al final, no en el medio; valores de catálogo sin fuente; "datos típicos" presentados como medidos |

## Script: `scripts/revisar_documento.py`
Último control del archivo que se entrega: `python revisar_documento.py informe.docx presentacion.pptx planilla.xlsx informe.pdf` (o `demo`). Lee Word, PowerPoint, Excel, PDF (con `pdftotext` o PyMuPDF) y texto; `--prohibidas lista.txt` suma palabras a buscar. Sale con código 1 si encuentra algo.

## Script: `scripts/verificar_numeros.py`
Recalcula los resultados del informe a partir de los datos y una fórmula por resultado, y marca los que difieren. Solo biblioteca estándar; las fórmulas solo admiten aritmética y funciones de `math` (no ejecuta otra cosa).

```json
{
  "datos": {"P": 7500, "U": 380, "cosphi": 0.85, "eta": 0.88},
  "chequeos": [
    {"nombre": "Corriente nominal", "donde": "Tabla 3", "informe": 15.3, "unidad": "A",
     "formula": "P / (sqrt(3) * U * cosphi * eta)", "guardar_como": "In"},
    {"nombre": "Arranque en estrella-triángulo", "informe": 34.5, "unidad": "A", "formula": "6.8 * In / 3", "tol": 2}
  ]
}
```
`python verificar_numeros.py chequeos.json` (o `demo`). `guardar_como` deja el valor recalculado para los chequeos siguientes; `tol` es la tolerancia en % (por defecto 1). Sale con código 1 si hay algo para revisar.

## Qué se entrega
1. **Tabla de correcciones**, de lo más grave a lo menos grave:

| # | Gravedad | Dónde | Dice | Debería decir | Por qué (cuenta o fuente) |
|---|---|---|---|---|---|

2. Lo verificado y correcto (una línea por bloque: "cálculos del punto 3 verificados").
3. Lo que no se pudo verificar y por qué (falta el libro, dato sin fuente).
4. Preguntas probables de la defensa con su respuesta corta.

Si además se corrige el trabajo: aplicar solo lo confirmado, mantener el formato del archivo y dejar un registro de cambios (dónde, antes, después, motivo). Lo dudoso se marca para que lo decida el autor o lo consulte con el profesor.

## Errores de la revisión misma
- Revisar "por arriba" y dar todo por bueno: cada número se recalcula.
- Corregir lo que estaba bien por no tener la fuente: si no se puede verificar, se dice, no se cambia.
- Cambiar criterios que fijó la cátedra (por ejemplo, un límite de caída de tensión distinto del de la norma): mandan los de la cátedra.
