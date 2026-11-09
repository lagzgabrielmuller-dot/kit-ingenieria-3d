# Instalaciones eléctricas: AEA 90364, puesta a tierra, conductores y símbolos

Leer este archivo cuando un trabajo tenga que elegir la parte de la reglamentación AEA, citar un valor eléctrico (caída de tensión, diferencial, puesta a tierra, secciones, grados de electrificación) o nombrar las normas de cables y materiales. El cálculo de conductores y caída de tensión está en la skill **calculos-ingenieria**.

## La reglamentación AEA 90364

La edita la Asociación Electrotécnica Argentina y se compra en papel o digital en la [tienda AEA](https://aea.org.ar/categoria-producto/reglamentaciones/). Es exigible cuando la adopta una autoridad: por ejemplo, la Res. SRT 900/15 manda a actuar si las mediciones no cumplen la reglamentación de la AEA.

| Documento | Título | Edición | Fuente de la edición |
|---|---|---|---|
| AEA 90364 partes 0 a 3 | Guía de aplicación; alcance, objeto y principios fundamentales; definiciones; determinación de las características generales de las instalaciones | 2025 (un tomo) | [tienda AEA](https://aea.org.ar/producto/aea-90364-partes-0a3-edicion-2025/) |
| AEA 90364-4 | Protecciones para preservar la seguridad | 2006 | tienda AEA |
| AEA 90364-5 | Elección e instalación de los materiales eléctricos | 2006 | tienda AEA |
| AEA 90364-6 | Verificación de las instalaciones eléctricas | 2025 | [tienda AEA](https://aea.org.ar/producto/verificacion-de-las-instalaciones-electricas/) |
| AEA 90364-7-701 | Cuartos de baño | 2012 | lista AEA 2019 |
| AEA 90364-7-702 | Piscinas y fuentes ornamentales | 2018 | lista AEA 2019 |
| AEA 90364-7-704 | Lugares de construcción, obras, demoliciones, obradores y lugares análogos | 2026 | [tienda AEA](https://aea.org.ar/producto/aea-90364-7-704-instalaciones-en-lugares-de-construccion-obras-demoliciones-obradores-y-lugares-analogos-edicion-2026/) |
| AEA 90364-7-710 | Locales para usos médicos y salas externas a los mismos | 2008 | lista AEA 2019 |
| AEA 90364-7-711 | Instalaciones eléctricas en eventos | 2021 | tienda AEA |
| AEA 90364-7-712 | Sistemas de suministro con paneles solares fotovoltaicos | 2015 | lista AEA 2019 |
| AEA 90364-7-718 | Lugares y locales de pública concurrencia | 2008 | lista AEA 2019 |
| AEA 90364-7-722 | Vehículos eléctricos | 2018 | lista AEA 2019 |
| AEA 90364-7-770 | Viviendas unifamiliares (hasta 63 A, clasificaciones BA2 y BD1) | 2017 | lista AEA 2019 |
| AEA 90364-7-771 | Viviendas, oficinas y locales (unitarios) | 2006 | lista AEA 2019 |
| AEA 90364-7-772 | Instalaciones de espacios comunes y servicios generales | 2019 | lista AEA 2019 |
| AEA 90364-8-1 | Eficiencia energética en las instalaciones eléctricas de baja tensión, sección 1 | 2019 | lista AEA 2019 |
| Guía AEA 770 | Instalaciones eléctricas en viviendas unifamiliares hasta 10 kW | 2018 | [tienda AEA](https://aea.org.ar/producto/guia-aea-770/) |
| AEA 95150 | Suministro y medición en baja tensión | 2007 | lista AEA 2019 |
| AEA 95403 | Inmuebles de tensión nominal mayor a 1 kV y hasta 36 kV en CA | 2018 | tienda AEA |
| AEA 92305 (IRAM 2184) | Protección contra rayos (partes 1 a 4 y 11) | 2015 y 2016 | lista AEA 2019 |

"Lista AEA 2019" es la [lista de documentos vigentes](https://aea.org.ar/wp-content/uploads/2019/10/Lista-de-Documentos-Vigentes-AEA.pdf) que publicó la AEA; puede haber ediciones más nuevas: confirmar en la tienda antes de citar.

**¿770 o 771?** La 770 (2017) es para viviendas unifamiliares de hasta 63 A con condiciones BA2 y BD1; la 771 (2006) para viviendas, oficinas y locales unitarios en general. Se usa la que pida la consigna; si no dice, se confirma el alcance en la cláusula 1 de cada sección y se aclara en el informe cuál se usó.

## Valores de la AEA 90364-7-770:2017

Tomados del texto completo publicado por la [Municipalidad de Junín](https://www.junin.gob.ar/sites/default/files/programas/archivos/reglamento_aea.pdf):

| Tema | Valor | Cláusula |
|---|---|---|
| Caída de tensión | Circuitos terminales de uso general o especial, para iluminación y tomacorrientes: 3 %. Circuitos que alimentan solo motores: 5 % en régimen y 15 % durante el arranque | 770.15.6 |
| Diferencial | Todos los circuitos terminales protegidos además contra contactos directos con un diferencial de IΔn ≤ 30 mA (es protección complementaria, no completa) | 770.14.2.3 |
| Puesta a tierra de protección | Resistencia máxima permanente ≤ 40 Ω; electrodo: jabalina cilíndrica acero-cobre IRAM 2309 (la Tabla 770.3.I cita IRAM 2309 e IRAM 2310) | 770.14.4.1, 770.14.4.3 |
| Conductor de protección (PE) | Nunca menor que 2,5 mm² | 770.14.4.5 |
| Secciones mínimas | Líneas principales 4 mm²; circuitos seccionales 2,5 mm²; circuitos terminales de tomacorrientes de uso general 2,5 mm²; de iluminación de uso general 1,5 mm² | Tabla 770.11.I |
| Grados de electrificación | Mínimo hasta 60 m²; medio más de 60 hasta 130 m²; elevado más de 130 hasta 200 m²; superior más de 200 m² | Tabla 770.7.I |
| Circuitos mínimos | Mínimo 2 (uno de iluminación y uno de tomacorrientes de uso general); medio 3; elevado 5; superior 6 | 770.7.4, Tabla 770.7.II |
| Bocas por cañería | Si varios circuitos de uso general comparten una cañería, el total de bocas que alimentan no supera 15 | 770.10.3.8.2 d) |
| Resistencia de aislación | MBTS/MBTF: ensayo a 250 V cc, ≥ 0,5 MΩ; hasta 500 V: 500 V cc, ≥ 1 MΩ; más de 500 V: 1000 V cc, ≥ 1 MΩ | Tabla 770.19.I (corrigendum 1 de 2018, publicado por el [GCBA](https://static.buenosaires.gob.ar/sites/default/files/media/document/2019/02/27/e1d0af388d98fe05551af18a30918ecb8abc9da2.pdf)) |

En la 770 el grado de electrificación sale de la superficie; la demanda de potencia máxima simultánea se calcula aparte (770.8.1, Tabla 770.8.I).

## Lo que se pudo confirmar de la AEA 90364-7-771:2006

- El [prólogo e índice](https://aea.org.ar/wp-content/uploads/2017/10/90364-7-771-2.pdf) que publica la AEA dice que la resistencia máxima de puesta a tierra de protección pasó de 10 a 40 Ω (771.3.3.1), con una tabla de valores admisibles según la corriente diferencial, y que la sección mínima de los circuitos de iluminación de uso general bajó a 1,5 mm² (771.13).
- La [guía práctica de la Res. SRT 900/15](https://argentina.gob.ar/sites/default/files/res_srt_900_15-guia-practica_0.pdf) cita de la 771: en esquema TT, Ra máxima de 40 Ω siempre que el diferencial no supere IΔn = 300 mA (la Tabla 771.3.I da Ra para cada IΔn); los circuitos terminales de iluminación y tomacorrientes de hasta 32 A llevan diferencial de IΔn ≤ 30 mA. La misma guía considera aceptable en TN-S una puesta a tierra del neutro de 2 Ω o menos (1 Ω o menos si se puede) y recomienda 10 Ω o menos para pararrayos.
- Caídas de tensión: cláusula 771.19.7; grados de electrificación y demanda: cláusula 771.8. Los valores de esas cláusulas no se pudieron leer en una fuente pública: tomarlos de la norma (verificar en la norma vigente).

## Puesta a tierra

| Documento | Título | Edición |
|---|---|---|
| AEA 95501-1 (IRAM 2281-1) | Puesta a tierra de sistemas eléctricos. Parte 1: Consideraciones generales | 2026 |
| AEA 95501-2 (IRAM 2281-2) | Parte 2: Guía de mediciones de magnitudes de puesta a tierra (resistividades, resistencias, impedancias y gradientes) | 2021 |
| AEA 95501-3 (IRAM 2281-3) | Parte 3: Instalaciones con tensiones nominales menores o iguales a 1 kV | 2024 |

Fuente: [tienda AEA](https://aea.org.ar/categoria-producto/reglamentaciones/). Medición en lugares de trabajo: Res. SRT 900/15 (protocolo obligatorio, validez 12 meses); su guía aconseja probar los dispositivos de protección con frecuencia mensual para verificar su funcionamiento mecánico.

## Conductores y materiales

Normas citadas por la AEA 90364-7-770 (texto de la Municipalidad de Junín) y por fichas de fabricante. Las descripciones no son los títulos oficiales: el título exacto y la edición se confirman en el [catálogo IRAM](https://www.iram.org.ar/normalizacion/busca-tu-norma/).

| Norma | Qué es | Fuente |
|---|---|---|
| IRAM NM 247-3 | Conductores unipolares aislados en PVC, sin envoltura, hasta 450/750 V, para instalaciones fijas (norma Mercosur basada en IEC 60227-3); en cañerías o bandejas | AEA 770 (770.10.2 a); ficha [Prysmian Superastic Jet](https://ar.prysmian.com/sites/ar.prysmian.com/files/media/documents/PRY2020_Superastic%20Jet.pdf) |
| IRAM 62267 | Igual uso que la NM 247-3, con aislación de baja emisión de humos y libre de halógenos (LS0H), hasta 450/750 V | AEA 770; ficha [Prysmian Afumex Green](https://ar.prysmian.com/sites/ar.prysmian.com/files/media/documents/PRY2024_Afumex%20Green_V3final.pdf) |
| IRAM 2178-1 | Cables con envoltura de protección, 0,6/1 kV (por ejemplo, PVC), para tendidos subterráneos o en bandejas | AEA 770 (770.10.2 b); ficha [Prysmian Sintenax Valio](https://ar.prysmian.com/sites/ar.prysmian.com/files/media/documents/PRY2026_Sintenax%20Valio_v2.pdf) |
| IRAM 62266 | Alternativa a la IRAM 2178-1 para cables con envoltura | AEA 770 (770.10.2 b) |
| IRAM NM 247-5, IRAM 2039, IRAM 2188 | Cordones y cables flexibles: no se admiten en instalaciones fijas | AEA 770 (770.10.1 k) |
| IRAM NM-280 / IEC 60228 | Conductores (clases de flexibilidad, por ejemplo clase 5) | ficha Prysmian |
| IRAM NM IEC 60332-1 y 60332-3-23 | Ensayos de no propagación de la llama (un cable) y del incendio (cables en haz, categoría B) | AEA 770; ficha Prysmian |
| IRAM 62386 (IEC 61386) | Caños para instalaciones (rígidos, curvables, flexibles) | AEA 770 |
| IRAM 2005, 2224, 62005, 62224, 2346 | Cajas | AEA 770 |
| IRAM 62084 (IEC 61084) | Cablecanales | AEA 770 |
| IRAM 2071 | Tomacorrientes 2P+T | AEA 770 |
| IRAM 2444 / IEC 60529; IEC 62262 | Grado de protección IP; grado IK contra impactos | AEA 770 |
| IRAM 2309, IRAM 2310 | Jabalinas cilíndricas para puesta a tierra | AEA 770 |

## Símbolos eléctricos

- **IEC 60617**: base de datos oficial de símbolos gráficos para esquemas (unos 1900 símbolos), con acceso por suscripción: [std.iec.ch/iec60617](https://std.iec.ch/iec60617).
- No se confirmó una norma IRAM vigente de simbología eléctrica. Si la cátedra pide símbolos IRAM, verificar el número en el catálogo IRAM antes de citarla.
- Para dibujar el unifilar o el esquema, ver la skill **planos-tecnicos**.
