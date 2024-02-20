from pysimmmulator import load_config, simmmulate
import pandas as pd
import argparse


def run_with_config(config_path):
    """Initiates `simmmulator` and executes `simmmmulator.run_with_config` against the passed config filepath

    Args:
        config_path (str): path to a valid config file, see example_config.yaml as example of `simmmulator` expected config format
    """
    cfg = load_config(config_path)
    sim = simmmulate()
    (mmm_input_df, channel_roi) = sim.run_with_config(config=cfg)

    # save to current directory. Should be an optional argument for this
    mmm_input_df.to_csv("mmm_input_df.csv", index=False)
    pd.DataFrame.from_dict(channel_roi, orient="index", columns=["true_roi"]).to_csv("channel_roi.csv")


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-c", "--config_path", action="store", help="Provides configuration file path for simulation"
    )
    arg_parser.add_argument(
        "-o", "--output_path", action="store", help="Provides output destination", default="."
    )
    args = arg_parser.parse_args()
    run_with_config(config_path=args.config_path)
