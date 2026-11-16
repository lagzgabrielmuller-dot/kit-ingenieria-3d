---
name: oleohidraulica
description: "Cálculo de sistemas oleohidráulicos (hidráulica de aceite) para prensas, máquinas y equipos móviles, con script en Python: cilindros (fuerzas, relación de áreas, presión para una carga, velocidad y tiempo de carrera, diámetro normalizado ISO 3320 e ISO 6020-2, pandeo del vástago), bombas y motores hidráulicos (cilindrada, caudal, potencia, motor eléctrico, torque), mangueras y cañerías (velocidades, diámetro, pérdida de carga con la viscosidad ISO VG a la temperatura de trabajo), acumuladores, tanque, calor, válvulas (alivio, direccionales, caudal, antirretorno, contrabalance, secuencia) y circuitos típicos con símbolos ISO 1219-1. Usar cuando se pregunte, por ejemplo, qué cilindro necesito para 10 t a 160 bar, cómo es el cálculo de una prensa hidráulica, qué bomba y qué motor pongo, cuánto tarda en salir el vástago, el diámetro de la manguera, por qué calienta el aceite o cómo es el circuito hidráulico de una prensa, o haya que calcular un acumulador o un tanque."
---

# Oleohidráulica

Cálculo de prensas, máquinas y equipos móviles con aceite a presión. `scripts/oleohidraulica.py` (Python 3.9+, solo biblioteca estándar) hace cada cuenta e imprime fórmula, reemplazo y resultado con coma decimal. No se repite lo que está en otras skills:
- Aire comprimido, secuencias, método cascada, GRAFCET y mando eléctrico con relés: **neumatica-electroneumatica**.
- Presentación de la memoria de cálculo y potencias normalizadas de motores: **calculos-ingenieria**.
- Pernos, ejes, chavetas y rodamientos de la máquina: **elementos-de-maquinas**. Motor eléctrico y su línea: **maquinas-electricas** e **instalaciones-electricas**.
- Plano del esquema: **planos-tecnicos**. Informe: **informe-tecnico**. Reglamentación de seguridad: **normas-tecnicas-ar**.

## Diferencias con la neumática

| | Neumática | Oleohidráulica |
|---|---|---|
| Presión habitual | unos 6 bar (ver **neumatica-electroneumatica**) | 100 a 350 bar ([Roymech](https://roymech.org/Related/Hydrostatics/Hydraulic_tubing.html)) |
| Fluido | Se comprime: rápido pero elástico | Casi no se comprime: fuerza grande, posición firme, velocidad regulable |
| Después del trabajo | Escapa a la atmósfera | Vuelve al tanque por una línea de retorno |
| Temperatura | Poco efecto | Cambia la viscosidad: pérdidas, fugas y rendimientos dependen de ella |
| Vías y símbolos | Números 1, 2, 4, 3, 5; triángulos vacíos | Letras P, T, A, B, X, Y, L; triángulos llenos (ISO 1219-1) |

## Método (siempre)

1. **Datos**: fuerza o masa, carrera, velocidades o tiempos, ciclo, presión de la bomba, montaje del cilindro, temperatura ambiente, equipo fijo o móvil.
2. **Cilindro**: diámetro mínimo con el rendimiento → normalizado → vástago (relación de áreas, pandeo, velocidad de retroceso) → presión real para la carga.
3. **Caudal y tiempos**: Q = A · v con la velocidad pedida, o v = Q / A con la bomba elegida; caudal que vuelve de la otra cámara (Q · φ).
4. **Bomba y motor eléctrico**: cilindrada, caudal real, potencia con la presión de la válvula de alivio, motor normalizado.
5. **Aceite**: grado ISO VG para que la viscosidad a la temperatura de trabajo quede en el rango de la bomba.
6. **Líneas**: diámetro por velocidad recomendada, manguera con presión de trabajo suficiente, pérdida de carga en caliente y en frío, aspiración.
7. **Circuito**: válvula de alivio, distribuidora con el centro adecuado, qué sostiene la carga, regulación de velocidad, secuencia; acumulador si hace falta.
8. **Tanque y calor**: volumen, potencia que se vuelve calor, lo que disipa el tanque, intercambiador.
9. **Pandeo** con la fuerza máxima (presión de alivio por A1).
10. **Documentar**: esquema ISO 1219-1, lista de componentes, memoria de cálculo y verificación.

## Cilindros

| Magnitud | Fórmula | Unidades |
|---|---|---|
| Áreas | A1 = π · D² / 4; Av = π · d² / 4; A3 = A1 − Av | D émbolo, d vástago [mm] |
| Relación de áreas | φ = A1 / A3 | nominales 1,06 · 1,12 · 1,25 · 1,4 · 1,6 · 2 · 2,5 · 5 (ISO 7181) |
| Fuerza | F = p · A · η (avance con A1, retroceso con A3) | p [bar] · 0,1 = N/mm²; F [N] |
| Presión para una carga | p = F / (A · η) | F = m · g si es una masa (10 t = 98,07 kN) |
| Diámetro mínimo | D = √(4 · F / (π · p · η)) | se adopta el normalizado siguiente |
| Velocidad y tiempo | v [m/s] = Q [L/min] / (6 · A [cm²]); t = s / v | |
| Caudal de la otra cámara | al avanzar sale Q / φ; al retroceder sale Q · φ | |
| Regenerativo | v = Q / Av; F = p · Av · η | |
| Intensificación | p3 = (p · A1 − F) / A3; sin carga, p · φ | al estrangular la salida del lado del vástago |

- Rendimiento: 0,95 en compresión (avance) y 0,92 en tracción (retroceso), los de los diagramas de HANSA-FLEX ([TI Hydraulic Cylinders, 09/2024](https://www.hansa-flex.de/fileadmin/hansaflex/Technical_Information/English/TI-Hydraulic_cylinders_EN_web.pdf)); si la consigna da otro, se usa ese.
- Diámetros preferidos de **ISO 3320** [mm]: 25 · 32 · 40 · 50 · 63 · 80 · 100 · 125 · 160 · 200 · 250 · 320 · 400 · 500 (y menores; no preferidos 90, 110, 140, 180…).
- Serie compacta de 160 bar, **ISO 6020-2**, vástagos [mm]: Ø25: 12/18 · Ø32: 14/18/22 · Ø40: 18/22/28 · Ø50: 22/28/36 · Ø63: 28/36/45 · Ø80: 36/45/56 · Ø100: 45/56/70 · Ø125: 56/70/90 · Ø160: 70/90/110 · Ø200: 90/110/140 (catálogo Confortinet; Rexroth publica las mismas relaciones para la CDT3).
- Velocidad: HANSA-FLEX admite 0,42 m/s con juntas estándar y 0,10 m/s al entrar en los extremos; más rápido, amortiguación o frenado.
- Pandeo (método de los catálogos Rexroth): Lk = β · L con β = 2 (empotrado y libre), 1 (articulado-articulado), 0,7 (empotrado y articulado guiado), 0,5 (empotrado-empotrado); λ = 4 · Lk / d; λg = π · √(E / (0,8 · Re)). Si λ > λg, Euler: F adm = π² · E · I / (ν · Lk²), con I = π · d⁴ / 64; si λ ≤ λg, Tetmajer: F adm = π · d² · (335 − 0,62 · λ) / (4 · ν). E = 210 000 N/mm², ν = 3,5 y Re la fluencia del vástago (la recta de Tetmajer es la del S355).

Tablas, áreas, fuerzas a 160 bar, montajes y fuentes: [references/cilindros-y-pandeo.md](references/cilindros-y-pandeo.md) (leerla al elegir el cilindro o verificar el pandeo).

## Bombas y motores hidráulicos

| | Bomba | Motor hidráulico |
|---|---|---|
| Caudal | Q = Vg · n · ηv / 1000 | Q = Vg · n / (1000 · ηv) |
| Velocidad | la del motor eléctrico | n = Q · 1000 · ηv / Vg |
| Torque | T = Vg · Δp / (20 · π · ηhm) | T = Vg · Δp · ηhm / (20 · π) |
| Potencia | P = Q · Δp / (600 · ηt) en el eje | P = Q · Δp · ηt / 600 de salida |

Unidades: Vg [cm³/rev], n [rpm], Q [L/min], Δp [bar], T [N·m], P [kW]; ηt = ηv · ηhm. Fuentes: Rexroth A10VSO (RE 92714/08.2015), AZPF (RE 10089/2019-07-17) y A2FM (RE 91001-01-X-B2, 04.2016).

- El motor eléctrico se elige con la presión de la válvula de alivio, no con la de trabajo, y con la potencia normalizada siguiente (**calculos-ingenieria**).
- Rendimientos: de las curvas del catálogo. Como orden de magnitud, en un ejemplo de Brendan Casey (Power & Motion, 2023) una bomba de engranajes tiene 85 % de rendimiento total y una de pistones de eje inclinado 92 %.

Catálogos de ejemplo, motor hidráulico y fuentes: [references/bombas-acumuladores-tanque.md](references/bombas-acumuladores-tanque.md) (leerla al elegir la bomba y el motor eléctrico o calcular un motor hidráulico).

## Aceite y viscosidad

- **ISO 3448**: el grado ISO VG es la viscosidad a 40 °C con ± 10 %: VG 32 de 28,8 a 35,2 mm²/s; VG 46 de 41,4 a 50,6; VG 68 de 61,2 a 74,8.
- A otra temperatura (**ASTM D341**): log log Z = A − B · log T, con Z = ν + 0,7 + exp(−1,47 − 1,84 · ν − 0,51 · ν²) y T en K; A y B salen de ν a 40 °C y a 100 °C de la hoja técnica.
- Mobil Nuto H 46 (44,0 y 6,6 mm²/s): 247 mm²/s a 10 °C, 44,0 a 40 °C, 28,8 a 50 °C y 14,3 a 70 °C.
- Rango de la bomba: Rexroth A10VSO, óptimo 16 a 36 mm²/s y hasta 1000 mm²/s en el arranque en frío; AZPF, recomendado 20 a 100 mm²/s y hasta 2000 en frío. Con el Nuto H 46 eso es de 45 a 66 °C y de 24 a 60 °C.

## Cañerías y mangueras

| Línea | Velocidad recomendada | Defecto del script |
|---|---|---|
| Aspiración | 0,6 a 1,5 m/s | 1 m/s |
| Retorno | 1,5 a 4 m/s | 3 m/s |
| Presión | hasta 50 bar 4 m/s; 50 a 100 bar 4 a 5; 100 a 200 bar 5 a 6; más de 200 bar 6 a 7 (máximo 8 m/s) | 4, 4, 5 y 6 m/s |

Fuentes: Atos (tabla P002-1/E), Roymech, HANSA-FLEX, Hydroscand y la *Formelsammlung Hydraulik* de H. Ortwig (Hochschule Trier), con links en la referencia.

- Diámetro interior: d = √(4 · Q / (π · v)), o d [mm] = √(21,22 · Q [L/min] / v [m/s]); se adopta el comercial siguiente.
- Manguera EN 853 2SN (Semperit), interior y presión de trabajo: DN 12, 13,0 mm, 275 bar · DN 16, 16,4 mm, 250 bar · DN 19, 19,5 mm, 215 bar · DN 25, 26,0 mm, 165 bar. La presión baja al crecer el diámetro.
- Pérdida de carga (Darcy-Weisbach): Re = v · d / ν; laminar (Re < 2300) λ = 64 / Re; turbulento liso λ = 0,3164 / Re^0,25 (Blasius); con rugosidad, Haaland. Δp = λ · (L / d) · ρ · v² / 2, más Σζ · ρ · v² / 2 en accesorios.
- En laminar la pérdida es proporcional a la viscosidad: se calcula también en frío, y la aspiración tiene que quedar sobre la presión absoluta mínima de la bomba.

Velocidades, viscosidades, mangueras y pérdidas, con fuentes: [references/aceite-y-canerias.md](references/aceite-y-canerias.md) (leerla al elegir el aceite o dimensionar una línea).

## Acumuladores, tanque y calor

- Acumulador (Boyle, presiones **absolutas**): p0 · V0ⁿ = p1 · V1ⁿ = p2 · V2ⁿ; ΔV = V0 · ((p0/p1)^(1/n) − (p0/p2)^(1/n)); n = 1 en procesos lentos (más de 1 min), n = 1,4 en rápidos (nitrógeno). Precarga p0 = 0,9 · p1 para acumular energía y p2 : p0 ≤ 4 en los de vejiga (HYDAC).
- Tanque: 3 a 5 veces el caudal de la bomba por minuto en instalaciones fijas y 1,5 a 2 veces en máquinas móviles, más 10 % de cámara de aire (Brendan Casey, Power & Motion, 2015).
- Calor = potencia en el eje − potencia útil. Por una válvula pasa a calor P = Δp · Q / 600 [kW]: si la bomba descarga por la válvula de alivio, toda su potencia. El tanque disipa P = h · A · ΔT / 1000 [kW], con A paredes y tapa [m²] y h = 12 W/(m²·K) ventilación normal, 24 forzada, 6 mala (Casey, 2019).

Detalle, temperaturas recomendadas y fuentes: [references/bombas-acumuladores-tanque.md](references/bombas-acumuladores-tanque.md) (leerla al dimensionar el acumulador o el tanque, o cuando el aceite calienta).

## Válvulas y circuitos

- **Alivio**: fija la presión máxima. **Distribuidora 4/3**: el centro tándem (P a T, A y B bloqueadas) descarga la bomba en reposo. **Antirretorno pilotado** o **contrabalance**: sostienen la carga; la contrabalance se ajusta al menos a 1,3 veces la presión que genera la carga (Sun Hydraulics). **Reguladora de caudal**: a la entrada, a la salida (cuidado con la intensificación) o en derivación. **Secuencia**: habilita un segundo movimiento al llegar a una presión.
- **Regenerativo**: v = Q / Av y F = p · Av · η; con φ = 2 iguala avance y retroceso. **Prensa**: bajada rápida, prensado hasta el presostato, mantenimiento (acumulador), descompresión y subida.
- Símbolos ISO 1219-1 (triángulos llenos en hidráulica), vías P, T, A, B, X, Y, L; seguridad según ISO 4413:2010; el aceite a presión se inyecta en la piel.

Componentes, centros, lectura paso a paso de un circuito, circuitos típicos y seguridad: [references/valvulas-y-circuitos.md](references/valvulas-y-circuitos.md) (leerla al armar o leer un esquema).

## Ejemplo resuelto (`python scripts/oleohidraulica.py demo`)

Prensa de 10 t, 160 bar en la válvula de alivio, carrera 300 mm, bomba de engranajes a 1450 rpm para unos 25 L/min (ηv = 0,95 y ηt = 0,85 supuestos), aceite Nuto H 46 a 50 °C (10 °C en el arranque), cilindro con brida delantera y puente guiado.

| Paso | Resultado |
|---|---|
| Cilindro | D mín = √(4 · 98 066 / (π · 16 · 0,95)) = 90,63 mm → Ø100; vástago Ø70: A1 = 78,54 cm², A3 = 40,06 cm², φ = 1,961 |
| Presión para 10 t | 131,4 bar; fuerza útil a 160 bar 119,4 kN (teórica 125,7 kN) |
| Bomba | Vg = 18,15 cm³ → 19 cm³ (AZPF); Q = 26,17 L/min; 6,98 kW hidráulicos, 8,21 kW en el eje, T = 54,1 N·m → motor de 11 kW |
| Tiempos | avance 0,0555 m/s en 5,40 s; retroceso 0,109 m/s en 2,75 s (pide amortiguación); regenerativo 0,113 m/s |
| Caudales | al retroceder vuelven Q · φ = 51,3 L/min; intensificación posible p · φ = 313,7 bar |
| Aceite | ν = 28,76 mm²/s a 50 °C y 247,3 mm²/s a 10 °C |
| Mangueras 2SN | presión y línea B DN 12 (3,29 m/s); línea A DN 16 (4,05 m/s); retorno DN 19 (2,86 m/s); aspiración DN 25 (0,82 m/s) |
| Pérdida | DN 12, 3 m: Re = 1485, λ = 0,0431, Δp = 0,470 bar a 50 °C y 4,04 bar a 10 °C; aspiración en frío 0,97 bar absolutos |
| Pandeo | caso 3, L = 450 mm, Re = 355 N/mm²: λ = 18,0 < λg = 85,4 → Tetmajer 356,1 kN ≥ 125,7 kN; L máx (Euler) 3367 mm |
| Acumulador | 0,4 L entre 140 y 160 bar, p0 = 126 bar: 3,58 L isotérmico, 4,77 L adiabático → 5 L |
| Tanque y calor | 79 a 131 L; descargando por la de alivio, 8,21 kW de calor contra 0,342 kW que disipa un tanque de 1,14 m² con 25 K |

El `demo` verifica 28 controles: cuentas a mano, Hagen-Poiseuille contra Darcy en laminar, la viscosidad del Shell Tellus S3 M 46 a 0 °C contra su hoja técnica (577 contra 565 mm²/s), las 26 relaciones φ del catálogo Rexroth CDT3, la continuidad Euler-Tetmajer en λg y las vueltas inversas (acumulador, pandeo, motor hidráulico). Termina en `DEMO OK` o sale con código 1.

## Script

```
python scripts/oleohidraulica.py cilindro --t 10 --p 160                     (diámetro y vástagos)
python scripts/oleohidraulica.py cilindro --D 100 --d 70 --p 160 --t 10 --carrera 300 --Q 26.2
python scripts/oleohidraulica.py bomba --Q 25 --p 160 --n 1450
python scripts/oleohidraulica.py motor --Vg 80 --Q 26.2 --dp 140             (o --n 300 --T 160 --dp 140)
python scripts/oleohidraulica.py viscosidad --vg 46 --temp 50                (o --nu40 46 --nu100 6.8)
python scripts/oleohidraulica.py cano --Q 51.3 --tipo retorno                (presion necesita --p)
python scripts/oleohidraulica.py perdida --Q 26.2 --d 13 --L 3 --vg 46 --temp 10
python scripts/oleohidraulica.py pandeo --d 70 --L 450 --caso 3 --D 100 --p 160
python scripts/oleohidraulica.py acumulador --dV 0.4 --p1 140 --p2 160       (o --V0 10)
python scripts/oleohidraulica.py tanque --Q 26.2 [--movil]
python scripts/oleohidraulica.py calor --p 160 --Q 26.2 --area 1.14 --dT 25
```

## Errores frecuentes

- Tomar la presión de la bomba como si llegara entera al cilindro (sin las pérdidas de la línea), u olvidar el rendimiento.
- Dimensionar el retorno con el caudal de la bomba: al retroceder un cilindro con φ = 2 vuelve el doble.
- Regular la bajada estrangulando el lado del vástago sin revisar la intensificación (p · φ).
- Elegir el motor eléctrico con la presión de trabajo y no con la de la válvula de alivio.
- Calcular la pérdida de carga solo en caliente; en frío, en laminar, se multiplica por la relación de viscosidades.
- Usar presiones manométricas en la ley de Boyle, o precargar el acumulador por encima de 0,9 · p1.
- Verificar el pandeo con la carga nominal y sin el factor del montaje, o con Euler cuando λ ≤ λg.
- Dejar la bomba de caudal fijo empujando contra la válvula de alivio en reposo: toda su potencia se vuelve calor.
- Manguera elegida solo por diámetro, sin mirar su presión de trabajo.

## Verificación antes de entregar

1. `python scripts/oleohidraulica.py demo` termina en `DEMO OK`.
2. Fuerza útil ≥ fuerza pedida con el diámetro adoptado, y presión necesaria ≤ presión de la válvula de alivio menos las pérdidas de la línea.
3. Velocidades dentro de los rangos, tanto en el cilindro como en cada línea, con el caudal real de cada una (Q · φ donde corresponda).
4. Viscosidad dentro del rango de la bomba a la temperatura de trabajo y en el arranque en frío.
5. Mangueras, cilindro y válvulas con presión nominal mayor que la máxima posible (alivio o intensificación).
6. Pandeo verificado con la fuerza máxima y el montaje real.
7. Balance de calor: lo que se genera contra lo que disipa el tanque.
8. Datos de catálogo del componente elegido (cilindro, bomba, mangueras, acumulador) en lugar de los de ejemplo. Para una entrega, una revisión independiente con **equipo-de-modelos** o **revision-tecnica**.
