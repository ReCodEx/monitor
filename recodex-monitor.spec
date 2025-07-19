%define name recodex-monitor
%define short_name monitor
%define version 1.2.0
%define unmangled_version 56bfec2ffa5d4eff0d3b8b92bce3837175ca0b53
%define release 2

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
%{?fedora:BuildRequires: python3 python3-devel python3-setuptools python3-pip python3-wheel}
%{?rhel:BuildRequires: python3 python3-devel python3-setuptools python3-pip python3-wheel}
BuildRequires: python3dist(build)
BuildRequires: python3dist(setuptools) >= 61.0
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
# %{?fedora:Requires: python3-PyYAML python3-websockets python3-zmq}
# %{?rhel:Requires: python3-PyYAML python3-websockets python3-pyzmq}
Requires: python3-PyYAML python3-websockets python3-pyzmq

Source0: https://github.com/ReCodEx/%{short_name}/archive/%{unmangled_version}.tar.gz#/%{short_name}-%{unmangled_version}.tar.gz

%description
Monitor is a proxying component that channels zeromq messages into websocket. It is a part of ReCodEx code examiner, an educational application for evaluating programming assignments.

%prep
%setup -n %{short_name}-%{unmangled_version}

%build
# Build using modern Python build system with pyproject.toml
# This replaces the legacy setup.py build process
%{python3} -m build --wheel --no-isolation


%install
# Install the wheel using pip (modern approach)
%{python3} -m pip install --no-deps --no-index --find-links dist/ --root=%{buildroot} recodex-monitor

# Create log directory
mkdir -p %{buildroot}/var/log/recodex

# Install system files manually (these files are no longer installed automatically with pyproject.toml)
mkdir -p %{buildroot}/lib/systemd/system
mkdir -p %{buildroot}%{_sysconfdir}/recodex/monitor
install -m 644 monitor/install/recodex-monitor.service %{buildroot}/lib/systemd/system/
install -m 644 monitor/install/config.yml %{buildroot}%{_sysconfdir}/recodex/monitor/


%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group recodex >/dev/null || groupadd -r recodex
getent passwd recodex >/dev/null || useradd -r -g recodex -d %{_sysconfdir}/recodex -s /sbin/nologin -c "ReCodEx Code Examiner" recodex
exit 0

%post
#%if 0%{?rhel}
#	pip3 install websockets zmq
#%endif
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
%{python3_sitelib}/recodex_monitor-%{version}.dist-info/
%{_bindir}/recodex-monitor
%config(noreplace) %attr(0600,recodex,recodex) %{_sysconfdir}/recodex/monitor/config.yml
/lib/systemd/system/recodex-monitor.service

