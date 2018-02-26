#!/usr/bin/env python
import os
import pip

from setuptools import Command, setup, find_packages


def extract_requirements(filename):
    requirements = []
    for x in pip.req.parse_requirements(
            filename, session=pip.download.PipSession()):
        if x.req:
            requirements.append(str(x.req))
    return requirements


install_requires = extract_requirements('requirements.txt')


class InstallRoleCommand(Command):
    """
    Installs an ansible role.
    """

    description = 'Install the ansible role for this package'
    user_options = [
        ('role-root=', None, ('Root path to where the modules live. '
                              'Default: /etc/ansible/roles/')),
        ('role-name=', None, 'Name of the module. Default: lib_yaml_editor'),
    ]

    def initialize_options(self):
        self.role_root = '/etc/ansible/roles/'
        self.role_name = 'lib_yaml_editor'

    def finalize_options(self):
        self._full_path = os.path.sep.join([
            self.role_root, self.role_name, 'library'])

    def run(self):
        # Ensure the path exists
        self.mkpath(self._full_path)
        self.copy_file(
            './src/yedit/__init__.py',
            os.path.sep.join([self._full_path, 'yedit.py']))


setup(
    name='yedit',
    version='0.0.1',
    description='Programmatic editing of yaml and json',
    author='Kenny Woodson',
    url='https://github.com/kwoodson/yedit',
    license="TODO",

    install_requires=install_requires,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    cmdclass={
        'install_role': InstallRoleCommand,
    },
)
