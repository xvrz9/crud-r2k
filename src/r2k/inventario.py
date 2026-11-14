"""Reglas de inventario de CRUD R2K: productos y salida de mercancía por venta.

Es lógica de dominio pura: no usa base de datos, red ni archivos. El inventario
se recibe como un diccionario de id_producto a Producto.
"""

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
    """Dice si `valor` es un entero de verdad.

    Recibe cualquier objeto. Devuelve True solo para `int`; devuelve False para
    `bool` (que en Python es subclase de `int`), `float`, texto, None y demás.
    No lanza errores.
    """
    return isinstance(valor, int) and not isinstance(valor, bool)


@dataclass
class Producto:
    """Un producto del inventario de R2K (modelo de datos del Diseño S4, §5).

    Atributos:
        id_producto: identificador del producto.
        nombre: nombre con el que se muestra.
        precio_compra: lo que costó, en pesos colombianos enteros.
        precio_venta: a cómo se vende, en pesos colombianos enteros.
        stock_actual: unidades disponibles.

    Lanza:
        ProductoInvalidoError: al crearlo, si `precio_compra`, `precio_venta` o
            `stock_actual` no es un entero o es negativo. La validación solo
            corre al crear el objeto, no en asignaciones posteriores.
    """

    id_producto: int
    nombre: str
    precio_compra: int
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
    """Busca un producto en el inventario por su id.

    Recibe:
        productos: inventario, diccionario de id_producto a Producto.
        id_producto: id que se quiere encontrar (la clave del diccionario).

    Devuelve:
        El mismo objeto Producto guardado en el diccionario, no una copia.

    Lanza:
        ProductoNoEncontradoError: si `id_producto` no es una clave del inventario.
    """
    try:
        return productos[id_producto]
    except KeyError:
        raise ProductoNoEncontradoError(
            f"No existe el producto {id_producto}"
        ) from None


def _validar_cantidad(cantidad: int) -> None:
    """Comprueba que la cantidad a vender sea un entero de al menos 1 unidad.

    Recibe:
        cantidad: unidades que se quieren vender.

    Devuelve:
        None si la cantidad es válida.

    Lanza:
        CantidadInvalidaError: si `cantidad` no es un entero (decimal, bool,
            texto, None) o si es menor que CANTIDAD_MINIMA_VENTA.
    """
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
    """Comprueba que el producto tenga unidades suficientes para la venta.

    Recibe:
        producto: el producto que se va a vender.
        cantidad: unidades a vender, ya validadas como entero.

    Devuelve:
        None si `cantidad` es menor o igual que `producto.stock_actual`.

    Lanza:
        StockInsuficienteError: si `cantidad` es mayor que el stock. El mensaje
            incluye el nombre del producto, el stock y la cantidad pedida.
    """
    if cantidad > producto.stock_actual:
        raise StockInsuficienteError(
            f"{producto.nombre}: hay {producto.stock_actual} en stock "
            f"y se intentaron vender {cantidad}"
        )


def registrar_salida(
    productos: dict[int, Producto], id_producto: int, cantidad: int
) -> int:
    """Registra la venta de un producto y descuenta las unidades de su stock (HU-02).

    Primero busca el producto, luego valida la cantidad y el stock, y solo al
    final descuenta. Por eso, si lanza cualquier error, el stock no cambia.

    Recibe:
        productos: inventario, diccionario de id_producto a Producto.
        id_producto: id del producto vendido.
        cantidad: unidades vendidas; entero mayor o igual a 1.

    Devuelve:
        El nuevo `stock_actual` del producto (entero, 0 si se vendió todo).

    Efecto:
        Modifica `stock_actual` del producto dentro del diccionario recibido.

    Lanza:
        ProductoNoEncontradoError: si `id_producto` no está en el inventario.
        CantidadInvalidaError: si `cantidad` no es un entero o es menor que 1.
        StockInsuficienteError: si `cantidad` es mayor que el stock del producto.
    """
    producto = _buscar_producto(productos, id_producto)
    _validar_cantidad(cantidad)
    _validar_stock_suficiente(producto, cantidad)
    producto.stock_actual -= cantidad
    return producto.stock_actual
