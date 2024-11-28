from pysimmmulator import load_parameters, simmm
import pytest

@pytest.fixture
def config():
    return load_parameters.load_config(config_path="./example_config.yaml")

def test_initiate_sim(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    simmm(my_basic_params)


def test_step1_baseline(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])


def test_step2_adspend(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(**config["ad_spend_params"])


def test_step3_media(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(**config["ad_spend_params"])
    sim.simulate_media(**config["media_params"])


def test_step4_cvr(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(**config["ad_spend_params"])
    sim.simulate_media(**config["media_params"])
    sim.simulate_cvr(**config["cvr_params"])


def tests_step5_adstock(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(**config["ad_spend_params"])
    sim.simulate_media(**config["media_params"])
    sim.simulate_cvr(**config["cvr_params"])
    sim.simulate_decay_returns(**config["adstock_params"])


def tests_step6_conversions(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(**config["ad_spend_params"])
    sim.simulate_media(**config["media_params"])
    sim.simulate_cvr(**config["cvr_params"])
    sim.simulate_decay_returns(**config["adstock_params"])
    sim.calculate_conversions()


def tests_step7_consolidatedataframe(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(**config["ad_spend_params"])
    sim.simulate_media(**config["media_params"])
    sim.simulate_cvr(**config["cvr_params"])
    sim.simulate_decay_returns(**config["adstock_params"])
    sim.calculate_conversions()
    sim.consolidate_dataframe()


def tests_step8_roi(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(**config["ad_spend_params"])
    sim.simulate_media(**config["media_params"])
    sim.simulate_cvr(**config["cvr_params"])
    sim.simulate_decay_returns(**config["adstock_params"])
    sim.calculate_conversions()
    sim.consolidate_dataframe()
    sim.calculate_channel_roi()


def tests_step9_consolidatedataframe(config):
    my_basic_params = load_parameters.define_basic_params(**config["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**config["baseline_params"])
    sim.simulate_ad_spend(**config["ad_spend_params"])
    sim.simulate_media(**config["media_params"])
    sim.simulate_cvr(**config["cvr_params"])
    sim.simulate_decay_returns(**config["adstock_params"])
    sim.calculate_conversions()
    sim.consolidate_dataframe()
    sim.finalize_output(**config["output_params"])


def test_run_with_config(config):
    config = load_parameters.load_config(config_path="example_config.yaml")
    sim = simmm()
    sim.run_with_config(config=config)


def test_run_with_config_weekly(config):
    config["output_params"]["aggregation_level"] = "weekly"
    sim = simmm()
    sim.run_with_config(config=config)


def test_run_with_high_frequency(config):
    config["basic_params"]["frequency_of_campaigns"] = 50
    sim = simmm()
    sim.run_with_config(config=config)
    assert sim.final_df.dropna().shape[0] > sim.final_df.shape[0] - 5
