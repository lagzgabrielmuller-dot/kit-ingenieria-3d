---
name: informe-tecnico
description: "Informes técnicos, trabajos prácticos, memorias descriptivas y de cálculo, monografías y protocolos de visita de escuela técnica o ingeniería, en Word, PDF o Google Docs, con portada (escuela, materia, docente, integrantes), índice, secciones numeradas, tablas y figuras con epígrafe, ecuaciones, bibliografía y anexos, en español técnico formal. Incluye un generador de pedidos para escribir el informe en vivo en Google Docs con su conector (títulos, listas, fórmulas con superíndices, tablas y figuras), para que el usuario lo vea crecer sección por sección. Usar cuando se pida un informe, un trabajo práctico, una memoria técnica, una monografía o la documentación escrita de un proyecto, o cuando el usuario diga 'escribilo en Google Docs', 'no tengo Word' o 'quiero ver cómo lo vas escribiendo'."
---

# Informe técnico

Esta skill define **qué** va en el informe y **cómo se escribe**. El formato de entrega es el que pida la consigna; en la escuela suele ser Word y PDF.

- Para construir un archivo Word, si el entorno tiene una skill de documentos Word (docx), leerla y seguirla.
- Si el usuario no tiene Word, si el trabajo es grupal o si quiere ver el informe mientras se escribe, conviene Google Docs con su conector: ver la sección "En vivo en Google Docs".

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
- Unidades SI con espacio entre número y unidad (25 kW, 3,5 m) y coma decimal. Los miles se separan con un espacio (1 500 kg), como pide el SI: el folleto del SI (BIPM, 9.ª ed., 2019, §5.4.4) prohíbe puntos y comas entre los grupos de tres cifras. Si la cátedra pide punto para los miles, se usa lo que pida.
- Tablas numeradas con el título arriba ("Tabla 3 – Consumo de aire por puesto"); figuras numeradas con el epígrafe abajo ("Figura 2 – Esquema unifilar"); todas citadas en el texto.
- Ecuaciones numeradas, con el significado y la unidad de cada símbolo debajo.
- Cada dato sacado de un catálogo, una norma o una página va con su fuente. Nunca inventar marcas, modelos ni valores: si no se encuentra, decirlo.
- Página A4, márgenes de 2,5 cm, letra Arial o Calibri de 11 pt, títulos numerados (1, 1.1, 1.1.1), número de página en el pie y título corto en el encabezado.

## En vivo en Google Docs

`scripts/docs_bloques.py` (Python 3.9+, solo biblioteca estándar) arma los pedidos para el conector de Google Docs. Claude escribe cada sección como texto con marcas simples:

```
# Memoria de cálculo
La potencia del motor es P = 4~kW a 1450~rpm (dato de placa).
- **Corriente nominal**: 8,6~A
$$ C = P / ω = 4000~W / 151,8~rad/s ≈ 26,3~N·m
EPIGRAFE: Figura 3. Placa de características del motor.
```

Después el script calcula los índices y los estilos:

```
python docs_bloques.py texto seccion.txt --inicio <endIndex − 1> --rev <revisionId> [--doc-vacio] [--despues-de-lista]
python docs_bloques.py tabla --en N --filas filas.json --rev R [--color-encabezado 0.99,0.89,0.78] [--anchos 140,226,85]
python docs_bloques.py figuras --datos figuras.json --rev R
python docs_bloques.py indices lectura.json --buscar "Figura 1."
```

- Cada salida es el JSON listo para `update_doc`, con la protección `requiredRevisionId`.
- Va una sección por pedido, para que el usuario vea crecer el documento.
- Antes de cada pedido se vuelve a leer el documento, porque los índices cambian con cada escritura.

El paso a paso tiene: cómo abrir el documento con la cuenta correcta, en qué orden van las tablas, cómo insertar figuras sin compartirlas en público, la verificación con el PDF exportado y los errores frecuentes. Está en `references/google-docs-en-vivo.md`: leerlo antes de la primera escritura.

## Verificación antes de entregar

1. Convertir a PDF (`soffice --headless --convert-to pdf informe.docx`) y mirar todas las páginas: sin páginas en blanco, tablas que no se salgan del margen, figuras legibles, títulos que no queden solos al final de una página.
2. El índice tiene que tener los títulos y números de página reales. Si queda vacío en el PDF, actualizar los campos o armarlo a partir del PDF renderizado.
3. Recorrer la consigna punto por punto y confirmar que todo está.
4. Si se pidió una exposición oral: armar además un guion por integrante y una lista de preguntas probables con su respuesta (skill **exposicion-oral**).
5. Para un trabajo importante, control independiente antes de entregar (skill **revision-tecnica**).

Si piden corregir un informe que ya existe, editar ese archivo manteniendo su formato y decir qué se cambió.

`python docs_bloques.py demo` comprueba el armado de los pedidos (texto, estilos, listas, tabla y figuras) contra índices tomados de un documento real de Google Docs y termina en `DEMO OK`.
