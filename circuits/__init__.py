# Module:	__init__
# Date:		3rd October 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Event framework with a Component architecture

circuits is an event-driven framework with a focus on Component Software
Architectures where System Functionality is defined in Components.
Components communicate with one another by propagating events throughout
the system. Each Component can react to events and expose events to other
parts of the system Components are able to manage their own events and
can also be linked to other Components.

circuits has a clean architecture and has no external dependencies on any
other library. It's simplistic design is unmatchable but yet delivers a
powerful framework for building large, scalable, maintainable applications
and systems. circuits was a core integral part of the
[http://trac.softcircuit.com.au/pymills pymills] library developed in 2006
and was partly inspired by the [http://trac.edgewall.org Trac] architecture.

Simple Example:

>>> from circuits.core import listener, Component, Event, Manager
>>>
>>> class Hello(Component):
...   @listener("hello")
...   def onHELLO(self):
...      print "Hello World!"
>>> manager = Manager()
>>> manager += Hello()
>>> manager.push(Event(), "hello")
>>> manager.flush()
Hello World!
"""

try:
	from __version__ import version as __version__
except ImportError:
	__version__ = "unknown"

__name__ = "circuits"
__description__ = "Event framework with a Component architecture"
__author__ = "James Mills"
__author_email__ = "%s, prologic at shortcircuit dot net dot au" % __author__
__maintainer__ = __author__
__maintainer_email__ = __author_email__
__url__ = "http://trac.shortcircuit.net.au/circuits/"
__download_url__ = "http://trac.softcircuit.com.au/circuits/downloads/%s-%s.tar.gz" % (__name__, __version__)
__copyright__ = "Copyright (C) 2004-2008 by %s" % __author__
__license__ = "MIT"
__platforms__ = "POSIX"
__keywords__ = "circuits event library framework component architecture"
__classifiers__ = [
	"Development Status :: 4 - Beta",
	"Environment :: Console",
	"Environment :: No Input/Output (Daemon)",
	"Environment :: Other Environment",
	"Environment :: Plugins",
	"Environment :: Web Environment",
	"Intended Audience :: Developers",
	"Intended Audience :: Information Technology",
	"Intended Audience :: Science/Research",
	"Intended Audience :: System Administrators",
	"Intended Audience :: Telecommunications Industry",
	"License :: OSI Approved",
	"License :: OSI Approved :: MIT License",
	"Natural Language :: English",
	"Operating System :: POSIX",
	"Operating System :: POSIX :: Linux",
	"Programming Language :: Python",
	"Programming Language :: Python :: 2.5",
	"Programming Language :: Python :: 2.6",
	"Programming Language :: Python :: 3.0",
	"Topic :: Adaptive Technologies",
	"Topic :: Communications :: Chat",
	"Topic :: Communications :: Chat :: Internet Relay Chat",
	"Topic :: Communications :: Email",
	"Topic :: Communications :: Email :: Mail Transport Agents",
	"Topic :: Database",
	"Topic :: Internet",
	"Topic :: Internet :: WWW/HTTP",
	"Topic :: Internet :: WWW/HTTP :: HTTP Servers",
	"Topic :: Internet :: WWW/HTTP :: WSGI",
	"Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
	"Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
	"Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
	"Topic :: Software Development :: Libraries",
	"Topic :: Software Development :: Libraries :: Application Frameworks",
	"Topic :: Software Development :: Libraries :: Python Modules",
	"Topic :: System :: Clustering",
	"Topic :: System :: Distributed Computing"]
__str__ = "%s-%s" % (__name__, __version__)
__package_data__ = {}
__install_requires__ = []
__setup_requires__ = []
__extras_require__ = {}
__entry_points__ = """\
[console_scripts]
circuits.bench = circuits.tools.bench:main
circuits.sniffer = circuits.tools.sniffer:main
"""

from core import listener, Event, Component, SimpleComponent, Manager

from timers import Timer
from bridge import Bridge
from workers import Worker
from debugger import Debugger
