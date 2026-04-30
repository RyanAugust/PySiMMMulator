from pysimmmulator import load_parameters, Simulate
import pytest

@pytest.fixture
def config():
    return load_parameters.load_config(config_path="./examples/example_config.yaml")

@pytest.fixture
def params(config):
    return load_parameters.create_all_parameters(config)

def test_initiate_sim(params):
    Simulate(params["basic_params"])


def test_step1_baseline(params):
    sim = Simulate(params["basic_params"])
    sim.simulate_baseline(params["baseline_params"])


def test_step2_adspend(params):
    sim = Simulate(params["basic_params"])
    baseline_df = sim.simulate_baseline(params["baseline_params"])
    sim.simulate_ad_spend(baseline_sales_df=baseline_df, params=params["ad_spend_params"])


def test_step3_media(params):
    sim = Simulate(params["basic_params"])
    baseline_df = sim.simulate_baseline(params["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, params=params["ad_spend_params"])
    sim.simulate_media(spend_df=spend_df, params=params["media_params"])


def test_step4_cvr(params):
    sim = Simulate(params["basic_params"])
    baseline_df = sim.simulate_baseline(params["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, params=params["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, params=params["media_params"])
    sim.simulate_cvr(spend_df=spend_df, params=params["cvr_params"])


def tests_step5_adstock(params):
    sim = Simulate(params["basic_params"])
    baseline_df = sim.simulate_baseline(params["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, params=params["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, params=params["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, params=params["cvr_params"])
    sim.simulate_decay_returns(spend_df=spend_df, params=params["adstock_params"])


def tests_step6_conversions(params):
    sim = Simulate(params["basic_params"])
    baseline_df = sim.simulate_baseline(params["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, params=params["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, params=params["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, params=params["cvr_params"])
    mmm_df = sim.simulate_decay_returns(spend_df=spend_df, params=params["adstock_params"])
    sim.calculate_conversions(mmm_df=mmm_df)


def tests_step7_consolidatedataframe(params):
    sim = Simulate(params["basic_params"])
    baseline_df = sim.simulate_baseline(params["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, params=params["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, params=params["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, params=params["cvr_params"])
    mmm_df = sim.simulate_decay_returns(spend_df=spend_df, params=params["adstock_params"])
    mmm_df = sim.calculate_conversions(mmm_df=mmm_df)
    sim.consolidate_dataframe(mmm_df=mmm_df, baseline_sales_df=baseline_df)


def tests_step8_roi(params):
    sim = Simulate(params["basic_params"])
    baseline_df = sim.simulate_baseline(params["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, params=params["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, params=params["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, params=params["cvr_params"])
    mmm_df = sim.simulate_decay_returns(spend_df=spend_df, params=params["adstock_params"])
    mmm_df = sim.calculate_conversions(mmm_df=mmm_df)
    mmm_df = sim.consolidate_dataframe(mmm_df=mmm_df, baseline_sales_df=baseline_df)
    sim.calculate_channel_roi(mmm_df=mmm_df)


def tests_step9_consolidatedataframe(params):
    sim = Simulate(params["basic_params"])
    baseline_df = sim.simulate_baseline(params["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, params=params["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, params=params["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, params=params["cvr_params"])
    mmm_df = sim.simulate_decay_returns(spend_df=spend_df, params=params["adstock_params"])
    mmm_df = sim.calculate_conversions(mmm_df=mmm_df)
    mmm_df = sim.consolidate_dataframe(mmm_df=mmm_df, baseline_sales_df=baseline_df)
    sim.finalize_output(mmm_df=mmm_df, params=params["output_params"])


def test_run_with_config(config):
    sim = Simulate()
    sim.run_with_config(config=config)


def test_run_with_config_weekly(config):
    config["output_params"]["aggregation_level"] = "weekly"
    sim = Simulate()
    sim.run_with_config(config=config)


def test_run_with_high_frequency(params):
    config = load_parameters.load_config(config_path="./examples/example_config.yaml")
    config["basic_params"]["frequency_of_campaigns"] = 50
    sim = Simulate()
    result = sim.run_with_config(config=config)
    assert result.df.dropna().shape[0] > result.df.shape[0] - 5
