# Instrumentos de medición e incertidumbre

Leer para explicar cómo se lee un calibre o un micrómetro, qué errores tiene cada uno, cómo se usan el comparador, las galgas y los bloques patrón, o para calcular la incertidumbre de una medida y decidir si una pieza cumple. Las cuentas están en `scripts/tolerancias.py` (subcomandos `nonio`, `micrometro` e `incertidumbre`; el `demo` las comprueba). Los números de norma de los instrumentos no se pudieron confirmar: van marcados (verificar en la norma vigente).

## Calibre (pie de rey)

- Partes: regla fija graduada en mm, cursor con el nonio, bocas de exteriores, orejetas de interiores, varilla de profundidad y tornillo de bloqueo.
- Nonio: n divisiones del nonio ocupan n − 1 divisiones de la regla (o 2·n − 1 en el nonio alargado, más fácil de leer). La apreciación es la diferencia entre una división de la regla y una del nonio: a = d/n (d = 1 mm). Con 10, 20 y 50 divisiones: 0,1 · 0,05 · 0,02 mm.
- Lectura, en tres pasos:
  1. Milímetros enteros: la última línea de la regla que quedó antes del cero del nonio.
  2. Buscar la línea del nonio que coincide exactamente con una línea de la regla (cualquiera).
  3. Lectura = enteros + número de esa línea × a.
- Ejemplos: el cero pasó el 23 y coincide la línea 37 de un nonio de 50 → 23 + 37·0,02 = 23,74 mm. Con un nonio de 20: 41 + 7·0,05 = 41,35 mm (`python tolerancias.py nonio --n 20 --entero 41 --linea 7`).
- Antes de medir: limpiar las bocas, cerrarlas y comprobar que el cero del nonio coincida con el de la regla (en los digitales, poner a cero).

Errores del calibre:

- **Paralaje**: leer con el ojo inclinado desplaza la coincidencia aparente. Mirar perpendicular a la escala, a la altura de la línea.
- **Abbe**: la escala está corrida una distancia h de la línea de medición; si la boca móvil se inclina un ángulo θ por juego del cursor o por apretar, el error es e = h·sen θ ≈ h·θ (θ en radianes). Con h = 25 mm y θ = 0,02°: e = 25·sen 0,02° = 0,0087 mm, casi 9 µm: cerca de la mitad de la apreciación de un calibre de 0,02 mm. Por eso se mide con la pieza lo más adentro posible de las bocas, cerca de la regla, y sin forzar. El micrómetro tiene el tornillo en línea con la pieza (cumple el principio de Abbe).
- **Fuerza**: apretar de más deforma las bocas y la pieza; el calibre no tiene trinquete.
- **Temperatura**: las medidas de las normas valen a 20 °C (ISO 1, verificar en la norma vigente); la pieza recién mecanizada está más caliente. Dilatación: ΔL = α·L·ΔT, con α del material (dato del fabricante o de tablas).
- Bocas gastadas o con rebabas, pieza sucia o con viruta, medir en una zona con chaflán.

Norma de calibres: ISO 13385-1 (verificar en la norma vigente).

## Micrómetro

- Tornillo de paso p = 0,5 mm y tambor de 50 divisiones: a = p/50 = 0,01 mm. Con un nonio de 10 divisiones en el cilindro: 0,001 mm.
- Lectura: escala del cilindro (milímetros arriba de la línea de referencia y medios milímetros abajo) + división del tambor que coincide con la línea × 0,01. Ejemplo: se ven 12 mm y el medio milímetro, y el tambor marca 28 → 12,5 + 28·0,01 = 12,78 mm (`python tolerancias.py micrometro --escala 12.5 --tambor 28`).
- Uso: limpiar las caras de medición, comprobar el cero (cerrado en el de 0 a 25 mm, con la varilla o un bloque patrón en los de 25 a 50 mm y siguientes), cerrar siempre con el trinquete para medir con la misma fuerza, leer con el tambor quieto y medir en dos direcciones a 90° para ver la ovalización.
- Cada micrómetro cubre 25 mm (0 a 25, 25 a 50…).

Norma de micrómetros de exteriores: ISO 3611 (verificar en la norma vigente).

## Comparador (reloj comparador)

- Mide la diferencia respecto de una referencia (bloque patrón, pieza patrón o mármol), no la medida absoluta. Apreciación habitual de 0,01 mm (también los hay de 0,001 mm).
- Usos: oscilación de un eje (girarlo entre puntas o en el torno y leer la diferencia entre la indicación mayor y la menor), planitud y paralelismo sobre un mármol, centrado de una pieza en el plato, y control de una serie contra una pieza patrón.
- Montaje: soporte rígido y corto, palpador perpendicular a la superficie y con algo de precarga; poner a cero sobre la referencia.

Norma: ISO 463 (verificar en la norma vigente).

## Galgas y calibres fijos

- **Galgas de espesores (sondas)**: láminas de espesor marcado para medir juegos (holguras de cojinetes, válvulas, alineación de acoplamientos).
- **Calibres pasa / no pasa**: tampón para agujeros y herradura o anillo para ejes. El lado PASA reproduce el límite de máximo material (Dmín del agujero, dmáx del eje) y tiene que entrar; el lado NO PASA reproduce el de mínimo material (Dmáx, dmín) y no tiene que entrar. Dicen si la pieza está dentro de la tolerancia sin dar un número: sirven para series. Norma ISO 1938-1 (verificar en la norma vigente).
- Galgas de radios y peines de roscas: comparan la forma.

## Bloques patrón

- Bloques de acero o cerámica con dos caras planas y paralelas a una distancia nominal muy exacta. Se adhieren entre sí deslizándolos con presión para formar una medida, y se usan para calibrar y poner a cero instrumentos.
- Armado de una medida: empezar por la última cifra decimal y usar la menor cantidad de bloques. 41,125 mm = 1,005 + 1,12 + 9 + 30 (si el juego tiene esos bloques).
- Calidades: grados K, 0, 1 y 2 de ISO 3650, de más exacto a menos (verificar en la norma vigente). Manipularlos con guantes o pinzas para no calentarlos, limpiarlos y aceitarlos al guardar.

## Elección del instrumento

La apreciación tiene que ser bastante más chica que la tolerancia que se verifica; un criterio orientativo de taller es la décima parte (verificar el que pida la cátedra o el cliente). Ejemplo: un eje Ø25 g6 tiene 13 µm de tolerancia: un calibre de 0,02 mm no alcanza; hace falta un micrómetro de 0,001 mm o un comparador con un bloque patrón. Para Ø25 h11 (130 µm), un calibre de 0,02 mm alcanza.

## Incertidumbre de la medición (GUM, JCGM 100:2008)

1. Repetir la medición n veces en las mismas condiciones: media x̄ = Σx/n y desvío s = √(Σ(x − x̄)²/(n − 1)).
2. Tipo A (repetibilidad): uA = s/√n.
3. Tipo B (otra información, distribución rectangular): resolución δ → uδ = δ/(2·√3); error máximo ±a del certificado o de la ficha → ue = a/√3; si el certificado da U con su k → u = U/k.
4. Combinada: uc = √(uA² + uδ² + ue² + …).
5. Expandida: U = k·uc, con k = 2 (nivel de confianza de aproximadamente 95 % con distribución normal).
6. Resultado: x̄ ± U, con U de una o dos cifras significativas y la media redondeada a la misma posición.

Ejemplo (datos del ejemplo): eje Ø25 g6 medido cinco veces con un micrómetro de 0,001 mm y error máximo ±0,002 mm: 24,986 · 24,988 · 24,987 · 24,985 · 24,988 mm.

- x̄ = 24,9868 mm; s = 0,00130 mm; uA = 0,00130/√5 = 0,00058 mm.
- uδ = 0,001/(2·√3) = 0,00029 mm; ue = 0,002/√3 = 0,00115 mm.
- uc = √(0,00058² + 0,00029² + 0,00115²) = 0,00133 mm; U = 2·0,00133 = 0,0027 mm.
- Resultado: (24,9868 ± 0,0027) mm, k = 2. El intervalo 24,9841 a 24,9895 mm queda entero dentro de 24,980 a 24,993 mm: el eje cumple.

`python tolerancias.py incertidumbre "24.986 24.988 24.987 24.985 24.988" --res 0.001 --emax 0.002`

Si el intervalo x̄ ± U cruza un límite de la tolerancia, la conformidad no es concluyente con esa regla: cómo declarar la regla de decisión, la propagación a magnitudes calculadas y la planilla del informe están en **ensayos-materiales** (archivo `references/informe-laboratorio.md` de esa skill).
