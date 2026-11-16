# Seguridad en el mantenimiento: bloqueo y etiquetado (LOTO) y consignación

Leer cuando haya que escribir el procedimiento de bloqueo de un equipo, explicar el LOTO en un trabajo o preparar una intervención con la máquina parada. El marco legal argentino de higiene y seguridad (Ley 19.587, Decreto 351/79 y resoluciones de la SRT) está en **normas-tecnicas-ar**.

## 1. Qué se bloquea

Toda energía que pueda mover, energizar o lastimar durante la intervención: eléctrica (incluidos capacitores y variadores), neumática, hidráulica, mecánica (piezas elevadas por gravedad, resortes, volantes que siguen girando), térmica y química. El bloqueo y la purga de circuitos neumáticos están en **neumatica-electroneumatica**. La norma internacional de diseño para evitar arranques inesperados es ISO 14118:2017, *Safety of machinery — Prevention of unexpected start-up* ([ISO](https://www.iso.org/standard/66460.html)).

## 2. Secuencia del control de energía (OSHA)

Norma de EE. UU. 29 CFR 1910.147, *The control of hazardous energy (lockout/tagout)*, párrafo (d) ([eTool de OSHA](https://www.osha.gov/etools/lockout-tagout/tutorial/application-energy-control); [texto](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147)):

1. **Preparación**: el trabajador autorizado conoce el tipo y la magnitud de cada energía, sus riesgos y cómo controlarla.
2. **Parada** de la máquina con su procedimiento normal, para no crear riesgos extra al detenerla.
3. **Aislamiento**: se ubican y se accionan todos los dispositivos de aislamiento de energía (seccionador, válvula de corte con escape, traba mecánica).
4. **Colocación de candados y tarjetas** por cada trabajador autorizado, en cada dispositivo de aislamiento; los candados lo mantienen en la posición segura y la tarjeta queda bien visible.
5. **Energía acumulada**: se libera, se desconecta, se sujeta o se neutraliza (descargar capacitores, purgar aire y aceite, calzar o bajar cargas, frenar volantes).
6. **Verificación**: antes de empezar, se comprueba que la máquina quedó aislada y sin energía (probar el arranque con los mandos normales y medir ausencia de tensión).

**Liberación**, párrafo (e): inspeccionar la zona y retirar lo que no corresponde (herramientas, materiales); asegurar que todos estén a salvo o fuera de la zona y avisarles antes del arranque; cada candado o tarjeta lo retira **el mismo trabajador que lo colocó**.

**Dispositivos**, párrafo (c)(5)(ii): durables para el ambiente donde se usan, estandarizados en la planta, lo bastante robustos para que no se puedan sacar sin fuerza excesiva, e identificables: indican quién los colocó. El procedimiento por equipo tiene que estar escrito, con su alcance y los pasos para parar, aislar, bloquear, colocar y retirar los dispositivos y verificar que el bloqueo es efectivo (párrafo (c)(4)).

## 3. Consignación de una instalación eléctrica (Argentina)

Decreto 351/79, Anexo VI (capítulo 14, instalaciones eléctricas), reglamentario de la Ley 19.587 ([copia del anexo en la UNICEN](https://www.fio.unicen.edu.ar/extension/seh/images/pdf/cap14/anexovi-351-79.pdf); texto oficial en [InfoLEG](https://servicios.infoleg.gob.ar/infolegInternet/anexos/30000-34999/32030/texact.htm)):

- **1.1.4, consignación**: el conjunto de operaciones para separar la instalación de toda fuente de tensión, bloquear en apertura los aparatos de corte, verificar la ausencia de tensión, poner a tierra y en cortocircuito, y señalizar y delimitar la zona de trabajo.
- **2.1.3, trabajos sin tensión en baja tensión**: en los puntos de alimentación, (a.1) seccionar la parte donde se va a trabajar, separándola de cualquier alimentación posible; (a.2) bloquear en apertura los aparatos de seccionamiento y, si no se pueden inmovilizar, colocar el cartel «PROHIBIDO MANIOBRAR» con el nombre del responsable; (a.3) verificar la ausencia de tensión en cada parte seccionada; (a.4) descargar la instalación. En el lugar de trabajo se repiten esos pasos y se ponen en cortocircuito y a tierra todas las partes que puedan energizarse por accidente; si hace falta, se delimita la zona.
- **Reposición del servicio**: el responsable comprueba personalmente que se retiraron las puestas a tierra y los cortocircuitos, las herramientas, los materiales sobrantes y la señalización, y que el personal salió de la zona de peligro y fue avisado; recién entonces desbloquea y cierra los aparatos que había abierto.

## 4. Procedimiento de bloqueo de un equipo (modelo)

| Campo | Contenido |
|---|---|
| Equipo, código y ubicación | |
| Trabajos que cubre | |
| Personal autorizado y afectado | |
| Energías presentes | Eléctrica ___ V; neumática ___ bar; hidráulica ___ bar; mecánica (gravedad, resortes, inercia); térmica |
| Dispositivo de aislamiento de cada energía y ubicación | Seccionador del tablero ___; válvula de corte ___ |
| Cómo se bloquea cada uno | Candado personal y tarjeta; pinza multicandado si son varios |
| Energía acumulada y cómo se libera | Descarga de capacitores (esperar el tiempo del fabricante del variador); purga; calzas |
| Verificación | Probar el arranque desde el mando normal; medir ausencia de tensión en bornes; manómetro en cero |
| Liberación | Zona despejada; protecciones colocadas; personal avisado; cada uno retira su candado |
| Firma del responsable y fecha de revisión | |

Errores frecuentes: bloquear solo el mando (el pulsador o la orden del PLC no son un dispositivo de aislamiento); usar un solo candado para todo el grupo; olvidar la energía acumulada; no verificar antes de empezar; arrancar sin avisar a quienes trabajaban en la máquina.
