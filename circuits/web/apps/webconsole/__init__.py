import os
import re
import sys
import codeop
import inspect
import traceback

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from circuits import handler
from circuits.web import Controller

docroot = os.path.abspath(os.path.join(os.path.dirname(__file__), "htdocs"))

class HTTPREPL(object):

    def __init__(self, locals=None):
        super(HTTPREPL, self).__init__()

        self.locals = {}
        if locals:
            self.locals.update(locals)
        self.buffer = []

    def push(self, line):
        """Push 'line' and return exec results (None if more input needed)."""
        if line == "help":
            return "Type help(object) for help about object."
        if line == "help()":
            return "You cannot call help() without an argument."

        self.buffer.append(line)
        source = "\n".join(self.buffer)

        try:
            code = codeop.compile_command(source, "<HTTP input>", 'single')
        except (OverflowError, SyntaxError, ValueError):
            self.buffer = []
            return traceback.format_exc()

        if code is None:
            # More lines needed.
            return None

        self.buffer = []
        return self.execute(code)

    def execute(self, code):
        """Execute the given code in self.locals and return any stdout/sterr."""
        out = StringIO()
        oldout = sys.stdout
        olderr = sys.stderr
        sys.stdout = sys.stderr = out
        try:
            try:
                exec code in self.locals
            except:
                result = traceback.format_exc()
            else:
                result = out.getvalue()
        finally:
            sys.stdout = oldout
            sys.stderr = olderr
        out.close()
        return result

    def dir(self, line):
        """Examine a partial line and provide attr list of final expr."""
        line = re.split(r"\s", line)[-1].strip()
        # Support lines like "thing.attr" as "thing.", because the browser
        # may not finish calculating the partial line until after the user
        # has clicked on a few more keys.
        line = ".".join(line.split(".")[:-1])
        try:
            result = eval("dir(%s)" % line, {}, self.locals)
        except:
            return ""
        return result

    def doc(self, line):
        """Examine a partial line and provide sig+doc of final expr."""
        line = re.split(r"\s", line)[-1].strip()
        # Support lines like "func(text" as "func(", because the browser
        # may not finish calculating the partial line until after the user
        # has clicked on a few more keys.
        line = "(".join(line.split("(")[:-1])
        try:
            result = eval(line, {}, self.locals)
            try:
                if isinstance(result, type):
                    func = result.__init__
                else:
                    func = result
                args, varargs, varkw, defaults = inspect.getargspec(func)
            except TypeError:
                if callable(result):
                    doc = getattr(result, "__doc__", "") or ""
                    return "%s\n\n%s" % (line, doc)
                return None
        except:
            return None

        if args and args[0] == 'self':
            args.pop(0)
        missing = object()
        defaults = defaults or []
        defaults = ([missing] * (len(args) - len(defaults))) + list(defaults)
        arglist = []
        for a, d in zip(args, defaults):
            if d is missing:
                arglist.append(a)
            else:
                arglist.append("%s=%s" % (a, d))
        if varargs:
            arglist.append("*%s" % varargs)
        if varkw:
            arglist.append("**%s" % varkw)
        doc = getattr(result, "__doc__", "") or ""
        return "%s(%s)\n%s" % (line, ", ".join(arglist), doc)

class WebConsole(Controller):

    @handler("started", target="*")
    def _on_started(self, component, mode):
        self.repl = HTTPREPL(locals={"root": self.root})

    def index(self):
        """Return an HTTP-based Read-Eval-Print-Loop terminal."""
        return open(os.path.join(docroot, "index.html")).read()

    def push(self, line):
        """Push 'line' and return exec results as a bare response."""
        result = self.repl.push(line)
        if result is None:
            # More input lines needed.
            self.response.code = 204
        return result

    def dir(self, line):
        """Push 'line' and return result of eval on the final expr."""
        result = self.repl.dir(line)
        if not result:
            self.response.code = 204
            return
        return repr(result)

    def doc(self, line):
        """Push 'line' and return result of getargspec on the final expr."""
        result = self.repl.doc(line)
        if not result:
            self.response.code = 204
        return result

__all__ = ("WebConsole",)
