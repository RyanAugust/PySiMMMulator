import pysimmmulator as pysimmm
import pytest
import os

@pytest.fixture
def sim_output():
    cfg = pysimmm.load_parameters.load_config(config_path="./examples/example_config.yaml")
    sim = pysimmm.Simulate()
    result = sim.run_with_config(config=cfg)
    return sim, result.df

def test_viz_clicks_daily(sim_output):
    sim, df = sim_output
    sim.plot_clicks(df=df, agg='daily')
    assert os.path.exists("Clicks_by_channel.png")
    os.remove("Clicks_by_channel.png")

def test_viz_clicks_weekly(sim_output):
    sim, df = sim_output
    sim.plot_clicks(df=df, agg='weekly')
    assert os.path.exists("Clicks_by_channel.png")
    os.remove("Clicks_by_channel.png")

def test_viz_clicks_monthly(sim_output):
    sim, df = sim_output
    sim.plot_clicks(df=df, agg='monthly')
    assert os.path.exists("Clicks_by_channel.png")
    os.remove("Clicks_by_channel.png")

def test_viz_clicks_yearly(sim_output):
    sim, df = sim_output
    sim.plot_clicks(df=df, agg='yearly')
    assert os.path.exists("Clicks_by_channel.png")
    os.remove("Clicks_by_channel.png")

def test_viz_impressions_daily(sim_output):
    sim, df = sim_output
    sim.plot_impressions(df=df, agg='daily')
    assert os.path.exists("Impressions_by_channel.png")
    os.remove("Impressions_by_channel.png")

def test_viz_spend_daily(sim_output):
    sim, df = sim_output
    sim.plot_spend(df=df, agg='daily')
    assert os.path.exists("Spend_by_channel.png")
    os.remove("Spend_by_channel.png")
