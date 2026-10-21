# Créditos: ciencia y cálculo (comunidad)

12 skills de [K-Dense-AI/claude-scientific-skills](https://github.com/K-Dense-AI/claude-scientific-skills) (K-Dense Inc.), licencia MIT (texto completo en `licencias/claude-scientific-skills-MIT.txt`), copiadas **sin modificaciones** del commit `593377bb048752abb0152deab9fbb1083a6087df`.

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

No se copiaron `infographics`, `scientific-schematics` ni `scientific-slides` porque necesitan una clave paga de OpenRouter, ni las skills de biología y química, que no aplican a este kit.

## Qué necesitan

`pip install sympy matplotlib seaborn plotly pint uncertainties scipy statsmodels simpy pymoo cantera "markitdown[all]"`, y GNU Octave para la skill `matlab` si no se tiene MATLAB. Cada `SKILL.md` detalla sus requisitos.

## Revisión

Revisé licencia, scripts, llamadas de red e instrucciones sospechosas, sin encontrar problemas. `markitdown` menciona servicios opcionales de Azure que solo se usan si se configuran a propósito. Los scripts no se ejecutaron durante la revisión.
