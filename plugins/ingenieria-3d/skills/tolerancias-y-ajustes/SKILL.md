---
name: tolerancias-y-ajustes
description: "Tolerancias dimensionales, ajustes y metrología con calculadora en Python: sistema ISO 286 (grados IT01 a IT18, desviaciones fundamentales, agujero único y eje único, límites, juego y aprieto máximo y mínimo, tipo de ajuste), ajustes recomendados (H7/g6, H7/h6, H7/k6, H7/n6, H7/p6, H7/s6, H8/f7, H11/c11), tolerancias generales ISO 2768-1 y 2768-2, tolerancias geométricas ISO 1101, rugosidad Ra y Rz (ISO 21920), cadenas de cotas por peor caso y RSS, calibre con nonio, micrómetro, comparador, galgas, bloques patrón e incertidumbre de medición (GUM). Usar cuando se pregunte qué ajuste uso, cómo se acota un H7/g6, la tolerancia de un eje o de un agujero, cómo calcular juego y aprieto, la tolerancia general ISO 2768, la rugosidad Ra de una superficie, tolerancias geométricas, una cadena de cotas, cómo se lee un calibre o un micrómetro, la incertidumbre de medición o un tema de metrología."
---

# Tolerancias, ajustes y metrología

`scripts/tolerancias.py` (Python 3.9+, solo biblioteca estándar, acepta coma decimal) calcula límites y ajustes ISO 286, tolerancias generales ISO 2768, cadenas de cotas, la incertidumbre de una medición y la lectura del calibre y del micrómetro, e imprime fórmula, reemplazo y resultado para la memoria de cálculo (presentación en **calculos-ingenieria**). Tablas completas y fuentes: [references/tablas.md](references/tablas.md), para citar un valor o calcular a mano. Instrumentos e incertidumbre paso a paso: [references/metrologia.md](references/metrologia.md).

Unidades: cotas en mm; IT, desviaciones, juegos y aprietos en µm (1 µm = 0,001 mm). Cómo se dibujan, acotan y rotulan en un plano IRAM: **planos-tecnicos**. Procesos y datos de corte para llegar a la medida: **cnc-mecanizado**.

```
python tolerancias.py ajuste 25 H7/g6                          límites, juego o aprieto y tipo de ajuste
python tolerancias.py it 25 7                                  IT7 de 25 mm = 21 µm
python tolerancias.py general 85 m                             ISO 2768-m: ±0,3 mm
python tolerancias.py cadena "+50:0.1 -20:0.05 -29.8:0.05"     peor caso y RSS
python tolerancias.py incertidumbre "24.986 24.988 24.987" --res 0.001 --emax 0.002
python tolerancias.py nonio --n 50 --entero 23 --linea 37      lectura del calibre: 23,74 mm
```

## Método para elegir y acotar un ajuste

1. **Función**: ¿gira o desliza (juego), se centra y se desarma (incierto) o transmite esfuerzo y queda fijo (aprieto)?
2. **Sistema**: agujero único (agujero H y se elige el eje; lo habitual, porque un agujero se termina con herramientas y calibres de medida fija y un eje se tornea a cualquier medida) o eje único (eje h y se elige el agujero; por ejemplo, una barra calibrada que lleva varias piezas).
3. **Ajuste**: partir de la tabla de recomendados y calcularlo con `ajuste D H7/g6`.
4. **Control**: el juego mínimo tiene que alcanzar para el lubricante y la dilatación; el aprieto máximo no puede romper el cubo ni impedir el montaje.
5. **Plano**: nominal y clase, y las desviaciones si conviene: Ø25 H7 (+0,021/0). Las cotas sin tolerancia quedan cubiertas por la tolerancia general del rótulo (ISO 2768).
6. **Medición**: un instrumento de apreciación mucho más chica que la tolerancia y el resultado con su incertidumbre.

## Sistema ISO 286

- **Grado IT** (ISO 286-1:2010, tabla 1): tolerancia fundamental según el escalón de la cota; 20 grados, de IT01 (el más fino) a IT18. Ejemplos de 18 a 30 mm: IT6 = 13 µm, IT7 = 21 µm, IT8 = 33 µm, IT11 = 130 µm.
- **Tolerancia**: IT = Dmáx − Dmín = ES − EI (agujero) = es − ei (eje).
- **Desviación fundamental**: la letra ubica la zona respecto de la cota nominal (línea de cero); mayúsculas para agujeros (A a ZC) y minúsculas para ejes (a a zc).
  - Ejes a a h: la tabla da es (h: es = 0) y ei = es − IT. Ejes k a zc: la tabla da ei y es = ei + IT. js y JS: ±IT/2.
  - Agujeros A a H: espejo del eje de la misma letra, EI = −es (H: EI = 0).
  - Agujeros K, M y N hasta IT8 y P a ZC hasta IT7: ES = −ei + Δ, con Δ = ITn − ITn−1 (Δ = 0 hasta 3 mm). Por encima de IT7, P: ES = −ei.
  - Ejemplo: K7 de 18 a 30 mm: ei(k) = +2 µm y Δ = IT7 − IT6 = 21 − 13 = 8 µm → ES = −2 + 8 = +6 µm; EI = 6 − 21 = −15 µm.
- **Notación**: Ø25 H7/g6 = agujero H7 con eje g6 (agujero único); Ø25 G7/h6 = eje único.
- **Juego y aprieto**: Jmáx = Dmáx − dmín = ES − ei; Jmín = Dmín − dmáx = EI − es. El aprieto es juego negativo: Amáx = −Jmín y Amín = −Jmáx.
- **Tipo**: con juego si Jmín ≥ 0; con aprieto si Jmáx ≤ 0; si no, incierto (de transición: según las piezas sale con juego o con aprieto).
- **Tolerancia del ajuste**: Jmáx − Jmín = IT del agujero + IT del eje.
- **Origen de la tabla**: para IT5 a IT18, redondeo de k·i, con i = 0,45·∛D + 0,001·D [µm] y D la media geométrica del escalón [mm]; k = 7, 10, 16, 25, 40, 64 y 100 para IT5 a IT11. Comprobado con código: difiere de la tabla hasta un 8,4 % por los redondeos (más de 3 mm). Siempre se usa la tabla.

**Ejemplo resuelto** (`ajuste 25 H7/g6`, un buje que gira sobre un eje): escalón de 18 a 30 mm. Agujero H7: IT7 = 21 µm, EI = 0, ES = +21 µm → 25,000 a 25,021 mm. Eje g6: IT6 = 13 µm, es = −7 µm, ei = −7 − 13 = −20 µm → 24,980 a 24,993 mm. Jmáx = 21 − (−20) = 41 µm; Jmín = 0 − (−7) = 7 µm: **ajuste con juego** de 0,007 a 0,041 mm; tolerancia del ajuste 21 + 13 = 34 µm. En el plano: Ø25 H7 (+0,021/0) y Ø25 g6 (−0,007/−0,020).

**Tablas del script**: cotas de más de 0 hasta 500 mm; IT01 a IT18; ejes c, d, e, f, g, h, js, k (IT4 a IT7), m, n, p, r y s; agujeros F, G, H, JS, K y N (IT3 a IT8) y P (desde IT3). Lo demás (otras letras, cotas de más de 500 mm): ISO 286-2 (verificar en la norma vigente). Las tablas se contrastaron con código contra cinco reproducciones publicadas de ISO 286 y JIS B 0401 (detalle en [references/tablas.md](references/tablas.md)).

## Ajustes recomendados (agujero único)

| Ajuste | Tipo | A Ø25 mm: Jmín a Jmáx [µm] | Uso típico |
|---|---|---|---|
| H11/c11 | juego amplio | +110 a +370 | pivotes, trabas y piezas expuestas a corrosión, calor o suciedad, donde la precisión no importa |
| H8/f7 | juego chico de giro | +20 a +74 | ejes y husillos que giran, varillas que deslizan; precisión moderada |
| H7/g6 | deslizante | +7 a +41 | juego mínimo y precisión alta: guías de ejes, engranajes que deslizan, muñones de cigüeñal |
| H7/h6 | posicionamiento con juego | 0 a +34 | se monta sin fuerza y desliza lubricado: guiado preciso de ejes, centrado de piezas que se desarman |
| H7/k6 | incierto | −15 a +19 | juego o aprieto casi nulos, se monta con maza de goma: cubos, engranajes, poleas, bujes |
| H7/n6 | incierto apretado | −28 a +6 | aprieto chico, se monta con prensa liviana: tapones, bujes, inducidos sobre ejes |
| H7/p6 | aprieto liviano | −35 a −1 | se monta y desmonta con prensa en frío: cubos, bujes y retenes que se pueden separar |
| H7/s6 | aprieto medio | −48 a −14 | prensa con mucha fuerza o montaje en caliente: engranajes, bujes y ejes de montaje permanente |

Tipo y uso según [Wikipedia, «Engineering fit»](https://en.wikipedia.org/wiki/Engineering_fit) y [RoyMech](https://roymech.org/Useful_Tables/ISO_Tolerances.html) (coinciden); juegos calculados con el script e iguales a los de BS 4500:1969 en el Machinery's Handbook. Asientos de rodamientos: usar las tablas del fabricante del rodamiento, porque los aros tienen tolerancias propias; vida y selección en **elementos-de-maquinas**.

## Tolerancias generales (ISO 2768)

Valen para toda cota sin tolerancia indicada cuando el rótulo dice, por ejemplo, «ISO 2768-mK» (m: cotas lineales y angulares de la parte 1; K: tolerancias geométricas de la parte 2).

ISO 2768-1:1989, cotas lineales [mm]:

| Clase | 0,5 a 3 | 3 a 6 | 6 a 30 | 30 a 120 | 120 a 400 | 400 a 1000 | 1000 a 2000 | 2000 a 4000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| f (fina) | ±0,05 | ±0,05 | ±0,1 | ±0,15 | ±0,2 | ±0,3 | ±0,5 | — |
| m (media) | ±0,1 | ±0,1 | ±0,2 | ±0,3 | ±0,5 | ±0,8 | ±1,2 | ±2 |
| c (gruesa) | ±0,2 | ±0,3 | ±0,5 | ±0,8 | ±1,2 | ±2 | ±3 | ±4 |
| v (muy gruesa) | — | ±0,5 | ±1 | ±1,5 | ±2,5 | ±4 | ±6 | ±8 |

Fuentes: [Wikipedia en alemán, «ISO 2768»](https://de.wikipedia.org/wiki/ISO_2768) y el paquete standards-mcp-server (coinciden). Aristas matadas, ángulos e ISO 2768-2 (H, K, L: rectitud, planitud, perpendicularidad, simetría y oscilación): [references/tablas.md](references/tablas.md); la parte 2 se contrastó con una sola fuente (verificar en la norma vigente). Script: `general 30 c --tipo angulo`, `general 250 K --tipo planitud`.

## Tolerancias geométricas (ISO 1101)

| Característica | Símbolo | Grupo | Referencia (dato) | Qué controla |
|---|---|---|---|---|
| Rectitud | ⏤ | forma | no | una línea o un eje no se aparta de una recta |
| Planitud | ⏥ | forma | no | una superficie queda entre dos planos paralelos a distancia t |
| Redondez (circularidad) | ○ | forma | no | cada sección de un cilindro queda entre dos circunferencias concéntricas |
| Cilindricidad | ⌭ | forma | no | toda la superficie queda entre dos cilindros coaxiales |
| Forma de una línea | ⌒ | forma u orientación y ubicación | no / sí | perfil de una línea contra el perfil teórico |
| Forma de una superficie | ⌓ | forma u orientación y ubicación | no / sí | superficie contra la superficie teórica |
| Paralelismo | ∥ | orientación | sí | paralela a la referencia, dentro de la zona t |
| Perpendicularidad | ⟂ | orientación | sí | a 90° de la referencia |
| Inclinación (angularidad) | ∠ | orientación | sí | al ángulo teórico respecto de la referencia |
| Posición | ⌖ | ubicación | sí | el elemento (eje de un agujero) dentro de una zona alrededor de su posición teórica |
| Concentricidad y coaxialidad | ◎ | ubicación | sí | el centro o el eje coincide con el de la referencia |
| Simetría | ⌯ | ubicación | sí | el plano medio coincide con el de la referencia |
| Oscilación circular | ↗ | oscilación | sí | variación al girar una vuelta alrededor del eje de referencia (se mide con comparador) |
| Oscilación total | ⌰ | oscilación | sí | igual, recorriendo toda la superficie |

Fuentes: [Wikipedia, «Geometric dimensioning and tolerancing»](https://en.wikipedia.org/wiki/Geometric_dimensioning_and_tolerancing) (símbolos) y [Wikipedia en alemán, «Form- und Lagetoleranz»](https://de.wikipedia.org/wiki/Form-_und_Lagetoleranz), que cita DIN EN ISO 1101:2017 y dice que todas, salvo las de forma, necesitan al menos una referencia. ASME Y14.5-2018 eliminó la concentricidad y la simetría; en ISO 1101 siguen figurando (verificar en la norma vigente). En IRAM, IRAM 4515 (ver **normas-tecnicas-ar**).

Cómo se indican: un cuadro rectangular con casillas, de izquierda a derecha: símbolo, valor de la tolerancia en mm (con Ø delante si la zona es cilíndrica, como en la posición de un eje) y letras de las referencias por orden de prioridad (A, B, C). La flecha va a la superficie si se controla la superficie, o en línea con la flecha de la cota si se controla el eje o el plano medio. La referencia se marca con un triángulo sobre la superficie unido a la letra en un recuadro. Casos especiales y modificadores: ISO 1101 e ISO 5459 (verificar en la norma vigente); el dibujo de los cuadros, en **planos-tecnicos**.

## Rugosidad

- **Ra** = (1/l)·∫|z(x)| dx: media aritmética de los apartamientos del perfil respecto de la línea media, en µm. Es el parámetro más usado.
- **Rz**: altura máxima del perfil (pico más alto + valle más profundo) en cada longitud de muestreo, promediada en la longitud de evaluación. RzJIS (promedio de cinco picos y cinco valles) es otra definición: no comparar valores de Rz sin saber con qué norma se midieron. Fuente: [Wikipedia, «Surface roughness»](https://en.wikipedia.org/wiki/Surface_roughness).
- **Normas**: la indicación en el plano es [ISO 21920-1:2021](https://www.iso.org/standard/72196.html) («Indication of surface texture», diciembre de 2021); [ISO 1302:2002](https://www.iso.org/standard/28089.html) figura retirada en el catálogo de ISO. Términos y parámetros: [ISO 21920-2:2021](https://www.iso.org/standard/72226.html). En IRAM, IRAM 4517 (símbolos del terminado superficial; edición vigente: verificar en **normas-tecnicas-ar**).
- En el plano: el símbolo gráfico de terminado superficial con el parámetro y su valor, por ejemplo Ra 1,6; las variantes del símbolo (remoción de material, proceso, dirección de las marcas) están en la norma de indicación (verificar en ISO 21920-1 o IRAM 4517 vigentes). Los grados N de planos viejos (N7 = Ra 1,6 µm) están en [references/tablas.md](references/tablas.md).
- **Ra típica por proceso**: no se confirmó una tabla con fuente (verificar). Tomar el Ra alcanzable del catálogo de la herramienta o de una tabla de procesos con su fuente, y confirmarlo midiendo con rugosímetro.

## Cadenas de cotas

La cota de cierre (resultante) es la suma de las cotas que la aumentan menos las que la disminuyen. Con Ti el ancho total de cada tolerancia:

- **Peor caso**: T = ΣTi; máximo = Σ máximos (+) − Σ mínimos (−); mínimo = Σ mínimos (+) − Σ máximos (−). Asegura el 100 % de los conjuntos.
- **Estadístico (RSS)**: T = √(ΣTi²), centrado en el valor medio. Supone cotas independientes, centradas, con distribución normal y tolerancia = ±3σ: queda adentro el 99,73 % de los conjuntos (comprobado con una simulación en el `demo`).

Ejemplo (`cadena "+50:0.1 -20:0.05 -29.8:0.05"`), juego axial de un buje entre dos resaltos: cierre = 50 − 20 − 29,8 = 0,200 mm. Peor caso: T = 0,2 + 0,1 + 0,1 = 0,4 mm → de 0,000 a 0,400 mm (puede quedar sin juego). RSS: T = √(0,04 + 0,01 + 0,01) = 0,245 mm → de 0,078 a 0,322 mm. Con pocas cotas o piezas únicas, el peor caso; con series grandes, el RSS. Con `--min` y `--max` el script compara con el requisito.

## Instrumentos (resumen; detalle en [references/metrologia.md](references/metrologia.md))

- **Calibre**: apreciación a = d/n (d división de la regla, n divisiones del nonio): 0,1 · 0,05 · 0,02 mm. Lectura = mm de la regla antes del cero del nonio + línea que coincide × a (23 + 37·0,02 = 23,74 mm).
- **Micrómetro**: a = paso/divisiones del tambor = 0,5/50 = 0,01 mm. Lectura = cilindro (mm y medios mm) + tambor × 0,01 (12,5 + 28·0,01 = 12,78 mm).
- **Paralaje**: leer mirando perpendicular a la escala.
- **Abbe**: si la escala está a h de la línea de medida y la boca se inclina θ, e = h·sen θ (25 mm y 0,02° → 0,0087 mm). El micrómetro cumple el principio de Abbe y el calibre no.
- **Comparador**: mide diferencias contra un patrón (0,01 mm): oscilación, planitud y paralelismo, centrado.
- **Galgas y calibres pasa/no pasa**: el PASA es el límite de máximo material (Dmín del agujero, dmáx del eje) y tiene que entrar; el NO PASA no.
- **Bloques patrón**: arman medidas de referencia (41,125 = 1,005 + 1,12 + 9 + 30) para calibrar y poner a cero.

## Incertidumbre de medición (GUM, JCGM 100:2008)

Con n lecturas: media x̄, desvío s, uA = s/√n; resolución δ → uδ = δ/(2·√3); error máximo ±a → ue = a/√3; uc = √(uA² + uδ² + ue²); U = k·uc con k = 2 (aproximadamente 95 %). Ejemplo (`incertidumbre`): cinco lecturas de un eje Ø25 g6 con micrómetro de 0,001 mm y ±0,002 mm → (24,9868 ± 0,0027) mm, k = 2; el intervalo queda entero dentro de 24,980 a 24,993 mm: cumple. Procedimiento completo, propagación y regla de decisión: **ensayos-materiales**.

## Normas IRAM

- Dibujo y tolerancias: IRAM 4515 (tolerancias geométricas), IRAM 4550 (acotación y tolerancias funcionales), IRAM 4575 (principio fundamental de tolerancia) e IRAM 4517 (terminado superficial); títulos y fuente en **normas-tecnicas-ar**.
- No se confirmó un número IRAM equivalente a ISO 286 ni a ISO 2768. Si un apunte cita IRAM 5001 o IRAM 4512 para ajustes, confirmar número, título y vigencia en el catálogo IRAM antes de citarlas (verificar).

## Errores frecuentes

- Confundir qué da la tabla: en ejes a a h es la desviación superior (negativa); en k a zc, la inferior.
- Calcular K, N o P de grado bajo sin Δ, o sumarle Δ a P8 o a un eje.
- Elegir mal el escalón: «de más de 18 hasta 30» incluye el 30; 18 mm va en el escalón anterior.
- Mezclar µm con mm (21 µm = 0,021 mm), o restar desviaciones sin el signo.
- Tomar H7/k6 o H7/n6 como aprieto: son inciertos y pueden salir con juego.
- Pedir tolerancias más finas que las necesarias (encarecen) o verificar 13 µm con un calibre de 0,02 mm.
- Usar el RSS con dos o tres cotas, o con cotas no centradas.
- Leer el calibre torcido (paralaje), medir lejos de la regla (Abbe) o con la pieza caliente.
- Comparar Rz de definiciones distintas o poner Ra sin el símbolo de terminado.

## Verificación

`python tolerancias.py demo` termina en `DEMO OK`: reproduce los ejemplos de esta página y los compara con valores publicados (ajustes a 50 mm de Wikipedia, K7 de 300 mm de RoyMech, juegos de BS 4500 a 25 y 480 mm, clases sueltas de JIS B 0401), comprueba la regla ×10 de la tabla IT, ISO 2768, la cadena con una simulación de 100 000 conjuntos, la incertidumbre, el nonio y el error de Abbe. Para una entrega, una revisión independiente con **revision-tecnica**.
