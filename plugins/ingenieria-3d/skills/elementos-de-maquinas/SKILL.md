---
name: elementos-de-maquinas
description: "Cálculo y selección de elementos de máquinas con memoria de cálculo: tornillos métricos (área resistente, precarga, torque de apriete, clases ISO 898-1), ejes a fatiga y fluencia (Goodman, von Mises, factores de Marin), chavetas DIN 6885-1, rodamientos (vida L10, capacidad necesaria), correas en V, cadenas de rodillos, engranajes cilíndricos rectos (geometría y Lewis) y cordones de soldadura en filete. Usar cuando haya que dimensionar o verificar un eje, un tornillo, una chaveta, un rodamiento, una transmisión por correa, cadena o engranajes, o una soldadura, o calcular el torque de apriete o la vida de un rodamiento."
---

# Elementos de máquinas

`scripts/elementos.py` (Python 3.9+, solo biblioteca estándar) hace cada cálculo e imprime fórmula, reemplazo y resultado, listo para una memoria de cálculo (presentación en **calculos-ingenieria**). Las tablas con su fuente están en [references/tablas.md](references/tablas.md): leerlas para citar un valor o calcular a mano. Bibliografía de base: Budynas y Nisbett, *Diseño en ingeniería mecánica de Shigley* (caps. 6 a 9, 13, 14 y 17).

Unidades del script: mm, N, N·m, MPa, kN y rpm.

## Tornillos

- Área resistente: As = π/4·((d2 + d3)/2)², d2 = d − 0,6495·P y d3 = d − 1,2269·P (ISO 898-1).
- Carga de prueba Fp = As·Sp; precarga Fi = 0,75·Fp si se desarma y 0,90·Fp si es permanente; torque T = K·Fi·d con K = 0,2 si no hay datos de lubricación (Shigley, cap. 8).
- La clase dice la resistencia: 8.8 → Rm 800 MPa y fluencia 640 MPa. Ojo: en 8.8, de M18 para arriba cambian los valores (tabla).

`python elementos.py tornillo --d 16 --clase 10.9 --carga 40000` → As = 156,7 mm², Fp = 130 035 N, Fi = 97 526 N, T = 312,1 N·m.

## Ejes

Eje que gira con flexión (alternante) y torque constante:

- Límite de fatiga: Se = ka·kb·ke·Se', con Se' = 0,5·Sut, ka por acabado, kb por tamaño y ke por confiabilidad.
- σa = 32·Kf·M/(π·d³) y σm = √3·16·Kfs·T/(π·d³) (von Mises de cada parte).
- Fatiga, ED-Goodman: 1/nf = σa/Se + σm/Sut. Fluencia: ny = Sy/σmax, con σmax = √((32·Kf·M/(π·d³))² + 3·(16·Kfs·T/(π·d³))²).
- Con `--n` despeja el diámetro mínimo; con `--d` verifica. Kf y Kfs salen del hombro, chavetero o ranura (Kt y sensibilidad a la entalla, Shigley cap. 6); sin ellos el eje se supone liso y el script avisa.

`python elementos.py eje --M 150 --T 200 --sut 600 --sy 350 --n 2 --kf 1.7 --kfs 1.5` → d mínimo 33,92 mm (nf = 2,00, ny = 3,68): se adopta 35 mm y se verifica con `--d 35`.

## Chavetas

Sección b × h de la DIN 6885-1 según el diámetro; F = 2·T/d. Corte: L ≥ F·n/(b·0,577·Sy). Aplastamiento con la mitad de la altura: L ≥ F·n/((h/2)·Sy). Se toma el mayor y el largo normalizado siguiente. Si pasa 1,5·d, conviene dos chavetas, un estriado o más diámetro (Shigley, cap. 7). El Sy es el del material de la chaveta (o del cubo, si es más blando).

## Rodamientos

L10 = (C/P)^p millones de vueltas, p = 3 a bolas y 10/3 a rodillos; L10h = 10⁶·L10/(60·n) (ISO 281). Carga equivalente P = X·Fr + Y·Fa con X e Y del catálogo. Con `--horas` sale la C necesaria para elegir en el catálogo. Vidas de diseño orientativas por tipo de máquina en la tabla.

`python elementos.py rodamiento --C 25.5 --fr 3 --fa 1 --x 0.56 --y 1.6 --rpm 1450 --horas 20000` → L10h = 5401 h; para 20 000 h hace falta C ≥ 39,45 kN.

## Correas en V y cadenas

- Correa: L = 2·C + π·(D + d)/2 + (D − d)²/(4·C); con un largo normalizado, C = 0,25·[(L − π·(D + d)/2) + √((L − π·(D + d)/2)² − 2·(D − d)²)]. Ángulo de la polea chica 180° − 2·asen((D − d)/(2·C)). Velocidad conveniente 5 a 25 m/s; D ≤ C ≤ 3·(D + d). La cantidad de correas sale de la potencia por correa del catálogo, corregida por ángulo y largo, contra la potencia de diseño P·Ks.
- Cadena: L/p = 2·C/p + (z1 + z2)/2 + (z2 − z1)²/(4·π²·C/p), redondeado a número par; D = p/sen(180°/z); piñón de 17 dientes o más y centros a 30 a 50 pasos (Shigley, cap. 17). El paso y la potencia admisible salen del catálogo (Renold, Rexnord, Tsubaki).

## Engranajes cilíndricos rectos

d = m·z, diámetro exterior m·(z + 2), de pie m·(z − 2,5), a = m·(z1 + z2)/2, p = π·m. Ft = 2·T/d1 y Fr = Ft·tg 20°. Lewis: σ = Kv·Ft/(b·m·Y), con Y de la tabla y Kv según cómo se tallaron. Ancho conveniente 3·p a 5·p; con 20° y menos de 18 dientes en el piñón puede haber interferencia. Lewis es un control de primera mano: el diseño final va por AGMA (flexión y picado).

## Soldadura en filete

Garganta a = 0,707·cateto; τ = F/(a·L·cordones); admisible AWS 0,30·Sut del electrodo (E70XX: 482 MPa → 144,6 MPa). Si la carga está excéntrica, hay que sumar la torsión o la flexión del grupo de cordones, y controlar también el metal base.

## Errores frecuentes

- Usar el diámetro nominal del tornillo en lugar del área resistente.
- Calcular un eje solo a torsión, o con Kf = 1 en un chavetero.
- Elegir el rodamiento por la carga estática cuando gira (va por vida L10) o al revés.
- Largo de correa no normalizado: hay que elegir uno del catálogo y recalcular C.
- Número impar de eslabones (obliga a un eslabón acodado, más débil).
- Mezclar N·mm con N·m o kN con N: el script trabaja siempre en las unidades de arriba.

## Verificación

`python elementos.py demo` tiene que terminar en `DEMO OK`. Compara el área resistente de M6 a M36 con la tabla de la ISO 898-1 (diferencia menor que 0,4 %, el redondeo de la tabla) y la carga de prueba de un M12 8.8 (48,9 kN). Reproduce el ejemplo de eje del cap. 7 de Shigley (eje de 1,1 in, M = 1260 lbf·in, T = 1100 lbf·in, Sut = 105 kpsi: nf = 1,62) y despeja el diámetro de vuelta. Además, controla con cuentas a mano la chaveta, el rodamiento, la correa, la cadena, el engranaje y la soldadura. Para una entrega, una revisión independiente con **equipo-de-modelos** o **revision-tecnica**.
