---
name: maniobra-y-transporte
description: "Cálculo y selección de equipos de maniobra y transporte de materiales con memoria de cálculo: cinta transportadora (capacidad por CEMA o DIN 22101, potencia en el tambor, tensiones T1 y T2 con Euler-Eytelwein, velocidad e inclinación máximas), tornillo sinfín (capacidad, llenado y potencia por CEMA 350), elevador de cangilones (capacidad y descarga centrífuga), aparejos y polipastos, cables de acero 6x19 y 6x36 (carga de rotura, coeficiente de seguridad, D/d, descarte), eslingas y cadenas de grado 8, puente grúa, autoelevador (centro de carga) y Decreto 351/79 para aparatos de izar. Usar cuando haya que calcular una cinta transportadora, un tornillo sinfín o un elevador de cangilones, elegir un cable de acero o una eslinga, resolver un aparejo o polipasto, revisar un puente grúa o un autoelevador, o en trabajos de maniobra y transporte de materiales."
---

# Equipos de maniobra y transporte

`scripts/transporte.py` (Python 3.9+, solo biblioteca estándar) hace cada cálculo e imprime fórmula, reemplazo y resultado con coma decimal, listo para la memoria de cálculo (presentación en **calculos-ingenieria**). Uso: `python scripts/transporte.py <comando> --help`, con los comandos `cinta`, `tornillo`, `cangilones`, `aparejo`, `cable`, `eslinga`, `autoelevador`, `grua` y `demo`. Unidades del script: mm (anchos y diámetros), m, m/s, rpm, kg/m³, cargas como masa en kg, kN y kW; g = 9,81 m/s².

Tablas completas, deducciones y fuentes con link: [references/transportadores.md](references/transportadores.md) para cintas, sinfines y cangilones, y [references/izaje.md](references/izaje.md) para aparejos, cables, eslingas, grúas, autoelevadores y el marco legal. Leerlas para citar un valor o calcular a mano. Lo marcado "(verificar)" no se pudo confirmar con la norma: revisarlo antes de entregar.

Relacionadas: correas, cadenas de transmisión, rodamientos y reductores en **elementos-de-maquinas**; elección y arranque del motor en **maquinas-electricas**; viga carrilera y estructuras en **resistencia-de-materiales**; bloqueo, permisos y protección personal en **higiene-y-seguridad**; marco legal general en **normas-tecnicas-ar**.

## Método

1. Material: densidad aparente ρ, tamaño, abrasividad y fluidez (tablas de las referencias o del fabricante).
2. Recorrido: caudal pedido (t/h), largo L, desnivel H e inclinación δ; en izaje, la masa, la altura y el uso (ciclos u horas).
3. Equipo: cinta para caudales grandes y distancias largas con poca pendiente; sinfín para tramos cortos y cerrados (harinas, polvos); cangilones para subir en vertical; aparejo, polipasto o grúa para izar.
4. Capacidad → tamaño y velocidad; controlar la velocidad máxima, la inclinación y las rpm.
5. Fuerzas y potencia → motor normalizado y transmisión.
6. Izaje: tensión en el cable o en la eslinga → coeficiente de seguridad legal → diámetro → D/d → inspección y descarte.

## Cinta transportadora

Sección de carga, con el ancho útil de la IS 11592:2000 (cl. 8.4.3), el mismo que usa DIN 22101:

- b = 0,9·B − 0,05 [m] con B ≤ 2 m; b = B − 0,25 con B > 2 m.
- Terna con rodillo central l3 y laterales a λ: l1 = (b − l3)/2; x = l3 + 2·l1·cos λ; trapecio A2 = (l3 + x)/2·l1·sen λ.
- Sobrecarga en arco de círculo con el ángulo de sobrecarga θ (CEMA): A1 = (x/2)²·(θ − sen θ·cos θ)/sen² θ. En triángulo con el ángulo dinámico β (DIN 22101): A1 = x²·tg β/4. θ = 20° para materiales de flujo normal (IS 11592, cl. 8.4.3.2); para la misma sección, β resulta cerca de 2/3 de θ.
- Iv = 3600·A·v·K [m³/h]; Im = Iv·ρ [t/h, con ρ en t/m³]; carga por metro m'L = A·K·ρ [kg/m]. Capacidad de diseño: el 90 % de la calculada, o el 75 % en bandas de hasta 600 mm (IS 11592, cl. 8.4.5).

Factor por inclinación K (IS 11592, tabla 9; completa en las referencias):

| δ | 0° a 2° | 6° | 10° | 14° | 18° | 20° | 22° | 25° | 30° |
|---|---|---|---|---|---|---|---|---|---|
| K | 1,00 | 0,98 | 0,95 | 0,91 | 0,85 | 0,81 | 0,76 | 0,68 | 0,56 |

Velocidad máxima en m/s (IS 11592, tabla 6), con el factor de velocidad = tamaño (0 a 4) + abrasividad (1 a 4; los granos de cereal son 1):

| Ancho [mm] | Factor 1 | 2 | 3 y 4 | 5 y 6 | 7 y 8 |
|---|---|---|---|---|---|
| hasta 500 | 2,50 | 2,30 | 2,00 | 1,65 | 1,45 |
| 750 a 800 | 3,50 | 3,20 | 2,75 | 2,35 | 2,05 |
| 1200 a 2000 | 4,50 | 4,12 | 3,55 | 3,00 | 2,62 |

Inclinación máxima por material: IS 8730:1997, tabla 3 (cemento portland, 20° a 23°); banda plana hasta 6° y en bajada no más de 12° (IS 11592); límite práctico general de 20° a 25° (MEKA). Para granos, el valor de esa tabla o del fabricante de la banda (verificar).

Fuerza en el tambor motriz (IS 11592, ec. 6; la forma de DIN 22101 e ISO 5048):

- FU = C·f·L·g·[m'R + (2·m'G + m'L)·cos δ] + m'L·g·H + FS [N]; potencia en el tambor PA = FU·v; en el motor PM = PA/η.
- m'R: partes que giran de los rodillos superiores e inferiores por metro; m'G: la banda (kg/m, de los catálogos). FS: raspadores, faldones, trippers.
- f = 0,020 normal; 0,016 en condiciones favorables; hasta 0,030 desfavorables; 0,012 en bajada con motor freno (IS 11592, cl. 8.5.1.1).
- C según el largo: 80 m → 1,92; 100 m → 1,78; 200 m → 1,45; 500 m → 1,20; 1000 m → 1,09 (DIN 22101 / ISO 5048, verificar en la norma vigente). Con L < 80 m es incierto (IS 11592, cl. 8.5.1.2): sumar las resistencias una por una.
- η del reductor de engranajes: hasta 98, 96 y 94 % con 1, 2 y 3 trenes (IS 11592, tabla 12).

Tensiones (Euler-Eytelwein): T1/T2 ≤ e^(μ·α) → T2 ≥ FU/(e^(μ·α) − 1) y T1 = FU + T2, con α el arco abrazado en radianes. μ de diseño 0,25 con tambor desnudo y 0,35 revestido (IS 11592, tabla 20: e^(μ·α) = 2,19 y 3,00 a 180°). Flecha entre rodillos: T ≥ a0·(m'G + m'L)·g/(8·h/a), con h/a cerca del 1 % (verificar). T1/B se compara con la tensión de trabajo de la banda del catálogo. Dec. 351/79, art. 130: resguardos hasta 1 m de los tambores.

## Transportador a tornillo sinfín

Q = 60·(π/4)·(D² − d²)·p·n·φ [m³/h] y Qm = Q·ρ, con D la hélice, d el tubo y p el paso en m: es la fórmula de CEMA 350 pasada al SI.

| Llenado φ (CEMA, tabla de KWS) | Materiales de ejemplo | Fm |
|---|---|---|
| 45 % | maíz, trigo, arroz, soja | 0,4 a 0,5 |
| 30 % A | harinas, azúcar, aserrín, carbón, caliza agrícola | 0,6 a 2,0 |
| 30 % B | cemento portland, sal fina, ceniza volante | 1,4 a 2,0 |
| 15 % | arena de banco húmeda | 2,8 |

rpm máximas para 12 in (KWS): 50 con 15 %, 90 con 30 % A, 50 con 30 % B y 145 con 45 %; de 6 a 16 in en las referencias.

Potencia por CEMA 350, en unidades inglesas (L en ft, n en rpm, C en ft³/h, W en lb/ft³):

- Vacío HPf = L·n·Fd·Fb/10⁶; material HPm = C·L·W·Ff·Fm·Fp/10⁶; total P = (HPf + HPm)·Fo/e.
- Fd: 6 in 18; 9 in 31; 12 in 55; 14 in 78; 16 in 106. Fb: rodamientos 1,0; bronce 1,7; plástico 2,0; hierro duro 4,4. e cerca de 0,88 (KWS).
- Con HPf + HPm < 5 hp, CEMA aplica el factor de sobrecarga Fo de su gráfico (no está en el script: se ingresa con `--fo`). Inclinado, la capacidad baja: consultar al fabricante. Dec. 351/79, art. 131: totalmente cubierto.

## Elevador de cangilones

Q = 3,6·(V/a)·v·φ [m³/h], con V el cangilón en litros, a la separación en m, v en m/s y φ cerca de 0,75 (verificar con el fabricante del cangilón).

Descarga en la cabeza: el polo de la resultante del peso y la fuerza centrífuga cae a hp = g/ω² ≈ 894/n² [m] sobre el eje del tambor, en cualquier posición del cangilón.

- hp < r del tambor (es decir, v² > g·r): descarga centrífuga, la de los elevadores de granos.
- hp > radio del borde exterior del cangilón: por gravedad; entre los dos, mixta.
- Para que el material salga arriba del tambor: ω²·rc = g → n = 29,9/√rc [rpm], o n = 42,3/√D con D = 2·rc en m.
- Potencia teórica ṁ·g·H = Qm·H/367 [kW con Qm en t/h]; el dragado del pie lo suma el fabricante (verificar).

## Aparejos, polipastos y cables de acero

- Aparejo de n ramales: η = (1 − ηp^n)/(n·(1 − ηp)); tiro F = m·g/(n·η), dividido otra vez por ηp por cada polea de desvío; el tiro recorre n·h. ηp cerca de 0,96 con bujes y 0,98 con rodamientos (verificar con el fabricante).
- Tensión en el ramal más cargado: S = (m + m_gancho)·g/(n·η); carga de rotura requerida Fmin ≥ cs·S.
- Cable: Fmin = K·d²·R/1000 [kN] con K = 0,330 (alma de fibra) o 0,356 (alma de acero) en 6x19 y 6x36, y R = 1770 o 1960 N/mm² (EN 12385-4, verificar en la norma vigente). Con 0,330 y 1770 reproduce a ±1,3 % la tabla de 6x19 IPS con alma de fibra de Engineering ToolBox. 6x19 resiste mejor la abrasión; 6x36 es más flexible, para poleas chicas.
- Coeficiente de seguridad: ≥ 6 en cables izadores (Dec. 351/79, arts. 118 y 123); ≥ 10 en cuerdas (art. 124); por grupo del mecanismo, Zp de 3,15 (M1) a 9,0 (M8) (ISO 4308-1, verificar en la norma vigente). Manda el mayor.
- D/d mínimo al eje del cable (ISO 4308-1, verificar): tambor 16 y polea 18 en M4; 20 y 22,4 en M6. Quedan al menos dos vueltas en el tambor con el gancho abajo (OSHA 1910.179).
- Descarte: más del 10 % de alambres rotos en dos tramos del cableado separados menos de 8·d (Dec. 351/79, art. 123); los criterios de la ISO 4309 (alambres rotos, diámetro, corrosión, deformación) en las referencias (verificar).

## Eslingas y cadenas

- T = m·g/(n·cos β), con β el ángulo de cada ramal con la vertical; factor de ángulo 1/cos β: 1,155 a 30°, 1,414 a 45° y 2 a 60°. No pasar de 60° con la vertical. Con 3 o 4 ramales se cuentan 3 (2 con carga rígida, verificar).
- Cadena de grado 8, carga de trabajo por ramal vertical (EN 818-4, coeficiente 4, verificar en el catálogo): 6 mm 1,12 t; 7 mm 1,5 t; 8 mm 2 t; 10 mm 3,15 t; 13 mm 5,3 t; 16 mm 8 t; 20 mm 12,5 t; 26 mm 21,2 t; 32 mm 31,5 t.
- Dec. 351/79, art. 122: cadenas con factor ≥ 5, ensayo al doble de la carga nominal y corte de los eslabones gastados más del 20 %. Con factor 5, la carga admisible es 4/5 de la de tabla: consultarlo con el servicio de higiene y seguridad.

## Puentes grúa y grúas

- Grupo del aparato A1 a A8 por la clase de utilización (U0 a U9, ciclos en su vida) y el espectro de carga (Q1 a Q4); del mecanismo, M1 a M8 por horas de marcha (T0 a T9) y espectro (L1 a L4) (ISO 4301-1 / FEM 1.001, verificar; matriz en las referencias). El grupo del mecanismo de izaje fija Zp y D/d del cable.
- Cargas: peso propio, carga por el coeficiente dinámico φ2 (EN 13001-2, verificar), aceleraciones y frenado, viento a la intemperie, choque contra los topes.
- Rueda más cargada con 2 ruedas por testero: Rmáx = [(φ·Q + Gc)·(L − e)/L + Gp/2]/2, con e la aproximación mínima del gancho al riel. Con Rmáx, la viga carrilera en **resistencia-de-materiales**.
- Dec. 351/79: carga máxima marcada (art. 114); ensayo antes de usar, control diario y revisión trimestral (art. 116); frenos para 1,5 veces la carga (art. 117); estructura con coeficiente 4 (art. 118); pasillos de 0,75 m en puentes grúa (art. 119).

## Autoelevadores

- Centro de carga: de la cara de las horquillas al centro de gravedad de la carga. La capacidad de la placa vale para un centro dado (24 in, unos 610 mm, en EE. UU.: OSHA 1910.178, apéndice A).
- Momento constante: Q = Qn·cn/c (OSHA: 3000 lb a 24 in → 2400 lb a 30 in). Con la distancia x del eje delantero a las horquillas, Q = Qn·(x + cn)/(x + c), menos conservador.
- Triángulo de estabilidad: las dos ruedas delanteras y el perno del eje trasero; el centro de gravedad del conjunto tiene que caer adentro. Al subir la carga, manda la tabla o curva de la placa.
- Res. SRT 960/15: placa con la carga máxima y la tabla de carga (IRAM 8412-1), capacitación de 10 h y 2 h por año, revisión trimestral; Dec. 351/79, art. 134.

## Ejemplo resuelto

Datos inventados: una planta de acopio lleva maíz (720 kg/m³) a una batería de silos. Las masas de rodillos y banda son del ejemplo; en un proyecto salen del catálogo.

```
python transporte.py cinta --B 800 --v 2.5 --rho 720 --delta 5 --fv 1 --L 100 --mr 12 --mg 9 --arco 200
  → A = 0,06451 m², K = 0,985: 571,9 m³/h = 411,8 t/h (de diseño 370,6); v ≤ 3,50 m/s, verifica
    FU = 6 549 N: 16,37 kW en el tambor, 17,42 kW en el motor → 18,5 kW; T2 = 2 737 N, T1 = 9 285 N (11,6 N/mm)
python transporte.py tornillo --D 300 --d 89 --rpm 80 --material maiz --L 12
  → 0,5222 m³/h por rpm: 41,77 m³/h = 30,11 t/h (máximo 145 rpm); 1,385 hp = 1,03 kW sin Fo (avisa: < 5 hp)
python transporte.py cangilones --V 1.6 --paso 0.25 --rho 720 --v 2.5 --D 1000 --proy 150 --H 20
  → 31,10 t/h; hp = 0,392 m < 0,5 m: descarga centrífuga; 1,70 kW de elevación teórica
python transporte.py cable --m 2000 --ramales 4 --grupo M4
  → η = 0,9704; S = 5 055 N; Fmin ≥ 30,33 kN → 6x36 alma de acero 1770 de 7 mm (30,9 kN); tambor ≥ 112 mm, poleas ≥ 126 mm
python transporte.py eslinga --m 2000 --ramales 2 --angulo 45
  → 13,87 kN por ramal → cadena de grado 8 de 7 mm; con el factor 5 del Dec. 351/79, de 8 mm
python transporte.py autoelevador --Qn 2500 --cn 500 --c 700 --x 450   → 1 786 kg (con x: 2 065 kg)
```

## Errores frecuentes

- Usar el ancho total B en lugar del útil b, o el ángulo de reposo en lugar del de sobrecarga.
- Mezclar el θ de CEMA (arco) con el β de DIN (triángulo): con el mismo número, el triángulo da bastante más sección.
- Olvidar K en una cinta inclinada o pasar la inclinación máxima del material.
- Calcular la potencia sin m'R ni m'G, o con el C de una cinta larga en una de 20 m.
- Sacar T2 solo con Euler: la flecha entre rodillos suele pedir más tensión.
- Sinfín: no restar el tubo, usar el llenado de los granos con un material abrasivo u olvidar Fo en los chicos.
- Cangilones: velocidad baja para descarga centrífuga, y el material vuelve a caer adentro del elevador.
- Izaje: tomar la masa (kg) como fuerza, olvidar el rendimiento del aparejo y las poleas de desvío, usar un coeficiente menor que el legal (6 en cables), medir el ángulo de la eslinga desde la horizontal con la fórmula de la vertical o contar 4 ramales portantes.
- Autoelevador: usar la capacidad de placa con otro centro de carga o con la carga en altura.

## Verificación

`python scripts/transporte.py demo` tiene que terminar en `DEMO OK` (código 0). Reproduce la sección del ejemplo de DIN 22101 de la tabla 3 del manual de Dunlop (580 m³/h a 1 m/s) y la de la tabla 4 del manual de rodillos de Sandvik (0,169 m²), citadas en el artículo de las referencias; cinco secciones de banda plana de la tabla 8 de la IS 11592 y los e^(μ·α) de su tabla 20; la capacidad a 1 rpm de KWS para sinfines de 6, 9 y 12 in y su ejemplo de 60 rpm; el ejemplo de autoelevador de OSHA 1910.178 (2400 lb) y la tabla de 6x19 IPS de Engineering ToolBox (±1,3 %). Además controla con cuentas a mano los ejemplos de arriba, el polo de los cangilones en 18 posiciones, el aparejo ramal por ramal y que la tabla de grado 8 sea coherente con 800 N/mm² y coeficiente 4. Para una entrega, una revisión independiente con **equipo-de-modelos** o **revision-tecnica**.
