# Module:	__init__
# Date:		3rd October 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Circuits

Circuits is an event-driven framework with a focus on Component Software
Architectures. Circuits is based arounds two core concepts:
	* Everything is a Component
	* Everything is an Event

Circuits has a clean architecture and has no external dependancies on any
other library. It's simplistic design is unmatchable but yet deliversa
powerful framework for building large, scalable, maintainable applications
and systems. Circuits was a core integral part of the pymills library
developed in 2006 and was partly inspired by the Trac architecture.

Simple Example:

>>> from circuits.core import listener, Component, Event, Manager

>>> class Hello(Component):
...	@listener("hello")
...	def onHELLO(self):
...		print "Hello World!"
>>> manager = Manager()
>>> manager += hello
>>> manager.push(Event(), "hello")
>>> manager.flush()
Hello World!
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

from core import *
from timers import *
from bridge import *
from workers import *
from debugger import *
