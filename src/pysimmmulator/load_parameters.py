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


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg

def define_basic_params(
        years,
        channels_clicks,
        channels_impressions,
        frequency_of_campaigns,
        start_date,
        true_cvr,
        revenue_per_conv
    ):
    "Takes in requirements for basic_params and loads with dataclass for validation as precursor"
    my_basic_params = basic_parameters(
        years=years,
        channels_clicks=channels_clicks,
        channels_impressions=channels_impressions,
        frequency_of_campaigns=frequency_of_campaigns,
        start_date=start_date,
        true_cvr=true_cvr,
        revenue_per_conv=revenue_per_conv
    )
    
    return my_basic_params
