# Izaje: aparejos, cables, eslingas, grúas, autoelevadores y marco legal

Leer cuando haya que calcular a mano un aparejo, elegir un cable o una eslinga, clasificar una grúa, corregir la capacidad de un autoelevador o citar el Decreto 351/79 en un informe. Los mismos valores están en `scripts/transporte.py`. Lo marcado "(verificar)" no se pudo confirmar con la norma: las normas ISO y EN de izaje son pagas y no se pudieron consultar.

## Aparejos y polipastos

Con n ramales que sostienen la carga, cada polea pierde un poco: si en el ramal que va al tiro la tensión es T, en los siguientes es T·ηp, T·ηp², … Sumando los n ramales: W = T·(1 − ηp^n)/(1 − ηp). De ahí:

- Rendimiento del aparejo: η = W/(n·T) = (1 − ηp^n)/(n·(1 − ηp)).
- Fuerza en el tiro: F = W/(n·η); cada polea fija de desvío entre el aparejo y el tiro la divide por ηp otra vez. Si el tiro sale de una polea fija del aparejo (aparejo de taller clásico), esa polea cuenta como desvío.
- El tiro recorre n veces lo que sube la carga.

| Ramales n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| η con ηp = 0,96 | 1,000 | 0,980 | 0,961 | 0,942 | 0,923 | 0,905 | 0,888 | 0,871 |
| η con ηp = 0,98 | 1,000 | 0,990 | 0,980 | 0,970 | 0,961 | 0,951 | 0,942 | 0,933 |

ηp ≈ 0,96 con bujes de bronce y 0,98 con rodamientos son valores habituales de los manuales de grúas (verificar con el fabricante).

## Cables de acero

### Construcciones

- **6x19**: seis cordones de 19 alambres (Seale, Filler o Warrington). Alambres más gruesos: resiste mejor la abrasión y el aplastamiento, es menos flexible.
- **6x36**: seis cordones de unos 36 alambres (por ejemplo 6x36 Warrington-Seale). Alambres más finos: más flexible y con mejor vida a la fatiga en poleas, pero se gasta antes por abrasión.
- **Alma de fibra**: la más flexible, pero se aplasta con facilidad. **Alma de acero** (independiente): la más durable en cualquier ambiente ([Wikipedia, Wire rope](https://en.wikipedia.org/wiki/Wire_rope)) y con más carga de rotura (K mayor, abajo).

### Carga de rotura mínima

Fmin = K·d²·R/1000 [kN], con d en mm, R el grado de los alambres (1770 o 1960 N/mm²) y K el factor de la clase: 0,330 para 6x19 y 6x36 con alma de fibra y 0,356 con alma de acero (EN 12385-4, verificar en la norma vigente). Con K = 0,330 y 1770 N/mm², la fórmula da los valores de la tabla de 6x19 IPS con alma de fibra de [Engineering ToolBox](https://www.engineeringtoolbox.com/wire-rope-strength-d_1518.html) (cable de norma estadounidense, de resistencia parecida) con diferencias de −1,2 % a +1,3 %:

| d | Tabla de ToolBox [kN] | Fórmula [kN] | Diferencia |
|---|---|---|---|
| 1/2 in (12,7 mm) | 95,2 | 94,2 | −1,0 % |
| 5/8 in (15,9 mm) | 149 | 147,2 | −1,2 % |
| 3/4 in (19,1 mm) | 212 | 212,0 | 0,0 % |
| 7/8 in (22,2 mm) | 286 | 288,5 | +0,9 % |
| 1 in (25,4 mm) | 372 | 376,8 | +1,3 % |

Valores de la fórmula, en kN (confirmar siempre con el catálogo del fabricante del cable que se compra):

| d [mm] | 8 | 10 | 12 | 13 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Alma de fibra, 1770 | 37,4 | 58,4 | 84,1 | 98,7 | 114,5 | 149,5 | 189,2 | 233,6 | 282,7 | 336,4 | 394,9 | 457,9 | 598,1 |
| Alma de acero, 1770 | 40,3 | 63,0 | 90,7 | 106,5 | 123,5 | 161,3 | 204,2 | 252,0 | 305,0 | 362,9 | 426,0 | 494,0 | 645,2 |
| Alma de acero, 1960 | 44,7 | 69,8 | 100,5 | 117,9 | 136,8 | 178,6 | 226,1 | 279,1 | 337,7 | 401,9 | 471,7 | 547,0 | 714,5 |

### Coeficiente de seguridad

Se adopta el mayor que corresponda:

| Criterio | Valor | Fuente |
|---|---|---|
| Cables izadores, en Argentina | ≥ 6 | Dec. 351/79, art. 118 (inc. 5) y art. 123 |
| Cuerdas (de fibra) para izar o transportar | ≥ 10 | Dec. 351/79, art. 124 |
| Cadenas | ≥ 5 | Dec. 351/79, art. 122 |
| Ganchos | 3 a mano; 4 con fuerza motriz; 5 si izan materiales peligrosos | Dec. 351/79, art. 118 |
| Partes estructurales de grúas | 4 | Dec. 351/79, art. 118 |
| Cable de puente grúa en EE. UU. | carga/ramales ≤ 20 % de la rotura (5) | [OSHA 1910.179(h)(2)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.179) |
| Por grupo del mecanismo, cables que corren | Zp: M1 3,15 · M2 3,35 · M3 3,55 · M4 4,0 · M5 4,5 · M6 5,6 · M7 7,1 · M8 9,0 | ISO 4308-1 / FEM 1.001 (verificar en la norma vigente) |

### Diámetro de tambores y poleas

D ≥ h·d, medido al eje del cable (ISO 4308-1 / FEM 1.001, verificar en la norma vigente):

| Grupo | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 |
|---|---|---|---|---|---|---|---|---|
| h1, tambor | 11,2 | 12,5 | 14 | 16 | 18 | 20 | 22,4 | 25 |
| h2, polea | 12,5 | 14 | 16 | 18 | 20 | 22,4 | 25 | 28 |

En el tambor quedan al menos dos vueltas de cable con el gancho en su posición más baja ([OSHA 1910.179(h)(2)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.179)). Las cadenas se enrollan solo en tambores, ejes o poleas con ranuras (Dec. 351/79, art. 122).

### Descarte

- Dec. 351/79, art. 123: revisión diaria de alambres rotos; se descarta el cable con más del 10 % de los alambres rotos, contados en dos tramos del cableado separados entre sí menos de 8 veces su diámetro. Lazos y ojales con guardacabos; sin nudos ni torceduras permanentes.
- ISO 4309 (inspección y descarte de cables de grúas): cantidad de alambres rotos visibles en 6·d y 30·d según la construcción, disminución del diámetro, corrosión, deformaciones (jaula de pájaro, ondulación, aplastamiento, cocas) y daño por calor (verificar los números en la norma vigente).
- Eslingas de cable, en EE. UU. ([OSHA 1910.184](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.184)): fuera de servicio con 10 alambres rotos al azar en un paso del cableado, o 5 en un cordón en un paso; con desgaste de un tercio del diámetro de los alambres exteriores; con aplastamiento, cocas, corrosión o daño por calor. Ganchos abiertos más del 15 % o torcidos más de 10°.

## Eslingas y cadenas

Tensión por ramal: T = m·g/(n·cos β), con β el ángulo de cada ramal con la vertical (si se mide desde la horizontal, α = 90° − β y T = m·g/(n·sen α)). OSHA 1910.184 toma como vertical un ramal a 5° o menos.

| β con la vertical | 0° | 15° | 30° | 45° | 60° |
|---|---|---|---|---|---|
| Factor de ángulo 1/cos β | 1,000 | 1,035 | 1,155 | 1,414 | 2,000 |
| Tensión por ramal con 2 ramales, en veces la carga | 0,500 | 0,518 | 0,577 | 0,707 | 1,000 |

Arriba de 60° con la vertical las tablas de eslingas no se usan. Con 3 o 4 ramales se cuenta que trabajan 3 (los largos nunca son iguales); con carga rígida, se recomienda contar 2 (verificar con la norma de la eslinga).

Factores de modo de las normas europeas (EN 13414-1 para cable, EN 818-4 para cadena; verificar en la norma vigente): carga de la eslinga = M × carga de un ramal vertical, con M = 1,4 para 2 ramales hasta 45° y 1,0 hasta 60°; M = 2,1 y 1,5 para 3 y 4 ramales. Son n·cos β redondeado, con n = 2 o 3.

Cadena de grado 8 (EN 818-4, carga de trabajo por ramal vertical con coeficiente 4, verificar en el catálogo del fabricante):

| d [mm] | 6 | 7 | 8 | 10 | 13 | 16 | 18 | 19 | 20 | 22 | 23 | 26 | 28 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Carga de trabajo [t] | 1,12 | 1,5 | 2,0 | 3,15 | 5,3 | 8,0 | 10,0 | 11,2 | 12,5 | 15,0 | 16,0 | 21,2 | 25,0 | 31,5 |

Cada valor queda entre el 90 % y el 100 % de la rotura que da el grado 8 (800 N/mm² sobre las dos secciones del eslabón) dividida por 4: el `demo` lo controla.

El Dec. 351/79, art. 122, pide para las cadenas factor de seguridad ≥ 5, ensayo de las nuevas o reacondicionadas al doble de la carga nominal, la carga máxima vertical marcada, y cortar los eslabones gastados más del 20 % o doblados o agrietados. Con factor 5 en lugar de 4, la carga admisible es 4/5 de la de la tabla; consultar el criterio con el servicio de higiene y seguridad.

## Puentes grúa y grúas

Clasificación (ISO 4301-1 / FEM 1.001, verificar en la norma vigente):

- Aparato: clase de utilización por ciclos de izaje en su vida (U0 hasta 16 000; U1 32 000; U2 63 000; U3 125 000; U4 250 000; U5 500 000; U6 1 000 000; U7 2 000 000; U8 4 000 000; U9 más) y espectro de carga por kp = Σ (ni/N)·(Pi/Pmáx)³ (Q1 hasta 0,125; Q2 0,25; Q3 0,5; Q4 1).
- Mecanismo: clase por horas de marcha (T0 hasta 200 h; T1 400; T2 800; T3 1600; T4 3200; T5 6300; T6 12 500; T7 25 000; T8 50 000; T9 más) y espectro km (L1 a L4 con los mismos límites).

| Espectro | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 / L1 | 1 | 1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| Q2 / L2 | 1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 8 |
| Q3 / L3 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 8 | 8 |
| Q4 / L4 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 8 | 8 | 8 |

La columna es la clase U o T; la celda, el grupo A o M. El grupo del mecanismo de izaje fija Zp y h del cable.

Cargas a considerar: peso propio; carga nominal por el coeficiente dinámico de izaje (EN 13001-2: φ2 = φ2,min + β2·vh, con φ2,min = 1,05 / 1,10 / 1,15 / 1,20 y β2 = 0,17 / 0,34 / 0,51 / 0,68 para las clases HC1 a HC4 y vh en m/s, verificar en la norma vigente); fuerzas horizontales de aceleración y frenado de carro y puente; viento en grúas a la intemperie; choque contra los topes.

Carga en las ruedas de un puente grúa con 2 ruedas por testero, carro a la aproximación mínima e del riel: Rmáx = [(φ·Q + Gc)·(L − e)/L + Gp/2]/2, con Q la carga, Gc el carro y Gp el puente (peso repartido). Con Rmáx se verifica la viga carrilera (flexión, flecha, aplastamiento del alma) en **resistencia-de-materiales**.

Prueba de carga: no más del 125 % de la nominal salvo otra indicación del fabricante ([OSHA 1910.179(k)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.179)).

## Autoelevadores

- Centro de carga: distancia horizontal desde la cara de las horquillas al centro de gravedad de la carga. La capacidad de la placa vale para un centro de carga dado; en EE. UU., 24 in (610 mm) en equipos de hasta 30 000 lb ([OSHA 1910.178, apéndice A](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.178AppA) y [eTool de OSHA](https://www.osha.gov/etools/powered-industrial-trucks/operating-forklift/load-handling)); los catálogos europeos usan 500 mm en los equipos chicos (verificar en la placa).
- Momento de la carga: el autoelevador no vuelca mientras el momento del equipo respecto de las ruedas delanteras sea igual o mayor que el de la carga. Con el momento de la placa constante: Q = Qn·cn/c. Ejemplo de OSHA: 3000 lb a 24 in son 72 000 lb·in; una carga de 60 in de largo (centro a 30 in) puede pesar como máximo 2400 lb.
- Contando la distancia x del eje delantero a la cara de las horquillas, Q = Qn·(x + cn)/(x + c): da más que la anterior, que queda del lado seguro.
- Triángulo de estabilidad: el equipo se apoya en tres puntos (las dos ruedas delanteras y el perno central del eje trasero, que pivota). Si la vertical del centro de gravedad combinado (equipo más carga) cae dentro del triángulo, no vuelca. Al levantar la carga sube el centro de gravedad y las fuerzas al subir, bajar, frenar o girar lo corren: la carga se lleva lo más baja posible y la capacidad con altura sale de la tabla o curva de la placa.
- Res. SRT 960/15 ([texto](https://www.argentina.gob.ar/normativa/nacional/norma-246619/texto)): placa identificatoria del equipo y del accesorio con la carga máxima admisible y la tabla o curvas de carga (IRAM 8412-1); cinturón, alarma de retroceso acústica y luminosa, espejos, luces, extintor; capacitación teórico-práctica de al menos 10 h con evaluación y revalidación anual de 2 h; control diario al inicio del turno; revisión general trimestral; prohibido llevar personas y usar el celular al conducir.

## Marco legal y normas en Argentina

| Norma | Qué fija | Texto |
|---|---|---|
| Dec. 351/79, Anexo I, cap. 15 "Máquinas y herramientas" (arts. 103 a 137) | Aparatos para izar (arts. 114 a 121), cadenas, cables, cuerdas y ganchos (arts. 122 a 126), transportadores (arts. 127 a 132), carretillas y autoelevadores (arts. 133 y 134), ascensores y montacargas (art. 137) | [InfoLEG](https://servicios.infoleg.gob.ar/infolegInternet/anexos/30000-34999/32030/texact.htm); copia en [FI-UNLP](https://www1.ing.unlp.edu.ar/sitio/administracion/concursos/archivos/Decreto-351-79.pdf) |
| Res. SRT 960/15 (B. O. 07/05/2015) | Trabajos con autoelevadores de hasta 3500 kg con conductor sentado | [argentina.gob.ar](https://www.argentina.gob.ar/normativa/nacional/norma-246619/texto) |
| IRAM 8412-1 | Placa identificatoria del autoelevador (la cita la Res. SRT 960/15) | Catálogo IRAM |
| IRAM 3920:2022 | Calificación del personal de equipos de izaje y elevación de cargas y personas | Catálogo IRAM |
| IRAM 3923-1:2009 | Grúas móviles: inspección, ensayos y mantenimiento | Catálogo IRAM |
| IRAM 3927:2010 | Grúas hidráulicas articuladas montadas sobre vehículo | Catálogo IRAM |

Las IRAM de la tabla salen del esquema de certificación de operadores de izaje de TÜV Rheinland Argentina ([PDF](https://origin.tuv.com/content-media-files/argentina/pdfs/2024/certificaci%C3%B3n-de-personal-en-operaciones-de-izaje-y-elevaci%C3%B3n-alcance-t%C3%A9cnico-och.rev.e.pdf)), que también cita ASME B30.5 (grúas móviles), ASME B30.22 (grúas articuladas) y ANSI/ITSDF B56.1 (autoelevadores).

Artículos del Dec. 351/79 sobre aparatos para izar:

| Art. | Qué pide |
|---|---|
| 114 | La carga máxima admisible marcada en el aparato, en forma destacada; prohibido superarla |
| 115 | Subir y bajar la carga despacio, sin arranques ni frenadas bruscas; prohibido viajar sobre cargas, ganchos o eslingas |
| 116 | Revisión y ensayo de todo aparato nuevo antes de usarlo; control diario por el operador; revisión general trimestral por personal especializado (cables, cadenas, fines de carrera, poleas, frenos, controles) |
| 117 | Frenos para una carga de 1,5 veces la máxima admisible; corte de la fuerza motriz al pasar la altura o el recorrido máximos |
| 118 | Coeficientes de seguridad de las grúas (ver la tabla de coeficientes); lastre o contrapeso; topes; cabinas con visibilidad; pasillos de 0,90 m en grúas manejadas desde el piso |
| 119 | Puentes grúa con accesos seguros a la cabina y pasillos de 0,75 m como mínimo |
| 120 y 121 | Carteles con la carga máxima admisible en las cabinas de las grúas automotores; disposición de las palancas de maniobra de las grúas portátiles |
| 126 | Ganchos de acero forjado, con pestillo u otro seguro para que la carga no se salga; partes en contacto con cables o cadenas, redondeadas |
| 134 | Autoelevadores con la carga máxima marcada, mandos seguros, conductores capacitados, luces, frenos, bocina, calzas en pendiente y extintor |
| 137 | Ascensores y montacargas con fines de carrera, entre otros requisitos |

Marco general de higiene y seguridad (Ley 19.587 y anexos del decreto) en **normas-tecnicas-ar** y **higiene-y-seguridad**.
