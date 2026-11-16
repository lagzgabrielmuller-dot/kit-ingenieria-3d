# Ruido, estrés térmico y ventilación

Leer cuando haga falta el tiempo permitido para un nivel de ruido, cómo se arma la dosis de una jornada, cómo estimar un protector auditivo, los límites de TGBH o la tabla de ventilación por persona. Los mismos valores están cargados en `scripts/seguridad.py`. El criterio legal de ruido (85 dBA, 3 dB, dosis, pico) y el protocolo de medición están resumidos en **normas-tecnicas-ar**: acá no se repiten.

## Ruido: tiempo permitido por nivel

Regla de la Res. MTEySS 295/03, Anexo V (criterio de 85 dBA para 8 h e intercambio de 3 dB): T = 8 h/2^((L − 85)/3). Tiempos calculados con esa regla:

| L [dBA] | T por día | L [dBA] | T por día |
|---|---|---|---|
| 82 | 16 h | 112 | 56,25 s (0,94 min) |
| 85 | 8 h | 115 | 28,12 s |
| 88 | 4 h | 118 | 14,06 s |
| 91 | 2 h | 121 | 7,03 s |
| 94 | 1 h | 124 | 3,52 s |
| 97 | 30 min | 127 | 1,76 s |
| 100 | 15 min | 130 | 0,88 s |
| 103 | 7,50 min | 133 | 0,44 s |
| 106 | 3,75 min | 136 | 0,22 s |
| 109 | 1,88 min | 139 | 0,11 s |

- La guía práctica N.º 2 de la SRT usa 82 dBA → 16 h, 88 dBA → 4 h y 91 dBA → 2 h, que coinciden con la regla ([guía de ruido](https://www.srt.gob.ar/wp-content/uploads/2016/08/Guia_practica_2_Ruido_2016.pdf)).
- Para citar en un informe, tomar los valores de la Tabla 1 del Anexo V (verificar en la norma vigente): en las copias consultadas, la tabla no se pudo leer.
- Entre 80 y 82 dBA, el script usa la fila de 82 dBA (16 h), del lado seguro. Con la regla pura, 80 dBA darían 25,4 h.

## Ruido: dosis y nivel equivalente

- **Dosis:** D = Σ(Ci/Ti), con Ci el tiempo de exposición a cada nivel y Ti el permitido para ese nivel. Si la suma pasa de 1, se supera el valor límite (Res. 295/03, Anexo V). En la suma entran todas las exposiciones de 80 dBA o más.
- **Nivel continuo equivalente** en el tiempo de exposición Te: LAeq,Te = 10·log(Σ ti·10^(Li/10)/Te). Referido a 8 h: LAeq,8h = 10·log(Σ ti·10^(Li/10)/8 h).
- **Relación entre los dos:** D ≈ 10^((LAeq,8h − 85)/10). La diferencia es menor que 1 %, porque la regla usa 3 dB y la duplicación de energía es 3,01 dB.
- **Criterio de tabla** (guía práctica N.º 2 de la SRT):
  - cuando el nivel medido no figura en la tabla, se entra con la fila inmediata superior (87 dBA → fila de 88 dBA);
  - ejemplo 1 de la guía: 1 h a 88 dBA, 1 h a 91 dBA, 4 h a 82 dBA y 2 h a 87 dBA → D = 1/4 + 1/2 + 4/16 + 2/4 = 1,5 (cuenta hecha con los tiempos de la guía);
  - ejemplo 2: 8 h a 90 dBA, con la fila de 91 dBA → 2 h permitidas.
  - En el script: `ruido --criterio tabla`.
- **Medición** (misma guía):
  - con dosímetro fijado en 85 dBA y 3 dB, el resultado de toda la jornada es la dosis;
  - si se mide una parte representativa, se proyecta por proporción simple;
  - si se mide un ciclo, se multiplica por la cantidad de ciclos;
  - con sonómetro integrador: ponderación A y respuesta lenta.
- La medición que vale para la SRT es la del protocolo de la Res. SRT 85/12.

## Protectores auditivos

- El método del NRR es del apéndice B de OSHA 29 CFR 1910.95 (EE. UU.), «Methods for Estimating the Adequacy of Hearing Protector Attenuation»:
  - con medición ponderada C: L' = LC − NRR;
  - con medición ponderada A (dosímetro, sonómetro o medición de área): L' = LA − (NRR − 7).
- El apéndice no fija un factor de reducción adicional, pero advierte que el cálculo vale solo si el protector está bien colocado y se usa todo el turno.
- En la normativa argentina consultada no aparece un método de cálculo de la atenuación. El protector se elige con los datos del fabricante y el profesional de higiene y seguridad (verificar en la norma vigente).
- La guía de la SRT considera que los protectores de copa protegen más que los tapones si se usan bien. También recomienda rotar al personal para que no esté expuesto más de cuatro horas por día.
- Ejemplo del SKILL.md: LAeq,8h = 89,7 dBA y NRR 25 → 89,7 − 18 = 71,7 dBA bajo el protector.

## Estrés térmico (TGBH)

Fuente: Res. MTEySS 295/03, estrés térmico. Es el texto vigente del anexo del art. 60 del Dec. 351/79, según la [biblioteca de AFIP](https://biblioteca.afip.gob.ar/pdfp/A2_dec351_79.pdf).

- Con exposición directa al sol: TGBH = 0,7·TBH + 0,2·TG + 0,1·TBS.
- Sin exposición directa al sol (interiores): TGBH = 0,7·TBH + 0,3·TG.
- TBH: temperatura de bulbo húmedo natural; TG: de globo; TBS: de bulbo seco, todas en °C.

Valores límite de TGBH [°C]:

| Régimen de trabajo y descanso | Ligero | Moderado | Pesado |
|---|---|---|---|
| 100 % trabajo | 29,5 | 27,5 | 26 |
| 75 % trabajo, 25 % descanso | 30,5 | 28,5 | 27,5 |
| 50 % trabajo, 50 % descanso | 31,5 | 29,5 | 28,5 |
| 25 % trabajo, 75 % descanso | 32,5 | 31 | 30 |

- Para trabajo muy pesado, la resolución no da valores: pide un análisis detallado o control fisiológico.
- Corrección por ropa, que se suma al TGBH medido: uniforme de verano, 0 °C; buzo de tela, + 3,5 °C; buzo de doble tela, + 5 °C.
- La corrección no vale para trajes herméticos ni para ropa impermeable o muy resistente al vapor de agua.
- Ejemplos del SKILL.md:
  - interior, TBH 24 °C y TG 32 °C → 26,4 °C, que verifica para trabajo moderado al 100 % (límite 27,5 °C);
  - con buzo de tela, 29,9 °C: verifica solo con 25 % de trabajo (31 °C);
  - con sol, TBH 25 °C, TG 40 °C y TBS 33 °C → 28,8 °C.

## Ventilación mínima por persona

Fuente: Dec. 351/79, Anexo I, art. 66 (cap. 11), según la [biblioteca de AFIP](https://biblioteca.afip.gob.ar/pdfp/A1_dec351_79.pdf).

| Cubaje del local por persona [m³] | Caudal, actividad sedentaria [m³/h por persona] | Caudal, actividad moderada [m³/h por persona] |
|---|---|---|
| 3 | 43 | 65 |
| 6 | 29 | 43 |
| 9 | 21 | 31 |
| 12 | 15 | 23 |
| 15 | 12 | 18 |

- Para un cubaje intermedio, el script toma la fila de cubaje inmediata inferior, que pide más aire (lado seguro). El artículo no dice cómo interpolar.
- Con menos de 3 m³ por persona, la tabla no da valor: hay que revisar el local.
- Ejemplo: 6 personas en 60 m³ con actividad sedentaria → fila de 9 m³ → 6·21 = 126 m³/h, es decir 2,1 renovaciones por hora.
- Si hay contaminantes, el caudal se calcula para mantenerlos por debajo de los valores de la Res. 295/03. Ese cálculo no es el de esta tabla.
