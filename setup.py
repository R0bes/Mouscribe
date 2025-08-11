#!/usr/bin/env python3
"""
Setup script for Mauscribe
"""

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]


setup(
    name="mauscribe",
    version="1.0.0",
    description="Voice-to-Text Tool mit Push-to-Talk",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "mauscribe=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
