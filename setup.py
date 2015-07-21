#!/usr/bin/env python


from glob import glob


from setuptools import setup, find_packages


from circuits.version import version


setup(
    name="circuits",
    version=version,
    description="Asynchronous Component based Event Application Framework",
    long_description=open("README.rst").read().replace(
        ".. include:: examples/index.rst",
        open("examples/index.rst", "r").read()
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
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
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
    install_requires=[],
    entry_points={
        "console_scripts": [
            "circuits.web=circuits.web.main:main",
        ]
    },
    test_suite="tests.main.main",
    zip_safe=True
)
