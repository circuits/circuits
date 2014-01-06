#!/usr/bin/env python

from os import getcwd, path
from imp import new_module


from setuptools import setup, find_packages


version = new_module("version")

exec(
    compile(
        open(path.join(path.dirname(globals().get("__file__", path.join(getcwd(), "tools"))), "tools/version.py"), "r").read(),
        "tools/version.py", "exec"
    ),
    version.__dict__
)


setup(
    name="circuits.tools",
    version=version.version,
    description="circuits.tools components",
    long_description="circuits.tools components",
    author="James Mills",
    author_email="James Mills, j dot mills at griffith dot edu dot au",
    url="http://circuitsframework.com/",
    download_url="http://bitbucket.org/circuits/circuits/downloads/",
    license="MIT",
    keywords="circuits tools",
    platforms="POSIX",
    packages=find_packages("."),
    zip_safe=True
)
