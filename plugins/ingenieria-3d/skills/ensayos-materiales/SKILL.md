---
name: ensayos-materiales
description: "Ensayos de materiales de laboratorio para TPs e informes, con calculadora en Python: tracción (curva tensión-deformación, módulo E, Rp0,2, ReH y ReL, Rm, A y Z, probetas proporcionales, ISO 6892-1 e IRAM-IAS U 500-102), dureza Brinell (HBW, índice de carga, validez de la huella, espesor y distancias, ISO 6506-1), Rockwell (HRC, HRB) y Vickers (HV), impacto Charpy y transición dúctil-frágil, doblado y plegado (ISO 7438, barras ADN 420 de IRAM-IAS U 500-528), fatiga (curva S-N) y ensayos no destructivos (tintas penetrantes, partículas magnéticas, ultrasonido, radiografía, corrientes inducidas). Usar cuando se pida calcular o explicar un ensayo de tracción, de dureza, Charpy, de doblado o de fatiga, procesar los datos de la máquina de ensayos, armar el informe de laboratorio con incertidumbre o elegir un END."
---

# Ensayos de materiales

Ensayos mecánicos de laboratorio (tracción, dureza, impacto, doblado, fatiga) y ensayos no destructivos, con sus cálculos y su informe. El formato general del documento (portada, índice, tablas, bibliografía) está en la skill **informe-tecnico**; acá va lo propio de un informe de ensayo. Las normas citadas son ISO; si la cátedra usa IRAM o ASTM, manda la de la cátedra.

## Método (siempre)

1. **Norma y edición**: anotar la norma del método (y la de producto si hay que aceptar o rechazar) y su año. Si no se pudo confirmar un valor en la norma vigente, decirlo.
2. **Probeta**: material, estado (laminado, recocido, templado), croquis y dimensiones **medidas**: al menos tres lecturas, promedio, e instrumento con su resolución.
3. **Datos crudos** en tabla con unidades; conservar el archivo original de la máquina (CSV) como anexo.
4. **Cálculos**: fórmula → reemplazo → resultado con unidades, hechos con código. Cifras según la incertidumbre, no las que da la calculadora.
5. **Comparar** con la norma de producto o con valores de referencia con fuente, y **concluir** (cumple / no cumple, qué indica del material).

## Calculadora

`scripts/ensayos.py` (Python 3.9+, solo biblioteca estándar; acepta coma decimal). `python scripts/ensayos.py demo` resuelve los ejemplos de esta skill y `demo --csv archivo.csv` guarda el CSV de tracción del ejemplo para ver el formato.

```
python scripts/ensayos.py brinell --kgf 3000 --D 10 --d1 4,10 --d2 4,14 --material acero
python scripts/ensayos.py brinell --material cobre --D 5 --sugerir
python scripts/ensayos.py vickers --kgf 30 --d1 0,512 --d2 0,520
python scripts/ensayos.py traccion ensayo.csv --d0 10 --L0 50 --Lu 62,5 --du 6,2 --material acero
python scripts/ensayos.py charpy --E0 300 --alfa 150 --beta 100
```

El CSV de tracción lleva fuerza y alargamiento en dos columnas, con o sin encabezado; acepta `;` con coma decimal (Excel en castellano), `,` o tabulación. Opciones: `--unidad-fuerza kN`, `--col-fuerza 3`, `--rango 0,1 0,4` (tramo para E como fracción de Rm), `--E-ref 205000` (sin extensómetro).

## Tracción (ISO 6892-1)

Norma de método: ISO 6892-1:2019 (temperatura ambiente). En Argentina, el método de ensayo de tracción de productos de acero es la IRAM-IAS U 500-102 (verificar en su edición vigente la correspondencia con ISO 6892-1).

**Probeta proporcional**: L0 = k·√S0 con k = 5,65 y L0 de al menos 15 mm; si con 5,65 queda más corta, se usa 11,3 o una probeta no proporcional. En probetas redondas 5,65·√S0 = 5·d0 (d0 = 10 mm → L0 = 50 mm). Con k = 11,3 se informa A11,3, y con no proporcionales A80mm, etc.

| Magnitud | Fórmula | Unidad |
|---|---|---|
| Tensión (ingenieril) | σ = F/S0, con S0 = π·d0²/4 o a0·b0 | MPa = N/mm² |
| Deformación | ε = ΔL/L0 | adimensional o % |
| Módulo de elasticidad | E = Δσ/Δε en el tramo recto | MPa o GPa |
| Límite de fluencia superior / inferior | ReH = máximo antes de la primera caída; ReL = mínimo de la meseta sin el transitorio inicial | MPa |
| Límite convencional 0,2 % | Rp0,2: tensión con deformación plástica de 0,2 % | MPa |
| Resistencia a la tracción | Rm = Fmax/S0 | MPa |
| Alargamiento total a fuerza máxima | Agt (elástico + plástico) | % |
| Alargamiento después de la rotura | A = (Lu − L0)/L0·100 | % |
| Estricción | Z = (S0 − Su)/S0·100 | % |

- **Rp0,2 gráfico**: trazar una recta paralela al tramo elástico que corte el eje de deformaciones en ε = 0,2 % (corrido desde el pie real de la curva) y leer la tensión donde corta la curva. Si el material tiene meseta de fluencia (acero de bajo carbono), se informan ReH y ReL, no Rp0,2.
- **A** se mide juntando los dos trozos de la probeta y midiendo Lu entre las marcas. Si la rotura queda cerca de una marca (a menos de L0/3), el valor puede no ser válido (verificar en la norma vigente el criterio y el método de corrección).

**Ejemplo resuelto** (el del demo): probeta redonda d0 = 10 mm → S0 = 78,54 mm²; L0 = 50 mm (k = 5,64: proporcional corta).
Fmax = 39,27 kN → Rm = 39270/78,54 = 500,0 MPa. E (regresión entre 10 y 40 % de Rm) = 205,0 GPa; a mano con un punto del tramo recto: F = 10 kN → σ = 127,3 MPa con ΔL = 0,03105 mm → ε = 0,000621 → E = 205 GPa. Rp0,2 = 350,0 MPa (Rp0,2/Rm = 0,70). Agt = 17,3 %. Lu = 62,5 mm → A = 25,0 %. du = 6,2 mm → Su = 30,19 mm² → Z = 61,6 %.

**Sin extensómetro**: si el alargamiento viene del travesaño, la curva incluye la deformación de la máquina y de las mordazas, y E sale muy bajo (en acero, mucho menos que los ≈ 200 GPa reales). Ese E **no se informa**. Rm no cambia; Rp0,2 y Agt son estimaciones; A se informa medido sobre la probeta. `--E-ref` corrige el tramo elástico para graficar.

E de referencia, orientativos (tablas de propiedades a 21 °C): acero al carbono ≈ 203 GPa; inoxidable austenítico ≈ 195 GPa; aluminio y sus aleaciones ≈ 69 GPa; cobre ≈ 110 GPa.

Barras ADN 420 (IRAM-IAS U 500-528), valores característicos mínimos según hojas técnicas de fabricantes: fluencia 420 MPa, resistencia 500 MPa, alargamiento de rotura 12 % y Rm/Re de 1,10 (verificar en la edición vigente de la norma).

Detalle (curva, verdadera vs ingenieril, cómo graficar, velocidad y temperatura): `references/traccion.md`.

## Dureza

| | Brinell (ISO 6506-1) | Rockwell (ISO 6508-1) | Vickers (ISO 6507-1) |
|---|---|---|---|
| Indentador | Bola de carburo de tungsteno de 10, 5, 2,5 o 1 mm | Cono de diamante de 120° (HRC) o bola de 1,5875 mm (HRB) | Pirámide de diamante de base cuadrada, 136° |
| Se mide | Diámetro de la huella (dos lecturas a 90°) | Profundidad permanente h | Diagonales de la huella |
| Resultado | HBW = 0,102·2F/(π·D·(D − √(D² − d²))), F en N | HR = N − h/0,002 (h en mm); N = 100 cono, 130 bola | HV = 0,1891·F/d² (F en N, d en mm) |
| Espesor mínimo | 8 veces la profundidad | 10·h (cono), 15·h (bola) | 1,5·d |
| Se informa | 215 HBW 10/3000 | 59 HRC; 80 HRBW | 209 HV 30 |

**Brinell**:
- Con F en kgf: HB = 2F/(π·D·(D − √(D² − d²))); con F en N se multiplica por 0,102 (= 1/9,80665).
- La fuerza se elige con el índice 0,102·F/D²: **30** para aceros, aleaciones de níquel y de titanio; fundición: 10 (menos de 140 HBW) o 30; cobre y sus aleaciones: 5, 10 o 30 según la dureza; metales livianos: 2,5 a 15; plomo y estaño: 1. Con bola de 10 mm e índice 30 → 29,42 kN (3000 kgf).
- Válido solo si **0,24·D ≤ d ≤ 0,6·D**; si no, se cambia la fuerza o la bola.
- Profundidad h = (D − √(D² − d²))/2; espesor de la pieza ≥ 8·h.
- Distancias: entre centros de huellas ≥ 3·d; del centro al borde ≥ 2,5·d.
- Tiempos: llegar a la fuerza en 2 a 8 s y mantenerla 10 a 15 s (si se mantiene otro tiempo, va en la designación: 600 HBW 1/30/20 = bola de 1 mm, 30 kgf, 20 s). Máximo del método: 650 HBW.
- **Ejemplo**: acero, D = 10 mm, F = 3000 kgf (29,42 kN), d1 = 4,10 mm y d2 = 4,14 mm → d = 4,12 mm (d/D = 0,412, válido) → HBW = 6000/(π·10·0,888) = **215 HBW 10/3000**; h = 0,444 mm → espesor ≥ 3,55 mm; huellas separadas ≥ 12,4 mm y a ≥ 10,3 mm del borde.
- Relación aproximada con la tracción, **solo aceros**: Rm [MPa] ≈ 3,55·HB (HB ≤ 175) o 3,38·HB (HB mayor de 175) → en el ejemplo Rm ≈ 727 MPa. Es una estimación: para convertir formalmente se usan las tablas de ISO 18265.

**Rockwell**: fuerza previa 98,07 N (10 kgf); total 1471 N (150 kgf) en HRC y 980,7 N (100 kgf) en HRB; S = 0,002 mm por unidad. HRC 60 equivale a h = 0,080 mm. Campos de aplicación (tabla 1 de ISO 6508-1): HRC de 20 a 70 (aceros templados); por debajo de 20 HRC se pasa a HRB (aceros blandos, latones). Es rápido y no necesita medir la huella, pero es sensible a la superficie y al apoyo.

**Vickers**: un solo indentador para todo el rango de durezas; la fuerza fija el tipo: F ≥ 49,03 N (HV 5 o más) ensayo Vickers; 1,961 a 49,03 N baja fuerza; menos de 1,961 N microdureza (capas, fases, tratamientos superficiales). Distancias: en acero y cobre ≥ 2,5·d al borde y ≥ 3·d entre centros; en metales livianos, plomo y estaño ≥ 3·d y ≥ 6·d. **Ejemplo**: HV 30 (294,2 N), diagonales 0,512 y 0,520 mm → d = 0,516 mm → HV = 0,1891·294,2/0,516² = **209 HV 30**; espesor ≥ 0,774 mm.

Las escalas no se convierten con fórmulas: se usan las tablas de ISO 18265, que valen para ciertos grupos de materiales. Detalle y tablas: `references/dureza.md`.

## Impacto Charpy (ISO 148-1)

- Probeta de 10 × 10 × 55 mm con entalla en V (45°, 2 mm de profundidad, radio de fondo 0,25 mm) o en U (5 mm, radio 1 mm). Un péndulo la rompe de un golpe en el lado opuesto a la entalla.
- Energía absorbida K = W·L·(cos β − cos α) [J], con W·L = peso del péndulo por distancia al centro de masa, α = ángulo de caída y β = ángulo de subida, desde la vertical. Se informa KV2 o KV8 (entalla en V, percutor de 2 u 8 mm) o KU2, KU8, siempre con la temperatura.
- A temperatura distinta de la ambiente: la probeta, a ±2 °C de la de ensayo, y no más de 5 s entre sacarla del baño y el golpe.
- **Transición dúctil-frágil**: en aceros ferríticos la energía cae fuerte al bajar la temperatura (fractura frágil, brillante, cristalina); los aceros inoxidables austeníticos, el cobre y el aluminio no tienen esa caída. Se informa la curva K-temperatura y la temperatura de transición según el criterio fijado (energía, porcentaje de fractura dúctil o expansión lateral).
- Si K supera el 80 % de la energía inicial del péndulo, el resultado es aproximado: hace falta un péndulo de más energía.
- **Ejemplo**: péndulo de 300 J soltado a α = 150° (W·L = 160,77 J) que sube a β = 100° → K = 160,77·(cos 100° − cos 150°) = 111,3 J.

## Doblado y plegado (ISO 7438)

- La probeta apoya en dos rodillos y un mandril de diámetro D la dobla en el centro hasta el ángulo α que fija la norma de producto; distancia entre apoyos l = (D + 3a) ± a/2, con a = espesor o diámetro, fija durante el ensayo, salvo que la norma de producto fije otra (ISO 7438:2020, 6.2.2; fuentes en `references/charpy-doblado-fatiga-end.md`). Variantes: hasta un ángulo, hasta ramas paralelas o hasta que las ramas se toquen (plegado a fondo, sin mandril).
- Temperatura entre 10 y 35 °C, o (23 ± 5) °C si se pide temperatura controlada. Criterio: el que fije la norma de producto; si no dice nada, que no aparezcan fisuras visibles sin aumento (cláusula 9 de ISO 7438:2020, no leída: verificar en la norma vigente).
- **Barras ADN 420** (IRAM-IAS U 500-528; ADN 420 S soldables: IRAM-IAS U 500-207): doblado a 180° sobre mandril de 3,5·d para d ≤ 25 mm, 5·d para 32 mm y 7·d para 40 mm (hojas técnicas de fabricantes; verificar en la edición vigente de la norma); se acepta si no hay fisuras ni grietas transversales en la zona traccionada.
- Deformación de la fibra exterior ≈ a/(D + a): con mandril 3,5·d, 1/4,5 = 22,2 %, mucho más que el 12 % de alargamiento mínimo: el ensayo exige ductilidad local.
- Trampa: el mandril del ensayo no es el diámetro mínimo de doblado en obra que dan las tablas de los fabricantes.

## Fatiga

- Curva S-N (Wöhler): amplitud de tensión σa contra log N. En aceros se vuelve horizontal desde alrededor de 10⁶ ciclos: ese nivel es el **límite de fatiga**. Los no ferrosos no tienen límite: se da la resistencia a fatiga a un N fijado (para aleaciones de aluminio y de magnesio, 30 a 40 % de Rm a 10⁸ ciclos).
- Estimación para aceros (probeta pulida, flexión rotativa): Se' ≈ 0,5·Rm si Rm ≤ 1400 MPa y 700 MPa si es mayor. Vida finita: recta en log-log entre 0,8·Rm a 10³ ciclos y Se' a 10⁶. Con tensión media, Goodman: 1/n = σa/Se + σm/Rm.
- Ejemplo: Rm = 600 MPa → Se' = 300 MPa; a 10⁵ ciclos Sf ≈ 351 MPa; con σa = 120 MPa y σm = 150 MPa, n = 1,54.
- Normas de ensayo: ISO 1143 (flexión rotativa) e ISO 1099 (axial con fuerza controlada). Una pieza real (rugosidad, tamaño, entallas) tiene un límite menor que la probeta: aplicar los factores de corrección de la bibliografía de diseño.

## Ensayos no destructivos

| Método | Qué detecta | Dónde sirve | Límites | Norma (principios) |
|---|---|---|---|---|
| Visual (VT) | Defectos superficiales, forma, terminación | Todo | Solo lo que se ve | ISO 17637 (soldaduras) |
| Tintas penetrantes (PT) | Discontinuidades **abiertas a la superficie** | Materiales no porosos | No ve lo interno ni lo cerrado; exige limpieza | ISO 3452-1 |
| Partículas magnéticas (MT) | Superficiales y **subsuperficiales cercanas** | Solo ferromagnéticos | Defectos paralelos al campo no se ven; desmagnetizar | ISO 9934-1 |
| Ultrasonido (UT) | Internos (fisuras, falta de fusión, inclusiones) y espesores | Casi todos los metales | Acoplante, geometría, grano grueso, operador calificado | ISO 16810 |
| Radiografía (RT) | Internos volumétricos (poros, inclusiones, rechupes) | Todos | Fisuras planas mal orientadas; radioprotección | ISO 17636-1 y -2 (soldaduras) |
| Corrientes inducidas (ET) | Superficiales y cercanas; espesor de recubrimientos; clasificar materiales | Conductores | Poca penetración; necesita patrones | ISO 15549 |

La calificación del personal es por ISO 9712. Pasos de PT y MT, y cómo elegir: `references/charpy-doblado-fatiga-end.md`.

## Informe de laboratorio e incertidumbre

Estructura: objetivo; norma y método; material y probetas (croquis y dimensiones con su incertidumbre); equipos (máquina, capacidad, calibración, extensómetro, durómetro, calibre o micrómetro y su resolución); procedimiento y condiciones (temperatura, velocidad, tiempos); resultados (tablas, curva, fotos de la rotura o de las huellas); cálculos; análisis contra la norma de producto o la bibliografía; conclusiones; anexos con los datos crudos.

Incertidumbre (GUM, JCGM 100:2008): tipo A = s/√n de lecturas repetidas; tipo B rectangular = a/√3 (a = semiancho, por ejemplo el error máximo del instrumento); resolución δ → δ/(2·√3). En productos y cocientes se suman en cuadratura las incertidumbres relativas, cada una multiplicada por su exponente; U = k·uc con k = 2 (≈ 95 %).
**Ejemplo** (Rm del ensayo anterior, datos de incertidumbre del ejemplo): fuerza con 1 % expandida (k = 2) según el certificado → 0,50 %; d0 con tres lecturas 10,00 / 10,02 / 9,98 mm, calibre de 0,02 mm y error máximo ±0,03 mm → u(d0) = √(0,0115² + 0,0058² + 0,0173²) = 0,0216 mm (0,216 %); u(Rm)/Rm = √(0,50² + (2·0,216)²) = 0,661 % → U = 2·0,661 %·500 = 6,6 MPa → **Rm = (500 ± 7) MPa (k = 2)**. Se redondea U a una o dos cifras y el resultado a la misma posición. Detalle y planilla: `references/informe-laboratorio.md`.

## Errores frecuentes y trampas

- Calcular σ con la sección final o con el diámetro nominal en vez del medido.
- Informar E sacado del desplazamiento del travesaño; trazar la paralela del 0,2 % desde el origen sin corregir el pie de la curva.
- Informar A sin decir la L0 (A con 5,65, A11,3 o A80mm no se comparan entre sí).
- Brinell con d fuera de 0,24·D a 0,6·D, pieza muy delgada o huellas cerca del borde; confundir kgf con N (factor 9,80665).
- Convertir durezas entre escalas con fórmulas o aplicar Rm ≈ 3,4·HB a algo que no es acero.
- Charpy: tardar más de 5 s desde el baño, entalla mal mecanizada, comparar KV2 con KV8.
- Doblado: usar el mandril de obra o un ángulo distinto del de la norma de producto.
- Fatiga: usar el Se' de la probeta pulida para una pieza real.
- Informar diez cifras: el resultado lleva las que permite la incertidumbre.

## Verificación

1. Correr `python scripts/ensayos.py demo` y el subcomando con los datos reales: los resultados del informe tienen que coincidir.
2. Unidades: 1 MPa = 1 N/mm²; 1 kgf = 9,80665 N; HBW y HV se informan sin unidad.
3. Órdenes de magnitud: E del acero ≈ 200 GPa; Rp0,2 menor que Rm; Agt menor que A; validez de cada huella; K menor que el 80 % de la energía del péndulo.
4. Comparar con la norma de producto o la bibliografía, con su fuente, y recorrer la consigna punto por punto.
