"""Utilities"""


import sys
from imp import find_module
from functools import wraps
from collections import deque
from itertools import count, izip
from contextlib import contextmanager


from fabric.api import abort, hide, local, puts, quiet, settings, warn


def tobool(s):
    if isinstance(s, bool):
        return s
    return s.lower() in ["yes", "y"]


def toint(s):
    if isinstance(s, int):
        return s
    return int(s)


@contextmanager
def msg(s):
    """Print message given as ``s`` in a context manager

    Prints "{s} ... OK"
    """

    puts("{0:s} ... ".format(s), end="", flush=True)
    with settings(hide("everything")):
        yield
    puts("OK", show_prefix=False, flush=True)


def pip(*args, **kwargs):
    requirements = kwargs.get("requirements", None)
    if requirements is not None:
        local("pip install -U -r {0:s}".format(kwargs["requirements"]))
    else:
        args = list(arg for arg in args if not has_module(arg))
        if args:
            local("pip install {0:s}".format(" ".join(args)))


def has_module(name):
    try:
        return find_module(name)
    except ImportError:
        return False


def has_binary(name):
    with quiet():
        return local("which {0:s}".format(name)).succeeded


def requires(*names, **kwargs):
    """Decorator/Wrapper that aborts if not all requirements are met.

    Aborts if not all requirements are met given a test function
    (defaulting to :func:`~has_binary`).

    :param kwargs: Optional kwargs. e.g: ``test=has_module``
    :type kwargs: dict

    :returns: None or aborts
    :rtype: None
    """

    test = kwargs.get("test", has_binary)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            if all(test(name) for name in names):
                return f(*args, **kwds)
            else:
                for name in names:
                    if not test(name):
                        warn("{0:s} not found".format(name))
                abort("requires({0:s}) failed".format(repr(names)))
        return wrapper
    return decorator


def ilen(seq):
    """Consume an iterable not reading it into memory; return the number of items.

    Borrowed from: https://github.com/Suor/funcy/blob/master/funcy/seqs.py
    """

    # NOTE: implementation borrowed from http://stackoverflow.com/a/15112059/753382
    counter = count()
    deque(izip(seq, counter), maxlen=0)  # (consume at C speed)
    return next(counter)


def progressbar(it, prefix="", size=60):
    """Simple Progress Bar

    Borrowed from: http://code.activestate.com/recipes/576986-progress-bar-for-console-programs-as-iterator/
    """

    count = ilen(it)

    def update(i):
        x = int(float(i) / float(count) * float(size))
        # x = int(ceil(float(size) * float(i) / float(count)))
        sys.stdout.write(
            "{0}: [{1}{2}] {3}/{4}\r".format(
                prefix, "#" * x, "." * (size - x), i, count
            )
        )
        sys.stdout.flush()

    update(0)
    for i, item in enumerate(it):
        yield item
        update(i + 1)

    sys.stdout.write("\n")
    sys.stdout.flush()
