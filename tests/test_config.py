from PySiMMMulator import load_parameters

def test_load_cfg():
    assert type(load_parameters.cfg) == dict