# Correlaciones, relaciones de intercambiadores y ejemplos publicados

Leer para elegir una correlación fuera de los casos del SKILL.md, citar su rango o revisar contra qué ejemplos publicados se controló el script. Números de ecuación: Incropera y otros, *Fundamentals of Heat and Mass Transfer*, 6.ª ed. (tal como los listan las [tablas del curso ME 340 de BYU](https://www.et.byu.edu/~vps/ME340/TABLES/9.2.pdf)), y Çengel, *Transferencia de calor y masa*, en castellano (extractos publicados por la Universidad de Guanajuato: [cap. 8](https://blogs.ugto.mx/wp-content/uploads/sites/71/2022/01/Desarrollo-del-flujo-laminar-en-la-region-de-entrada-paginas-470-a-491.pdf) y [cap. 9](https://blogs.ugto.mx/wp-content/uploads/sites/71/2022/01/Conveccion-natural-paginas-503-a-544.pdf); la edición no figura en el extracto: verificar la edición).

## Convección natural

Ra_L = g·β·(Ts − T∞)·L³/(ν·α) = Gr_L·Pr, propiedades a T_f = (Ts + T∞)/2.

| Caso | Correlación | Rango | Ecuación |
|---|---|---|---|
| Placa vertical | Nu = {0,825 + 0,387·Ra^(1/6)/[1 + (0,492/Pr)^(9/16)]^(8/27)}² | toda la gama | Incropera 9.26; Çengel 9-21 |
| Placa vertical, laminar (algo más precisa) | Nu = 0,68 + 0,670·Ra^¼/[1 + (0,492/Pr)^(9/16)]^(4/9) | Ra ≤ 10⁹ | Incropera 9.27 |
| Placa vertical, leyes simples | Nu = 0,59·Ra^¼ / Nu = 0,1·Ra^⅓ | 10⁴ a 10⁹ / 10⁹ a 10¹³ | Çengel 9-19 y 9-20 (en el ejemplo 9-2 dan 13 % menos que Churchill y Chu) |
| Placa inclinada hasta 60° de la vertical | la vertical con g·cos θ | θ ≤ 60° | tabla de BYU (Incropera, cap. 9) |
| Cilindro vertical | como placa vertical si D ≥ 35·L/Gr_L^¼ | | tabla de BYU (Incropera, cap. 9) |
| Placa horizontal, cara caliente arriba o fría abajo, L = A/P | Nu = 0,54·Ra^¼ / Nu = 0,15·Ra^⅓ | 10⁴ a 10⁷ / 10⁷ a 10¹¹ | Incropera 9.30 y 9.31; Çengel 9-22 y 9-23 |
| Placa horizontal, cara caliente abajo o fría arriba | Nu = 0,27·Ra^¼ | 10⁵ a 10¹⁰ (Çengel: hasta 10¹¹) | Incropera 9.32; Çengel 9-24 |
| Cilindro horizontal | Nu = {0,60 + 0,387·Ra^(1/6)/[1 + (0,559/Pr)^(9/16)]^(8/27)}² | Ra ≤ 10¹² | Incropera 9.34 |
| Cilindro horizontal, ley potencial Nu = C·Ra^n | C y n: 0,675 y 0,058 (10⁻¹⁰ a 10⁻²); 1,02 y 0,148 (10⁻² a 10²); 0,850 y 0,188 (10² a 10⁴); 0,480 y 0,250 (10⁴ a 10⁷); 0,125 y 0,333 (10⁷ a 10¹²) | | Incropera 9.33 |
| Esfera | Nu = 2 + 0,589·Ra^¼/[1 + (0,469/Pr)^(9/16)]^(4/9) | Pr ≥ 0,7; Ra ≤ 10¹¹ | Incropera 9.35 |

## Convección forzada sobre una placa plana

Re_x = v·x/ν; propiedades a T_f ([tabla de BYU](https://www.et.byu.edu/~vps/ME340/TABLES/7.1.pdf); Incropera, cap. 7).

| Caso | Correlación | Rango |
|---|---|---|
| Laminar, local | Nu_x = 0,332·Re_x^½·Pr^⅓ | Pr ≥ 0,6 |
| Laminar, medio | Nu_L = 0,664·Re_L^½·Pr^⅓ | Re_L ≤ 5·10⁵, Pr ≥ 0,6 |
| Turbulento, local | Nu_x = 0,0296·Re_x^0,8·Pr^⅓ | 0,6 ≤ Pr ≤ 60 |
| Capa mixta, medio | Nu_L = (0,037·Re_L^0,8 − A)·Pr^⅓, con A = 0,037·Re_x,c^0,8 − 0,664·Re_x,c^½ = 871 para Re_x,c = 5·10⁵ (871,3 calculado) | 5·10⁵ ≤ Re_L ≤ 10⁸; 0,6 ≤ Pr ≤ 60 |
| Flujo de calor uniforme, local | Nu_x = 0,453·Re_x^½·Pr^⅓ (laminar) y 0,0308·Re_x^0,8·Pr^⅓ (turbulento) | |

El cilindro en flujo cruzado (viento sobre una cañería; correlación de Churchill y Bernstein, Incropera cap. 7) no está en el script: se da --ho con un valor calculado aparte.

## Flujo dentro de tubos

[Tablas de BYU](https://www.et.byu.edu/~vps/ME340/TABLES/8.5.pdf) e Incropera cap. 8; Çengel cap. 8. Propiedades a la temperatura media del fluido. Diámetro hidráulico de conductos no circulares: D_h = 4·A/P (A, sección; P, perímetro mojado).

| Caso | Correlación | Rango |
|---|---|---|
| Laminar, longitud de entrada | x_h ≈ 0,05·Re·D; x_t ≈ x_h·Pr; en turbulento ≈ 10·D | |
| Laminar desarrollado | Nu = 3,66 (pared isoterma) y 4,36 (flujo de calor uniforme) | Re < 2300 |
| Laminar, entrada térmica (Hausen), pared isoterma | Nu = 3,66 + 0,0668·(D/L)·Re·Pr/[1 + 0,04·((D/L)·Re·Pr)^⅔] | [tabla de BYU](https://www.et.byu.edu/~vps/ME340/TABLES/8.4.pdf) (verificar la edición) |
| Laminar, entrada combinada (Sieder y Tate) | Nu = 1,86·(Re·Pr·D/L)^⅓·(μ/μs)^0,14 | 0,48 < Pr < 16 700; 0,0044 < μ/μs < 9,75 |
| Factor de fricción de tubo liso (Petukhov) | f = (0,790·ln Re − 1,64)⁻² | 3000 ≤ Re ≤ 5·10⁶ (Incropera 8.21; Çengel 8-65) |
| Turbulento, Gnielinski | Nu = (f/8)·(Re − 1000)·Pr/[1 + 12,7·(f/8)^½·(Pr^⅔ − 1)] | 3000 ≤ Re ≤ 5·10⁶; 0,5 ≤ Pr ≤ 2000 (Incropera 8.62; Çengel 8-71, que la recomienda) |
| Turbulento, Dittus y Boelter | Nu = 0,023·Re^0,8·Pr^n; n = 0,4 si se calienta el fluido y 0,3 si se enfría | Re ≥ 10 000; 0,7 ≤ Pr ≤ 160 (Incropera 8.60; Çengel 8-68) |
| Turbulento con mucha variación de propiedades (Sieder y Tate) | Nu = 0,027·Re^0,8·Pr^⅓·(μ/μs)^0,14 | Re ≥ 10 000; 0,7 ≤ Pr ≤ 16 700 (Incropera 8.61) |
| Salida con pared isoterma | (Ts − T_sal)/(Ts − T_ent) = exp(−h·As/(ṁ·cp)), As = P·L | Çengel, ejemplo 8-6 |

## Radiación

- σ = 2π⁵·k_B⁴/(15·h³·c²) = 5,670374419·10⁻⁸ W/(m²·K⁴), con las constantes exactas del SI de 2019 (el script la calcula así).
- q'' = ε·σ·(Ts⁴ − Tsur⁴) vale para una superficie que intercambia con alrededores mucho más grandes (o negros). Entre superficies que se ven entre sí (interior de un horno, pantallas de radiación) hacen falta factores de forma: Incropera, cap. 13 (no incluido).
- h_r = ε·σ·(Ts + Tsur)·(Ts² + Tsur²) (Incropera, cap. 1) es una factorización exacta de q'' con las temperaturas de la iteración.

## Intercambiadores

Relaciones de efectividad: tablas 10-3 y 10-4 del [apunte de la Universidad Al-Mustaqbal](https://uomus.edu.iq/img/lectures21/MUCLecture_2022_4207934.pdf), con la numeración de Holman, *Heat Transfer* (verificar la edición); las mismas relaciones están en Incropera, cap. 11. N = NTU = U·A/Cmin, C = Cr = Cmin/Cmax.

| Tipo | ε(N, C) | N(ε, C) |
|---|---|---|
| Paralelo | [1 − e^(−N·(1 + C))]/(1 + C) | −ln[1 − ε·(1 + C)]/(1 + C) |
| Contracorriente, C menor que 1 | [1 − e^(−N·(1 − C))]/[1 − C·e^(−N·(1 − C))] | ln[(ε − 1)/(ε·C − 1)]/(C − 1) |
| Contracorriente, C = 1 | N/(N + 1) | ε/(1 − ε) |
| Carcasa con 1 paso y 2, 4… pasos de tubos | 2·{1 + C + (1 + C²)^½·[1 + e^(−N·(1 + C²)^½)]/[1 − e^(−N·(1 + C²)^½)]}⁻¹ | −(1 + C²)^(−½)·ln[(2/ε − 1 − C − (1 + C²)^½)/(2/ε − 1 − C + (1 + C²)^½)] |
| Cualquiera con C = 0 (condensador, evaporador) | 1 − e^(−N) | −ln(1 − ε) |

Factor F de un paso de carcasa y 2, 4… pasos de tubos, con P = (t_s − t_e)/(T_e − t_e) y R = (T_e − T_s)/(t_s − t_e) (t, fluido de los tubos; T, de la carcasa):

F = [√(R² + 1)/(R − 1)]·ln[(1 − P)/(1 − P·R)] / ln{[2 − P·(R + 1 − √(R² + 1))]/[2 − P·(R + 1 + √(R² + 1))]}

y con R = 1: F = [P·√2/(1 − P)] / ln{[2 − P·(2 − √2)]/[2 − P·(2 + √2)]}. Solo hay solución si P es menor que 2/(R + 1 + √(R² + 1)) (0,586 con R = 1); si no, hacen falta más pasos de carcasa. Es la misma relación que ε-NTU: F = N_contracorriente(ε, C)/N_carcasa(ε, C), con ε = P y C = R si R ≤ 1, o ε = P·R y C = 1/R si R es mayor que 1. El demo lo comprueba (diferencia de 10⁻¹⁵) y da F = 0,8023 con P = 0,5 y R = 1.

Ensuciamiento: 1/U = 1/hi + R_f,i + R_pared + R_f,e + 1/he (referidas a la misma área). Los valores de R_f están en las tablas de TEMA o de los libros (no consultadas: verificar en la bibliografía).

## Aletas de sección constante

M = √(h·P·k·Ac)·θ_b, m = √(h·P/(k·Ac)), θ_b = Tb − T∞ (Incropera, tablas 3.4 y 3.5; [tabla de BYU](https://www.et.byu.edu/~vps/ME340/TABLES/3.6.3.pdf)).

| Extremo | Calor de la aleta |
|---|---|
| Con convección (exacto) | q = M·[senh(m·L) + (h/(m·k))·cosh(m·L)]/[cosh(m·L) + (h/(m·k))·senh(m·L)] |
| Adiabático | q = M·tanh(m·L) |
| Aleta infinita | q = M |
| Longitud corregida (aproximación de uso habitual) | adiabático con Lc = L + Ac/P: recta, Lc ≈ L + t/2; aguja, L + D/4 |

Eficiencia η = q/(h·Af·θ_b) = tanh(m·Lc)/(m·Lc); conjunto de N aletas: η_o = 1 − (N·Af/At)·(1 − η), con At = N·Af + A_base. Para la aleta del SKILL.md la longitud corregida da 0,24 % menos que el extremo convectivo exacto (las fórmulas del extremo, de Incropera tabla 3.4: verificar la edición).

## Radio crítico de aislación

r_cr = k/h en cilindros y 2·k/h en esferas, con h el coeficiente exterior (convección más radiación). Incropera, 6.ª ed., ejemplo 3.5: vidrio celular con k = 0,055 W/(m·K) y h = 5 W/(m²·K) → r_cr = 11 mm.

## Ejemplos publicados que reproduce el demo

| Ejemplo | Libro | Script | Fuente consultada |
|---|---|---|---|
| Çengel 9-1: caño horizontal D = 0,08 m y 6 m a 70 °C, sala a 20 °C | Ra = 1,867·10⁶; Nu = 17,39; h = 5,867; Q = 442 W; radiación con ε = 1: 553 W | 1,867·10⁶; 17,39; 5,868; 442; 554 | [ugto, cap. 9](https://blogs.ugto.mx/wp-content/uploads/sites/71/2022/01/Conveccion-natural-paginas-503-a-544.pdf) |
| Çengel 9-2: placa de 0,6 × 0,6 m a 90 °C, aire a 30 °C | vertical: Ra = 7,649·10⁸, Nu = 113,3, h = 5,302; horizontal (L = 0,15 m): Nu = 31,75 arriba y 15,87 abajo | 7,649·10⁸; 113,3; 5,305; 31,75; 15,88 | ídem. El libro usa 0,54·Ra^¼ con Ra = 1,195·10⁷, apenas fuera del rango; con 0,15·Ra^⅓ daría 34,3 |
| Çengel 7-1: aceite a 60 °C sobre placa de 5 m a 20 °C, 2 m/s | Re = 4,13·10⁴; h = 55,2; Q = 11 040 W | 41 322; 55,24; 11 049 | [apunte de Waterloo, ECE 309](https://www.mhtlab.uwaterloo.ca/courses/ece309_mechatronics/lectures/pdffiles/chapter6.pdf) |
| Çengel 8-5: agua de 15 a 65 °C, D = 3 cm, 5 m, 10 l/min | Re = 10 760; Nu = 69,4; h = 1460; Ts a la salida 115 °C | 10 750; 69,4; 1459; 115,3 | [ugto, cap. 8](https://blogs.ugto.mx/wp-content/uploads/sites/71/2022/01/Desarrollo-del-flujo-laminar-en-la-region-de-entrada-paginas-470-a-491.pdf) |
| Çengel 8-6: ducto de 0,2 × 0,2 m y 8 m, aire a 80 °C y 0,15 m³/s, pared a 60 °C | Re = 35 765; Nu = 91,4; h = 13,5; salida 71,3 °C | 35 765; 91,4; 13,49; 71,4 | ídem |
| Solucionario de Çengel, problemas 14-82 y 14-45 | Nu = 35,15 (placa vertical) y 374,1 (cilindro) | 35,14; 374,1 | [Waterloo, ECE 309](https://www.mhtlab.uwaterloo.ca/courses/ece309/assignments/pdffiles/cengel/all14.pdf) |
| Incropera 9.2: pantalla de 0,71 × 1,02 m a 232 °C, sala a 23 °C | q = 1060 W | 1060 W | datos: [FOSSEE](https://git.fossee.in/Scilab-TBC-Uploads/.git/plain/latex/book_534.pdf); resultado: [All About Thermofluids (Sheffield)](https://sites.google.com/a/sheffield.ac.uk/all-about-thermofluids/free-convection/14-revision-questions) |
| Incropera 9.4: caño de 0,1 m a 165 °C, sala a 23 °C, ε = 0,85 | Ra = 5,073·10⁶; Nu = 23,3; h = 7,29; q' = 325 + 441 = 766 W/m | 5,071·10⁶; 23,09; 7,23; 322 + 441 = 763 W/m | [apunte de SNU](https://ocw.snu.ac.kr/sites/default/files/NOTE/2251.pdf) y FOSSEE. El Nu del libro queda 0,9 % arriba de lo que da su propia fórmula; el total difiere 0,4 % |
| Incropera 3.5 | r_cr = 11 mm | 11,0 mm | FOSSEE |
| Incropera 3.1 (4.ª ed.): ventana de horno de dos plásticos, Ts ≤ 50 °C | (resultado por despeje directo: L = 62,7 mm) | 62,71 mm | datos: [Waterloo, ME 353](https://www.mhtlab.uwaterloo.ca/courses_old/me353/maple/examples/ex3p11.html) |
| Incropera 11.1: enfriador de aceite en contracorriente | q = 8524 W; Tc,s = 40,2 °C; ΔTml = 43,2 K | 8524; 40,2; 43,2 | datos: FOSSEE; resultados: reproducción de terceros en [SlideShare](https://www.slideshare.net/slideshow/heat-transfer-heat-exchanger-chapter6-ppt/273968727) (verificar con el libro) |
| Aleta recta: L = 60 mm, t = 3 mm, h = 60, k = 200 | η = 0,8063 | 0,8063 | [biblioteca de EES, Nellis y Klein](https://fchartsoftware.com/ees/heat_transfer_library/fin_efficiency/hs100.htm) |
| Caño de acero desnudo de 2" en aire quieto a 26,7 °C (80 °F), a 82, 138, 193, 249 y 304 °C | 141, 350, 623, 974 y 1420 Btu/(h·ft) = 135,6; 336,5; 599,0; 936,5; 1365,4 W/m | con ε = 0,8: 133,2; 329,3; 587,3; 919,2; 1340,4 W/m (1,8 a 2,2 % menos) | [NIA, Design Data, tabla 6](https://insulation.org/training-tools/designguide/design-data/) (datos de ASHRAE; la tabla no dice qué ε usa) |
