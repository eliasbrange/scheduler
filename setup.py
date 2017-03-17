#!/usr/bin/env python
from setuptools import setup, find_packages

VERSION = '0.0.1'

setup(
    name='scheduler',
    version=VERSION,
    include_package_data=True,

    packages=find_packages(),

    install_requires=[
        'click>=6.0.0,<7.0.0',
        'iso8601>=0.1.11,<1.0.0',
        'tinydb>=3.2.2,<4.0.0',
    ],

    entry_points={
        'console_scripts': [
            'scheduler = scheduler:cli'
        ]
    },
)
