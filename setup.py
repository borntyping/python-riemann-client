#!/usr/bin/env python2.6

import sys

import setuptools

if sys.version_info >= (3,):
    protobuf = 'protobuf>=3.2.0,<4.0.0'
else:
    protobuf = 'protobuf>=2.3.0,<4.0.0'

setuptools.setup(
    name='riemann-client',
    version='7.0.0pre1',

    author="Sam Clements",
    author_email="sam.clements@datasift.com",

    url="https://github.com/borntyping/python-riemann-client",
    description="A Riemann client and command line tool",
    long_description=open('README.rst').read(),
    license="MIT",

    packages=[
        'riemann_client',
    ],

    install_requires=[
        'click>=3.1',
        protobuf
    ],

    extras_require={
        'docs': [
            'sphinx',
            'sphinx_rtd_theme'
        ]
    },

    entry_points={
        'console_scripts': [
            'riemann-client = riemann_client.command:main',
        ]
    },

    classifiers=[
        'Development Status :: 7 - Inactive',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration'
    ],
)
