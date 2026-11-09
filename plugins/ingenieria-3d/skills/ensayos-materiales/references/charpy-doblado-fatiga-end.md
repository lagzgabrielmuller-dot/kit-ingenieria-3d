# Charpy, doblado y plegado, fatiga y ensayos no destructivos: detalle

Leer cuando el TP pide el procedimiento completo de un Charpy o de un doblado, la curva de transición, un cálculo de fatiga con tensión media, o elegir y describir un ensayo no destructivo.

## 1. Impacto Charpy (ISO 148-1:2016)

**Probeta**: 55 mm de largo, sección cuadrada de 10 mm. Entalla en V de 45°, 2 mm de profundidad y radio de fondo 0,25 mm; o en U de 5 mm de profundidad y radio 1 mm. La entalla se mecaniza (no se lima a mano) y su fondo define el resultado: una entalla mal hecha invalida el ensayo. Si el espesor del material no alcanza se usan probetas de ancho reducido, cuyos resultados no se comparan directamente con los de 10 mm.

**Procedimiento**:
1. Medir la probeta y revisar la entalla.
2. Acondicionar a la temperatura de ensayo con ±2 °C (baño o cámara) y no tardar más de 5 s entre sacarla y el golpe.
3. Apoyarla con la entalla del lado contrario al percutor y centrada entre los apoyos (dentro de 0,5 mm).
4. Soltar el péndulo y leer la energía absorbida K (o los ángulos).
5. Guardar los trozos: aspecto de la fractura y expansión lateral.

**Cálculo con ángulos**: K = W·L·(cos β − cos α); energía inicial E0 = W·L·(1 − cos α). El rozamiento y el aire se estiman con un vuelo libre sin probeta (ángulo β0): K ≈ W·L·(cos β − cos β0).
Ejemplo: péndulo de 300 J con α = 150° (W·L = 160,77 J); β = 100° → K = 111,3 J; si en vuelo libre sube a β0 = 148°, K corregida ≈ 108,4 J (`python scripts/ensayos.py charpy --E0 300 --alfa 150 --beta 100 --beta0 148`).

**Resultados que se informan**: KV2 (o KV8, KU2, KU8) en J con la temperatura; porcentaje de fractura dúctil (zona fibrosa y opaca frente a la frágil, brillante); expansión lateral en mm (cuánto se ensancha la cara comprimida, medida de la capacidad de deformarse con tensiones triaxiales).

**Curva de transición**: se ensayan varias probetas (por ejemplo, tres por temperatura) en un rango de temperaturas y se grafica K en función de T. En aceros ferríticos hay una meseta alta (dúctil), una caída y una meseta baja (frágil). La temperatura de transición Tt marca la posición de la caída y se define por un criterio: una energía dada, un porcentaje de fractura dúctil o una expansión lateral. Metales de estructura cúbica centrada en las caras (aceros austeníticos, cobre, aluminio) no muestran la caída.

**Cuidado**: KV2 y KV8 no se comparan entre sí; el Charpy compara materiales y controla calidad, no da un valor de diseño. Si K supera el 80 % de E0, el resultado es aproximado.

## 2. Doblado y plegado (ISO 7438)

ISO 7438:2020 (cuarta edición, reemplaza a la de 2016) define el método; el diámetro del mandril, el ángulo y el criterio de aceptación los fija la **norma de producto**.

**Probeta** (valores de la edición 2016):
- Ancho: el del producto si es de 20 mm o menos; si es mayor, (20 ± 5) mm para espesores menores de 3 mm y de 20 a 50 mm para espesores de 3 mm o más.
- Espesor: el del producto; si supera 25 mm se puede reducir mecanizando una cara, hasta no menos de 25 mm.
- Aristas redondeadas con radio de hasta 1 mm (espesor menor de 10 mm), 1,5 mm (10 a 50 mm) o 3 mm (50 mm o más).
- Barras y alambres: la sección entera.

**Ensayo**:
- Dos rodillos de apoyo y un mandril de diámetro D en el centro; distancia entre apoyos l = (D + 3a) ± a/2, con a = espesor o diámetro, fija durante el ensayo, salvo que la norma de producto fije otra. Es la fórmula (1) de ISO 7438:2020, cláusula 6.2.2 (4.2.2 en las ediciones 2005 y 2016), leída en las vistas previas de iTeh de la [edición 2020](https://iteh.es/catalog/standards/iso/b3f3b8b3-b9e1-4c92-ae7c-c3ed77b61527/iso-7438-2020) y de la [edición 2005](https://cdn.standards.iteh.ai/samples/35928/e42a5bb60352419b809333d0ffbc6508/ISO-7438-2005.pdf). La edición 2020 (cuarta) reemplaza a la 2016 y agrega el anexo B, doblado en deformación plana.
- Temperatura entre 10 y 35 °C (o (23 ± 5) °C si se pide temperatura controlada): cláusula 6.1 de las ediciones 2005 y 2016, en las mismas vistas previas.
- Se dobla en forma continua y lenta hasta el ángulo α pedido. Otras variantes que piden algunas normas de producto: llevar las ramas a paralelas a una distancia dada, o hasta que se toquen (plegado a fondo, sin mandril).
- Inspección: la cara traccionada (exterior). Si la norma de producto no fija otra cosa, se acepta si no hay fisuras visibles sin aumento. Ese criterio va en la cláusula 9, «Interpretación de los resultados», de la edición 2020 (7 en la 2016), que no aparece en las vistas previas (verificar en la edición vigente).

**Deformación de la fibra exterior**: ε ≈ a/(D + a) (eje neutro en la mitad del espesor). Ejemplos: mandril 3,5·d → 22,2 %; 5·d → 16,7 %; 7·d → 12,5 %; chapa de 3 mm sobre mandril de 6 mm → 33,3 %, con l = 6 + 9 ± 1,5 = (15 ± 1,5) mm.

**Barras para hormigón** (Argentina):
- ADN 420 (IRAM-IAS U 500-528) y ADN 420 S soldable (IRAM-IAS U 500-207): doblado a 180° sobre mandril de 3,5·d (d ≤ 25 mm), 5·d (32 mm) y 7·d (40 mm), según hojas técnicas de fabricantes (verificar en la edición vigente; un manual de fabricante da 200 mm para la barra de 40 mm). Ejemplos: d = 12 mm → mandril 42 mm; d = 25 mm → 87,5 mm.
- Aceptación: sin fisuras ni grietas transversales en la zona traccionada.
- Las normas de barras también tienen un ensayo de doblado y desdoblado (para ver el envejecimiento); sus ángulos y condiciones se toman de la norma de producto.
- No confundir con el diámetro mínimo de doblado en obra que publican los fabricantes, que es mayor.

**Soldaduras**: el doblado de cara, de raíz o lateral se usa para calificar procedimientos y soldadores, con su propia norma y criterio.

## 3. Fatiga

**Definiciones**: σa = (σmax − σmin)/2 (amplitud); σm = (σmax + σmin)/2 (media); R = σmin/σmax (R = −1: alternante pura, como en flexión rotativa). Ejemplo: σmax = 270 MPa y σmin = 30 MPa → σa = 120 MPa, σm = 150 MPa, R = 0,111.

**Ensayos**: flexión rotativa (ISO 1143: la probeta gira cargada y cada fibra pasa de tracción a compresión en cada vuelta) y axial con fuerza controlada (ISO 1099). Varias probetas a distintos niveles de σa; para cada una se registran los ciclos hasta la rotura. Las que no rompen hasta el límite de ciclos fijado se marcan como "sin rotura" (flecha en el gráfico).

**Curva S-N (Wöhler)**: σa en función de log N. Aceros: se vuelve horizontal desde alrededor de 10⁶ ciclos (límite de fatiga). No ferrosos: sin límite; se informa la resistencia a fatiga a un N dado (aleaciones de aluminio y de magnesio: 30 a 40 % de Rm a 10⁸ ciclos).

**Estimaciones para aceros** (apuntes de diseño de máquinas basados en Shigley): Se' ≈ 0,5·Rm si Rm ≤ 1400 MPa, y 700 MPa si Rm es mayor (probeta pulida en flexión rotativa). Vida finita entre 10³ y 10⁶ ciclos, recta en log-log: Sf = a·N^b, con a = (0,8·Rm)²/Se' y b = −(1/3)·log10(0,8·Rm/Se') (el factor 0,8 varía según el texto).
Ejemplo: Rm = 600 MPa → Se' = 300 MPa; a = 768 MPa; b = −0,0680; a 10⁵ ciclos Sf = 351 MPa.

**Tensión media**: Goodman modificado, 1/n = σa/Se + σm/Rm. Con σa = 120 MPa, σm = 150 MPa, Se = 300 MPa y Rm = 600 MPa → n = 1,54. Otros criterios: Soderberg (con Re en lugar de Rm, más conservador) y Gerber (parábola).

**Pieza real**: el límite de la probeta se reduce por terminación superficial, tamaño, tipo de carga, temperatura, confiabilidad y concentradores de tensiones (factores de Marin y Kf de la bibliografía de diseño). Nunca usar Se' directo para un eje con chavetero.

**Rotura por fatiga**: zona de inicio (en un concentrador), zona de propagación lisa con marcas de playa, y zona de rotura final rugosa; cuanto más chica la zona final, menor era la tensión.

## 4. Ensayos no destructivos

**Tintas penetrantes (PT, ISO 3452-1)**:
1. Limpieza previa y secado (sin grasa, pintura ni óxido en la zona).
2. Aplicar el penetrante (coloreado o fluorescente) y esperar el tiempo de penetración que indican el fabricante y el procedimiento.
3. Remover el exceso sin lavar las discontinuidades.
4. Aplicar el revelador en capa fina y esperar.
5. Inspeccionar con buena luz blanca, o con luz UV si es fluorescente; registrar las indicaciones (foto, croquis).
6. Limpieza final.
Detecta solo lo abierto a la superficie; no sirve en materiales porosos.

**Partículas magnéticas (MT, ISO 9934-1)**:
- Magnetizar (yugo, puntas, bobina o paso de corriente) y aplicar las partículas (secas o en suspensión, coloreadas o fluorescentes) mientras dura la magnetización.
- Un defecto se ve cuando corta las líneas del campo: inspeccionar en dos direcciones a 90°.
- Detecta defectos superficiales y algo por debajo de la superficie, solo en materiales ferromagnéticos (no en inoxidables austeníticos, aluminio ni cobre). Desmagnetizar al final si la pieza lo requiere.

**Ultrasonido (UT, ISO 16810)**:
- Un palpador emite pulsos de alta frecuencia; los ecos en discontinuidades o en la cara opuesta se ven en pantalla (A-scan). Se calibra con bloques patrón y necesita acoplante (gel, aceite, agua).
- Palpador normal para espesores, laminaciones e inclusiones; angular para soldaduras.
- Encuentra defectos internos planos (fisuras, falta de fusión) mejor que la radiografía; limitado por geometrías complicadas, granos gruesos y superficies rugosas; el operador tiene que estar calificado.

**Radiografía (RT, ISO 17636-1 y -2 para soldaduras)**:
- Rayos X o gamma atraviesan la pieza y se registran en película o detector digital; un indicador de calidad de imagen verifica la sensibilidad.
- Ve bien defectos volumétricos (poros, inclusiones de escoria, rechupes); las fisuras planas solo si están alineadas con el haz.
- Requiere radioprotección, zona controlada y operadores habilitados.

**Corrientes inducidas (ET, ISO 15549)**:
- Una bobina con corriente alterna induce corrientes en la pieza; una fisura o un cambio de material modifica la impedancia de la bobina.
- Detecta fisuras superficiales y cercanas, mide espesores de recubrimientos no conductores y clasifica materiales por conductividad. Solo conductores; poca penetración; necesita patrones.

**Visual (VT, ISO 17637 para soldaduras)**: siempre el primero; con buena luz, lupa, galgas y espejos.

**Cómo elegir**:

| Se busca | Material | Método |
|---|---|---|
| Fisuras superficiales | Cualquiera no poroso | PT |
| Fisuras superficiales o justo debajo | Acero al carbono (ferromagnético) | MT |
| Fisuras o faltas de fusión internas, espesores | Metales | UT |
| Poros e inclusiones internos, registro permanente | Cualquiera | RT |
| Fisuras superficiales en serie, recubrimientos | Conductores | ET |

En soldaduras, los niveles de aceptación salen de normas aparte (por ejemplo ISO 5817 para la inspección visual e ISO 10675-1 y -2 para radiografía). La calificación del personal de END es por ISO 9712.
