---
name: maquinas-electricas
description: "Máquinas eléctricas para TPs, ensayos de laboratorio y exámenes, con calculadora en Python: transformadores mono y trifásicos (relación de transformación, circuito equivalente, ensayos de vacío y cortocircuito, ucc, regulación, rendimiento, grupo Dyn11, paralelo, autotransformador, TI y TV), motor asincrónico trifásico (velocidad sincrónica, deslizamiento, balance de potencias, cupla, Kloss, placa, arranque directo, estrella-triángulo, autotransformador, arrancador suave, variador, clases IE, guardamotor y térmico), motores monofásicos y Steinmetz, máquina sincrónica (polos, P y Q, curvas en V, sincronización) y corriente continua. Usar cuando se pida calcular, explicar o verificar algo de un motor, un transformador o un generador: leer la placa del motor, sacar la corriente o la cupla, elegir el arranque, resolver un TP, un ensayo o un examen de máquinas eléctricas."
---

# Máquinas eléctricas

Transformadores, motores asincrónicos trifásicos y monofásicos, máquinas sincrónicas y de corriente continua. Lo que ya cubre la skill **calculos-ingenieria** (sección de conductores y caída de tensión, P = T·ω, transmisiones, potencias normalizadas IEC) no se repite: ver esa skill. Para escribir el informe del TP o del ensayo, ver la skill **informe-tecnico**.

## Método (siempre)

1. **Datos** en una tabla con unidad y fuente (placa, catálogo, consigna, medición). Anotar la conexión (estrella Y o triángulo Δ) y si cada tensión o corriente es **de línea o de fase**.
2. **Fórmula** con el significado y la unidad de cada símbolo → **reemplazo** a la vista → **resultado** con unidades.
3. **Verificación** por otro camino (rendimiento por potencias y por pérdidas, cupla por Pag/ωs y por Pmi/ω) y contra valores típicos o de catálogo.
4. Las cuentas se hacen con código, nunca de cabeza. Si la consigna o la cátedra usan otra nomenclatura (por ejemplo εcc en vez de ucc), se usa esa.

## Calculadora

`scripts/maquinas.py` (Python 3.9+, solo biblioteca estándar; acepta coma decimal). `python scripts/maquinas.py demo` resuelve todos los ejemplos de esta skill; `--help` en cada subcomando lista los datos.

```
python scripts/maquinas.py motor --P 7,5 --U 380 --n 1455 --eta 90,4 --cosphi 0,82 --TmaxTn 2,8
python scripts/maquinas.py balance --P1 8300 --Pcu1 300 --Pfe 200 --s 3 --Pmec 80
python scripts/maquinas.py arranque --P 7,5 --U 380 --n 1455 --eta 90,4 --cosphi 0,82 --IaIn 7 --TaTn 2,3 --k 0,65 0,8 --limite 3 --Tr 25
python scripts/maquinas.py trafo --S 315 --U1 13200 --U2 400 --conexion Dyn11 --U0 400 --I0 6,8 --P0 720 --Ucc 528 --Pcc 3900
python scripts/maquinas.py sincronica --f 50 --n 71,4
python scripts/maquinas.py steinmetz --P 1,5 --U 220
```

## Transformadores

**Relación y circuito equivalente.** a = N1/N2 ≈ U1/U20 ≈ I2/I1 (monofásico; U20 = tensión secundaria en vacío). El circuito aproximado referido al primario tiene Rcc = R1 + a²·R2 y Xcc = X1 + a²·X2 en serie, y la rama RFe ∥ Xμ en paralelo; una impedancia pasa del secundario al primario multiplicada por a². En trifásicos se trabaja **por fase en estrella equivalente** (Uf = U/√3, Pf = P/3) aunque el bobinado sea triángulo, y la relación de espiras depende de la conexión: en Dy, N1/N2 = √3·U1/U2.

| Ensayo | Cómo se hace | Se mide | Se obtiene |
|---|---|---|---|
| Vacío | BT a tensión nominal, AT abierto | U0, I0, P0 (y U20) | a; P0 ≈ PFe; cosφ0 = P0/(√3·U0·I0); IFe = I0·cosφ0; Iμ = I0·senφ0; RFe = Uf/IFe; Xμ = Uf/Iμ |
| Cortocircuito | BT en cortocircuito; AT con tensión reducida hasta que circula In | Ucc, Icc, Pcc | ucc; Pcc ≈ PCu a In; Zcc = (Ucc/√3)/In; Rcc = Pcc/(3·In²); Xcc = √(Zcc² − Rcc²) |

- P0 ≈ PFe porque I0 es una fracción chica de In (el cobre casi no pierde); Pcc ≈ PCu porque con Ucc de pocos % el flujo y PFe son despreciables. En monofásicos, las mismas fórmulas sin el √3 ni el 3.
- Si el cortocircuito no se hizo a In: Pcc,n = Pcc·(In/Icc)² y Ucc,n = Ucc·In/Icc.
- ucc % = Ucc,n/Un·100; uR % = Pcc,n/Sn·100; uX % = √(ucc² − uR²). Corriente de cortocircuito permanente con red de potencia infinita: Icc = In·100/ucc.
- Impedancias mínimas reconocidas de IEC 60076-5: ucc = 4 % hasta 630 kVA; 5 % de 631 a 1250 kVA; 6 % de 1251 a 2500 kVA.
- **Caída de tensión** (primario a tensión nominal, índice de carga C = I2/I2n): ε % ≈ C·(uR·cosφ + uX·senφ) + C²·(uX·cosφ − uR·senφ)²/200, con senφ negativo si la carga es capacitiva (ε puede salir negativa: la tensión sube). U2 = U20·(1 − ε/100). En el ejemplo coincide con el cálculo fasorial exacto hasta el cuarto decimal.
- **Rendimiento**: η = C·Sn·cosφ / (C·Sn·cosφ + P0 + C²·Pcc,n). Es máximo cuando las pérdidas en el cobre igualan a las del hierro: C²·Pcc = P0 → Copt = √(P0/Pcc).

**Ejemplo resuelto** (datos del ejemplo, no de un catálogo): 315 kVA, 13,2/0,4 kV, Dyn11. Vacío del lado BT a 400 V: I0 = 6,8 A, P0 = 720 W. Cortocircuito del lado AT a In: Ucc = 528 V, Pcc = 3900 W.

| Resultado | Valor |
|---|---|
| In AT / In BT | 13,78 A / 454,66 A |
| Relación de tensiones / de espiras (Dy) | 33,00 / 57,16 |
| ucc / uR / uX | 4,00 % / 1,238 % / 3,804 % |
| Rcc / Xcc por fase, referidos a AT | 6,848 Ω / 21,039 Ω (a BT: 6,29 mΩ / 19,32 mΩ) |
| cosφ0 / RFe / Xμ por fase, referidos a BT | 0,1528 / 222,2 Ω / 34,37 Ω |
| Caída a plena carga, cosφ = 0,8 inductivo | 3,30 % → U2 ≈ 386,8 V |
| η a plena carga, cosφ = 0,8 | 98,20 % |
| η máxima (C = 0,430) | 98,69 % |
| Icc permanente en BT | 11.367 A |

**Conexiones y otros.** Dyn11: AT en triángulo, BT en estrella con neutro accesible, índice 11 → la BT atrasa 11 × 30° = 330° (adelanta 30°) respecto de la AT. Paralelo: mismas relaciones de tensión (diferencias menores de 0,4 %), mismo índice horario, ucc iguales o que difieran menos de 10 % y potencias que no difieran más de 2:1; cada uno toma carga en proporción a Sn/ucc. Autotransformador: la potencia que transforma el bobinado es S·(1 − U2/U1) (400/320 V → 20 %), pero no aísla y su ucc es baja. Transformadores de medida (IEC 61869-2 y 61869-3): TI con secundario de 5 A o 1 A, **nunca abrir su secundario con corriente en el primario** (se cortocircuita antes de sacar el instrumento); TV con secundario de 100, 110 o 120 V, **nunca cortocircuitar su secundario**.

Detalle, más ejemplos (paralelo, grupo vectorial, TI y TV): `references/transformadores.md`.

## Motor asincrónico trifásico

- **Velocidad sincrónica**: ns = 60·f/p [rpm], con p = **pares** de polos. A 50 Hz: 2 polos 3000, 4 polos 1500, 6 polos 1000, 8 polos 750 rpm.
- **Deslizamiento**: s = (ns − n)/ns; frecuencia de las corrientes del rotor f2 = s·f.
- **Balance de potencias**: P1 = √3·U·I·cosφ → menos Pcu1 (cobre del estator) y PFe → **Pag** (entrehierro) → Pcu2 = s·Pag (cobre del rotor) → Pmi = (1 − s)·Pag (mecánica interna) → menos Pmec (rozamiento y ventilación) → Pu (útil en el eje).
- **Cupla**: T = Pag/ωs = Pmi/ω, con ω = 2π·n/60 [rad/s]; en la práctica T [N·m] = 9550·P [kW]/n [rpm].
- **Placa**: la potencia es la **útil en el eje**, no la absorbida. In = P/(√3·U·η·cosφ). "380/660 V" quiere decir triángulo en 380 V y estrella en 660 V; "220/380 V", triángulo en 220 V y estrella en 380 V. Servicio S1 = continuo; aislamiento clase B 130 °C, F 155 °C, H 180 °C. El factor de servicio (FS) es de NEMA: IEC no lo reconoce.

**Ejemplo resuelto** (placa del ejemplo): 7,5 kW, 4 polos, 380 V Δ, 50 Hz, 1455 rpm, η = 90,4 %, cosφ = 0,82; catálogo Ia/In = 7, Ta/Tn = 2,3, Tmax/Tn = 2,8.
ns = 1500 rpm; s = 3,00 %; f2 = 1,50 Hz; In = 7500/(√3·380·0,904·0,82) = 15,37 A; Tn = 7500/152,37 = 49,22 N·m; P1 = 8296 W; pérdidas = 796 W.
Balance con P1 = 8300 W, Pcu1 = 300 W, PFe = 200 W, s = 3 %, Pmec = 80 W: Pag = 7800 W; Pcu2 = 234 W; Pmi = 7566 W; Pu = 7486 W; η = 90,19 %; T = 49,66 N·m.

**Curva cupla-velocidad (Kloss).** T/Tmax = 2/(s/sk + sk/s), con sk = sn·(λ + √(λ² − 1)) y λ = Tmax/Tn. Sale del circuito equivalente despreciando R1 (verificado: coincide exacto). Zona estable entre s = sk y s = 0. En el ejemplo sk = 0,1625 (Tmax a 1256 rpm), pero en s = 1 Kloss da 0,89·Tn contra 2,3·Tn del catálogo: **para la cupla de arranque se usa el catálogo**, porque el rotor de barras profundas cambia R2 con la frecuencia.

**Arranque** (Ia y Ta = corriente y cupla de arranque directo, de catálogo):

| Método | Corriente de línea | Cupla | Cuándo |
|---|---|---|---|
| Directo | Ia (Ia/In de catálogo) | Ta | Motores chicos o red que lo admite |
| Estrella-triángulo | Ia/3 | Ta/3 | Solo si el motor trabaja **en triángulo a la tensión de red** (380/660 V en red de 380 V), con 6 bornes; carga liviana al arrancar |
| Autotransformador, toma k | k²·Ia | k²·Ta | Tomas típicas 50, 65 y 80 %; más cupla que Y-Δ solo a cambio de más corriente |
| Resistencias estatóricas o arrancador suave (tensión x·U) | x·Ia | x²·Ta | Cargas de cupla baja al arrancar (bombas centrífugas, ventiladores) |
| Variador de frecuencia (V/f) | ≈ In para Tn | Tn desde n = 0 (más, según la sobrecarga del equipo) | Arranques pesados o control de velocidad |

**Trampa clave**: con la misma corriente de línea, el autotransformador da **la misma cupla** que la estrella-triángulo (k = 1/√3 = 57,7 % → k² = 1/3), no más. La tensión reducida por resistencias o arrancador suave da menos: limitando a la misma corriente, la cupla cae con el cuadrado.

Ejemplo (motor anterior, carga que pide 25 N·m al arrancar): directo 107,6 A y 113,2 N·m; Y-Δ 35,9 A y 37,7 N·m; autotransformador 65 % 45,5 A y 47,8 N·m; 80 % 68,9 A y 72,5 N·m; arrancador suave limitado a 3·In 46,1 A y 20,8 N·m (**no arranca**: 20,8 es menor que 25). Además tiene que sobrar cupla en toda la aceleración, no solo en n = 0.

**Variador V/f**: por debajo de 50 Hz se mantiene U/f constante (380 V/50 Hz = 7,6 V/Hz → 190 V a 25 Hz) para que el flujo y la cupla disponible sean los nominales; por encima de 50 Hz la tensión ya no sube: debilitamiento de campo, potencia constante y cupla que baja. A baja velocidad un motor autoventilado se enfría peor.
**Inversión de giro**: permutar dos fases (con contactores enclavados). **Frenado**: contracorriente (permutar dos fases y cortar en n = 0), inyección de corriente continua, regenerativo (el motor pasa a generador por encima de ns, con variador) o freno mecánico.
**Eficiencia**: clases IE de IEC 60034-30-1 (la edición 2025 define IE1 a IE5, de 0,12 a 1000 kW, 2, 4, 6 y 8 polos). Ejemplo con la tabla de la edición 2014: 7,5 kW, 4 polos, 50 Hz → IE2 88,7 %, IE3 90,4 %, IE4 92,6 % (el motor del ejemplo es IE3 justo). En Argentina el etiquetado de motores trifásicos sigue IRAM 62405.
**Protección**: guardamotor, o contactor con relé térmico, ajustado a la **In de placa**. En estrella-triángulo, si el relé está en el circuito de las fases del motor (debajo del contactor de triángulo) se ajusta a 0,58·In; si está aguas arriba del arrancador, a In. Clase de disparo según el tiempo de arranque: 10 (arranque normal), 20 o 30 (arranques pesados).

Detalle (ensayos de vacío y rotor bloqueado, circuito equivalente, esquemas de arranque, tabla IE, clases de disparo): `references/motor-asincronico.md`.

## Motores monofásicos

Una sola bobina crea un campo **pulsante**, que equivale a dos campos giratorios iguales en sentidos opuestos: en reposo sus cuplas se anulan y el motor no arranca solo (si se lo empuja, gira para ese lado). Para arrancar se agrega una bobina auxiliar desfasada:

| Tipo | Cómo arranca | Cupla de arranque | Uso típico |
|---|---|---|---|
| Fase partida | Auxiliar de alta resistencia, se desconecta con centrífugo (≈ 75 % de ns) | Moderada | Ventiladores, bombas chicas |
| Capacitor de arranque | Capacitor electrolítico en serie con la auxiliar, se desconecta | Alta | Compresores, bombas |
| Capacitor permanente | Capacitor de marcha siempre conectado | Baja | Ventiladores, extractores |
| Dos capacitores | Arranque + marcha | Alta, con buen rendimiento | Compresores, máquinas herramienta |
| Espira de sombra | Espira en cortocircuito en parte del polo | Muy baja | Potencias muy chicas |
| Universal (serie) | Colector y escobillas, no necesita desfasaje; anda en CA y CC | Alta, velocidad alta | Herramientas, electrodomésticos |

Para invertir el giro de un motor de capacitor se invierte la conexión de la bobina auxiliar respecto de la principal.

**Steinmetz** (motor trifásico en red monofásica): el motor va en la conexión de la tensión monofásica (220/380 V → triángulo en 220 V) y un capacitor de marcha une la tercera fase con uno de los bornes de red; pasarlo al otro borne invierte el giro. Regla práctica: **≈ 70 µF por kW a 230 V**; para arrancar con carga se agrega uno de arranque de hasta 2 veces el de marcha. Entrega ≈ 70 a 80 % de la potencia nominal. Detalle, deducción y ejemplo: `references/monofasicos-sincronica-cc.md`.

## Máquina sincrónica

- Gira **exactamente** a n = 60·f/p. Rotor liso (turbogeneradores de 2 o 4 polos, 3000 o 1500 rpm a 50 Hz) o polos salientes (hidráulicos lentos, muchos polos: a 71,4 rpm y 50 Hz son p = 60·50/71,4 = 42 pares, 84 polos; velocidad exacta 71,43 rpm).
- Rotor liso, despreciando la resistencia, con E y V de línea y Xs por fase: **P = E·V·senδ/Xs** y **Q = (E·V·cosδ − V²)/Xs** (δ = ángulo de carga). Límite de estabilidad estática en δ = 90°: Pmax = E·V/Xs. Ejemplo: E = 16 kV, V = 13,2 kV, Xs = 4 Ω, δ = 20° → P = 18,06 MW; Q = 6,06 Mvar entregados; Pmax = 52,8 MW.
- **Excitación**: con P fija, la corriente de campo regula Q. Sobreexcitada (E·cosδ mayor que V) entrega reactivo a la red, como un capacitor; subexcitada lo absorbe. **Curvas en V**: corriente del estator en función de la de campo, con mínimo en cosφ = 1.
- **Sincronizar con la red**: igual tensión, igual frecuencia, igual secuencia de fases y en fase (ángulo cero) al cerrar el interruptor; se controla con sincronoscopio, lámparas o un equipo automático.
- **Motor sincrónico**: velocidad constante; sobreexcitado corrige el factor de potencia de la planta. No arranca solo: arranca como asincrónico con la jaula amortiguadora o con variador.

## Máquinas de corriente continua (breve)

E = k·Φ·n (n en rpm); T = (60/2π)·k·Φ·Ia; motor: U = E + Ra·Ia → n = (U − Ra·Ia)/(k·Φ). Excitación independiente, derivación, serie (alta cupla de arranque; **nunca en vacío**: se embala) o compuesta. Arranque: Ia = U/Ra es enorme → resistencia de arranque o tensión reducida. Velocidad: tensión de armadura (cupla constante hasta la velocidad base) y debilitamiento de campo (potencia constante por encima). Invertir el giro: invertir la armadura o el campo, no los dos. Ejemplo y detalle en `references/monofasicos-sincronica-cc.md`.

## Errores frecuentes y trampas

- Confundir **polos con pares de polos** (un motor de 4 polos tiene p = 2).
- Tomar la potencia de placa como absorbida: es la útil; la absorbida es P/η.
- Mezclar valores de línea y de fase: olvidar el √3 en U y el 3 en P al pasar a una fase.
- Suponer que la relación de espiras es U1/U2 en un Dy o Yd.
- Usar Pcc y Ucc medidos a una corriente distinta de In sin corregirlos.
- Arrancar en estrella-triángulo un motor 220/380 V en red de 380 V: ese motor va en estrella fija; en triángulo a 380 V sus bobinas quedarían con √3 veces su tensión.
- Creer que el autotransformador da más cupla que la Y-Δ "porque es mejor": a igual corriente de línea da la misma.
- Calcular la cupla de arranque con Kloss, o el relé térmico de una Y-Δ siempre a In.
- Rendimiento de un transformador sin el cosφ de la carga, o suponer que el máximo es a plena carga.
- Abrir el secundario de un TI en servicio.

## Cómo presentar el resultado

- Tabla de datos con fuente; fórmulas numeradas con sus símbolos y unidades; resultados con unidades y comparación con la placa o el catálogo (por ejemplo, In calculada contra In de placa).
- En ensayos de laboratorio: esquema del circuito de ensayo, instrumentos (alcance y clase), planilla de mediciones, cálculos y discusión de las diferencias con los valores nominales.
- Si suma, el diagrama fasorial, la curva cupla-velocidad con la cupla resistente superpuesta o el reparto de potencias en un gráfico.

## Verificación

1. Correr `python scripts/maquinas.py demo` y el subcomando del caso: los resultados tienen que coincidir con el cálculo presentado.
2. Órdenes de magnitud: deslizamiento nominal de pocos %; ucc entre 4 y 6 % en distribución; η del motor contra la tabla IE de su potencia; In calculada cerca de la de placa.
3. Coherencia: η = Pu/P1 = 1 − pérdidas/P1; T = Pag/ωs = Pmi/ω; regulación aproximada contra la fasorial.
4. Recorrer la consigna punto por punto.
