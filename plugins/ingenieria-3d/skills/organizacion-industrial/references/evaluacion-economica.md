# Evaluación económica: costos, flujo de fondos, inflación y tasa

Leer al armar el estudio económico del proyecto final o un trabajo de costos. Las cuentas las hacen los comandos `equilibrio`, `amortizacion`, `van` e `inflacion` de `scripts/organizacion.py`.

## Costos

- Hay costos fijos, variables y semivariables. Los semivariables tienen una parte fija y otra variable, como la energía con cargo fijo más consumo, y se separan en sus dos partes.
- Los costos indirectos se reparten con una base (horas máquina, horas hombre, m², unidades). La base elegida se dice en el informe.
- Costo unitario: cu = cv + CF/Q. Baja con la cantidad, porque el costo fijo se reparte entre más unidades.
- Con varios productos se usa el margen de contribución ponderado: mc̄ = Σ wi·mci, con wi la participación de cada producto en las unidades vendidas. Qe total = CF/mc̄, repartido según la mezcla.

| Rubro típico de un proyecto final | Clase | De dónde sale |
|---|---|---|
| Materia prima e insumos | variable, directo | cotización con fecha y proveedor |
| Energía eléctrica de proceso | variable | potencia · horas · tarifa de la distribuidora |
| Mano de obra directa | fijo o variable, según cómo se pague | convenio colectivo vigente (verificar) |
| Mantenimiento | fijo o semivariable | plan de **mantenimiento-industrial** |
| Amortizaciones | fijo, no desembolsable | comando `amortizacion` |
| Seguros, alquiler, administración | fijo, indirecto | cotización |

Los precios van sin IVA si la empresa es responsable inscripta, porque el IVA de las compras se descuenta del de las ventas (verificar el caso con un contador).

## Estructura del flujo de fondos

| Renglón | Año 0 | Años 1 a n |
|---|---|---|
| + Ingresos por ventas | | Q·p |
| − Costos desembolsables (variables y fijos) | | C |
| − Amortizaciones (no son salida de caja) | | A |
| = Utilidad antes de impuestos | | I − C − A |
| − Impuesto a las ganancias | | t·(I − C − A) |
| = Utilidad neta | | |
| + Amortizaciones (se vuelven a sumar) | | A |
| − Inversión fija (equipos, obra, instalación) | I0 | reposiciones |
| − Capital de trabajo (materiales en stock, crédito a clientes) | CT | aumentos |
| + Valor residual y recupero del capital de trabajo | | último año |
| = Flujo neto | FF0 | FFt |

- Si al final el equipo se vende a VM y su valor de libro es VL, entra VM − t·(VM − VL). En el ejemplo del SKILL.md, VM = VL = 10 000 USD y no hay impuesto.
- Si la utilidad antes de impuestos sale negativa, el tratamiento del quebranto depende de la ley (verificar en la norma vigente). En un trabajo escolar se aclara el supuesto.
- La alícuota t es la vigente del impuesto a las ganancias para el tipo de empresa (verificar en la norma vigente). En el ejemplo del SKILL.md se supuso 30 %.

## Moneda e inflación

- **Moneda constante** (real): todo a precios de un año base, con tasa real r.
- **Moneda corriente** (nominal): con los precios de cada año, con tasa nominal i.
- Fisher: (1 + i) = (1 + r)·(1 + π), con π la inflación del período. El formulario EGEL Plus IINDU del CENEVAL (2021, p. 38) la usa para la tasa mínima aceptable: TMAR = (1 + i)·(1 + f) − 1, con i el premio al riesgo y f la inflación.
- Con inflación de dos dígitos la resta falla. Con i = 45,6 % y π = 30 %, la tasa real es 12 % y la resta da 15,6 % (`inflacion --nominal 45.6 --inflacion 30`).
- Para pasar flujos corrientes a constantes del año 0 sirven Ct = Ft·IPC0/IPCt (`inflacion --ipc`) o Ct = Ft/Π(1 + πk) (`inflacion --inflaciones`). El IPC lo publica el INDEC.
- En dólares, se usan los precios en dólares (equipos importados, cotizaciones en USD). Se dice qué tipo de cambio y de qué fecha se usó para pasar los costos en pesos. Si los flujos son "USD constantes", la tasa es real en dólares.
- Si la amortización impositiva no se actualiza por inflación, el ahorro de impuesto pierde valor. En ese caso conviene armar el flujo en moneda corriente con tasa nominal (verificar en la norma vigente el ajuste por inflación impositivo).
- Comprobación: si todos los flujos siguen a la inflación, el VAN en moneda corriente con tasa nominal es igual al VAN en moneda constante con tasa real. El demo lo comprueba con el ejemplo del SKILL.md.

## Tasa de descuento

- Es el costo de oportunidad: lo que rendiría el dinero en otra inversión de riesgo parecido. No es la inflación ni la tasa de un plazo fijo, sin más.
- En dólares se construye con supuestos explícitos: tasa libre de riesgo (bono del Tesoro de EE. UU. del plazo del proyecto), más riesgo país (diferencia de tasa de los bonos argentinos en dólares sobre los de EE. UU.), más una prima por el riesgo propio del proyecto. Si hay préstamo, se pondera el costo del capital propio con el de la deuda.
- En un trabajo escolar se usa la tasa que indique la cátedra. Si no indica ninguna, va una tasa supuesta y justificada, con sensibilidad (por ejemplo, el VAN al 8, 12 y 16 %).

## Indicadores y sus trampas

- **VAN**: es el criterio principal. Se puede sumar entre proyectos y dice cuánto se gana por encima de la alternativa.
- **TIR**: puede haber más de una si el flujo cambia varias veces de signo (el script avisa y las lista). Tampoco sirve para comparar proyectos excluyentes de distinto tamaño o duración: para eso, el VAN.
- **Recupero**: mide liquidez y riesgo, no rentabilidad, e ignora lo que pasa después.
- **B/C**: el script calcula VA de los flujos positivos / VA de los negativos. Si solo el año 0 es negativo, da 1 + VAN/I0. Con ingresos y egresos brutos da otro número. En los dos casos B/C > 1 equivale a VAN > 0, pero ninguno de los dos sirve para ordenar proyectos.
- **Sensibilidad**: se recalcula el VAN cambiando una variable por vez (precio, cantidad, costo variable, inversión, tasa) en ±10 y ±20 %. La variable que más lo mueve es la crítica. El precio o la cantidad que hacen VAN = 0 son los de equilibrio del proyecto.

## Presentación

Lleva la tabla del flujo de fondos año por año, los supuestos con su fuente (cotizaciones con fecha, tarifas, alícuotas), los indicadores y la sensibilidad. El formato del capítulo está en **informe-tecnico** y las preguntas típicas de la defensa, en **exposicion-oral**.

Bibliografía de consulta: N. Sapag Chain y otros, *Preparación y evaluación de proyectos*, y G. Baca Urbina, *Evaluación de proyectos*, ambos de McGraw-Hill (verificar la edición que use la cátedra).
