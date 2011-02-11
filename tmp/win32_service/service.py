# winservice.py

import sys
from sys import modules
from traceback import format_exc
from threading import currentThread
from os.path import splitext, abspath

from servicemanager import LogInfoMsg
from win32api import SetConsoleCtrlHandler

from win32serviceutil import InstallService, RemoveService
from win32serviceutil import ServiceFramework, StartService

from win32event import INFINITE
from win32event import CreateEvent, SetEvent, WaitForSingleObject

from win32service import SERVICE_STOPPED
from win32service import SERVICE_AUTO_START, SERVICE_RUNNING
from win32service import SERVICE_START_PENDING, SERVICE_STOP_PENDING

from circuits import BaseComponent

class Service(BaseComponent, ServiceFramework):

    _svc_name_ = "unknown"
    _svc_display_name_ = "Service Template"

    def __init__(self, *args):
        BaseComponent.__init__(self)
        ServiceFramework.__init__(self, *args)

        self._stop_event = CreateEvent(None, 0, 0, None)

    def SvcDoRun(self):
        self.ReportServiceStatus(SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(SERVICE_RUNNING)
            self.run()
            WaitForSingleObject(self._stop_event, INFINITE)
        except Exception, e:
            LogInfoMsg("ERROR: %s" % e)
            LogInfoMsg(format_exc())
            self.SvcStop()

    def SvcStop(self):
        self.ReportServiceStatus(SERVICE_STOP_PENDING)
        self.stop()
        SetEvent(self._stop_event)
        self.ReportServiceStatus(SERVICE_STOPPED)

def install_service(cls, name, description=None, stay_alive=True):
    cls._svc_name_ = name
    cls._svc_display_name_ = description or name

    if hasattr(modules[cls.__module__], "__file__"):
        module_path = modules[cls.__module__].__file__
    else:
        module_path = sys.executable

    module_file = splitext(abspath(module_path))[0]

    cls._svc_reg_class_ = "%s.%s" % (module_file, cls.__name__)

    if stay_alive:
        SetConsoleCtrlHandler(lambda x: True, True)

    try:
        InstallService(
                cls._svc_reg_class_,
                cls._svc_name_,
                cls._svc_display_name_,
                startType=SERVICE_AUTO_START
        )
        print "Service installed"

        StartService(cls._svc_name_)
        print "Service started"
    except Exception, e:
        print "ERROR: %s" % e
        print format_exc()

def remove_service(name):
    try:
        RemoveService(name)
    except Exception, e:
        print "ERROR: %s" % e
        print format_exc()
