#!/usr/bin/env python
from codecs import open
from os import path
from os import linesep

import re
import subprocess

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

here = path.abspath(path.dirname(__file__))

def get_package_metadata(package, key):
  with open(path.join(here, package, '__init__.py'), 'rb') as init_py:
    src = init_py.read().decode('utf-8')
    return re.search("__" + key + "__ = ['\"]([^'\"]+)['\"]", src).group(1)

with open(path.join(here, 'README.md'), mode='r', encoding='utf-8') as f:
  long_description = f.read()

setup(
  name=get_package_metadata("craftai", "title"),
  version=get_package_metadata("craftai", "version"),

  description="craft ai API client for python",
  long_description=long_description,
  long_description_content_type="text/markdown",

  author=get_package_metadata("craftai", "author"),
  author_email="contact@craft.ai",
  url="https://github.com/craft-ai/craft-ai-client-python/",

  license=get_package_metadata("craftai", "license"),

  classifiers=[
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",

    # Should match "license" above)
    "License :: OSI Approved :: BSD License",

    # Python versions against which the code has been tested and is
    # actively supported.
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.5",
  ],
  keywords="ai craft-ai",

  packages=["craftai"],
  install_requires=[
    "requests~=2.20.1",
    "six~=1.10",
    "datetime~=4.1.1",
    "semver~=2.7.7",
    "tzlocal~=1.2.2",
    "python-dateutil~=2.7.2"
  ],
  extras_require = {
    "pandas_support":  [
      "pandas~=0.24.2"
    ],
    "sklearn_support": [
      "scikit-learn~=0.20.3"
    ]
  },

  include_package_data=True
)
