import pytest

from r2k import datos
from r2k.copia import copiar


def test_la_copia_tiene_los_mismos_datos(tmp_path):
    ruta = tmp_path / "r2k.db"
    con = datos.conectar(ruta)
    datos.crear_producto(con, "Casco integral", 180000, 10)
    con.close()
    usb = tmp_path / "usb"
    usb.mkdir()

    archivo = copiar(ruta, usb, hoy="2026-11-30")

    assert archivo == usb / "R2K_copias" / "r2k_2026-11-30.db"
    copia = datos.conectar(archivo)
    assert [p["nombre"] for p in datos.listar_productos(copia)] == ["Casco integral"]
    copia.close()


def test_sin_usb_conectada_avisa(tmp_path):
    ruta = tmp_path / "r2k.db"
    datos.conectar(ruta).close()
    with pytest.raises(FileNotFoundError, match="USB"):
        copiar(ruta, tmp_path / "no_existe")


def test_sin_base_de_datos_avisa(tmp_path):
    with pytest.raises(FileNotFoundError, match="base de datos"):
        copiar(tmp_path / "r2k.db", tmp_path)
