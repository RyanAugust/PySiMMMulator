import pandas as pd
import numpy as np
from pysimmmulator.simulate import Simulate

def test_geometric_adstock():
    vector = pd.Series([100, 0, 0, 0])
    lambda_ = 0.5
    adstocked = Simulate._geometric_adstock(vector, lambda_)
    expected = [100, 50, 25, 12.5]
    assert np.allclose(adstocked.values, expected)

def test_weibull_adstock_pdf():
    vector = pd.Series([100, 0, 0, 0, 0])
    # Weibull with shape > 1 should peak after day 0
    shape = 2.0
    scale = 2.0
    adstocked = Simulate._weibull_adstock(vector, shape, scale, adstock_type='pdf')
    # Peak should not be at index 0
    assert adstocked.values[1] > adstocked.values[0]
    assert len(adstocked) == len(vector)

def test_weibull_adstock_cdf():
    vector = pd.Series([100, 0, 0, 0, 0])
    shape = 2.0
    scale = 2.0
    adstocked = Simulate._weibull_adstock(vector, shape, scale, adstock_type='cdf')
    # Should decay from the peak at index 0
    assert adstocked.values[0] > adstocked.values[1]
    assert len(adstocked) == len(vector)

def test_scurve_saturation():
    vector = pd.Series([0, 10, 100, 1000])
    alpha = 2.0
    gamma = 0.5
    saturated = Simulate._scurve_saturation(vector, alpha, gamma)
    assert saturated[0] == 0
    assert saturated[3] < 1000 # Diminishing returns
    assert len(saturated) == len(vector)

def test_hill_saturation():
    vector = pd.Series([0, 10, 100, 1000])
    alpha = 2.0
    gamma = 100.0 # Absolute value
    saturated = Simulate._hill_saturation(vector, alpha, gamma)
    assert saturated[0] == 0
    assert saturated[3] < 1000
    # At vector=100, saturated should be 100 * (100**2 / (100**2 + 100**2)) = 100 * 0.5 = 50
    assert np.isclose(saturated[2], 50.0)

def test_modular_integration():
    # Mocking basic_params for the Simulate instance
    class MockParams:
        all_channels = ["Test"]
        channels_impressions = ["Test"]
        channels_clicks = []

    sim = Simulate()
    sim.basic_params = MockParams()

    mmm_df = pd.DataFrame({
        "Test_impressions": [100.0, 100.0, 100.0, 100.0]
    })

    adstock_config = {
        "Test": {
            "type": "geometric",
            "params": {"lambda": 0.5}
        }
    }

    saturation_config = {
        "Test": {
            "type": "hill",
            "params": {"alpha": 1.0, "gamma": 100.0}
        }
    }

    mmm_df = sim._simulate_decay(mmm_df, adstock_config)
    assert "Test_impressions_adstocked" in mmm_df.columns

    mmm_df = sim._simulate_diminishing_returns(mmm_df, saturation_config)
    assert "Test_impressions_adstocked_decay_diminishing" in mmm_df.columns
