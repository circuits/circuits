# Module:   docs
# Date:     03rd April 2013
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""Documentation Tasks"""

from fabric.api import execute, lcd, local, task

from .utils import pip, requires, tobool


@task()
@requires("sphinx-apidoc")
def apidoc():
    """Generate API Documentation"""

    local("sphinx-apidoc -f -T -o docs/source/api circuits")


@task(default=True)
@requires("make", "sphinx-build")
def build(**options):
    """Generate the Sphinx documentation

    The following options are recognized:

    - ``clean``
      Perform a clean of the docs build
    - ``view``
      Open a web browser to display the built documentation
    """

    clean = tobool(options.get("clean", False))
    view = tobool(options.get("view", False))

    execute(apidoc)

    with lcd("docs"):
        pip(requirements="requirements.txt")
        local("make clean html") if clean else local("make html")

        if view:
            local("open build/html/index.html")
