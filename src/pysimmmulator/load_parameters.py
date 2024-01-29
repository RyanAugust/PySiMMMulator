import yaml
from PySiMMMulator.helpers import (
    basic_parameters,
    baseline
)

def load_config():
    with open("config.yaml") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg

cfg = load_config()
my_basic_params = basic_parameters(**cfg['basic_parms'])
my_baseline_params = baseline(basic_params=my_basic_params, **cfg['baseline_parms'])
