from setuptools import setup

required = open("requirements.txt").read().split("\n")

setup(version="1.0",
      install_requires=required,
      entry_points={
        "console_scripts": ["depender=depender.main:main"],
      })
