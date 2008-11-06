#!/usr/bin/env python

from distutils.filelist import findall
from setuptools import setup, find_packages

import circuits as pkg

from circuits import version
version.forget_version()
version.remember_version()

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
		packages=find_packages(),
		install_requires=pkg.__install_requires__,
		setup_requires=pkg.__setup_requires__,
		extras_require=pkg.__extras_require__,
		entry_points=pkg.__entry_points__,
		package_data=pkg.__package_data__,
)
