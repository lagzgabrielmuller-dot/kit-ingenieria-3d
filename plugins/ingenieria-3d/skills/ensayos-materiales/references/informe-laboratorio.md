# Informe de laboratorio de ensayos e incertidumbre

Leer cuando hay que escribir el informe de un ensayo, armar las tablas de resultados, calcular la incertidumbre de una medición o decir si el material cumple una especificación. El formato del documento (portada, índice, numeración, bibliografía) está en la skill **informe-tecnico**.

## 1. Estructura

1. **Objetivo**: qué propiedad se determina y para qué (caracterizar un material, verificar una norma de producto, comparar tratamientos).
2. **Norma y método**: número, año y método elegido dentro de la norma (por ejemplo, Brinell HBW 10/3000, Charpy KV2 a −20 °C).
3. **Material y probetas**: designación, proveedor o procedencia, estado (laminado, recocido, templado y revenido), dirección de extracción, croquis con dimensiones nominales y medidas, cantidad de probetas e identificación de cada una.
4. **Equipos**: máquina (marca, modelo, capacidad, escala usada), extensómetro, durómetro, péndulo, calibre o micrómetro (resolución) y estado de calibración (certificado, fecha).
5. **Procedimiento y condiciones**: pasos realizados, temperatura del laboratorio, velocidad o tiempos de aplicación, cualquier desvío respecto de la norma y por qué.
6. **Resultados**: tablas con los valores de cada probeta, promedio y dispersión; curva tensión-deformación o curva de transición; fotos de las roturas o de las huellas con escala.
7. **Cálculos**: fórmula, reemplazo para una probeta como ejemplo, el resto en la tabla; incertidumbre.
8. **Análisis**: comparación con la norma de producto o la bibliografía (con fuente), causas de las diferencias, observaciones de la rotura.
9. **Conclusiones**: valores obtenidos con su incertidumbre, si cumple o no y con qué regla, limitaciones del ensayo.
10. **Anexos**: datos crudos (CSV de la máquina), certificados, planillas de campo.

## 2. Tablas modelo

Tracción:

| Probeta | d0 [mm] | S0 [mm²] | L0 [mm] | Fmax [kN] | Rp0,2 [MPa] | Rm [MPa] | Lu [mm] | A [%] | du [mm] | Z [%] |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | 10,00 | 78,54 | 50,0 | 39,27 | 350 | 500 | 62,5 | 25,0 | 6,20 | 61,6 |

Dureza Brinell:

| Huella | d1 [mm] | d2 [mm] | d [mm] | d/D | HBW | Observaciones |
|---|---|---|---|---|---|---|
| 1 | 4,10 | 4,14 | 4,12 | 0,412 | 215 | válida |

Charpy:

| Probeta | Temperatura [°C] | KV2 [J] | Fractura dúctil [%] | Expansión lateral [mm] |
|---|---|---|---|---|

## 3. Incertidumbre (GUM, JCGM 100:2008)

**Paso a paso**:
1. Escribir el modelo: la fórmula del resultado en función de lo medido (por ejemplo Rm = 4·Fmax/(π·d0²)).
2. Para cada magnitud de entrada, juntar sus fuentes de incertidumbre:
   - **Tipo A** (estadística): con n lecturas repetidas, u = s/√n (s = desviación estándar).
   - **Tipo B** (otra información): error máximo del instrumento ±a con distribución rectangular → u = a/√3; resolución δ de una indicación digital → u = δ/(2·√3) (varianza δ²/12); valor de un certificado con U y k → u = U/k.
   - Se combinan en cuadratura: u(x) = √(u1² + u2² + …).
3. Propagar: uc(y)² = Σ (∂y/∂xi · u(xi))². Si el modelo es un producto o cociente de potencias, y = c·x1^p1·x2^p2…, es más fácil en relativo: (uc/y)² = Σ (pi·u(xi)/xi)².
4. Incertidumbre expandida U = k·uc con k = 2 (nivel de confianza ≈ 95 %).
5. Redondear U a una o dos cifras significativas y el resultado a la misma posición decimal.

**Ejemplo 1, Rm** (datos de incertidumbre del ejemplo): Rm = 4·F/(π·d0²) → (u/Rm)² = (u(F)/F)² + (2·u(d0)/d0)².
- Fuerza: certificado de la máquina con 1 % expandido (k = 2) → u(F)/F = 0,50 %.
- d0: lecturas 10,00 / 10,02 / 9,98 mm → promedio 10,00 mm, s = 0,020 mm, tipo A = 0,020/√3 = 0,0115 mm; resolución del calibre 0,02 mm → 0,0058 mm; error máximo ±0,03 mm → 0,0173 mm. u(d0) = √(0,0115² + 0,0058² + 0,0173²) = 0,0216 mm → 0,216 %.
- (u/Rm) = √(0,50² + (2·0,216)²) = 0,661 % → uc = 3,3 MPa → U = 6,6 MPa.
- Resultado: **Rm = (500 ± 7) MPa, k = 2**.
- Lectura: d0 pesa el doble por estar al cuadrado; medir con micrómetro en vez de calibre baja mucho la incertidumbre.

**Ejemplo 2, Brinell** (solo la medición de la huella): HBW es muy sensible a d: con d = 4,12 mm, ∂HBW/∂d = −109,5 por mm, o sea u(HBW)/HBW ≈ 2,1·u(d)/d. Con lupa de 0,01 mm (0,0029 mm) y la semidiferencia de las dos lecturas como rectangular (0,02/√3 = 0,0115 mm): u(d) = 0,0119 mm → u(HBW) = 1,3 → U = 2,6 → **(215 ± 3) HBW 10/3000, k = 2**, sin contar la fuerza ni la bola. Las normas de dureza traen un anexo informativo con el cálculo completo (verificar en la edición vigente).

## 4. Comparar con una especificación

- Declarar la regla de decisión: por ejemplo, "cumple si el resultado menos U es mayor o igual que el mínimo" (conservadora) o "cumple si el resultado es mayor o igual que el mínimo" (aceptación simple). Las versiones actuales de ISO/IEC 17025 (en Argentina IRAM 301) piden decir qué regla se usó al declarar conformidad.
- Si el resultado queda dentro de ±U del límite, decirlo: la conclusión es "no concluyente" con esa regla.
- Ejemplo: barra ADN 420 con Re = (432 ± 6) MPa contra un mínimo de 420 MPa → cumple con las dos reglas (432 − 6 = 426).

## 5. Redacción

- Impersonal y en pasado: "se ensayaron tres probetas", "se obtuvo".
- Cada valor con su unidad y cifras según la incertidumbre; HBW y HV sin unidad.
- No explicar teoría que no se usa; sí explicar cualquier desvío del procedimiento (probeta fuera de medida, rotura fuera de las marcas, huella inválida descartada).
- Las fotos y gráficos, numerados y citados en el texto, con epígrafe y escala.
