#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read()

setup(
    name='weather',
    version='0.1',
    description='Weather in console',
    author='Maksim Rakitin',
    url='https://github.com/mrakitin/web',
    packages=['weather'],
    install_requires=required,
)
