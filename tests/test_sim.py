from pysimmmulator import load_parameters, Simulate
import pytest

@pytest.fixture
def config():
    return load_parameters.load_config(config_path="./examples/example_config.yaml")

def test_initiate_sim(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    Simulate(my_basic_params)


def test_step1_baseline(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])


def test_step2_adspend(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    baseline_df = sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(baseline_sales_df=baseline_df, **config["ad_spend_params"])


def test_step3_media(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    baseline_df = sim.simulate_baseline(**config["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, **config["ad_spend_params"])
    sim.simulate_media(spend_df=spend_df, **config["media_params"])


def test_step4_cvr(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    baseline_df = sim.simulate_baseline(**config["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, **config["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, **config["media_params"])
    sim.simulate_cvr(spend_df=spend_df, **config["cvr_params"])


def tests_step5_adstock(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    baseline_df = sim.simulate_baseline(**config["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, **config["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, **config["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, **config["cvr_params"])
    sim.simulate_decay_returns(spend_df=spend_df, **config["adstock_params"])


def tests_step6_conversions(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    baseline_df = sim.simulate_baseline(**config["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, **config["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, **config["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, **config["cvr_params"])
    mmm_df = sim.simulate_decay_returns(spend_df=spend_df, **config["adstock_params"])
    sim.calculate_conversions(mmm_df=mmm_df)


def tests_step7_consolidatedataframe(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    baseline_df = sim.simulate_baseline(**config["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, **config["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, **config["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, **config["cvr_params"])
    mmm_df = sim.simulate_decay_returns(spend_df=spend_df, **config["adstock_params"])
    mmm_df = sim.calculate_conversions(mmm_df=mmm_df)
    sim.consolidate_dataframe(mmm_df=mmm_df, baseline_sales_df=baseline_df)


def tests_step8_roi(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    baseline_df = sim.simulate_baseline(**config["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, **config["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, **config["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, **config["cvr_params"])
    mmm_df = sim.simulate_decay_returns(spend_df=spend_df, **config["adstock_params"])
    mmm_df = sim.calculate_conversions(mmm_df=mmm_df)
    mmm_df = sim.consolidate_dataframe(mmm_df=mmm_df, baseline_sales_df=baseline_df)
    sim.calculate_channel_roi(mmm_df=mmm_df)


def tests_step9_consolidatedataframe(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = Simulate(my_basic_params)
    baseline_df = sim.simulate_baseline(**config["baseline_params"])
    spend_df = sim.simulate_ad_spend(baseline_sales_df=baseline_df, **config["ad_spend_params"])
    spend_df = sim.simulate_media(spend_df=spend_df, **config["media_params"])
    spend_df = sim.simulate_cvr(spend_df=spend_df, **config["cvr_params"])
    mmm_df = sim.simulate_decay_returns(spend_df=spend_df, **config["adstock_params"])
    mmm_df = sim.calculate_conversions(mmm_df=mmm_df)
    mmm_df = sim.consolidate_dataframe(mmm_df=mmm_df, baseline_sales_df=baseline_df)
    sim.finalize_output(mmm_df=mmm_df, **config["output_params"])


def test_run_with_config(config):
    config = load_parameters.load_config(config_path="./examples/example_config.yaml")
    sim = Simulate()
    sim.run_with_config(config=config)


def test_run_with_config_weekly(config):
    config["output_params"]["aggregation_level"] = "weekly"
    sim = Simulate()
    sim.run_with_config(config=config)


def test_run_with_high_frequency(config):
    config["basic_params"]["frequency_of_campaigns"] = 50
    sim = Simulate()
    final_df, _ = sim.run_with_config(config=config)
    assert final_df.dropna().shape[0] > final_df.shape[0] - 5
