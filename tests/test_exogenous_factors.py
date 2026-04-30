from pysimmmulator.simulate import Simulate
from pysimmmulator.param_handlers import BasicParameters, BaselineParameters

def test_exogenous_multiplier():
    basic_params = BasicParameters(
        years=1,
        channels_impressions=["TV"],
        channels_clicks=[],
        frequency_of_campaigns=1,
        start_date="2023/01/01",
        true_cvr={"TV": 0.01},
        revenue_per_conv=10.0
    )
    sim = Simulate(basic_params)

    # Event on Jan 1st with 2.0 multiplier
    exogenous_factors = [
        {"name": "New Year", "dates": ["2023-01-01"], "impact": 2.0, "type": "multiplier"}
    ]

    params = BaselineParameters(
        basic_params=basic_params,
        base_p=100, trend_p=0, temp_var=0,
        temp_coef_mean=0, temp_coef_sd=0, error_std=0,
        exogenous_factors=exogenous_factors
    )

    df = sim.simulate_baseline(params)

    # Jan 1st should be exactly 200 (100 * 2.0)
    assert df.loc[df["date"] == "2023-01-01", "baseline_sales"].values[0] == 200.0
    # Other days should be exactly 100
    assert df.loc[df["date"] == "2023-01-02", "baseline_sales"].values[0] == 100.0

def test_exogenous_additive():
    basic_params = BasicParameters(
        years=1,
        channels_impressions=["TV"],
        channels_clicks=[],
        frequency_of_campaigns=1,
        start_date="2023/01/01",
        true_cvr={"TV": 0.01},
        revenue_per_conv=10.0
    )
    sim = Simulate(basic_params)

    # Additive impact of 500 on Jan 5th
    exogenous_factors = [
        {"name": "Promo", "dates": ["2023-01-05"], "impact": 500.0, "type": "additive"}
    ]

    params = BaselineParameters(
        basic_params=basic_params,
        base_p=100, trend_p=0, temp_var=0,
        temp_coef_mean=0, temp_coef_sd=0, error_std=0,
        exogenous_factors=exogenous_factors
    )

    df = sim.simulate_baseline(params)

    # Jan 5th should be 600 (100 + 500)
    assert df.loc[df["date"] == "2023-01-05", "baseline_sales"].values[0] == 600.0

def test_exogenous_range():
    basic_params = BasicParameters(
        years=1,
        channels_impressions=["TV"],
        channels_clicks=[],
        frequency_of_campaigns=1,
        start_date="2023/01/01",
        true_cvr={"TV": 0.01},
        revenue_per_conv=10.0
    )
    sim = Simulate(basic_params)

    # Multiplier of 0.5 for first week
    exogenous_factors = [
        {"name": "Lockdown", "start_date": "2023-01-01", "end_date": "2023-01-07", "impact": 0.5, "type": "multiplier"}
    ]

    params = BaselineParameters(
        basic_params=basic_params,
        base_p=100, trend_p=0, temp_var=0,
        temp_coef_mean=0, temp_coef_sd=0, error_std=0,
        exogenous_factors=exogenous_factors
    )

    df = sim.simulate_baseline(params)

    # Jan 1st to 7th should be 50
    assert (df.loc[(df["date"] >= "2023-01-01") & (df["date"] <= "2023-01-07"), "baseline_sales"] == 50.0).all()
    # Jan 8th should be 100
    assert df.loc[df["date"] == "2023-01-08", "baseline_sales"].values[0] == 100.0

def test_us_retail_example_run():
    from pysimmmulator.load_parameters import load_config, create_all_parameters
    cfg = load_config("examples/us_retail_exogenous_config.yaml")
    sim = Simulate()
    df, roi = sim.run_with_config(cfg)
    assert len(df) > 0
    assert "baseline_sales" not in df.columns # it's aggregated in total_revenue

    # We can check specific dates in the internal baseline if we run it manually
    params = create_all_parameters(cfg)
    b_df = sim.simulate_baseline(params["baseline_params"])

    # Black Friday 2023-11-24 multiplier was 3.5
    # Base is 1000, trend is growing.
    bf_row = b_df.loc[b_df["date"] == "2023-11-24"]
    assert bf_row["multiplier_impact"].values[0] == 3.5
