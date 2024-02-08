from pysimmmulator import simmmulate, load_parameters

def test_initiate_sim():
    simmmulate.simulate(load_parameters.my_basic_params)

def test_step1_baseline():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.simulate_baseline(**load_parameters.cfg["baseline_params"])

def test_step2_adspend():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.simulate_baseline(**load_parameters.cfg["baseline_params"])
    sim.simulate_ad_spend(**load_parameters.cfg["ad_spend_params"])

def test_step3_media():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.simulate_baseline(**load_parameters.cfg["baseline_params"])
    sim.simulate_ad_spend(**load_parameters.cfg["ad_spend_params"])
    sim.simulate_media(**load_parameters.cfg["media_params"])

def test_step4_cvr():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.simulate_baseline(**load_parameters.cfg["baseline_params"])
    sim.simulate_ad_spend(**load_parameters.cfg["ad_spend_params"])
    sim.simulate_media(**load_parameters.cfg["media_params"])
    sim.simulate_cvr(**load_parameters.cfg["cvr_params"])

def tests_step5_adstock():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.simulate_baseline(**load_parameters.cfg["baseline_params"])
    sim.simulate_ad_spend(**load_parameters.cfg["ad_spend_params"])
    sim.simulate_media(**load_parameters.cfg["media_params"])
    sim.simulate_cvr(**load_parameters.cfg["cvr_params"])
    sim.simulate_decay_returns(**load_parameters.cfg["adstock_params"])

def tests_step6_conversions():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.simulate_baseline(**load_parameters.cfg["baseline_params"])
    sim.simulate_ad_spend(**load_parameters.cfg["ad_spend_params"])
    sim.simulate_media(**load_parameters.cfg["media_params"])
    sim.simulate_cvr(**load_parameters.cfg["cvr_params"])
    sim.simulate_decay_returns(**load_parameters.cfg["adstock_params"])
    sim.calculate_conversions()

def tests_step7_consolidatedataframe():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.simulate_baseline(**load_parameters.cfg["baseline_params"])
    sim.simulate_ad_spend(**load_parameters.cfg["ad_spend_params"])
    sim.simulate_media(**load_parameters.cfg["media_params"])
    sim.simulate_cvr(**load_parameters.cfg["cvr_params"])
    sim.simulate_decay_returns(**load_parameters.cfg["adstock_params"])
    sim.calculate_conversions()
    sim.consolidate_dataframe()

def test_run_with_config():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.run_with_config()