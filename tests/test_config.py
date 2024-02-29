from pysimmmulator import load_parameters


def test_load_cfg():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    assert type(cfg) == dict


def test_cfg_base_keys():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    assert "basic_params" in cfg.keys()


def test_media_cfg_check():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    media_params = load_parameters.media_parameters(**cfg["media_params"])
    media_params.check(basic_params=my_basic_params)
    assert True == True


def test_cvr_cfg_check():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    cvr_params = load_parameters.cvr_parameters(**cfg["cvr_params"])
    cvr_params.check(basic_params=my_basic_params)
    assert True == True


def test_adstock_cfg_check():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    adstock_params = load_parameters.adstock_parameters(**cfg["adstock_params"])
    adstock_params.check(basic_params=my_basic_params)
    assert True == True

def test_validate_config():
    overall = load_parameters.validate_config(config_path="./example_config.yaml")
    assert overall == True