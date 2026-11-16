# Recurso solar: fuentes, HSP, inclinación y sombras

Leer este archivo para elegir de dónde sacar las horas de sol pico (HSP), para consultar cada fuente, para citar la tabla de ciudades o los datos del punto del ejemplo, y para justificar la inclinación, la orientación y la separación entre filas.

## Definiciones

- **Irradiancia** G [W/m²]: potencia que llega por unidad de superficie. Las condiciones estándar de ensayo (STC) de un módulo son 1000 W/m², 25 °C de celda y AM 1,5 (hoja de datos del módulo).
- **Irradiación** H [kWh/m²]: energía en un período (día, mes o año). Global horizontal (GHI), difusa horizontal (DIF) y en el plano inclinado de los módulos (GTI o H_T).
- **HSP** [h/día] = H_T [kWh/m²·día] / 1 kW/m²: horas equivalentes a 1000 W/m² sobre el plano de los módulos. El *Manual de generación distribuida solar fotovoltaica* lo usa así: 7 kWh/m² en un día son 7 horas a 1000 W/m².
- PVGIS y el Global Solar Atlas dan **totales del mes** (kWh/m² en el mes): se dividen por los días del mes. El Atlas argentino y NASA POWER dan **medias diarias**.
- La HSP que sirve es la del **plano de los módulos**. Los mapas del Atlas son de irradiación horizontal: hay que pasarla a la inclinación elegida (tablas del Anexo II de la Guía, PVGIS o el comando `inclinacion`).

## Fuentes que cubren la Argentina

| Fuente | Qué da | Cobertura | Cómo se consulta |
|---|---|---|---|
| *Atlas de Energía Solar de la República Argentina*, H. Grossi Gallegos y R. Righini (Universidad Nacional de Luján), 1.ª ed., mayo de 2007, ISBN 978-987-9285-36-7; edición financiada por la SECyT y la UNLu | 12 mapas de la irradiación global horizontal media diaria (kWh/m²·día), isolíneas cada 0,5 kWh/m²·día, y mapas de heliofanía efectiva; datos medidos en tierra hasta 1997, incertidumbre de no más de un 10 % | Todo el país | Se lee la isolínea del mes en el mapa. [Copia en PDF publicada por el CAI](https://www.cai.org.ar/wp-content/uploads/cursos/2018/eficiencia-energetica/03/Atlas_de_energia_solar_de_la_Argentina.pdf) |
| *Guía del recurso solar*, Subsecretaría de Energías Renovables y Eficiencia Energética, 1.ª ed. revisada, febrero de 2019 | Anexo I: mapas mensuales de irradiación horizontal (del Atlas). Anexo II: coeficientes H_T/H por jurisdicción, inclinaciones de 0° a 90° cada 5° y azimut de 0° a 60° cada 15° (modelo de Perez, albedo 0,2). Anexo III: discos de pérdidas por orientación. Anexo IV: trayectorias solares. Anexo V: pérdidas por sombras. Anexo VI: temperaturas medias mensuales de 87 estaciones del SMN | Todas las provincias | H horizontal del mapa × coeficiente del Anexo II = H en el plano. [PDF de anexos](https://www.argentina.gob.ar/sites/default/files/guia_del_recurso_solar_anexos_final.pdf) |
| PVGIS 5.3 (Centro Común de Investigación, Comisión Europea), versión de producción desde septiembre de 2024 | Irradiación mensual horizontal, a la inclinación óptima anual o a la elegida, difusa, temperatura; producción de un sistema a red (PVcalc) o aislado (SHScalc) | Base satelital PVGIS-SARAH3, por defecto en «Europa, Asia Central, África y Sudamérica (en parte)»; donde no llega el satélite, PVGIS-ERA5 (reanálisis de cobertura mundial). En PVGIS 5.2 la base por defecto para Sudamérica al sur de 20° S era SARAH2. Confirmar en el mapa de cobertura qué base usa el punto | Web o API: `https://re.jrc.ec.europa.eu/api/v5_3/MRcalc?lat=-33.89&lon=-60.57&horirrad=1&optrad=1&selectrad=1&angle=45&d2g=1&avtemp=1&outputformat=json`. Ver el [manual de usuario](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/pvgis-user-manual_en) y el [servicio no interactivo](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/using-pvgis-5/api-non-interactive-service_en) |
| NASA POWER (NASA Langley) | Climatología mensual: ALLSKY_SFC_SW_DWN (global horizontal), ALLSKY_SFC_SW_DIFF (difusa), T2M (temperatura), SI_EF_OPTIMAL (plano a la inclinación óptima) | Mundial; radiación desde 1984; radiación de SRB v4 y CERES SYN1deg | API: `https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_DIFF,T2M&community=RE&longitude=-60.57&latitude=-33.89&format=JSON` ([documentación](https://power.larc.nasa.gov/docs/services/api/temporal/climatology/)). La unidad sale en el encabezado de la respuesta (verificar que sea kWh/m²·día) |
| Global Solar Atlas 2 (Banco Mundial y ESMAP, datos de Solargis) | GHI, DIF, DNI, GTI a la inclinación óptima (OPTA), OPTA, temperatura media y producción específica PVOUT (kWh/kWp), mensuales y anuales | Mundial | Web o `https://api.globalsolaratlas.info/data/lta?loc=-33.89,-60.57`; en la consulta del 16/11/2026 la respuesta decía: modelo Solargis 2.2.68 actualizado el 1/4/2026, temperatura de «ERA (ECMWF)» 1994-2025 |

Datos de PVGIS para el diseño: recomienda 14 % de pérdidas del sistema para un sistema a red (inversor, cables, dispersión y envejecimiento de alrededor de 0,5 % por año); en un aislado no deja elegir pérdidas y usa un rendimiento global de 0,67; corte de descarga por defecto 40 % (plomo) y 20 % sugerido para litio ([manual de usuario de PVGIS](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/pvgis-user-manual_en); [fuentes de datos y métodos](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/general-information/data-sources-calculation-methods_en)).

**Contraste con mediciones.** La red solarimétrica pampeana de la Universidad Nacional de Luján midió en junio 2,33 kWh/m²·día en Pergamino, contra 2,26 de NASA (unos dos años de medición; R. Righini y R. Aristegui, [*Análisis de datos de la Red Solarimétrica Pampeana*](https://www.gersolar.unlu.edu.ar/sites/www.gersolar.unlu.edu.ar/files/site/An%C3%A1lisis%20de%20datos%20de%20la%20Red%20Solarim%C3%A9trica%20Pampeana.pdf), GERSolar, sin fecha). El Global Solar Atlas da 2,38 para el punto del ejemplo: 2,2 % más que la medición. Las [nuevas cartas de la Pampa Húmeda](https://www.gersolar.unlu.edu.ar/sites/www.gersolar.unlu.edu.ar/files/site/ATLAS_PAMPA_HUMEDA_GERsolar_V2.pdf) del mismo grupo (mediciones hasta 2018) dan medias mensuales que difieren de la real en un 10 % como máximo, con 90 % de confianza.

## Tabla orientativa de ciudades

Global Solar Atlas 2, consulta del 16/11/2026 al API (`data/lta`) en el punto indicado. HSP = GTI a la inclinación óptima anual (OPTA) dividido por los días del período. Son valores modelados por Solargis para ese punto: para un proyecto se consulta el lugar exacto.

| Ciudad | Punto (lat; lon) | OPTA | HSP media anual a OPTA [h/día] | HSP junio a OPTA | HSP diciembre a OPTA | GHI anual [kWh/m²] | PVOUT [kWh/kWp·año] |
|---|---|---|---|---|---|---|---|
| Zona rural cercana a Pergamino (ejemplo) | −33,89; −60,57 | 30° | 5,51 | 3,75 | 6,78 | 1783 | 1627 |
| Ciudad de Buenos Aires | −34,60; −58,38 | 30° | 5,41 | 3,67 | 6,82 | 1753 | 1606 |
| Córdoba | −31,42; −64,18 | 30° | 5,77 | 4,58 | 6,55 | 1874 | 1698 |
| Rosario | −32,95; −60,65 | 29° | 5,57 | 3,81 | 6,75 | 1815 | 1639 |
| Mendoza | −32,89; −68,83 | 31° | 6,13 | 4,66 | 7,26 | 1970 | 1799 |
| Salta | −24,79; −65,41 | 25° | 5,48 | 4,78 | 5,59 | 1853 | 1613 |
| Posadas | −27,37; −55,90 | 24° | 5,34 | 3,74 | 6,33 | 1807 | 1556 |
| Neuquén | −38,95; −68,06 | 34° | 5,94 | 3,51 | 7,79 | 1855 | 1739 |
| Bahía Blanca | −38,72; −62,27 | 34° | 5,58 | 3,62 | 7,20 | 1744 | 1653 |
| Comodoro Rivadavia | −45,86; −67,48 | 40° | 4,85 | 1,53 | 6,88 | 1507 | 1573 |

El invierno manda en los aislados: la HSP de junio va del 22 % (Comodoro Rivadavia) al 86 % (Salta) de la de diciembre, y en la región pampeana ronda el 55 %.

## Punto del ejemplo, mes a mes

Global Solar Atlas 2, punto −33,89; −60,57 (zona rural cercana a Pergamino, provincia de Buenos Aires), consulta del 16/11/2026. Son los datos que carga `scripts/fotovoltaica.py` (`GSA`).

| | ene | feb | mar | abr | may | jun | jul | ago | sep | oct | nov | dic | año |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GHI [kWh/m²·mes] | 224,7 | 179,2 | 160,2 | 114,0 | 88,1 | 71,5 | 80,9 | 109,6 | 139,7 | 177,9 | 206,0 | 231,0 | 1783 |
| DIF [kWh/m²·mes] | 67,0 | 57,2 | 52,6 | 38,1 | 32,8 | 26,7 | 29,5 | 39,5 | 47,8 | 59,6 | 61,7 | 68,5 | 581 |
| GTI a 30° [kWh/m²·mes] | 210,0 | 182,3 | 184,6 | 150,5 | 130,1 | 112,5 | 124,0 | 151,1 | 168,3 | 188,8 | 197,0 | 210,1 | 2009 |
| HSP a 30° [h/día] | 6,77 | 6,51 | 5,95 | 5,02 | 4,20 | 3,75 | 4,00 | 4,87 | 5,61 | 6,09 | 6,57 | 6,78 | 5,51 |
| Temperatura media [°C] | 24,4 | 22,9 | 21,1 | 17,4 | 13,9 | 10,9 | 10,2 | 12,1 | 14,4 | 17,4 | 20,7 | 23,2 | 17,4 |
| PVOUT [kWh/kWp·mes] | 162,9 | 143,1 | 147,4 | 123,7 | 110,1 | 97,2 | 106,9 | 127,1 | 138,0 | 151,6 | 155,0 | 163,4 | 1627 |

El PR anual implícito del Global Solar Atlas es 1627/2009 = 0,81. La temperatura es una media mensual: para la mínima de diseño (Voc en frío) hace falta la mínima absoluta del lugar, que se pide al SMN.

## Inclinación y orientación

- **Orientación:** al norte. «Para sistemas ubicados en el hemisferio sur, la dirección Norte es la orientación óptima» ([*Manual de generación distribuida solar fotovoltaica*](https://argentina.gob.ar/sites/default/files/manual_de_generacion_distribuida_solar_fotovoltaica_vf_8mb.pdf), Subsecretaría de Energías Renovables y Eficiencia Energética, diciembre de 2019).
- **Máxima energía anual:** cerca de la latitud, algunos grados menos. Para la Ciudad de Buenos Aires el máximo está en 33° (disco de irradiación del Manual de GD); el Global Solar Atlas da 30° en el punto del ejemplo y de 24° (Posadas) a 40° (Comodoro Rivadavia) en la tabla de arriba.
- **Aislado con consumo parejo todo el año:** el mes crítico es junio y conviene más inclinación. El pliego de instalaciones aisladas del IDAE (España, hemisferio norte) da como inclinación óptima φ + 10° si el período de diseño es diciembre (su invierno), φ − 20° para julio y φ − 10° para todo el año (tabla III del [PCT-A-REV, febrero de 2009](https://www.solarweb.net/forosolar/attachments/fotovoltaica-sistemas-aislados-la-red/2330d1295707309-hola-soy-dingdon-pct-a30.pdf)). En la Argentina el invierno es junio: |φ| + 10°. Su regla anual (|φ| − 10°) da menos que el óptimo de las fuentes locales (24° contra 30° en el ejemplo): para el año se usa el valor de la fuente del lugar.
- **Pérdidas admisibles:** el Manual de GD fija en 10 % el límite de pérdidas por una inclinación y orientación no adecuadas. El IDAE, para aislados: hasta 20 % por orientación e inclinación, hasta 10 % por sombras y 20 % las dos juntas, con el factor FI = 1 − [1,2·10⁻⁴·(β − β_opt)² + 3,5·10⁻⁵·α²] para 15° < β < 90° (α: azimut).
- **Comando `inclinacion`:** modelo isotrópico de Liu y Jordan, H_T = (H − Hd)·R̄b + Hd·(1 + cos β)/2 + H·ρ·(1 − cos β)/2, con R̄b de Klein (1977) para una superficie que mira al ecuador (en el hemisferio sur, la inclinada β equivale a una horizontal en la latitud φ + β), declinación de Cooper δ = 23,45°·sen(360°·(284 + n)/365), día medio de cada mes de Klein (17, 47, 75, 105, 135, 162, 198, 228, 258, 288, 318 y 344) y albedo 0,2, el mismo de la Guía (J. A. Duffie y W. A. Beckman, *Solar Engineering of Thermal Processes*, Wiley, 4.ª ed., 2013, cap. 2). En el punto del ejemplo, a 30°, queda entre 2,6 % y 4,9 % por debajo del GTI del Global Solar Atlas (que usa un modelo anisotrópico): sesgo conservador. Resultados para ese punto: máximo anual en 27°; junio con 3,66 h/día a 30°, 4,01 a 45° (9,6 % más) y 4,13 a 60°.

## Sombras

- **Separación entre filas** (Manual de GD, ec. 2): cada fila tiene que recibir al menos 4 horas de sol el día en que el sol está más bajo. d = h/tg αc, con h = L·sen β la altura del módulo y αc = 90° − |φ| − 23,5° − 7°. Ejemplo del Manual: módulos de 1 m a 40° en Buenos Aires, d = 1,38 m (el demo lo reproduce con φ = 34,6° S). El paso entre filas es d + L·cos β.
- **Obstáculos:** trayectorias solares (Anexo IV de la Guía) y tablas de pérdidas por sombras (Anexo V). PVGIS tiene en cuenta el horizonte del terreno (`usehorizon`) y acepta uno medido (`userhorizon`).
- En serie la corriente es la misma para todos los módulos: un módulo sombreado limita al string hasta que conducen sus diodos de bypass. Conviene que una sombra previsible caiga sobre un solo string.
