# setup.py
from setuptools import setup, find_packages

# Read the README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="pyconfocal",                      # Package name
    version="0.1.0",                         # Start with 0.1.0
    author="Nathan Bérubé",
    author_email="nathan.berube.1@ulaval.ca",
    description="Python package for controlling a confocal microscope via Red Pitaya",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyconfocal",
    packages=find_packages(),                # Automatically finds pyconfocal and subpackages
    python_requires="==3.11.*",
    install_requires=requirements,           # Dependencies read from requirements.txt
)