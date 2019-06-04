from setuptools import setup, find_packages

install_requires = [
    "click>=4.0",
    "click-spinner>=0.1.0",
    "matplotlib>=3.0.0",
    "colorlover>=0.3",
    "Jinja2>=2.9",
    "networkx>=2.3",
    "numpy>=1.15.4",
]

setup(
    name="depender",
    author="Anes Benmerzoug",
    description="A package that finds the external and internal dependencies in your Python project" \
                "and draws a directed graph to represent them.",
    long_description="file: README.md",
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
    ],
    version="1.0",
    install_requires=install_requires,
    packages= find_packages(),
    entry_points={
        "console_scripts": ["depender=depender.cli:main"],
    }
)
