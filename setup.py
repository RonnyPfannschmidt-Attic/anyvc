#!/usr/bin/python
from __future__ import with_statement
from setuptools import setup, find_packages


def read_readme():
    result = []
    for fname in ('docs/readme.rst', 'docs/changelog.rst'):
        with open(fname) as f:
            result.append(f.read())
    return '\n'.join(result)


setup(
    name='anyvc',
    packages=find_packages(),
    setup_requires=[
        'hgdistver',
    ],
    install_requires=[
        'click>=3.0',
        'colorama',
        'apipkg',
        'py>=1.3',
    ],
    extras_require={
        'mercurial': ['mercurial'],
        'git': ['dulwich'],
        'remoting': ['execnet'],
    },
    entry_points='''
        [console_scripts]
        vc = anyvc.client:cli
    ''',


    description='Library to access any version control system.',
    license='GNU GPL2 (or later) as published by the FSF',
    url='http://www.bitbucket.org/RonnyPfannschmidt/anyvc/',
    author='Ronny Pfannschmidt',
    author_email='Ronny.Pfannschmidt@gmx.de',
    long_description=read_readme(),
    get_version_from_scm=True,
    classifiers=[
        'Intended Audience :: Developers',
    ],
)
