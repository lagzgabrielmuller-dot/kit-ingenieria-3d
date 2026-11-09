# Motores monofásicos, Steinmetz, máquina sincrónica y corriente continua

Leer cuando el TP pide explicar o conectar un motor monofásico, hacer andar un motor trifásico en 220 V monofásico, calcular P, Q y ángulo de carga de un generador, sincronizar, corregir el factor de potencia con un motor sincrónico o resolver una máquina de corriente continua.

## 1. Motores monofásicos

- **Por qué no arrancan solos**: la bobina principal sola crea un campo pulsante, que equivale a dos campos giratorios de la mitad de amplitud y sentidos opuestos (teorema de Leblanc o de Ferraris). En reposo las dos cuplas son iguales y se anulan; si el rotor ya gira, domina el campo que va en su sentido y el motor acelera para ese lado.
- **Solución**: una bobina auxiliar desplazada 90° eléctricos en el estator, con una corriente desfasada de la principal (por resistencia o por capacitor). Las dos bobinas forman un campo giratorio, más parecido al de un trifásico cuanto más cerca de 90° esté el desfasaje de las corrientes.
- **Fase partida**: auxiliar de alambre fino (más resistencia, menos reactancia). Un interruptor centrífugo la desconecta alrededor del 75 % de la velocidad sincrónica; si el centrífugo no abre, la auxiliar se quema.
- **Capacitor de arranque**: capacitor electrolítico para CA, de servicio intermitente, en serie con la auxiliar; da más desfasaje y más cupla de arranque. También se desconecta con centrífugo o relé.
- **Capacitor permanente**: capacitor de marcha (polipropileno, servicio continuo) siempre conectado; poca cupla de arranque, marcha silenciosa y buen cosφ.
- **Dos capacitores**: uno de arranque (se desconecta) y uno de marcha (queda); buena cupla de arranque y buen rendimiento.
- **Espira de sombra**: parte de cada polo abrazada por una espira en cortocircuito que atrasa el flujo; muy simple, cupla de arranque muy baja y rendimiento bajo; giro fijo.
- **Universal**: motor serie con colector y escobillas; anda con CA y con CC, gira rápido y la velocidad baja mucho con la carga. Las escobillas se gastan y generan chispas.
- **Identificar bobinas** (fase partida o capacitor de arranque): la principal suele tener menos resistencia que la auxiliar (alambre más grueso); medir con el óhmetro y comparar con el esquema de la placa.
- **Invertir el giro**: invertir la conexión de la bobina auxiliar respecto de la principal (o al revés). Dar vuelta el enchufe no cambia nada.

## 2. Conexión Steinmetz (trifásico en red monofásica)

**Conexión**: el motor va en la conexión que corresponde a la tensión de la red monofásica (un motor 220/380 V va en triángulo en 220 V). La red se conecta a dos bornes (L1 y L2) y el capacitor de marcha une el tercer borne con uno de los dos bornes de red; **pasarlo al otro borne invierte el giro**.

**Valores orientativos** (fabricante de motores ATEK, que cita la regla de la norma DIN 48501, hoy retirada):
- Capacitor de marcha ≈ **70 µF por kW a 230 V**.
- Capacitor de arranque adicional, en paralelo durante el arranque: hasta ≈ 2 veces el de marcha.
- Potencia disponible ≈ 80 % de la nominal (otras fuentes dicen ≈ 70 %).
- Cupla de arranque con solo el de marcha: 20 a 50 % de la nominal; con el de arranque, cerca de 100 %.

**De dónde sale** (verificado con un cálculo nodal): si el motor fuera una carga equilibrada de impedancia Z por fase, las tres tensiones quedan perfectamente equilibradas solo si el ángulo de Z es 60° (cosφ = 0,5) y Xc = |Z|/√3, o sea C = P1/(√3·ω·U²·cosφ). Para 1 kW con η = 0,8 en 230 V da 87 µF con cosφ = 0,5 y 56 µF con cosφ = 0,78: la regla de 70 µF/kW queda entre los dos, y el equilibrio en servicio nunca es perfecto (por eso se pierde potencia). Como Q = ω·C·U², para un motor diseñado para otra tensión se escala con (230/U)².

**Ejemplo**: motor de 1,5 kW, 220/380 V, en red de 220 V → triángulo; C ≈ 70·1,5·(230/220)² ≈ 115 µF de marcha (valor comercial más cercano); de arranque hasta ≈ 230 µF; potencia disponible ≈ 1,05 a 1,2 kW (`python scripts/maquinas.py steinmetz --P 1,5 --U 220`).

**En la práctica**: capacitor de marcha para servicio permanente en CA con tensión nominal mayor que la de red (en vacío la tensión del capacitor puede superar la de red); medir con pinza la corriente de los tres bornes del motor con la carga real: ninguna tiene que superar la In de placa; si una se pasa, el capacitor no es el adecuado o la carga es excesiva.

## 3. Máquina sincrónica

**Velocidad**: n = 60·f/p exacta, sin deslizamiento. A 50 Hz: 1 par 3000 rpm, 2 pares 1500 rpm, 42 pares 71,43 rpm. Los generadores hidráulicos de baja caída giran lento y llevan muchos polos salientes; los de turbinas de vapor o gas, rotor liso de 2 o 4 polos.

**Ecuación por fase** (generador, R despreciada): E = V + j·Xs·I. Con E y V de línea (estrella equivalente) y Xs por fase:
- P = E·V·senδ/Xs; Q = (E·V·cosδ − V²)/Xs (Q positiva = entregada a la red).
- Pmax = E·V/Xs en δ = 90° (límite de estabilidad estática); en servicio δ queda bastante por debajo.
- Polos salientes (Xd y Xq): P = E·V·senδ/Xd + (V²/2)·(1/Xq − 1/Xd)·sen 2δ; el segundo término es la cupla de reluctancia (existe aun sin excitación).

**Ejemplos** (rotor liso, E = 16 kV, V = 13,2 kV, Xs = 4 Ω): con δ = 20° → P = 18,06 MW y Q = 6,06 Mvar entregados; para P = 10 MW con la misma excitación → δ = 10,92° y Q = 8,28 Mvar; Pmax = 52,8 MW. Con polos salientes, Xd = 4 Ω y Xq = 2,6 Ω, a δ = 20° se suman 7,54 MW de cupla de reluctancia (P = 25,60 MW).

**Excitación y curvas en V**:
- Conectada a una red fuerte, V y f los fija la red: la turbina fija P y la corriente de campo fija E y con ella Q.
- Sobreexcitada (E·cosδ mayor que V): entrega reactivo (se ve desde la red como un capacitor). Subexcitada: lo absorbe (como una inductancia).
- Curvas en V: corriente del estator en función de la de campo, una curva por cada P; el mínimo de cada curva es cosφ = 1. A la izquierda subexcitada, a la derecha sobreexcitada; hay un límite de subexcitación por estabilidad.

**Sincronización con la red** (condiciones al cerrar el interruptor):
1. Igual tensión eficaz.
2. Igual frecuencia (en la práctica, el generador apenas más rápido para que tome carga).
3. Igual secuencia de fases (se comprueba una vez, con un secuencímetro, al montar).
4. Igual fase: ángulo cero entre las tensiones de las mismas fases.
- Métodos: lámparas apagadas (una lámpara entre cada par de fases correspondientes: se cierra cuando las tres están apagadas a la vez), lámparas rotantes (dos cruzadas: el sentido del giro de la luz dice si el generador va rápido o lento), sincronoscopio, o sincronizador automático con relé de verificación de sincronismo. Cerrar fuera de fase produce corrientes y cuplas muy grandes.

**Motor sincrónico y corrección del factor de potencia**:
- No arranca solo (con el rotor quieto la cupla media es cero): arranca como asincrónico con la jaula amortiguadora, con el campo cerrado sobre una resistencia, y se excita cerca de la velocidad de sincronismo; o con variador.
- Sobreexcitado entrega reactivo a la planta. Potencia reactiva para pasar de cosφ1 a cosφ2 con P constante: Q = P·(tanφ1 − tanφ2).
- Ejemplo: planta de 400 kW con cosφ = 0,75 que se quiere llevar a 0,95 → Q = 400·(0,8819 − 0,3287) = 221,3 kvar. Un motor sincrónico que mueve 150 kW y entrega esos 221,3 kvar trabaja con S = √(150² + 221,3²) = 267,3 kVA (cosφ = 0,561 capacitivo): se elige por kVA, no por kW. Sin carga mecánica (compensador sincrónico) da solo reactivo.

## 4. Máquinas de corriente continua

**Ecuaciones**:
- Fem: E = k·Φ·n, con n en rpm y k = p·Z/(60·a) (p pares de polos, Z conductores activos del inducido, a pares de ramas en paralelo; algunos libros usan otra letra o el número de ramas: usar la de la cátedra).
- Cupla: T = (p·Z/(2π·a))·Φ·Ia = (60/2π)·k·Φ·Ia. Control: E·Ia = T·ω.
- Motor: U = E + Ra·Ia → n = (U − Ra·Ia)/(k·Φ). Generador: E = U + Ra·Ia.

**Excitaciones**:
- Independiente y derivación (shunt): velocidad casi constante con la carga.
- Serie: Φ crece con Ia → cupla de arranque muy alta y velocidad que baja mucho con la carga; **en vacío se embala** (nunca arrancarlo sin carga ni con correa).
- Compuesta (aditiva): intermedia entre las dos.

**Arranque**: con el rotor quieto E = 0 → Ia = U/Ra, muchas veces la nominal. Se agrega una resistencia de arranque R = U/Iarr − Ra que se va sacando, o se arranca con tensión reducida (rectificador controlado).
**Control de velocidad**: bajando la tensión de armadura (cupla constante, hasta la velocidad base) o debilitando el campo (por encima de la base, potencia constante; nunca cortar el campo de un motor en marcha: se embala).
**Inversión de giro**: invertir la armadura o el campo, no los dos.

**Ejemplo** (motor derivación): U = 220 V, Ra = 0,5 Ω, Ia = 20 A, n = 1500 rpm.
- E = 220 − 0,5·20 = 210 V; k·Φ = 210/1500 = 0,14 V/rpm; T = 9,549·0,14·20 = 26,74 N·m; control: E·Ia = 4200 W = T·ω.
- Arranque directo: Ia = 220/0,5 = 440 A (22 veces la de servicio). Para limitarla a 40 A: R total = 220/40 = 5,5 Ω → resistencia de arranque de 5,0 Ω.
- Campo al 80 % con la misma cupla: Ia = 20/0,8 = 25 A; E = 220 − 0,5·25 = 207,5 V; n = 207,5/(0,8·0,14) = 1852,7 rpm.
