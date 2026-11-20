# kanidm-rpm

EL9 (AlmaLinux 9) RPMs of [Kanidm](https://github.com/kanidm/kanidm), built from upstream tags in
GitHub Actions.

openSUSE OBS `network:idm` publishes only one (often outdated) build for CentOS Stream 9 and drops
old builds, so pinned versions disappear. This repo builds the same packages from a chosen upstream
tag and keeps every version as a GitHub release.

## Packages

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

## Releasing a version

Push a tag `v<upstream version>-<package release>`:

```sh
git tag v1.10.5-1 && git push origin v1.10.5-1
```

The workflow builds `kanidm-*-1.10.5-1.el9.x86_64.rpm` and attaches them to a release with the same
name. A manual run (`workflow_dispatch`) only builds and uploads the RPMs as a workflow artifact.

Kanidm servers must be upgraded one minor version at a time, and clients should stay within the
supported window of the server version.

## Installing

```sh
dnf install https://github.com/mighty-sponge/kanidm-rpm/releases/download/v1.10.5-1/kanidm-unixd-clients-1.10.5-1.el9.x86_64.rpm \
            https://github.com/mighty-sponge/kanidm-rpm/releases/download/v1.10.5-1/kanidm-clients-1.10.5-1.el9.x86_64.rpm
```

Runtime dependencies (`tpm2-tss`, `tpm2-tools`, `sqlite`, `pam`) come from the AlmaLinux repos.
