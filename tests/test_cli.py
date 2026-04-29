from pysimmmulator import command_line
import os
import unittest.mock

def test_cli():
    with unittest.mock.patch("sys.argv", ["pysimmm", "-i", "./examples/example_config.yaml", "-o", "."]):
        command_line.main()

    # check output files
    assert os.path.exists("./mmm_input_df.csv")
    assert os.path.exists("./channel_roi.csv")

    # cleanup
    os.remove("./mmm_input_df.csv")
    os.remove("./channel_roi.csv")
