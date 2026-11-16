# Propiedades del aire y del agua

Leer para citar una propiedad en un informe o interpolar a mano. Son las mismas tablas que usa `scripts/calor.py` (comando `propiedades`), con interpolación lineal entre filas.

## Cómo se evalúan

- **Convección exterior** (natural o forzada): a la temperatura de película T_f = (Ts + T∞)/2.
- **Flujo en tubos:** a la temperatura media del fluido, (T_entrada + T_salida)/2; si la salida no se conoce, se supone, se calcula y se repite.
- **β en gases** (aire como gas ideal): β = 1/T_f, con T_f en K. En líquidos, de la tabla.
- **Presión:** cp, k, μ y Pr del aire casi no dependen de la presión; ρ y ν sí (ν ∝ 1/p). A 1000 m de altura (89,9 kPa) ν es casi 13 % mayor que a nivel del mar (presión según la altitud en **secado-y-psicrometria**).

## Aire a 1 atm

Fuente: Çengel, tabla «Propiedades del aire a 1 atm de presión» (tabla A-15 de *Transferencia de calor y masa*, de Çengel y Ghajar; tabla A-9 de *Mecánica de fluidos*, de Çengel y Cimbala), datos generados con EES (Klein y Alvarado) a partir de Keenan, Chao y Keyes, *Gas Tables* (1984), y Touloukian y otros, *Thermophysical Properties of Matter*, vol. 3 y 11 (1970). Copias consultadas: [Penn State (Cimbala)](https://www.me.psu.edu/cimbala/me405/Links/Table_A_9_CC_Properties_of_Air.pdf) y [Engineers Edge](https://engineersedge.com/physics/properties_of_air_at_1_atm_pressure_13828.htm); coinciden fila por fila.

| T [°C] | ρ [kg/m³] | cp [J/(kg·K)] | k [W/(m·K)] | μ [kg/(m·s)] | ν [m²/s] | Pr |
|---|---|---|---|---|---|---|
| −20 | 1,394 | 1005 | 0,02211 | 1,630·10⁻⁵ | 1,169·10⁻⁵ | 0,7408 |
| −10 | 1,341 | 1006 | 0,02288 | 1,680·10⁻⁵ | 1,252·10⁻⁵ | 0,7387 |
| 0 | 1,292 | 1006 | 0,02364 | 1,729·10⁻⁵ | 1,338·10⁻⁵ | 0,7362 |
| 10 | 1,246 | 1006 | 0,02439 | 1,778·10⁻⁵ | 1,426·10⁻⁵ | 0,7336 |
| 20 | 1,204 | 1007 | 0,02514 | 1,825·10⁻⁵ | 1,516·10⁻⁵ | 0,7309 |
| 30 | 1,164 | 1007 | 0,02588 | 1,872·10⁻⁵ | 1,608·10⁻⁵ | 0,7282 |
| 40 | 1,127 | 1007 | 0,02662 | 1,918·10⁻⁵ | 1,702·10⁻⁵ | 0,7255 |
| 50 | 1,092 | 1007 | 0,02735 | 1,963·10⁻⁵ | 1,798·10⁻⁵ | 0,7228 |
| 60 | 1,059 | 1007 | 0,02808 | 2,008·10⁻⁵ | 1,896·10⁻⁵ | 0,7202 |
| 70 | 1,028 | 1007 | 0,02881 | 2,052·10⁻⁵ | 1,995·10⁻⁵ | 0,7177 |
| 80 | 0,9994 | 1008 | 0,02953 | 2,096·10⁻⁵ | 2,097·10⁻⁵ | 0,7154 |
| 90 | 0,9718 | 1008 | 0,03024 | 2,139·10⁻⁵ | 2,201·10⁻⁵ | 0,7132 |
| 100 | 0,9458 | 1009 | 0,03095 | 2,181·10⁻⁵ | 2,306·10⁻⁵ | 0,7111 |
| 120 | 0,8977 | 1011 | 0,03235 | 2,264·10⁻⁵ | 2,522·10⁻⁵ | 0,7073 |
| 140 | 0,8542 | 1013 | 0,03374 | 2,345·10⁻⁵ | 2,745·10⁻⁵ | 0,7041 |
| 160 | 0,8148 | 1016 | 0,03511 | 2,420·10⁻⁵ | 2,975·10⁻⁵ | 0,7014 |
| 180 | 0,7788 | 1019 | 0,03646 | 2,504·10⁻⁵ | 3,212·10⁻⁵ | 0,6992 |
| 200 | 0,7459 | 1023 | 0,03779 | 2,577·10⁻⁵ | 3,455·10⁻⁵ | 0,6974 |
| 250 | 0,6746 | 1033 | 0,04104 | 2,760·10⁻⁵ | 4,091·10⁻⁵ | 0,6946 |
| 300 | 0,6158 | 1044 | 0,04418 | 2,934·10⁻⁵ | 4,765·10⁻⁵ | 0,6935 |
| 350 | 0,5664 | 1056 | 0,04721 | 3,101·10⁻⁵ | 5,475·10⁻⁵ | 0,6937 |
| 400 | 0,5243 | 1069 | 0,05015 | 3,261·10⁻⁵ | 6,219·10⁻⁵ | 0,6948 |
| 450 | 0,4880 | 1081 | 0,05298 | 3,415·10⁻⁵ | 6,997·10⁻⁵ | 0,6965 |
| 500 | 0,4565 | 1093 | 0,05572 | 3,563·10⁻⁵ | 7,806·10⁻⁵ | 0,6986 |
| 600 | 0,4042 | 1115 | 0,06093 | 3,846·10⁻⁵ | 9,515·10⁻⁵ | 0,7037 |

Controles hechos con código:
- Coherencia interna: ν = μ/ρ en todas las filas dentro de 0,17 % (la mayor diferencia, a 160 °C, ya está en las dos copias).
- Contra CoolProp 8.0 (correlaciones de Lemmon y Jacobsen, 2004): ρ y cp dentro de 0,3 %; k entre 3,1 % menos (a −20 °C) y 0,1 % menos (de 450 a 500 °C); μ entre 0,6 % más (a −20 °C) y 2,9 % menos (a 600 °C). Es la diferencia entre los datos de 1970 y los actuales: no cambia un cálculo de ingeniería, pero conviene saberla si se compara con otro programa. La tabla A.4 de Incropera usa otra fuente: a 350 K da k = 0,0300 W/(m·K) (dato del ejemplo 9.5 según el [compañero de FOSSEE](https://git.fossee.in/Scilab-TBC-Uploads/.git/plain/latex/book_534.pdf)) y esta tabla da 0,0293 a 76,85 °C.
- El ejemplo 9-1 de Çengel usa a 45 °C k = 0,02699, ν = 1,750·10⁻⁵ y Pr = 0,7241: la interpolación del script da lo mismo.

## Agua líquida saturada

Fuente: [NIST Chemistry WebBook, SRD 69](https://webbook.nist.gov/chemistry/fluid/) (Lemmon, McLinden y Friend), propiedades de saturación del agua: ecuación de estado IAPWS-95 (Wagner y Pruss, *J. Phys. Chem. Ref. Data* 31, 2002), viscosidad IAPWS 2008 (Huber y otros, 2009) y conductividad IAPWS 2011 (Huber y otros, 2012). β = −(1/ρ)·(∂ρ/∂T) a presión constante, de IAPWS-95 calculado con CoolProp 8.0. Pr = μ·cp/k. Por encima de 100 °C el agua está líquida a su presión de saturación (agua presurizada).

| T [°C] | p_sat [kPa] | ρ [kg/m³] | cp [J/(kg·K)] | μ [Pa·s] | k [W/(m·K)] | Pr | β [1/K] |
|---|---|---|---|---|---|---|---|
| 5 | 0,8726 | 999,92 | 4205,5 | 1,5183·10⁻³ | 0,56772 | 11,25 | 1,574·10⁻⁵ |
| 10 | 1,2282 | 999,65 | 4195,5 | 1,3060·10⁻³ | 0,57871 | 9,468 | 8,769·10⁻⁵ |
| 15 | 1,7058 | 999,06 | 4188,8 | 1,1376·10⁻³ | 0,58874 | 8,094 | 1,507·10⁻⁴ |
| 20 | 2,3393 | 998,16 | 4184,4 | 1,0016·10⁻³ | 0,59795 | 7,009 | 2,067·10⁻⁴ |
| 25 | 3,1699 | 997,00 | 4181,6 | 8,9004·10⁻⁴ | 0,60646 | 6,137 | 2,572·10⁻⁴ |
| 30 | 4,2470 | 995,61 | 4180,1 | 7,9722·10⁻⁴ | 0,61434 | 5,424 | 3,033·10⁻⁴ |
| 35 | 5,6290 | 993,99 | 4179,5 | 7,1912·10⁻⁴ | 0,62165 | 4,835 | 3,458·10⁻⁴ |
| 40 | 7,3849 | 992,18 | 4179,6 | 6,5272·10⁻⁴ | 0,62844 | 4,341 | 3,855·10⁻⁴ |
| 45 | 9,5950 | 990,17 | 4180,4 | 5,9575·10⁻⁴ | 0,63474 | 3,924 | 4,226·10⁻⁴ |
| 50 | 12,352 | 988,00 | 4181,5 | 5,4650·10⁻⁴ | 0,64057 | 3,567 | 4,578·10⁻⁴ |
| 55 | 15,762 | 985,66 | 4183,1 | 5,0361·10⁻⁴ | 0,64598 | 3,261 | 4,912·10⁻⁴ |
| 60 | 19,946 | 983,16 | 4185,1 | 4,6602·10⁻⁴ | 0,65096 | 2,996 | 5,233·10⁻⁴ |
| 65 | 25,042 | 980,52 | 4187,5 | 4,3288·10⁻⁴ | 0,65554 | 2,765 | 5,541·10⁻⁴ |
| 70 | 31,201 | 977,73 | 4190,2 | 4,0353·10⁻⁴ | 0,65972 | 2,563 | 5,840·10⁻⁴ |
| 75 | 38,595 | 974,81 | 4193,3 | 3,7740·10⁻⁴ | 0,66353 | 2,385 | 6,131·10⁻⁴ |
| 80 | 47,414 | 971,77 | 4196,9 | 3,5404·10⁻⁴ | 0,66697 | 2,228 | 6,414·10⁻⁴ |
| 85 | 57,867 | 968,59 | 4200,8 | 3,3306·10⁻⁴ | 0,67004 | 2,088 | 6,693·10⁻⁴ |
| 90 | 70,182 | 965,30 | 4205,3 | 3,1417·10⁻⁴ | 0,67277 | 1,964 | 6,967·10⁻⁴ |
| 95 | 84,608 | 961,88 | 4210,2 | 2,9708·10⁻⁴ | 0,67516 | 1,853 | 7,237·10⁻⁴ |
| 100 | 101,42 | 958,35 | 4215,7 | 2,8158·10⁻⁴ | 0,67721 | 1,753 | 7,506·10⁻⁴ |
| 110 | 143,38 | 950,95 | 4228,3 | 2,5461·10⁻⁴ | 0,68035 | 1,582 | 8,041·10⁻⁴ |
| 120 | 198,67 | 943,11 | 4243,5 | 2,3203·10⁻⁴ | 0,68224 | 1,443 | 8,578·10⁻⁴ |
| 130 | 270,28 | 934,83 | 4261,5 | 2,1294·10⁻⁴ | 0,68295 | 1,329 | 9,123·10⁻⁴ |
| 140 | 361,54 | 926,13 | 4282,6 | 1,9664·10⁻⁴ | 0,68253 | 1,234 | 9,684·10⁻⁴ |
| 150 | 476,16 | 917,01 | 4307,1 | 1,8261·10⁻⁴ | 0,68102 | 1,155 | 1,027·10⁻³ |
| 160 | 618,23 | 907,45 | 4335,4 | 1,7043·10⁻⁴ | 0,67873 | 1,089 | 1,088·10⁻³ |
| 170 | 792,19 | 897,45 | 4367,8 | 1,5977·10⁻⁴ | 0,67552 | 1,033 | 1,153·10⁻³ |
| 180 | 1002,8 | 887,00 | 4405,0 | 1,5038·10⁻⁴ | 0,67128 | 0,987 | 1,222·10⁻³ |
| 190 | 1255,2 | 876,08 | 4447,4 | 1,4204·10⁻⁴ | 0,66609 | 0,948 | 1,297·10⁻³ |
| 200 | 1554,9 | 864,66 | 4495,8 | 1,3458·10⁻⁴ | 0,66001 | 0,917 | 1,379·10⁻³ |

Controles hechos con código:
- Los valores de NIST coinciden con CoolProp 8.0 (mismas formulaciones) dentro de 0,004 %.
- Contra la tabla de agua saturada de Çengel (tabla A-3 de *Mecánica de fluidos*, [copia de Penn State](https://www.me.psu.edu/cimbala/me405/Links/Table_A_3_CC_Saturated_Water.pdf)): ρ dentro de 0,1 %, cp dentro de 0,15 %, μ dentro de 0,5 % y k hasta 1 % más alta en el libro (usa la conductividad de Sengers y Watson, 1986). En esa copia hay erratas: ρ = 921,7 a 140 °C (NIST: 926,13) y β = 0,733·10⁻³ a 10 °C (IAPWS-95: 0,0877·10⁻³). β a 20 °C es 0,195·10⁻³ en el libro y 0,207·10⁻³ en IAPWS-95: para convección natural en agua conviene esta tabla.
- El ejemplo 8-5 de Çengel usa a 40 °C ρ = 992,1, cp = 4179, k = 0,631 y Pr = 4,32; esta tabla da 992,18, 4180, 0,6284 y 4,341.
