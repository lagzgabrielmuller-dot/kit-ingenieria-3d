---
name: neumatica-electroneumatica
description: "Diseño y cálculo de circuitos neumáticos y electroneumáticos para TPs y prácticas con FluidSIM, Automation Studio o tablero real: componentes (compresor, unidad FRL, válvulas 3/2, 5/2 y 5/3, accionamientos, cilindros de simple y doble efecto, reguladores de caudal, escape rápido, válvulas O e Y, temporizadores), símbolos ISO 1219 y numeración de conexiones (1, 2, 4, 3, 5, 12, 14), diagrama espacio-fase, secuencias tipo A+ B+ B- A-, métodos intuitivo, cascada y paso a paso, relés, finales de carrera y sensores, GRAFCET y su paso a PLC, fuerza y consumo de aire de cilindros, diámetro normalizado y pandeo del vástago, con script en Python. Usar cuando se pida armar, resolver o explicar un circuito neumático o electroneumático, una secuencia de cilindros, el método cascada, un GRAFCET, calcular un cilindro, su consumo de aire o el pandeo, o revisar un esquema de FluidSIM."
---

# Neumática y electroneumática

Circuitos con cilindros para TPs, prácticas de laboratorio y tableros didácticos. No se repite lo que ya está en otras skills:
- Red de aire comprimido (caudal total, Δp, diámetro de cañería, tanque): skill **calculos-ingenieria**.
- Plano del esquema en DXF y PDF A3: skill **planos-tecnicos**. Informe del TP: skill **informe-tecnico**.
- Programar el PLC (TIA Portal, CODESYS): plugin **automatizacion-industrial** (skills `siemens-tia-portal` y `codesys`).
- Normas y reglamentaciones argentinas (tanques a presión, seguridad): skill **normas-tecnicas-ar**.

## Método (siempre)

1. **Leer la consigna** y anotar: cilindros y qué hace cada uno, secuencia, marcha (ciclo único o continuo), paro, emergencia, temporizaciones, movimientos simultáneos, tipo de mando (neumático, electroneumático o PLC) y programa (FluidSIM, Automation Studio, tablero).
2. **Escribir la secuencia** con letras (A+ = A sale, A− = A entra) y dibujar el **diagrama espacio-fase**.
3. **Analizar la secuencia** con `python scripts/neumatica.py cascada "A+ B+ B- A-"`: dice si el método intuitivo alcanza o qué señales chocan, y arma los grupos de la cascada.
4. **Elegir el método**: intuitivo (sin conflictos), cascada (pocos grupos), paso a paso (muchos grupos o se quiere ampliar fácil), relés o PLC (electroneumática).
5. **Dimensionar** cada cilindro: fuerza con rendimiento, diámetro normalizado, consumo y pandeo (`cilindro`, `pandeo`).
6. **Dibujar el esquema** en posición de reposo, con símbolos ISO 1219-1, conexiones numeradas y cada componente identificado.
7. **Simular** paso a paso (FluidSIM o Automation Studio) y recién después armar el tablero.
8. **Documentar**: secuencia, diagrama, esquema, lista de componentes, cálculos y explicación del funcionamiento.

## Componentes

| Componente | Función | A tener en cuenta |
|---|---|---|
| Compresor y depósito | Generan y acumulan el aire | El depósito es un aparato sometido a presión (ver **normas-tecnicas-ar**) |
| Unidad FRL | Filtro, regulador con manómetro y lubricador | El lubricador se usa según lo que indique el fabricante de los equipos |
| Válvula distribuidora n/m | n vías (conexiones) y m posiciones: 3/2, 4/2, 5/2, 5/3 | 3/2 normal cerrada (NC) o abierta (NA); 5/3 con centro cerrado, a escape o a presión |
| Accionamientos | Pulsador, palanca, pedal, rodillo, rodillo abatible, piloto neumático, solenoide, resorte | Monoestable: vuelve sola (resorte). Biestable: queda en la última posición (memoria) |
| Cilindro de simple efecto | Avanza con aire y retrocede con resorte | El resorte resta fuerza al avance |
| Cilindro de doble efecto | Avanza y retrocede con aire | El retroceso tiene menos fuerza (área anular) |
| Regulador de caudal unidireccional | Estrangulador con antirretorno: regula la velocidad | En doble efecto se estrangula el aire de escape |
| Válvula de escape rápido | Descarga el cilindro cerca de la cámara | Aumenta la velocidad de retroceso o avance |
| Válvula O (selectora) | Sale señal si llega por cualquiera de sus dos entradas | Mando desde dos lugares |
| Válvula Y (de simultaneidad) | Sale señal solo si llegan las dos | Mando a dos manos, condiciones Y |
| Temporizador neumático | Estrangulador, depósito y 3/2 | Retardo a la conexión o a la desconexión |
| Captadores | Final de carrera de rodillo, sensor magnético en la camisa, inductivo, capacitivo, óptico, presostato | Se nombran a0 (A adentro) y a1 (A afuera) |

## Símbolos y numeración de conexiones

- Símbolos: **ISO 1219-1:2012** (con Amd 1:2016) ([iso.org](https://www.iso.org/standard/60184.html)). Reglas para dibujar el esquema: **ISO 1219-2:2012** ([iso.org](https://www.iso.org/standard/51200.html)).
- Conexiones: **ISO 11727:1999** ([iso.org](https://www.iso.org/standard/19651.html), extracto público en [iTeh](https://cdn.standards.iteh.ai/samples/19651/1b2216534be8442abe9f25ed37abc365/ISO-11727-1999.pdf)). Las vías principales llevan una cifra: **1** alimentación, **2 y 4** utilización (salidas), **3 y 5** escapes. Los pilotajes y mandos llevan dos cifras: la primera es 1 y la segunda es la vía que queda conectada con 1 al accionarlos: **14** une 1 con 4, **12** une 1 con 2, **10** bloquea la 1.
- Cada cuadrado es una posición; el esquema se dibuja **en reposo**, con las tuberías conectadas al cuadrado de la posición de reposo.
- Identificación de componentes: FluidSIM y muchos apuntes usan 1A1 (cilindro), 1V1 (válvula), 1S1 (captador), que vienen de la primera edición de ISO 1219-2; la edición 2012 ya no usa letras (lo dice su introducción, [vista previa](https://webstore.ansi.org/preview-pages/ISO/preview_ISO+1219-2-2012.pdf)). Se usa la nomenclatura que pida la cátedra.
- Disposición habitual del esquema: abajo la alimentación y la FRL; encima los captadores y pulsadores; después las válvulas de procesamiento (O, Y, memorias, temporizadores); después las de potencia y arriba los cilindros.

Detalle de símbolos, accionamientos y sensores: [references/simbolos-y-componentes.md](references/simbolos-y-componentes.md) (leerlo al dibujar o revisar un esquema).

## Diagrama espacio-fase

Una fila por cilindro (0 = adentro, 1 = afuera) y una columna por fase; cada movimiento es una línea inclinada y al final de cada fase se anota la señal que la termina. Para A+ B+ B− A−:

| Fase | 1 | 2 | 3 | 4 | 5 = 1 |
|---|---|---|---|---|---|
| A | 0 → 1 | 1 | 1 | 1 → 0 | 0 |
| B | 0 | 0 → 1 | 1 → 0 | 0 | 0 |
| Termina con | a1 | b1 | b0 | a0 | (Marcha) |

## Secuencias: intuitivo, cascada y paso a paso

**Método intuitivo**: cada movimiento lo manda el fin de carrera del movimiento anterior (el primero, Marcha · fin del último). Falla cuando una señal sigue activa al momento de mandar el movimiento contrario del mismo cilindro (señal permanente o bloqueante). Salida del script para A+ B+ B− A−:

```
A+  <- Marcha · a0      B+  <- a1      B-  <- b1      A-  <- b0
CONFLICTO en A: cuando tiene que hacer A+ sigue activa b0, que manda A-.
CONFLICTO en B: cuando tiene que hacer B- sigue activa a1, que manda B+.
```

**Método cascada** (reglas):
1. Se divide la secuencia en **grupos** sin letras repetidas: A+ B+ | B− A−.
2. G grupos → G líneas de presión y **G − 1 válvulas memoria** (4/2 o 5/2 biestables). Solo una línea tiene presión a la vez.
3. El primer movimiento de cada grupo sale **directo de su línea**; los siguientes, del fin de carrera del movimiento anterior **alimentado por la línea del grupo**.
4. El fin de carrera del último movimiento de cada grupo activa la línea siguiente; para volver a la línea I va en serie con **Marcha**. En reposo queda con presión la última línea.

Para A+ B+ B− A− el script da: grupos I = [A+ B+] y II = [B− A−], 1 memoria; b1 (alimentado por la línea I) activa la línea II; Marcha · a0 (alimentado por la línea II) activa la línea I; B+ sale de a1 con la línea I y A− de b0 con la línea II. Con una 5/2 biestable: línea I en la salida 4 (pilotaje 14) y línea II en la 2 (pilotaje 12). Si el último y el primer grupo no comparten cilindros, `--unir-extremos` ahorra un grupo.

**Paso a paso**: una memoria por paso; cada memoria se activa con la del paso anterior y el fin de carrera correspondiente, y se borra con la del paso siguiente. Hacen falta al menos 3 pasos: con 2, el paso anterior y el siguiente serían la misma memoria y recibiría activación y borrado a la vez.

Ejemplos completos (cascada de 3 grupos, unión de extremos, temporizadores, rodillo abatible): [references/metodos-secuencias.md](references/metodos-secuencias.md).

## Electroneumática

- Mando a 24 V CC: pulsadores (S), relés (K) con contactos NA y NC, finales de carrera eléctricos o sensores, y electroválvulas (bobinas Y).
- **Monoestable** (retorno por resorte): la bobina tiene que quedar energizada todo el tiempo que el cilindro deba estar afuera. **Biestable**: alcanza un pulso, pero nunca las dos bobinas a la vez.
- **Autorretención**: el relé se mantiene con un contacto propio en paralelo con la orden de marcha y se corta con un NC en serie.
- Cascada eléctrica: G − 1 relés. Para A+ B+ B− A− con válvulas biestables (Y1 = A+, Y2 = A−, Y3 = B+, Y4 = B−) alcanza un relé: K1 = (Marcha · a0 + K1) · /b1; Y1 = K1; Y3 = K1 · a1; Y4 = /K1; Y2 = /K1 · b0 (la barra indica contacto NC).
- Paso a paso eléctrico: un relé por paso, como en el neumático; es el más fácil de ampliar.
- Paro y emergencia: definir qué hace cada cilindro (quedarse, volver o descargarse) según el tipo de válvula; una biestable mantiene la posición aunque se corte la tensión.

Esquemas de escalera completos y sensores de 3 hilos: [references/metodos-secuencias.md](references/metodos-secuencias.md).

## GRAFCET y paso a PLC

- Lenguaje definido por **IEC 60848:2013** (3.ª edición, [webstore IEC](https://webstore.iec.ch/en/publication/3684)): etapas (la inicial con doble cuadro), transiciones con su receptividad y acciones asociadas a las etapas.
- Reglas de evolución (cláusulas 4.5.2 a 4.5.6): situación inicial; una transición se franquea si todas sus etapas anteriores están activas y la receptividad es verdadera; al franquearla se desactivan las etapas anteriores y se activan las siguientes a la vez; las transiciones franqueables al mismo tiempo se franquean juntas; una etapa activada y desactivada a la vez queda activa.
- A+ B+ B− A−: etapa 0 (reposo) → Marcha · a0 · b0 → etapa 1 (Y1, A+) → a1 → etapa 2 (Y3, B+) → b1 → etapa 3 (Y4, B−) → b0 → etapa 4 (Y2, A−) → a0 → etapa 0.
- Al PLC: una marca por etapa, X(i) se activa con X(i−1) · receptividad y se borra con X(i+1); la etapa inicial se activa en el primer ciclo. Con válvulas monoestables la salida se mantiene en todas las etapas en que el cilindro debe seguir afuera (en el ejemplo, Y_A = X1 + X2 + X3). Para escribirlo en TIA Portal o CODESYS, usar el plugin **automatizacion-industrial**.

## Cálculo de cilindros

| Magnitud | Fórmula | Símbolos y unidades |
|---|---|---|
| Fuerza de avance | F_av = η · p · A_e, con A_e = π · D² / 4 | p presión manométrica [N/mm²] (1 bar = 0,1 N/mm²), D émbolo [mm], F [N] |
| Fuerza de retroceso | F_ret = η · p · A_r, con A_r = π · (D² − d²) / 4 | d vástago [mm], A_r área anular [mm²] |
| Diámetro mínimo | D = √(4 · F / (π · p · η)) | Se adopta el normalizado inmediato superior |
| Aire libre por ciclo | V = (A_e + A_r) · s · (p + p_atm) / p_atm | s carrera [mm]; mm³ · 10⁻⁶ = l; p_atm = 1,013 bar |
| Consumo | Q = V · n | n ciclos por minuto → l/min de aire libre |
| Caudal en la carrera | Q = A_e · v · (p + p_atm) / p_atm | v = s / t velocidad media [m/s] |
| Pandeo (Euler) | F_k = π² · E · I / L_k², I = π · d⁴ / 64, L_k = β · L | E acero 210 000 N/mm², I [mm⁴], L_k longitud libre [mm] |

- **Rendimiento o factor de carga η**: SMC recomienda η ≤ 0,7 para trabajo estático (sujetar, prensar), η ≤ 0,5 para mover una carga y menos aún a alta velocidad; hasta 1 en horizontal con guía ([datos técnicos SMC](https://ca01.smcworld.com/catalog/BEST-technical-data-en/pdf/6-2-1-m21-43-tech_en.pdf)). En simple efecto se resta además la fuerza del resorte (catálogo).
- **Diámetros usuales** [mm]: 8, 10, 12, 16, 20, 25 (ISO 6432, [iso.org](https://www.iso.org/standard/64054.html)) y 32, 40, 50, 63, 80, 100, 125… hasta 320 (ISO 15552, [iso.org](https://www.iso.org/standard/66921.html)). Vástagos típicos y fuerzas a 6 bar: [references/cilindros-tablas.md](references/cilindros-tablas.md).
- **Pandeo**: β = 2 (empotrado-libre), 1 (articulado-articulado), 0,7 (empotrado-articulado; el valor exacto es 0,699) y 0,5 (empotrado-empotrado). F_adm = F_k / ν; como referencia, HANSA-FLEX usa ν = 3,5 en su diagrama de pandeo para cilindros articulados en los dos extremos ([información técnica](https://www.hansa-flex.de/fileadmin/hansaflex/Technical_Information/English/TI-Hydraulic_cylinders_EN_web.pdf)). Si el fabricante del cilindro da su diagrama, manda ese. Euler sirve con esbeltez 4 · L_k / d mayor que unos 100; por debajo sobreestima la carga crítica ([Power & Motion](https://www.powermotiontech.com/technologies/cylinders-actuators/article/21887243/understanding-buckling-strength-of-hydraulic-cylinders)).
- Al consumo calculado se le suman mangueras y volúmenes muertos; en su ejemplo de selección, SMC elige un compresor de al menos 1,4 veces el consumo. La red y el tanque se calculan con **calculos-ingenieria**.

**Ejemplo** (`python scripts/neumatica.py demo`): cilindro Ø50/20 mm, 6 bar, carrera 200 mm, η = 0,7, 10 ciclos/min.

| Resultado | Valor |
|---|---|
| A_e / A_r | 19,63 cm² / 16,49 cm² |
| F_av teórica / útil | 1.178,1 N / 824,7 N |
| F_ret teórica / útil | 989,6 N / 692,7 N |
| Aire libre por ciclo | 2,719 l + 2,284 l = 5,002 l |
| Consumo | 50,0 l/min = 3,00 m³/h |
| Para 800 N útiles con η = 0,7 / 0,5 | D mín 49,2 mm → Ø50 / 58,3 mm → Ø63 |

Verificación: la fuerza teórica a 6 bar coincide con la del catálogo Festo DSBC para Ø50/20 (1.178 N y 990 N).

## Script

```
python scripts/neumatica.py demo
python scripts/neumatica.py cilindro --D 50 --d 20 --p 6 --carrera 200 --eta 0.7 --ciclos 10 --tiempo 0.5
python scripts/neumatica.py cilindro --fuerza 800 --p 6 --eta 0.5 --carrera 150
python scripts/neumatica.py tabla --p 6 --eta 0.7
python scripts/neumatica.py cascada "A+ B+ B- A-" [--unir-extremos]
python scripts/neumatica.py pandeo --d 10 --L 400 --caso 1 --F 295
python scripts/neumatica.py pandeo --d 10 --caso 1 --F 295        (longitud máxima)
```

Python 3.9 o posterior, sin dependencias. Las secuencias se escriben de a un movimiento; los movimientos simultáneos se resuelven a mano.

## Seguridad

- **Energía residual**: al cerrar la alimentación queda aire atrapado en cilindros, tubos y depósitos. Una carga puede moverse al accionar una válvula o al soltar una manguera, y una carga vertical puede caer al descargar.
- **Bloqueo y purga** antes de intervenir: cerrar con una válvula de corte con escape y trabarla con candado y tarjeta, descargar todo el circuito, verificar presión cero con manómetro y calzar las cargas.
- Al volver a dar aire, usar arranque progresivo si lo hay y confirmar la posición de cada válvula: con biestables, el cilindro puede salir apenas llega la presión.
- Nunca desconectar mangueras con presión (latigazo), usar protección ocular, silenciadores en los escapes y no dirigir aire comprimido al cuerpo.
- Reglas generales de seguridad de sistemas neumáticos en máquinas: **ISO 4414:2010** ([iso.org](https://www.iso.org/standard/44790.html)); no cubre compresores ni la red de distribución.

## Errores frecuentes

- Armar por intuición una secuencia con señales en conflicto: el cilindro no se mueve o la válvula queda trabada.
- Regular la velocidad de un doble efecto estrangulando la entrada en vez del escape (movimiento a saltos).
- Usar el área completa para el retroceso, olvidar η, o confundir aire libre con aire comprimido.
- Esquema dibujado fuera de la posición de reposo, numeración de vías inventada o captadores sin ubicar en el diagrama.
- Monoestable cuya bobina se corta antes de tiempo; biestable con las dos bobinas energizadas.
- En cascada, alimentar un captador desde la red en lugar de la línea de su grupo (vuelve la señal permanente).
- Tomar la carrera como longitud de pandeo sin el factor β del montaje, o aplicar Euler con esbeltez baja.

## Cómo presentar el TP

1. Consigna, secuencia y diagrama espacio-fase.
2. Método elegido y por qué (salida del análisis de conflictos).
3. Esquema neumático (y eléctrico o GRAFCET) en reposo, con componentes identificados y vías numeradas.
4. Lista de componentes: código, designación (por ejemplo, válvula 5/2 biestable con pilotaje neumático), cantidad.
5. Funcionamiento fase por fase, cálculos (fórmula, datos, reemplazo, resultado, valor adoptado) y capturas de la simulación.

## Verificación antes de entregar

1. Simular el ciclo completo, el arranque, el paro y la emergencia; en reposo, cada captador tiene que estar como dice el diagrama.
2. Volver a correr `cascada` y comprobar grupos, memorias y señales de cambio contra el esquema.
3. Revisar unidades (bar a N/mm², mm³ a litros) y que F útil ≥ F pedida con el diámetro adoptado.
4. Verificar el pandeo con la longitud y el montaje reales.
5. Confirmar diámetros, vástagos y datos con el catálogo del cilindro elegido.
