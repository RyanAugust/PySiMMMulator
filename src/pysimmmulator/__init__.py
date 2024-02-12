__title__ = "CheetahPy"
__author__ = "RyanAugust"
__license__ = "MIT"
__copyright__ = "Copyright 2024"

import os

with open(os.path.join("src/pysimmmulator", "VERSION")) as version_file:
    __version__ = version_file.read().strip()

from .simulate import simmmulate
from .load_parameters import load_config, define_basic_params