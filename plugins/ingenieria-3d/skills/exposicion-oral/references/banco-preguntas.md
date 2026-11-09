# Banco de preguntas típicas por tema

Preguntas frecuentes en defensas de trabajos de electromecánica, con la pista para responder. Elegir las que correspondan al trabajo y completar cada respuesta con los datos propios (valor, fuente, diapositiva o página). Formato de la respuesta: frase directa, fundamento y, si suma, límite o mejora; 30 s como máximo.

## Generales del trabajo

- ¿Cuál es el objetivo y el alcance? → Una frase con el objetivo y qué quedó afuera (y por qué).
- ¿De dónde salen los datos de partida? → Consigna, relevamiento, medición, catálogo o norma, con la fecha si son precios o mediciones.
- ¿Cómo verificaron los resultados? → Por otro método, contra un rango típico, con una medición o con el simulador validado.
- ¿Qué cambiarían si tuvieran que hacerlo de nuevo? → Una mejora técnica concreta, no "organizarnos mejor".

## Cálculos y valores adoptados

- ¿Por qué ese valor (coeficiente, factor, margen)? → Fuente (norma, tabla, catálogo, consigna) y criterio; si es un valor de bibliografía, el rango que da y por qué se eligió ese.
- ¿Qué pasa si ese valor cambia un 20 %? → Sentido y orden de magnitud del cambio en el resultado; ¿sigue verificando?
- ¿Qué significa cada término de la fórmula y en qué unidades va? → Recorrerla sin mirar la diapositiva.
- ¿Por qué adoptaron un valor comercial mayor que el calculado? → Nunca se adopta uno menor; se elige el normalizado inmediato superior y se dice el margen.
- ¿Con cuántas cifras trabajaron? → Las cuentas sin redondear; el redondeo, solo en el resultado final.

## Instalaciones eléctricas

- ¿Por qué esa sección de conductor? → Tres criterios en orden: corriente admisible (tabla de la AEA 90364 para esa forma de instalación, con los factores de temperatura y agrupamiento), caída de tensión (límite de la AEA para ese circuito) y cortocircuito (S ≥ I·√t/k). Decir cuál de los tres la definió.
- ¿Por qué ese calibre de protección? → Ib ≤ In ≤ Iz; curva elegida según la corriente de arranque de la carga.
- ¿Para qué el diferencial y por qué de 30 mA? → Protege a las personas: 30 mA es la sensibilidad que da protección adicional contra contactos directos; citar el artículo de la AEA 90364 que lo pide para ese circuito.
- ¿Qué pasa si la caída de tensión es mayor que la admitida? → Los motores tienen menos cupla (proporcional a U²) y, con la misma carga, toman más corriente y se calientan; las lámparas dan menos luz.
- ¿Cómo es la puesta a tierra? → Conductor de protección verde y amarillo hasta la toma de tierra, valor de resistencia medido y el máximo que fija la reglamentación para que actúe la protección.
- ¿Por qué corregir el factor de potencia y cómo? → Menos corriente para la misma potencia activa (menos pérdidas y caída) y sin recargo de la distribuidora; capacitores con Q_c = P·(tg φ1 − tg φ2).

## Motores, máquinas y transmisiones

- ¿Por qué ese motor? → Potencia de la carga dividida por el rendimiento de la transmisión, con factor de servicio; potencia normalizada inmediata superior y su margen; polos según la velocidad (n_s = 60·f/p); protección IP según el ambiente.
- ¿Qué pasa si se corta una fase? → Si está girando, sigue en marcha monofásica, toma más corriente por las otras fases y se calienta; si está parado, no arranca y zumba. Lo protege el guardamotor o el relé térmico con detección de falta de fase.
- ¿Por qué estrella-triángulo, arrancador suave o variador? → Bajan la corriente de arranque; estrella-triángulo la baja a un tercio pero también la cupla, así que sirve si la máquina arranca con poca carga. El variador además regula la velocidad.
- ¿Qué es el deslizamiento y cuánto vale acá? → s = (n_s − n)/n_s; a plena carga, unos pocos por ciento.
- ¿Qué pasa si la carga supera la cupla máxima? → El motor se frena, la corriente sube cerca de la de arranque y tiene que actuar la protección.
- ¿Cómo se invierte el giro? → Intercambiando dos fases.
- ¿Por qué esa transmisión (correa, cadena, reductor)? → Relación i = n1/n2 = d2/d1 = z2/z1, rendimiento, espacio, mantenimiento y costo.

## Transformadores

- ¿Por qué el rendimiento máximo no se da a plena carga? → Se da cuando las pérdidas en el cobre (crecen con x²) igualan a las del hierro (fijas): x = √(P_0/P_cc).
- ¿Qué se obtiene de los ensayos de vacío y de cortocircuito? → Vacío: pérdidas en el hierro, corriente de vacío y relación de transformación. Cortocircuito: pérdidas en el cobre a corriente nominal y tensión de cortocircuito ε_cc.
- ¿Para qué sirve la tensión de cortocircuito? → Limita la corriente de cortocircuito (I_cc = I_n·100/ε_cc) y define la caída de tensión con carga.
- ¿Qué significa Dyn11? → Primario en triángulo, secundario en estrella con neutro accesible y desfasaje de 11 × 30° = 330°; importa para poner transformadores en paralelo.

## Neumática e hidráulica

- ¿Por qué esa presión de trabajo? → La que piden los cilindros y herramientas más las pérdidas de la red; más presión es más energía consumida.
- ¿Por qué la red en anillo? → El aire llega por dos caminos: menos pérdida de carga y presión más pareja en los puntos de consumo.
- ¿Por qué la pendiente y las purgas? → Para que el condensado corra hacia los purgadores (pendiente del orden del 1 %, o la que indique la bibliografía de la materia).
- ¿Por qué las bajadas salen por arriba de la cañería principal? → Para que el agua condensada no baje a las herramientas.
- ¿Cómo eligieron el compresor y el tanque? → Caudal de aire libre con simultaneidad, ampliación prevista y fugas; tanque con V = Q·t·p_0/Δp.
- ¿Por qué ese diámetro? → Pérdida de carga admisible (habitualmente 0,1 bar en la red principal) con la longitud equivalente de los accesorios; la pérdida crece aproximadamente con la quinta potencia de la inversa del diámetro.

## Iluminación

- ¿Por qué ese nivel de iluminación? → Tabla de la IRAM-AADL J 20-06 para la tarea, y el mínimo del Decreto 351/79.
- ¿Qué es el factor de mantenimiento? → La pérdida de flujo por suciedad y envejecimiento (habitual de 0,6 a 0,8).
- ¿Qué pasa si las paredes o el techo son más oscuros? → Baja el coeficiente de utilización y hacen falta más luminarias.
- ¿Por qué esa luminaria? → Flujo, eficacia (lm/W), vida útil, grado de protección y costo; comparación de dos o tres opciones del catálogo.

## Mecánica, estructuras y materiales

- ¿Qué coeficiente de seguridad usaron y contra qué? → Según el tipo de carga (estática, variable, con golpes) y la incertidumbre; aclarar si es contra la fluencia o contra la rotura.
- ¿Qué pasa si la carga se duplica? → En la zona elástica las tensiones se duplican: ¿sigue verificando con ese coeficiente?
- ¿Por qué ese material? → Resistencia, soldabilidad, corrosión, costo y medidas comerciales disponibles.
- ¿Cómo se fabrica y se monta? → Procesos, uniones, tolerancias y secuencia de montaje.

## Ensayos de materiales

- ¿Qué norma rige el ensayo y qué pide? → Probeta, condiciones y criterio de aceptación.
- ¿Qué informa el resultado y para qué se usa? → Propiedad que mide y decisión que permite tomar.
- Doblado: ¿por qué ese diámetro de mandril? → Lo fija la norma o la especificación según el material y el espesor; la fibra exterior se estira ε = a/(D + a).
- Tracción: ¿qué diferencia hay entre el límite de fluencia y la resistencia a la tracción? ¿Qué indica el alargamiento? → Fluencia: comienzo de la deformación permanente; resistencia: tensión máxima convencional; alargamiento: ductilidad.
- Dureza Brinell: ¿por qué se mantiene constante F/D²? → Para que huellas de distinto tamaño sean comparables (semejanza geométrica); la huella vale si su diámetro está entre 0,24·D y 0,6·D.
- ¿Cuál es la incertidumbre de la medición? → Resolución del instrumento, dispersión entre probetas y errores de lectura.

## Seguridad e higiene

- ¿Qué riesgos tiene y cómo se controlan? → Riesgos mecánicos, eléctricos, térmicos y de ruido, con sus medidas: protecciones fijas, parada de emergencia, bloqueo y etiquetado, elementos de protección personal (Ley 19.587 y Decreto 351/79).
- ¿Qué pasa si falla tal componente? → Cómo falla, qué protección actúa y cómo queda la máquina.
- ¿Dónde va la parada de emergencia y qué corta? → Al alcance del operario y cortando el movimiento peligroso.

## Ambiente, costos y mantenimiento

- ¿Qué residuos o emisiones genera y qué se hace con ellos? → Tipo, cantidad estimada y tratamiento o destino.
- ¿Cuánto cuesta y de dónde sacaron los precios? → Fuente y fecha de cada precio (cambian rápido); en dólares, con la cotización y la fecha.
- ¿Se recupera la inversión? → Repago simple = inversión / ahorro anual, con sus supuestos.
- ¿Qué mantenimiento necesita? → Tareas, frecuencia y quién las hace.

## Simulador, modelo 3D y programas

- ¿Cómo saben que el simulador da bien? → Usa el mismo modelo que la memoria, se validó contra un caso resuelto a mano y por otro método, y se comparó con las mediciones (decir el error medio).
- ¿Qué supuestos tiene y dónde deja de valer? → Los del panel de supuestos y límites.
- ¿Qué programas usaron y para qué? → CAD, cálculo, simulación; qué hizo cada uno y cómo se revisó.

## Proceso y trabajo en grupo

- ¿Cómo se organizaron y qué hizo cada uno? → Concreto y coherente con la tabla de reparto.
- ¿Qué fue lo más difícil y cómo lo resolvieron? → Un problema técnico real y la solución.
- ¿Qué falta para que esto se construya de verdad? → Ensayos, permisos, cálculos de detalle, presupuesto actualizado.
- ¿Qué aprendieron? → Algo técnico y algo de trabajo en equipo, sin frases hechas.
- ¿Usaron inteligencia artificial u otras herramientas? → Decir la verdad: para qué se usó y cómo verificaron lo que dio (cálculo a mano, segundo método, catálogo). Cada integrante tiene que poder explicar su parte sin ayuda.

## Público general (stand o muestra)

- ¿Para qué sirve? → Una frase con un ejemplo de la vida diaria.
- ¿Cuánto cuesta? ¿Cuánto consume? → Orden de magnitud con unidades que se entiendan ("como tres estufas").
- ¿Es peligroso? → Qué riesgo tiene y cómo se protege.
- ¿Se puede comprar o hacer en casa? → Qué existe en el mercado y qué tiene de distinto.
