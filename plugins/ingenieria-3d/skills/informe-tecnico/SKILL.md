---
name: informe-tecnico
description: "Informes técnicos, trabajos prácticos, memorias descriptivas y de cálculo, monografías y protocolos de visita de escuela técnica o ingeniería, en Word y PDF, con portada (escuela, materia, docente, integrantes), índice, secciones numeradas, tablas y figuras con epígrafe, ecuaciones, bibliografía y anexos, en español técnico formal. Usar cuando se pida un informe, un trabajo práctico, una memoria técnica, una monografía o la documentación escrita de un proyecto."
---

# Informe técnico

Esta skill define **qué** va en el informe y **cómo se escribe**. Para construir el archivo, si el entorno tiene una skill de documentos Word (docx), leerla y seguirla. El formato de entrega es el que pida la consigna; en la escuela suele ser Word y PDF.

## Antes de escribir

- La **consigna manda**: copiar su lista de puntos y verificar al final que cada uno esté respondido, con el mismo nombre o número.
- Datos de portada: escuela, especialidad y curso, materia, docente, título, integrantes (orden alfabético), lugar y fecha. Usar los que se conozcan; los que falten van como `[COMPLETAR]` resaltado en amarillo, nunca inventados.
- Si el informe acompaña un proyecto con planos, modelo 3D o cálculos, usar esos resultados (skills planos-tecnicos, modelado-3d-cad, calculos-ingenieria) para que todo coincida: mismos códigos de equipos, mismos valores.

## Estructura de referencia (adaptar a la consigna)

1. **Portada.**
2. **Índice** automático (y de tablas y figuras si son muchas).
3. **Introducción**: contexto, objetivo general y específicos, alcance.
4. **Marco teórico y normativa**: solo lo que se usa después.
5. **Memoria descriptiva**: qué es, dónde, cómo funciona, proceso paso a paso.
6. **Memoria de cálculo**: fórmula → datos → reemplazo → resultado con unidades → valor adoptado → verificación.
7. **Selección de equipos**: tabla con marca, modelo, datos técnicos y fuente (link a la ficha).
8. **Planos**: lista de láminas con número, título y escala, y miniaturas.
9. **Presupuesto**, si se pide.
10. **Seguridad e higiene** (Ley 19.587 y Dec. 351/79) e **impacto ambiental**, si aplican.
11. **Conclusiones**: qué se logró, valores clave, limitaciones y mejoras posibles.
12. **Bibliografía** (APA o el formato de la cátedra) y **anexos** (catálogos, cálculos completos, código).

Para un protocolo de visita técnica: datos de la empresa, proceso observado, equipos e instalaciones, seguridad, preguntas realizadas y conclusiones, siguiendo los bloques del protocolo de la escuela.

## Cómo se escribe

- Español técnico formal, impersonal: "se calculó", "se adoptó", "se verificó". Oraciones cortas y concretas; nada de relleno.
- Unidades SI con espacio entre número y unidad (25 kW, 3,5 m), coma decimal y punto para miles (1.500 kg).
- Tablas numeradas con el título arriba ("Tabla 3 – Consumo de aire por puesto"); figuras numeradas con el epígrafe abajo ("Figura 2 – Esquema unifilar"); todas citadas en el texto.
- Ecuaciones numeradas, con el significado y la unidad de cada símbolo debajo.
- Cada dato sacado de un catálogo, una norma o una página va con su fuente. Nunca inventar marcas, modelos ni valores: si no se encuentra, decirlo.
- Página A4, márgenes de 2,5 cm, letra Arial o Calibri de 11 pt, títulos numerados (1, 1.1, 1.1.1), número de página en el pie y título corto en el encabezado.

## Verificación antes de entregar

1. Convertir a PDF (`soffice --headless --convert-to pdf informe.docx`) y mirar todas las páginas: sin páginas en blanco, tablas que no se salgan del margen, figuras legibles, títulos que no queden solos al final de una página.
2. El índice tiene que tener los títulos y números de página reales. Si queda vacío en el PDF, actualizar los campos o armarlo a partir del PDF renderizado.
3. Recorrer la consigna punto por punto y confirmar que todo está.
4. Si se pidió una exposición oral: armar además un guion por integrante y una lista de preguntas probables con su respuesta.

Si piden corregir un informe que ya existe, editar ese archivo manteniendo su formato y decir qué se cambió.
