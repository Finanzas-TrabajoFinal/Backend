"""Golden-master test contra el caso base del Excel de Interbank."""
import pytest
from app.domain.engine import simular
from app.schemas.cotizacion import SimulacionInput
from app.domain.enums import TipoTasa, Capitalizacion, Moneda


@pytest.fixture
def caso_interbank():
    return SimulacionInput(
        moneda=Moneda.PEN,
        precio_venta=16000,
        pct_cuota_inicial=0.20,
        pct_cuota_final=0.40,
        num_anios=3,
        num_cuotas=36,
        tasa_valor=0.15,
        tasa_tipo=TipoTasa.TNA,
        capitalizacion=Capitalizacion.DIARIA,
        frecuencia_dias=30,
        dias_anio=360,
        costes_iniciales={"notariales": 100, "registrales": 75},
        costes_periodicos={
            "gps": 20,
            "portes": 3.5,
            "gastos_adm": 3.5,
            "pct_seg_desgravamen": 0.00049,
            "pct_seg_riesgo": 0.003,
        },
        gracia={"total": 3, "parcial": 3},
        cok_anual=0.50,
    )


def test_golden_cabecera(caso_interbank):
    r = simular(caso_interbank)
    c = r.cabecera
    assert float(c.tea)           == pytest.approx(0.16179795, abs=1e-6)
    assert float(c.tem)           == pytest.approx(0.01257582, abs=1e-6)
    assert float(c.cuota_inicial) == pytest.approx(3200,       abs=1e-2)
    assert float(c.cuota_final)   == pytest.approx(6400,       abs=1e-2)
    assert float(c.monto_prestamo) == pytest.approx(12975,     abs=1e-2)
    assert float(c.saldo_regular)  == pytest.approx(9015.9907, abs=1e-3)
    assert float(c.cuota_regular)  == pytest.approx(379.1584,  abs=1e-3)
    assert float(c.tir_mensual)    == pytest.approx(0.01586175, abs=1e-6)
    assert float(c.tcea)           == pytest.approx(0.20785636, abs=1e-5)
    assert float(c.van)            == pytest.approx(4436.1832,  abs=1e-2)


def test_num_filas(caso_interbank):
    r = simular(caso_interbank)
    # 36 cuotas + 1 liquidación del cuotón = 37 filas
    assert len(r.cronograma) == 37


def test_gracia_total_no_paga_cuota(caso_interbank):
    r = simular(caso_interbank)
    for fila in r.cronograma[:3]:
        assert fila.pg.value == "T"
        assert fila.regular.cuota == pytest.approx(0, abs=1e-9)


def test_gracia_parcial_cuota_igual_interes(caso_interbank):
    r = simular(caso_interbank)
    for fila in r.cronograma[3:6]:
        assert fila.pg.value == "P"
        # cuota = interés + desgravamen (solo paga interés, no amortiza)
        assert fila.regular.amort == pytest.approx(0, abs=1e-9)


def test_cuoton_saldo_cero_al_final(caso_interbank):
    r = simular(caso_interbank)
    assert float(r.cronograma[-1].cuoton.saldo_fin) == pytest.approx(0, abs=1e-4)
