#!/usr/bin/env python

from os import getcwd, path
from imp import new_module


from setuptools import setup, find_packages


version = new_module("version")

exec(
    compile(
        open(path.join(path.dirname(globals().get("__file__", path.join(getcwd(), "io"))), "iio/version.py"), "r").read(),
        "io/version.py", "exec"
    ),
    version.__dict__
)


setup(
    name="circuits.io",
    version=version.version,
    description="circuits.io components",
    long_description="circuits.io components",
    author="James Mills",
    author_email="James Mills, j dot mills at griffith dot edu dot au",
    url="http://circuitsframework.com/",
    download_url="http://bitbucket.org/circuits/circuits/downloads/",
    license="MIT",
    keywords="circuits io",
    platforms="POSIX",
    packages=find_packages("."),
    install_requires=[
        "circuits.core"
    ],
    zip_safe=True
)
