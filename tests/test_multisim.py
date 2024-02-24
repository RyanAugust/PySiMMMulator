from pysimmmulator import load_parameters, multisimmm


def test_initiate_msim():
    msim = multisimmm()
    assert 1 == 1


def test_multiple_runs():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    msim = multisimmm()
    msim.run(config=cfg, runs=10)
    assert len(msim.final_frames) == 10
