from pysimmmulator import load_parameters
import pytest

@pytest.fixture
def config():
    return load_parameters.load_config(config_path="./examples/example_config.yaml")

def test_load_cfg(config):
    assert type(config) == dict

def test_cfg_base_keys(config):
    assert "basic_params" in config.keys()

def test_media_cfg_check(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    media_params = load_parameters.MediaParameters(**config["media_params"])
    media_params.check(basic_params=my_basic_params)
    assert True == True

def test_cvr_cfg_check(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    cvr_params = load_parameters.CVRParameters(**config["cvr_params"])
    cvr_params.check(basic_params=my_basic_params)
    assert True == True

def test_adstock_cfg_check(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    adstock_params = load_parameters.AdstockParameters(**config["adstock_params"])
    adstock_params.check(basic_params=my_basic_params)
    assert True == True

def test_validate_config():
    overall = load_parameters.validate_config(config_path="./examples/example_config.yaml")
    assert overall == True
