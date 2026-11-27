import pytest

from r2k.inventario import (
    CantidadInvalidaError,
    Producto,
    ProductoNoEncontradoError,
    StockInsuficienteError,
    registrar_salida,
)


@pytest.fixture
def productos():
    return {
        1: Producto(1, "Casco integral", 120000, 180000, 10),
        2: Producto(2, "Guantes de moto", 25000, 40000, 5),
    }


def test_venta_normal_descuenta_el_stock(productos):
    assert registrar_salida(productos, 1, 3) == 7


def test_venta_de_una_unidad_descuenta_uno(productos):
    assert registrar_salida(productos, 2, 1) == 4


def test_la_venta_queda_guardada_en_el_producto(productos):
    registrar_salida(productos, 1, 3)
    assert productos[1].stock_actual == 7


def test_vender_todo_el_stock_lo_deja_en_cero(productos):
    assert registrar_salida(productos, 2, 5) == 0


def test_vender_una_unidad_mas_que_el_stock_falla(productos):
    with pytest.raises(StockInsuficienteError):
        registrar_salida(productos, 2, 6)


def test_stock_insuficiente_no_cambia_el_stock(productos):
    with pytest.raises(StockInsuficienteError, match="Guantes de moto"):
        registrar_salida(productos, 2, 8)
    assert productos[2].stock_actual == 5


@pytest.mark.parametrize("cantidad", [0, -1])
def test_cantidad_cero_o_negativa_lanza_error(productos, cantidad):
    with pytest.raises(CantidadInvalidaError):
        registrar_salida(productos, 1, cantidad)
    assert productos[1].stock_actual == 10


def test_producto_inexistente_lanza_error(productos):
    with pytest.raises(ProductoNoEncontradoError, match="99"):
        registrar_salida(productos, 99, 1)