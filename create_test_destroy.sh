#!/bin/bash

echo 'creating virtual env'
virtualenv tests
source tests/bin/activate
echo 'installing riemann_client'
python setup.py install
echo 'running tests'
py.test
echo ''
echo 'destroying virtualenv'
rm -fr tests
