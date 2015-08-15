"""Development Task"""


from __future__ import print_function


from fabric.api import execute, hide, local, settings, task


import help  # noqa
import docs  # noqa
import docker  # noqa
import release  # noqa

from .utils import pip, requires, tobool


@task()
@requires("pip")
def build(**options):
    """Build and install required dependencies

    Options can be provided to customize the build.
    The following options are supported:

    - dev -> Whether to install in development mode (Default: Fase)
    """

    dev = tobool(options.get("dev", False))

    if dev:
        pip(requirements="requirements-dev.txt")

    with settings(hide("stdout", "stderr"), warn_only=True):
        local("python setup.py {0:s}".format("develop" if dev else "install"))


@task()
def clean():
    """Clean up build files and directories"""

    files = ["build", ".coverage", "coverage", "dist", "docs/build"]

    local("rm -rf {0:s}".format(" ".join(files)))

    local("find . -type f -name '*~' -delete")
    local("find . -type f -name '*.pyo' -delete")
    local("find . -type f -name '*.pyc' -delete")
    local("find . -type d -name '__pycache__' -delete")
    local("find . -type d -name '*egg-info' -exec rm -rf {} +")


@task()
def develop():
    """Build and Install in Development Mode"""

    return execute(build, dev=True)


@task()
@requires("py.test")
def test():
    """Run all unit tests and doctests."""

    local("python setup.py test")
