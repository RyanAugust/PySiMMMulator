import pandas as pd
import numpy as np
import yaml
from pysimmmulator import (
    Simulate, Geos, Study, BatchStudy, load_parameters
)
from pysimmmulator.param_handlers import BasicParameters, BaselineParameters

def test_basic_parameters_repr():
    params = BasicParameters(
        years=1,
        channels_impressions=["TV"],
        channels_clicks=["Search"],
        frequency_of_campaigns=1,
        start_date="2020/01/01",
        true_cvr={"TV": 0.01, "Search": 0.02},
        revenue_per_conv=10.0
    )
    repr_str = repr(params)
    assert "Years of Data to generate" in repr_str
    assert "TV" in repr_str
    assert "Search" in repr_str

def test_validate_config_invalid(tmp_path):
    # Test invalid basic_params
    invalid_cfg = {
        "basic_params": {"years": 0} # Invalid years
    }
    cfg_path = tmp_path / "invalid_config.yaml"
    with open(cfg_path, "w") as f:
        yaml.dump(invalid_cfg, f)

    assert not load_parameters.validate_config(str(cfg_path))

    # Test invalid baseline_params
    invalid_cfg = {
        "basic_params": {
            "years": 1,
            "channels_impressions": ["TV"],
            "channels_clicks": [],
            "frequency_of_campaigns": 1,
            "start_date": "2020/01/01",
            "true_cvr": {"TV": 0.01},
            "revenue_per_conv": 10.0
        },
        "baseline_params": {
            "base_p": 100,
            "error_std": 150 # error_std > base_p is invalid
        }
    }
    with open(cfg_path, "w") as f:
        yaml.dump(invalid_cfg, f)
    assert not load_parameters.validate_config(str(cfg_path))

import unittest.mock

def test_geos_zero_population():
    geo_maker = Geos(total_population=100)
    # Replace rng with a mock since its methods are read-only
    mock_rng = unittest.mock.MagicMock()
    mock_rng.normal.return_value = np.array([0.0])
    geo_maker.rng = mock_rng

    geo_specs = {"Geo1": {"loc": 0.0, "scale": 1.0}}
    geo_details = geo_maker.create_geos(geo_specs=geo_specs)
    assert geo_details["Geo1"] == 100

def test_simulate_report_random_state():
    sim = Simulate()
    state = sim._report_random_state()
    assert state is not None

def test_simulate_negative_baseline_sales():
    basic_params = BasicParameters(
        years=1,
        channels_impressions=["TV"],
        channels_clicks=[],
        frequency_of_campaigns=1,
        start_date="2020/01/01",
        true_cvr={"TV": 0.01},
        revenue_per_conv=10.0
    )
    sim = Simulate(basic_params)
    params = BaselineParameters(
        basic_params=basic_params,
        base_p=100, trend_p=0, temp_var=1000,
        temp_coef_mean=-1, temp_coef_sd=0, error_std=90
    )
    df = sim.simulate_baseline(params)
    assert (df["baseline_sales"] >= 0).all()
    assert (df["seasonality"].min() < -500)
def test_negative_check_warning(caplog):
    sim = Simulate()
    df = pd.DataFrame({"test_col": [-1, 2, 3]})
    sim._negative_check(df, "test_col", "ChannelA")
    assert "negative values for ChannelA" in caplog.text

def test_simulate_modular_types(caplog):
    sim = Simulate()
    sim.basic_params = type('obj', (object,), {'channels_impressions': ['TV'], 'all_channels': ['TV']})
    mmm_df = pd.DataFrame({"TV_impressions": [100, 100]})

    # Weibull adstock
    adstock_config = {"TV": {"type": "weibull", "params": {"shape": 2.0, "scale": 1.0}}}
    sim._simulate_decay(mmm_df, adstock_config)
    assert "TV_impressions_adstocked" in mmm_df.columns

    # Scurve saturation
    saturation_config = {"TV": {"type": "scurve", "params": {"alpha": 3.0, "gamma": 0.5}}}
    sim._simulate_diminishing_returns(mmm_df, saturation_config)
    assert "TV_impressions_adstocked_decay_diminishing" in mmm_df.columns

    # Unknown adstock type
    adstock_config = {"TV": {"type": "unknown", "params": {}}}
    sim._simulate_decay(mmm_df, adstock_config)
    assert "Unknown adstock type unknown" in caplog.text

    # Unknown saturation type
    mmm_df["TV_impressions_adstocked"] = [100, 100]
    saturation_config = {"TV": {"type": "unknown", "params": {}}}
    sim._simulate_diminishing_returns(mmm_df, saturation_config)
    assert "Unknown saturation type unknown" in caplog.text

def test_study_misc():
    s = Study(channel_name="test", true_roi=0.5)
    s.update_roi(0.6)
    assert s.roi == 0.6

    results = s.generate_dynamic(bias=[0.1, 0.2], stdev=[0.05, 0.05])
    assert len(results) == 2

def test_batch_study_dynamic():
    rois = {"A": 0.5, "B": 0.3}
    bs = BatchStudy(channel_rois=rois)

    # Universal dynamic
    res_univ = bs.generate_dynamic(universal_bias=[0.1, 0.2], universal_stdev=[0.05, 0.05])
    assert len(res_univ["A"]) == 2

    # Channel specific dynamic
    res_chan = bs.generate_dynamic(
        channel_bias={"A": [0.1], "B": [0.2]},
        channel_stdev={"A": [0.05], "B": [0.05]}
    )
    assert len(res_chan["A"]) == 1
    assert len(res_chan["B"]) == 1

def test_visualize_empty_columns():
    from pysimmmulator.visualize import Visualize
    v = Visualize()
    # Should return early without error
    assert v._plot_majors(pd.DataFrame(), []) is None

def test_multisim_get_data_coverage():
    from pysimmmulator.simulate import Multisim
    ms = Multisim()
    ms.results = "test_data"
    assert ms.get_data == "test_data"

def test_reproducibility():
    with open("examples/example_config.yaml", "r") as f:
        config = yaml.safe_load(f)

    config["geo_params"] = {
        "total_population": 1000000,
        "count": 5
    }

    seed = 42
    sim1 = Simulate(random_seed=seed)
    result1 = sim1.run_with_config(config)

    sim2 = Simulate(random_seed=seed)
    result2 = sim2.run_with_config(config)

    pd.testing.assert_frame_equal(result1.df, result2.df)
    assert result1.channel_roi == result2.channel_roi
