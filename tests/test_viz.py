import pysimmmulator as pysimmm
import pytest

@pytest.fixture
def config():
    return pysimmm.load_parameters.load_config(config_path="./example_config.yaml")

def test_viz_clicks_daily(config):
    sim = pysimmm.simmm()
    sim.run_with_config(config=config)
    sim.plot_clicks(agg='daily')

def test_viz_clicks_weekly(config):
    sim = pysimmm.simmm()
    sim.run_with_config(config=config)
    sim.plot_clicks(agg='weekly')

def test_viz_clicks_monthly(config):
    sim = pysimmm.simmm()
    sim.run_with_config(config=config)
    sim.plot_clicks(agg='monthly')

def test_viz_clicks_yearly(config):
    sim = pysimmm.simmm()
    sim.run_with_config(config=config)
    sim.plot_clicks(agg='yearly')

def test_viz_impressions_daily(config):
    sim = pysimmm.simmm()
    sim.run_with_config(config=config)
    sim.plot_impressions(agg='daily')

def test_viz_spend_daily(config):
    sim = pysimmm.simmm()
    sim.run_with_config(config=config)
    sim.plot_spend(agg='daily')
    
