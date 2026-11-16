# Capacidad, balanceo, layout y planificación

Leer para resolver a mano, armar los archivos del script o justificar el layout. Las cuentas las hacen los comandos `capacidad`, `balanceo` y `cpm` de `scripts/organizacion.py`.

## Capacidad

- **Capacidad de diseño**: lo que produce la estación en el tiempo disponible, sin pérdidas: C = m·T/t.
- **Capacidad efectiva**: descontando paradas planificadas, cambios de herramienta y mantenimiento. En el script es `--rendimiento η`, con C = m·T·η/t. Las pérdidas reales se miden con el OEE de **mantenimiento-industrial**.
- **Eficiencia** = producción real/capacidad efectiva (CENEVAL, Formulario EGEL Plus IINDU, 2021, p. 32). **Utilización** = Q·t/(m·T): la fracción del tiempo disponible que se usa.
- **Cuello de botella**: la estación de menor capacidad. Mejorar cualquier otra no aumenta la producción. Si se lo agranda, el cuello pasa a la estación siguiente, y el script la informa.
- Para llevar la capacidad a la demanda: horas extra o un segundo turno en el cuello, una máquina más, un método mejor en el cuello (estudio de métodos) o tercerizar esa operación.

## Balanceo de línea

1. Armar la tabla de tareas con tiempo y precedentes, y el diagrama de precedencias.
2. Tiempo de ciclo: C = T/D, con T el tiempo productivo del período y D las unidades pedidas. Si una tarea dura más que C, hay que dividirla o poner estaciones en paralelo.
3. Estaciones mínimas: Nt = ⌈Σt/C⌉.
4. Asignar con una regla de prioridad y desempatar con otra:
   - más tareas sucesoras (todas las que dependen de ella, directa o indirectamente);
   - mayor peso posicional (su tiempo más el de todas sus sucesoras);
   - mayor tiempo.
5. Calcular la eficiencia E = Σt/(N·C), el retraso del balance 1 − E y el tiempo ocioso N·C − Σt por ciclo. Si N > Nt, probar otra regla. A veces las precedencias impiden llegar a Nt, como en el ejemplo del SKILL.md.

Archivo de tareas (lo da `balanceo --ejemplo`):

```
tarea,tiempo,precedentes,descripcion
A,40,,corte de perfiles
B,30,A,agujereado
E,35,B C,punteado
```

Los precedentes se separan con espacios, o con coma si el CSV va separado por punto y coma (como lo guarda una planilla en castellano, con coma decimal). En JSON: `[{"tarea": "A", "tiempo": 40, "precedentes": []}, ...]`.

## Distribución en planta

| Tipo | Ventajas | Desventajas |
|---|---|---|
| Por posición fija | el producto no se mueve; sirve para piezas únicas o enormes | mucho traslado de personas y equipos; poco espacio de trabajo |
| Por proceso (funcional) | flexible; una máquina parada no frena todo | recorridos largos, más stock en proceso y más control |
| Por producto (en línea) | recorrido corto, poco stock, fácil de controlar | rígida; una parada frena la línea; hay que balancearla |
| Celular | recorrido corto con algo de flexibilidad | hay que agrupar las piezas en familias; máquinas repetidas |

Método SLP (R. Muther, *Systematic Layout Planning*, Cahners Books, ed. de 1984):
1. Datos: productos, cantidades, recorridos, servicios y tiempos (análisis producto-cantidad).
2. Recorrido de los materiales: cursograma, diagrama de recorrido y tabla de doble entrada con los flujos entre sectores.
3. Tabla relacional entre sectores, con el motivo de cada calificación:

| Código | Proximidad |
|---|---|
| A | absolutamente necesaria |
| E | especialmente importante |
| I | importante |
| O | normal |
| U | sin importancia |
| X | no deseable |

Fuente de los códigos: CENEVAL, Formulario EGEL Plus IINDU (2021), p. 49.

4. Diagrama relacional, superficie necesaria y disponible, y alternativas de bloques.
5. Evaluación de las alternativas con la carga-distancia Σ fij·dij, donde fij son los viajes (o los kg) entre los sectores i y j, y dij la distancia en m entre sus centros. Gana la menor, pero también pesan la seguridad, las ampliaciones y los servicios.

Pasillos, salidas y protecciones van según **higiene-y-seguridad**, y los planos, según **planos-tecnicos**.

## CPM y PERT paso a paso

1. Hacer la lista de actividades con su duración (o los tiempos a, m y b) y sus precedentes inmediatos.
2. Ida: IT = máx(FT de las precedentes), 0 al comienzo; FT = IT + d.
3. Duración del proyecto: T = máx FT.
4. Vuelta: FR = mín(IR de las siguientes), T al final; IR = FR − d.
5. HT = IR − IT = FR − FT; HL = mín(IT de las siguientes) − FT. Las críticas son las de HT = 0.
6. PERT: te y σ² de cada actividad, y σ del proyecto con el camino crítico; P = Φ(z). Supone caminos independientes y toma uno solo: si hay caminos casi críticos, la probabilidad real de cumplir es menor.
7. Gantt: barras desde el IT, con las críticas marcadas y la holgura a continuación. Se usan las fechas tempranas, salvo que convenga atrasar actividades con holgura para nivelar recursos (gente, grúa, soldadora).

Origen: PERT, Malcolm, Roseboom, Clark y Fazar (1959), «Application of a Technique for Research and Development Program Evaluation», *Operations Research* 7(5), 646–669, para el programa Polaris de la Marina de EE. UU. CPM, Kelley y Walker en DuPont (Kelley, Walker y Sayer, 1989, «The Origins of CPM: a personal history»). La fórmula de te también está en H. Kerzner, *Project Management*, 10.ª ed., Wiley, 2009.

Archivo de actividades (lo da `cpm --ejemplo`):

```
actividad,a,m,b,precedentes,descripcion
A,2,4,6,,relevamiento y proyecto
B,6,9,18,A,compra de la máquina
E,2,3,4,B C,montaje mecánico
```

Con una sola duración por actividad, la columna es `duracion` (o `tiempo`). En JSON: `[{"actividad": "A", "duracion": 4, "precedentes": []}, ...]`. Para el informe, el Gantt se rehace en una planilla o en un programa de proyectos libre (GanttProject, ProjectLibre).
