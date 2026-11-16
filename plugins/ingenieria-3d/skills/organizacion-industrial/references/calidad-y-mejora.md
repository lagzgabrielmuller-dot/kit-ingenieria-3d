# Control de calidad y mejora continua

Leer para armar un plan de calidad o interpretar un gráfico de control. Las cuentas las hacen los comandos `calidad` y `pareto` de `scripts/organizacion.py`.

## Pareto e Ishikawa

- **Pareto**: se cuentan los defectos (o las paradas, o los reclamos) por categoría en un período, se ordenan de mayor a menor y se calcula el % acumulado. Las pocas categorías que suman cerca del 80 % son las que se atacan primero. Ejemplo: rebabas 52 y medida fuera de tolerancia 28 suman el 80 % de 100 defectos (`pareto --categorias ... --cantidades 52,28,10,6,4`).
- **Ishikawa** (causa y efecto, o espina de pescado): el efecto va en la cabeza y las causas posibles en espinas agrupadas en mano de obra, máquina, método, material, medición y medio ambiente (6M). Las causas más probables se confirman con datos antes de actuar.

## Gráficos de control X̄-R

1. Tomar subgrupos de n piezas consecutivas (habitualmente 4 o 5) a intervalos regulares. Para fijar los límites se suelen usar unos 20 a 25 subgrupos (verificar).
2. Calcular X̄ y R de cada subgrupo, X̿ y R̄, y los límites: X̄, con X̿ ± A2·R̄; R, con LCS = D4·R̄ y LCI = D3·R̄.
3. Buscar señales. Si hay una con causa asignable que se corrigió, se saca ese subgrupo y se recalculan los límites. Después, los límites quedan fijos para vigilar la producción.
4. Los límites de control salen del proceso y las tolerancias, del plano: no se mezclan.

| n | A2 | D3 | D4 | d2 |
|---|---|---|---|---|
| 2 | 1,880 | 0 | 3,267 | 1,128 |
| 3 | 1,023 | 0 | 2,575 | 1,693 |
| 4 | 0,729 | 0 | 2,282 | 2,059 |
| 5 | 0,577 | 0 | 2,115 | 2,326 |
| 6 | 0,483 | 0 | 2,004 | 2,534 |
| 7 | 0,419 | 0,076 | 1,924 | 2,704 |
| 8 | 0,373 | 0,136 | 1,864 | 2,847 |
| 9 | 0,337 | 0,184 | 1,816 | 2,970 |
| 10 | 0,308 | 0,223 | 1,777 | 3,078 |

Fuente: A2, D3 y D4, NIST/SEMATECH e-Handbook of Statistical Methods, sección 6.3.2.1, donde A2 = 3/(d2·√n), D3 = 1 − 3·d3/d2 (0 si da negativo) y D4 = 1 + 3·d3/d2. El valor d2 es la media del rango de n valores normales en unidades de σ. Se calculó por integración numérica y reproduce los A2 de la tabla; el demo recalcula d2 y d3 y compara los tres factores con la tabla, con una diferencia máxima de 0,0005. Para n = 5 el valor exacto de D4 es 2,1145, por eso hay tablas que dan 2,114 y otras 2,115. La tabla llega a n = 10; para subgrupos más grandes se usa el gráfico X̄-S (verificar).

**Reglas de Western Electric** (NIST/SEMATECH, sección 6.3.2), con zonas a 1, 2 y 3 σ de X̄ desde la línea central:
1. un punto fuera de los límites de 3σ;
2. dos de tres puntos seguidos más allá de 2σ, del mismo lado;
3. cuatro de cinco puntos seguidos más allá de 1σ, del mismo lado;
4. ocho puntos seguidos del mismo lado de la línea central.

El script revisa las cuatro en el gráfico X̄ y la primera en el gráfico R. Cada regla que se agrega suma falsas alarmas (el NIST cita a Champ y Woodall, 1987).

## Capacidad del proceso

- Cp = (LES − LEI)/(6·σ̂) compara el ancho de la tolerancia con la dispersión.
- Cpk = mín[Cpu; Cpl], con Cpu = (LES − X̿)/(3·σ̂) y Cpl = (X̿ − LEI)/(3·σ̂), tiene en cuenta el centrado. Con una sola tolerancia (por ejemplo, solo un máximo), se usa el índice de ese lado.
- σ̂ = R̄/d2 es la dispersión dentro de los subgrupos, la de corto plazo. Pp y Ppk se calculan igual, pero con el desvío s de todas las mediciones, e incluyen los corrimientos entre subgrupos.
- Ejemplo del NIST (sección 6.1.6): LES = 20, LEI = 8, media 16 y σ = 2 dan Cp = 1,0, Cpu = 0,6667, Cpl = 1,3333 y Cpk = 0,6667. El proceso no es bueno y hay que reducir la dispersión o centrarlo.
- Fracción fuera de tolerancia con el proceso centrado y distribución normal: 2·Φ(−3·Cp). Cp = 1 (3σ a cada lado) da 2 700 ppm; Cp = 4/3 (4σ), 63 ppm; Cp = 5/3 (5σ), 0,57 ppm; Cp = 2 (6σ), 0,002 ppm. Con el proceso descentrado, la fracción es mayor (el script la calcula con X̿ y σ̂).
- El mínimo aceptable lo fija el cliente o la norma del producto; suele pedirse Cpk ≥ 1,33 (verificar el requisito). Solo tiene sentido con el proceso bajo control.

## Mejora continua

| S | Japonés | Qué se hace en el taller |
|---|---|---|
| 1 | Seiri (clasificar) | sacar lo que no se usa: tarjeta roja y destino |
| 2 | Seiton (ordenar) | un lugar marcado para cada cosa, cerca de donde se usa |
| 3 | Seisō (limpiar) | limpiar e inspeccionar a la vez máquinas y puestos |
| 4 | Seiketsu (estandarizar) | normas visuales y planillas para mantener las tres primeras |
| 5 | Shitsuke (sostener) | disciplina y auditorías periódicas |

Fuente: H. Hirano, *5 Pillars of the Visual Workplace*, Productivity Press, 1995. También T. Osada, *The 5S's: Five Keys to a Total Quality Environment*, Asian Productivity Organization, 1995.

**Lean.** Los siete desperdicios (muda) de T. Ohno (*Toyota Production System: Beyond Large-Scale Production*, Productivity Press, 1988) son la sobreproducción, las esperas, el transporte, los procesos de más, el inventario, los movimientos y los defectos. Se suman la sobrecarga (muri) y el desparejo (mura). Las herramientas habituales son:
- kaizen (mejoras chicas y continuas, con el ciclo planificar, hacer, verificar y actuar);
- kanban (producir lo que consume el proceso siguiente);
- SMED (cambio rápido de herramienta);
- poka-yoke (dispositivos que impiden el error);
- flujo continuo al ritmo de la demanda (takt time = tiempo disponible/demanda, el mismo C del balanceo).

Las paradas y el OEE se tratan en **mantenimiento-industrial**.
