<img align="left" src="PySiMMMulator_logo.png" alt="logo" width="150"/>

# PySiMMMulator

[![CodeFactor](https://www.codefactor.io/repository/github/ryanaugust/pysimmmulator/badge)](https://www.codefactor.io/repository/github/ryanaugust/pysimmmulator)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pysimmmulator.svg?label=PyPI%20downloads)](
https://pypi.org/project/pysimmmulator/)

PySiMMMulator is an open source Python adaption of the R-package [siMMMulator](https://github.com/facebookexperimental/siMMMulator), which allows users to generate simulated data to use in testing Marketing Mix Models (MMMs).
While this package cointains a full pipeline for data generation (configurable via .conf file) it can also be utilized in parts to generate select portions of MMM input data (ie campaign/channel spend)

## Installation

Accessable via PyPI

```bash
pip install pysimmmulator
```

## Usage

PySiMMMulator's simulator can either be run on a step-by-step basis, or can be run single-shot by passing a config file.

### Run via config

Run using this method, you'll be returned both a dataframe of for MMM input as well as the "True ROI" values for each of your channels. These true values are critical to validating your MMM model.

```python
cfg = load_config(config_path="./my_config.yaml")
sim = simmm()
mmm_input_df, channel_roi = sim.run_with_config(config=cfg)
```

### Run by stages

Alternatively you may run each of the stages independently, which allows for easier debugging and in-run adjustments based on the results of each stage. The order of the stages is reflected below **(without their inputs)**. Once you've run through every stage, results are available by calling the `sim.final_df` object (channel ROI results are stored as `sim.channel_roi`).

```python
sim = simmm()
sim.simulate_baseline()
sim.simulate_ad_spend()
sim.simulate_media()
sim.simulate_cvr()
sim.simulate_decay_returns()
sim.calculate_conversions()
sim.consolidate_dataframe()
sim.calculate_channel_roi()
sim.finalize_output()
```

### Run via CLI

A configuration file is required as input for this and should be passed as seen below. An output path can also be passed via `-o`, however when not passed the current working directory will be used.

```bash
pysimmm -i example_config.yaml -o .
```

## Development

Setting up a dev environment

```bash
conda create --prefix=./env python=3.11
conda activate ./env
pip install -e '.[dev]'
```
