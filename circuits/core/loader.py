"""
This module implements a generic Loader suitable for dynamically loading
components from other modules. This supports loading from local paths,
eggs and zip archives. Both setuptools and distribute are fully supported.
"""
import sys
from inspect import getmembers, getmodule, isclass

from .components import BaseComponent
from .handlers import handler
from .utils import safeimport


class Loader(BaseComponent):

    """Create a new Loader Component

    Creates a new Loader Component that enables dynamic loading of
    components from modules either in local paths, eggs or zip archives.
    """

    channel = "loader"

    def __init__(self, auto_register=True, init_args=None,
                 init_kwargs=None, paths=None, channel=channel):
        "initializes x; see x.__class__.__doc__ for signature"

        super(Loader, self).__init__(channel=channel)

        self._auto_register = auto_register
        self._init_args = init_args or tuple()
        self._init_kwargs = init_kwargs or dict()

        if paths:
            for path in paths:
                sys.path.insert(0, path)

    @handler("load")
    def load(self, name):
        module = safeimport(name)
        if module is not None:

            def test(x):
                return isclass(x) and issubclass(x, BaseComponent) and getmodule(x) is module
            components = [x[1] for x in getmembers(module, test)]

            if components:
                TheComponent = components[0]

                component = TheComponent(
                    *self._init_args,
                    **self._init_kwargs
                )

                if self._auto_register:
                    component.register(self)

                return component
