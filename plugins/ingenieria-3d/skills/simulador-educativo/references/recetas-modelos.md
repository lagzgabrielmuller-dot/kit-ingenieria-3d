# Recetas de modelos para simuladores de TP

Cada receta trae lo necesario para armar el objeto `SIM` de la plantilla: modelo, parámetros, escenarios, gráfico, animación, supuestos y límites, y un caso para validar con Python. Los valores numéricos de los casos son de ejemplo: en el trabajo se usan los de la consigna, el catálogo o la tabla de la cátedra, con su fuente. Si la cátedra usa otra nomenclatura u otra fórmula, manda la de la cátedra.

Para cálculos de instalaciones (iluminación, caída de tensión, aire comprimido, cintas, balances) las fórmulas están en la skill **calculos-ingenieria**.

## 1. Curva cupla-velocidad: variantes del ejemplo de la plantilla

Base (ya está en la plantilla): T = 2·T_máx / (s/s_k + s_k/s), con s_k = s_N·(λ + √(λ² − 1)) y T_máx = λ·T_n·(U/U_n)².

- **Carga de ventilador o bomba centrífuga**: T_L(n) = T_L0 + (T_LN − T_L0)·(n/n_N)², con T_L0 la cupla de arranque de la carga (rozamientos) y T_LN la cupla a velocidad nominal. No hay fórmula cerrada para el cruce: buscarlo con bisección entre n_k y n_s sobre f(n) = T_motor(n) − T_L(n) (en la rama estable hay un solo cruce si f(n_k) > 0). Graficar la carga como parábola.
- **Arranque estrella-triángulo**: en estrella cada bobina recibe U/√3, así que la cupla y la corriente de línea bajan a un tercio. Parámetro U en % (58 % en estrella) o una lista "estrella / triángulo".
- **Rotor bobinado con resistencias de arranque**: T_máx no cambia y s_k crece en proporción a la resistencia del rotor: s_k' = s_k·(R_2' + R_ad')/R_2'. Con s_k' = 1 la cupla máxima aparece en el arranque. Escenarios: sin resistencia, con la que da s_k' = 1 y con una mayor.
- **Variador de frecuencia con U/f constante**: n_s = 60·f/p; T_máx casi constante y s_k·f constante, así que la curva se corre en paralelo. Límite: por debajo de un 10 a 15 % de f_n pesa la resistencia del estator y el variador agrega tensión (refuerzo); el modelo simple deja de valer.
- **Validación**: el caso a mano de `scripts/validar_modelo_kloss.py` y, para la carga cuadrática, la bisección en Python contra la de la página.

## 2. Ensayo de doblado y plegado

**Doblado guiado** (ISO 7438 o la norma que indique la cátedra): probeta de espesor a y ancho b doblada con un mandril de diámetro D hasta un ángulo α, sobre dos apoyos separados l = D + 3·a (± a/2) (ISO 7438:2020, 6.2.2; fuentes en la skill **ensayos-materiales**). Se aprueba con el criterio de la norma de producto; si no fija ninguno, si la cara traccionada no muestra fisuras visibles sin aumento.
- Deformación de la fibra exterior, con el eje neutro en la mitad del espesor: ε = a / (D + a). Con D = 2·a, ε = 33,3 %; con D = 3·a, 25 %.
- Comparación orientativa con el material: el alargamiento a rotura A % del ensayo de tracción, o el radio mínimo de doblado de Kalpakjian, R_mín/a = 50/r − 1 (r: reducción de área en %).
- Fuerza en flexión de tres puntos (orientativa, material elastoplástico perfecto): zona elástica F = 48·E·I·δ/l³ con I = b·a³/12, hasta F_y = 2·σ_y·b·a²/(3·l); colapso plástico F_p = σ_y·b·a²/l = 1,5·F_y.

**Plegado de chapa** (Groover y Kalpakjian):
- Desarrollo de la zona doblada: A_b = 2π·(α/360)·(R + K_ba·t), con K_ba = 0,33 si R < 2·t y 0,5 si R ≥ 2·t (α en grados, R radio interior).
- Fuerza de plegado: F = K_bf·TS·w·t²/D, con K_bf = 1,33 en V y 0,33 en pestaña; TS resistencia a la tracción, w largo del pliegue, D abertura de la matriz.
- Recuperación elástica: R_i/R_f = 4·(R_i·Y/(E·t))³ − 3·(R_i·Y/(E·t)) + 1 y α_f = α_i·(R_i + t/2)/(R_f + t/2), con Y el límite de fluencia.

Armado:
- Parámetros: espesor, diámetro de mandril (o D/a), ángulo, material en lista (E, σ_y, TS y A % de la tabla de la cátedra o del certificado del material), ancho.
- Escenarios: el mandril de la consigna, uno más chico que el mínimo (debería fisurar), plegado a 90° en V, la chapa de otro material.
- Gráfico: ε exterior [%] en función de D/a con la recta del alargamiento del material; el cruce da el mandril mínimo y una marca señala el elegido. Para la fuerza, F [kN] en función de δ [mm].
- Animación: la probeta que envuelve el mandril hasta α (ángulo que avanza con el tiempo y cursor en el gráfico), con la cara traccionada coloreada según ε y una fisura dibujada si ε supera el límite.
- Laboratorio: fuerza contra desplazamiento del punzón si la máquina lo registra, o el ángulo final medido tras la recuperación.
- Supuestos: material homogéneo, eje neutro en el medio (vale para R/t grande; con radios chicos se corre hacia adentro, por eso K_ba = 0,33), sin rozamiento.
- Límites: el resultado real depende de los bordes, la dirección de laminación y los defectos (en soldaduras, del cordón); la fuerza de tres puntos es solo orientativa en grandes deformaciones.
- Validación: a = 10 mm, D = 20 mm → ε = 33,3 %. Tres puntos con b = 20 mm, σ_y = 250 MPa, l = 50 mm: F_y = 6.667 N y F_p = 10.000 N. R = 5 mm, t = 2 mm, α = 90° → A_b = 9,42 mm. Plegado en V con TS = 400 MPa, w = 100 mm, t = 2 mm y D = 16 mm → F = 13.300 N. Recuperación con Y = 250 MPa y E = 200.000 MPa → R_f = 5,047 mm y α_f = 89,3°.

## 3. Campo magnético giratorio

- Corrientes: i_1 = I_m·cos(ωt), i_2 = I_m·cos(ωt − 120°), i_3 = I_m·cos(ωt − 240°) (secuencia inversa: cambiar el signo de los desfasajes). Bobinas a 0°, 120° y 240° eléctricos: B = Σ B_k(t)·u_k, con B_k proporcional a i_k y u_k el versor de cada eje.
- Con corrientes equilibradas, |B| = 1,5·B_m constante y gira a la velocidad sincrónica n_s = 60·f/p.
- Falta de una fase (motor en estrella con un conductor cortado): i_3 = 0 e i_1 = −i_2 (la misma corriente recorre dos bobinas en serie). B = i_1·(u_1 − u_2) queda sobre un eje fijo y pulsa: es un campo alternativo y el motor parado no arranca.
- Parámetros: f, pares de polos, secuencia (lista), amplitud de la fase 3 en % (desequilibrio) y un escenario de falta de fase.
- Gráfico: las tres corrientes en un período (eje en ms o en grados de ωt) con el cursor del instante animado; |B| en por unidad como cuarta serie.
- Animación: tres ejes a 120° con flechas que pulsan, colores de fase de la AEA 90364 (marrón, negro y rojo) y el vector resultante con su rastro; en cámara lenta (50 Hz son 50 vueltas eléctricas por segundo).
- Supuestos: campo senoidal en el entrehierro, sin saturación ni armónicos, corrientes impuestas.
- Validación: en ωt = 0, B = (1,5·B_m; 0); en ωt = 90°, B = (0; 1,5·B_m). Con falta de fase, en ωt = 0, |B| = √3·B_m a −30°.

## 4. Secado de un producto

- Humedad en base húmeda w (kg de agua por kg de producto húmedo) y en base seca X = w/(1 − w).
- Agua a evaporar: m_agua = m_h·(w_i − w_f)/(1 − w_f).
- Cinética de capa delgada (modelo exponencial o de Lewis): MR = (X − X_e)/(X_0 − X_e) = e^(−k·t), con X_e la humedad de equilibrio (de la isoterma del producto, según la temperatura y la humedad relativa del aire) y k [1/h] empírica. Variante de Page: MR = e^(−k·tⁿ). k y X_e se sacan de bibliografía de ese producto o se ajustan con el modo laboratorio (mover k hasta que el error medio sea mínimo); nunca inventarlos.
- Tiempo para llegar a la humedad final: t = −ln(MR_f)/k, con MR_f = (X_f − X_e)/(X_0 − X_e); solo existe si X_f > X_e (avisar si no).
- Energía: Q = m_agua·h_fg + m_s·c_p·ΔT + pérdidas, con h_fg ≈ 2.358 kJ/kg a 60 °C (2.257 kJ/kg a 100 °C); combustible m = Q/(PCI·η).
- Parámetros: masa húmeda, w_i, w_f, humedad de equilibrio, k, temperatura del aire.
- Escenarios: el de la consigna, aire más caliente (k mayor), producto más húmedo, humedad final pedida menor que la de equilibrio (aviso).
- Gráfico: humedad [% b.h.] en función del tiempo [h] con la recta de la humedad final y la marca del tiempo de secado; cursor animado.
- Animación: bandeja o cinta con el producto que cambia de color, vapor proporcional a la velocidad de secado (dX/dt) y un reloj; acelerada (`escalaTiempo: 3600`).
- Supuestos: capa delgada, aire con temperatura y humedad constantes, k constante, sin período de velocidad constante.
- Límites: en lechos gruesos la humedad varía a lo alto del lecho (hace falta un modelo por capas); k cambia con la temperatura del aire.
- Validación: 1.000 kg de w_i = 70 % a w_f = 20 % → m_agua = 625 kg. Con X_e = 0,05 y k = 0,3 1/h → MR_f = 0,0876 y t = 8,12 h.

## 5. Rendimiento y regulación de un transformador

- Rendimiento: η = x·S_n·cosφ / (x·S_n·cosφ + P_0 + x²·P_cc), con x = S/S_n el índice de carga, P_0 las pérdidas de vacío (hierro) y P_cc las de cortocircuito a corriente nominal (cobre).
- Máximo en x_ópt = √(P_0/P_cc), cuando las pérdidas en el cobre igualan a las del hierro.
- Regulación aproximada (Kapp): ε = x·(ε_R·cosφ + ε_X·senφ) [%], con ε_R = 100·P_cc/S_n y ε_X = √(ε_cc² − ε_R²); senφ negativo para carga capacitiva (la tensión puede subir).
- Parámetros: S_n, P_0, P_cc y ε_cc (de los ensayos de vacío y cortocircuito o de la chapa), cosφ, tipo de carga e índice de carga del punto de trabajo.
- Gráfico: η [%] en función de x (0 a 1,25) para el cosφ elegido y para cosφ = 1, con marcas en el máximo y en el punto de trabajo.
- Animación: flujo de potencia con flechas cuyo ancho sigue a P_1, P_2, P_Fe (constante) y P_Cu (crece con x²).
- Laboratorio: rendimiento medido con carga (P_1 y P_2 con vatímetros) para cada x.
- Supuestos: P_0 constante (tensión nominal), P_Cu proporcional a x², circuito equivalente aproximado; Kapp vale para ε_cc chico.
- Validación: S_n = 100 kVA, P_0 = 400 W, P_cc = 1.600 W, cosφ = 0,8 → η(1) = 97,56 %, x_ópt = 0,5, η(0,5) = 98,04 %. Con ε_cc = 4 %: ε_R = 1,6 %, ε_X = 3,67 % y regulación a plena carga de 3,48 % (inductiva) y −0,92 % (capacitiva).

## 6. Ensayo de tracción

- Valores convencionales: σ = F/S_0 y ε = ΔL/L_0. Verdaderos: ε_v = ln(1 + ε) y σ_v = σ·(1 + ε).
- Zona elástica: σ = E·ε hasta σ_y. Zona plástica (Hollomon en valores verdaderos, con meseta de fluencia): σ_v = máx(σ_y; K·ε_vⁿ). K y n salen de la tabla de la cátedra (el Groover trae una) o del ajuste de las mediciones.
- Comienzo de la estricción (Considère): ε_v = n, y resistencia a la tracción σ_u = K·nⁿ·e^(−n) con ε_u = e^n − 1, si K·nⁿ > σ_y. Después de ese punto el modelo no vale: dibujar la caída con guiones y decirlo.
- Parámetros: material en lista (E, σ_y, K, n), diámetro o sección, longitud calibrada L_0.
- Gráfico: σ [MPa] en función de ε [%] con marcas en σ_y y σ_u; si la máquina registra fuerza y alargamiento, graficar F [kN] en función de ΔL [mm] para comparar directo en el modo laboratorio.
- Animación: la probeta que se estira (deformación exagerada en escala) y se estrecha al llegar a σ_u; cursor en ε.
- Supuestos: deformación uniforme hasta la estricción, volumen constante, velocidad de ensayo sin efecto.
- Validación: K = 500 MPa, n = 0,25 y σ_y = 250 MPa → meseta hasta ε_v = (σ_y/K)^(1/n) = 0,0625; σ_u = 275,3 MPa con ε_u = 28,4 % (el máximo numérico de la curva convencional da lo mismo).

## 7. Calentamiento y enfriamiento de un motor

- Calentamiento desde frío: θ(t) = θ_a + Δθ_f·(1 − e^(−t/τ)); enfriamiento: θ(t) = θ_a + (θ_0 − θ_a)·e^(−t/τ_e). Motor autoventilado detenido: τ_e mayor que τ.
- Calentamiento final según la carga: Δθ_f = Δθ_n·(a + x²)/(a + 1), con x = P/P_n y a = pérdidas fijas / pérdidas variables a plena carga.
- Servicio intermitente (S3): alternar calentamiento y enfriamiento con el ciclo de la consigna; el gráfico muestra el diente de sierra que se estabiliza.
- Clases térmicas (IEC 60085): B 130 °C, F 155 °C, H 180 °C. Son límites del punto más caliente; la elevación admisible del catálogo es menor.
- Parámetros: τ, Δθ_n, carga x, temperatura ambiente, a, ciclo de servicio.
- Gráfico: θ [°C] en función de t [min] con la recta de la clase de aislación; cursor animado.
- Animación: motor coloreado según la temperatura y un termómetro (es el ejemplo mínimo del SKILL.md).
- Supuestos: cuerpo homogéneo con una sola constante de tiempo, pérdidas y ambiente constantes.
- Límites: el bobinado se calienta más rápido que la carcasa (hay varias constantes de tiempo); con arranques frecuentes manda la corriente de arranque.
- Validación: en t = τ llega al 63,2 % de Δθ_f; en 3τ, al 95,0 %; en 5τ, al 99,3 %. Con a = 0,5 y x = 1,2, Δθ_f = 1,293·Δθ_n.
