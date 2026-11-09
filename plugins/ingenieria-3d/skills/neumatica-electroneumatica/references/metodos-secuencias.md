# Métodos para secuencias de cilindros

Leer este archivo al resolver una secuencia con cascada, paso a paso, relés o GRAFCET, o al revisar por qué un circuito se traba. Notación: A+ = A sale, A− = A entra; a0 = captador de A adentro, a1 = A afuera; /x = contacto NC o señal negada.

## 1. Señales en conflicto (método intuitivo)

En el método intuitivo cada movimiento lo manda el captador del final del movimiento anterior. Con válvulas biestables, hay conflicto cuando, al tener que mandar un movimiento, sigue activa la señal del movimiento contrario del mismo cilindro: la válvula recibe los dos pilotajes y queda donde estaba.

`python scripts/neumatica.py cascada "<secuencia>"` revisa todos los movimientos y marca:
- **CONFLICTO**: señal que sigue activa y bloquea la válvula.
- **AMBIGÜEDAD**: un mismo captador mandaría dos movimientos distintos (pasa cuando un cilindro se mueve más de una vez por ciclo).

Secuencias sin conflicto, como A+ B+ A− B− o A+ B+ C+ A− B− C−, se resuelven conectando cada captador al pilotaje del movimiento siguiente. Con conflicto (A+ B+ B− A−, A+ A− B+ B−, A+ B+ C+ C− B− A−) hay que anular la señal que sobra:
- **Rodillo abatible**: da señal en un solo sentido; sirve para casos simples, pero el captador queda un poco antes del final y la señal es corta.
- **Memorias** (cascada o paso a paso): la señal se alimenta solo mientras su grupo o paso está activo. Es la solución general.

## 2. Método cascada: ejemplo de dos grupos

Secuencia A+ B+ B− A−. Grupos I = [A+ B+] y II = [B− A−]: dos líneas y una memoria.

Conexiones (cilindros de doble efecto con válvulas 5/2 biestables de pilotaje neumático; captadores 3/2 NC con rodillo):

| Componente | Conexión |
|---|---|
| Memoria (5/2 biestable) | 1 ← red; 4 → línea I; 2 → línea II; 3 y 5 escapes |
| Pilotaje 14 de la memoria | Marcha · a0: a0 se alimenta de la línea II y su salida alimenta al pulsador de marcha (3/2 NC), que va al 14. También se puede hacer con una válvula Y |
| Pilotaje 12 de la memoria | b1 alimentado por la línea I |
| Válvula de A (5/2 biestable) | 1 ← red; 4 → cámara de avance; 2 → cámara de retroceso; 14 ← línea I (A+); 12 ← b0 alimentado por la línea II (A−) |
| Válvula de B (5/2 biestable) | 14 ← a1 alimentado por la línea I (B+); 12 ← línea II (B−) |

Funcionamiento: en reposo la línea II tiene presión (B adentro; b0 manda A adentro). Marcha con a0 pasa la memoria a la línea I: sale A; a1 manda B+; b1 pasa a la línea II: entra B; b0 manda A−; con a0 queda listo para otro ciclo. Cada captador se queda sin aire cuando su línea se descarga, así que ninguna señal queda permanente.

## 3. Cascada con más grupos y unión de extremos

A+ A− B+ B− da tres grupos: I = [A+], II = [A− B+], III = [B−]; dos memorias. Cambios: a1 (línea I) → línea II; b1 (línea II) → línea III; Marcha · b0 (línea III) → línea I. Mandos: A+ directo de I, A− directo de II, B+ con a0 alimentado por II, B− directo de III.

Como el último grupo ([B−]) y el primero ([A+]) no comparten cilindros, se pueden unir (`--unir-extremos`): I = [B− A+], II = [A− B+], una sola memoria. El ciclo arranca dentro del grupo I: en reposo la línea I tiene presión (B adentro) y A+ sale con Marcha · b0 alimentado por la línea I; a1 (línea I) activa la II y b1 (línea II) vuelve a la I, ya sin Marcha.

Con tres grupos o más, las memorias se encadenan en serie para que solo una línea tenga presión. Si en un cambio de grupo conmutan dos memorias a la vez, puede aparecer un pulso breve en una línea que no corresponde. Conviene partir del esquema de cascada de la cátedra o de un ejemplo de FluidSIM y comprobar en la simulación, mirando la presión de cada línea, que en cada cambio se active solo la línea siguiente.

## 4. Método paso a paso

- Un **paso** por grupo (o por movimiento) y una memoria por paso (en neumática, módulos de paso o válvulas 3/2 biestables).
- La memoria del paso k se activa con la salida del paso k − 1 y el captador que cierra ese paso, y se borra con la salida del paso k + 1. Su salida manda los movimientos del paso y alimenta los captadores que habilitan el paso siguiente.
- Hacen falta al menos tres pasos: con dos, el paso anterior y el siguiente son la misma memoria y llegarían a la vez la orden de activar y la de borrar.
- Ventaja frente a la cascada: cada paso es igual al anterior, así que ampliar la secuencia es agregar módulos. Desventaja: más válvulas.

## 5. Electroneumática con relés

**Cascada eléctrica, A+ B+ B− A−, válvulas 5/2 biestables** (Y1 = A+, Y2 = A−, Y3 = B+, Y4 = B−), S0 paro (NC), S1 marcha (NA):

```
K1:  +24V --[S0]--+--[S1]--[a0]--+--[/b1]--( K1 )      grupo I activo
                  +-----[K1]-----+
Y1:  +24V --[K1]------------------------( Y1 )   A+
Y3:  +24V --[K1]--[a1]------------------( Y3 )   B+
Y4:  +24V --[/K1]-----------------------( Y4 )   B-
Y2:  +24V --[/K1]--[b0]-----------------( Y2 )   A-
```

Nunca quedan energizadas las dos bobinas de una misma válvula: Y1 y Y2 dependen de K1 y /K1, igual que Y3 y Y4.

**Paso a paso eléctrico, la misma secuencia, válvulas 5/2 monoestables** (Y1 saca A, Y2 saca B; sin tensión los cilindros entran):

```
K1:  --+--[S1]--[a0]--[b0]--+--[/K2]--( K1 )   paso 1: A+
       +--------[K1]--------+
K2:  --+--[K1]--[a1]--+--[/K3]--( K2 )         paso 2: B+
       +-----[K2]-----+
K3:  --+--[K2]--[b1]--+--[/K4]--( K3 )         paso 3: B-
       +-----[K3]-----+
K4:  --+--[K3]--[b0]--+--[/a0]--( K4 )         paso 4: A-
       +-----[K4]-----+
Y1:  --+--[K1]--+--( Y1 )                      A afuera en los pasos 1, 2 y 3
       +--[K2]--+
       +--[K3]--+
Y2:  --[K2]--( Y2 )                            B afuera solo en el paso 2
```

- Con monoestables, la bobina queda energizada todo el tiempo que el cilindro debe estar afuera; por eso Y1 suma los pasos 1 a 3.
- Paro de emergencia (NC) en la alimentación común: caen todos los relés; con monoestables los cilindros vuelven a reposo, con biestables quedan donde estaban. Elegir según qué sea seguro para la máquina.
- Ciclo continuo: un selector en paralelo con S1; al terminar el ciclo (a0 · b0) arranca otro. Paro al final del ciclo: un relé que corta esa rama hasta la próxima marcha.

## 6. GRAFCET y PLC

GRAFCET de A+ B+ B− A− (IEC 60848:2013):

| Etapa | Acción | Receptividad para pasar a la siguiente |
|---|---|---|
| 0 (inicial, doble cuadro) | — | Marcha · a0 · b0 |
| 1 | A+ (Y1) | a1 |
| 2 | B+ (Y3) | b1 |
| 3 | B− (Y4) | b0 |
| 4 | A− (Y2) | a0 → vuelve a la etapa 0 |

Paso al PLC con una marca por etapa (texto estructurado, IEC 61131-3). Primero se calculan todas las transiciones con el estado de las etapas al empezar el ciclo del PLC y después se actualizan las etapas; así no se franquean dos transiciones seguidas en un mismo ciclo y, si una etapa se activa y se desactiva a la vez, queda activa:

```
IF PrimerCiclo THEN                      (* bit de primer ciclo del PLC *)
  X0 := TRUE; X1 := FALSE; X2 := FALSE; X3 := FALSE; X4 := FALSE;
ELSE
  T01 := X0 AND Marcha AND a0 AND b0;    (* 1) transiciones *)
  T12 := X1 AND a1;
  T23 := X2 AND b1;
  T34 := X3 AND b0;
  T40 := X4 AND a0;
  X0 := (X0 AND NOT T01) OR T40;         (* 2) etapas *)
  X1 := (X1 AND NOT T12) OR T01;
  X2 := (X2 AND NOT T23) OR T12;
  X3 := (X3 AND NOT T34) OR T23;
  X4 := (X4 AND NOT T40) OR T34;
END_IF;
YA := X1 OR X2 OR X3;                    (* válvulas monoestables *)
YB := X2;
```

- Con biestables, cada etapa da su bobina: Y1 := X1; Y3 := X2; Y4 := X3; Y2 := X4.
- Para programarlo en una plataforma concreta (TIA Portal, CODESYS: bit de primer ciclo, tipos de datos, entradas y salidas), usar el plugin **automatizacion-industrial**.
