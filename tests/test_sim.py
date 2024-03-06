from pysimmmulator import load_parameters, simmm


def test_initiate_sim():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    simmm(my_basic_params)


def test_step1_baseline():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])


def test_step2_adspend():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])
    sim.simulate_ad_spend(**cfg["ad_spend_params"])


def test_step3_media():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])
    sim.simulate_ad_spend(**cfg["ad_spend_params"])
    sim.simulate_media(**cfg["media_params"])


def test_step4_cvr():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])
    sim.simulate_ad_spend(**cfg["ad_spend_params"])
    sim.simulate_media(**cfg["media_params"])
    sim.simulate_cvr(**cfg["cvr_params"])


def tests_step5_adstock():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])
    sim.simulate_ad_spend(**cfg["ad_spend_params"])
    sim.simulate_media(**cfg["media_params"])
    sim.simulate_cvr(**cfg["cvr_params"])
    sim.simulate_decay_returns(**cfg["adstock_params"])


def tests_step6_conversions():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])
    sim.simulate_ad_spend(**cfg["ad_spend_params"])
    sim.simulate_media(**cfg["media_params"])
    sim.simulate_cvr(**cfg["cvr_params"])
    sim.simulate_decay_returns(**cfg["adstock_params"])
    sim.calculate_conversions()


def tests_step7_consolidatedataframe():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])
    sim.simulate_ad_spend(**cfg["ad_spend_params"])
    sim.simulate_media(**cfg["media_params"])
    sim.simulate_cvr(**cfg["cvr_params"])
    sim.simulate_decay_returns(**cfg["adstock_params"])
    sim.calculate_conversions()
    sim.consolidate_dataframe()


def tests_step8_roi():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])
    sim.simulate_ad_spend(**cfg["ad_spend_params"])
    sim.simulate_media(**cfg["media_params"])
    sim.simulate_cvr(**cfg["cvr_params"])
    sim.simulate_decay_returns(**cfg["adstock_params"])
    sim.calculate_conversions()
    sim.consolidate_dataframe()
    sim.calculate_channel_roi()


def tests_step9_consolidatedataframe():
    cfg = load_parameters.load_config(config_path="./example_config.yaml")
    my_basic_params = load_parameters.define_basic_params(**cfg["basic_params"])
    sim = simmm(my_basic_params)
    sim.simulate_baseline(**cfg["baseline_params"])
    sim.simulate_ad_spend(**cfg["ad_spend_params"])
    sim.simulate_media(**cfg["media_params"])
    sim.simulate_cvr(**cfg["cvr_params"])
    sim.simulate_decay_returns(**cfg["adstock_params"])
    sim.calculate_conversions()
    sim.consolidate_dataframe()
    sim.finalize_output(**cfg["output_params"])


def test_run_with_config():
    cfg = load_parameters.load_config(config_path="example_config.yaml")
    sim = simmm()
    sim.run_with_config(config=cfg)


def test_run_with_config_weekly():
    cfg = load_parameters.load_config(config_path="example_config.yaml")
    cfg["output_params"]["aggregation_level"] = "weekly"
    sim = simmm()
    sim.run_with_config(config=cfg)


def test_run_with_high_frequency():
    cfg = load_parameters.load_config(config_path="example_config.yaml")
    cfg["basic_params"]["frequency_of_campaigns"] = 50
    sim = simmm()
    sim.run_with_config(config=cfg)
    assert sim.final_df.dropna().shape[0] > sim.final_df.shape[0] - 5
