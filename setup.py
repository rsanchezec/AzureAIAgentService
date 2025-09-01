from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Azure AI Agent Service",
    version="0.1",
    author="rsanchez",
    packages=find_packages(),
    install_requires = requirements,
)