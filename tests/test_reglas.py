import pytest

from r2k.inventario import (
    CantidadInvalidaError,
    ProductoNoEncontradoError,
    StockInsuficienteError,
    calcular_ganancia,
    estado_stock,
    registrar_entrada,
    registrar_salida,
)


def _stocks(catalogo):
    return {id_producto: p.stock_actual for id_producto, p in catalogo.items()}


def test_vender_producto_agotado_falla_y_el_stock_sigue_en_cero(catalogo):
    with pytest.raises(StockInsuficienteError):
        registrar_salida(catalogo, 3, 1)
    assert catalogo[3].stock_actual == 0


def test_mensaje_de_stock_insuficiente_conserva_la_enie(catalogo):
    with pytest.raises(StockInsuficienteError, match="Guantes Ñandú"):
        registrar_salida(catalogo, 1, 6)


@pytest.mark.parametrize(
    ("id_producto", "cantidad", "esperado"),
    [
        (1, 1, 6),
        (2, 15, 25),
        (3, 4, 4),
        (2, 1000, 1010),
    ],
    ids=["limite_cantidad_uno", "entrada_normal", "reabastece_agotado", "volumen"],
)
def test_registrar_entrada_suma_al_stock(catalogo, id_producto, cantidad, esperado):
    assert registrar_entrada(catalogo, id_producto, cantidad) == esperado


def test_registrar_entrada_guarda_el_stock_en_el_producto(catalogo):
    registrar_entrada(catalogo, 1, 2)
    assert catalogo[1].stock_actual == 7


@pytest.mark.parametrize(
    ("id_producto", "cantidad", "error"),
    [
        (1, 0, CantidadInvalidaError),
        (1, -5, CantidadInvalidaError),
        (1, 2.5, CantidadInvalidaError),
        (1, True, CantidadInvalidaError),
        (99, 3, ProductoNoEncontradoError),
    ],
    ids=[
        "limite_cantidad_cero",
        "cantidad_negativa",
        "cantidad_decimal",
        "cantidad_bool",
        "producto_inexistente",
    ],
)
def test_registrar_entrada_invalida_no_cambia_el_stock(
    catalogo, id_producto, cantidad, error
):
    antes = _stocks(catalogo)
    with pytest.raises(error):
        registrar_entrada(catalogo, id_producto, cantidad)
    assert _stocks(catalogo) == antes


@pytest.mark.parametrize(
    ("ventas", "esperado"),
    [
        ([], 0),
        ([(1, 1)], 15000),
        ([(2, 2)], 120000),
        ([(5, 10)], 0),
        ([(6, 3)], 0),
        ([(1, 2), (2, 1), (4, 3)], 102000),
        ([(7, 2)], -20000),
        ([(1, 1), (7, 2)], -5000),
    ],
    ids=[
        "vacia",
        "una_unidad",
        "dos_cascos",
        "precio_cero",
        "margen_cero",
        "varias",
        "perdida",
        "perdida_resta_a_la_ganancia",
    ],
)
def test_calcular_ganancia(catalogo, ventas, esperado):
    assert calcular_ganancia(ventas, catalogo) == esperado


def test_calcular_ganancia_devuelve_entero_y_no_float(catalogo):
    resultado = calcular_ganancia([(1, 1)], catalogo)
    assert resultado == 15000
    assert type(resultado) is int


def test_calcular_ganancia_no_cambia_el_stock(catalogo):
    antes = _stocks(catalogo)
    calcular_ganancia([(1, 2), (2, 1)], catalogo)
    assert _stocks(catalogo) == antes


@pytest.mark.parametrize(
    ("ventas", "error"),
    [
        ([(99, 1)], ProductoNoEncontradoError),
        ([(1, 0)], CantidadInvalidaError),
        ([(1, -2)], CantidadInvalidaError),
        ([(1, 1), (99, 1)], ProductoNoEncontradoError),
    ],
    ids=[
        "inexistente",
        "limite_cantidad_cero",
        "cantidad_negativa",
        "error_en_segunda",
    ],
)
def test_calcular_ganancia_invalida(catalogo, ventas, error):
    with pytest.raises(error):
        calcular_ganancia(ventas, catalogo)


@pytest.mark.parametrize(
    ("stock", "minimo", "esperado"),
    [
        (0, 3, "agotado"),
        (1, 3, "bajo"),
        (3, 3, "bajo"),
        (4, 3, "ok"),
        (50, 3, "ok"),
        (0, 0, "agotado"),
        (1, 0, "ok"),
    ],
)
def test_estado_stock(stock, minimo, esperado):
    assert estado_stock(stock, minimo) == esperado


@pytest.mark.parametrize(("stock", "minimo"), [(-1, 3), (3, -1), (-1, -1)])
def test_estado_stock_negativo_lanza_value_error(stock, minimo):
    with pytest.raises(ValueError):
        estado_stock(stock, minimo)
