import pytest
import pandas as pd
import numpy as np
from pysimmmulator.simulate import Simulate

def test_ctr_guard():
    config = {
        "basic_params": {
            "years": 1, "channels_impressions": ["TV", "Search"], "channels_clicks": ["Search"],
            "frequency_of_campaigns": 7, "start_date": "2023/01/01",
            "true_cvr": {"TV": 0.01, "Search": 0.01}, "revenue_per_conv": 100.0,
        },
        "baseline_params": {
            "base_p": 1000, "trend_p": 100, "temp_var": 10, "temp_coef_mean": 1.0, "temp_coef_sd": 0.1, "error_std": 50,
        },
        "ad_spend_params": {
            "campaign_spend_mean": 5000, "campaign_spend_std": 500,
            "max_min_proportion_on_each_channel": {"TV": {"min": 0.5, "max": 0.5}},
        },
        "media_params": {
            "true_cpm": {"TV": 1000.0}, # Very high CPM -> very few impressions
            "true_cpc": {"Search": 0.001}, # Very low CPC -> many clicks
            "noisy_cpm_cpc": {
                "TV": {"loc": 0.0, "scale": 0.1},
                "Search": {"loc": 0.0, "scale": 0.0001},
            },
        },
        "cvr_params": { "noisy_cvr": { "TV": {"loc": 1.0, "scale": 0.1}, "Search": {"loc": 1.0, "scale": 0.1} } },
        "adstock_params": {
            "adstock": { "TV": {"type": "geometric", "params": {"lambda": 0.5}}, "Search": {"type": "geometric", "params": {"lambda": 0.5}} },
            "saturation": { "TV": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}}, "Search": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}} },
        },
        "output_params": { "aggregation_level": "daily" }
    }

    sim = Simulate()
    result = sim.run_with_config(config)
    df = result.df

    # Search clicks should be capped by Search impressions (which we didn't specify but are calculated)
    # Actually, if Search is in channels_clicks, it might not have impressions if true_cpm is not provided.
    # Let's check Search impressions.
    assert (df["Search_clicks"] <= df["Search_impressions"]).all()

def test_reach_population_guard():
    config = {
        "basic_params": {
            "years": 1, "channels_impressions": ["TV"], "channels_clicks": [],
            "frequency_of_campaigns": 7, "start_date": "2023/01/01",
            "true_cvr": {"TV": 0.01}, "revenue_per_conv": 100.0,
        },
        "baseline_params": {
            "base_p": 1000, "trend_p": 100, "temp_var": 10, "temp_coef_mean": 1.0, "temp_coef_sd": 0.1, "error_std": 50,
        },
        "ad_spend_params": {
            "campaign_spend_mean": 500000, "campaign_spend_std": 50000,
            "max_min_proportion_on_each_channel": {},
        },
        "media_params": {
            "true_cpm": {"TV": 1.0}, # Low CPM -> many impressions
            "true_cpc": {},
            "noisy_cpm_cpc": {"TV": {"loc": 0.0, "scale": 0.1}},
            "true_reach_frequency": {
                "TV": {"reach": 2.0} # Target reach is 200% of population (logical impossible)
            }
        },
        "cvr_params": { "noisy_cvr": { "TV": {"loc": 1.0, "scale": 0.1} } },
        "adstock_params": {
            "adstock": { "TV": {"type": "geometric", "params": {"lambda": 0.5}} },
            "saturation": { "TV": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}} },
        },
        "output_params": { "aggregation_level": "daily" },
        "geo_params": {
            "total_population": 100000,
            "count": 1
        }
    }

    sim = Simulate()
    result = sim.run_with_config(config)
    df = result.df

    # Reach should not exceed total population
    # Summing across geos for each day
    daily_reach = df.groupby("date")["TV_reach"].sum()
    assert (daily_reach <= 100000).all()

def test_geo_reach_guard():
    config = {
        "basic_params": {
            "years": 1, "channels_impressions": ["TV"], "channels_clicks": [],
            "frequency_of_campaigns": 7, "start_date": "2023/01/01",
            "true_cvr": {"TV": 0.01}, "revenue_per_conv": 100.0,
        },
        "baseline_params": {
            "base_p": 1000, "trend_p": 100, "temp_var": 10, "temp_coef_mean": 1.0, "temp_coef_sd": 0.1, "error_std": 50,
        },
        "ad_spend_params": {
            "campaign_spend_mean": 500000, "campaign_spend_std": 50000,
            "max_min_proportion_on_each_channel": {},
        },
        "media_params": {
            "true_cpm": {"TV": 1.0},
            "true_cpc": {},
            "noisy_cpm_cpc": {"TV": {"loc": 0.0, "scale": 0.1}},
            "true_reach_frequency": {
                "TV": {"reach": 0.9} # 90% reach
            }
        },
        "cvr_params": { "noisy_cvr": { "TV": {"loc": 1.0, "scale": 0.1} } },
        "adstock_params": {
            "adstock": { "TV": {"type": "geometric", "params": {"lambda": 0.5}} },
            "saturation": { "TV": {"type": "scurve", "params": {"alpha": 1.0, "gamma": 0.5}} },
        },
        "output_params": { "aggregation_level": "daily" },
        "geo_params": {
            "total_population": 100000,
            "geo_specs": {
                "SmallGeo": {"loc": 0.01, "scale": 0.001} # Very small geo
            },
            "count": 2 # SmallGeo + one random
        }
    }

    sim = Simulate()
    result = sim.run_with_config(config)
    df = result.df # result.df has geo_name and date in index

    # For SmallGeo, reach should not exceed its population
    # Get population of SmallGeo
    from pysimmmulator.geos import Geos
    geos = Geos(total_population=100000)
    geo_details = geos(geo_specs=config["geo_params"]["geo_specs"], count=2)
    small_geo_pop = geo_details["SmallGeo"]

    small_geo_data = df.xs("SmallGeo", level="geo_name")
    assert (small_geo_data["TV_reach"] <= small_geo_pop).all()
