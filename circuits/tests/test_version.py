# Module:   test_version
# Date:     17th March 2009
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""Version Test Suite"""

import os
import sys
import unittest
from os import path
from os.path import abspath, dirname
from subprocess import Popen, call, PIPE

class TestVersion(unittest.TestCase):
    """Test Version

    Test the version of circuits that is generated.
    """

    def runTest(self):
        root = abspath("%s/../" % dirname(abspath(__file__)))

        if "circuits.__version__" in sys.modules:
            del sys.modules["circuits.__version__"]

        if path.exists(path.join(root, "__version__.py")):
            os.remove(path.join(root, "__version__.py"))
        if path.exists(path.join(root, "__version__.pyc")):
            os.remove(path.join(root, "__version__.pyc"))

        import circuits
        reload(circuits)

        self.assertEquals(circuits.__version__, "unknown")

        from circuits import version
        version.forget_version()
        version.remember_version()

        try:
            import mercurial
        except ImportError:
            return

        root = abspath("%s/../" % root)

        cwd = os.getcwd()
        os.chdir(root)

        if path.exists(path.join(root, ".hg")):
            call("python setup.py build &> /dev/null", shell=True)

            reload(circuits)

            p = Popen(["hg id -i"], stdout=PIPE, shell=True)
            id = p.communicate()[0].rstrip("\n+")

            self.assertEquals(circuits.__version__, id)

        os.chdir(cwd)

if __name__ == "__main__":
    unittest.main()
