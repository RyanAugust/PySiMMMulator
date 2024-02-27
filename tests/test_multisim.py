from pysimmm import load_parameters, multisim


def test_initiate_msim():
    msim = multisim()
    assert 1 == 1


def test_multiple_runs():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    msim = multisim()
    msim.run(config=cfg, runs=10)
    assert len(msim.final_frames) == 10
