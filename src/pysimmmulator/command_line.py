from pysimmmulator import load_config, simmmulate
import pandas as pd
import sys

def run_with_config(config_path):
    """Initiates `simmmulator` and executes `simmmmulator.run_with_config` against the passed config filepath
    
    Args:
        config_path (str): path to a valid config file, see example_config.yaml as example of `simmmulator` expected config format"""
    cfg = load_config(config_path)
    sim = simmmulate()
    (mmm_input_df, channel_roi) = sim.run_with_config(config=cfg)

    # save to current directory. Should be an optional argument for this    
    mmm_input_df.to_csv('mmm_input_df.csv', index=False)
    pd.DataFrame.from_dict(channel_roi, orient='index',columns=['true_roi']).to_csv('mmm_input_df.csv')


def main():
    # parse args
    args = sys.argv
    config_path = args.config_path
    run_with_config(config_path=config_path)