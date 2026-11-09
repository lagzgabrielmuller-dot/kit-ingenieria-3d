# Ensayos de dureza: detalle y tablas

Leer cuando hay que elegir la fuerza y la bola de un Brinell, comprobar si una huella es válida, elegir escala Rockwell o Vickers, o convertir una dureza. Normas: ISO 6506-1 (Brinell), ISO 6508-1 (Rockwell), ISO 6507-1 (Vickers), ISO 18265 (conversiones).

## 1. Brinell (ISO 6506-1:2014)

**Fórmula**: HBW = 0,102·2F/(π·D·(D − √(D² − d²))) = 0,102·F/(π·D·h), con F en N, D y d en mm y h = (D − √(D² − d²))/2. La constante 0,102 es 1/9,80665: con F en kgf la fórmula queda sin ella. d es el promedio de dos diámetros medidos a 90°.

**Índice de carga 0,102·F/D²** (tabla 3 de la norma):

| Material | Dureza | Índice |
|---|---|---|
| Acero, aleaciones de níquel y de titanio | | 30 |
| Fundición | menos de 140 HBW | 10 |
| | 140 HBW o más | 30 |
| Cobre y sus aleaciones | menos de 35 HBW | 5 |
| | 35 a 200 HBW | 10 |
| | más de 200 HBW | 30 |
| Metales livianos y sus aleaciones | menos de 35 HBW | 2,5 |
| | 35 a 80 HBW | 5, 10 o 15 |
| | más de 80 HBW | 10 o 15 |
| Plomo, estaño | | 1 |
| Metales sinterizados | | según ISO 4498 |

**Fuerza** = índice·D²·9,80665 [N] (= índice·D² en kgf):

| Bola D | Índice 30 | Índice 10 | Índice 5 | Índice 2,5 | Índice 1 |
|---|---|---|---|---|---|
| 10 mm | 29,42 kN (3000 kgf) | 9,807 kN (1000) | 4,903 kN (500) | 2,452 kN (250) | 980,7 N (100) |
| 5 mm | 7,355 kN (750) | 2,452 kN (250) | 1,226 kN (125) | 612,9 N (62,5) | 245,2 N (25) |
| 2,5 mm | 1,839 kN (187,5) | 612,9 N (62,5) | 306,5 N (31,25) | 153,2 N (15,625) | 61,29 N (6,25) |
| 1 mm | 294,2 N (30) | 98,07 N (10) | 49,03 N (5) | 24,52 N (2,5) | 9,807 N (1) |

Se usa la bola más grande que permita el espesor de la pieza. `python scripts/ensayos.py brinell --material acero --D 10 --sugerir` lista las opciones.

**Validez de la huella**: 0,24·D ≤ d ≤ 0,6·D. Con bola de 10 mm y 3000 kgf eso cubre de 653,5 HBW (d = 2,4 mm) a 95,5 HBW (d = 6,0 mm):

| d [mm] | h [mm] | Espesor mínimo 8·h [mm] | HBW 10/3000 |
|---|---|---|---|
| 2,4 | 0,146 | 1,17 | 653,5 |
| 3,0 | 0,230 | 1,84 | 414,6 |
| 4,0 | 0,417 | 3,34 | 228,8 |
| 5,0 | 0,670 | 5,36 | 142,6 |
| 6,0 | 1,000 | 8,00 | 95,5 |

**Condiciones**: espesor de la pieza ≥ 8·h (y que no se marque del otro lado); entre centros de huellas ≥ 3·d y del centro al borde ≥ 2,5·d; fuerza aplicada en 2 a 8 s y mantenida 10 a 15 s; superficie plana, lisa y limpia; pieza bien apoyada. El método llega hasta 650 HBW (por encima la bola se deforma: usar Vickers o Rockwell C).

**Designación**: valor, HBW, diámetro de la bola en mm, fuerza en kgf y, si no fue de 10 a 15 s, el tiempo: "215 HBW 10/3000"; "600 HBW 1/30/20" (bola de 1 mm, 30 kgf, 20 s). La "W" es por la bola de carburo de tungsteno: el viejo "HB" con bola de acero ya no se usa en la norma.

**Sensibilidad**: en el ejemplo (d = 4,12 mm) un error de 0,01 mm en d cambia HBW en 1,1 unidades; la incertidumbre relativa de HBW es ≈ 2,1 veces la de d. Por eso conviene medir con lupa o microscopio graduado y promediar.

## 2. Rockwell (ISO 6508-1)

Mide la **profundidad permanente** h entre la fuerza previa y la total: HR = N − h/S, con S = 0,002 mm; N = 100 con cono de diamante y 130 con bola.

| Escala | Indentador | Fuerza previa | Fuerza total | Campo de aplicación |
|---|---|---|---|---|
| A | Cono de diamante 120° | 98,07 N (10 kgf) | 588,4 N (60 kgf) | 20 a 88 HRA |
| B | Bola de 1,5875 mm | 98,07 N (10 kgf) | 980,7 N (100 kgf) | 20 a 100 HRB |
| C | Cono de diamante 120° | 98,07 N (10 kgf) | 1471 N (150 kgf) | 20 a 70 HRC |

Fuente de la tabla: IS 1586:2000 (norma india de ensayo Rockwell). Las ediciones actuales de ISO 6508-1 usan bola de carburo de tungsteno (HRBW) y pueden tener otros campos de aplicación: verificar en la vigente.

- h en el ejemplo: 60 HRC → (100 − 60)·0,002 = 0,080 mm; 80 HRBW → (130 − 80)·0,002 = 0,100 mm.
- Espesor mínimo: 10·h con cono (0,8 mm para 60 HRC) y 15·h con bola (1,5 mm para 80 HRBW).
- Distancias (misma fuente; verificar en la edición vigente de ISO 6508-1): entre centros ≥ 4 veces el diámetro de la huella; del centro al borde ≥ 2,5 veces.
- Ventajas: rápido, lectura directa, huella chica. Cuidado con superficies curvas (en cilindros chicos se aplica la corrección por curvatura de la norma), con la cascarilla o la descarburación superficial y con el apoyo: si la pieza se mueve, la lectura no sirve.
- Designación: "59 HRC", "80 HRBW".

## 3. Vickers (ISO 6507-1)

**Fórmula**: HV = 0,102·2F·sen(136°/2)/d² = 0,1891·F/d², con F en N y d = promedio de las dos diagonales en mm. Sirve para diagonales de 0,020 a 1,400 mm.

| Fuerza | Símbolo | Tipo de ensayo |
|---|---|---|
| F ≥ 49,03 N | HV 5 o más | Ensayo Vickers |
| 1,961 N ≤ F menor de 49,03 N | HV 0,2 a menos de HV 5 | Vickers de baja fuerza |
| 0,009807 N ≤ F menor de 1,961 N | HV 0,001 a menos de HV 0,2 | Microdureza Vickers |

- Espesor ≥ 1,5·d. Distancias: acero, cobre y sus aleaciones: centro al borde ≥ 2,5·d y entre centros ≥ 3·d; metales livianos, plomo y estaño: ≥ 3·d y ≥ 6·d.
- Fuerza aplicada en 2 a 8 s y mantenida 10 a 15 s (otro tiempo va en la designación: "640 HV 30/20" = 294,2 N durante 20 s).
- Mismo indentador para materiales blandos y templados: sirve para comparar, y la microdureza mide capas cementadas, nitruradas o zonas de una soldadura (perfil de durezas).
- Preparación: superficie pulida (más fina cuanto menor la fuerza), para ver bien los vértices de la huella.

## 4. Conversiones y relación con la tracción

- No hay fórmula exacta entre escalas: se usan las tablas de ISO 18265, que valen para grupos de materiales (por ejemplo aceros no aleados y de baja aleación) y dentro de rangos. Fuera de eso la conversión no tiene respaldo.
- Estimación de Rm desde Brinell, **solo aceros**: Rm [MPa] ≈ 3,55·HB si HB ≤ 175 y ≈ 3,38·HB si HB es mayor (guía de ensayos de dureza del centro alemán de información del acero inoxidable, ISER). Ejemplo: 215 HBW → Rm ≈ 727 MPa. Se informa como estimación, nunca en lugar de un ensayo de tracción.
- Para informar una conversión: "≈ … HV (convertido de 215 HBW con la tabla … de ISO 18265)", indicando la tabla usada.
