# This metadata goes unused.
# We are just reusing the .spec file format
# as a way to declare requirements basically.
# Note that everything here must be BuildRequires as
# we use `dnf builddep` to install things.
Name:           fedora-bootc
Version:        0
Release:        0
Summary:        Base image
License:        ASL 2.0

# NOTE! This magical comment is interpreted to pass `--setopt=install_weak_deps=0` to dnf
# Recommends: false

# Basic components
BuildRequires: systemd bootc kernel
# Requirements for container self-install (bootc install)
BuildRequires: gdisk xfsprogs e2fsprogs dosfstools
# And ostree
BuildRequires: ostree nss-altfiles

# SELinux
BuildRequires: selinux-policy-targeted container-selinux

# Enable TPM integration
BuildRequires: tpm2-tools

# Integration with https://github.com/coreos/bootupd and bootloader logic
# xref https://github.com/coreos/fedora-coreos-tracker/issues/510
BuildRequires: bootupd
# And the underlying bootloader
%ifarch s390x
BuildRequires: /usr/sbin/zipl
%endif
%ifarch x86_64 aarch64
# We use grub/shim by default
BuildRequires: efibootmgr shim
%endif
%ifarch x86_64
BuildRequires: grub2 grub2-efi-x64
# And ensure we get microcode updates
BuildRequires: microcode_ctl
%endif
%ifarch aarch64
BuildRequires: grub2-efi-aa64
%endif
%ifarch ppc64le
BuildRequires: grub2
%endif

%description
%{summary}
