---
name: calculos-ingenieria
description: "Cálculos de ingeniería electromecánica presentados como en una memoria de cálculo (fórmula, datos, reemplazo, resultado con unidades y verificación con código) para iluminación por el método de los lúmenes, redes de aire comprimido, conductores y caída de tensión, motores y transmisiones, cintas transportadoras, balances de masa y energía, y selección de equipos de catálogo. Usar cuando haya que dimensionar, calcular, verificar o seleccionar equipos o instalaciones, o revisar un cálculo."
---

# Cálculos de ingeniería electromecánica

## Método (siempre)

1. **Datos y supuestos** en una tabla, cada uno con su fuente (consigna, catálogo, norma, medición).
2. **Fórmula**, con el significado y la unidad de cada símbolo.
3. **Reemplazo numérico** a la vista.
4. **Resultado** con unidades y redondeo con criterio.
5. **Valor adoptado**: el comercial o normalizado inmediato superior, con su margen.
6. **Verificación**: por otro método, contra un rango típico o por orden de magnitud.

Las cuentas se hacen con código (Python), nunca de cabeza, y el script queda como anexo si suma. Si la consigna fija valores (pérdida de carga admisible, factores, nomenclatura de la cátedra), se usan esos aunque difieran de los típicos.

## Calculadoras del kit

Antes de programar una cuenta desde cero, conviene usar la calculadora probada de la skill del tema. Cada una está en `scripts/` de su skill, tiene `--help` y un `demo` que reproduce un ejemplo resuelto.

| Tema | Skill | Script |
|---|---|---|
| Corriente, caída de tensión, sección, factor de potencia, cortocircuito, jabalina, iluminación | **instalaciones-electricas** | `electricas.py` |
| Transformadores, motor asincrónico, máquina sincrónica y de continua | **maquinas-electricas** | `maquinas.py` |
| Energía solar fotovoltaica | **energia-solar-fotovoltaica** | `fotovoltaica.py` |
| Tornillos, ejes, chavetas, rodamientos, correas, cadenas, engranajes, soldadura | **elementos-de-maquinas** | `elementos.py` |
| Vigas, torsión, pandeo, círculo de Mohr, secciones | **resistencia-de-materiales** | `resistencia.py` |
| Ajustes ISO 286, tolerancias generales, cadenas de cotas | **tolerancias-y-ajustes** | `tolerancias.py` |
| Tracción, dureza, Charpy, doblado | **ensayos-materiales** | `ensayos.py` |
| Neumática: cilindros, consumo de aire, secuencias | **neumatica-electroneumatica** | `neumatica.py` |
| Oleohidráulica: cilindros, bombas, cañerías | **oleohidraulica** | `oleohidraulica.py` |
| Cintas, tornillos sinfín, cangilones, cables y eslingas | **maniobra-y-transporte** | `transporte.py` |
| Conducción, convección, aislación, intercambiadores | **transferencia-de-calor** | `calor.py` |
| Aire húmedo y secaderos | **secado-y-psicrometria** | `psicrometria.py` |
| Refrigeración y aire acondicionado | **refrigeracion-y-aire-acondicionado** | `refrigeracion.py` |
| Indicadores y planes de mantenimiento | **mantenimiento-industrial** | `mantenimiento.py` |
| Costos, VAN y TIR, tiempos, camino crítico, control de calidad | **organizacion-industrial** | `organizacion.py` |
| Carga de fuego, dosis de ruido, matriz de riesgos | **higiene-y-seguridad** | `seguridad.py` |
| Datos de corte y programas CNC | **cnc-mecanizado** | `cnc.py` |
| Rehacer las cuentas de un informe terminado | **revision-tecnica** | `verificar_numeros.py` |

## Recetas

**Iluminación interior (método de los lúmenes)**
- Nivel de iluminación según IRAM-AADL J 20-06; mínimo legal según Dec. 351/79, Anexo IV.
- Índice del local: k = a·b / [h·(a + b)], con h = altura de la luminaria sobre el plano de trabajo.
- Coeficiente de utilización CU de la tabla del fabricante (con k y las reflectancias); factor de mantenimiento fm (habitual 0,6 a 0,8).
- Flujo total: Φt = E·S / (CU·fm). Cantidad: N = Φt / Φ por luminaria → redondear hacia arriba y distribuir en filas parejas respetando la separación máxima del fabricante.
- Verificación: E = N·Φ·CU·fm / S ≥ E requerida.

**Red de aire comprimido**
- Caudal: Σ (consumo de cada herramienta × cantidad) × coeficiente de simultaneidad × (1 + ampliación prevista) + fugas.
- Longitud de cálculo = longitud real + longitudes equivalentes de accesorios (codos, tes, válvulas).
- Diámetro por nomograma o por Darcy-Weisbach: Δp = f·(L/D)·ρ·v²/2, con ρ = p_abs/(R·T), R = 287 J/(kg·K) y f por Colebrook o Haaland.
- Verificar Δp ≤ admisible (típico 0,1 bar en la red principal, o el de la consigna) y adoptar el diámetro comercial.
- Tanque: V = Q·t·p0/Δp (Q de aire libre, t entre arranques del compresor, Δp del presostato).

**Conductores**
- Corriente: monofásica I = P/(U·cosφ); trifásica I = P/(√3·U·cosφ); motores I = P_útil/(√3·U·cosφ·η).
- Sección por corriente admisible según las tablas de la AEA 90364 (forma de instalación, temperatura, agrupamiento). Coordinar Ib ≤ In ≤ Iz.
- Caída de tensión: trifásica ΔU = √3·I·L·(r·cosφ + x·senφ); monofásica ΔU = 2·I·L·(r·cosφ + x·senφ). ρ del cobre ≈ 0,0172 Ω·mm²/m a 20 °C (corregir a la temperatura de servicio). Comparar con el límite de la AEA (770.15.6; 771.19.7): 3 % en circuitos terminales de iluminación y tomacorrientes; en circuitos que alimentan solo motores, 5 % en régimen y 15 % en el arranque. La caída de un circuito terminal se suma a la de la línea seccional que alimenta su tablero (fuentes en la skill **normas-tecnicas-ar**).
- Cortocircuito: S ≥ I·√t / k, con k = 115 (cobre en PVC) o 143 (cobre en XLPE).

**Motores y transmisiones**
- P = T·ω, con ω = 2π·n/60. Potencia del motor = potencia de la carga / rendimiento de la transmisión, con factor de servicio.
- Relación: i = n1/n2 = d2/d1 (poleas) = z2/z1 (engranajes).
- Potencias normalizadas IEC (kW): 0,37 · 0,55 · 0,75 · 1,1 · 1,5 · 2,2 · 3 · 4 · 5,5 · 7,5 · 11 · 15 · 18,5 · 22 · 30 · 37 · 45 · 55 · 75.
- Cinta transportadora: capacidad Q [t/h] = 3600·A [m²]·v [m/s]·ρ [t/m³]; la potencia, con el método del fabricante de la banda o de los rodillos (método completo en **maniobra-y-transporte**).

**Balances de masa y energía (secado, calentamiento, combustión)**
- Agua a evaporar (humedad en base húmeda): m_agua = m_h·(wi − wf)/(1 − wf).
- Calor: Q = m·cp·ΔT + m_agua·h_fg (h_fg ≈ 2257 kJ/kg a 100 °C). Combustible: m = Q/(PCI·η).

**Selección de equipos de catálogo**
- Buscar modelos reales y vigentes, preferentemente disponibles en Argentina: marca, modelo, datos técnicos y link a la ficha.
- Comparar 2 o 3 opciones en una tabla y elegir con criterio (margen, rendimiento, costo, disponibilidad). Nunca inventar modelos ni datos.

## Errores frecuentes

- Mezclar presión absoluta y manométrica, o aire libre y aire comprimido.
- Unidades: 1 bar = 100 kPa; 1 m³/h = 16,67 l/min; 1 HP = 0,7457 kW; 1 CV = 0,7355 kW.
- Olvidar cosφ, rendimiento o simultaneidad; redondear antes de terminar el cálculo.
- Adoptar un valor menor al calculado.

## Presentación

Al final, una tabla resumen con los resultados y los valores adoptados. Si hay curvas (pérdida de carga, consumo, temperatura), un gráfico. Los resultados tienen que coincidir con los planos y con la lista de equipos.
