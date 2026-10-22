# Créditos: ciencia y cálculo (comunidad)

26 skills de [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) (K-Dense Inc.), licencia MIT (texto completo en `licencias/claude-scientific-skills-MIT.txt`), copiadas **sin modificaciones** del commit `593377bb048752abb0152deab9fbb1083a6087df`.

| Skill | Para qué sirve en electromecánica |
|---|---|
| `sympy` | Despejar, derivar e integrar ecuaciones; resolver sistemas |
| `matplotlib`, `scientific-visualization` | Curvas y gráficos prolijos para informes |
| `uncertainty-and-units` | Unidades e incertidumbre de mediciones (ensayos de laboratorio) |
| `statistical-analysis` | Análisis estadístico de datos medidos |
| `simpy` | Simular líneas de producción, colas y tiempos de máquina |
| `pymoo` | Optimización con varios objetivos (costo, peso, rendimiento) |
| `matlab` | Programas en MATLAB o GNU Octave |
| `cantera` | Combustión y reactores químicos |
| `markitdown` | Pasar PDF, Word, Excel y PowerPoint a texto para analizarlos |
| `markdown-mermaid-writing` | Documentación con diagramas Mermaid |
| `pptx-posters` | Pósters editables en PowerPoint (exposiciones, olimpíadas) |

Sumadas en la segunda tanda (mismo commit):

| Skill | Para qué sirve |
|---|---|
| `exploratory-data-analysis` | Primera mirada a una planilla o archivo de datos: faltantes, valores raros, distribuciones |
| `seaborn` | Gráficos estadísticos (distribuciones, correlaciones, mapas de calor) |
| `polars` | Tablas de datos grandes y rápidas en Python |
| `scikit-learn` | Aprendizaje automático: regresión, clasificación, agrupamiento |
| `statsmodels` | Regresiones, series de tiempo y pronósticos con sus incertidumbres |
| `networkx` | Grafos y redes: caminos más cortos, redes de cañerías o eléctricas |
| `scientific-writing` | Redactar y revisar informes técnicos con fuentes trazables |
| `literature-review` | Búsqueda bibliográfica ordenada y revisión de la literatura |
| `citation-management` | Buscar papers, verificar citas y armar la bibliografía (BibTeX) |
| `scientific-critical-thinking` | Evaluar si una afirmación o un ensayo está bien fundado |
| `scientific-brainstorming` | Generar y comparar ideas de investigación o de proyecto |
| `hypothesis-generation` | Pasar de una observación a hipótesis comprobables y cómo medirlas |
| `peer-review` | Revisar críticamente un trabajo ajeno (o el propio antes de entregar) |
| `latex-posters` | Pósters en LaTeX (beamerposter, tikzposter) |

No se copiaron `infographics`, `scientific-schematics` ni `scientific-slides` porque necesitan una clave paga de OpenRouter, ni las skills de biología y química, que no aplican a este kit.

## Qué necesitan

`pip install sympy matplotlib seaborn plotly pint uncertainties scipy statsmodels simpy pymoo cantera "markitdown[all]" polars scikit-learn networkx requests`, y GNU Octave para la skill `matlab` si no se tiene MATLAB. `latex-posters` necesita una distribución de LaTeX (MiKTeX o TeX Live). Cada `SKILL.md` detalla sus requisitos.

`literature-review`, `latex-posters` y `scientific-critical-thinking` ofrecen como opción generar esquemas con IA a través de OpenRouter (servicio pago, con clave `OPENROUTER_API_KEY`); sin esa clave funcionan igual, sin esos dibujos. `citation-management` y `literature-review` consultan bases públicas (OpenAlex, PubMed, arXiv, Crossref).

## Revisión

Revisé licencia, scripts, llamadas de red e instrucciones sospechosas, sin encontrar problemas. `markitdown` menciona servicios opcionales de Azure que solo se usan si se configuran a propósito. Los scripts no se ejecutaron durante la revisión.
