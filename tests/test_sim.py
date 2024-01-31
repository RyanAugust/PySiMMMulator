from pysimmmulator import simmmulate, load_parameters

def test_initiate_sim():
    simmmulate.simulate(load_parameters.my_basic_params)


def test_run_with_config():
    sim = simmmulate.simulate(load_parameters.my_basic_params)
    sim.run_with_config()