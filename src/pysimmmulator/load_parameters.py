import yaml
from pysimmmulator.helpers import (
    basic_parameters,
    baseline
)

def load_config(config_path: str = 'config.yaml') -> dict:
    with open(config_path) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg


def build_params(config_dict: dict) -> None:
    my_basic_params = basic_parameters(**config_dict['basic_params'])
    my_baseline_params = baseline(basic_params=my_basic_params, **config_dict['baseline_parms'])

cfg = load_config(config_path = 'config.yaml')
my_basic_params = basic_parameters(**cfg['basic_params'])
my_baseline_params = baseline(basic_params=my_basic_params, **cfg['baseline_parms'])
