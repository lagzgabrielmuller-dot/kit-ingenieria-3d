# Cilindros: tablas y criterios de cálculo

Leer este archivo al dimensionar un cilindro, elegir el diámetro o verificar el pandeo. Las fórmulas están en el SKILL.md y el script `scripts/neumatica.py` hace las cuentas.

## Diámetros, vástagos y fuerzas a 6 bar

Fuerzas teóricas (η = 1) a 6 bar manométricos y aire libre consumido por un ciclo completo de doble efecto (avance y retroceso) por cada 100 mm de carrera, con p_atm = 1,013 bar. Calculado con `python scripts/neumatica.py tabla --p 6`.

| D [mm] | d [mm] | A_e [cm²] | A_r [cm²] | F_av a 6 bar [N] | F_ret a 6 bar [N] | Aire libre por ciclo cada 100 mm [l] |
|---|---|---|---|---|---|---|
| 8 | 4 | 0,50 | 0,38 | 30 | 23 | 0,061 |
| 10 | 4 | 0,79 | 0,66 | 47 | 40 | 0,100 |
| 12 | 6 | 1,13 | 0,85 | 68 | 51 | 0,137 |
| 16 | 6 | 2,01 | 1,73 | 121 | 104 | 0,259 |
| 20 | 8 | 3,14 | 2,64 | 188 | 158 | 0,400 |
| 25 | 10 | 4,91 | 4,12 | 295 | 247 | 0,625 |
| 32 | 12 | 8,04 | 6,91 | 483 | 415 | 1,035 |
| 40 | 16 | 12,57 | 10,56 | 754 | 633 | 1,601 |
| 50 | 20 | 19,63 | 16,49 | 1.178 | 990 | 2,501 |
| 63 | 20 | 31,17 | 28,03 | 1.870 | 1.682 | 4,099 |
| 80 | 25 | 50,27 | 45,36 | 3.016 | 2.721 | 6,620 |
| 100 | 25 | 78,54 | 73,63 | 4.712 | 4.418 | 10,535 |
| 125 | 32 | 122,72 | 114,68 | 7.363 | 6.881 | 16,435 |

Fuentes y alcance:
- 8 a 25 mm: cilindros ISO 6432 ([iso.org](https://www.iso.org/standard/64054.html)). 32 a 320 mm: cilindros ISO 15552 ([iso.org](https://www.iso.org/standard/66921.html)). La serie de diámetros y vástagos es la de ISO 3320 ([iso.org](https://www.iso.org/standard/61647.html)).
- Los vástagos de la tabla reproducen las fuerzas a 6 bar que publica Festo para DSNU, ISO 6432 ([catálogo](https://ftp.festo.com/public/PNEUMATIC/SOFTWARE_SERVICE/Documentation/2026/ES/DSNU_ES.PDF)) y DSBC, ISO 15552 ([catálogo](https://ftp.festo.com/public/PNEUMATIC/SOFTWARE_SERVICE/Documentation/2013/ES/DSBC_ES.PDF)). Festo da 189 N para Ø20 (el cálculo da 188,5 N).
- Para 160 a 320 mm, y para cualquier modelo concreto, tomar el vástago, la carrera máxima y las fuerzas del catálogo del fabricante.

## Rendimiento o factor de carga

La fuerza teórica no descuenta el rozamiento de juntas y guías ni la presión que hace falta para acelerar la carga. SMC lo resuelve con un factor de carga η ([datos técnicos SMC](https://ca01.smcworld.com/catalog/BEST-technical-data-en/pdf/6-2-1-m21-43-tech_en.pdf)):

| Uso | η máximo |
|---|---|
| Trabajo estático (sujetar, prensar) | 0,7 |
| Trabajo dinámico (mover una carga) | 0,5 (menos si es a alta velocidad) |
| Carga horizontal sobre guía | 1 |

SMC también recomienda ajustar el regulador al 85 % de la presión de la red, de modo que la presión de cálculo tiene que ser la del regulador, no la del compresor. Si la consigna o la cátedra dan un rendimiento (por ejemplo, 0,9 por rozamiento), se usa ese y se aclara.

## Elección del diámetro

1. Fuerza útil pedida F (con la carga, el rozamiento externo y, si sube en vertical, el peso).
2. D mín = √(4 · F / (π · p · η)), con p en N/mm² y D en mm.
3. Adoptar el diámetro normalizado inmediato superior y verificar F útil ≥ F.
4. Si la fuerza crítica está en el retroceso, verificar con el área anular.
5. Revisar pandeo, consumo y velocidad con el diámetro adoptado.

Ejemplo: 800 N a 6 bar. Con η = 0,7, D mín = 49,2 mm → Ø50 (F útil 824,7 N). Con η = 0,5, D mín = 58,3 mm → Ø63 (F útil 935 N).

## Consumo de aire y caudal

- El volumen de la cámara se llena con aire a la presión de trabajo; en aire libre (a presión atmosférica) eso es (p + p_atm) / p_atm veces más: a 6 bar, 6,923 veces.
- Doble efecto: V_ciclo = (A_e + A_r) · s · (p + p_atm) / p_atm. Simple efecto: solo el avance.
- Q [l/min] = V_ciclo [l] × ciclos por minuto. Para pasar a m³/h, × 60 / 1000.
- Caudal durante una carrera de duración t: Q = A_e · (s / t) · (p + p_atm) / p_atm. Sirve para elegir el tamaño de la válvula y de las mangueras con el caudal nominal del catálogo.
- Al consumo de los cilindros se le suma el volumen de mangueras y conexiones entre válvula y cilindro (se llena en cada carrera) y las fugas. La red, el compresor y el tanque se calculan con la skill **calculos-ingenieria**.

## Pandeo del vástago

Fórmula de Euler: F_k = π² · E · I / L_k², con I = π · d⁴ / 64 y L_k = β · L.

| Caso de Euler | Extremos | β |
|---|---|---|
| 1 | Empotrado en un extremo y libre en el otro | 2 |
| 2 | Articulado en los dos extremos | 1 |
| 3 | Empotrado en un extremo y articulado en el otro | 0,7 (exacto 0,699: raíz de tan x = x, x = 4,4934; β = π / x) |
| 4 | Empotrado en los dos extremos | 0,5 |

- L es la longitud libre con el vástago afuera: el fabricante indica cómo medirla para cada tipo de fijación (brida, pie, charnela, muñón). Si no hay dato, tomar el caso más desfavorable que pueda darse.
- Carga admisible F_adm = F_k / ν. HANSA-FLEX usa ν = 3,5 en su diagrama de pandeo para cilindros articulados en los dos extremos ([información técnica](https://www.hansa-flex.de/fileadmin/hansaflex/Technical_Information/English/TI-Hydraulic_cylinders_EN_web.pdf)); si el fabricante del cilindro publica su propio diagrama de carrera máxima, ese manda.
- Validez: esbeltez λ = L_k / i, con i = d / 4 para sección circular llena, o sea λ = 4 · L_k / d. Euler describe bien vástagos con λ mayor que unos 100 y sobreestima la carga crítica por debajo ([Power & Motion](https://www.powermotiontech.com/technologies/cylinders-actuators/article/21887243/understanding-buckling-strength-of-hydraulic-cylinders)). Con λ chico, usar el diagrama del fabricante o un método inelástico (Tetmajer, Johnson).
- E del acero: 210 000 N/mm².

Ejemplo (`python scripts/neumatica.py demo`): vástago Ø10 de un cilindro Ø25, L = 400 mm, caso 1 → L_k = 800 mm, I = 490,9 mm⁴, F_k = 1.590 N, F_adm = 454 N con ν = 3,5, λ = 320. La fuerza teórica a 6 bar (295 N) verifica; la longitud máxima para 295 N es 496 mm.

## Velocidad y amortiguación

- La velocidad depende del caudal que dejan pasar la válvula, las mangueras y los reguladores; se ajusta con reguladores de caudal unidireccionales estrangulando el escape.
- La energía cinética de la carga al final de la carrera tiene que poder absorberla la amortiguación del cilindro: el catálogo da la energía o la velocidad máxima admisible para cada diámetro. Si no alcanza, agregar amortiguadores externos o bajar la velocidad.
