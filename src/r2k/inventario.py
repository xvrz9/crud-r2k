from dataclasses import dataclass

CANTIDAD_MINIMA_VENTA = 1
CAMPOS_ENTEROS_NO_NEGATIVOS = ("precio_compra", "precio_venta", "stock_actual")


class ErrorInventario(Exception):
    """Base de todos los errores de dominio del inventario."""


class StockInsuficienteError(ErrorInventario):
    """La cantidad vendida supera el stock disponible."""


class CantidadInvalidaError(ErrorInventario):
    """La cantidad no es un entero o es menor que CANTIDAD_MINIMA_VENTA."""


class ProductoNoEncontradoError(ErrorInventario):
    """El id_producto no está en el inventario."""


class ProductoInvalidoError(ErrorInventario, ValueError):
    """Un precio o el stock del producto no es un entero mayor o igual a 0."""


def _es_entero(valor: object) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)


@dataclass
class Producto:
    id_producto: int
    nombre: str
    precio_compra: int  # pesos colombianos, entero (nunca float)
    precio_venta: int
    stock_actual: int

    def __post_init__(self) -> None:
        for campo in CAMPOS_ENTEROS_NO_NEGATIVOS:
            valor = getattr(self, campo)
            if not _es_entero(valor) or valor < 0:
                raise ProductoInvalidoError(
                    f"{campo} debe ser un entero mayor o igual a 0 "
                    f"(recibido: {valor!r})"
                )


def _buscar_producto(productos: dict[int, Producto], id_producto: int) -> Producto:
    try:
        return productos[id_producto]
    except KeyError:
        raise ProductoNoEncontradoError(
            f"No existe el producto {id_producto}"
        ) from None


def _validar_cantidad(cantidad: int) -> None:
    if not _es_entero(cantidad):
        raise CantidadInvalidaError(
            f"La cantidad debe ser un número entero (recibido: {cantidad!r})"
        )
    if cantidad < CANTIDAD_MINIMA_VENTA:
        raise CantidadInvalidaError(
            f"La cantidad debe ser al menos {CANTIDAD_MINIMA_VENTA} "
            f"(recibido: {cantidad})"
        )


def _validar_stock_suficiente(producto: Producto, cantidad: int) -> None:
    if cantidad > producto.stock_actual:
        raise StockInsuficienteError(
            f"{producto.nombre}: hay {producto.stock_actual} en stock "
            f"y se intentaron vender {cantidad}"
        )


def registrar_salida(
    productos: dict[int, Producto], id_producto: int, cantidad: int
) -> int:
    """Descuenta `cantidad` del stock del producto y devuelve el nuevo stock_actual.

    Si algo falla, lanza el error correspondiente y el stock NO cambia.
    """
    producto = _buscar_producto(productos, id_producto)
    _validar_cantidad(cantidad)
    _validar_stock_suficiente(producto, cantidad)
    producto.stock_actual -= cantidad
    return producto.stock_actual
