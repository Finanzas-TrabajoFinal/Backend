import pytest
from decimal import Decimal
from app.domain.rates import resolver_tasas
from app.domain.enums import TipoTasa, Capitalizacion


def test_tna_diaria_a_tea():
    tea, tem = resolver_tasas(
        tasa_valor=Decimal("0.15"),
        tasa_tipo=TipoTasa.TNA,
        capitalizacion=Capitalizacion.DIARIA,
        frecuencia_dias=30,
        dias_anio=360,
    )
    assert float(tea) == pytest.approx(0.16179795, abs=1e-6)
    assert float(tem) == pytest.approx(0.01257582, abs=1e-6)


def test_tea_directa():
    tea, tem = resolver_tasas(
        tasa_valor=Decimal("0.16179795"),
        tasa_tipo=TipoTasa.TEA,
        capitalizacion=None,
        frecuencia_dias=30,
        dias_anio=360,
    )
    assert float(tea) == pytest.approx(0.16179795, abs=1e-6)
    assert float(tem) == pytest.approx(0.01257582, abs=1e-6)
