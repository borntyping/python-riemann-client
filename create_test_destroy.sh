#!/bin/bash

echo 'creating virtual env'
virtualenv tests
source tests/bin/activate
pip install pytest
echo 'installing riemann_client'
pip install -e .
echo 'running tests'
py.test tests
echo ''
echo 'destroying virtualenv'
rm -fr tests
