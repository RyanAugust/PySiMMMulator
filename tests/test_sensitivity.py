import pytest
import numpy as np
from pysimmmulator import load_config, Multisim

def test_multisim_sensitivity_variation():
    cfg = load_config("./examples/example_config.yaml")
    
    # Define ranges for error_std and one channel's lambda
    sensitivity_config = {
        "baseline_params": {
            "error_std": [10.0, 500.0]
        },
        "adstock_params": {
            "adstock": {
                "Amazon": {
                    "params": {
                        "lambda": [0.1, 0.9]
                    }
                }
            }
        }
    }
    
    msim = Multisim(random_seed=42)
    msim.run(config=cfg, runs=5, sensitivity_config=sensitivity_config)
    
    results = msim.get_data
    assert len(results) == 5
    
    # Verify that parameters actually varied
    error_stds = [r.config["baseline_params"]["error_std"] for r in results]
    lambdas = [r.config["adstock_params"]["adstock"]["Amazon"]["params"]["lambda"] for r in results]
    
    # Check uniqueness
    assert len(set(error_stds)) == 5
    assert len(set(lambdas)) == 5
    
    # Check bounds
    for val in error_stds:
        assert 10.0 <= val <= 500.0
    for val in lambdas:
        assert 0.1 <= val <= 0.9

def test_multisim_sensitivity_reproducibility():
    cfg = load_config("./examples/example_config.yaml")
    sensitivity_config = {
        "baseline_params": {
            "error_std": [50.0, 100.0]
        }
    }
    
    seed = 123
    msim1 = Multisim(random_seed=seed)
    msim1.run(cfg, runs=3, sensitivity_config=sensitivity_config)
    results1 = msim1.get_data
    
    msim2 = Multisim(random_seed=seed)
    msim2.run(cfg, runs=3, sensitivity_config=sensitivity_config)
    results2 = msim2.get_data
    
    for r1, r2 in zip(results1, results2):
        assert r1.config["baseline_params"]["error_std"] == r2.config["baseline_params"]["error_std"]
        np.testing.assert_array_equal(r1.df.values, r2.df.values)
