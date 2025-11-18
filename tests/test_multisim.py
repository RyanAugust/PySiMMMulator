from pysimmmulator import load_parameters, Multisim

def test_initiate_msim():
    msim = Multisim()
    assert 1 == 1

def test_multiple_runs():
    cfg = load_parameters.load_config(config_path="./examples/example_config.yaml")
    msim = Multisim()
    msim.run(config=cfg, runs=10)
    assert len(msim.final_frames) == 10
