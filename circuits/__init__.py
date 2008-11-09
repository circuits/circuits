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
	"Classifier: Development Status :: 6 - Mature",
	"Classifier: Environment :: Console",
	"Classifier: Environment :: No Input/Output (Daemon)",
	"Classifier: Environment :: Other Environment",
	"Classifier: Environment :: Plugins",
	"Classifier: Environment :: Web Environment",
	"Classifier: Intended Audience :: Developers",
	"Classifier: Intended Audience :: Information Technology",
	"Classifier: Intended Audience :: Science/Research",
	"Classifier: Intended Audience :: System Administrators",
	"Classifier: Intended Audience :: Telecommunications Industry",
	"Classifier: License :: OSI Approved",
	"Classifier: License :: OSI Approved :: MIT License",
	"Classifier: Natural Language :: English",
	"Classifier: Operating System :: POSIX",
	"Classifier: Operating System :: POSIX :: Linux",
	"Classifier: Programming Language :: Python",
	"Classifier: Programming Language :: Python :: 2.5",
	"Classifier: Programming Language :: Python :: 2.6",
	"Classifier: Programming Language :: Python :: 3.0",
	"Classifier: Topic :: Adaptive Technologies",
	"Classifier: Topic :: Communications :: Chat",
	"Classifier: Topic :: Communications :: Chat :: Internet Relay Chat",
	"Classifier: Topic :: Communications :: Email",
	"Classifier: Topic :: Communications :: Email :: Mail Transport Agents",
	"Classifier: Topic :: Database",
	"Classifier: Topic :: Internet",
	"Classifier: Topic :: Internet :: WWW/HTTP",
	"Classifier: Topic :: Internet :: WWW/HTTP :: HTTP Servers",
	"Classifier: Topic :: Internet :: WWW/HTTP :: WSGI",
	"Classifier: Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
	"Classifier: Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
	"Classifier: Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
	"Classifier: Topic :: Software Development :: Libraries",
	"Classifier: Topic :: Software Development :: Libraries :: Application Frameworks",
	"Classifier: Topic :: Software Development :: Libraries :: Python Modules",
	"Classifier: Topic :: System :: Clustering",
	"Classifier: Topic :: System :: Distributed Computing"]
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

from core import listener, Event, Component, Manager

from timers import Timer
from bridge import Bridge
from workers import Worker
from debugger import Debugger
