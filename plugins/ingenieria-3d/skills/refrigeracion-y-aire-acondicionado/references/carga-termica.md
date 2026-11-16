# Carga térmica de un ambiente: método simplificado

Leer para armar o revisar a mano un cálculo de carga de refrigeración (verano) o para entender qué hace `scripts/refrigeracion.py carga`. Es un método de régimen permanente: no tiene en cuenta la inercia térmica de muros y losas ni la hora del pico. Sirve para elegir un equipo de confort y para trabajos prácticos; para un proyecto se usa el método del fabricante o el de ASHRAE Handbook Fundamentals, cap. 18. Lo que no se pudo confirmar con una fuente va marcado "(verificar)".

## 1. Datos de diseño

- **Exterior:** temperatura y humedad de diseño de verano de la localidad, de la consigna o de tablas climáticas (en la Argentina, la serie IRAM 11603 trae datos climáticos por localidad; verificar la edición y el dato).
- **Interior:** el ejemplo usa 24 °C y 50 % (valores supuestos; la consigna o la reglamentación pueden fijar otros).
- ΔT = te − ti, en K.

## 2. Transmisión por paredes, techo y piso

Q = U·A·ΔT, con U en W/(m²·K) de cada cerramiento (cálculo de U por capas en **transferencia-de-calor**). Si el cerramiento da a un local no acondicionado, se usa la temperatura de ese local en lugar de te.

**Superficies al sol:** se suma ΔTsol, que sale de la temperatura sol-aire de ASHRAE (Fundamentals, cap. 18): t_sa = te + α·I/ho − ε·ΔR/ho, con α/ho ≈ 0,026 m²·K/W para superficie clara y 0,052 m²·K/W para oscura, y ε·ΔR/ho ≈ 3,9 K en superficies horizontales y 0 en verticales (verificar en la edición consultada). Entonces ΔTsol = t_sa − te. Con I = 900 W/m² sobre un techo (valor supuesto):

| Techo | Cuenta | ΔTsol |
|---|---|---|
| Claro | 0,026·900 − 3,9 | 19,5 K (el ejemplo usa 20 K) |
| Oscuro | 0,052·900 − 3,9 | 42,9 K |

El color del techo pesa mucho: pintarlo de blanco baja la carga. En régimen permanente, una losa pesada da menos de lo calculado porque su masa demora y amortigua el pico.

## 3. Vidrios

Q = U·A·ΔT + A·FS·I. FS es el factor solar (en inglés, SHGC): la fracción de la radiación que entra, con la protección incluida (cortina, persiana, alero); sale del catálogo del vidrio o de tablas (verificar). I es la irradiancia sobre el plano del vidrio, que depende de la orientación, la latitud, el mes y la hora; se toma de las tablas de la bibliografía (ASHRAE, Carrier) o de una medición. En el hemisferio sur, el sol de la tarde castiga las ventanas al oeste y el del mediodía las del norte. Ejemplo: 6 m² con FS = 0,6 e I = 350 W/m² (supuestos) → 1260 W, más que todo el techo.

## 4. Aire exterior: infiltración y ventilación

- Caudal: V = n·Vol/3600 + Vvent, en m³/s, con n las renovaciones por hora por rendijas y puertas (el ejemplo supone 1 por hora) y Vvent el aire de ventilación que fija la consigna o la reglamentación (en ambientes de trabajo, el Dec. 351/79: verificar el artículo y el caudal, y ver **higiene-y-seguridad**).
- De la entalpía del aire húmedo h = 1,006·t + W·(2501 + 1,86·t) (ASHRAE, en **secado-y-psicrometria**) sale la separación exacta en sensible y latente:
  - Qs = ρ·V·(1006 + 1860·We)·(te − ti), en W;
  - Ql = ρ·V·(2 501 000 + 1860·ti)·(We − Wi), en W;
  - con ρ = 1,2 kg/m³ (aire estándar) y W = 0,621945·pw/(p − pw), pw = φ·pws(t).
- Para cuentas rápidas: Qs ≈ 0,34·V·ΔT y Ql ≈ 0,85·V·ΔW, con V en m³/h y ΔW en g/kg.
- Ejemplo: 444 m³/h con We = 14,13 g/kg (35 °C y 40 %) y Wi = 9,30 g/kg (24 °C y 50 %) → 1681 W sensibles y 1821 W latentes.

## 5. Personas

Calor por persona según la actividad (ASHRAE Handbook Fundamentals 2017, cap. 18, tabla 1, valores ajustados para un grupo mixto; verificar en la edición consultada):

| `--actividad` | Ejemplo de local | Sensible [W] | Latente [W] |
|---|---|---:|---:|
| reposo | teatro, cine | 65 | 30 |
| oficina | oficina, aula | 70 | 45 |
| comercio | comercio, caminando despacio | 75 | 55 |
| banco | trabajo liviano en banco de taller | 80 | 140 |
| pesado | trabajo pesado en taller | 170 | 255 |

## 6. Iluminación y equipos

Toda la potencia eléctrica que se consume adentro termina en calor sensible del local: iluminación instalada (en LED, con el driver) y equipos en uso (placa o medición; si no andan todos a la vez, el factor de uso).

## 7. Resultado y elección del equipo

- Q = Qs + Ql. Factor de calor sensible FCS = Qs/Q: con mucho latente (mucha gente, mucho aire exterior), revisar en el catálogo la capacidad sensible además de la total.
- Conversiones (NIST SP 811): 1 frig/h = 1 kcal/h = 1,163 W; 1 BTU/h = 0,2931 W; 1 TR = 12 000 BTU/h = 3,517 kW. "Equipo de 3000 frigorías" = 3000 frig/h = 3489 W = 11 905 BTU/h.
- Se elige con la capacidad del catálogo en las condiciones de diseño. La nominal se mide en condiciones de ensayo normalizadas (ISO 5151; verificar la edición) y suele ser mayor que la que entrega un día de calor extremo.
- Margen de seguridad solo si lo pide la consigna (`--margen`), dicho en el informe.

## 8. Ejemplo completo (es el `demo`)

Aula de 8 m × 6 m × 3 m (48 m², 144 m³), 30 personas sentadas, exterior 35 °C y 40 %, interior 24 °C y 50 %. Todos los datos son supuestos para el ejemplo.

| Rubro | Cálculo | Sensible [W] | Latente [W] |
|---|---|---:|---:|
| Techo de chapa aislado al sol | 0,6·48·(11 + 20) | 893 | - |
| Paredes exteriores | 1,8·36·11 | 713 | - |
| Vidrio, transmisión | 5,8·6·11 | 383 | - |
| Vidrio, radiación | 6·0,6·350 | 1260 | - |
| Aire exterior, 144 + 300 m³/h | fórmulas del punto 4 | 1681 | 1821 |
| Personas | 30·(70 + 45) | 2100 | 1350 |
| Iluminación | 400 W instalados | 400 | - |
| Equipos | 300 W en uso | 300 | - |
| **Total** | | **7729** | **3171** |

Total 10 900 W = 9372 frig/h = 37 192 BTU/h = 3,10 TR; FCS = 0,71; 227 W/m². El demo comprueba que el script da lo mismo que esta cuenta a mano.

## 9. Errores frecuentes

- Calcular el techo al sol con el ΔT de la sombra, u olvidar la radiación por los vidrios.
- Olvidar el calor latente de las personas y del aire exterior.
- Contar dos veces el aire exterior (como infiltración y como ventilación del mismo caudal).
- Confundir frigorías con frigorías/h, o elegir por la capacidad nominal.
- Usar U de catálogo sin las resistencias superficiales, o mezclar W con kcal/h.
