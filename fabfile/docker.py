"""Docker Tasks"""


from fabric.api import local, task

from .utils import msg, requires, tobool

TAG = "prologic/circuits"


@task(default=True)
@requires("docker")
def build(**options):
    """Build Docker Image

    Options can be provided to customize the build.
    The following options are supported:

    - rebuild -> Whether to rebuild without a cache.
    - version -> Specific version to tag the image with (Default: latest)
    """

    rebuild = tobool(options.get("rebuild", False))
    version = options.get("version", "latest")

    tag = "{0:s}:{1:s}".format(TAG, version)
    args = ["docker", "build", "-t", tag, "."]

    if rebuild:
        args.insert(-1, "--no-cache")

    with msg("Building Image"):
        local(" ".join(args))


@task()
@requires("docker")
def publish():
    """Publish Docker Image"""

    args = ["docker", "push", TAG]

    with msg("Pushing Image"):
        local(" ".join(args))


@task()
@requires("docker")
def run():
    """Run Docker Container"""

    args = ["docker", "run", "-i", "-t", "--rm", TAG]

    local(" ".join(args))
