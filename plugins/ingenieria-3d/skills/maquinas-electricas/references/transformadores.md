# Transformadores: detalle y ejemplos

Leer cuando el TP o el examen pide el circuito equivalente completo, la planilla de un ensayo, el grupo de conexión, el paralelo de dos transformadores, un autotransformador o transformadores de medida. Los números del ejemplo base (315 kVA, 13,2/0,4 kV, Dyn11) salen de `python scripts/maquinas.py demo`.

## 1. Trabajo por fase en trifásicos

- Se reemplaza cada lado por una **estrella equivalente**: Uf = U/√3, If = I de línea, Pf = P/3. Así las fórmulas del monofásico sirven igual, sin importar si el bobinado real es Y o Δ.
- Potencia y corriente nominal: Sn = √3·U·In → In = Sn/(√3·U).
- Relación de tensiones de línea a = U1/U2 (la que se usa para referir impedancias de la estrella equivalente: Z' = a²·Z).
- Relación de espiras: N1/N2 = U1,bobina/U2,bobina, con U,bobina = U si el lado es Δ y U/√3 si es Y. En el ejemplo Dy: 13200/(400/√3) = 57,16, mientras que a = 33.
- Por unidad (pu): Zbase = U²/Sn de cada lado; ucc % es la impedancia de cortocircuito en pu × 100, igual vista de los dos lados.

## 2. Circuito equivalente

- **Exacto**: R1 + jX1 → rama paralelo RFe ∥ jXμ → a²·R2 + j·a²·X2 → carga referida a²·ZL.
- **Aproximado** (el de los TPs): la rama paralelo se pasa a los bornes de entrada y queda en serie Rcc = R1 + a²·R2, Xcc = X1 + a²·X2. El error es chico porque I0 es mucho menor que In.
- Si piden separar R1 y R2: se mide R1 y R2 con corriente continua (puente o voltímetro-amperímetro) y se reparte Xcc en partes iguales (X1 = a²·X2 = Xcc/2), que es la simplificación habitual.

## 3. Ensayos de vacío y cortocircuito

**Vacío**: se alimenta la BT (tensiones más cómodas) a su tensión nominal, con la AT abierta. Instrumentos: voltímetro, amperímetro, vatímetro (en trifásico, dos vatímetros en conexión Aron o un analizador) y un voltímetro en la AT para la relación.
- Se mide: U0, I0, P0 y U20. Resultados: a = U1/U20; P0 ≈ PFe; cosφ0 = P0/(√3·U0·I0); IFe = I0·cosφ0; Iμ = I0·senφ0; RFe = (U0/√3)/IFe; Xμ = (U0/√3)/Iμ, todo por fase del lado BT. Para referirlos a AT: × a².
- Peligro: la AT abierta queda con su tensión nominal. Se trabaja con el tablero cerrado y se descarga antes de tocar.
- Ejemplo: U0 = 400 V, I0 = 6,8 A (1,50 % de In), P0 = 720 W → cosφ0 = 0,1528; IFe = 1,039 A; Iμ = 6,720 A; RFe = 222,2 Ω y Xμ = 34,37 Ω (BT); 242,0 kΩ y 37,42 kΩ (AT).

**Cortocircuito**: la BT se une con un puente de sección suficiente para la In de BT, y se sube despacio la tensión de la AT desde cero (con variac o regulador) hasta que circula In. **Nunca** aplicar la tensión nominal con el secundario en cortocircuito.
- Se mide: Ucc, Icc, Pcc. Si Icc no es In: Pcc,n = Pcc·(In/Icc)² y Ucc,n = Ucc·In/Icc.
- Resultados por fase en el lado del ensayo: Zcc = (Ucc,n/√3)/In; Rcc = Pcc,n/(3·In²); Xcc = √(Zcc² − Rcc²); ucc, uR, uX en %.
- Ejemplo: Ucc = 528 V, Pcc = 3900 W a In = 13,78 A → Zcc = 22,126 Ω; Rcc = 6,848 Ω; Xcc = 21,039 Ω; ucc = 4,00 %; uR = 1,238 %; uX = 3,804 %.

Planilla mínima de cada ensayo: instrumento, alcance usado, clase, lectura, constante y valor; temperatura ambiente; tensión y corriente nominales del transformador.

## 4. Caída de tensión (regulación)

Con el primario a tensión nominal, la tensión secundaria en carga es U2 = U20·(1 − ε/100), con:

ε % ≈ C·(uR·cosφ + uX·senφ) + C²·(uX·cosφ − uR·senφ)²/200

- C = I2/I2n (índice de carga); senφ positivo para carga inductiva, negativo para capacitiva.
- El primer término es el del triángulo de Kapp; el segundo corrige el ángulo y casi siempre es chico.
- Exacto (fasorial, en pu): V1 = V2 + I·(uR + j·uX)/100 con |V1| = 1; el script hace las dos cuentas.

Ejemplo (C = 1):

| Carga | ε % | U2 [V] |
|---|---|---|
| cosφ = 1 | 1,310 | 394,8 |
| cosφ = 0,9 inductivo | 2,814 | 388,7 |
| cosφ = 0,8 inductivo | 3,299 | 386,8 |
| cosφ = 0,6 inductivo | 3,794 | 384,8 |
| cosφ = 0,8 capacitivo | −1,220 | 404,9 (sube) |

La caída es máxima cuando el ángulo de la carga es el de la impedancia de cortocircuito (cosφ = uR/ucc) y entonces vale ≈ C·ucc.

## 5. Rendimiento

η = C·Sn·cosφ / (C·Sn·cosφ + P0 + C²·Pcc,n). Las pérdidas en el hierro son fijas (dependen de la tensión) y las del cobre van con C². El máximo está en Copt = √(P0/Pcc,n).

Ejemplo (P0 = 720 W, Pcc = 3900 W, Copt = 0,430):

| C | η con cosφ = 1 | η con cosφ = 0,8 |
|---|---|---|
| 0,25 | 98,79 % | 98,49 % |
| 0,50 | 98,94 % | 98,67 % |
| 0,75 | 98,78 % | 98,48 % |
| 1,00 | 98,55 % | 98,20 % |
| 1,25 | 98,30 % | 97,88 % |

Como un transformador de distribución trabaja buena parte del día con carga parcial, conviene que su máximo esté por debajo de plena carga.

## 6. Grupo de conexión (índice horario)

- Letra mayúscula = AT (Y, D o Z), minúscula = BT (y, d o z), n = neutro accesible, número = índice horario. Cada unidad del índice = 30° de atraso de la BT respecto de la AT (método del reloj: la tensión de AT en las 12 y la de BT en la hora que indica el índice).
- Cómo sacarlo en un TP: dibujar el triángulo de tensiones de AT; dibujar los fasores de BT paralelos a los de las bobinas de AT montadas en la misma columna; medir el ángulo entre la tensión fase-neutro de AT y la de BT de la misma letra; dividir por 30°.
- Comunes: Dyn11 y Dyn5 (distribución: el neutro de BT permite cargas monofásicas y el triángulo de AT deja circular las corrientes de tercer armónico), Yyn0, Yzn11 (potencias chicas con cargas desequilibradas), Dd0.
- Dos transformadores solo se conectan en paralelo con el mismo índice: un Dyn11 con un Dyn5 tienen 180° entre sus secundarios.

## 7. Paralelo

Condiciones (reglas usuales, de una guía basada en IEC): misma relación de tensiones (diferencias menores de 0,4 %), mismo índice horario y misma secuencia, ucc iguales o que difieran menos de 10 %, y potencias que no difieran más de 2:1 para paralelo permanente. Los cables hasta el punto de unión, de longitud y sección parecidas.

Reparto de carga (relaciones iguales): Si = Scarga·(Sni/ucci) / Σ(Snj/uccj). Lo que más carga toma es el de **menor** ucc.

Ejemplo: 630 kVA con ucc = 4,0 % y 400 kVA con ucc = 4,4 % (diferencia de 10 %, en el límite), alimentando 1000 kVA → el de 630 kVA toma 634,0 kVA (100,6 %, apenas sobrecargado) y el de 400 kVA toma 366,0 kVA (91,5 %). La carga máxima sin sobrecargar ninguno es 993,6 kVA, no 1030 kVA.

## 8. Autotransformador

- Un solo bobinado con una toma: por la parte común circula la diferencia de corrientes I2 − I1.
- Potencia de paso S = U1·I1 (o √3·U·I); potencia que transforma el bobinado (propia) = S·(1 − U2/U1) para reducir tensión. Ejemplo trifásico de 50 kVA, 400/320 V: propia 10 kVA; I1 = 72,2 A; I2 = 90,2 A; parte común 18,0 A.
- Ventajas: menos cobre y hierro, menos pérdidas y caída cuando U2/U1 está cerca de 1. Desventajas: no aísla galvánicamente (una falla del bobinado lleva la AT a la BT) y su ucc es baja, por eso la corriente de cortocircuito es mayor. Se usa en arranque de motores, en variacs y para enlazar redes de tensiones parecidas.

## 9. Transformadores de medida (IEC 61869-2 y 61869-3)

- **TI (de intensidad)**: primario en serie con la línea, secundario de 5 A o 1 A (por ejemplo 200/5 A, relación 40: con 150 A en el primario circulan 3,75 A por el instrumento). Bornes P1-P2 del primario y S1-S2 del secundario: respetar la polaridad para vatímetros y medidores.
- **Nunca abrir el secundario de un TI con corriente en el primario**: toda la corriente primaria pasa a magnetizar el núcleo, aparece una tensión peligrosa en S1-S2 y el núcleo se satura y calienta. Se cortocircuita el secundario (bornera con puente) antes de sacar un instrumento.
- **TV (de tensión)**: secundario de 100, 110 o 120 V (dividido por √3 si el primario va entre fase y neutro). **Nunca cortocircuitar su secundario**: se protege con fusibles.
- Clases: medición 0,2 - 0,2S - 0,5 - 0,5S - 1 - 3 (error de relación en %); protección 5P o 10P seguidas del factor límite de precisión (5P10: error compuesto de 5 % como máximo hasta 10 veces la corriente nominal). El factor de seguridad FS de los TI de medición limita la corriente que llega al instrumento en un cortocircuito.
- Prestación (carga) en VA: la suma de los instrumentos y los cables no tiene que superar la prestación nominal del TI, o deja de cumplirse la clase.

## 10. Impedancias de cortocircuito mínimas (IEC 60076-5)

| Potencia nominal [kVA] | ucc mínima [%] |
|---|---|
| hasta 630 | 4,0 |
| 631 a 1250 | 5,0 |
| 1251 a 2500 | 6,0 |
| 2501 a 6300 | 7,0 |
| 6301 a 25000 | 8,0 |

Fuente: tabla de impedancias mínimas reconocidas para transformadores de dos arrollamientos de IEC 60076-5:2006, según la norma india IS 2026-5:2011 basada en ella (verificar en la edición vigente). En Argentina, los fabricantes de transformadores de distribución declaran cumplir IRAM 2250 además de la serie IEC 60076; los valores garantizados (P0, Pcc, ucc) se toman siempre de la hoja de datos o del protocolo de ensayo del equipo.
