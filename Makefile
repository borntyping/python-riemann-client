# Uses fpm (https://github.com/jordansissel/fpm) to build RPMs

vendor="Sam Clements <sam.clements@datasift.com>"

define fpm
	@mkdir -p dist
	fpm -s python -t rpm --package $@ --vendor ${vendor} --epoch 1
endef


default:
	@echo "Usage:"
	@echo "  make riemann-client - build generic riemann-client RPM"
	@echo "  make el6 - build CentOS 6 riemann-client RPM"
	@echo "  make el5 - build CentOS 5 riemann-client and protobuf RPM"


version=$(shell python setup.py --version)
release=4

riemann-client: dist/python-riemann-client-${version}-${release}.noarch.rpm

dist/python-riemann-client-${version}-${release}.noarch.rpm:
	${fpm} --iteration ${release} --version ${version} setup.py


el5: riemann-client.el5 protobuf.el5

riemann-client.el5: dist/python26-riemann-client-${version}-${release}.el5.noarch.rpm

dist/python26-riemann-client-${version}-${release}.el5.noarch.rpm:
	${fpm} --version ${version} --iteration ${release}.el5 \
	--python-bin python2.6 \
	--python-package-name-prefix python26 \
	setup.py

protobuf_version=2.5.0
protobuf_release=2

protobuf.el5: dist/python26-protobuf-${protobuf_version}-${protobuf_release}.el5.noarch.rpm

dist/python26-protobuf-${protobuf_version}-${protobuf_release}.el5.noarch.rpm:
	${fpm} --version ${protobuf_version} --iteration ${protobuf_release}.el5 \
	--python-package-name-prefix python26 protobuf


el6: riemann-client.el6

riemann-client.el6: dist/python-riemann-client-${version}-${release}.el6.noarch.rpm

dist/python-riemann-client-${version}-${release}.el6.noarch.rpm:
	${fpm} --iteration ${release}.el6 --version ${version} \
	--python-bin python2.6 \
	--no-python-dependencies \
	--depends 'python-argparse >= 1.1' \
	--depends 'protobuf-python >= 2.3.0' \
	setup.py


.PHONY: default riemann-client el5 riemann-client.el5 protobuf.el5 el6 riemann-client.el6
