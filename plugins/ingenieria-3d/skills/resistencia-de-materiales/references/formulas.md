# Fórmulas, convenciones y fuentes

Leer cuando haga falta un giro de tabla, la deducción de una fórmula, la convención de signos del script, los coeficientes de pandeo que no están en el SKILL.md o la cita completa de una fuente.

## Convenciones de signos del script

- Vigas: x en m desde el extremo izquierdo (en el voladizo, el empotramiento está en x = 0). Cargas P y q positivas hacia abajo; pares aplicados positivos antihorarios.
- Corte V: suma de las fuerzas a la izquierda de la sección, positivas hacia arriba. Momento flector M positivo si tracciona la fibra de abajo (viga "sonriente"); en un voladizo cargado hacia abajo, M es negativo.
- Flecha: el script integra E·I·y'' = M con y hacia arriba e informa la flecha f = −y (positiva hacia abajo).
- Mohr: σ positiva de tracción; τxy positiva si en la cara +x apunta hacia +y; θ antihorario desde x. Con esa convención, un corte "horario" en la cara x se carga con signo negativo.

## Relaciones entre carga, corte y momento

dV/dx = −q y dM/dx = V. Consecuencias para dibujar los diagramas sin calcular cada punto:
- Sin carga entre dos puntos, V es constante y M varía en forma lineal; con q uniforme, V es lineal y M es una parábola.
- Una carga puntual produce un salto en V (del valor de la carga) y un quiebre en M; un par aplicado produce un salto en M.
- M es máximo o mínimo donde V pasa por cero (o cambia de signo bajo una carga puntual). La variación de M entre dos secciones es el área del diagrama de corte entre ellas.
- En un extremo libre o un apoyo articulado de extremo, M = 0.

## Giros de tabla (verificados con sympy)

| Caso | Giro |
|---|---|
| Apoyada, q uniforme | θ en los apoyos = q·L³/(24·E·I) |
| Apoyada, P al centro | θ en los apoyos = P·L²/(16·E·I) |
| Voladizo, P en el extremo | θ en el extremo = P·L²/(2·E·I) |
| Voladizo, q uniforme | θ en el extremo = q·L³/(6·E·I) |

Con P a la distancia b del apoyo más cercano (b ≤ L/2), la flecha **al centro** es P·b·(3·L² − 4·b²)/(48·E·I): sirve para sumar por superposición en el mismo punto. La flecha máxima de esa carga sola está en x = √((L² − b²)/3) medido desde el apoyo más lejano.

**Superposición**: vale en régimen elástico y con deformaciones chicas. Se suman flechas (o giros) **en el mismo punto**; las máximas de cada caso caen en x distintos, así que sumar los máximos da un valor del lado de la seguridad pero no el real. El script resuelve todas las cargas juntas.

## Cómo integra el script

Arma una malla con los extremos, los apoyos, los puntos de carga y los bordes de las cargas uniformes, más 400 tramos parejos. En cada tramo M es a lo sumo una parábola, así que integrar M/(E·I) con la regla de Simpson da el giro exacto, y el giro (un polinomio cúbico) integrado otra vez con Simpson da la flecha exacta en los nodos. Después aplica las condiciones de borde: en una viga apoyada suma una recta para que y = 0 en los dos apoyos; en el voladizo arranca con y = 0 y θ = 0 en el empotramiento. La flecha máxima se busca donde el giro cambia de signo (por bisección dentro del tramo) y en los extremos libres. El demo la compara con seis fórmulas de tabla: la diferencia queda por debajo de 10⁻⁹.

## Tensiones de corte en flexión

τ = V·Q/(I·b), con Q el momento estático del área que está por encima de la fibra considerada respecto del eje neutro y b el ancho en esa fibra. En la fibra neutra (verificado con sympy en rectángulo y círculo):

| Sección | τ máxima |
|---|---|
| Rectángulo | 1,5·V/A |
| Círculo macizo | (4/3)·V/A |
| Tubo de radios R y r | (4/3)·(V/A)·(R² + R·r + r²)/(R² + r²); tiende a 2·V/A en tubo delgado |
| Doble T | V·Q/(I·tw), con Q = b·tf·(h − tf)/2 + tw·(h/2 − tf)²/2; en la práctica, τ ≈ V/(h·tw) |

En vigas cortas con cargas grandes cerca de los apoyos, el corte puede mandar; en vigas largas casi siempre manda la flexión o la flecha.

## Pandeo

- Factor K teórico, verificado por elementos finitos de viga (autovalor de la carga crítica): 1 (articulada-articulada), 2 (empotrada-libre), 0,699 (empotrada-articulada, raíz de tan x = x: x = 4,4934), 0,5 (empotrada-empotrada), 1 (empotrada con el otro extremo sin giro pero con desplazamiento lateral) y 2 (articulada con el otro extremo sin giro y con desplazamiento).
- Los empotramientos reales giran algo, y por eso los comentarios de las normas de acero recomiendan valores de diseño mayores: 0,65 en lugar de 0,5, 0,80 en lugar de 0,7, 1,2 en lugar de 1 (empotrado con desplazamiento sin giro) y 2,1 en lugar de 2 (valores del comentario de la especificación AISC: verificar en la edición vigente). En pórticos arriostrados, el CIRSOC 301-2005 (C.2.1) toma k = 1 salvo que un análisis estructural justifique un valor menor.
- Johnson: σcr = fy − (fy·λ/(2·π))²/E. En λ1 = √(2·π²·E/fy) vale fy/2 y es tangente a Euler (misma pendiente): el demo lo verifica. Con fy = 235 MPa y E = 200 000 MPa, λ1 = 129,6.
- CIRSOC 301-2005, E.2 (pandeo flexional): φc = 0,85; Pn = Fcr·Ag; λc = (1/π)·(k·L/r)·√(Fy/E); Fcr = 0,658^(λc²)·Fy si λc ≤ 1,5 y Fcr = (0,877/λc²)·Fy si λc > 1,5. Las dos ramas empalman en λc = 1,5 (0,38995 y 0,38978: 0,04 % de diferencia); la rama elástica es 0,877 veces Euler (tiene en cuenta la falta de rectitud). Con Fy = 235 MPa, λc = 1,5 corresponde a k·L/r = 137,5. Esbeltez máxima (B.7): 200 en barras comprimidas y 300 en traccionadas (150 y 250 con acciones dinámicas que no sean viento).
- Tetmajer (recta σ = a − b·λ para λ < λ0, y Euler arriba de λ0): los coeficientes son de tabla y dependen del material; la bibliografía alemana da para el acero S235 (St 37) a = 310 MPa, b = 1,14 MPa y λ0 = 105 (verificar en la bibliografía que se use). El script los recibe con `--tetmajer 310,1.14,105` y no deja pasar de fy.
- Un ángulo solo pandea alrededor del eje v (radio de giro mínimo iv). Si se carga por un ala con uniones excéntricas, la verificación es la del reglamento, no la de la columna ideal.

## Tensiones combinadas

- Transformación: σθ = (σx + σy)/2 + (σx − σy)/2·cos 2θ + τxy·sen 2θ; τθ = −(σx − σy)/2·sen 2θ + τxy·cos 2θ.
- Principales: tan 2θp = 2·τxy/(σx − σy); el script usa atan2 para dar el ángulo que lleva a σ1. Las direcciones de corte máximo están a 45°.
- Invariantes que sirven de control: σ1 + σ2 = σx + σy y σ1·σ2 = σx·σy − τxy².
- Con σ3 = 0 (estado plano), si σ1 y σ2 tienen el mismo signo el corte máximo absoluto es el mayor de |σ1|/2 y |σ2|/2, no (σ1 − σ2)/2.
- von Mises (energía de distorsión) predice bien la fluencia de los metales dúctiles; Tresca (corte máximo) da un poco menos de capacidad y es más conservador. Para materiales frágiles (fundición gris) se usan otros criterios (Mohr-Coulomb, Rankine).

## Fuentes

- INTI-CIRSOC (2005). *Reglamento Argentino de Estructuras de Acero para Edificios* (CIRSOC 301), edición julio 2005: A.3.1, A.3.5, B.7, C.2.1, E.2 y Tabla A-L.4.1. https://www.inti.gob.ar/assets/uploads/files/cirsoc/vigencia-2013/area300/reglamento_301.pdf
- INTI-CIRSOC. *Ejemplos de aplicación del Reglamento CIRSOC 301* (2005 y 2018): https://www.inti.gob.ar/assets/uploads/files/cirsoc/EJEMPLOS%202/EJEMPLOS%202.2/1_%20ejemplos_301.pdf y https://www.inti.gob.ar/assets/uploads/files/cirsoc/08-reglamentos-3ra-generacion/ejemplos-aplicacion/09_01-Ejemplos-CIRSOC301-2018-Completo.pdf
- INTI-CIRSOC (2009). *Ejemplos de aplicación del Reglamento CIRSOC 303*: https://www.inti.gob.ar/assets/uploads/files/cirsoc/EJEMPLOS%202/EJEMPLOS%202.2/ejemplos303-09completo.pdf
- ArcelorMittal, tabla IPN: https://sections.arcelormittal.com/repository2/Sections/Sections_MB_ArcelorMittal_FR_EN_DE_IPN.pdf
- STAD, datos técnicos de secciones (UPN y ángulos): https://www.stad.fr/downloads/pdf/stad-technical-data-of-sections.pdf
- Podut, A. (2018). *Strength of Materials Supplement for Power Engineering* (revisión 2). BCcampus, licencia CC BY 4.0: https://pressbooks.bccampus.ca/powr4406/ (cap. 3, problema 2, y cap. 9, problema 2, con las respuestas del final del libro). Complementa el libro abierto de B. Dupen, *Applied Strength of Materials for Engineering Technology*.
- Gere, J. M. y Goodno, B. J. *Mecánica de materiales*, ejemplo 3-8 (eje ABC de 50 mm con un motor de 50 kW a 10 Hz y engranajes de 35 y 15 kW): los datos y los resultados se confirmaron en los apuntes del curso de NTHU OpenCourseWare (https://ocw.nthu.edu.tw/ocw/upload/8/252/Chapter_3-98.pdf), que no nombran la edición: verificar la edición y la numeración del ejemplo en el libro que se use.
- Shigley (Budynas y Nisbett), *Diseño en ingeniería mecánica*: parábola de Johnson (cap. 4) y tabla A-20 de aceros SAE (valores de la tabla: verificar).
