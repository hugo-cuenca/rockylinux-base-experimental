# Build system rationale

There are a lot of build systems out there that can generate container images;
the "application base image" at quay.io/fedora/fedora:39 is derived from
a layer of things wrapping Anaconda+kickstart, etc.

As I like to say, OCI is just tarballs wrapped with JSON, so there are a *lot*
of things that do that.

However, there's also quite a lot of special sauce and historical stuff
involved in ostree-containers.

Some of these requirements will [eventually be lifted](https://github.com/containers/bootc/pull/215)
but today there's quite a bit of load-bearing stuff in rpm-ostree
in particular.

Even beyond the history, rpm-ostree also knows how to generate
[chunked images](https://coreos.github.io/rpm-ostree/container/#converting-ostree-commits-to-new-base-images)
which split up the RPM content into reproducible (timestamp squashed) chunks,
making updates a lot more efficient than ad-hoc layers.

## vs rpm-ostree

rpm-ostree is also a full end-to-end system, with a bespoke YAML format that is designed
around:

- Accepting primarily RPMs as input
- With support for arbitrary (but sandboxed!) postprocessing scripts that run in the middle
- That outputs an ostree commit or an ostree-container image

A few problems with this:

- The build system itself is not at all container native; e.g. including labels
  and metadata is awkward
- scripts intentionally can't access the network; non-RPM content requires some
  awkward external juggling
- It is not optimized for directly building an image into containers-storage
- The system is very opinionated in general; hacking on it is difficult
  (big mess of C++/Rust).  See e.g. https://github.com/coreos/rpm-ostree/issues/4893
  for an arbitrary limitation.
- Defining inputs (especially dnf/yum repository configuration) is bespoke
  (list of repos in YAML, separate .repo files)

In the longer term I'd like to deprecate the rpm-ostree build system.

## vs osbuild

The [osbuild/images](https://github.com/osbuild/images) project has also learned
how to output ostree-containers.  Its design really mirrors rpm-ostree in many ways:

- Big dichotomy between internal (Go code) vs external (blueprints)
- Accepting primarily RPMs as input
- Any "custom logic" requires adding a new "stage" into the upstream

Blueprints are OK but:

- No support for e.g. architecture or distribution conditionals, which are important
  for this project
- Very verbose in general with repeated `[[package]]` table

Both of these are solvable by templating, but at that point we're on a new
bespoke format.

And the problems are very similar:

- The build system itself is not at all container native
- It is not optimized for directly building an image into containers-storage,
  making it convenient to run/test and later push
- The system is very opinionated in general; hacking on it is (arguably)
  difficult for anyone unfamiliar with the architecture
- Defining inputs (especially dnf/yum repository configuration) is bespoke

## How this Containerfile and the `build/` directory came to be

The requirements are:

- Must feel container native
- Must also feel "dnf native"; in contrast to the above, the Containerfile
  has a `builder` image and we *directly* use the `/etc/yum.repos.d` from it.
- Must also grant a lot of power to the builder; e.g. pinning on a
  particular kernel version, removing or changing arbitrary package
  or other file content
- Must support fetching and injecting non-RPM content (if desired)

Overall goals:

- Avoid inventing any new file formats (especially for package lists)
- Be very hackable

### Key aspect: podman/buildah support for `FROM oci-archive:`

See <https://github.com/coreos/rpm-ostree/issues/4688> in which
we concluded that the support that landed in podman/buildah
for `FROM oci-archive` allows us to do a container build
in a container - this lets rpm-ostree generate "chunked" images.

But notice in the `Containerfile` that we can use the default
e.g. `LABEL` instructions etc. on the resulting image.

Right now, this requires some extra privileges so that
the build process can use container features itself
(mostly namespaces).

### Key aspect: `FROM <image> as builder`

As noted above, we don't try to define any new wrapper for dnf
repository configuration, gpg keys etc.

We just ultimately invoke `dnf --installroot`, which honors
the builder container's repository configuration.

### Key aspect: Reusing .spec files

First, it does work as part of the build process to do:

`RUN dnf --installroot=/workdir/rootfs install foo bar baz ...`

(Actually in order to properly set up e.g. `/proc` in the root
 we have a thin `dnf-installroot` wrapper)

But, beyond any kind of non-small scale, one desires a few things:

- Comments (next to the packages)
- Sane multi-line syntax
- A declarative file format so in theory other tools can parse
  it and know what will be installed

And as noted above we have stronger requirements:

- Architecture and distribution conditionals

There is an absolutely giant set of things that are declarative
wrappers for installing RPM packages; kickstart, blueprints, comps,
really a near-uncountable set of different YAML variants, etc.

After some thought and experimentation I decided to reuse `.spec`
files for this, because:

- It's an existing well-known format that anyone who has
  interacted with the RPM ecosystem has seen (for better or worse)
- It supports architecture/distribution conditionals

Note we don't actually *build* RPMs, we just reuse the `.spec` format
and evaluate the `BuildRequires:` for installation.

### Key aspect: "imagedir"

In a generalization beyond .spec files, there is the concept of an
"imagedir" which can contain a `.spec` file with packages, but also
other content.  See below:

#### `.post` files

The rpm-ostree YAML format that the content here was translated
from had a bunch of inline shell script in YAML, which was ugly.
So alongside `.spec` for lists of packages, a `.post` executable
script is run in a container in the target root.

#### `rootfs`

There is also support for a `rootfs` directory with inline
content that is merged into the root.  Some of the postprocess
YAML scripts were actually just synthesizing files, which was a
triple indirection (YAML, bash, file).  This drops out the
first two layers.

## Hackability

This project started out writing some of the build system in
Go, but in practice 90% of it ended up being just fork/exec
of external subprocesses, which was very verbose.

So I landed back on shell script for now.  Yes, I really
dislike shell script, but it does make the system feel
very hackable for now.

I'd be very happy to kill off some shell scripts
in favor of tooling in a proper language...but, what
exactly that is needs a lot of bikeshedding =)

Most importantly though there are clearly separated
phases, so if you just want to go and change
nearly any point in the build (including arbitrary
changes to the final rootfs) you can just go and
edit the scripts and `podman build` and get that
change, which is not at all true of rpm-ostree or osbuild.
