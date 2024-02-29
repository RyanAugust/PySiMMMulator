__title__ = "PySiMMM"
__author__ = "RyanAugust"
__license__ = "MIT"
__copyright__ = "Copyright 2024"

import os

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
    __version__ = version_file.read().strip()


from .simulate import simmm, multisimmm
from .load_parameters import load_config, define_basic_params
