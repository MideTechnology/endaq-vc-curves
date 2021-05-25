#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools


with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read().replace(".. :changelog:", "")

INSTALL_REQUIRES = [
    "numpy",
    "scipy",
    "idelib>=3.1.0",
]
TEST_REQUIRES = [
    "hypothesis",
    "pytest",
    "pytest-cov",
]


setuptools.setup(
    name="nre_utils",
    version="0.1.0",
    description="Reusable utilities for the NRE Python projects.",
    long_description=readme + "\n\n" + history,
    author="Becker Awqatty",
    author_email="bawqatty@mide.com",
    url="https://github.com/MideTechnology/nre_utils",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    test_suite="tests",
    tests_require=TEST_REQUIRES,
)
