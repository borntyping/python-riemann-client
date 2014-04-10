%define version %(python setup.py --version)

Name: python-riemann-client
Version: %{version}
Release: 1

Group: Development/Libraries
Url: https://github.com/borntyping/python-riemann-client
Summary: A Riemann client and command line tool
Vendor: Sam Clements <sam.clements@datasift.com>
License: MIT

Source0: %{name}-%{version}.tar.gz

Requires: python
Requires: python-argparse
Requires: protobuf-python
BuildRequires: python-setuptools

BuildArch: noarch


%description
A Riemann client library and command line tool for Python.

https://github.com/borntyping/python-riemann-client

%prep
%setup -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --no-compile --skip-build --root=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README.rst LICENSE
%{_bindir}/riemann-client
%{python_sitelib}/*
