import pysimmmulator as pysimmm
import pytest

@pytest.fixture
def cfg_sim() -> pysimmm.simmm:
    cfg = pysimmm.load_parameters.load_config(config_path="./example_config.yaml")
    sim = pysimmm.simmm()
    sim.run_with_config(config=cfg)
    return sim

def test_viz_clicks_daily(cfg_sim): cfg_sim.plot_clicks(agg='daily')

def test_viz_clicks_weekly(cfg_sim): cfg_sim.plot_clicks(agg='weekly')

def test_viz_clicks_monthly(cfg_sim): cfg_sim.plot_clicks(agg='monthly')

def test_viz_clicks_yearly(cfg_sim): cfg_sim.plot_clicks(agg='yearly')

def test_viz_impressions_daily(cfg_sim): cfg_sim.plot_impressions(agg='daily')

def test_viz_spend_daily(cfg_sim): cfg_sim.plot_spend(agg='daily')
    
