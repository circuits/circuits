# Module:   test_version
# Date:     17th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Version Tests"""

import os
import sys
import unittest
from os import path
from os.path import abspath, dirname
from subprocess import Popen, call, PIPE

def test():
    root = abspath("%s/../" % dirname(abspath(__file__)))

    if "circuits.__version__" in sys.modules:
        del sys.modules["circuits.__version__"]

    if path.exists(path.join(root, "__version__.py")):
        os.remove(path.join(root, "__version__.py"))
    if path.exists(path.join(root, "__version__.pyc")):
        os.remove(path.join(root, "__version__.pyc"))

    import circuits
    reload(circuits)

    assert circuits.__version__ == "unknown"

    from circuits import version
    version.forget_version()
    version.remember_version()

    try:
        import mercurial
    except ImportError:
        return

    cwd = os.getcwd()
    if not cwd == root:
        os.chdir(root)

    if path.exists(path.join(root, ".hg")):
        call("python setup.py build &> /dev/null", shell=True)

        reload(circuits)

        p = Popen(["hg id -i"], stdout=PIPE, shell=True)
        id = p.communicate()[0].rstrip("\n+")

        assert circuits.__version__ == id

    os.chdir(cwd)
