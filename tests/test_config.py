from pysimmmulator import load_parameters

def test_load_cfg():
    assert type(load_parameters.cfg) == dict

def test_cfg_base_keys():
    cfg = load_parameters.cfg
    assert 'basic_params' in cfg.keys()