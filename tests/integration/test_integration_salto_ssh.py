import subprocess

def test_salto_ssh_exitoso():
    # Ejecuta el script como si fueras el usuario final
    resultado = subprocess.run(
        ["python3", "utils.py", "192.168.10.10"],
        capture_output=True,
        text=True
    )

    # Verifica que la ejecución fue exitosa y la salida contiene lo esperado
    assert resultado.returncode == 0
    assert "Conectado al bastion" in resultado.stdout
    assert "ssh -tt" in resultado.stdout or "[vagrant@" in resultado.stdout
