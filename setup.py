from pathlib import Path

from setuptools import find_packages, setup

install_requires = open("requirements.txt").read()


HERE = Path(__file__).parent

README = (HERE / "README.rst").read_text()

setup(
    name="depender",
    version="0.1.2",
    description="A package that finds the external and internal dependencies in your Python project"
    "and draws a directed graph and/or matrix to represent them",
    long_description=README,
    long_description_content_type="text/x-rst",
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
    ],
    url="https://github.com/AnesBenmerzoug/depender",
    author="Anes Benmerzoug",
    author_email="anes.benmerzoug@gmail.com",
    install_requires=install_requires,
    include_package_data=True,
    packages=find_packages(exclude=["tests", "docs"]),
    entry_points={"console_scripts": ["depender=depender.cli:main"]},
)
