from setuptools import setup, find_packages

setup(
    name="ion-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ION-cli=ion_cli.cli:main",
        ],
    },
    author="Chris Egersdoerfer",
    author_email="cegersdo@udel.edu",
    description="A command line utility for interacting with the I/O Navigator",
    keywords="ion, cli, command line, utility",
    url="https://github.com/cegersdoerfer/ion-cli",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
) 