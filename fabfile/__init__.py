"""Development Task"""


from __future__ import print_function

from os import getcwd

import docker  # noqa
import docs  # noqa
import help  # noqa
from fabric.api import (
    abort, cd, execute, hide, hosts, local, prefix, prompt, run, settings,
    task,
)

from .utils import msg, pip, requires, tobool


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


@task()
@hosts("localhost")
def release():
    """Performs a full release"""

    with cd(getcwd()):
        with msg("Creating env"):
            run("mkvirtualenv test")

        with msg("Building"):
            with prefix("workon test"):
                run("fab develop")

        with msg("Running tests"):
            with prefix("workon test"):
                run("fab test")

        with msg("Building docs"):
            with prefix("workon test"):
                run("pip install -r docs/requirements.txt")
                run("fab docs")

        version = run("python setup.py --version")
        if "dev" in version:
            abort("Detected Development Version!")

        print("Release version: {0:s}".format(version))

        if prompt("Is this ok?", default="Y", validate=r"^[YyNn]?$") in "yY":
            run("git tag {0:s}".format(version))
            run("python setup.py egg_info sdist bdist_egg bdist_wheel register upload")
            run("python setup.py build_sphinx upload_sphinx")

        with msg("Destroying env"):
            run("rmvirtualenv test")
