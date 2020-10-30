#!/usr/bin/env python
from glob import glob

from setuptools import find_packages, setup


def read_file(filename):
    try:
        return open(filename, "r").read()
    except IOError:
        return ""


setup(
    name="circuits",
    description="Asynchronous Component based Event Application Framework",
    long_description=open("README.rst").read().replace(
        ".. include:: examples/index.rst",
        read_file("examples/index.rst")
    ),
    author="James Mills",
    author_email="prologic@shortcircuit.net.au",
    url="http://circuitsframework.com/",
    download_url="http://bitbucket.org/circuits/circuits/downloads/",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Adaptive Technologies",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
        "Topic :: Communications :: Email :: Mail Transport Agents",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing"],
    license="MIT",
    keywords="event framework distributed concurrent component asynchronous",
    platforms="POSIX",
    packages=find_packages(
        exclude=[
            "*.tests",
            "*.tests.*",
            "tests.*",
            "tests",
            "*.fabfile",
            "*.fabfile.*",
            "fabfile.*",
            "fabfile",
        ]
    ),
    scripts=glob("bin/*"),
    entry_points={
        "console_scripts": [
            "circuits.web=circuits.web.main:main",
        ]
    },
    zip_safe=True,
    use_scm_version={
        "write_to": "circuits/version.py",
    },
    setup_requires=[
        "setuptools_scm"
    ],
    extras_require={"stomp": ["stompest>=2.3.0", "pysocks>=1.6.7"]},
)
