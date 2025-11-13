import yaml
from pysimmmulator.param_handlers import (
    BasicParameters,
    BaselineParameters,
    AdSpendParameters,
    MediaParameters,
    CVRParameters,
    AdstockParameters,
    OutputParameters,
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
    my_basic_params = BasicParameters(
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
    """Loads and validates the parameters against individual

    Args:
        config_path (os.pathlike): path to the configuration file
        return_individual_results (bool): control for if a detailed param by param result is returned. Default is for a single bool value return
    Returns:
       (Union[bool, dict]): results of the validation check. Default will return a bool indicating overall valid or invalid status."""
    cfg = load_config(config_path=config_path)
    results = {}
    overall = True
    try:
        define_basic_params(**cfg["basic_params"])
        results.update({"basic_params": True})
    except Exception as e:
        results.update({"basic_params": e})
        overall = False
    try:
        my_basic_params = define_basic_params(**cfg["basic_params"])
        BaselineParameters(basic_params=my_basic_params, **cfg["baseline_params"])
        results.update({"baseline_params": True})
    except Exception as e:
        results.update({"baseline_params": e})
        overall = False

    matched_validation = {
        AdSpendParameters: "ad_spend_params",
        MediaParameters: "media_params",
        CVRParameters: "cvr_params",
        AdstockParameters: "adstock_params",
        OutputParameters: "output_params"
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
