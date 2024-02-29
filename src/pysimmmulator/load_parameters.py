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
    revenue_per_conv,
):
    "Takes in requirements for basic_params and loads with dataclass for validation as precursor"
    my_basic_params = basic_parameters(
        years=years,
        channels_clicks=channels_clicks,
        channels_impressions=channels_impressions,
        frequency_of_campaigns=frequency_of_campaigns,
        start_date=start_date,
        true_cvr=true_cvr,
        revenue_per_conv=revenue_per_conv,
    )

    return my_basic_params

def validate_config(config_path: str, return_individual_results: bool = False):
    cfg = load_config(config_path=config_path)
    results = {}
    overall = True
    try:
        define_basic_params(**cfg["basic_params"])
        results.update({"basic_params":True})
    except Exception as e:
        results.update({"basic_params":e})
        overall = False
    try:
        my_basic_params = define_basic_params(**cfg["basic_params"])
        baseline_parameters(basic_params=my_basic_params, **cfg["baseline_params"])
        results.update({"baseline_params":True})
    except Exception as e:
        results.update({"baseline_params":e})
        overall = False
    
    matched_validation = {
        ad_spend_parameters:"ad_spend_params",
        media_parameters:"media_params",
        cvr_parameters:"cvr_params",
        adstock_parameters:"adstock_params",
        output_parameters:"output_params"
    }
    for handler, conf_name in matched_validation.items():
        try:
            handler(**cfg[conf_name])
            results.update({conf_name: True})
        except Exception as e:
            results.update({conf_name: e})
            overall = False

    if return_individual_results:
        return results
    else:
        return overall