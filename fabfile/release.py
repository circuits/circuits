"""Release Tasks"""


from __future__ import print_function

import re
from os import getcwd
from time import sleep
from operator import itemgetter


from requests import get
from fabric.api import abort, cd, hosts, local, prefix, prompt, run, task


from .utils import msg, progressbar


ISSUE_RE = re.compile("^.*([#][0-9]+).*$")


@task()
def changelog():
    """Update the ChangeLog"""

    tag = local("git describe --abbrev=0 --tags", capture=True).strip()
    log = local("git log --oneline {0}..HEAD".format(tag), capture=True).strip().split("\n")

    baseurl = "https://api.github.com/repos"
    owner, project = "circuits", "circuits"

    issues = []
    metadata = {}

    for entry in progressbar(log, "Collecting Issues"):
        sha, msg = entry.split(" ", 1)
        match = ISSUE_RE.match(msg)
        number = match and match.group(1)[1:] or None
        if number and number not in issues:
            issues.append(number)

            try:
                response = get("{0}/{1}/{2}/issues/{3}".format(baseurl, owner, project, number))
                response.raise_for_status()
                metadata[number] = response.json()
            except Exception as error:
                print("Warning: Ignore issue #{0} because of error {1}".format(number, error))
            finally:
                # So we don't break the Github API rate limit :)
                sleep(1)

    print("Latest Tag: {0}".format(tag))
    print("Issues: {0}".format(", ".join(issues)))

    for issue in issues:
        labels = map(itemgetter("name"), metadata["labels"])
        if "bug" in labels:
            type = "bug"
        elif "enhancement" in labels:
            type = "feature"
        else:
            type = "support"

        title = metadata[issue]["title"]

        print("- :{1}:`{2}` {3}".format(type, issue, title))


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
