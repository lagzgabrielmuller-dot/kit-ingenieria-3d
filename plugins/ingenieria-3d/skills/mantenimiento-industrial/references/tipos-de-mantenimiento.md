# Tipos de mantenimiento, TPM y RCM

Leer cuando haya que elegir o justificar la estrategia de mantenimiento de un equipo, explicar qué es el TPM o el RCM, o armar el marco teórico de un trabajo de mantenimiento.

## Clasificación

La terminología europea está en **EN 13306:2017**, *Maintenance — Maintenance terminology* (cláusula 7, «Tipos de mantenimiento»; en castellano, UNE-EN 13306). Divide el mantenimiento en dos grandes ramas (definiciones exactas: verificar en la norma vigente):

- **Preventivo**: se hace antes de la falla, para bajar la probabilidad de que ocurra. Puede ser **predeterminado** (a intervalos fijos de tiempo o de uso, sin mirar el estado) o **basado en la condición** (se mide el estado y se actúa según lo que se mide). El **predictivo** es mantenimiento basado en la condición que, además, proyecta la evolución de la variable para anticipar cuándo intervenir.
- **Correctivo**: se hace después de la falla, para devolver el equipo a su función. Puede ser **inmediato** o **diferido** (se programa para más adelante).

Ficha de la norma: [EN 13306:2017 en EVS](https://www.evs.ee/en/evs-en-13306-2017).

## Cuándo conviene cada uno

| Estrategia | Conviene cuando | No conviene cuando | Ejemplos |
|---|---|---|---|
| Correctivo planificado (dejar que falle) | La falla no afecta la seguridad ni el ambiente, es barata de reparar o hay equipo de reserva | La falla para la producción, daña otros componentes o es peligrosa | Lámparas, motores chicos con repuesto en el pañol |
| Preventivo por tiempo o uso | La falla depende de la edad o del uso (desgaste, envejecimiento de la grasa, fatiga con vida conocida) y la tarea cuesta menos que la falla | La falla es aleatoria: cambiar por edad no la evita y puede agregar fallas por la intervención | Lubricación, cambio de juntas, correas, filtros |
| Predictivo o por condición | La falla da señales medibles (vibración, temperatura, ruido, aceite) con tiempo suficiente para planificar | No hay variable que avise o el intervalo entre la señal y la falla es muy corto | Rodamientos, alineación, tableros (termografía) |
| Mejora o rediseño | Ninguna tarea periódica evita la falla y sus consecuencias son graves | La falla es rara y barata | Cambio de material, de diseño o de condición de uso |

**Intervalo P-F.** Entre el momento en que una falla se puede detectar (falla potencial P) y el momento en que el equipo pierde su función (falla funcional F) pasa un tiempo: la inspección por condición tiene que hacerse con una frecuencia bastante menor que ese intervalo, o la falla aparece entre dos inspecciones. El valor del intervalo depende del modo de falla y de la técnica de medición (verificar en la bibliografía de RCM para cada caso).

**Dato que cambió la práctica** (F. S. Nowlan y H. F. Heap, *Reliability-Centered Maintenance*, United Airlines para el Departamento de Defensa de EE. UU., 29/12/1978, sección 2.8, exhibit 2.13; [PDF en DTIC](https://apps.dtic.mil/sti/pdfs/ADA066579.pdf)): de los componentes de aviones estudiados, solo el 4 % mostró la curva de la bañera y el 6 % tenía un desgaste marcado; otro 5 % no tenía una zona de desgaste definida y el 89 % no tenía zona de desgaste. Concluyen que, salvo que haya un modo de falla dominante, un límite de edad hace poco o nada para mejorar la confiabilidad de un ítem complejo, y que una recorrida programada puede aumentar la tasa de fallas por la mortalidad infantil que introduce. Por eso el preventivo por tiempo se justifica para el desgaste y, para el resto, conviene el mantenimiento por condición o el rediseño.

## TPM (mantenimiento productivo total)

Sistema de gestión desarrollado en Japón: Seiichi Nakajima, en el Japan Institute of Plant Maintenance (JIPM), lideró a comienzos de los años setenta la introducción del TPM, del OEE y de las seis grandes pérdidas ([oee.com, World-Class OEE](https://oee.com/world-class-oee)). Su libro es *Introduction to TPM* (1984; en inglés, Productivity Press, 1988).

Pilares, sobre la base de las 5S ([leanproduction.com, TPM](https://www.leanproduction.com/tpm/)):

| Pilar | Qué hace |
|---|---|
| Mantenimiento autónomo | Los operadores hacen la limpieza, la lubricación y la inspección de rutina de su máquina |
| Mantenimiento planificado | Las tareas se programan según las tasas de falla previstas o medidas |
| Mantenimiento de calidad | Se incorporan al proceso la detección y la prevención de errores |
| Mejora enfocada | Grupos chicos hacen mejoras continuas en el funcionamiento del equipo |
| Gestión temprana de equipos | Lo aprendido en el mantenimiento se usa para diseñar los equipos nuevos |
| Capacitación | Se cubren las faltas de conocimiento para lograr los objetivos del TPM |
| Seguridad, salud y ambiente | Lugar de trabajo seguro y sano |
| TPM en la administración | Las técnicas del TPM se aplican a las tareas administrativas |

**5S**: clasificar (sacar lo que no hace falta), ordenar, limpiar e inspeccionar, estandarizar y sostener (misma fuente).

**Seis grandes pérdidas** y su factor del OEE ([oee.com, Six Big Losses](https://www.oee.com/oee-six-big-losses/)):

| Pérdida | Factor del OEE | Ejemplos |
|---|---|---|
| Fallas del equipo | Disponibilidad | Roturas, mantenimiento no planificado, falta de material u operador |
| Preparación y ajustes | Disponibilidad | Cambios de formato, ajustes, limpieza, calentamiento, mantenimiento planificado en horario de producción |
| Paradas menores y marcha en vacío | Rendimiento | Atascos, sensores sucios o desalineados, alimentación defectuosa |
| Velocidad reducida | Rendimiento | Equipo sucio o gastado, mala lubricación, operador sin experiencia |
| Defectos del proceso | Calidad | Ajustes incorrectos, errores de manipulación |
| Rendimiento reducido en el arranque | Calidad | Descarte hasta estabilizar después de un arranque o un cambio |

El cálculo del OEE está en [indicadores.md](indicadores.md).

## RCM (mantenimiento centrado en la confiabilidad)

Método para decidir, modo de falla por modo de falla, qué tarea conviene según las consecuencias de la falla. Nació con el informe de Nowlan y Heap (1978). Los criterios para decir que un proceso es RCM están en **SAE JA1011** (*Evaluation Criteria for Reliability-Centered Maintenance (RCM) Processes*, agosto de 1999), que exige responder siete preguntas ([ReliaSoft, RCM](https://help.reliasoft.com/articles/content/basics/rcm.htm)):

1. ¿Cuáles son las funciones del activo y los estándares de desempeño deseados en su contexto operativo actual? (funciones)
2. ¿De qué maneras puede dejar de cumplir sus funciones? (fallas funcionales)
3. ¿Qué causa cada falla funcional? (modos de falla)
4. ¿Qué pasa cuando ocurre cada falla? (efectos)
5. ¿De qué manera importa cada falla? (consecuencias)
6. ¿Qué se puede hacer para predecir o prevenir cada falla? (tareas proactivas y sus intervalos)
7. ¿Qué hacer si no se encuentra una tarea proactiva adecuada? (acciones por defecto: rediseño, búsqueda de fallas ocultas o dejar que falle)

Las preguntas 2 a 4 son las del AMFE ([analisis-de-fallas.md](analisis-de-fallas.md)); las 5 a 7 deciden la estrategia de la tabla de arriba.

## Cómo justificarlo en un trabajo

1. Criticidad del equipo: qué pasa si falla (seguridad, ambiente, producción, calidad, costo).
2. Modos de falla principales (AMFE) y si avisan antes de fallar.
3. Estrategia por modo de falla con su justificación (tabla de arriba), tarea, frecuencia y fuente de la frecuencia.
4. Indicadores para medir el resultado (MTBF, disponibilidad, OEE, costo) antes y después.
