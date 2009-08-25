#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""An example of a Circuits Component that requires users authenticate
against /etc/passwd and /etc/shadow before letting them into the web site."""

import os, re
from commands import getstatusoutput
from circuits import handler, Component
from circuits.web import _httpauth, Server, Controller
from circuits.web.errors import HTTPError, Unauthorized

__author__ = 'Dan McDougall <YouKnowWho@YouKnowWhat.com>'

def check_credentials(user, password):
    """Checks a given user and password against /etc/shadow (or /etc/passwd if
    /etc/shadow doesn't exist).  Returns True on success and False on failure."""
    from crypt import crypt
    shadow_hash = ''
    salt_regex = re.compile(r'\$.*\$.*\$') # Matches salts, e.g. "$1$72p6zzHp$"
    if os.path.exists('/etc/shadow'):
        password_file = '/etc/shadow'
    else:
        password_file = '/etc/passwd'
    shadow = open(password_file, 'r').readlines()
    for line in shadow:
        cols = line.split(':')
        if cols[0] == user:
            shadow_hash = cols[1]
    if salt_regex.match(shadow_hash): # If there's a hashed password...
        salt = salt_regex.match(shadow_hash).group() # Grab it
        hashed_pass = crypt(password, salt) # Now hash the plaintext password
        if hashed_pass == shadow_hash: # If they match...
            return True
    return False

class PasswdAuth(Component):
    """A Circuits Component that authenticates the user using the credentials
    stored in /etc/passwd and /etc/shadow (if present)."""

    channel = "web"

    def __init__(self, name="circuits.passwdauth", *args, **kwargs):
        super(PasswdAuth, self).__init__(*args, **kwargs)
        self._name = name

    @handler("request", filter=True)
    def authcheck(self, request, response):
        """Obtains the authorization header (if any) and checks the supplied
        username and password against the credentials stored in /etc/passwd
        and /etc/shadow (if present)"""
        if 'authorization' in request.headers:
            ah = _httpauth.parseAuthorization(request.headers['authorization'])
            if ah is None:
                return HTTPError(request, response, 400)
            username = ah["username"]
            password = ah["password"]
            
            auth_result = check_credentials(username, password)
            if auth_result: # User authenticated successfully
                request.login = ah["username"]
                return
        response.headers["WWW-Authenticate"] = _httpauth.basicAuth('System')
        request.login = False
        return Unauthorized(request, response)

class Root(Controller):
    """Our web site"""
    def index(self):
        return "Hello, %s" % self.request.login

(Server(8000) + PasswdAuth() + Root()).run()
