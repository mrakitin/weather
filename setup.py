#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='weather',
    version='0.1',
    description='Weather in console',
    author='Maksim Rakitin',
    url='https://github.com/mrakitin/web',
    packages=['weather'],
    install_requires=required,
    entry_points={
        "console_scripts": ['weather = weather.weather:weather_cli']
    },
)
