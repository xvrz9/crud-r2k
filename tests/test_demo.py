from r2k.__main__ import ejecutar_demo


def test_la_demo_muestra_la_venta_y_el_rechazo(capsys):
    ejecutar_demo()
    salida = capsys.readouterr().out
    assert "stock: 7" in salida
    assert "rechazada" in salida
    assert "Stock de Guantes de moto: 5" in salida
