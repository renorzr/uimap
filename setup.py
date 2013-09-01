#!/usr/bin/env python

from distutils.core import setup

setup(name='uimap',
      version='1.0',
      description='Cross-platform UI Automation Python Library',
      author='Reno Ren',
      author_email='friendkey@gmail.com',
      url='http://www.python.org/sigs/uimap/',
      packages=['uimap', 'uimap.drivers', 'uimap.drivers.ldtp', 'uimap.drivers.wpf'],
      package_dir={'': 'src'},
      license='MIT',
     )
