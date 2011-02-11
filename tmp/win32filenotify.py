from sys import modules
import os
import win32file
import win32event
import win32con
import httplib
import urllib
import ConfigParser
import win32serviceutil
import win32service
import win32api

################################################################################
#   Written by      : Warwick Prince
#   Date            : 07/03/2010
#   Comment         : Runs as a windows service.  Self installation and removal :-)
#   Note            : To get this to install, I had to comment out a line in (py2exe) boot_service.py
#                   : as follows;  # description = getattr(k, "_svc_description_", None), as
#                   : it was broken..

class Service(win32serviceutil.ServiceFramework):

    """
        Service to listen to a given folder for new files or file deletions. In the
        case of a new file, read the file content and POST it to a waiting web server
        that will accept POSTS to s /FILENOTIFY url.  Expect a OK\n or FAIL\n response
    """

    _svc_name_ = 'FileNotification'
    _svc_display_name_ = 'MSI File Notifications to Clear Enterprise'

    def __init__(self, *args):

        win32serviceutil.ServiceFramework.__init__(self, *args)

        self.log('Preparing Service')
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

        # Set some defaults just incase not in ini or no ini
        self.watchFolder = '\\\\127.0.0.1\\c\\'
        self.notifyServer = '127.0.0.1'
        self.retryInterval = 60000
        self.pauseInterval = 2000
        self.fileFilter = ''
        self.debugMode = True

        logEntry = ''

        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open('c:\\Program Files\\File Notifications Service\\FileNotification.ini'))

            # Set defaults if no setting found
            if config.has_option('Server', 'WatchFolder'): self.watchFolder = config.get('Server', 'WatchFolder')
            if config.has_option('Server', 'NotifyServer'): self.notifyServer = config.get('Server', 'NotifyServer')
            if config.has_option('Server', 'RetryInterval'): self.retryInterval = config.getint('Server', 'RetryInterval')
            if config.has_option('Server', 'PauseInterval'): self.pauseInterval = config.getint('Server', 'PauseInterval')
            if config.has_option('Server', 'DebugMode'): self.debugMode = config.getboolean('Server', 'DebugMode')
            if config.has_option('Server', 'FileFilter'): self.fileFilter = config.get('Server', 'FileFilter')

        except:
            self.log('WARNING: No FileNotification.ini file located in c:\\Program Files\\File Notifications Service\\FileNotification.ini')
            config = None
            pass # Probably no ini file found

        self.retryFiles = []
        self.pathToWatch = os.path.abspath(self.watchFolder) # Creates a full path to the path supplied.  e.g. watchFolder could be "." for "here"

        if self.debugMode:
            logEntry += 'Server initialised OK'
            logEntry += 'Configuration\n'
            logEntry += 'WatchFolder  : %s\n' % self.watchFolder
            logEntry += 'NotifyServer : %s\n' % self.notifyServer
            logEntry += 'RetryInterval: %s\n' % self.retryInterval
            logEntry += 'PauseInterval: %s\n' % self.pauseInterval
            self.log(logEntry)

    def log(self, msg):
        import servicemanager
        servicemanager.LogInfoMsg(str(msg))
        def sleep(self, sec):
            win32api.Sleep(sec*1000, True)
    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.startWatching()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.log('stopping')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def startWatching(self):
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('Start Watching')
            #
            #  FindFirstChangeNotification sets up a handle for watching
            #  file changes. The first parameter is the path to be
            #  watched; the second is a boolean indicating whether the
            #  directories underneath the one specified are to be watched;
            #  the third is a list of flags as to what kind of changes to
            #  watch for. We're just looking at file additions / deletions.
            #
            try:
                changeHandle = win32file.FindFirstChangeNotification(self.pathToWatch, False, win32con.FILE_NOTIFY_CHANGE_FILE_NAME)
            except:
                self.log('ERROR: There is a problem with the path to watch: %s' % self.pathToWatch)
                raise

            #
            # Loop forever, listing any file changes. The WaitFor... will
            # time out every set interval allowing for keyboard interrupts
            # to terminate the loop / program
            # We are ALSO listeniong for a service stop request to get out of the loop
            #

            try:
                oldPathContents = dict([(file, None) for file in os.listdir(self.pathToWatch)])
                retryTimer = 0

                while 1:
                    result = win32event.WaitForSingleObject(changeHandle, self.pauseInterval)
                    #
                    #   If the WaitFor... returned because of a notification (as
                    #   opposed to timing out or some error) then look for the
                    #   changes in the directory contents.
                    #

                    if result == win32con.WAIT_OBJECT_0:

                        # Get the updated directory now that we know something has changed
                        newPathContents = dict([(file, None) for file in os.listdir (self.pathToWatch)])

                        # Diff the old and the new to get those items added and those items removed.
                        addedFiles = [file for file in newPathContents if not file in oldPathContents]
                        deletedFiles = [file for file in oldPathContents if not file in newPathContents]

                        # Send content of added files to HTTP server for further processing
                        if addedFiles:
                            self.onAdd(addedFiles)

                        # Interesting, but of no use to us here - do nothing at this point
                        if deletedFiles:
                            self.onDelete(deletedFiles)

                        oldPathContents = newPathContents

                        win32file.FindNextChangeNotification(changeHandle)

                    # See if we have been stopped
                    result = win32event.WaitForSingleObject(self.stop_event, 10)

                    if result == win32con.WAIT_OBJECT_0:
                        self.log('Service Stop Requested..')
                        break

                    # If we have any files that have failed to be sent, retry them after the retry timeout has occured
                    if self.retryFiles:
                        retryTimer += self.pauseInterval
                        if retryTimer >= self.retryInterval:
                            if self.debugMode: print 'Attempting retry of retry list: %s...' % self.retryFiles
                            addedFiles = [] + self.retryFiles    # copy the retry list into the addedFiles list for processing again
                            self.onAdd(addedFiles) # retry the send
                            retryTimer = 0

            except Exception as message:
    			self.log('Exception : %s' % message)
	       		self.SvcStop()

            finally:
              win32file.FindCloseChangeNotification(changeHandle)

        except Exception as message:
			self.log('Exception : %s' % message)
			self.SvcStop()

    def onAdd(self, addedFiles):
        self.log("Processing: %s" % addedFiles)

        if self.fileFilter:
            pass # Not supported at this time

        # Step through one or more files and process them
        for fileName in addedFiles:
            # Create the full path to the file (OS safe!)
            parts = (self.pathToWatch, fileName)
            completeFilename = os.path.join(*parts)

            try:
                file = open(completeFilename, 'r')
                fileContent = file.read()
                file.close()
                httpContent = urllib.urlencode({'xml': fileContent})
                httpContent = httpContent.replace('+', '%20') # fix what appears to be bad escaping in the above function
                sendFailed = True
                # send to the web server
                try:
                    # Connect to server
                    httpConnection = httplib.HTTPConnection(self.notifyServer, 80)
                    if self.debugMode and httpConnection: self.log('Connected to HTTP server OK')
                    # Post the data
                    httpConnection.request('POST', '/FILENOTIFY', httpContent)
                    # Get the response
                    httpResponse = httpConnection.getresponse()
                    if self.debugMode and httpResponse: self.log('Got a response form the HTTP server')
                    # Check the result, if OK, then remove the file.  If NOT OK
                    # then add to the retry list.

                    if httpResponse.status in (200, 201, 202, 300, 301, 307):
                        # OK raw comms level response, now check what the server actually returned.
                        # We can expect a basic OK\n or FAIL\n response

                        responseText = httpResponse.read()
                        if self.debugMode: self.log('Received this response: %s' % responseText)

                        if responseText == 'OK\n':
                            if self.debugMode: self.log('OK response received!')
                            sendFailed = False # flag All OK
                        else:
                            if self.debugMode: self.log('Response received was: %s' % responseText)

                except httplib.CannotSendRequest:
                    self.log('Exception caught on BAD SEND TO HTTP SERVER')
                    pass

                finally:
                    # Make sure we kill the server conections etc.
                    try:
                        httpConnection.close()
                    except:
                        pass

                # If we failed to send, it's placed in the retryFiles list for processing later.

                if sendFailed:
                    self.log('Send to HTTP server failed - Adding file to retry list')
                    if fileName not in self.retryFiles: self.retryFiles.append(fileName)
                else:
                    # OK to remove the file from the folder now - no longer required.
                    try:
                        if fileName in self.retryFiles: self.retryFiles.remove(fileName)
                        os.remove(completeFilename)
                    except:
                        pass # Hmm..  Oh well, no harm in leaving it there..

            except Exception as message:
                # Hmm - failed to open or process the file.  If it's in the retry list, it could possibly have been deleted.  Remove from there
                self.log('CRITICAL FAIL - Could not open or read file: %s\nException was %s' % (completeFilename, message))
                if fileName in self.retryFiles:
                    self.log('Located %s in retry list and removed it' % fileName)
                    self.retryFiles.remove(fileName)
                    pass

    def onDelete(self, deletedFiles):
        # We don't really care about deletes in this version
        pass
