specfile=python-riemann-client.spec

name=python-riemann-client
version=$(shell python setup.py --version)
release=$(shell grep Release ${specfile} | awk '{ print $$2 }')

package_name=${name}-${version}-${release}.noarch.rpm
package=dist/${package_name}
tarball=${HOME}/rpmbuild/SOURCES/${name}-${version}.tar.gz

${package}: ${specfile} ${tarball}
	rpmbuild -ba ${specfile}
	mkdir -p dist
	cp ${HOME}/rpmbuild/RPMS/noarch/${package_name} dist/${package_name}

${specfile}:

${tarball}:
	tar -zcf ${tarball} . --exclude-vcs --transform='s/./${name}-${version}/'

test: ${package}
	rpm -qpl ${package} | grep /usr/bin/riemann-client
	rpm -qpl ${package} | grep riemann_client/client.py
	rpm -qpl ${package} | grep README.rst

.PHONY: rpm test test_%
.SILENT: test test_%
