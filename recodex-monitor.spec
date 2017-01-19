%define name recodex-monitor
%define version 1.0.0
%define unmangled_version 1.0.0
%define unmangled_version 1.0.0
%define release 1

Summary: Publish ZeroMQ messages through WebSockets
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Petr Stefan <UNKNOWN>
Url: https://github.com/ReCodEx/monitor

%description
UNKNOWN

%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%post
#!/bin/sh

CONF_DIR=/etc/recodex
LOG_DIR=/var/log/recodex

# Create 'recodex' user if not exist
id -u recodex > /dev/null 2>&1
if [ $? -eq 1 ]
then
	useradd --system --shell /sbin/nologin recodex
fi

# Create default logging directory and set proper permission
mkdir -p ${LOG_DIR}
chown -R recodex:recodex ${LOG_DIR}

# Change owner of config files
chown -R recodex:recodex ${CONF_DIR}



%files -f INSTALLED_FILES
%defattr(-,root,root)
