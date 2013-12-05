#!/usr/bin/env python

from setuptools import setup, Command

from distutils.command.build_py import build_py


setup(name='psrecord',
      version='0.1.0.dev',
      description='Python package to record activity from processes',
      author='Thomas Robitaille',
      author_email='thomas.robitaille@gmail.com',
      packages=['psrecord'],
      provides=['psrecord'],
      scripts=['scripts/psrecord'],
      requires=['psutil'],
      cmdclass={'build_py': build_py},
      classifiers=[
                   "Development Status :: 3 - Alpha",
                   "Programming Language :: Python",
                   "License :: OSI Approved :: BSD License",
                  ],
     )
