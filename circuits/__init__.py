# Module:	__init__
# Date:		3rd October 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Circuits

...
"""

__name__ = "circuits"
__description__ = "Circuits"
__version__ = "1.0"
__author__ = "James Mills"
__author_email__ = "%s, prologic at shortcircuit dot net dot au" % __author__
__maintainer__ = __author__
__maintainer_email__ = __author_email__
__url__ = "http://trac.shortcircuit.net.au/circuits/"
__download_url__ = "http://shortcircuit.net.au/~prologic/downloads/software/%s-%s.tar.gz" % (__name__, __version__)
__copyright__ = "CopyRight (C) 2005-2008 by %s" % __author__
__license__ = "GPL"
__platforms__ = "POSIX"
__keywords__ = "Circuits"
__classifiers__ = [
		"Development Status :: 3 - Alpha",
		"Development Status :: 4 - Beta",
		"Development Status :: 5 - Production/Stable",
		"Environment :: Other Environment",
		"Intended Audience :: Developers",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: GNU General Public License (GPL)",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Adaptive Technologies",
		"Topic :: Communications :: Chat :: Internet Relay Chat",
		"Topic :: Database :: Front-Ends",
		"Topic :: Scientific/Engineering :: Artificial Intelligence",
		"Topic :: Software Development :: Libraries",
		"Topic :: Software Development :: Libraries :: Application Frameworks",
		"Topic :: Software Development :: Libraries :: Python Modules",
		]
__str__ = "%s-%s" % (__name__, __version__)

__package_data__ = {
		}

__install_requires__ = [
		]

__setup_requires__ = [
		]

__extras_require__ = {
		}

__entry_points__ = """
"""

from circuits.core import Manager, Component
from circuits.core import filter, listener, Event

manager = Manager()

__all__ = (
	"manager",
	"filter",
	"listener",
	"Event",
	"Manager",
	"Component")
