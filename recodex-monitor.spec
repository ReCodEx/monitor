%define name recodex-monitor
%define short_name monitor
%define version 1.0.1
%define unmangled_version 2464f987fec22833d468faa61caba416f13402d4
%define release 4

Summary: Publish ZeroMQ messages through WebSockets
Name: %{name}
Version: %{version}
Release: %{release}
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Petr Stefan <UNKNOWN>
Url: https://github.com/ReCodEx/monitor

BuildRequires: systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%if 0%{?fedora}
BuildRequires: python3 python3-devel python3-setuptools python3-pip
%endif


Source0: https://github.com/ReCodEx/%{short_name}/archive/%{unmangled_version}.tar.gz#/%{short_name}-%{unmangled_version}.tar.gz

%description
ReCodEx monitor for proxying zeromq messages to websocket channels

%prep
%setup -n %{short_name}-%{unmangled_version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post 'recodex-monitor.service'

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


%preun
%systemd_preun 'recodex-monitor.service'

%postun
%systemd_postun_with_restart 'recodex-monitor.service'

%files
%defattr(-,root,root)
%{python_sitelib}/*
%config(noreplace) %attr(-,recodex,recodex) %{_sysconfdir}/recodex/monitor/config.yml
/lib/systemd/system/recodex-monitor.service

