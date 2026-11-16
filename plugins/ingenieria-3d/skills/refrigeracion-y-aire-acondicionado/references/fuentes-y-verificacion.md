# Fuentes y verificación

Leer para citar de dónde sale un dato, para saber qué falta confirmar o para regenerar las tablas del script.

## Cómo se generaron las tablas de `refrigeracion.py`

- **Programa:** CoolProp 8.0.0 para Python, backend HEOS. Fluidos puros con las ecuaciones de estado de referencia que trae CoolProp (ficha de cada fluido en [coolprop.org](https://coolprop.org/fluid_properties/PurePseudoPure.html); la del R-134a es la de Tillner-Roth y Baehr, 1994, *J. Phys. Chem. Ref. Data* 23, 657-729). Mezclas con el modelo de Kunz y otros (GERG) y los parámetros de Lemmon y Jacobsen (2004, *J. Phys. Chem. Ref. Data* 33) ([coolprop.org, mezclas](https://coolprop.org/fluid_properties/Mixtures.html)): R-410A = R-32/R-125 con fracciones molares 0,697615/0,302385 (50/50 % en masa) y R-404A = R-125/R-134a/R-143a con 0,357817/0,038264/0,603919 (44/4/52 % en masa).
- **Referencia de entalpía y entropía (IIR):** h = 200 kJ/kg y s = 1 kJ/(kg·K) para el líquido saturado (burbuja) a 0 °C. Los puros ya la traen en CoolProp; a las mezclas se les sumó la constante necesaria. Un diagrama p-h con otra referencia da otros valores absolutos y las mismas diferencias.
- **Nodos:** saturación a −50, −40, …, 60 y 65 °C (presión de burbuja y de rocío, h y s del líquido y del vapor, densidad del líquido, volumen del vapor). Vapor sobrecalentado: h − hv, s − sv y ln(v/vv) a 10, 20, 40, 60, 90, 120 y 150 K sobre cada temperatura de rocío. Líquido subenfriado: h(p, t − SC) − hl(t − SC) a 10, 20 y 30 K, porque la presión cambia algo la entalpía del líquido (hasta 1 kJ/kg en el R-410A).
- **Interpolación:** cúbica de Lagrange con los cuatro nodos más cercanos; la presión, como ln p contra 1/T.
- **Mezclas cerca de 45 °C:** el flash por temperatura y título de CoolProp 8.0 no converge para el R-410A entre unos 42 y 45,5 °C. Ahí la presión se tomó de la envolvente de fases de CoolProp (interpolación cúbica local: 0,002 % contra el flash en los puntos vecinos) y las propiedades, con presión y temperatura y la fase impuesta.
- **Compresión:** a la presión de condensación se busca el SH con la misma entropía de la succión. Si la entropía queda por debajo de la del vapor saturado (R-600a, fluido "seco"), la descarga isentrópica es vapor húmedo y se resuelve con el título (regla de la palanca, exacta en un fluido puro).

Para regenerar (con CoolProp instalado, fuera del script):

```python
import CoolProp.CoolProp as CP
AS = CP.AbstractState('HEOS', 'R32&R125'); AS.set_mass_fractions([0.5, 0.5])
AS.update(CP.QT_INPUTS, 1, 278.15)          # vapor saturado (rocío) a 5 °C
p = AS.p()                                   # Pa absolutos
AS.specify_phase(CP.iphase_gas)
AS.update(CP.PT_INPUTS, p, 288.15)           # vapor con SH = 10 K
h, s = AS.hmass() / 1000, AS.smass() / 1000  # sumarles la constante de la referencia IIR
```

## Exactitud medida contra CoolProp directo

| Qué | Diferencia máxima |
|---|---|
| Tablas presión-temperatura de −40 a 65 °C cada 5 °C (los 7 refrigerantes) | 0,005 % (0,0012 bar) |
| 200 puntos al azar de −50 a 65 °C | presión 0,003 %; hl 0,11 kJ/kg; hv 0,14 kJ/kg; sv 0,0004 kJ/(kg·K); temperatura desde la presión 0,0014 K |
| 40 ciclos al azar (evaporación −40 a 10 °C, condensación 30 a 60 °C, ηis 0,7) | COP 0,08 %; caudal 0,08 %; descarga isentrópica 0,06 K |
| Ciclo del ejemplo (R-410A) | caudal 0,021507 kg/s, COP isentrópico 5,406 y descarga 66,88 °C con CoolProp; el script da 0,02151, 5,405 y 66,84 °C |

Las entalpías de las mezclas cerca de 65 °C son las menos exactas: el punto crítico del R-410A está a 71,3 °C y el del R-404A a 72,1 °C (CoolProp).

## Confirmado en fuentes oficiales o primarias

| Dato | Fuente |
|---|---|
| 1 Btu_IT/h = 0,2930711 W; 1 kcal_IT = 4186,8 J (de ahí 1 kcal/h = 1,163 W); 1 ton of refrigeration (12 000 Btu_IT/h) = 3516,853 W; 1 psi = 6894,757 Pa; 1 mmHg = 133,3224 Pa; 1 atm = 101 325 Pa | NIST SP 811, [apéndice B.8](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b8) |
| Aires acondicionados con etiqueta obligatoria IRAM 62406 y estándar mínimo clase A; normas: Disposición 859/2008 (etiqueta) y Resolución 228/2014 (estándar mínimo); escala de A (verde) a G (rojo) | [argentina.gob.ar, etiquetado en eficiencia energética](https://www.argentina.gob.ar/economia/energia/eficiencia-energetica/etiquetado-en-eficiencia-energetica) |
| Disposición 859/2008 de la Dirección Nacional de Comercio Interior (7/11/2008, Boletín Oficial 31.529 del 11/11/2008): pone en vigencia la Res. 319/99 para aires acondicionados split y compactos, con certificación según "la norma IRAM 62406:2007, o de aquella que la reemplace" | [texto en argentina.gob.ar](https://www.argentina.gob.ar/normativa/nacional/norma-147008/texto) |
| Composición de las mezclas y modelo de mezcla | [coolprop.org, mezclas](https://coolprop.org/fluid_properties/Mixtures.html) |

## Sin confirmar en línea al armar la skill (marcado "verificar")

- **Clasificación de seguridad** (ISO 817 y ANSI/ASHRAE 34; confirmar la edición vigente): A1 para R-134a, R-410A, R-22 y R-404A; A2L para R-32; A3 para R-290 y R-600a.
- **PCA (GWP) a 100 años:** AR4 (IPCC 2007, Grupo de Trabajo I, tabla 2.14) y AR5 (IPCC 2013, Grupo de Trabajo I, tabla 8.A.1) de HFC-32 675/677, HFC-125 3500/3170, HFC-134a 1430/1300, HFC-143a 4470/4800 y HCFC-22 1810/1760; R-290 y R-600a ≈ 3. Las mezclas se calculan con esos valores (el demo lo hace). **PAO** del HCFC-22: 0,055 (Protocolo de Montreal, anexo C).
- **Leyes y calendarios:** Protocolo de Montreal aprobado por la Ley 23.778 y enmienda de Kigali por la Ley 27.559; calendario de eliminación de HCFC para países del artículo 5, con un remanente para servicio técnico hasta 2040; calendario de reducción de HFC de Kigali. Buscarlas en [argentina.gob.ar/normativa](https://www.argentina.gob.ar/normativa) por número y año.
- **Resolución 228/2014:** organismo y texto (la página oficial dio error del servidor). Límites de EER de cada clase de la IRAM 62406.
- **Valores de taller:** rangos orientativos de SH, SC y diferencias de temperatura de condensación y evaporación; la tabla de síntomas; el tiempo de estabilización (10 a 15 min); el criterio de la prueba de caída (unos 1000 micrones en 10 min); el llenado máximo del cilindro de recuperación (80 %).
- **Carga térmica:** calor de las personas (ASHRAE Handbook Fundamentals 2017, cap. 18, tabla 1) y constantes de la temperatura sol-aire (mismo capítulo).
- **Otras normas citadas:** IEC 60335-2-24 e IEC 60335-2-40 (límites de carga de refrigerantes inflamables), ISO 5149 y EN 378 (seguridad de sistemas frigoríficos), ISO 5151 (ensayo de capacidad de acondicionadores), IRAM 11603 (datos climáticos).

Antes de entregar un informe, confirmar estos puntos en la edición vigente y citarla (formato de cita en **normas-tecnicas-ar**).
