#!/usr/bin/env python
import pip

from setuptools import setup


def extract_requirements(filename):
    requirements = []
    for x in pip.req.parse_requirements(
            filename, session=pip.download.PipSession()):
        if x.req:
            requirements.append(str(x.req))
    return requirements


install_requires = extract_requirements('requirements.txt')


setup(
    name='yedit',
    version='0.0.1',
    description='Programmatic editing of yaml and json',
    author='Kenny Woodson',
    url='https://github.com/kwoodson/yedit',
    license="TODO",

    install_requires=install_requires,
    packages=['yedit'],
    package_dir={'': 'roles/lib_yaml_editor/'}
)
