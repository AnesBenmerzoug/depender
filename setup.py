from setuptools import setup

install_requires = [
    "click>=4.0",
    "click-spinner>=0.1.0",
    "bokeh>=1.0.0",
    "matplotlib>=3.0.0",
    "plotly>=3.8.0",
    "Jinja2>=2.9"
]

setup(version="1.0",
      install_requires=install_requires,
      entry_points={
        "console_scripts": ["depender=depender.cli:main"],
      })
