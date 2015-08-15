"""Release Tasks"""


from __future__ import print_function

from os import getcwd


from fabric.api import abort, cd, hosts, prefix, prompt, run, task


from .utils import msg


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
