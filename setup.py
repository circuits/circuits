#!/usr/bin/env python


try:
    from setuptools import setup, find_packages
    HAS_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    HAS_SETUPTOOLS = False

if not HAS_SETUPTOOLS:
    import os

    def is_package(path):
        return (
            os.path.isdir(path) and
            os.path.isfile(os.path.join(path, '__init__.py')
            ))

    def find_packages(path, base=""):
        """ Find all packages in path """
        packages = {}
        for item in os.listdir(path):
            dir = os.path.join(path, item)
            if is_package( dir ):
                if base:
                    module_name = "%(base)s.%(item)s" % vars()
                else:
                    module_name = item
                packages[module_name] = dir
                packages.update(find_packages(dir, module_name))
        return packages

from circuits import version
version.forget_version()
version.remember_version()

import circuits as pkg

setup(
		name=pkg.__name__,
		version=pkg.__version__,
		description=pkg.__description__,
		long_description=pkg.__doc__,
		author=pkg.__author__,
		author_email=pkg.__author_email__,
		maintainer=pkg.__maintainer__,
		maintainer_email=pkg.__maintainer_email__,
		url=pkg.__url__,
		download_url=pkg.__download_url__,
		classifiers=pkg.__classifiers__,
		license=pkg.__license__,
		keywords=pkg.__keywords__,
		platforms=pkg.__platforms__,
		packages=find_packages("."),
		install_requires=pkg.__install_requires__,
		setup_requires=pkg.__setup_requires__,
		extras_require=pkg.__extras_require__,
		entry_points=pkg.__entry_points__,
		package_data=pkg.__package_data__,
)
