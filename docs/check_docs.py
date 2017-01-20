#!/usr/bin/env python

from subprocess import PIPE, STDOUT, Popen


def test_linkcheck(tmpdir):
    doctrees = tmpdir.join("doctrees")
    htmldir = tmpdir.join("html")
    p = Popen([
        "sphinx-build", "-W", "-blinkcheck",
        "-d", str(doctrees), "source", str(htmldir)
    ], stdout=PIPE, stderr=STDOUT)
    stdout, _ = p.communicate()
    if not p.wait() == 0:
        print(stdout)


def test_build_docs(tmpdir):
    doctrees = tmpdir.join("doctrees")
    htmldir = tmpdir.join("html")
    p = Popen([
        "sphinx-build", "-W", "-bhtml",
        "-d", str(doctrees), "source", str(htmldir)
    ], stdout=PIPE, stderr=STDOUT)
    stdout, _ = p.communicate()
    if not p.wait() == 0:
        print(stdout)
