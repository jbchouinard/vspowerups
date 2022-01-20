from setuptools import setup, find_packages, Extension

setup(
    name="vspowerups",
    version="0.2.8.0",
    url="https://github.com/jbchouinard/vspowerups.git",
    author="Jerome Boisvert-Chouinard",
    author_email="github@jbchouinard.net",
    description="Power Ups optimizer for the Vampire Survivors game.",
    packages=find_packages(),
    setup_requires=["Cython"],
    install_requires=[],
    entry_points={"console_scripts": ["vspowerups = vspowerups.gui:main"]},
    ext_modules=[Extension("vspowerups.optimize", sources=["vspowerups/optimize.pyx"])],
)
