version=$(shell python setup.py --version)
release=$(shell grep Release python-riemann-client.spec | awk '{ print $$2 }')

package=python-riemann-client-${version}-${release}.noarch.rpm
tarball=${HOME}/rpmbuild/SOURCES/python-riemann-client-${version}.tar.gz

dist/${package}: python-riemann-client.spec ${tarball}
	rpmbuild -ba python-riemann-client.spec
	rsync -a ${HOME}/rpmbuild/RPMS/noarch/${package} dist/${package}

${tarball}: $(shell find riemann_client)
	tar -zcf ${tarball} . --exclude-vcs --transform='s/./python-riemann-client-${version}/'
