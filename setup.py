import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
  name='censys',
  version='0.0.0',
  description='Python library for interacting with Censys Search Engine (censys.io)',
  long_description=open(os.path.join(here, 'README.md')).read(),
  classifiers=[
    "Programming Language :: Python",
  ],
  author='Censys Team',
  author_email='team@censys.io',
  url='https://github.com/censys/censys-python',
  keywords='censys',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires = [
    "requests"
  ],
  entry_points = {
    'console_scripts': [
        'censys = censys.__main__:main',
    ]
  }
)
