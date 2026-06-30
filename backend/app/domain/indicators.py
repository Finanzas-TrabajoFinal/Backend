from decimal import Decimal


def calcular_van(flujos: list[Decimal], cok_mensual: Decimal) -> Decimal:
    """VAN desde perspectiva del deudor: flujo[0] = +préstamo, resto negativos."""
    van = Decimal(0)
    for t, f in enumerate(flujos):
        van += f / (1 + cok_mensual) ** t
    return van


def calcular_tir(flujos: list[Decimal], max_iter: int = 1000, tol: float = 1e-12) -> Decimal:
    """TIR mensual por Newton-Raphson."""
    # Estimación inicial
    r = Decimal("0.01")
    for _ in range(max_iter):
        f_r = Decimal(0)
        df_r = Decimal(0)
        for t, cf in enumerate(flujos):
            t_dec = Decimal(t)
            factor = (1 + r) ** t_dec
            f_r += cf / factor
            if t > 0:
                df_r -= t_dec * cf / ((1 + r) ** (t_dec + 1))
        if df_r == 0:
            break
        delta = f_r / df_r
        r -= delta
        if abs(float(delta)) < tol:
            break
    return r


def tir_a_tcea(tir_mensual: Decimal) -> Decimal:
    return (1 + tir_mensual) ** 12 - 1


def cok_anual_a_mensual(cok_anual: Decimal) -> Decimal:
    return (1 + cok_anual) ** (Decimal(1) / Decimal(12)) - 1
