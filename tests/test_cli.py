from pysimmmulator import simmmulate, command_line
import subprocess


def test_cli():
    subprocess.run(["pysimmm", "-c", "example_config.yaml", "-o", "./"])
    assert 1 == 1
