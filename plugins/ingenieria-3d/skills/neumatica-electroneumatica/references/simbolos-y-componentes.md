# Símbolos, conexiones y componentes

Leer este archivo al dibujar un esquema neumático, al revisar uno hecho en FluidSIM o Automation Studio, o al armar la lista de componentes.

## Normas

| Norma | Qué define | Enlace |
|---|---|---|
| ISO 1219-1:2012 + Amd 1:2016 | Elementos básicos de los símbolos y reglas para armarlos (neumática e hidráulica) | [iso.org](https://www.iso.org/standard/60184.html) · [Amd 1](https://www.iso.org/standard/66287.html) |
| ISO 1219-2:2012 | Reglas para dibujar esquemas de circuitos | [iso.org](https://www.iso.org/standard/51200.html) |
| ISO 11727:1999 | Identificación de vías y mandos de válvulas y otros componentes neumáticos | [iso.org](https://www.iso.org/standard/19651.html) |

Las normas ISO son pagas. FluidSIM y Automation Studio traen las bibliotecas de símbolos; para el TP alcanza con usarlas bien y nombrarlas como pide la cátedra.

## Cómo se lee una válvula distribuidora

- Cada **cuadrado** es una posición; la cantidad de cuadrados es la cantidad de posiciones.
- Dentro de cada cuadrado, una **flecha** es un paso de aire y una **T** es una vía cerrada.
- Las tuberías se dibujan conectadas al cuadrado de la **posición de reposo**. El accionamiento dibujado al costado de un cuadrado es el que pone esa posición.
- Designación: **vías/posiciones**. 3/2 = tres vías y dos posiciones; 5/2; 5/3.
- 3/2 **normal cerrada** (NC): en reposo la 1 está bloqueada y la 2 descarga por la 3. 3/2 **normal abierta** (NA): en reposo la 1 alimenta a la 2.

| Válvula | Uso típico |
|---|---|
| 2/2 | Abrir o cerrar un paso |
| 3/2 NC | Señales (pulsadores, finales de carrera), mando de cilindros de simple efecto, corte con escape |
| 3/2 NA | Señal que se corta al accionar |
| 4/2 o 5/2 | Mando de cilindros de doble efecto; como biestable, memoria |
| 5/3 centro cerrado | Detener el cilindro en una posición intermedia (queda aire atrapado en las dos cámaras) |
| 5/3 centro a escape | Dejar el cilindro sin presión en las dos cámaras (se mueve a mano) |
| 5/3 centro a presión | Presión en las dos cámaras: en un cilindro con vástago simple sale por la diferencia de áreas |

## Numeración de vías y mandos (ISO 11727)

Según las cláusulas 4.2, 4.3 y la tabla 1 de ISO 11727:1999 ([extracto público](https://cdn.standards.iteh.ai/samples/19651/1b2216534be8442abe9f25ed37abc365/ISO-11727-1999.pdf)):

| Identificación | Significado |
|---|---|
| 1 | Entrada (alimentación) |
| 2 y 4 | Salidas (utilización) |
| 3 y 5 | Escapes |
| 12 | Mando que une la 1 con la 2 |
| 14 | Mando que une la 1 con la 4 |
| 10 | Mando que bloquea la 1 (por ejemplo, el que vuelve a reposo una 3/2 NA) |

- Vías principales: una cifra. Mandos, pilotajes y sus cables: dos cifras, la primera es 1 y la segunda la vía que queda unida con la 1 al accionar. La regla no se aplica a la posición central de las válvulas de tres posiciones.
- En libros viejos aparecen letras: P para la alimentación, A y B para las salidas, R y S para los escapes. Si el apunte las usa, tomar su tabla de equivalencias.
- En un esquema, si la salida 4 va a la cámara de avance, el pilotaje 14 (o la bobina del lado 14) produce el avance.

## Accionamientos

| Accionamiento | Dónde se usa |
|---|---|
| Pulsador, palanca, pedal | Marcha, paro, mando manual |
| Rodillo | Final de carrera: da señal mientras la leva lo apreta |
| Rodillo abatible (escamoteable) | Da señal solo en un sentido del movimiento; resuelve señales permanentes sin memoria, pero hay que ubicarlo un poco antes del final |
| Pilotaje neumático (12, 14) | Señal que viene de otra válvula |
| Solenoide | Electroválvula; puede tener servopilotaje y accionamiento manual auxiliar |
| Resorte | Retorno a reposo (válvula monoestable) |

## Componentes de tratamiento y regulación

- **Unidad FRL**: filtro con purga, regulador de presión con manómetro y lubricador; el lubricador se usa según indique el fabricante de los equipos. A la entrada conviene una válvula de corte con escape (3/2) bloqueable.
- **Regulador de caudal unidireccional**: estrangulador regulable en paralelo con un antirretorno. Se coloca para que estrangule el aire que sale del cilindro (regulación en el escape).
- **Escape rápido**: descarga la cámara directo a la atmósfera, cerca del cilindro.
- **Válvula O (selectora)**: dos entradas y una salida; sale la que tenga presión.
- **Válvula Y (simultaneidad o de dos presiones)**: sale aire solo si llegan las dos señales.
- **Temporizador neumático**: estrangulador + depósito + 3/2 pilotada; el tiempo se regula con el estrangulador.
- **Presostato**: da señal cuando se alcanza una presión (por ejemplo, para confirmar que una prensa llegó a la fuerza).

## Captadores (sensores)

| Tipo | Detecta | Notas |
|---|---|---|
| Final de carrera mecánico (neumático o eléctrico) | Contacto con una leva | Simple y robusto; tiene desgaste |
| Magnético (reed o electrónico) en la camisa | El imán del émbolo | El cilindro tiene que ser con émbolo magnético |
| Inductivo | Metales a pocos milímetros | Sin contacto; distancia de detección según el metal |
| Capacitivo | Casi cualquier material (también líquidos y granos) | Ajuste de sensibilidad |
| Óptico | Interrupción o reflexión de luz | Barrera, réflex o difuso |

- Los sensores electrónicos de corriente continua suelen ser de 3 hilos (dos de alimentación y uno de salida). En un sensor **PNP** la salida activa entrega +24 V a la carga; en uno **NPN** la conecta a 0 V. Conectar siempre según la hoja de datos y según el tipo de entrada del PLC o del relé.
- Nombrar los captadores igual que en el diagrama espacio-fase: a0 (A adentro), a1 (A afuera), b0, b1…

## Lista de componentes del esquema

| Código | Designación | Cantidad |
|---|---|---|
| 0Z1 | Unidad FRL con manómetro | 1 |
| 0V1 | Válvula 3/2 de corte con escape, bloqueable | 1 |
| 1A1 | Cilindro de doble efecto Ø50 × 200 mm, émbolo magnético | 1 |
| 1V1 | Válvula 5/2 biestable con pilotaje neumático | 1 |
| 1V2, 1V3 | Reguladores de caudal unidireccionales | 2 |
| 1S1, 1S2 | Finales de carrera 3/2 NC con rodillo (a0, a1) | 2 |

Códigos de ejemplo al estilo de FluidSIM; si la cátedra usa otra nomenclatura, se adapta.
