#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
    HAS_SETUPTOOLS = True
except ImportError:
    from distutils.core import setup
    HAS_SETUPTOOLS = False

if not HAS_SETUPTOOLS:
    import os
    from os import getcwd, listdir
    from os.path import isdir, isfile

    def is_package(path):
        return isdir(path) and isfile(os.path.join(path, "__init__.py"))

    def find_packages(where="."):
        packages = {}
        for item in listdir(where):
            dir = os.path.join(where, item)
            if is_package(dir):
                module_name = item
                packages[module_name] = dir
                packages.update(find_packages(dir))
        return packages

from circuits.version import forget_version, remember_version

forget_version()
version = remember_version()

setup(
    name="circuits",
    version=version,
    description="Lightweight Event driven Framework",
    long_description=open("README", "r").read(),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="http://bitbucket.org/prologic/circuits/",
    download_url="http://bitbucket.org/prologic/circuits/downloads/",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Environment :: Other Environment",
        "Environment :: Plugins",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3.0",
        "Topic :: Adaptive Technologies",
        "Topic :: Communications :: Chat",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        "Topic :: Communications :: Email",
        "Topic :: Communications :: Email :: Mail Transport Agents",
        "Topic :: Database",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing"],
    license="MIT",
    keywords="event framework distributed concurrent component asynchronous",
    platforms="POSIX",
    packages=find_packages("."),
    entry_points="""
    [console_scripts]
    circuits.bench = circuits.tools.bench:main
    circuits.web = circuits.web.main:main
    """
)
