"""Utilities"""

from contextlib import contextmanager
from functools import wraps
from imp import find_module

from fabric.api import abort, hide, local, puts, quiet, settings, warn


def tobool(s):
    if isinstance(s, bool):
        return s
    return s.lower() in ['yes', 'y']


def toint(s):
    if isinstance(s, int):
        return s
    return int(s)


@contextmanager
def msg(s):
    """
    Print message given as ``s`` in a context manager

    Prints "{s} ... OK"
    """
    puts(f'{s:s} ... ', end='', flush=True)
    with settings(hide('everything')):
        yield
    puts('OK', show_prefix=False, flush=True)


def pip(*args, **kwargs):
    requirements = kwargs.get('requirements', None)
    if requirements is not None:
        local('pip install -U -r {:s}'.format(kwargs['requirements']))
    else:
        args = [arg for arg in args if not has_module(arg)]
        if args:
            local('pip install {:s}'.format(' '.join(args)))


def has_module(name):
    try:
        return find_module(name)
    except ImportError:
        return False


def has_binary(name):
    with quiet():
        return local(f'which {name:s}').succeeded


def requires(*names, **kwargs):
    """
    Decorator/Wrapper that aborts if not all requirements are met.

    Aborts if not all requirements are met given a test function
    (defaulting to :func:`~has_binary`).

    :param kwargs: Optional kwargs. e.g: ``test=has_module``
    :type kwargs: dict

    :returns: None or aborts
    :rtype: None
    """
    test = kwargs.get('test', has_binary)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            if all(test(name) for name in names):
                return f(*args, **kwds)
            for name in names:
                if not test(name):
                    warn(f'{name:s} not found')
            abort(f'requires({names!r:s}) failed')
            return None

        return wrapper

    return decorator
