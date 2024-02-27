from setuptools import setup
import os

with open(os.path.join('src/pysimmm', 'VERSION')) as version_file:
    version = version_file.read().strip()

setup(
    version=version,
    entry_points = {
        'console_scripts': ['pysimmm=pysimmm.command_line:main'],
    }
)
