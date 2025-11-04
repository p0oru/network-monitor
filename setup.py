"""
Setup script for NetScope.
"""
from setuptools import setup, find_packages

setup(
    name="netscope",
    version="1.0.0",
    description="Professional network and system monitoring application",
    packages=find_packages(),
    install_requires=[
        "PyQt5==5.15.10",
        "psutil==5.9.8",
        "speedtest-cli==2.1.3",
        "requests==2.31.0",
        "matplotlib==3.8.2",
    ],
    entry_points={
        "console_scripts": [
            "netscope=netscope.main:main",
        ],
    },
)
