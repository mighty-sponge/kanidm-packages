# EL9 build of Kanidm, trimmed from the openSUSE OBS spec (network:idm/kanidm).
# Package names and file layout are kept identical to the OBS packages so they upgrade in place.
# Version and release are passed by the workflow: --define "pkgver 1.10.5" --define "pkgrel 1"

%global debug_package %{nil}
%define kanidm_profile release_linux
%define configdir %{_sysconfdir}/kanidm

Name:           kanidm
Version:        %{pkgver}
Release:        %{pkgrel}%{?dist}
Summary:        A identity management service and clients.
License:        MPL-2.0
URL:            https://github.com/kanidm/kanidm
Source0:        https://github.com/kanidm/kanidm/archive/refs/tags/v%{version}.tar.gz#/kanidm-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  clang
BuildRequires:  libselinux-devel
BuildRequires:  systemd-devel
BuildRequires:  pam-devel
BuildRequires:  rust >= 1.93.0
BuildRequires:  sqlite-devel
BuildRequires:  tpm2-tss-devel
BuildRequires:  openssl-devel
BuildRequires:  systemd
BuildRequires:  systemd-rpm-macros
%{?systemd_requires}

Requires:       %{name}-clients
Requires:       %{name}-unixd-clients

ExclusiveArch:  x86_64

%description
An identity management platform written in rust that supports RADIUS, SSH Key management
and more.

%package clients
Summary:        Client tools for interacting with Kanidm
License:        MPL-2.0

%description clients
Client utilities for interactive with kanidm servers

%package server
Summary:        Kanidm server and related tools
License:        MPL-2.0
Requires:       %{name}-clients

%description server
Server for kanidm providing the main authentication and identity service

%package unixd-clients
Summary:        Client nsswitch/pam/ssh integration for consuming kanidm
License:        MPL-2.0
Requires:       %{name}-clients
Requires:       tpm2-tools
Requires:       tpm2-tss

%description unixd-clients
A localhost resolver and libraries that allow a system to resolve posix
identities to a kanidm instance.

%prep
%setup -q -n kanidm-%{version}

%build
export KANIDM_BUILD_PROFILE=%{kanidm_profile}
export CARGO_INCREMENTAL=0
# no debuginfo in the release profile, strip symbols: packages stay small
export CARGO_PROFILE_RELEASE_DEBUG=false
export CARGO_PROFILE_RELEASE_STRIP=symbols
export RUSTFLAGS="-Clink-arg=-Wl,-z,relro,-z,now"
cargo build --release --features=kanidm_unix_int/selinux

%install
install -D -d -m 0755 %{buildroot}%{_sysconfdir}/zsh_completion.d
install -D -d -m 0755 %{buildroot}%{_sysconfdir}/bash_completion.d
install -D -d -m 0755 %{buildroot}%{configdir}
install -D -d -m 0755 %{buildroot}%{_unitdir}
install -D -d -m 0755 %{buildroot}%{_sbindir}
install -D -d -m 0755 %{buildroot}%{_bindir}
install -D -d -m 0755 %{buildroot}%{_libdir}
install -D -d -m 0755 %{buildroot}/%{_lib}/security
install -D -d -m 0755 %{buildroot}%{_datadir}/kanidm/ui

T=target/release
install -m 0755 $T/kanidmd %{buildroot}%{_sbindir}/kanidmd
install -m 0755 $T/kanidm %{buildroot}%{_bindir}/kanidm
install -m 0755 $T/kanidm-ipa-sync %{buildroot}%{_sbindir}/kanidm-ipa-sync
install -m 0755 $T/kanidm-ldap-sync %{buildroot}%{_sbindir}/kanidm-ldap-sync
install -m 0755 $T/kanidm-unix %{buildroot}%{_sbindir}/kanidm-unix
install -m 0755 $T/kanidm_ssh_authorizedkeys %{buildroot}%{_sbindir}/kanidm_ssh_authorizedkeys
install -m 0755 $T/kanidm_ssh_authorizedkeys_direct %{buildroot}%{_sbindir}/kanidm_ssh_authorizedkeys_direct
install -m 0755 $T/kanidm_unixd %{buildroot}%{_sbindir}/kanidm_unixd
install -m 0755 $T/kanidm_unixd_tasks %{buildroot}%{_sbindir}/kanidm_unixd_tasks
install -m 0644 $T/libnss_kanidm.so %{buildroot}%{_libdir}/libnss_kanidm.so.2
install -m 0644 $T/libpam_kanidm.so %{buildroot}/%{_lib}/security/pam_kanidm.so

install -m 0644 platform/opensuse/kanidmd.service %{buildroot}%{_unitdir}/kanidmd.service
install -m 0644 platform/opensuse/kanidm-unixd.service %{buildroot}%{_unitdir}/kanidm-unixd.service
install -m 0644 platform/opensuse/kanidm-unixd-tasks.service %{buildroot}%{_unitdir}/kanidm-unixd-tasks.service
install -m 0644 platform/opensuse/kanidm-ipa-sync.service %{buildroot}%{_unitdir}/kanidm-ipa-sync.service
install -m 0644 examples/server.toml %{buildroot}%{configdir}/server.toml

C=$T/build/completions
for c in _kanidmd _kanidm _kanidm_ssh_authorizedkeys_direct _kanidm_unix _kanidm_ssh_authorizedkeys; do
  install -m 0755 $C/$c %{buildroot}%{_sysconfdir}/zsh_completion.d/$c
done
for c in kanidmd kanidm kanidm_ssh_authorizedkeys_direct kanidm_unix kanidm_ssh_authorizedkeys; do
  install -m 0755 $C/$c.bash %{buildroot}%{_sysconfdir}/bash_completion.d/$c.sh
done

cp -r server/core/static %{buildroot}%{_datadir}/kanidm/ui/hpkg

%files
%defattr(-,root,root)

%files clients
%defattr(-,root,root)
%dir %{configdir}
%{_bindir}/kanidm
%dir %{_sysconfdir}/zsh_completion.d
%dir %{_sysconfdir}/bash_completion.d
%{_sysconfdir}/zsh_completion.d/_kanidm
%{_sysconfdir}/bash_completion.d/kanidm.sh

%files server
%{_sbindir}/kanidmd
%{_sbindir}/kanidm-ipa-sync
%{_sbindir}/kanidm-ldap-sync
%{_unitdir}/kanidmd.service
%{_unitdir}/kanidm-ipa-sync.service
%dir %{_datadir}/kanidm
%dir %{_datadir}/kanidm/ui
%{_datadir}/kanidm/ui/hpkg
%dir %{configdir}
%config(noreplace) %{configdir}/server.toml
%dir %{_sysconfdir}/zsh_completion.d
%dir %{_sysconfdir}/bash_completion.d
%{_sysconfdir}/zsh_completion.d/_kanidmd
%{_sysconfdir}/bash_completion.d/kanidmd.sh

%files unixd-clients
%{_libdir}/libnss_kanidm.so.2
/%{_lib}/security/pam_kanidm.so
%{_sbindir}/kanidm-unix
%{_sbindir}/kanidm_ssh_authorizedkeys
%{_sbindir}/kanidm_ssh_authorizedkeys_direct
%{_sbindir}/kanidm_unixd
%{_sbindir}/kanidm_unixd_tasks
%{_unitdir}/kanidm-unixd.service
%{_unitdir}/kanidm-unixd-tasks.service
%dir %{_sysconfdir}/zsh_completion.d
%dir %{_sysconfdir}/bash_completion.d
%{_sysconfdir}/zsh_completion.d/_kanidm_ssh_authorizedkeys_direct
%{_sysconfdir}/zsh_completion.d/_kanidm_ssh_authorizedkeys
%{_sysconfdir}/zsh_completion.d/_kanidm_unix
%{_sysconfdir}/bash_completion.d/kanidm_ssh_authorizedkeys_direct.sh
%{_sysconfdir}/bash_completion.d/kanidm_ssh_authorizedkeys.sh
%{_sysconfdir}/bash_completion.d/kanidm_unix.sh

%changelog
* Fri Nov 20 2026 Kirill Shklyaev - 1.10.5-1
- EL9 build from upstream tags, spec trimmed from openSUSE OBS network:idm/kanidm
