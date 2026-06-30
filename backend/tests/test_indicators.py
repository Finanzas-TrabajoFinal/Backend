import pytest
from decimal import Decimal
from app.domain.indicators import calcular_tir, tir_a_tcea, cok_anual_a_mensual


def test_tcea_desde_tir():
    tir = Decimal("0.01586175")
    tcea = tir_a_tcea(tir)
    assert float(tcea) == pytest.approx(0.20785636, abs=1e-5)


def test_cok_mensual():
    cok_m = cok_anual_a_mensual(Decimal("0.50"))
    # (1.5)^(1/12) - 1
    assert float(cok_m) == pytest.approx(0.034366, abs=1e-5)
