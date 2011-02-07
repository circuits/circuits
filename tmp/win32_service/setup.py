#!/usr/bin/env python

from distutils.core import setup

import py2exe

setup(
    name="test_service",
    console=["test_service.py"],
)
