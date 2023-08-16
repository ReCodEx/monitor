%define name recodex-monitor
%define short_name monitor
%define version 1.1.1
%define unmangled_version 17032a170de28fd0a45d603f179dfcee89efaba7
%define release 1

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
%{?fedora:BuildRequires: python3 python3-devel python3-setuptools}
%{?rhel:BuildRequires: python3 python3-devel python3-setuptools}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%{?fedora:Requires: python3-PyYAML python3-websockets python3-zmq}
%{?rhel:Requires: python3-PyYAML}

Source0: https://github.com/ReCodEx/%{short_name}/archive/%{unmangled_version}.tar.gz#/%{short_name}-%{unmangled_version}.tar.gz

%description
Monitor is a proxying component that channels zeromq messages into websocket. It is a part of ReCodEx code examiner, an educational application for evaluating programming assignments.

%prep
%setup -n %{short_name}-%{unmangled_version}

%build
%py3_build

%install
%py3_install
mkdir -p %{buildroot}/var/log/recodex

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group recodex >/dev/null || groupadd -r recodex
getent passwd recodex >/dev/null || useradd -r -g recodex -d %{_sysconfdir}/recodex -s /sbin/nologin -c "ReCodEx Code Examiner" recodex
exit 0

%post
%if 0%{?rhel}
	pip3 install websockets zmq
%endif
%systemd_post 'recodex-monitor.service'

%preun
%systemd_preun 'recodex-monitor.service'

%postun
%systemd_postun_with_restart 'recodex-monitor.service'

%files
%defattr(-,root,root)
%dir %attr(-,recodex,recodex) %{_sysconfdir}/recodex/monitor
%dir %attr(-,recodex,recodex) /var/log/recodex

%{python3_sitelib}/monitor/
%{python3_sitelib}/recodex_monitor-%{version}-py?.?.egg-info/
%{_bindir}/recodex-monitor
%config(noreplace) %attr(0600,recodex,recodex) %{_sysconfdir}/recodex/monitor/config.yml
/lib/systemd/system/recodex-monitor.service

