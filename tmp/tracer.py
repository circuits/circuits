# Module:   debugger
# Date:     2nd April 2006
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""
Debugger component used to debug each event in a system by printing
each event to sys.stderr or to a Logger Component instnace.
"""

import os
import gc
import sys
from cStringIO import StringIO

from circuits.tools import reprhandler
from circuits import handler, BaseComponent

def modname(path):
    """Return a plausible module name for the patch."""

    base = os.path.basename(path)
    filename, ext = os.path.splitext(base)
    return filename

class Tracer(BaseComponent):

    def __init__(self):
        super(Tracer, self).__init__()

        self._old_trace_func = sys.gettrace()

        sys.settrace(self.globaltrace)

    def __del__(self):
        sys.settrace(self._old_trace)

    def globaltrace(self, frame, why, arg):
        if why == 'call':
	    if frame is not None:
                f = self.file_module_function_of(frame)
                if not f[0].startswith("/usr"):
                    print f[1], f[2]
            if frame.f_back is not None:
                p = self.file_module_function_of(frame.f_back)
                if not p[0].startswith("/usr"):
                    print " ", p[1], p[2]

    def file_module_function_of(self, frame):
        code = frame.f_code
        filename = code.co_filename
        if filename:
            modulename = modname(filename)
        else:
            modulename = None

        funcname = code.co_name
        clsname = None
        ## use of gc.get_referrers() was suggested by Michael Hudson
        # all functions which refer to this code object
        funcs = [f for f in gc.get_referrers(code)
                     if hasattr(f, "func_doc")]
        # require len(func) == 1 to avoid ambiguity caused by calls to
        # new.function(): "In the face of ambiguity, refuse the
        # temptation to guess."
        if len(funcs) == 1:
            dicts = [d for d in gc.get_referrers(funcs[0])
                         if isinstance(d, dict)]
            if len(dicts) == 1:
                classes = [c for c in gc.get_referrers(dicts[0])
                               if hasattr(c, "__bases__")]
                if len(classes) == 1:
                    # ditto for new.classobj()
                    clsname = str(classes[0])
                    # cache the result - assumption is that new.* is
                    # not called later to disturb this relationship
                    # _caller_cache could be flushed if functions in
                    # the new module get called.
        if clsname is not None:
            # final hack - module name shows up in str(cls), but we've already
            # computed module name, so remove it
            clsname = clsname.split(".")[1:]
            clsname = ".".join(clsname)
            funcname = "%s.%s" % (clsname, funcname)

        return filename, modulename, funcname
