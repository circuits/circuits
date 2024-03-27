#!/usr/bin/env python
"""
Shadow Auth Demo

An example of a Circuits Component that requires users authenticate
against /etc/passwd or /etc/shadow before letting them into the web site.

curl -i http://test:test@localhost:8000/
curl -i http://root:test@localhost:8000/
"""

from crypt import crypt

from os import path
from re import compile as compile_regex
from socket import gethostname

from circuits import Component, handler
from circuits.web import Controller, Server, _httpauth
from circuits.web.errors import httperror, unauthorized


def check_auth(user, password):
    salt_pattern = compile_regex(r'\$.*\$.*\$')
    passwd = './etc/shadow' if path.exists('./etc/shadow') else '/etc/passwd'

    with open(passwd) as f:
        rows = (line.strip().split(':') for line in f)
        records = [row for row in rows if row[0] == user]

    if not records:
        return False
    hash = records[0][1]
    salt = salt_pattern.match(hash).group()

    return crypt(password, salt) == hash


class PasswdAuth(Component):
    channel = 'web'

    def init(self, realm=None):
        self.realm = realm or gethostname()

    @handler('request', priority=1.0)
    def _on_request(self, event, request, response):
        if 'authorization' in request.headers:
            ah = _httpauth.parseAuthorization(request.headers['authorization'])
            if ah is None:
                event.stop()
                return httperror(request, response, 400)

            username, password = ah['username'], ah['password']

            if check_auth(username, password):
                request.login = username
                return

        response.headers['WWW-Authenticate'] = _httpauth.basicAuth(self.realm)

        event.stop()
        return unauthorized(request, response)


class Root(Controller):
    def index(self):
        return f'Hello, {self.request.login:s}'


app = Server(('0.0.0.0', 8000))
PasswdAuth().register(app)
Root().register(app)
app.run()
