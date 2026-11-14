"""Pruebas de abuso: entradas que intentan romper el contrato de inventario.

Se agregaron en la revisión de seguridad de la semana 6. Las pruebas de la
semana 5 (test_inventario.py) no se modificaron.
"""

import pytest

from r2k.inventario import CantidadInvalidaError, Producto, registrar_salida

STOCK_INICIAL = 10


@pytest.fixture
def productos():
    return {1: Producto(1, "Casco integral", 120000, 180000, STOCK_INICIAL)}


# --- H-01: la cantidad debe ser un entero de verdad ---
@pytest.mark.parametrize(
    "cantidad",
    [2.5, float("nan"), float("inf"), True, "3", None, [1]],
    ids=["decimal", "nan", "infinito", "bool", "texto", "none", "lista"],
)
def test_cantidad_que_no_es_entero_se_rechaza_y_no_cambia_el_stock(
    productos, cantidad
):
    with pytest.raises(CantidadInvalidaError):
        registrar_salida(productos, 1, cantidad)
    assert productos[1].stock_actual == STOCK_INICIAL


def test_el_stock_sigue_siendo_entero_despues_de_un_intento_con_decimal(productos):
    with pytest.raises(CantidadInvalidaError):
        registrar_salida(productos, 1, 0.5)
    assert type(productos[1].stock_actual) is int
