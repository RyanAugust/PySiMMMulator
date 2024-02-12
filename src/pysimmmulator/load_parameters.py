import yaml
from pysimmmulator.param_handlers import (
    basic_parameters,
    baseline_parameters,
    ad_spend_parameters,
    media_parameters,
    cvr_parameters,
    adstock_parameters,
    output_parameters,
)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg


def build_params(config_dict: dict) -> None:
    my_basic_params = basic_parameters(**config_dict["basic_params"])
    my_baseline_params = baseline_parameters(basic_params=my_basic_params, **config_dict["baseline_params"])


cfg = load_config(config_path="config.yaml")
my_basic_params = basic_parameters(**cfg["basic_params"])
my_baseline_params = baseline_parameters(basic_params=my_basic_params, **cfg["baseline_params"])
my_ad_spend_params = ad_spend_parameters(**cfg["ad_spend_params"])
my_media_params = media_parameters(**cfg["media_params"])
my_cvr_params = cvr_parameters(**cfg["cvr_params"])
my_adstock_params = adstock_parameters(**cfg["adstock_params"])
my_output_params = output_parameters(**cfg["output_params"])
