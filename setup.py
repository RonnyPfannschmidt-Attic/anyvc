#!/usr/bin/python
from __future__ import with_statement
import os, sys
from commands import getoutput
try:
    from setuptools import setup
except:
    from distutils.core import setup
import time
import hgdistver

def read_readme():
    with open('docs/readme.rst') as f:
        return f.read()

setup(
    version = hgdistver.get_version(cachefile='anyvc/__version__.py'),
    name = 'anyvc',
    packages = [
        'anyvc',
        'anyvc.common',
        'anyvc.remote',

        # backends
        'anyvc.mercurial',
        'anyvc.git',
        'anyvc.subversion',
        'anyvc.bazaar',
    ],
    install_requires=[
        'py>=1.3',
    ],
    extras_require={
        'mercurial': ['mercurial'],
        'bazaar': ['bzr'],
        'git': ['dulwich'],
        'subversion': ['subvertpy'],
        'remoting': ['execnet'],
    },

    scripts=[
        'bin/vc',
    ],
    description='Library to access any version control system.',
    license='GNU GPL2 (or later) as published by the FSF',
    url='http://www.bitbucket.org/RonnyPfannschmidt/anyvc/',
    author='Ronny Pfannschmidt',
    author_email='Ronny.Pfannschmidt@gmx.de',
    long_description=read_readme(),
    classifiers = [
        'Intended Audience :: Developers',
    ],
)
