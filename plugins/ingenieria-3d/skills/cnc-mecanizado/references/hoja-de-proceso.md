# Hoja de proceso (plantilla y ejemplo)

Leer cuando se pida la hoja de proceso, la tabla de operaciones o la planilla de herramientas de una pieza CNC. Si la cátedra tiene su propio formato, se usa ese con estos mismos datos.

## Plantilla

**Encabezado**

| Pieza | Plano n.º | Material | Bruto | Máquina y control | Sujeción | Cero pieza | Programa | Autor | Fecha |
|---|---|---|---|---|---|---|---|---|---|
| (completar) | | (designación y estado, HB) | (Ø × largo o placa) | (marca, modelo, control exacto) | (plato, morsa, voladizo) | (dónde está X0 Z0 o X0 Y0 Z0) | (O0001…) | | |

**Operaciones** (una fila por operación, en el orden en que se hacen):

| N.º | Operación | Herramienta (T y corrector; portaherramienta e inserto o fresa) | Vc (m/min) | n (rpm) | f (mm/v) o fz (mm/diente) | ap (mm) | Vf (mm/min) | L (mm) | Pasadas | t (min) | Observaciones |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | | | | | | | | | | | |

- n = 1000·Vc/(π·D) con el diámetro de cada operación (en fresadora, el de la herramienta); con G96, anotar el rango de rpm y el límite G50 S.
- Vf = f·n (torno) o fz·z·n (fresadora); t = L/Vf por pasada, con L que incluya la entrada y la salida.
- `cnc.py corte` imprime cada fila lista; `cnc.py perfil` da el tiempo de desbaste y terminación de un perfil.
- Al pie: tiempo total de corte, tiempo estimado de rápidos y cambios (si la cátedra lo pide), croquis de la sujeción con el cero pieza, y lista de herramientas con su corrector.

**Herramientas**

| T | Corrector | Portaherramienta | Plaquita o herramienta | Radio de punta | Material de corte | Uso |
|---|---|---|---|---|---|---|

## Ejemplo resuelto: eje escalonado del ejemplo de `cnc.py perfil`

Perfil Ø16 (chaflán de 2 × 45° hasta Ø20), Ø20 hasta Z−15, cono hasta Ø30 en Z−25 y Ø30 hasta Z−40; acero de bajo carbono; bruto Ø34; torno con control Fanuc (sistema A), límite G50 S2000. Datos de corte de ejemplo, del extremo bajo de los catálogos (ver `datos-de-corte.md`).

| Pieza | Material | Bruto | Máquina y control | Sujeción | Cero pieza | Programa |
|---|---|---|---|---|---|---|
| Eje escalonado | acero no aleado, C menor que 0,25 % | Ø34 × 70 | torno CNC, Fanuc T sistema A | plato de 3 mordazas, 50 mm de voladizo | eje de la pieza y cara terminada | O0001 |

| N.º | Operación | Herramienta | Vc (m/min) | n (rpm) | f (mm/v) | ap (mm) | Vf (mm/min) | L (mm) | Pasadas | t (min) | Observaciones |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 10 | Refrentado (G94) | T0101, plaquita de desbaste rε 0,8 | 180 | 1685 (Ø34) a 2000 | 0,20 | 1,0 | 337 a 400 | 18 | 1 | 0,05 | con G96 tarda algo menos que a 1685 rpm fijas |
| 20 | Desbaste exterior (G71) | T0101 | 180 | 1685 a 2000 | 0,25 | 1,0 | 421 a 500 | — | 8 + perfilado | 0,44 | deja 0,4 mm en X (diámetro) y 0,1 mm en Z |
| 30 | Terminación (G70) | T0202, plaquita de terminación | 220 pedida; real 100 a 188 | 2000 (límite) | 0,10 | 0,2 | 200 | — | 1 | 0,24 | la Vc pedida no se alcanza con 2000 rpm en Ø30 o menos |

Tiempo de corte total ≈ 0,05 + 0,44 + 0,24 = 0,73 min, sin rápidos ni cambios de herramienta.

De dónde salen los números:
- Fila 10: `cnc.py corte --vc 180 --d 34 --f 0,2 --ap 1 --l 18 --material acero-bajo-c` → n = 1685 rpm, Vf = 337 mm/min, t = 0,05 min, Pc = 1,14 kW. Con G96 la rpm sube hasta el límite de 2000 a partir de Ø28,6 (1000·180/(π·2000)).
- Filas 20 y 30: `cnc.py perfil --puntos "16;0 20;-2 20;-15 30;-25 30;-40" --bruto 34 --t-term T0202 --vc-term 220` → desbaste 0,44 min y terminación 0,24 min (integrado con G96 y el límite de rpm). Para 220 m/min harían falta 2000 rpm ya en Ø35, así que toda la terminación va a 2000 rpm: Vc real = π·D·2000/1000, de 100 m/min en Ø16 a 188 m/min en Ø30.
- Potencia del desbaste a Ø34 con ap 1 y f 0,25: `cnc.py corte --vc 180 --d 34 --f 0,25 --ap 1 --material acero-bajo-c` → Pc = 1,35 kW (1,69 kW en el motor con η = 0,8): comparar con la potencia del torno.
