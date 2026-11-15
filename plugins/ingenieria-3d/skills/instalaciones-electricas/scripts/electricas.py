#!/usr/bin/env python3
"""electricas.py - calculos de instalaciones electricas de baja tension (solo biblioteca estandar).

Cada comando imprime formula, reemplazo y resultado (coma decimal), listo para una memoria de calculo.
  corriente --P kW --U V [--fases 3] [--cos 0.85] [--rend 1]          corriente de proyecto
  caida --I A --L m (--S mm2 | --limite %) [--U 380] [--fases 3] [--cos 0.85] [--material cu|al] [--temp 70] [--x ohm/km]
        caida de tension; con --limite y sin --S, la seccion minima y la normalizada siguiente
  capacitor --P kW --cos1 0.75 --cos2 0.95 [--U 380] [--f 50]          correccion del factor de potencia (kvar y uF)
  cortocircuito --S kVA --uk % [--U 400] [--L m --seccion mm2 --material cu] [--t s --k 115]
        corriente de cortocircuito trifasico en bornes del transformador (y al final de un cable), y seccion minima termica
  jabalina --rho ohm.m --L m --d mm [--max 40]                          resistencia de una jabalina (Dwight)
  lumenes --a m --b m --h m --E lx --flujo lm --cu --fm                 metodo de los lumenes
  demo                                                                  verifica todos los comandos con cuentas a mano
Los limites (caida de tension, puesta a tierra, iluminacion) se toman de la reglamentacion vigente o de la consigna.
"""
import argparse
import math
import sys

RHO20 = {'cu': 0.017241, 'al': 0.028264}   # ohm.mm2/m a 20 C (cobre recocido IEC 60028; aluminio IEC 60889)
ALFA20 = {'cu': 0.00393, 'al': 0.00403}     # 1/C
SECCIONES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400]   # mm2, serie IEC 60228


def n(x, d=2):
    return ('%.*f' % (d, x)).replace('.', ',')


def miles(x, d=0):
    s = ('%.*f' % (d, x))
    ent, _, dec = s.partition('.')
    signo = '-' if ent.startswith('-') else ''
    ent = ent.lstrip('-')
    grupos = []
    while len(ent) > 3:
        grupos.insert(0, ent[-3:])
        ent = ent[:-3]
    grupos.insert(0, ent)
    return signo + ' '.join(grupos) + (',' + dec if dec else '')


def raiz(fases):
    if fases not in (1, 3):
        raise ValueError('fases: 1 o 3')
    return math.sqrt(3) if fases == 3 else 1.0


# ------------------------------------------------------------------------------------------ comandos
def corriente(P, U, fases=3, cos=0.85, rend=1.0):
    I = P * 1000 / (raiz(fases) * U * cos * rend)
    f = 'I = P/(√3·U·cosφ·η)' if fases == 3 else 'I = P/(U·cosφ·η)'
    return {'I': I}, ['%s = %s W/(%s%s V·%s·%s) = %s A' % (f, miles(P * 1000), '√3·' if fases == 3 else '', n(U, 0), n(cos, 2), n(rend, 2), n(I, 2))]


def resistividad(material, temp):
    if material not in RHO20:
        raise ValueError('material: cu o al')
    return RHO20[material] * (1 + ALFA20[material] * (temp - 20))


def caida(I, L, S=None, U=380, fases=3, cos=0.85, material='cu', temp=70, x=0.0, limite=None):
    rho = resistividad(material, temp)
    k = math.sqrt(3) if fases == 3 else 2.0
    sen = math.sqrt(max(0.0, 1 - cos ** 2))
    L_ = ['Resistividad a %s °C: ρ = ρ20·(1 + α·(t − 20)) = %s·(1 + %s·%s) = %s Ω·mm²/m'
          % (n(temp, 0), n(RHO20[material], 6), n(ALFA20[material], 5), n(temp - 20, 0), n(rho, 5))]
    r = {'rho': rho}
    if S is None:
        if not limite:
            raise ValueError('indicá --S (sección) o --limite (caída máxima en %) para calcular la sección')
        du_max = limite / 100 * U
        resto = du_max - k * I * L * x / 1000 * sen
        if resto <= 0:
            raise ValueError('con esa reactancia no se llega al límite con ninguna sección')
        Smin = k * I * L * rho * cos / resto
        S = next((s for s in SECCIONES if s >= Smin), None)
        if S is None:
            raise ValueError('hace falta más de 400 mm²: dividir en conductores en paralelo')
        L_.append('Sección mínima por caída de tensión (%s %% de %s V = %s V): S = %s·I·L·ρ·cosφ/ΔU = %s mm² → se adopta %s mm²'
                  % (n(limite, 1), n(U, 0), n(du_max, 2), '√3' if fases == 3 else '2', n(Smin, 2), n(S, 1)))
        r['Smin'] = Smin
    Rp = rho / S                    # ohm/m
    Xp = x / 1000                   # ohm/m
    du = k * I * L * (Rp * cos + Xp * sen)
    r.update({'S': S, 'du': du, 'pct': 100 * du / U})
    kk = '√3' if fases == 3 else '2'
    if x:
        L_.append('ΔU = %s·I·L·(r·cosφ + x·senφ) = %s·%s A·%s m·(%s·%s + %s·%s) = %s V → %s %% de %s V'
                  % (kk, kk, n(I, 2), n(L, 1), n(Rp, 6), n(cos, 2), n(Xp, 6), n(sen, 3), n(du, 2), n(r['pct'], 2), n(U, 0)))
    else:
        L_.append('ΔU = %s·I·L·r·cosφ, con r = ρ/S = %s Ω/m: %s·%s A·%s m·%s·%s = %s V → %s %% de %s V'
                  % (kk, n(Rp, 6), kk, n(I, 2), n(L, 1), n(Rp, 6), n(cos, 2), n(du, 2), n(r['pct'], 2), n(U, 0)))
    if limite:
        L_.append('%s: %s %% %s %s %% admisible' % ('Verifica' if r['pct'] <= limite + 1e-9 else 'NO VERIFICA', n(r['pct'], 2),
                                                 '≤' if r['pct'] <= limite + 1e-9 else '>', n(limite, 1)))
    if x == 0 and S > 50:
        L_.append('AVISO: con más de 50 mm² conviene sumar la reactancia del catálogo del cable (--x en Ω/km).')
    L_.append('La caída de un circuito terminal se suma a la de la línea que alimenta su tablero; el sector de la reglamentación fija el límite.')
    return r, L_


def capacitor(P, cos1, cos2, U=380, f=50):
    if not 0 < cos1 < cos2 <= 1:
        raise ValueError('tiene que ser 0 < cos1 < cos2 ≤ 1')
    t1, t2 = math.tan(math.acos(cos1)), math.tan(math.acos(cos2))
    Q = P * (t1 - t2)               # kvar
    w = 2 * math.pi * f
    C_tri = Q * 1000 / (3 * w * U ** 2) * 1e6    # uF por fase, en triangulo (cada uno ve la tension de linea)
    C_est = Q * 1000 / (w * U ** 2) * 1e6        # uF por fase, en estrella
    I1, I2 = P * 1000 / (math.sqrt(3) * U * cos1), P * 1000 / (math.sqrt(3) * U * cos2)
    L_ = ['Potencia reactiva a compensar: Qc = P·(tg φ1 − tg φ2) = %s·(%s − %s) = %s kvar' % (n(P, 1), n(t1, 4), n(t2, 4), n(Q, 2)),
          'Capacidad por fase en triángulo: C = Qc/(3·ω·U²) = %s µF; en estrella: C = Qc/(ω·U²) = %s µF (ω = 2π·%g)' % (n(C_tri, 1), n(C_est, 1), f),
          'Corriente de línea: de %s A a %s A (las pérdidas en los cables bajan %s %%)' % (n(I1, 1), n(I2, 1), n(100 * (1 - (I2 / I1) ** 2), 1)),
          'El cos φ objetivo lo fija la distribuidora en su cuadro tarifario; elegir el banco con el escalón comercial siguiente.']
    return {'Q': Q, 'C_tri': C_tri, 'C_est': C_est, 'I1': I1, 'I2': I2}, L_


def cortocircuito(S, uk, U=400, L=None, seccion=None, material='cu', t=None, k=None):
    In = S * 1000 / (math.sqrt(3) * U)
    Zt = uk / 100 * U ** 2 / (S * 1000)          # ohm por fase (se toma toda reactiva)
    Ik = U / (math.sqrt(3) * Zt)
    L_ = ['Transformador de %s kVA, uk = %s %%: In = S/(√3·U) = %s A; Zt = uk·U²/S = %s Ω' % (n(S, 0), n(uk, 1), n(In, 1), n(Zt, 5)),
          'Cortocircuito trifásico en bornes (red de alimentación infinita): Ik = U/(√3·Zt) = In/uk = %s kA' % n(Ik / 1000, 2)]
    r = {'In': In, 'Zt': Zt, 'Ik': Ik}
    if L and seccion:
        Rc = resistividad(material, 20) * L / seccion
        Z = math.hypot(Rc, Zt)
        r['Ik_fin'] = U / (math.sqrt(3) * Z)
        L_.append('Al final de %s m de cable de %s mm²: Rc = ρ·L/S = %s Ω; Z = √(Rc² + Zt²) = %s Ω → Ik = %s kA'
                  % (n(L, 0), n(seccion, 1), n(Rc, 5), n(Z, 5), n(r['Ik_fin'] / 1000, 2)))
    if t and k:
        r['Smin'] = Ik * math.sqrt(t) / k
        L_.append('Sección mínima por calentamiento (falla al principio del cable, la corriente más alta): S ≥ Ik·√t/k = %s·√%s/%s = %s mm²'
                  % (miles(Ik), n(t, 2), n(k, 0), n(r['Smin'], 1)))
    L_.append('Cálculo simplificado: IEC 60909 suma la impedancia de la red y el factor de tensión c; sirve para elegir el poder de corte con margen.')
    return r, L_


def jabalina(rho, L, d, maximo=40.0):
    a = d / 2000                                    # radio en m
    R = rho / (2 * math.pi * L) * (math.log(4 * L / a) - 1)
    L_ = ['Jabalina de %s m y %s mm de diámetro en suelo de %s Ω·m: R = ρ/(2π·L)·(ln(4·L/a) − 1) = %s Ω (fórmula de Dwight)'
          % (n(L, 2), n(d, 1), n(rho, 0), n(R, 1))]
    if maximo:
        L_.append('%s: %s Ω %s %s Ω' % ('Verifica' if R <= maximo else 'NO VERIFICA', n(R, 1), '≤' if R <= maximo else '>', n(maximo, 0)))
        if R > maximo:
            L_.append('Para bajarla: jabalina más larga, varias en paralelo separadas al menos su largo (no bajan a R/n por la interferencia) o mejorar el suelo.')
    L_.append('ρ del suelo: medirla (método de Wenner); el valor final se verifica con la medición en obra.')
    return {'R': R}, L_


def lumenes(a, b, h, E, flujo, cu, fm):
    S = a * b
    k = a * b / (h * (a + b))
    phit = E * S / (cu * fm)
    N = math.ceil(phit / flujo - 1e-9)
    Er = N * flujo * cu * fm / S
    L_ = ['Índice del local: k = a·b/(h·(a + b)) = %s·%s/(%s·(%s + %s)) = %s (con k y las reflectancias se lee CU en la tabla del fabricante)'
          % (n(a, 2), n(b, 2), n(h, 2), n(a, 2), n(b, 2), n(k, 2)),
          'Flujo total: Φt = E·S/(CU·fm) = %s·%s/(%s·%s) = %s lm' % (n(E, 0), n(S, 2), n(cu, 2), n(fm, 2), miles(phit)),
          'Luminarias: N = Φt/Φ = %s/%s = %s → %d' % (miles(phit), miles(flujo), n(phit / flujo, 2), N),
          'Iluminancia con %d luminarias: E = N·Φ·CU·fm/S = %s lx' % (N, n(Er, 0)),
          'Distribuirlas en filas parejas y respetar la separación máxima del fabricante; el nivel exigido sale de la norma o de la consigna.']
    return {'k': k, 'phit': phit, 'N': N, 'E': Er}, L_


# ------------------------------------------------------------------------------------------ demo
def cerca(x, y, tol):
    return abs(x - y) <= tol


def cmd_demo():
    ok = []
    r, _ = corriente(10, 380, 3, 0.85)
    ok.append(('corriente de 10 kW a 380 V y 0,85: %s A (10 000/(√3·380·0,85) = 17,87)' % n(r['I'], 2), cerca(r['I'], 10000 / (math.sqrt(3) * 380 * 0.85), 1e-9)))
    r, _ = caida(20, 50, 4, 380, 3, 0.85, 'cu', 70)
    a_mano = math.sqrt(3) * 20 * 50 * 0.017241 * (1 + 0.00393 * 50) / 4 * 0.85
    ok.append(('caída de 20 A en 50 m de 4 mm² Cu a 70 °C: %s V (%s %%)' % (n(r['du'], 3), n(r['pct'], 2)), cerca(r['du'], a_mano, 1e-9)))
    r2, _ = caida(20, 50, None, 380, 3, 0.85, 'cu', 70, limite=r['pct'])
    ok.append(('la sección mínima para esa caída vuelve a 4 mm²', cerca(r2['Smin'], 4.0, 1e-9) and r2['S'] == 4))
    r, _ = capacitor(100, 0.75, 0.95, 380, 50)
    q = 100 * (math.tan(math.acos(0.75)) - math.tan(math.acos(0.95)))
    ok.append(('capacitor de 100 kW de 0,75 a 0,95: %s kvar y %s µF por fase en triángulo' % (n(r['Q'], 2), n(r['C_tri'], 1)),
               cerca(r['Q'], q, 1e-9) and cerca(r['C_tri'], q * 1000 / (3 * 2 * math.pi * 50 * 380 ** 2) * 1e6, 1e-9)))
    r, _ = cortocircuito(630, 4, 400)
    ok.append(('cortocircuito de 630 kVA y 4 %%: %s kA (In/uk = 909,3/0,04)' % n(r['Ik'] / 1000, 2), cerca(r['Ik'], 630000 / (math.sqrt(3) * 400) / 0.04, 1e-6)))
    r, _ = jabalina(100, 1.5, 14.6)
    ok.append(('jabalina de 1,5 m en 100 Ω·m: %s Ω (100/(2π·1,5)·(ln(4·1,5/0,0073) − 1))' % n(r['R'], 2),
               cerca(r['R'], 100 / (2 * math.pi * 1.5) * (math.log(6 / 0.0073) - 1), 1e-9)))
    r, _ = lumenes(10, 6, 2.2, 500, 4000, 0.6, 0.8)
    ok.append(('lúmenes: k = %s, %d luminarias, %s lx' % (n(r['k'], 2), r['N'], n(r['E'], 0)), r['N'] == 16 and cerca(r['E'], 512, 1e-9)))
    for nombre, bien in ok:
        print('  %s %s' % ('ok ' if bien else 'MAL', nombre))
    todo = all(b for _, b in ok)
    print('DEMO %s' % ('OK' if todo else 'FALLO'))
    return 0 if todo else 1


def construir_parser():
    ap = argparse.ArgumentParser(prog='electricas.py', description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('corriente')
    p.add_argument('--P', type=float, required=True)
    p.add_argument('--U', type=float, required=True)
    p.add_argument('--fases', type=int, default=3)
    p.add_argument('--cos', type=float, default=0.85)
    p.add_argument('--rend', type=float, default=1.0)
    p = sp.add_parser('caida')
    p.add_argument('--I', type=float, required=True)
    p.add_argument('--L', type=float, required=True)
    p.add_argument('--S', type=float)
    p.add_argument('--U', type=float, default=380)
    p.add_argument('--fases', type=int, default=3)
    p.add_argument('--cos', type=float, default=0.85)
    p.add_argument('--material', default='cu', choices=['cu', 'al'])
    p.add_argument('--temp', type=float, default=70)
    p.add_argument('--x', type=float, default=0.0, help='reactancia en ohm/km (del catalogo)')
    p.add_argument('--limite', type=float)
    p = sp.add_parser('capacitor')
    p.add_argument('--P', type=float, required=True)
    p.add_argument('--cos1', type=float, required=True)
    p.add_argument('--cos2', type=float, required=True)
    p.add_argument('--U', type=float, default=380)
    p.add_argument('--f', type=float, default=50)
    p = sp.add_parser('cortocircuito')
    p.add_argument('--S', type=float, required=True)
    p.add_argument('--uk', type=float, required=True)
    p.add_argument('--U', type=float, default=400)
    p.add_argument('--L', type=float)
    p.add_argument('--seccion', type=float)
    p.add_argument('--material', default='cu', choices=['cu', 'al'])
    p.add_argument('--t', type=float)
    p.add_argument('--k', type=float)
    p = sp.add_parser('jabalina')
    p.add_argument('--rho', type=float, required=True)
    p.add_argument('--L', type=float, required=True)
    p.add_argument('--d', type=float, required=True)
    p.add_argument('--max', type=float, default=40.0)
    p = sp.add_parser('lumenes')
    for x in ('a', 'b', 'h', 'E', 'flujo', 'cu', 'fm'):
        p.add_argument('--' + x, type=float, required=True)
    sp.add_parser('demo')
    return ap


def main(argv=None):
    a = construir_parser().parse_args(argv)
    try:
        if a.cmd == 'demo':
            return cmd_demo()
        if a.cmd == 'corriente':
            _, L = corriente(a.P, a.U, a.fases, a.cos, a.rend)
        elif a.cmd == 'caida':
            _, L = caida(a.I, a.L, a.S, a.U, a.fases, a.cos, a.material, a.temp, a.x, a.limite)
        elif a.cmd == 'capacitor':
            _, L = capacitor(a.P, a.cos1, a.cos2, a.U, a.f)
        elif a.cmd == 'cortocircuito':
            _, L = cortocircuito(a.S, a.uk, a.U, a.L, a.seccion, a.material, a.t, a.k)
        elif a.cmd == 'jabalina':
            _, L = jabalina(a.rho, a.L, a.d, a.max)
        else:
            _, L = lumenes(a.a, a.b, a.h, a.E, a.flujo, a.cu, a.fm)
    except ValueError as ex:
        print('electricas.py: %s' % ex, file=sys.stderr)
        return 2
    print('\n'.join(L))
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
