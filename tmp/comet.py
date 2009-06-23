#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Comet Examples with circuits.web

Based on a CherryPy example by Dan McDougall
"""

import os
import time
import signal
from subprocess import Popen, PIPE

# These two are Python 2.6+ only...
from multiprocessing import Process, Queue, Pipe
from string import Template

from circuits.web import Server, Controller, Logger

def execute_command(command, conn, q):
    """Run the given command, report the resulting pid via q, and stream the
    output through conn.

    @command: Command to execute (may be a command that never exits on it's own)
    @conn: Pipe() to stream the command output into.
    @q: multiprocessing.Queue() to report back the process PID"""
# When starting a process that may spawn other processes it is critical
# that 'preexec_fn=os.setsid' be set
    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE,
                    close_fds=True, preexec_fn=os.setsid)
    while True:
        q.put(process.pid) # Report back our process group PID
        out = process.stdout.read(1) # One character at a time
        if out == '' and process.poll() != None:
            break
        if out != '':
            conn.send(out) # Stream the output of our command through the Pipe

# Trying to cut down on long lines...
jquery_url = 'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js'
jquery_ui_url = 'http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/jquery-ui.min.js'
jquery_ui_css_url = \
'http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/themes/black-tie/jquery-ui.css'

class Comet(Controller):
    command_pid = None

    def index(self):
        # Note: Dollar signs are escaped by using two ($$)
        html = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
  <head>
    <link rel="stylesheet" type="text/css" href="${jquery_ui_css_url}" media="screen" />
    <script type="text/javascript" src="${jquery_url}"></script>
    <script type="text/javascript" src="${jquery_ui_url}"></script>
    <style>
    .fg-button {
    outline: 0;
    clear: left;
    margin:0 4px 0 0;
    padding: .1em .5em;
    text-decoration:none !important;
    cursor:pointer;
    position: relative;
    text-align: center;
    zoom: 1;
    }
    .fg-button .ui-icon {
    position: absolute;
    top: 50%;
    margin-top: -8px;
    left: 50%;
    margin-left: -8px;
    }
    a.fg-button { float:left;  }
    .terminal {
    font-family: monospace;
    width: 100%; height: 100%;
    border: none;
    }
    </style>
  </head>
  <body>
  <script type="text/javascript">
    $$(document).ready(function(){
        $$('#kill_ping').click(function() {
            $$.ajax({
                url: "/kill_proc",
                cache: false,
                success: function(html){
                    window.frames[0].stop();
                    $$("#ping_kill").html(html);
                }
            });
            return false;
        });
    });
    </script>
  <form id="ping_form" target="console_iframe" method="post" action="/ping">
  <input type="text" id="host" name="host" size="18" />
  <button id="ping" class="fg-button ui-state-default ui-corner-all" type="submit">
  Ping
  </button>
  </form>
  <form id="kill_form" method="post" action="/kill_proc">
  <button id="kill_ping" class="fg-button ui-state-default ui-corner-all" type="submit">
  Control-C
  </button>
  </form>
  <div id="ping_kill"></div>
  <iframe name="console_iframe" class="terminal" scrolling="auto" />
  </body>
</html>
"""
        t = Template(html)
        page = t.substitute(
            jquery_ui_css_url=jquery_ui_css_url,
            jquery_url=jquery_url,
            jquery_ui_url=jquery_ui_url)
        return page

    def ping(self, host, **kw):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.stream = True
        command = "ping '%s'" % host
        def run_command():
            parent_conn, child_conn = Pipe() # Set up the communications channel
            q = Queue() # This is just for communicating the pid
            p = Process(target=execute_command, args=(command,child_conn,q))
            p.start()
            # Assign the command PID so we can use it elsewhere...
            self.command_pid = q.get()

            while True:
                out = parent_conn.recv()
                if out == '' and process.poll() != None:
                    break
                if out != '':
                    yield out
        return run_command()

    def kill_proc(self, **kw):
        """Kill the process associated with self.command_pid"""
        os.killpg(self.command_pid, signal.SIGUSR1)
        return "Success!"

from circuits import Debugger
(Server(10000) + Debugger() + Logger() + Comet()).run()
