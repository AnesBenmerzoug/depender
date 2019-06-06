from setuptools import setup, find_packages
from pathlib import Path

install_requires = [
    "click>=4.0",
    "click-spinner>=0.1.0",
    "matplotlib>=3.0.0",
    "Jinja2>=2.9",
    "networkx[scipy]>=2.3",
    "numpy>=1.15.4",
]

HERE = Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="depender",
    version="0.1.1",
    description="A package that finds the external and internal dependencies in your Python project"
                "and draws a directed graph and/or matrix to represent them",
    long_description=README,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
    ],
    url="https://github.com/AnesBenmerzoug/depender",
    author="Anes Benmerzoug",
    author_email="anes.benmerzoug@gmail.com",
    install_requires=install_requires,
    include_package_data=True,
    packages=find_packages(exclude=["tests", "docs"]),
    entry_points={
        "console_scripts": ["depender=depender.cli:main"],
    }
)
