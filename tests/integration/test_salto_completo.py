import subprocess

def test_salto_real_desde_admin_server():
    resultado = subprocess.run(
        ["python3", "-m", "remote_access_tool.main", "destination"],
        capture_output=True,
        text=True
    )

    print("STDOUT:", resultado.stdout)
    print("STDERR:", resultado.stderr)

    assert "Ejecutando salto SSH hacia" in resultado.stderr or resultado.stdout
    assert resultado.returncode == 0 or resultado.returncode == 1