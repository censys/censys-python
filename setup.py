import os
from setuptools import setup, find_packages

import censys

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='censys',
    version=censys.__version__,
    description='Python library for interacting with Censys Search Engine (censys.io)',
    long_description='Python library for interacting with Censys Search Engine (censys.io)',
    classifiers=[
        "Programming Language :: Python",
    ],
    author=censys.__author__,
    author_email=censys.__email__,
    license=censys.__license__,
    url='https://github.com/censys/censys-python',
    keywords='censys',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "requests",
        "netaddr"
    ],
    entry_points={
        'console_scripts': [
            'censys = censys.__main__:main',
        ]
    }
)
