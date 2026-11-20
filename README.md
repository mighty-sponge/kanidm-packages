# kanidm-packages

[Kanidm](https://github.com/kanidm/kanidm) packages built from upstream tags in GitHub Actions:

- RPMs for EL9 (AlmaLinux 9)
- debs for Ubuntu 24.04 (noble) and Debian 13 (trixie)

openSUSE OBS `network:idm` publishes only one (often outdated) build for CentOS Stream 9 and drops
old builds, and the upstream `kanidm_ppa` lags behind releases. This repo builds the chosen upstream
tag for every OS and keeps every version as a GitHub release.

## RPM (EL9)

`kanidm.spec` is trimmed from the OBS spec: same package names and file layout, so they upgrade OBS
installs in place.

| Package | Content |
|---|---|
| `kanidm-server` | `kanidmd`, `kanidm-ipa-sync`, `kanidm-ldap-sync`, web UI, `kanidmd.service` |
| `kanidm-clients` | `kanidm` CLI |
| `kanidm-unixd-clients` | `kanidm_unixd`, `kanidm_unixd_tasks`, `kanidm-unix`, `kanidm_ssh_authorizedkeys`, NSS and PAM modules, units |
| `kanidm` | meta package (clients + unixd-clients) |

Built with `KANIDM_BUILD_PROFILE=release_linux` (x86-64-v2 baseline) and the `selinux` feature of
the unix integration, without debuginfo.

## deb (Ubuntu 24.04, Debian 13)

Built with the upstream PPA scripts ([kanidm/kanidm_ppa_automation](https://github.com/kanidm/kanidm_ppa_automation),
pinned by commit in the workflow) and the `cargo-deb` metadata of `kanidm/kanidm`: the same
packages as the upstream PPA (`kanidm`, `kanidm-unixd`, `libnss-kanidm`, `libpam-kanidm`,
`kanidmd`). The only change is the version: `<version>-<release>~<codename>` instead of the commit
date, e.g. `1.12.1-1~noble`.

`kanidm-unixd` depends on `libnss-kanidm` and `libpam-kanidm` of exactly the same version, so
install the three together.

## Releasing a version

Push a tag `v<upstream version>-<package release>`:

```sh
git tag v1.12.1-1 && git push origin v1.12.1-1
```

The workflow builds all packages and attaches them to a release with the same name:

```
kanidm-unixd-clients-1.12.1-1.el9.x86_64.rpm
kanidm-unixd_1.12.1-1.noble_amd64.deb      # package version 1.12.1-1~noble
kanidm-unixd_1.12.1-1.trixie_amd64.deb     # package version 1.12.1-1~trixie
...
```

GitHub does not allow `~` in asset names, so deb files are named with `.` before the codename; the
version inside the package keeps `~`. A manual run (`workflow_dispatch`) only builds and uploads the
packages as workflow artifacts.

Kanidm servers must be upgraded one minor version at a time, and clients should stay within the
supported window of the server version.

## Installing

```sh
# EL9
base=https://github.com/mighty-sponge/kanidm-packages/releases/download/v1.12.1-1
dnf install $base/kanidm-unixd-clients-1.12.1-1.el9.x86_64.rpm $base/kanidm-clients-1.12.1-1.el9.x86_64.rpm

# Ubuntu 24.04: download the debs, then
apt install ./kanidm_1.12.1-1.noble_amd64.deb ./kanidm-unixd_1.12.1-1.noble_amd64.deb \
            ./libnss-kanidm_1.12.1-1.noble_amd64.deb ./libpam-kanidm_1.12.1-1.noble_amd64.deb
```

Runtime dependencies come from the distribution repos.
