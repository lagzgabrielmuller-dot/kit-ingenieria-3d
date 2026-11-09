# Ensayo de tracción: detalle

Leer cuando hay que interpretar o graficar la curva, sacar Rp0,2 a mano o en una planilla, pasar a tensión y deformación verdaderas, trabajar sin extensómetro o describir la rotura. Definiciones según ISO 6892-1:2019.

## 1. La curva y sus zonas

1. **Elástica**: recta (ley de Hooke, σ = E·ε); si se descarga, la probeta vuelve a su largo.
2. **Fluencia**: en aceros de bajo carbono aparece una meseta con un máximo previo (ReH) y oscilaciones (ReL); la deformación avanza en bandas (bandas de Lüders). En otros materiales la transición es gradual y se usa Rp0,2.
3. **Endurecimiento por deformación**: la fuerza sigue subiendo hasta Fmax; la deformación es uniforme en toda la longitud. La deformación plástica a fuerza máxima es Ag; la total, Agt.
4. **Estricción**: desde Fmax la deformación se concentra en una zona, la sección baja rápido y la fuerza cae hasta la rotura.

Definiciones de la norma (resumidas): ReH, tensión máxima antes de la primera caída de fuerza; ReL, la menor tensión durante la fluencia plástica sin contar el efecto transitorio inicial; Rp, tensión a la que la extensión plástica llega a un porcentaje dado de la longitud del extensómetro; Rm, tensión a la fuerza máxima; A, alargamiento permanente después de la rotura (Lu − L0) en % de L0; Z, máxima reducción de la sección (S0 − Su) en % de S0.

## 2. Probetas

- Proporcionales: L0 = k·√S0 con k = 5,65 (preferida) y L0 de al menos 15 mm; si no alcanza, k = 11,3 o probeta no proporcional. Redondas: L0 = 5·d0 (corta) o 10·d0 (larga).
- Medir d0 (o a0 y b0) en al menos tres lugares de la parte calibrada y usar el promedio (algunas normas de producto piden la sección mínima).
- Marcar L0 con marcas finas o tinta, sin entallar la probeta.

## 3. Cálculos paso a paso

1. S0 = π·d0²/4 (redonda) o a0·b0 (plana).
2. σ = F/S0 y ε = ΔL/L0 para cada punto (MPa = N/mm²).
3. **E**: pendiente del tramo recto. Con regresión lineal entre dos niveles de tensión (el script usa 10 % a 40 % de Rm por defecto) o con dos puntos: E = (σ2 − σ1)/(ε2 − ε1). Informar también el R² de la recta.
4. **Rp0,2**: recta σ = E·(ε − ε0 − 0,002), donde ε0 es donde la recta elástica corta el eje (corrige el pie de la curva por asentamiento de mordazas). Rp0,2 es la tensión en el cruce con la curva.
   - En una planilla: columna σ, columna ε, columna "recta" = E·(ε − ε0 − 0,002), columna diferencia σ − recta; el cruce es donde la diferencia cambia de signo; interpolar entre esas dos filas.
5. **Rm** = Fmax/S0.
6. **Agt** = deformación total en Fmax (×100); **Ag** = Agt − Rm/E·100.
7. **A** = (Lu − L0)/L0·100 con Lu medido sobre los trozos unidos. Desde la curva se puede estimar como la deformación a la rotura menos la parte elástica que se recupera (σ de rotura/E), pero el valor que se informa es el medido.
8. **Z** = (S0 − Su)/S0·100, con Su de dos diámetros perpendiculares medidos en la sección mínima.

Si la rotura queda cerca de una marca (a menos de L0/3), el alargamiento medido puede no ser representativo: la norma da el criterio de validez y un método de corrección (verificar en la edición vigente).

## 4. Tensión y deformación verdaderas

Hasta Fmax (deformación uniforme, volumen constante): σv = σ·(1 + ε) y εv = ln(1 + ε). Ejemplo del demo en Fmax (ε = 0,1734): σv = 500·1,1734 = 586,7 MPa; εv = 0,1599. Después de Fmax hace falta medir la sección real de la estricción.

## 5. Energías por unidad de volumen

- Resiliencia (energía elástica hasta la fluencia): Ur = Rp²/(2·E) → 350²/(2·205000) = 0,299 MJ/m³.
- Tenacidad (área bajo toda la curva), estimación: UT ≈ (Rp + Rm)/2·A → (350 + 500)/2·0,25 = 106 MJ/m³. Para el valor real se integra la curva (regla del trapecio en la planilla o en Python).

## 6. Sin extensómetro

- El desplazamiento del travesaño incluye la deformación de la máquina, las mordazas, las cabezas de la probeta y el deslizamiento: el tramo elástico sale con una pendiente mucho menor que E. Ese E **no se informa**; se escribe que E no se determinó por falta de extensómetro, o se da el de bibliografía con su fuente.
- La recta del 0,2 % trazada paralela a la pendiente medida separa bien la parte elástica de la máquina (que es lineal), pero el travesaño también mide la deformación plástica de toda la parte calibrada, que es más larga que L0. Por eso Rp0,2, Ag y Agt quedan como estimaciones y se dice así en el informe.
- `--E-ref` (por ejemplo 205000 MPa para acero) corrige la deformación elástica para que el gráfico tenga la pendiente real: ε corregida = ε − σ/E medido + σ/E de referencia.

## 7. Tipo de rotura

- **Dúctil**: estricción marcada, superficie de copa y cono, fibrosa y opaca. Aceros de bajo carbono, aluminio y cobre recocidos.
- **Frágil**: sin estricción, superficie plana, brillante o cristalina, perpendicular a la carga. Fundición gris, aceros templados sin revenir.
- Fotografiar los dos trozos y la superficie de rotura, con una escala.

## 8. Velocidad y condiciones

- La norma fija la velocidad del ensayo: método A (por velocidad de deformación, el que recomienda) o método B (por velocidad de tensión en el tramo elástico). Anotar la velocidad usada y la temperatura del laboratorio (el rango admitido para "temperatura ambiente" está en la norma).
- Si la máquina indica la fuerza en kgf (máquinas viejas), convertir: 1 kgf = 9,80665 N (`--unidad-fuerza kgf` en el script).

## 9. Gráfico para el informe

- σ [MPa] en el eje vertical y ε [%] en el horizontal, con la recta del 0,2 % punteada y los puntos Rp0,2, Rm y rotura marcados.
- Si hay Python con matplotlib: leer el CSV, calcular σ y ε y graficar; con Excel o LibreOffice, gráfico de dispersión con líneas suaves desactivadas.
- Epígrafe: "Figura N – Curva tensión-deformación ingenieril, probeta X (material, d0, L0)".

## 10. Barras para hormigón

Las barras ADN 420 (IRAM-IAS U 500-528) y ADN 420 S (IRAM-IAS U 500-207) se aceptan por valores característicos mínimos; según hojas técnicas de los fabricantes: fluencia 420 MPa, resistencia 500 MPa, alargamiento de rotura 12 % y relación Rm/Re de 1,10. La sección de cálculo es la nominal de la barra (los resaltes no cuentan); verificar el criterio y los valores en la edición vigente de la norma. Ejemplo: barra de 12 mm → S = 113,1 mm²; la fuerza de fluencia mínima es 420·113,1 = 47,5 kN y la máxima mínima 500·113,1 = 56,5 kN.
