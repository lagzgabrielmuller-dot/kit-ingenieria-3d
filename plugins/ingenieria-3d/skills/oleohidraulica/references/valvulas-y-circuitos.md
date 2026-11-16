# Válvulas, circuitos, símbolos y seguridad

Leer este archivo al armar, dibujar o leer un circuito hidráulico (por ejemplo el de una prensa), al elegir válvulas o al revisar la seguridad de una instalación.

## Símbolos y vías

- Símbolos: **ISO 1219-1:2012** con Amd 1:2016, los mismos para neumática e hidráulica ([iso.org](https://www.iso.org/standard/60184.html)); reglas para dibujar el esquema: **ISO 1219-2:2012** ([iso.org](https://www.iso.org/standard/51200.html)). Cómo se leen las posiciones (cuadrados), las flechas y las vías bloqueadas está en **neumatica-electroneumatica**: es igual.
- Diferencia a la vista: los triángulos de energía son llenos (negros) en hidráulica y vacíos en neumática (Andrew Parr, *Hydraulics and Pneumatics*, Butterworth-Heinemann, 2011, [O'Reilly](https://www.oreilly.com/library/view/hydraulics-and-pneumatics/9780080966755/B978008096674800015X.xhtml)). En hidráulica cada retorno termina en el símbolo del tanque; en neumática el escape va a la atmósfera.
- Vías con letras: P (presión, de la bomba), T (tanque), A y B (utilización) y L (fuga o drenaje); STAUFF las da como designaciones estándar ([STAUFF, 19-08-2025](https://stauff.co.uk/en/blog/products/correctly-reading-circuit-symbols-according-to-din-iso-1219)). En las válvulas pilotadas, X es la alimentación externa del pilotaje e Y su retorno al tanque (Rexroth, [RE 24751-XE/04.16](https://www.pneu-hyd.co.th/images/Products/rexroth-thailand/industrial-hydraulic/on-off-valves/directional-valves/directional-spool-valves/pilot-operated/re24751-XE_2016-04.pdf)). En las bombas de pistones, L es la conexión de drenaje de la carcasa (la A10VSO mide ahí la temperatura).
- La identificación de vías de válvulas hidráulicas es tema de **ISO 9461:1992**, confirmada en 2024 y con revisión prevista ([iso.org](https://www.iso.org/standard/17190.html)); las letras exactas que fija: verificar en la norma vigente. La numeración 1, 2, 4, 3, 5 de ISO 11727 es de neumática.
- Para dibujar el esquema en un plano: **planos-tecnicos**. Para simular: FluidSIM (versión de hidráulica) o Automation Studio, como pida la cátedra.

## Componentes

| Componente | Qué hace | A tener en cuenta |
|---|---|---|
| Bomba de caudal fijo | Da un caudal proporcional a la velocidad | Necesita una válvula de alivio: el caudal sale por algún lado |
| Bomba de caudal variable | Ajusta la cilindrada (por ejemplo, compensada por presión) | Menos calor cuando el cilindro está parado a presión |
| Motor hidráulico | Convierte caudal y presión en velocidad y torque | Drenaje de carcasa si el catálogo lo pide |
| Cilindro diferencial (doble efecto, vástago simple) | Avanza con A1 y retrocede con A3 | Relación φ, intensificación, pandeo |
| Válvula de alivio (limitadora de presión) | Normalmente cerrada; abre a tanque cuando la entrada llega al ajuste | Fija la presión máxima; mientras descarga, la potencia del caudal que pasa (Δp · Q / 600) se vuelve calor |
| Reductora de presión | Normalmente abierta; mantiene una presión menor a la salida | Para una rama que necesita menos fuerza (por ejemplo, una sujeción) |
| Válvula de secuencia | Normalmente cerrada; habilita otra rama cuando la entrada llega al ajuste | Drenaje externo; se ajusta por encima de la presión que necesita el primer movimiento |
| Contrabalance | Normalmente cerrada, con antirretorno en paralelo; sostiene la carga y evita que se adelante | Ajuste y relación de pilotaje: ver abajo |
| Antirretorno | Deja pasar en un solo sentido | Con resorte, tiene una presión de apertura |
| Antirretorno pilotado (desbloqueable) | Bloquea sin fugas; se abre con presión de pilotaje | Para sostener una carga; con carga que tira, conviene contrabalance |
| Estrangulador | Regula caudal con una restricción | El caudal cambia con la carga (Δp) y con la temperatura (viscosidad) |
| Reguladora de caudal compensada | Mantiene el caudal aunque cambie la carga | Con antirretorno para regular en un solo sentido |
| Distribuidora 4/2 o 4/3 | Dirige P y T hacia A y B | En las de 3 posiciones manda el centro |
| Acumulador, filtro, intercambiador, presostato, manómetro | Energía, limpieza, temperatura y señal o lectura de presión | Ver [bombas-acumuladores-tanque.md](bombas-acumuladores-tanque.md) |

Centros más usados de una 4/3:

| Centro | Conexiones en reposo | Uso |
|---|---|---|
| Cerrado | P, T, A y B bloqueadas | El cilindro queda quieto; la bomba de caudal fijo descarga por la de alivio (calor) |
| Tándem | P con T; A y B bloqueadas | Descarga la bomba a baja presión y deja quieto el cilindro: muy usado con bomba de caudal fijo |
| Abierto | Todas unidas | Bomba descargada y cilindro libre |
| Flotante | A y B con T; P bloqueada | Cilindro libre, por ejemplo para que la carga apoye |

## Regulación de velocidad

- **A la entrada** (meter-in): se estrangula el aceite que entra; sirve con cargas que se oponen al movimiento.
- **A la salida** (meter-out): se estrangula el que sale; frena cargas que tiran (verticales o que se adelantan). En un cilindro diferencial, al estrangular la salida del lado del vástago la presión ahí sube: p3 = (p · A1 − F) / A3, y sin carga p3 = p · φ. En la prensa del ejemplo (φ = 1,96 a 160 bar) serían 313,7 bar, más que los 275 bar de la manguera DN 12 2SN: hace falta otra manguera, una válvula de seguridad en esa cámara o regular de otra forma.
- **En derivación** (bleed-off): se manda parte del caudal a tanque; calienta menos, pero es menos preciso.
- En los tres casos el caudal que pasa por la restricción genera calor: P = Δp · Q / 600 [kW].

## Cómo leer un circuito

1. Ubicar la bomba, la válvula de alivio y el tanque: la presión máxima es el ajuste de la de alivio.
2. Identificar cada actuador con su válvula. El esquema se dibuja en reposo, con las líneas conectadas a la posición central o de reposo.
3. Para cada posición de la válvula, seguir el aceite: P → A o B → cámara del actuador → la otra cámara → T.
4. Ver qué sostiene la carga en reposo (centro, antirretorno pilotado, contrabalance) y qué pasa si se corta la energía.
5. Armar una tabla por fase: posición de cada válvula, recorrido del aceite, presión, movimiento y señal que termina la fase (final de carrera, presostato, tiempo).
6. Revisar caudales (Q · φ en el retorno) y presiones (intensificación) de cada línea, y dónde se genera calor.

## Circuitos típicos

### Prensa vertical

Componentes habituales: tanque con nivel y termómetro, filtro de aspiración, bomba y motor eléctrico, válvula de alivio con manómetro, distribuidora 4/3 de centro tándem con solenoides, contrabalance (o antirretorno pilotado) en la línea del lado del vástago para sostener el puente, presostato que avisa que se llegó a la fuerza, acumulador opcional con su bloque de seguridad y descarga, filtro de retorno e intercambiador si hace falta.

| Fase | Válvula | Qué pasa |
|---|---|---|
| Reposo | Centro tándem | La bomba descarga a baja presión; la contrabalance sostiene el puente |
| Bajada | P → A, B → T | El puente baja; la contrabalance frena la salida del lado del vástago |
| Prensado | P → A | Al tocar la pieza la presión sube hasta la necesaria (131,4 bar para 10 t en el ejemplo); el presostato da la señal |
| Mantenimiento | Centro tándem, con acumulador | El acumulador repone las fugas y la bomba no calienta el aceite contra la de alivio |
| Descompresión | Breve, controlada | Bajar la presión de la cámara antes de invertir evita el golpe de la energía guardada en el aceite y las mangueras |
| Subida | P → B, A → T | Vuelve Q · φ por la línea A (51,3 L/min en el ejemplo) |

### Regenerativo

- El aceite que sale del lado del vástago se suma al de la bomba en el lado del émbolo: v = Q / Av y F = p · Av · η. Con un cilindro 2:1 la regeneración da en el avance la misma velocidad y la misma fuerza que en el retroceso; cuando la carga hace subir la presión, una válvula de secuencia manda el aceite del lado del vástago a tanque y el cilindro sigue con toda la fuerza a la mitad de la velocidad ([Power & Motion, H&P Book 2, cap. 17, 15-01-2010](https://www.powermotiontech.com/other-technologies/book-2-chapter-17-regeneration-circuits?page=2)).
- En la prensa del ejemplo (100/70, 26,17 L/min): acercamiento a 0,113 m/s en lugar de 0,056 m/s, pero con 58,5 kN como máximo a 160 bar; para las 10 t tiene que pasar a conexión normal.

### Contrabalance

- Sostiene la carga y evita que baje sola o que se adelante a la bomba. Sun Hydraulics indica ajustarla al menos a 1,3 veces la presión máxima que genera la carga, y aclara que la contrapresión en la conexión 2 se suma al ajuste efectivo multiplicada por (1 + relación de pilotaje); su CBCH tiene relación 10:1 ([hoja de la CBCH](https://paro.nl/library//storage/datasheets/Sun/Cartridges/Sun_CBCH.pdf/datasheet.html)).
- Presión que genera la carga: p = m · g / A del lado que la sostiene. Ejemplo: un puente de 500 kg colgado del lado del vástago de un 100/70 da 4903 N / 4006 mm² = 12,2 bar → ajuste mínimo 15,9 bar.
- Cuánto pilotaje hace falta para abrirla depende del modelo y de su relación de pilotaje: tomarlo de la hoja de la válvula.

### Secuencia

- Primero sujetar y después prensar: la válvula de secuencia deja pasar aceite al segundo cilindro recién cuando el primero llegó a su presión de ajuste.
- Se ajusta por encima de la presión que necesita el primer movimiento y por debajo de la de alivio, con el margen que dé el catálogo de la válvula.
- La alternativa electrohidráulica (presostato o final de carrera y relés o PLC) es más fácil de cambiar; la lógica de secuencias, relés y GRAFCET es la de **neumatica-electroneumatica**.

## Seguridad

- Reglas generales y requisitos de seguridad de sistemas hidráulicos: **ISO 4413:2010** ([iso.org](https://www.iso.org/standard/44781.html)).
- Inyección de aceite: el fluido puede penetrar la piel con presiones de apenas 2,07 bar (30 psi); nunca buscar pérdidas con la mano (usar un cartón o una madera) y tratar cualquier inyección como una emergencia médica ([IFPS, 17-06-2026](https://ifps.org/fluid-injection-injuries-fluid-power-safety-tips-training-and-ifps-resources)).
- Energía guardada: el acumulador mantiene la presión con la bomba parada, y un antirretorno pilotado o una contrabalance dejan presión atrapada en el cilindro. Antes de aflojar un racor: calzar o trabar la carga, descargar el acumulador y el circuito, y verificar presión cero con el manómetro.
- Mangueras y racores con presión de trabajo mayor que la máxima de la línea (alivio o intensificación); una manguera que se suelta con presión latiguea.
- El aceite caliente quema; los derrames resbalan y contaminan.
- Reglamentación argentina de higiene y seguridad: **normas-tecnicas-ar**.
