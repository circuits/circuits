#!/usr/bin/env python
from setuptools import setup


def parse_requirements(filename):
    with open(filename, "r") as f:
        for line in f:
            if line and line[0] != "#":
                yield line.strip()


setup(
    name="wiki",
    version="dev",
    description="circuits wiki demo",
    scripts=(
        "wiki.py",
    ),
    install_requires=list(parse_requirements("requirements.txt")),
    zip_safe=True
)
