# Motor asincrónico trifásico: detalle y ejemplos

Leer cuando el TP pide el circuito equivalente, los ensayos de vacío y de rotor bloqueado, los esquemas de arranque, el tiempo de arranque, la tabla de clases IE o la elección de la protección. Los ejemplos usan el motor de SKILL.md: 7,5 kW, 4 polos, 380 V Δ, 1455 rpm, In = 15,37 A, Tn = 49,22 N·m.

## 1. Circuito equivalente por fase (estrella equivalente)

- Estator R1 + jX1; rama paralelo RFe ∥ jXμ; rotor referido al estator R2' + jX2'; la carga mecánica es la resistencia R2'·(1 − s)/s.
- Potencias (I2' = corriente del rotor referida): Pag = 3·I2'²·R2'/s; Pcu2 = 3·I2'²·R2' = s·Pag; Pmi = 3·I2'²·R2'·(1 − s)/s = (1 − s)·Pag.
- Cupla: T = Pag/ωs. Despreciando R1, la cupla máxima vale Tmax = 3·Uf²/(2·ωs·Xcc) y aparece en sk = R2'/Xcc: **Tmax no depende de R2'** y sk es proporcional a R2'. De ahí sale la fórmula de Kloss.
- La cupla es proporcional al cuadrado de la tensión: con 90 % de la tensión queda 81 % de la cupla en cada velocidad.

## 2. Ensayos de vacío y de rotor bloqueado

**Resistencia del estator**: se mide en corriente continua entre dos bornes (Rb). En la estrella equivalente R1 = Rb/2, sea el bobinado Y o Δ.

**Vacío**: motor desacoplado, a tensión y frecuencia nominales. Se mide U0, I0, P0.
- P0 = PFe + Pmec + 3·I0²·R1 → PFe + Pmec = P0 − 3·I0²·R1.
- Para separar PFe de Pmec se repite bajando la tensión y se extrapola la recta (P0 − Pcu1) en función de U² hasta U = 0: la ordenada al origen es Pmec.
- I0 es mucho mayor en proporción que en un transformador por el entrehierro: el cosφ0 es muy bajo.

**Rotor bloqueado (cortocircuito)**: se traba el rotor y se sube la tensión desde cero hasta que circula In. Se mide Ucc, Icc, Pcc.
- Zcc = (Ucc/√3)/Icc; Rcc = Pcc/(3·Icc²); Xcc = √(Zcc² − Rcc²); R2' = Rcc − R1; reparto habitual X1 = X2' = Xcc/2.
- Corriente de arranque directo estimada: Ia ≈ Icc·Un/Ucc.
- Ojo: a 50 Hz el rotor de barras profundas tiene más resistencia que en marcha (donde f2 es de 1 o 2 Hz). Por eso este ensayo se hace a veces con frecuencia reducida, y el R2' de 50 Hz sobreestima las pérdidas del rotor en servicio.

**Ejemplo** (datos del ejemplo): Rb = 1,10 Ω → R1 = 0,55 Ω. Vacío: 380 V, 6,0 A, 420 W → cosφ0 = 0,1064; Pcu1 = 3·6,0²·0,55 = 59,4 W; PFe + Pmec = 360,6 W. Rotor bloqueado: 55 V, 15,4 A, 760 W → Zcc = 2,062 Ω; Rcc = 1,068 Ω; Xcc = 1,764 Ω; R2' = 0,518 Ω; X1 = X2' = 0,882 Ω; cosφcc = 0,518; Ia ≈ 15,4·380/55 = 106,4 A (6,92·In).
Verificación: con esos parámetros, el circuito a s = 3 % da T ≈ 49,5 N·m e I ≈ 14,6 A, cerca de la placa (49,2 N·m y 15,4 A).

## 3. Curva cupla-velocidad

- Puntos de catálogo: cupla de arranque Ta (s = 1), cupla mínima durante la aceleración, cupla máxima Tmax (en sk), cupla nominal Tn (en sn) y cupla cero en ns.
- Kloss: T = 2·Tmax/(s/sk + sk/s); con λ = Tmax/Tn y sn: sk = sn·(λ + √(λ² − 1)). Sirve entre vacío y la cupla máxima; para s = 1 se usa la Ta del catálogo.
- Zona estable: entre sk y 0 (si la carga sube, el motor frena un poco, s aumenta y la cupla también). Entre s = 1 y sk es inestable.
- Rotor bobinado: resistencias en el rotor corren sk hacia s = 1 y suben la cupla de arranque **bajando** la corriente; es el único método que mejora las dos cosas.
- Para dibujarla: calcular T con Kloss para s entre sn y 1 en un script, y superponer la cupla resistente de la carga (constante, cuadrática para bombas y ventiladores, etc.). El punto de trabajo es el cruce.

## 4. Tiempo de arranque

t ≈ J·ω / Tacel, con J = inercia total referida al eje del motor [kg·m²] (J de la carga dividida por i² si hay reducción), ω = velocidad final [rad/s] y Tacel = cupla media del motor menos cupla media de la carga durante la aceleración [N·m].
Ejemplo: J = 0,5 kg·m², 1455 rpm (152,37 rad/s), Tacel = 60 N·m → t ≈ 1,27 s. Con estrella-triángulo la Tacel baja mucho y el tiempo crece: puede hacer falta un relé de clase 20 o 30.

## 5. Esquemas de arranque

- **Directo**: interruptor o fusibles, contactor y relé térmico, o un guardamotor y contactor.
- **Estrella-triángulo**: bornera de 6 bornes (U1-V1-W1 y U2-V2-W2) sin puentes. Tres contactores: línea KM1, estrella KM3 (une U2-V2-W2) y triángulo KM2. Secuencia: KM1 + KM3 → temporizador → abre KM3 → cierra KM2. KM2 y KM3 con enclavamiento eléctrico y mecánico. La transición es abierta: hay un pico de corriente y de cupla al pasar a triángulo, menor cuanto más cerca de la velocidad nominal se haga el cambio.
- **Autotransformador**: tomas de 50, 65 y 80 %. En la conexión Korndörfer la transición es cerrada (el motor no queda sin tensión), con menos picos.
- **Resistencias o reactancias estatóricas**: en serie con cada fase, se cortocircuitan al final. Bajan la corriente en x y la cupla en x².
- **Arrancador suave**: tiristores en antiparalelo que suben la tensión en rampa y limitan la corriente; al terminar, un contactor de bypass. Permite parada suave (útil en bombas para evitar el golpe de ariete). Misma física que la tensión reducida: cupla en x².
- **Variador de frecuencia**: rectificador, bus de continua y ondulador con transistores IGBT (modulación PWM). Arranca con corriente cercana a la nominal y cupla nominal, regula velocidad y puede frenar. Se elige por corriente del motor y tipo de carga, con la sobrecarga que declara el fabricante.

## 6. Variador V/f

- Por debajo de la frecuencia base: U/f constante (380 V/50 Hz = 7,6 V/Hz; 190 V a 25 Hz; 266 V a 35 Hz) → flujo constante → cupla disponible ≈ nominal. A muy baja frecuencia se agrega un refuerzo de tensión (boost) porque la caída en R1 pesa más.
- Por encima de la base: la tensión queda en la nominal; el flujo baja con 1/f, la cupla disponible también y la potencia queda ≈ constante.
- Un motor autoventilado a baja velocidad se enfría peor: con cupla constante a pocas rpm hace falta bajar la carga o poner ventilación forzada (dato del fabricante del motor).

## 7. Inversión de giro y frenado

- **Inversión**: permutar dos fases. Con dos contactores (adelante y atrás) enclavados eléctrica y mecánicamente; nunca los dos cerrados a la vez (sería un cortocircuito entre fases).
- **Contracorriente**: se permutan dos fases con el motor girando; frena fuerte pero con corriente mayor que la de arranque, y hay que cortar en n = 0 (detector de velocidad) o el motor arranca al revés.
- **Inyección de corriente continua**: se desconecta la red y se alimenta el estator con continua; el campo fijo frena el rotor. No retiene en reposo.
- **Regenerativo**: con variador, bajando la frecuencia el motor pasa a ns menor que n y funciona como generador; la energía va a una resistencia de frenado o vuelve a la red.
- **Mecánico**: motofreno con freno electromagnético que actúa al quitar la tensión (aparatos de elevación).

## 8. Clases de eficiencia IE (IEC 60034-30-1)

La edición 2 (2025-12) define IE1 a IE5 para motores de 0,12 a 1000 kW, 2, 4, 6 u 8 polos, 50 V a 1000 V, 50 o 60 Hz. Rendimientos mínimos a 50 Hz, 4 polos, de la edición 2014 (nota técnica de ABB sobre IEC 60034-30-1; verificar en la edición vigente):

| kW | IE1 | IE2 | IE3 | IE4 | | kW | IE1 | IE2 | IE3 | IE4 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0,75 | 72,1 | 79,6 | 82,5 | 85,7 | | 11 | 87,6 | 89,8 | 91,4 | 93,3 |
| 1,1 | 75,0 | 81,4 | 84,1 | 87,2 | | 15 | 88,7 | 90,6 | 92,1 | 93,9 |
| 1,5 | 77,2 | 82,8 | 85,3 | 88,2 | | 18,5 | 89,3 | 91,2 | 92,6 | 94,2 |
| 2,2 | 79,7 | 84,3 | 86,7 | 89,5 | | 22 | 89,9 | 91,6 | 93,0 | 94,5 |
| 3 | 81,5 | 85,5 | 87,7 | 90,4 | | 30 | 90,7 | 92,3 | 93,6 | 94,9 |
| 4 | 83,1 | 86,6 | 88,6 | 91,1 | | 37 | 91,2 | 92,7 | 93,9 | 95,2 |
| 5,5 | 84,7 | 87,7 | 89,6 | 91,9 | | 45 | 91,7 | 93,1 | 94,2 | 95,4 |
| 7,5 | 86,0 | 88,7 | 90,4 | 92,6 | | 55 | 92,1 | 93,5 | 94,6 | 95,7 |

Misma fuente, otras polaridades: 7,5 kW 2 polos: 86,0 / 88,1 / 90,1 / 91,7 %; 7,5 kW 6 polos: 84,7 / 87,2 / 89,1 / 91,3 %; 15 kW 2 polos: 88,7 / 90,3 / 91,9 / 93,3 %; 15 kW 6 polos: 87,7 / 89,7 / 91,2 / 92,9 % (IE1 / IE2 / IE3 / IE4).

En Argentina, el etiquetado de eficiencia energética de motores trifásicos de inducción sigue IRAM 62405 (motores de 0,75 a 30 kW, 380 V, 50 Hz, 2, 4 y 6 polos, servicio S1); los monofásicos, IRAM 62409.

## 9. Protección

- **Guardamotor**: interruptor con disparo térmico regulable (sobrecarga) y magnético fijo (cortocircuito). El térmico se ajusta a la In de placa a la tensión de servicio.
- **Contactor + relé térmico**: el relé protege contra sobrecarga y falta de fase; el cortocircuito lo cubren fusibles o un interruptor aguas arriba, coordinados según el catálogo del fabricante (coordinación tipo 1 o tipo 2 de IEC 60947-4-1).
- **Estrella-triángulo**: si el relé está debajo del contactor de triángulo, ve la corriente de fase del bobinado y se ajusta a 0,58·In (= In/√3); si está aguas arriba del arrancador, a In.
- **Clase de disparo** (IEC 60947-4-1): tiempo de disparo a 7,2 veces la corriente de ajuste, desde frío.

| Clase | Tiempo de disparo a 7,2·Ir |
|---|---|
| 10A | 2 a 10 s |
| 10 | 4 a 10 s |
| 20 | 6 a 20 s |
| 30 | 9 a 30 s |

Se elige una clase que no dispare durante el arranque: en la curva del relé, el tiempo de disparo a la corriente de arranque tiene que superar con margen el tiempo de arranque calculado (sección 4). Clase 10 para arranques normales; 20 o 30 para ventiladores grandes, molinos o cargas de mucha inercia. Para protección térmica directa del bobinado se usan sondas PTC con su relé.
