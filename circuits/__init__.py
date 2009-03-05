# Module:	__init__
# Date:		3rd October 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""A Lightweight, Event driven Framework with a strong Component Architecture.

Components communicate with one another by propagating Events on Channels
throughout the System. Each Component has a set of Event Handlers that
can listen for or filter Events on one or more Channels. Components react to Events and in turn expose further Events into the System. Each Component
is capable of managing it's own Events as well as those of other Components.
Complex directed graph structures can be created with Component Registrations,
this gives a level of hierarchy and separation of concern.

Example:
   >>> from time import sleep
   >>> from circuits import Event, Component
   >>>
   >>> class App(Component):
   ...   def hello(self):
   ...      print "Hello World!"
   >>> app = App()
   >>> app.start()
   >>> app.push(Event(), "hello")
   >>> sleep(1)
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
__copyright__ = "Copyright (C) 2004-2009 by %s" % __author__
__license__ = "MIT"
__platforms__ = "POSIX"
__keywords__ = "circuits Event Library Framework Component Architecture"
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

from core import listener, handler, Event, Component,  Manager

from bridge import Bridge
from workers import Thread
from debugger import Debugger
from timers import Timer, Timer

try:
    from workers import Process
except ImportError:
    pass
