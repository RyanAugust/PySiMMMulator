import pytest
import pandas as pd
import numpy as np
from pysimmmulator.simulate import Simulate

def test_reach_frequency_generation():
    config = {
        "basic_params": {
            "years": 1,
            "channels_impressions": ["TV"],
            "channels_clicks": ["Search"],
            "frequency_of_campaigns": 7,
            "start_date": "2023/01/01",
            "true_cvr": {"TV": 0.01, "Search": 0.02},
            "revenue_per_conv": 100.0,
        },
        "baseline_params": {
            "base_p": 1000,
            "trend_p": 100,
            "temp_var": 10,
            "temp_coef_mean": 1.0,
            "temp_coef_sd": 0.1,
            "error_std": 50,
        },
        "ad_spend_params": {
            "campaign_spend_mean": 5000,
            "campaign_spend_std": 500,
            "max_min_proportion_on_each_channel": {
                "TV": {"min": 0.4, "max": 0.6},
            },
        },
        "media_params": {
            "true_cpm": {"TV": 10.0},
            "true_cpc": {"Search": 1.0},
            "noisy_cpm_cpc": {
                "TV": {"loc": 0.0, "scale": 1.0},
                "Search": {"loc": 0.0, "scale": 0.1},
            },
            "true_reach_frequency": {
                "TV": {"frequency": 2.5}
            }
        },
        "cvr_params": {
            "noisy_cvr": {
                "TV": {"loc": 1.0, "scale": 0.1},
                "Search": {"loc": 1.0, "scale": 0.1},
            }
        },
        "adstock_params": {
            "adstock": {
                "TV": {"type": "geometric", "params": {"lambda": 0.5}},
                "Search": {"type": "geometric", "params": {"lambda": 0.3}},
            },
            "saturation": {
                "TV": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}},
                "Search": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}},
            },
        },
        "output_params": {
            "aggregation_level": "daily"
        }
    }

    sim = Simulate()
    result = sim.run_with_config(config)
    df = result.df

    assert "TV_reach" in df.columns
    assert "TV_frequency" in df.columns
    
    # Check relationship: impressions / reach = frequency
    # We use a small epsilon because of rounding in daily_reach and daily_impressions
    # impressions = reach * frequency
    
    # Filter where impressions > 0
    test_df = df[df["TV_impressions"] > 0]
    assert len(test_df) > 0
    
    for idx, row in test_df.iterrows():
        calc_freq = row["TV_impressions"] / row["TV_reach"]
        assert pytest.approx(calc_freq, abs=0.1) == row["TV_frequency"]

def test_reach_as_proportion():
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
                "TV": {"reach": 0.1} # 10% reach
            }
        },
        "cvr_params": { "noisy_cvr": { "TV": {"loc": 1.0, "scale": 0.1} } },
        "adstock_params": {
            "adstock": { "TV": {"type": "geometric", "params": {"lambda": 0.5}} },
            "saturation": { "TV": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}} },
        },
        "output_params": { "aggregation_level": "daily" },
        "geo_params": {
            "total_population": 1000000,
            "count": 5
        }
    }

    sim = Simulate()
    result = sim.run_with_config(config)
    df = result.df

    assert "TV_reach" in df.columns
    # With 1M population and 0.1 reach, reach count should be around 100,000 for the campaign.
    # Daily reach should be 100,000 / 7 approx 14286.
    
    test_df = df[df["TV_impressions"] > 0]
    daily_total_reach = test_df.groupby("date")["TV_reach"].sum()
    assert daily_total_reach.mean() == pytest.approx(100000 / 7, abs=10)

def test_frequency_min_one():
    # Force a case where reach could potentially exceed impressions
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
            "campaign_spend_mean": 100, # Very low spend
            "campaign_spend_std": 10,
            "max_min_proportion_on_each_channel": {},
        },
        "media_params": {
            "true_cpm": {"TV": 100.0}, # High CPM -> very few impressions
            "true_cpc": {},
            "noisy_cpm_cpc": {"TV": {"loc": 0.0, "scale": 1.0}},
            "true_reach_frequency": {
                "TV": {"reach": 1.0} # 100% reach
            }
        },
        "cvr_params": { "noisy_cvr": { "TV": {"loc": 1.0, "scale": 0.1} } },
        "adstock_params": {
            "adstock": { "TV": {"type": "geometric", "params": {"lambda": 0.5}} },
            "saturation": { "TV": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}} },
        },
        "output_params": { "aggregation_level": "daily" },
        "geo_params": {
            "total_population": 1000000,
            "count": 1
        }
    }

    sim = Simulate()
    result = sim.run_with_config(config)
    df = result.df

    # Filter where impressions > 0
    test_df = df[df["TV_impressions"] > 0]
    assert len(test_df) > 0
    
    # Frequency should never be below 1
    assert (test_df["TV_frequency"] >= 1.0).all()
    # Reach should never exceed impressions
    assert (test_df["TV_reach"] <= test_df["TV_impressions"]).all()
