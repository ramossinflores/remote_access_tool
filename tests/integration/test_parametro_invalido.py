import subprocess

def test_maquina_no_existe():
    resultado = subprocess.run(
        ["python3", "-m", "remote_access_tool.main", "no_existo"],
        capture_output=True,
        text=True
    )

    print("STDERR:", resultado.stderr)
    print("STDOUT:", resultado.stdout)

    assert "No se encontró la máquina" in resultado.stderr
    assert resultado.returncode != 0
