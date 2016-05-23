#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
  README = f.read()

requires = [
  'aadict >= 0.2.2',
  'caditlib >= 0.1-r4943',
  'morph >= 0.1.2',
  'pyramid >= 1.4.2',
  'pyramid_iniherit >= 0.1.9',
  'six >= 1.6.1',
  'sqlalchemy >= 0.8.2',
  ]

test_requires = [
  'nose >= 1.3.0',
  ]

classifiers = [
  'Development Status :: 4 - Beta',
  'Environment :: Web Environment',
  'Intended Audience :: Developers',
  'License :: OSI Approved :: MIT License',
  'Natural Language :: English',
  'Operating System :: OS Independent',
  'Programming Language :: Python',
  'Topic :: Software Development :: Testing',
]

setup(
  name='pyramid_test',
  version='0.1.0',
  description="A collection of test helper functions to make testing easy!",
  long_description=README,
  classifiers=classifiers,
  platforms=['any'],
  url='https://github.com/canaryhealth/pyramid_test',
  license='MIT',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=True,
  install_requires=requires,
  tests_require=test_requires,
)
