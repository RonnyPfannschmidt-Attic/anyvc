
import os

from distutils.core import setup

def read_readme():
    f = open(os.path.join('docs', 'source', 'readme.rst'))
    readme = f.read()
    f.close()
    return readme

setup(
    version = '0.2',
    name = 'anyvc',
    packages = [
        'anyvc',
        'anyvc.repository',
        'anyvc.workdir',
    ],
    scripts = ['bin/vc'],

    description='Library to access any version control system.',
    url='http://www.bitbucket.org/RonnyPfannschmidt/anyvc/',
    author='Ronny Pfannschmidt',
    author_email='Ronny.Pfannschmidt@gmx.de',
    long_description=read_readme(),

)
