import pytest

from r2k.inventario import Producto


@pytest.fixture
def catalogo():
    return {
        1: Producto(1, "Guantes Ñandú", 25000, 40000, 5),
        2: Producto(2, "Casco D'Angelo", 120000, 180000, 10),
        3: Producto(3, "Impermeable Tía Rosa", 35000, 55000, 0),
        4: Producto(4, "", 8000, 12000, 3),
        5: Producto(5, "Calcomanía R2K", 0, 0, 50),
        6: Producto(6, "Espejo viejo", 10000, 25000, 0, activo=False),
    }


@pytest.fixture
def ventas():
    return [
        ("2026-10-31", "Casco integral", 1, 180000),
        ("2026-11-01", "Casco integral", 2, 180000),
        ("2026-11-03", "Guantes de moto", 5, 40000),
        ("2026-11-15", "Casco integral", 1, 180000),
        ("2026-11-30", "Espejo retrovisor", 2, 25000),
        ("2026-12-01", "Guantes de moto", 1, 40000),
    ]
