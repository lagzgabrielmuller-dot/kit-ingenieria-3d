---
name: transferencia-de-calor
description: "Transferencia de calor en equipos y procesos con memoria de cálculo: conducción en paredes planas y cilíndricas multicapa (resistencias en serie y en paralelo, puentes térmicos, radio crítico), convección natural (placas y cilindros, Churchill y Chu) y forzada (placa plana; Gnielinski y Dittus-Boelter en tubos) con propiedades del aire y del agua según la temperatura, radiación y emisividades, coeficiente global U, intercambiadores por LMTD con factor F y por ε-NTU, aletas, pérdidas de calor de hornos, secaderos, tanques y cañerías, y espesor de aislación por temperatura de superficie segura o pérdida admitida. Usar cuando se pregunte cuánto calor pierde la pared de un secador, un horno, un tanque o una cañería, qué espesor de lana de vidrio o de lana de roca hace falta, cómo aislar una cañería de vapor, el coeficiente de convección del aire o del agua, las pérdidas por radiación de un horno, o haya que calcular un intercambiador de calor o una aleta."
---

# Transferencia de calor

Las pérdidas de un horno, un secadero, un tanque o una cañería salen de un circuito de resistencias térmicas: películas de convección, capas que conducen y radiación en la superficie. Como los coeficientes de película dependen de las temperaturas de superficie, que no se conocen, el cálculo es iterativo. `scripts/calor.py` (Python 3.9+, solo biblioteca estándar) hace la iteración y escribe cada paso con coma decimal, listo para la memoria de cálculo (presentación en **calculos-ingenieria**; el informe, en **informe-tecnico**). El aire húmedo y el balance de un secadero están en **secado-y-psicrometria**: las pérdidas por paredes que salen de acá se suman a la potencia del calentador que da esa skill.

Bibliografía de base: Incropera, DeWitt, Bergman y Lavine, *Fundamentals of Heat and Mass Transfer*, 6.ª ed. (Wiley; caps. 1, 3, 7, 8, 9 y 11) y Çengel, *Transferencia de calor y masa* (McGraw-Hill; caps. 8 y 9). Los números de ecuación cambian entre ediciones (verificar la edición que se use).

| Leer | Cuándo |
|---|---|
| [references/propiedades.md](references/propiedades.md) | Para citar o interpolar a mano las propiedades del aire (−20 a 600 °C) y del agua (5 a 200 °C) |
| [references/materiales.md](references/materiales.md) | Para elegir k de un material o de un aislante según la temperatura, la emisividad o la temperatura de superficie segura |
| [references/correlaciones.md](references/correlaciones.md) | Para el detalle de cada correlación, sus rangos, las relaciones ε-NTU y la lista de ejemplos publicados que controla el demo |

## Método para las pérdidas de un equipo

1. **Esquema:** fluido interior (temperatura Ti), capas de adentro hacia afuera (material, espesor e, conductividad k), superficie exterior (emisividad ε), aire exterior (Te) y alrededores (Tsur, en un galpón cerrado ≈ Te).
2. **Geometría de cada cara:** paredes verticales (L = altura), techo y piso (L = área/perímetro), caños horizontales (L = diámetro exterior). Cada cara se calcula aparte y las pérdidas se suman.
3. **Suponer las temperaturas de superficie** y con ellas calcular hi, hc y hr (propiedades a la temperatura de película).
4. **Circuito:** resistencias en serie desde el fluido interior hasta la superficie exterior; afuera, convección y radiación en paralelo.
5. **Calor y nuevas temperaturas:** q = (Ti − Te)/R_total; Ts = Ti − q·R hasta la superficie. Volver a 3 hasta que Ts no cambie (el script lo hace en 20 a 30 vueltas).
6. **k a la temperatura media de cada capa:** la de un aislante sube mucho con la temperatura; con la tabla del fabricante, el script la toma sola.
7. **Controles:** el calor que sale por la superficie, hc·(Ts − Te) + hr·(Ts − Tsur), tiene que ser igual al que atraviesa la pared; y cada correlación, dentro de su rango (el script avisa).

## Conducción y resistencias

| Elemento | Resistencia | Unidad |
|---|---|---|
| Capa plana | R'' = e/k | m²·K/W |
| Capa cilíndrica entre r1 y r2 | R' = ln(r2/r1)/(2π·k) | m·K/W (por metro de caño) |
| Película de convección o radiación | R'' = 1/h; en un caño, R' = 1/(h·2π·r) | m²·K/W o m·K/W |
| En serie | R = R1 + R2 + …; q = ΔT/R | |
| En paralelo (caminos lado a lado) | 1/R = 1/R1 + 1/R2 + …; un puente térmico en una capa: k_eq = (1 − f)·k + f·k_puente | |
| Coeficiente global | U = 1/R''_total; en caños, U referido al área exterior: U = q'/(2π·r_ext·ΔT) | W/(m²·K) |

**Radio crítico:** en un caño, la aislación agrega resistencia de conducción pero también área exterior. La pérdida es máxima con r_cr = k/h (esfera: 2k/h). Si el radio exterior del caño desnudo es menor que r_cr (cables y caños finos con aislantes de k alta), agregar un poco de aislación aumenta la pérdida. Con lana y h ≈ 5 W/(m²·K), r_cr ≈ 10 mm: en caños de vapor nunca molesta. El script lo informa en `cilindro`.

Conductividades de cálculo (`calor.py materiales` muestra todas con su fuente):

| Material | k [W/(m·K)] | Fuente |
|---|---|---|
| Acero / acero inoxidable | 58 / 17 | Municipalidad de Rosario (valores tipo IRAM 11601; verificar en la norma vigente) |
| Ladrillo macizo 1600 / 1800 / 2000 kg/m³ | 0,81 / 0,91 / 1,10 | ídem |
| Hormigón de piedra 2400 kg/m³ / armado | 1,63 / 2,30 | ídem; 1,63 coincide con IRAM 11601 citada por UTN FRC |
| Lana de vidrio en fieltro 15 a 18 kg/m³ (edificios) | 0,040 | ídem |
| Panel de lana de vidrio ISOVER TECH Slab 3.0 | 0,034 a 10 °C · 0,038 a 50 °C · 0,047 a 100 °C · 0,070 a 200 °C | ficha técnica (EN 12667), hasta 300 °C |
| Coquilla de lana de roca ROCKWOOL ProRox PS 960 | 0,040 a 50 °C · 0,046 a 100 °C · 0,064 a 200 °C · 0,092 a 300 °C | ficha técnica (EN ISO 8497), hasta 650 °C |
| Poliuretano rígido 30 a 60 kg/m³ (placas) | 0,027 | Municipalidad de Rosario (verificar en la norma vigente) |
| Aire quieto a 20 °C | 0,0251 | Çengel, tabla del aire; solo en capas muy delgadas: en una cámara de aire hay convección y radiación |

## Convección

Propiedades a la temperatura de película T_f = (Ts + T∞)/2 en convección exterior y a la temperatura media del fluido en tubos. `calor.py propiedades --fluido aire --t 50` interpola la tabla del aire (Çengel) o del agua (NIST, IAPWS). En gases β = 1/T_f, con T_f en K.

**Natural:** Ra = g·β·(Ts − T∞)·L³·Pr/ν², con g = 9,81 m/s²; h = Nu·k/L.

| Superficie | Correlación (Incropera, cap. 9; Çengel, cap. 9) | Rango |
|---|---|---|
| Placa o pared vertical, L = altura | Nu = {0,825 + 0,387·Ra^(1/6)/[1 + (0,492/Pr)^(9/16)]^(8/27)}² (Churchill y Chu) | toda la gama de Ra |
| Cilindro horizontal, L = D | Nu = {0,60 + 0,387·Ra^(1/6)/[1 + (0,559/Pr)^(9/16)]^(8/27)}² (Churchill y Chu) | Ra ≤ 10¹² |
| Cara caliente hacia arriba (techo de un horno), L = A/P | Nu = 0,54·Ra^¼ / Nu = 0,15·Ra^⅓ | 10⁴ a 10⁷ / 10⁷ a 10¹¹ |
| Cara caliente hacia abajo (fondo de un tanque elevado) | Nu = 0,27·Ra^¼ | 10⁵ a 10¹⁰ |

**Forzada sobre una placa plana** (viento sobre una pared, aire dentro de un secadero), Re_L = v·L/ν con L en el sentido del flujo: laminar si Re_L ≤ 5·10⁵, Nu = 0,664·Re^½·Pr^⅓ (Pr ≥ 0,6); si no, capa mixta con transición en 5·10⁵: Nu = (0,037·Re^0,8 − 871)·Pr^⅓ (hasta Re = 10⁸, 0,6 ≤ Pr ≤ 60).

**Forzada dentro de un tubo**, Re = v·D/ν = 4ṁ/(π·D·μ):

| Régimen | Correlación | Rango |
|---|---|---|
| Laminar desarrollado (Re < 2300) | Nu = 3,66 (pared isoterma) o 4,36 (flujo de calor uniforme) | región de entrada: ver references |
| Turbulento, recomendada | Gnielinski: Nu = (f/8)·(Re − 1000)·Pr/[1 + 12,7·(f/8)^½·(Pr^⅔ − 1)], con f = (0,790·ln Re − 1,64)⁻² (Petukhov) | 3000 ≤ Re ≤ 5·10⁶; 0,5 ≤ Pr ≤ 2000 |
| Turbulento, clásica | Dittus-Boelter: Nu = 0,023·Re^0,8·Pr^n, n = 0,4 si se calienta el fluido y 0,3 si se enfría | Re ≥ 10 000; 0,7 ≤ Pr ≤ 160; L/D ≥ 10 |

Con la pared a temperatura uniforme, la salida del fluido es (Ts − T_sal)/(Ts − T_ent) = exp(−h·As/(ṁ·cp)), con As = π·D·L.

```
python calor.py conveccion --caso vertical --ts 60 --tinf 20 --L 2             # pared de 2 m de alto
python calor.py conveccion --caso tubo --fluido agua --D 0.03 --tinf 40 --v 0.236 --ts 100
```

## Radiación

q'' = ε·σ·(Ts⁴ − Tsur⁴), con σ = 5,670374419·10⁻⁸ W/(m²·K⁴) y temperaturas en K, para una superficie que ve alrededores grandes. Para sumarla a la convección se linealiza: h_r = ε·σ·(Ts + Tsur)·(Ts² + Tsur²) y q'' = h_r·(Ts − Tsur) (exacto con las temperaturas de la iteración). Un horno con la chapa a 300 °C y ε = 0,9 en un galpón a 25 °C irradia 5,10 kW/m² (h_r = 18,6 W/(m²·K)): `calor.py radiacion --ts 300 --tsur 25 --eps 0.9`.

| Superficie | ε | Fuente |
|---|---|---|
| Chapa de aluminio comercial / pulida | 0,1 / 0,04 | NIA, *Mechanical Insulation Design Guide* (datos de ASHRAE) |
| Acero galvanizado nuevo y brillante / opaco | 0,1 / 0,3 | ídem |
| Acero inoxidable nuevo | 0,2 | ídem |
| Metal pintado / hierro o acero | 0,8 | ídem |
| Acero oxidado / chapa laminada | 0,79 / 0,6 | CIBSE Guide C, tabla C3.7 |
| Ladrillo / pintura | 0,93 / 0,95 | ídem |

## Coeficiente global e intercambiadores

**Balance:** q = Ch·(Th,e − Th,s) = Cc·(Tc,s − Tc,e), con C = ṁ·cp en W/K. **U** sale del circuito: 1/(U·A) = 1/(hi·Ai) + R_pared + R_ensuciamiento + 1/(he·Ae), con cada h de la correlación de su lado.

**LMTD** (para dimensionar, con las cuatro temperaturas): ΔTml = (ΔT1 − ΔT2)/ln(ΔT1/ΔT2); en contracorriente ΔT1 = Th,e − Tc,s y ΔT2 = Th,s − Tc,e; en paralelo, entre las entradas y entre las salidas. A = q/(U·F·ΔTml), con F = 1 en tubos concéntricos. Para carcasa y tubos con 1 paso de carcasa y 2, 4… pasos de tubos, F sale de P = (t_s − t_e)/(T_e − t_e) y R = (T_e − T_s)/(t_s − t_e) (t, fluido de los tubos), con la fórmula de [references/correlaciones.md](references/correlaciones.md); si no hay solución, hacen falta más pasos de carcasa.

**ε-NTU** (para verificar un equipo existente, sin las salidas): NTU = U·A/Cmin, Cr = Cmin/Cmax, q = ε·Cmin·(Th,e − Tc,e).

| Tipo | ε |
|---|---|
| Contracorriente | [1 − e^(−NTU·(1 − Cr))]/[1 − Cr·e^(−NTU·(1 − Cr))]; con Cr = 1, NTU/(1 + NTU) |
| Paralelo | [1 − e^(−NTU·(1 + Cr))]/(1 + Cr) |
| Condensador o evaporador (Cr = 0), cualquier tipo | 1 − e^(−NTU) |
| Carcasa 1 paso, tubos 2, 4… | fórmula en [references/correlaciones.md](references/correlaciones.md) |

```
python calor.py intercambiador --tipo carcasa --thi 150 --tho 90 --tci 20 --tco 60 --Ch 3000 --U 300   # dimensionar: F = 0,933, A = 8,08 m²
python calor.py intercambiador --tipo contracorriente --thi 100 --tci 30 --mh 0.1 --cph 2131 --mc 0.2 --cpc 4178 --U 38 --A 5.2
```

## Aletas

m = √(h·P/(k·Ac)): aleta recta de espesor t, m = √(2h/(k·t)) y longitud corregida Lc = L + t/2; aleta de aguja de diámetro D, m = √(4h/(k·D)) y Lc = L + D/4. Eficiencia η = tanh(m·Lc)/(m·Lc); calor q = η·h·Af·(Tb − T∞), con Af = 2·w·Lc en la recta. Conjunto: η_o = 1 − (N·Af/At)·(1 − η). Efectividad ε_a = q/(h·Ac·(Tb − T∞)): si es baja, la aleta no conviene. `calor.py aleta --k 200 --h 60 --L 60 --t 3 --tb 100 --tinf 20` → η = 0,8063 (Incropera, tablas 3.4 y 3.5).

## Ejemplo resuelto: pared de un secador a 80 °C (es el `demo`)

Cámara de secado de 3 m × 2 m en planta y 2 m de alto (20 m² de paredes), en un galpón cerrado a 20 °C (aire y paredes). Adentro, aire a 80 °C que circula a 3 m/s a lo largo de la pared (2 m en el sentido del flujo). Pared: chapa de acero de 1,25 mm, panel de lana de vidrio TECH Slab 3.0 de 50 mm y chapa de 0,8 mm pintada (ε = 0,8).

```
python calor.py pared --ti 80 --te 20 --capa acero:1.25 --capa lana-vidrio-panel:50 --capa acero:0.8 --interior forzada:3:2 --exterior vertical:2 --eps 0.8 --area 20
```

| Paso | Resultado |
|---|---|
| Película interior (placa plana, laminar, Re = 2,92·10⁵) | hi = 4,69 W/(m²·K); la chapa interior queda a 72,4 °C |
| Lana: temperatura media 48,7 °C | k = 0,0379 W/(m·K) (ficha); R'' = 0,050/0,0379 = 1,320 m²·K/W (79 % del total) |
| Exterior: placa vertical de 2 m (Ra = 4,12·10⁹) y radiación | hc = 2,43 y hr = 4,69 W/(m²·K): la radiación lleva el 66 % |
| Total | R'' = 1,674 m²·K/W; U = 0,597 W/(m²·K); q = 60/1,674 = 35,8 W/m² |
| Superficie exterior y pérdida | Ts = 25,0 °C; Q = 35,8·20 = 717 W |
| Sin lana (dos chapas) | q = 184,0 W/m², Ts = 40,9 °C, Q = 3679 W: la lana ahorra el 80 % |

**Espesor de aislación.** Si se admite una pérdida de 25 W/m²:

```
python calor.py aislacion --ti 80 --te 20 --capa acero:1.25 --capa lana-vidrio-panel:50 --capa acero:0.8 --interior forzada:3:2 --exterior vertical:2 --eps 0.8 --area 20 --aislante 2 --qmax 25 --espesores 0/25/40/50/80/100
```

El espesor mínimo es 77,4 mm. El panel viene de 40 y 50 mm, así que se adoptan dos capas de 40 mm: q = 24,3 W/m² y Q = 486 W. La temperatura exterior no limita: con 50 mm la chapa está a 25 °C.

### Caño de vapor (también en el `demo`)

Caño de acero de 2" (60,3 mm de diámetro exterior, NIA, tabla 2) con vapor a 150 °C (476 kPa absolutos según NIST), en una sala a 20 °C. La película de condensación y la pared del caño se desprecian frente a la aislación: la superficie del caño está a 150 °C. Coquilla de lana de roca ProRox PS 960 con chapa de aluminio (ε = 0,1).

```
python calor.py cilindro --ti 150 --te 20 --d 60.3 --capa lana-roca-coquilla:40 --eps 0.1 --largo 1
python calor.py aislacion --ti 150 --te 20 --d 60.3 --capa lana-roca-coquilla:40 --eps 0.1 --tmax 60 --espesores 10/20/30/40
```

- Desnudo (acero, ε = 0,8): 399 W por metro. Con 40 mm: k = 0,0453 a 94 °C de media, Ts = 37,9 °C y 37,8 W/m (90 % menos).
- Temperatura de contacto: ASTM C1055 toma 60 °C en superficies metálicas para 5 s de contacto (según NIA; verificar en la norma vigente). Alcanzan 14,2 mm; para no perder más de 50 W/m hacen falta 24,5 mm (`--qmax 50`). Manda el mayor; se adopta el espesor comercial siguiente del fabricante.
- Con chapa pintada (ε = 0,8) la superficie queda más fría (30,7 °C con 40 mm) y pierde un poco más (39,8 W/m): el aluminio brillante irradia poco y por eso se calienta más.

## Errores frecuentes

- Usar la k del aislante a 10 °C (valor de edificios) en un equipo caliente: a 200 °C la lana de roca conduce 60 % más que a 50 °C.
- Olvidar la radiación: en paredes a menos de 100 °C con pintura o chapa oxidada lleva la mitad o más de la pérdida exterior.
- Tomar h de "aire quieto" de una tabla en vez de calcularlo con la geometría y la temperatura, o evaluar las propiedades a Ti en vez de a la temperatura de película.
- Poner las temperaturas de la radiación en °C (van en K) o mezclar W/m² de pared con W/m de caño.
- Usar Dittus-Boelter fuera de su rango (Re menor que 10 000) o el Nu laminar en flujo turbulento.
- Despreciar los puentes térmicos: un perfil de chapa que une las dos caras, aunque ocupe 0,2 % del área, lleva la pérdida del ejemplo de 35,8 a 90,3 W/m² (`--puente 0.002:58`, estimación por caminos en paralelo).
- En carcasa y tubos, aplicar la LMTD de contracorriente sin el factor F, o seguir con un F muy bajo en vez de agregar pasos de carcasa.
- Adoptar un espesor menor que el calculado, o uno que no exista en el catálogo.

## Verificación

- `python calor.py demo` tiene que terminar en `DEMO OK` (33 controles): propiedades contra Çengel, NIST y CoolProp 8.0; correlaciones contra los ejemplos publicados de Çengel (7-1, 8-5, 8-6, 9-1, 9-2) e Incropera (3.5, 9.2, 9.4, 11.1), la aleta de Nellis y Klein (EES) y la tabla de caños desnudos de ASHRAE (diferencia de 2 %); identidades ε-NTU y LMTD; y los dos ejemplos de arriba.
- En cada cálculo: el balance de la superficie exterior cierra, la temperatura media de cada aislante cae dentro de su tabla y del máximo de servicio, y las correlaciones están en rango (si no, el script avisa).
- Las correlaciones son empíricas (Gnielinski y Dittus-Boelter difieren hasta 15 % donde valen las dos): se informa con 2 o 3 cifras y con margen en el espesor adoptado. Para una entrega, una revisión independiente con **revision-tecnica** o **equipo-de-modelos**.
