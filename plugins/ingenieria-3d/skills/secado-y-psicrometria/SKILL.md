---
name: secado-y-psicrometria
description: "Psicrometría del aire húmedo y cálculo de secaderos por aire caliente: propiedades del aire (humedad relativa y absoluta, entalpía, punto de rocío, bulbo húmedo, volumen específico, presión según la altitud), humedad del producto en base húmeda y seca, agua a evaporar, caudal de aire del ventilador, potencia del calentador, consumo de combustible, mezcla de corrientes (recirculación) y diagrama psicrométrico en SVG con el proceso dibujado. Usar cuando se diseñe o verifique un secadero o una secadora (granos, guano, alimentos, madera, ladrillos, pintura), se pida el caudal de aire o la potencia para secar, se calcule humedad relativa, punto de rocío o entalpía del aire, o haya que dibujar un proceso en el diagrama psicrométrico."
---

# Secado y psicrometría

Un secadero por aire caliente es un problema de aire húmedo: el aire ambiente se calienta, pasa por el producto, se carga de agua y sale. Con dos balances (agua y energía) sobre el diagrama psicrométrico salen el caudal de aire, la potencia del calentador y el consumo. `scripts/psicrometria.py` (Python 3.9+, solo biblioteca estándar) hace las cuentas en formato de memoria de cálculo y dibuja el diagrama. Para la presentación de los resultados, ver **calculos-ingenieria**.

## Propiedades del aire húmedo

Fuente: ASHRAE Handbook, Fundamentals (2017), cap. 1 "Psychrometrics" (aire húmedo como gas ideal). Todo va **por kg de aire seco**, porque el caudal de aire seco no cambia a lo largo del secadero y el de aire húmedo sí.

| Magnitud | Fórmula | Unidades |
|---|---|---|
| Presión de saturación | p_ws(t), ecuaciones de Hyland y Wexler (sobre hielo debajo de 0 °C) | kPa |
| Humedad relativa | φ = p_w/p_ws | % |
| Humedad absoluta | W = 0,621945·p_w/(p − p_w) | kg de agua/kg de aire seco |
| Entalpía | h = 1,006·t + W·(2501 + 1,86·t) | kJ/kg de aire seco |
| Volumen específico | v = 0,287042·(t + 273,15)·(1 + 1,607858·W)/p | m³/kg de aire seco, con p en kPa |
| Punto de rocío | t_r tal que p_ws(t_r) = p_w | °C |
| Bulbo húmedo | ecuación psicrométrica de ASHRAE, resuelta por bisección | °C |
| Presión según la altitud Z | p = 101,325·(1 − 2,25577·10⁻⁵·Z)^5,2559 | kPa, con Z en m |

```
python psicrometria.py aire --t 20 --hr 50                 # W 7,26 g/kg · h 38,6 kJ/kg · rocío 9,3 °C · bh 13,8 °C
python psicrometria.py aire --t 30 --tbh 20 --altitud 1000 # con bulbo húmedo en lugar de HR, a 1000 m (89,9 kPa)
```

## Humedad del producto

- Base húmeda: w = m_agua/m_total. Base seca: X = m_agua/m_sólido seco. X = w/(1 − w) y w = X/(1 + X).
- `psicrometria.py humedad --bh 75` → base seca 300 %.
- Agua a evaporar: m_w = m_h·(w_i − w_f)/(1 − w_f). De 75 % a 15 % no se va el 60 % de la masa sino 70,6 kg cada 100 kg, porque el 15 % final es sobre una masa menor.

## Método para un secadero de aire caliente

1. **Producto:** sólidos secos m_s = m_h·(1 − w_i) y agua a evaporar m_w.
2. **Estados del aire:** 1 ambiente (t, φ) → 2 calentado (W2 = W1: calentar no agrega agua) → 3 salida. Si el secadero no pierde calor, la salida es adiabática: h3 = h2 (el aire se enfría por una línea de entalpía constante, casi la de bulbo húmedo constante) hasta la humedad relativa de salida adoptada.
3. **Aire seco:** m_a = m_w/(W3 − W1). Caudal del ventilador: V = m_a·v con el v del aire donde está el ventilador (v1 si está antes del calentador, v2 si está después).
4. **Potencia:** P = m_a·(h2 − h1); calentador P_cal = P/η; combustible m_c = P_cal/PCI (con el PCI del proveedor, en la misma unidad que se quiere el consumo).
5. **Indicador:** energía específica E = P_cal/ṁ_w, en kJ por kg de agua evaporada. Nunca baja del calor de vaporización (unos 2400 kJ/kg); cuanto más arriba, más energía se va con el aire de salida.

### Ejemplo (es el `demo`)

100 kg/h de producto húmedo de 75 % a 15 % (base húmeda); aire ambiente a 25 °C y 60 %, calentado a 70 °C, sale adiabático al 70 %; calentador con η = 0,9.

```
python psicrometria.py secador --producto 100 --hi 75 --hf 15 --tamb 25 --hramb 60 --taire 70 --hrsal 70 --rend 0.9 --diagrama proceso.svg
```

| Resultado | Valor |
|---|---|
| Agua a evaporar | m_w = 100·(0,75 − 0,15)/(1 − 0,15) = 70,59 kg/h |
| Aire: 1 → 2 → 3 | W1 = 11,90 g/kg y h1 = 55,5 kJ/kg; h2 = 101,7 kJ/kg; salida a 35,4 °C con W3 = 25,75 g/kg |
| Aire seco | m_a = 70,59/(0,02575 − 0,01190) = 5094 kg/h |
| Caudal en el ventilador (aire ambiente) | V1 = 4385 m³/h |
| Calor al aire / calentador | 65,5 kW / 72,7 kW |
| Energía específica | 3710 kJ por kg de agua |

Con CoolProp 8.0 (aire húmedo real) el mismo caso da 5077 kg/h y 65,4 kW: diferencia menor que 0,4 %.

Opciones: `--lote-horas H` cuando `--producto` es la carga de un lote que se seca en H horas; `--tsal` en lugar de `--hrsal` para fijar la temperatura de salida; las dos juntas para un estado de salida medido, y entonces el script informa cuánta entalpía perdió el aire (calor que se llevaron el producto y las paredes); `--pci` para el consumo; `--altitud` o `--p` para la presión.

## Decisiones de diseño

- **Temperatura del aire caliente:** la limita el producto (se quema, se degrada, larga olor o se vuelve riesgo de incendio) y el material del secadero. Sale de los datos del producto o de ensayos, no de esta skill.
- **Humedad relativa de salida:** cuanto más alta, menos aire y menos energía, pero el secado es más lento y crece el riesgo de condensación en la salida. El 100 % es el límite teórico (caudal mínimo); el valor adoptado se justifica en el informe.
- **Recirculación:** devolver parte del aire de salida ahorra energía. La mezcla se resuelve con balances por kg de aire seco: W_m = (m_A·W_A + m_B·W_B)/(m_A + m_B), igual para h, y t_m = (h_m − 2501·W_m)/(1,006 + 1,86·W_m): `psicrometria.py mezcla --a "25;60;3000" --b "35,4;70;2000"`. Si la mezcla cae sobre la curva de saturación, condensa y el script avisa.
- **Tiempo de secado:** el caudal da la capacidad de evaporación, m_a·(W3 − W1) por hora. El tiempo real depende además del período de velocidad decreciente, en el que el producto entrega el agua más despacio de lo que el aire la puede llevar; se obtiene con una curva de secado del producto (ensayo). Teoría en Geankoplis, *Procesos de transporte y operaciones unitarias*, cap. 9 (secado).

## Diagrama psicrométrico

`psicrometria.py diagrama --salida carta.svg --punto "25;60;1 ambiente" --punto "70;6;2 caliente"` dibuja curvas de humedad relativa, líneas de entalpía, los puntos y flechas en el orden dado; `secador ... --diagrama proceso.svg` dibuja 1 → 2 → 3 solo. El SVG entra directo en Word o en una página web; para PNG: `rsvg-convert -w 1600 carta.svg -o carta.png`.

## Errores frecuentes

- Restar humedades en base húmeda como si fueran porcentajes de la masa inicial.
- Usar la masa de aire húmedo en los balances en lugar de la de aire seco.
- Calcular el caudal del ventilador con el volumen específico del aire equivocado (ventilador antes o después del calentador).
- Suponer aire de salida saturado y quedarse corto de caudal.
- Olvidar la altitud: a 1000 m la presión es 89,9 kPa y cambian W y v.
- Mezclar kW con kJ/h (1 kW = 3600 kJ/h) o el poder calorífico inferior con el superior.

## Verificación

- `python psicrometria.py demo` tiene que terminar en `DEMO OK`: presión de saturación contra las tablas de vapor (IAPWS-IF97), aire a 20 °C y 50 % contra CoolProp, el secadero del ejemplo, la mezcla y el diagrama.
- Precisión contra CoolProp 8.0 (aire húmedo real, ASHRAE RP-1485), de −20 a 50 °C: W 0,7 %, h 1,2 kJ/kg, v 0,1 %, rocío y bulbo húmedo 0,03 °C (cerca de 0 °C el bulbo húmedo puede diferir 0,5 °C, según haya agua o hielo en la mecha); hasta 80 °C, W 1,1 %. Presión de saturación: 0,03 % de 1 a 150 °C.
- En cada cálculo, el balance de agua tiene que cerrar: m_a·(W3 − W1) = m_w (el script lo muestra). Uno o dos puntos se pueden comparar con un diagrama psicrométrico impreso.
- Para una entrega importante, una revisión independiente con **equipo-de-modelos**.
