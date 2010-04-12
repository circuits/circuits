# Module:   __init__
# Date:     3rd October 2008
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""circuits

Lightweight Event driven Framework

:copyright: CopyRight (C) 2004-2010 by James Mills
:license: MIT (See: LICENSE)
"""

try:
    from __version__ import version as __version__
except ImportError:
    __version__ = "unknown"

from core import *
