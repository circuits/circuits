#!/bin/bash

curl -q -o - https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python
curl -q -o - https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python -
pip -q install -U mercurial
pip -q install -e hg+https://bitbucket.org/circuits/circuits-dev
