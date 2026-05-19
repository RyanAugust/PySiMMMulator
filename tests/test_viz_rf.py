import pytest
import os
from pysimmmulator.simulate import Simulate

def test_viz_reach_frequency():
    config = {
        "basic_params": {
            "years": 1,
            "channels_impressions": ["TV"],
            "channels_clicks": [],
            "frequency_of_campaigns": 7,
            "start_date": "2023/01/01",
            "true_cvr": {"TV": 0.01},
            "revenue_per_conv": 100.0,
        },
        "baseline_params": {
            "base_p": 1000, "trend_p": 100, "temp_var": 10, "temp_coef_mean": 1.0, "temp_coef_sd": 0.1, "error_std": 50,
        },
        "ad_spend_params": {
            "campaign_spend_mean": 5000, "campaign_spend_std": 500,
            "max_min_proportion_on_each_channel": {},
        },
        "media_params": {
            "true_cpm": {"TV": 10.0}, "true_cpc": {},
            "noisy_cpm_cpc": {"TV": {"loc": 0.0, "scale": 1.0}},
            "true_reach_frequency": {
                "TV": {"frequency": 2.5}
            }
        },
        "cvr_params": { "noisy_cvr": { "TV": {"loc": 1.0, "scale": 0.1} } },
        "adstock_params": {
            "adstock": { "TV": {"type": "geometric", "params": {"lambda": 0.5}} },
            "saturation": { "TV": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}} },
        },
        "output_params": { "aggregation_level": "daily" }
    }

    sim = Simulate()
    result = sim.run_with_config(config)
    df = result.df

    sim.plot_reach(df=df, agg='daily')
    assert os.path.exists("Reach_by_channel.png")
    os.remove("Reach_by_channel.png")

    sim.plot_frequency(df=df, agg='daily')
    assert os.path.exists("Frequency_by_channel.png")
    os.remove("Frequency_by_channel.png")
