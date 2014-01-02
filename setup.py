#!/usr/bin/env python2.6

import setuptools
import sys

setuptools.setup(
    name = "riemann-client",
    version = '2.0.0',

    author = "Sam Clements",
    author_email = "sam.clements@datasift.com",

    url = "https://github.com/borntyping/python-riemann-client",
    description = "A Riemann client and command line tool",
    long_description = open('README.rst').read(),

    packages = setuptools.find_packages(),

    install_requires = [
        'argparse==1.2.1',
        'protobuf==2.5.0',
    ],

    entry_points = {
        'console_scripts': [
            'riemann-client = riemann.command:main',
            'riemann-client-{0}.{1} = riemann.command:main'.format(*sys.version_info)
        ]
    },

    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration'
    ],
)
