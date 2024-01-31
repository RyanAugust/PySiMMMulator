from pysimmmulator import load_parameters

def test_load_cfg():
    assert type(load_parameters.cfg) == dict

def test_cfg_base_keys():
    cfg = load_parameters.cfg
    assert 'basic_params' in cfg.keys()

def test_media_cfg_check():
    cfg = load_parameters.cfg
    media_params = load_parameters.media_parameters(**cfg['media_params'])
    media_params.check(basic_params=load_parameters.my_basic_params)
    assert True == True
