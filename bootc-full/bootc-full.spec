# This metadata goes unused.
# We are just reusing the .spec file format
# as a way to declare requirements basically.
# Note that everything here must be BuildRequires as
# we use `dnf builddep` to install things.
Name:           fedora-bootc-full
Version:        0
Release:        0
Summary:        Base image
License:        ASL 2.0

# We carry this in the full image for now
BuildRequires: rpm-ostree

# linux-firmware now a recommends so let's explicitly include it
# https://gitlab.com/cki-project/kernel-ark/-/commit/32271d0cd9bd52d386eb35497c4876a8f041f70b
# https://src.fedoraproject.org/rpms/kernel/c/f55c3e9ed8605ff28cb9a922efbab1055947e213?branch=rawhide
BuildRequires: linux-firmware
# If you're using linux-firmware, you probably also want fwupd
BuildRequires: fwupd

# Networking
# Standard tools for configuring network/hostname
BuildRequires: NetworkManager hostname
# Interactive Networking configuration during coreos-install
BuildRequires: NetworkManager-tui
# Teaming https://github.com/coreos/fedora-coreos-config/pull/289
# and http://bugzilla.redhat.com/1758162
BuildRequires: NetworkManager-team teamd
# Support for cloud quirks and dynamic config in real rootfs:
# https://github.com/coreos/fedora-coreos-tracker/issues/320
BuildRequires: NetworkManager-cloud-setup
# Route manipulation and QoS
BuildRequires: iproute iproute-tc
# Firewall manipulation
BuildRequires: iptables nftables
# Interactive network tools for admins
BuildRequires: socat net-tools bind-utils

# Podman
BuildRequires: crun
BuildRequires: podman
BuildRequires: container-selinux
BuildRequires: skopeo

# Packaging
BuildRequires: dnf

# These are packages that are related to configuring parts of the system.
# Configuring SSH keys, cloud provider check-in, etc
# TODO: needs Ignition kargs
# - afterburn afterburn-dracut
# NTP support
BuildRequires: chrony
# Storage configuration/management
BuildRequires: lvm2 cryptsetup e2fsprogs sg3_utils xfsprogs
## This is generally useful... https://github.com/CentOS/centos-bootc/issues/394
BuildRequires: cloud-utils-growpart
# User configuration
BuildRequires: passwd shadow-utils acl
# Manipulating the kernel keyring; used by bootc
BuildRequires: keyutils
# There are things that write outside of the journal still (such as the
# classic wtmp, etc.). auditd also writes outside the journal but it has its
# own log rotation.
# Anything package layered will also tend to expect files dropped in
# /etc/logrotate.d to work. Really, this is a legacy thing, but if we don't
# have it then people's disks will slowly fill up with logs.
BuildRequires: logrotate
# Boost starving threads
# https://github.com/coreos/fedora-coreos-tracker/issues/753
BuildRequires: stalld

# These packages are either widely used utilities/services or
# are targeted for improving the general user experience.
# Basic user tools
BuildRequires: jq
BuildRequires: bash-completion coreutils file less
# Authorization
BuildRequires: sudo
# Intended to be part of baseline RHEL-derived operating systems
BuildRequires: sos
# File compression/decompression
## bsdtar - dependency of 35coreos-live dracut module
BuildRequires: bsdtar bzip2 gzip tar xz zstd
# kdump support
# https://github.com/coreos/fedora-coreos-tracker/issues/622
BuildRequires: kexec-tools
# Remote Access
BuildRequires: openssh-clients openssh-server
# for managing nvme disks
BuildRequires: nvme-cli

# Generic default packages
# Include and set the default editor
BuildRequires: nano
BuildRequires: nfs-utils
# Additional firewall support; we aren't including these in RHCOS or they
# don't exist in RHEL
BuildRequires: iptables-nft iptables-services
BuildRequires: WALinuxAgent-udev
# Allow communication between sudo and SSSD
# for caching sudo rules by SSSD.
# https://github.com/coreos/fedora-coreos-tracker/issues/445
BuildRequires: libsss_sudo
# SSSD; we only ship a subset of the backends
BuildRequires: sssd-client sssd-ad sssd-ipa sssd-krb5 sssd-ldap
# Used by admins interactively
BuildRequires: attr
BuildRequires: openssl
BuildRequires: lsof
# Provides terminal tools like clear, reset, tput, and tset
BuildRequires: ncurses
# i18n
BuildRequires: kbd
# zram-generator (but not zram-generator-defaults) for F33 change
# https://github.com/coreos/fedora-coreos-tracker/issues/509
BuildRequires: zram-generator
%if 0%{?rhel} >= 11
BuildRequires: systemd-resolved
%endif

%ifarch x86_64 ppc64le aarch64
BuildRequires: irqbalance
%endif
%ifarch ppc64le
BuildRequires: librtas
BuildRequires: powerpc-utils-core
BuildRequires: ppc64-diag-rtas
%endif

%description
%{summary}
