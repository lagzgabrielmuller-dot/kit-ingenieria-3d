---
name: instalaciones-electricas
description: "Cálculos de instalaciones eléctricas de baja tensión con memoria de cálculo: corriente de proyecto, caída de tensión y sección mínima por caída (cobre o aluminio, a la temperatura de servicio), corrección del factor de potencia (kvar y capacitores en estrella o triángulo), corriente de cortocircuito de un transformador y sección mínima térmica, resistencia de una jabalina de puesta a tierra e iluminación interior por el método de los lúmenes. Usar cuando haya que dimensionar o verificar un conductor, calcular la caída de tensión, el banco de capacitores, el cortocircuito, la puesta a tierra o la cantidad de luminarias de un local."
---

# Instalaciones eléctricas

`scripts/electricas.py` (Python 3.9+, solo biblioteca estándar) hace cada cuenta e imprime fórmula, reemplazo y resultado con coma decimal, listo para la memoria de cálculo (presentación en **calculos-ingenieria**). Los valores que exige la reglamentación (caídas de tensión admisibles, resistencia de puesta a tierra, niveles de iluminación) están, con su fuente, en **normas-tecnicas-ar**; si la consigna o el profesor dan otros, mandan esos.

## Comandos y fórmulas

| Comando | Fórmulas |
|---|---|
| `corriente --P kW --U V [--fases 3] [--cos] [--rend]` | Trifásica I = P/(√3·U·cosφ·η); monofásica I = P/(U·cosφ·η) |
| `caida --I A --L m --S mm² [--limite %]` | ρ = ρ20·(1 + α·(t − 20)); ΔU = √3·I·L·(r·cosφ + x·senφ) en trifásica y 2·I·L·(…) en monofásica, con r = ρ/S |
| `caida --I A --L m --limite %` (sin `--S`) | Sección mínima S = k·I·L·ρ·cosφ/ΔU y la normalizada siguiente (serie IEC 60228: 1,5 · 2,5 · 4 · 6 · 10 · 16 · 25 · 35 · 50 · 70 · 95 · 120 · 150 · 185 · 240 · 300 · 400 mm²) |
| `capacitor --P kW --cos1 --cos2` | Qc = P·(tg φ1 − tg φ2); por fase, C = Qc/(3·ω·U²) en triángulo y C = Qc/(ω·U²) en estrella |
| `cortocircuito --S kVA --uk %` | Zt = uk·U²/S; Ik = U/(√3·Zt) = In/uk; con `--L --seccion`, la Ik al final del cable; con `--t --k`, S ≥ Ik·√t/k |
| `jabalina --rho Ω·m --L m --d mm` | R = ρ/(2π·L)·(ln(4·L/a) − 1), con a el radio (fórmula de Dwight) |
| `lumenes --a --b --h --E --flujo --cu --fm` | k = a·b/(h·(a + b)); Φt = E·S/(CU·fm); N = Φt/Φ hacia arriba; E = N·Φ·CU·fm/S |

Datos que usa el script: resistividad a 20 °C del cobre recocido 0,017241 Ω·mm²/m (IEC 60028) y del aluminio 0,028264 Ω·mm²/m (IEC 60889); coeficiente de temperatura 0,00393 y 0,00403 1/°C. La temperatura de servicio por defecto es 70 °C (conductor aislado en PVC a plena carga). Los k del cortocircuito (115 para cobre en PVC, 143 para cobre en XLPE) están en **calculos-ingenieria**.

## Ejemplos

```
python electricas.py caida --I 32 --L 45 --limite 3 --fases 1 --U 220 --cos 0.9
  → sección mínima 8,10 mm² → 10 mm²; ΔU = 5,35 V = 2,43 % (verifica el 3 %)
python electricas.py capacitor --P 75 --cos1 0.78 --cos2 0.95
  → 35,52 kvar; 261,0 µF por fase en triángulo; la corriente baja de 146,1 A a 119,9 A
python electricas.py cortocircuito --S 400 --uk 4 --L 60 --seccion 95 --t 0.2 --k 115
  → 14,43 kA en bornes; 11,93 kA a 60 m; S térmica ≥ 56,1 mm²
python electricas.py jabalina --rho 80 --L 3 --d 14.6   → 27,2 Ω (≤ 40 Ω)
python electricas.py lumenes --a 12 --b 8 --h 2.5 --E 300 --flujo 5200 --cu 0.55 --fm 0.75   → k 1,92; 14 luminarias; 313 lx
```

## Criterios

- **Caída de tensión:** la de un circuito terminal se suma a la de la línea seccional que alimenta su tablero. Arriba de 50 mm², sumar la reactancia del catálogo del cable (`--x` en Ω/km): el script avisa.
- **Sección:** la caída es uno de los criterios; también corriente admisible (tablas de la AEA según forma de instalación, temperatura y agrupamiento, con Ib ≤ In ≤ Iz) y cortocircuito. Se adopta la mayor.
- **Factor de potencia:** el cos φ objetivo lo fija la distribuidora en su cuadro tarifario; el banco se elige con el escalón comercial siguiente y, si la carga varía, con regulación automática.
- **Cortocircuito:** el cálculo toma la red de alimentación como infinita y el transformador como reactancia pura; IEC 60909 agrega la red y el factor de tensión c. Sirve para un primer poder de corte con margen.
- **Puesta a tierra:** ρ del suelo se mide (método de Wenner) y la resistencia final se verifica con la medición en obra (en el trabajo, con el protocolo de la Res. SRT 900/15). Varias jabalinas en paralelo bajan menos que R/n si están cerca: separarlas al menos su largo.
- **Iluminación:** CU sale de la tabla del fabricante con k y las reflectancias; fm según limpieza y mantenimiento (habitual 0,6 a 0,8).

## Errores frecuentes

- Calcular la caída con la resistividad a 20 °C en lugar de la de servicio.
- Usar 2 en lugar de √3 en trifásica (o al revés en monofásica).
- Tomar la corriente de cortocircuito del final del cable para la sección térmica: manda la del principio, que es mayor.
- Confundir kW con kVA o kvar, y µF por fase con µF del banco.
- Redondear N luminarias hacia abajo.

## Verificación

`python electricas.py demo` tiene que terminar en `DEMO OK`: cada comando contra su cuenta a mano, y la sección mínima por caída vuelve al valor de partida. Para una entrega, una revisión independiente con **equipo-de-modelos** o **revision-tecnica**.
