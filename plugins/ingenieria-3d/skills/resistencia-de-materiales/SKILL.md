---
name: resistencia-de-materiales
description: "Resistencia de materiales con memoria de cálculo y calculadora en Python: tracción y compresión (ley de Hooke, dilatación térmica impedida), corte en pernos y pasadores (simple y doble) y aplastamiento, torsión de ejes macizos y huecos (potencia, torque y ángulo de giro), vigas simplemente apoyadas y en voladizo (reacciones, diagramas de corte y de momento flector, tensiones de flexión y de corte, flecha por integración numérica y por tablas con superposición), pandeo de columnas (Euler, Johnson y CIRSOC 301), círculo de Mohr, von Mises y Tresca, y propiedades de secciones con Steiner y perfiles IPN, UPN y ángulos. Usar cuando haya que calcular una viga, hacer el diagrama de momento flector, saber cuánto flexa, verificar a pandeo una columna, decidir qué perfil uso, fijar la tensión admisible o el coeficiente de seguridad, o resolver un ejercicio de resistencia de materiales."
---

# Resistencia de materiales

`scripts/resistencia.py` (Python 3.9+, solo biblioteca estándar) resuelve cada caso e imprime fórmula, reemplazo y resultado con coma decimal, listo para la memoria de cálculo (cómo presentarla: **calculos-ingenieria**). Ejes a fatiga, tornillos, chavetas y soldadura: **elementos-de-maquinas**. Ensayo de tracción y dureza: **ensayos-materiales**. Normas y designación de aceros: **normas-tecnicas-ar**.

Referencias, para leer cuando hagan falta:
- [references/perfiles-y-materiales.md](references/perfiles-y-materiales.md): tablas IPN, UPN y ángulos, y materiales, cada uno con su fuente. Leerlo para elegir un perfil o citar un valor.
- [references/formulas.md](references/formulas.md): convenciones de signos, giros de tabla, corte en vigas, coeficientes de pandeo, Mohr y la bibliografía completa. Leerlo para una deducción o una cita.

Unidades del script: kN y kN·m en vigas, N·m en torque, m en largos de vigas, barras y columnas, mm en las secciones, cm⁴ y cm³ como en los catálogos, MPa (= N/mm²) en tensiones, E y G.

| Comando | Para qué |
|---|---|
| `axial` | σ, ε y alargamiento; dilatación libre o impedida (con holgura) |
| `corte` | pernos en corte simple o doble, aplastamiento, bulones de un acoplamiento |
| `torsion` | τ, ángulo de giro, diámetro mínimo por resistencia y por rigidez |
| `viga` | reacciones, V y M máximos y dónde, σ y τ, flecha por integración numérica, `--csv`, `--elegir IPN` |
| `pandeo` | Euler, Johnson y CIRSOC 301 (E.2), con K por vínculos |
| `mohr` | principales, τ máxima, von Mises, Tresca y coeficiente de seguridad |
| `seccion`, `perfiles` | A, I, W, i; compuesta con Steiner; tablas y el perfil más liviano que cumple |

## Método (siempre)

1. Croquis con vínculos, cargas con su origen (peso propio, sobrecarga) y cotas, en unidades coherentes.
2. Reacciones por equilibrio (ΣFx = 0, ΣFy = 0, ΣM = 0) y diagramas de esfuerzos: dan la sección crítica.
3. Tensiones en la sección crítica contra la admisible σadm = fy/n, o contra la resistencia de diseño del reglamento.
4. Deformaciones (alargamiento, giro, flecha) contra su límite.
5. Adoptar el perfil o el diámetro comercial siguiente y **volver a verificar** con el adoptado, con su peso propio.
6. Control independiente: superposición de casos de tabla, otro método u orden de magnitud.

## Tracción y compresión

- σ = N/A [MPa]; ε = σ/E; δ = N·L/(E·A).
- Dilatación libre: δT = α·ΔT·L. Impedida entre apoyos rígidos: σT = −E·α·ΔT (al calentar, comprime); con una holgura h que se cierra, σT = −E·(δT − h)/L.
- Acero: E = 200 000 MPa, α = 12·10⁻⁶ 1/°C (CIRSOC 301-2005, A.3.5). Una barra comprimida se verifica además a pandeo.

`python resistencia.py axial --L 0,3 --d 50 --dT -200 --alfa 11,7e-6 --impedida` → σ = 468,0 MPa de tracción y F = 918,9 kN: un bulón de 50 mm calentado a 250 °C, apretado sin tensión, que trabaja a 50 °C (Podut, 2018, cap. 3, problema 2: 468 MPa; 0,00234; 919 kN).

## Corte directo y aplastamiento

- τ = F/(m·A), con A = π·d²/4 y m = 1 en corte simple o 2 en corte doble (dos planos de corte).
- Aplastamiento: σap = F/(d·t), con t el espesor que apoya: en corte simple, la chapa más delgada; en corte doble, el menor entre la chapa del medio y la suma de las dos de afuera.
- Fluencia en corte: τy = 0,577·fy (von Mises). Acoplamiento de bridas: F = T/(R·n) por perno, con R el radio de la circunferencia de pernos.

`corte --T 208890,9 --dp 340 --pernos 6 --d 40` → 204,79 kN por perno y τ = 162,97 MPa.

## Torsión de ejes circulares

- τ = T·r/J. Macizo: J = π·d⁴/32 y τ = 16·T/(π·d³). Hueco: J = π·(D⁴ − d⁴)/32.
- Ángulo de giro: θ = T·L/(G·J) [rad]. Acero: G = 77 200 MPa (CIRSOC 301-2005, A.3.5).
- Potencia: T = P/ω, o sea T [N·m] = 9549·P [kW]/n [rpm].
- Diámetro mínimo por resistencia: d = (16·T/(π·τadm))^(1/3); por rigidez: d = (32·T/(π·G·θ'))^(1/4), con θ' el giro admisible en rad/mm.

`torsion --P 3500 --rpm 160 --d 180 --L 2 --G 85000` → T = 208 890,9 N·m, τ = 182,42 MPa, θ = 2,73°. Es el eje de un turbogenerador con seis bulones de 40 mm en 340 mm (Podut, 2018, cap. 9, problema 2: 182,4 y 162,97 MPa).

## Flexión de vigas

- dV/dx = −q y dM/dx = V: M es máximo donde V cambia de signo, no siempre al centro.
- Tensión normal: σ = M·c/I = M/W; con M en kN·m y W en cm³, σ [MPa] = 1000·M/W.
- Corte: τ = V·Q/(I·b). Rectángulo 1,5·V/A; círculo (4/3)·V/A; tubo delgado 2·V/A; alma de un doble T, τ ≈ V/(h·tw).
- Flechas de tabla (E·I constante; f hacia abajo; verificadas con sympy y en el demo):

| Caso | M máximo | Flecha máxima |
|---|---|---|
| Apoyada, q uniforme | q·L²/8 al centro | 5·q·L⁴/(384·E·I) al centro |
| Apoyada, P al centro | P·L/4 | P·L³/(48·E·I) |
| Apoyada, P a b del apoyo más cercano | P·a·b/L bajo la carga | P·b·(L² − b²)^1,5/(9·√3·L·E·I), en x = √((L² − b²)/3) desde el apoyo lejano |
| Voladizo, P en el extremo | P·L en el empotramiento | P·L³/(3·E·I) |
| Voladizo, q uniforme | q·L²/2 | q·L⁴/(8·E·I) |
| Voladizo, P a la distancia a del empotramiento | P·a | P·a²·(3·L − a)/(6·E·I) en el extremo |

Con varias cargas, **superposición**: se suman las flechas en el mismo punto (los máximos de cada caso caen en x distintos). Giros de tabla y deducciones: [references/formulas.md](references/formulas.md).

Flecha admisible, CIRSOC 301-2005, Tabla A-L.4.1 (total / solo sobrecarga útil): pisos en general L/250 y L/300; techos en general L/200 y L/250; barras de pisos o techos con revestimientos que se fisuran L/300 y L/350; pisos que soportan columnas L/400 y L/500. En ménsulas, L = 2 veces el voladizo. Para vigas carril y otros casos, la tabla completa o la consigna.

El script integra M/(E·I) dos veces con la regla de Simpson en una malla que incluye apoyos y puntos de carga (con cargas puntuales y uniformes es exacta) y aplica las condiciones de borde: y = 0 en los apoyos; y = 0 y θ = 0 en el empotramiento. `--csv` guarda x, V, M, giro y flecha para graficar los diagramas.

**Ejemplo resuelto** (el del demo): viga de un entrepiso de un galpón, simplemente apoyada, L = 5 m, q = 6 kN/m (con el peso propio) y P = 10 kN a 2 m del apoyo A; acero F-24, fy = 235 MPa, n = 1,5 → σadm = 156,7 MPa.
1. Reacciones: RA = q·L/2 + P·b/L = 15 + 10·3/5 = 21 kN; RB = 15 + 10·2/5 = 19 kN.
2. V(2⁻) = 21 − 6·2 = 9 kN y V(2⁺) = −1 kN: el corte cambia de signo bajo la carga → Mmáx = 21·2 − 6·2²/2 = 30 kN·m en x = 2 m.
3. W ≥ M/σadm = 30 000/156,7 = 191,5 cm³ → IPN 200 (W = 214 cm³, I = 2140 cm⁴, ArcelorMittal): σ = 140,2 MPa y n = 1,68; en el alma, τ ≈ 21 000/(200·7,5) = 14,0 MPa.
4. E·I = 200 000·2140·10⁻⁵ = 4280 kN·m². Flecha al centro por superposición: 5·6·5⁴/(384·4280) + 10·2·(3·5² − 4·2²)/(48·4280) = 11,41 + 5,74 = 17,15 mm. Máxima por integración: 17,16 mm en x = 2,448 m ≤ L/250 = 20 mm: verifica. Con solo la sobrecarga útil, el límite es L/300.

`python resistencia.py viga --tipo apoyada --L 5 --q 6 --P 10@2 --perfil IPN200 --fy 235 --n 1,5 --limite 250`. Para que elija el perfil: `--elegir IPN` en lugar de `--perfil` (más `--peso-propio` si q no incluye el peso del perfil).

## Pandeo de columnas

| Vínculos | K teórico |
|---|---|
| Articulada en los dos extremos | 1 |
| Empotrada y libre (ménsula) | 2 |
| Empotrada y articulada | 0,7 (0,699) |
| Empotrada en los dos extremos | 0,5 |

Los empotramientos reales giran algo: para diseño se usan valores mayores (ver [references/formulas.md](references/formulas.md)). En pórticos arriostrados el CIRSOC 301-2005 (C.2.1) toma k = 1, salvo que un análisis justifique uno menor.

- Lk = K·L; i = √(I/A), el mínimo salvo que el eje débil esté arriostrado; λ = Lk/i. Máximo λ = 200 en barras comprimidas (CIRSOC 301-2005, B.7).
- Euler: Pcr = π²·E·I/Lk² y σcr = π²·E/λ². Vale en la zona elástica: λ ≥ λ1 = √(2·π²·E/fy), donde σcr = fy/2.
- Intermedias (λ < λ1), parábola de Johnson: σcr = fy − (fy·λ/(2·π))²/E, tangente a Euler en λ1. Tetmajer (recta de tabla): en las referencias.
- Estructuras de acero de edificios, CIRSOC 301-2005 (E.2): λc = (λ/π)·√(fy/E); Fcr = 0,658^(λc²)·fy si λc ≤ 1,5, o (0,877/λc²)·fy si es mayor; φc·Pn = 0,85·Fcr·Ag, que se compara con la carga mayorada Pu.
- Un ángulo solo pandea alrededor del eje v: se usa iv.

**Ejemplo** (demo): puntal de tubo de 80 × 4 mm, L = 2,5 m, articulado en los dos extremos, fy = 235 MPa. A = 9,55 cm², i = 2,691 cm, λ = 92,9 < λ1 = 129,6 → Johnson: σcr = 174,6 MPa y Pcr = 166,8 kN (Euler daría 218,4 kN: sobreestima 31 %); con P = 50 kN de servicio, n = 3,34. CIRSOC: λc = 1,014, Fcr = 152,8 MPa, φc·Pn = 124,1 kN contra Pu.

`pandeo --L 2,5 --vinculos art-art --tubo 80x4 --P 50 --Pu 70`

## Tensiones combinadas

- Círculo de Mohr (estado plano): C = (σx + σy)/2; R = √(((σx − σy)/2)² + τxy²); σ1,2 = C ± R; τmáx en el plano = R; tan 2θp = 2·τxy/(σx − σy).
- Con σ3 = 0, el corte máximo absoluto es el mayor de |σ1 − σ2|/2, |σ1|/2 y |σ2|/2.
- von Mises: σ' = √(σ1² − σ1·σ2 + σ2²) = √(σx² − σx·σy + σy² + 3·τxy²). Tresca: σ1 − σ3, más conservador. Coeficiente de seguridad: n = fy/σ'.
- Eje con flexión y torsión estáticas: σ = 32·M/(π·d³) y τ = 16·T/(π·d³) → σ' = √(σ² + 3·τ²). A fatiga: **elementos-de-maquinas**.

`mohr --sx 80 --txy -50 --fy 250` → σ1 = 104,03 MPa, σ2 = −24,03 MPa, θ1 = −25,67° (horario), τmáx = 64,03 MPa, σ' = 117,90 MPa, n = 2,12.

## Propiedades de secciones

| Sección | A | I | W | i |
|---|---|---|---|---|
| Rectángulo b × h | b·h | b·h³/12 | b·h²/6 | h/√12 |
| Círculo d | π·d²/4 | π·d⁴/64 | π·d³/32 | d/4 |
| Tubo D, d | π·(D² − d²)/4 | π·(D⁴ − d⁴)/64 | 2·I/D | √(D² + d²)/4 |
| Doble T de chapas b, h, tw, tf | 2·b·tf + (h − 2·tf)·tw | (b·h³ − (b − tw)·(h − 2·tf)³)/12 | 2·I/h | √(I/A) |

- Torsión: J = 2·I en círculo y tubo.
- Steiner: I = Ic + A·d². En una sección compuesta, yc = Σ(A·y)/ΣA e I = Σ(Ic + A·d²) respecto de ese baricentro: `seccion compuesta --parte 250x20@330 --parte 20x300@170 --parte 250x20@10` → I = 30 133 cm⁴.
- Un doble T de chapas sin radios da algo más que el laminado (IPN 200: 2162 contra 2140 cm⁴): para perfiles, el catálogo. `perfiles IPN --W 191,5` da el más liviano que cumple.

## Materiales y tensión admisible

| Material | fy [MPa] | fu [MPa] | E [MPa] | Fuente |
|---|---|---|---|---|
| Acero F-24 | 235 | 370 | 200 000 | ejemplos de aplicación del CIRSOC 303 y 301 (fu: verificar en IRAM-IAS U 500-503) |
| Acero F-36 | 355 (verificar) | (verificar) | 200 000 | no confirmado en el CIRSOC |
| SAE 1010, 1020, 1045 | según estado | | ≈ 207 000 | Shigley, tabla A-20 (verificar): tabla en las referencias |
| Aluminio 6061-T6 | ≈ 240 a 276 (verificar) | ≈ 260 a 310 (verificar) | ≈ 70 000 | E: Podut (2018), cap. 8 |

- σadm = fy/n; el coeficiente n lo fijan la consigna, el reglamento o la bibliografía de diseño, según el tipo de carga y las consecuencias de la falla.
- El CIRSOC 301 no trabaja con tensiones admisibles: compara cargas mayoradas con resistencias de diseño φ·Rn (por ejemplo, φc = 0,85 en compresión). No mezclar los dos métodos en una misma verificación.

## Errores frecuentes

- Mezclar kN con N, m con mm o cm⁴ con mm⁴ (1 cm⁴ = 10⁴ mm⁴; 1 cm³ = 10³ mm³).
- Tomar I o W del eje equivocado: el IPN flexa por el eje fuerte y pandea por el débil.
- Buscar el momento máximo siempre en el centro, o sumar las flechas máximas de casos que caen en puntos distintos.
- Usar Euler en una columna intermedia (λ < λ1): sobreestima la carga.
- Tomar K = 0,5 o 0,7 con empotramientos que en la obra giran.
- Verificar sin el peso propio, o adoptar el perfil sin verificar la flecha (en entrepisos suele mandar la flecha).
- Confundir corte simple con doble, o calcular el aplastamiento con el espesor equivocado.
- Usar E = 210 000 MPa de tablas europeas y 200 000 del CIRSOC sin decir cuál.

## Verificación

`python resistencia.py demo` tiene que terminar en `DEMO OK`. Reproduce los ejemplos de esta skill, los dos problemas del libro abierto de Podut (2018), con sus respuestas, y el ejemplo 3-8 de Gere y Goodno (eje ABC de 50 mm: 796 N·m, 32,4 MPa y 1,26°; edición: verificar). Compara la flecha numérica con seis fórmulas de tabla (diferencia menor que 10⁻⁹), y controla la superposición, el equilibrio, el K teórico, la continuidad de Johnson y del CIRSOC, los invariantes de Mohr, Steiner, los ángulos contra STAD y la coherencia de las tablas de perfiles. Para una entrega, una revisión independiente con **revision-tecnica** o **equipo-de-modelos**.
