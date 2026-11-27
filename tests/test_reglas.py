import pytest

from r2k.inventario import (
    CantidadInvalidaError,
    ProductoConStockError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
    eliminar_producto,
    registrar_entrada,
    registrar_salida,
    reporte_mensual,
)


def stocks(catalogo):
    return {i: p.stock_actual for i, p in catalogo.items()}


# registrar_salida


def test_vender_producto_agotado_falla(catalogo):
    with pytest.raises(StockInsuficienteError):
        registrar_salida(catalogo, 3, 1)
    assert catalogo[3].stock_actual == 0


def test_mensaje_de_stock_insuficiente_con_enie(catalogo):
    with pytest.raises(StockInsuficienteError, match="Guantes Ñandú"):
        registrar_salida(catalogo, 1, 6)


def test_no_se_puede_vender_un_producto_eliminado(catalogo):
    with pytest.raises(ProductoNoEncontradoError):
        registrar_salida(catalogo, 6, 1)


# registrar_entrada


@pytest.mark.parametrize(
    ("id_producto", "cantidad", "esperado"),
    [(1, 1, 6), (2, 15, 25), (3, 4, 4), (2, 1000, 1010)],
)
def test_entrada_suma_al_stock(catalogo, id_producto, cantidad, esperado):
    assert registrar_entrada(catalogo, id_producto, cantidad) == esperado
    assert catalogo[id_producto].stock_actual == esperado


@pytest.mark.parametrize(
    ("id_producto", "cantidad", "error"),
    [
        (1, 0, CantidadInvalidaError),
        (1, -5, CantidadInvalidaError),
        (1, 2.5, CantidadInvalidaError),
        (99, 3, ProductoNoEncontradoError),
        (6, 3, ProductoNoEncontradoError),
    ],
)
def test_entrada_invalida_no_cambia_el_stock(catalogo, id_producto, cantidad, error):
    antes = stocks(catalogo)
    with pytest.raises(error):
        registrar_entrada(catalogo, id_producto, cantidad)
    assert stocks(catalogo) == antes


# eliminar_producto (tabla de decision)


def test_eliminar_producto_con_stock_cero(catalogo):
    eliminar_producto(catalogo, 3)
    assert catalogo[3].activo is False
    assert 3 in catalogo


def test_eliminar_producto_con_stock_falla(catalogo):
    with pytest.raises(ProductoConStockError, match="todavía tiene 5 unidades"):
        eliminar_producto(catalogo, 1)
    assert catalogo[1].activo is True


def test_eliminar_producto_con_una_unidad_falla(catalogo):
    registrar_salida(catalogo, 4, 2)
    with pytest.raises(ProductoConStockError, match="todavía tiene 1 unidades"):
        eliminar_producto(catalogo, 4)


@pytest.mark.parametrize("id_producto", [99, 6])
def test_eliminar_producto_que_no_existe_o_ya_se_elimino(catalogo, id_producto):
    with pytest.raises(ProductoNoEncontradoError):
        eliminar_producto(catalogo, id_producto)


# reporte_mensual


def test_reporte_de_noviembre(ventas):
    assert reporte_mensual(ventas, "2026-11") == {
        "mes": "2026-11",
        "productos": [
            {"nombre": "Casco integral", "cantidad": 3, "valor": 540000},
            {"nombre": "Guantes de moto", "cantidad": 5, "valor": 200000},
            {"nombre": "Espejo retrovisor", "cantidad": 2, "valor": 50000},
        ],
        "total_vendido": 790000,
    }


@pytest.mark.parametrize(
    ("mes", "total"),
    [("2026-10", 180000), ("2026-12", 40000), ("2026-01", 0)],
)
def test_reporte_solo_cuenta_las_ventas_del_mes(ventas, mes, total):
    assert reporte_mensual(ventas, mes)["total_vendido"] == total


def test_reporte_sin_ventas():
    assert reporte_mensual([], "2026-11") == {
        "mes": "2026-11",
        "productos": [],
        "total_vendido": 0,
    }


@pytest.mark.parametrize("mes", ["2026-00", "2026-13", "2026-1", "noviembre", None])
def test_reporte_con_mes_invalido(ventas, mes):
    with pytest.raises(ValueError):
        reporte_mensual(ventas, mes)
