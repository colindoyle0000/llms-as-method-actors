"""Setup file for Connections Solver.

This Python project is a package for using large language models to solve Connections puzzles.

The project is currently in the early stages of development. Comments and feedback are welcome. 
Email: Colin.Doyle@lls.edu
"""
from setuptools import setup, find_packages

setup(
    name="connections",
    version="0.1",
    author="Colin Doyle",
    author_email="Colin.Doyle@LLS.edu",
    description="A package for for using large language models to solve Connections puzzles.",
    url="https://www.colin-doyle.net/",
    packages=find_packages(),
    package_data={
        'connections': ['data/*.txt'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'need to fill out',
        # Other dependencies
    ],
)
