import yaml
import pytest
import os
from pysimmmulator.simulate import Simulate

@pytest.fixture
def base_config():
    with open("examples/example_config.yaml", "r") as f:
        return yaml.safe_load(f)

def test_run_with_config_no_geo(base_config):
    sim = Simulate()
    result = sim.run_with_config(base_config)

    assert result.df.index.name == "date"
    assert "geo_name" not in result.df.index.names
    assert len(result.df) > 0

def test_run_with_config_with_geo(base_config):
    base_config["geo_params"] = {
        "total_population": 1000000,
        "count": 5,
        "universal_scale": 1.0
    }

    sim = Simulate()
    result = sim.run_with_config(base_config)

    assert "geo_name" in result.df.index.names
    assert "date" in result.df.index.names
    geos = result.df.index.get_level_values("geo_name").unique()
    assert len(geos) == 5

def test_run_with_config_weekly_geo(base_config):
    base_config["output_params"]["aggregation_level"] = "weekly"
    base_config["geo_params"] = {
        "total_population": 1000000,
        "count": 3,
    }

    sim = Simulate()
    result = sim.run_with_config(base_config)

    assert "geo_name" in result.df.index.names
    assert "week_start" in result.df.index.names
    geos = result.df.index.get_level_values("geo_name").unique()
    assert len(geos) == 3

def test_run_with_config_single_geo(base_config):
    base_config["geo_params"] = {
        "total_population": 1000000,
        "count": 1,
    }

    sim = Simulate()
    result = sim.run_with_config(base_config)

    assert "geo_name" in result.df.index.names
    assert "date" in result.df.index.names
    geos = result.df.index.get_level_values("geo_name").unique()
    assert len(geos) == 1

def test_geo_visualization(base_config):
    base_config["geo_params"] = {
        "total_population": 1000000,
        "count": 2,
    }

    sim = Simulate()
    result = sim.run_with_config(base_config)

    # Test plotting with multi-indexed geo data
    try:
        sim.plot_spend(result.df, agg="weekly")
        assert os.path.exists("Spend_by_channel.png")

        sim.plot_revenue(result.df, agg="monthly")
        assert os.path.exists("Revenue_by_channel.png")
    finally:
        # Cleanup
        for f in ["Spend_by_channel.png", "Revenue_by_channel.png"]:
            if os.path.exists(f):
                os.remove(f)
