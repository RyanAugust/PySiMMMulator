import pysimmmulator as pysimmm

def test_viz_clicks_daily():
    cfg = pysimmm.load_parameters.load_config(config_path="example_config.yaml")
    sim = pysimmm.simmm()
    sim.run_with_config(config=cfg)
    sim.plot_clicks(agg='daily')

def test_viz_clicks_weekly():
    cfg = pysimmm.load_parameters.load_config(config_path="example_config.yaml")
    sim = pysimmm.simmm()
    sim.run_with_config(config=cfg)
    sim.plot_clicks(agg='weekly')

def test_viz_clicks_monthly():
    cfg = pysimmm.load_parameters.load_config(config_path="example_config.yaml")
    sim = pysimmm.simmm()
    sim.run_with_config(config=cfg)
    sim.plot_clicks(agg='monthly')

def test_viz_clicks_yearly():
    cfg = pysimmm.load_parameters.load_config(config_path="example_config.yaml")
    sim = pysimmm.simmm()
    sim.run_with_config(config=cfg)
    sim.plot_clicks(agg='yearly')

def test_viz_impressions_daily():
    cfg = pysimmm.load_parameters.load_config(config_path="example_config.yaml")
    sim = pysimmm.simmm()
    sim.run_with_config(config=cfg)
    sim.plot_impressions(agg='daily')

def test_viz_spend_daily():
    cfg = pysimmm.load_parameters.load_config(config_path="example_config.yaml")
    sim = pysimmm.simmm()
    sim.run_with_config(config=cfg)
    sim.plot_spend(agg='daily')
    
