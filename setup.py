from setuptools import setup, find_packages, Extension

setup(
    name="vsoptimizer",
    version="0.2.8.2",
    url="https://github.com/jbchouinard/vspowerups.git",
    author="Jerome Boisvert-Chouinard",
    author_email="github@jbchouinard.net",
    description="Power Ups optimizer for the Vampire Survivors game.",
    packages=find_packages(),
    setup_requires=[],
    install_requires=[],
    entry_points={"console_scripts": ["vsoptimizer = vsoptimizer:main"]},
)
