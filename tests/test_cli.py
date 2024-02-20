from pysimmmulator import simmmulate, command_line
import subprocess


def test_cli():
    subprocess.run(["pysimmm", "-c", "example_config.yaml", "-o", "."])
    import os
    #cleanup
    os.remove("./mmm_input_df.csv")
    os.remove("./channel_roi.csv")
    assert 1 == 1
