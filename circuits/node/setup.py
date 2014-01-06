#!/usr/bin/env python

from os import getcwd, path
from imp import new_module


from setuptools import setup, find_packages


version = new_module("version")

exec(
    compile(
        open(path.join(path.dirname(globals().get("__file__", path.join(getcwd(), "node"))), "node/version.py"), "r").read(),
        "node/version.py", "exec"
    ),
    version.__dict__
)


setup(
    name="circuits.node",
    version=version.version,
    description="circuits.node components",
    long_description="circuits.node components",
    author="James Mills",
    author_email="James Mills, j dot mills at griffith dot edu dot au",
    url="http://circuitsframework.com/",
    download_url="http://bitbucket.org/circuits/circuits/downloads/",
    license="MIT",
    keywords="circuits node",
    platforms="POSIX",
    packages=find_packages("."),
    install_requires=[
        "circuits.core",
        "circuits.net",
    ],
    zip_safe=True
)
