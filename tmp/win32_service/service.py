# winservice.py

import sys
from sys import modules
from traceback import format_exc
from os.path import splitext, abspath

from win32api import SetConsoleCtrlHandler
from servicemanager import LogInfoMsg, RegisterServiceCtrlHandler

from win32serviceutil import InstallService, RemoveService
from win32serviceutil import ServiceFramework, StartService

from win32event import INFINITE
from win32event import CreateEvent, SetEvent, WaitForSingleObject

from win32service import SetServiceStatus
from win32service import SERVICE_STOPPED
from win32service import SERVICE_CONTROL_STOP
from win32service import SERVICE_CONTROL_SHUTDOWN
from win32service import SERVICE_WIN32_OWN_PROCESS
from win32service import SERVICE_CONTROL_INTERROGATE
from win32service import SERVICE_AUTO_START, SERVICE_RUNNING
from win32service import SERVICE_START_PENDING, SERVICE_STOP_PENDING
from win32service import SERVICE_ACCEPT_STOP, SERVICE_ACCEPT_SHUTDOWN

from circuits import BaseComponent

class Service(BaseComponent):

    _svc_name_ = "unknown"
    _svc_display_name_ = "Service Template"

    channel = "service"

    def __init__(self, *args, **kwargs):
        channel = kwargs.get("channel", Service.channel)
        super(Service, self).__init__(channel=channel)

        self._ssh = RegisterServiceCtrlHandler(args[0], self.ServiceCtrlHandler)
        self._checkPoint = 0

    def GetAcceptedControls(self):
        return SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN

    def ReportServiceStatus(self, serviceStatus, waitHint=5000, win32ExitCode=0,
            svcExitCode = 0):
        if self._ssh is None: # Debugging!
            return
        if serviceStatus == SERVICE_START_PENDING:
            accepted = 0
        else:
            accepted = self.GetAcceptedControls()

        if serviceStatus in [SERVICE_RUNNING,  SERVICE_STOPPED]:
            checkPoint = 0
        else:
            self._checkPoint += 1
            checkPoint = self._checkPoint

        # Now report the status to the control manager
        status = (SERVICE_WIN32_OWN_PROCESS,
                 serviceStatus,
                 accepted, # dwControlsAccepted,
                 win32ExitCode, # dwWin32ExitCode;
                 svcExitCode, # dwServiceSpecificExitCode;
                 checkPoint, # dwCheckPoint;
                 waitHint)
        SetServiceStatus(self._ssh, status)

    def SvcInterrogate(self):
        # Assume we are running, and everyone is happy.
        self.ReportServiceStatus(SERVICE_RUNNING)

    def SvcOther(self, control):
        print "Unknown control status - %d" % control

    def ServiceCtrlHandler(self, control):
        if control == SERVICE_CONTROL_STOP:
            self.SvcStop()
        elif control == SERVICE_CONTROL_INTERROGATE:
            self.SvcInterrogate()
        elif control == SERVICE_CONTROL_SHUTDOWN:
            self.SvcShutdown()
        else:
            self.SvcOther(control)

    def SvcRun(self):
        self.ReportServiceStatus(SERVICE_RUNNING)
        self.run()
        self.ReportServiceStatus(SERVICE_STOP_PENDING)

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
