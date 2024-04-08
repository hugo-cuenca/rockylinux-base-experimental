# Base bootc images for Fedora

## Motivation

The original Docker container model of using "layers" to model
applications has been extremely successful.  This project
aims to apply the same technique for bootable host systems - using
standard OCI/Docker containers as a transport and delivery format
for base operating system updates.

## More information on bootc

See: <https://containers.github.io/bootc/>

## Images

At present there are two images:

### `full`

This image is a fairly large, generic base image that can
be deployed in cloud or bare metal (e.g. it has full `linux-firmware` etc.)

### `minimal`

This image has just effectively:

- `podman systemd kernel bootc`

And represents a smaller target reference image.


## Building

At the current time, the `Containerfile` *requires* podman or buildah; it will not build with docker
or other container build systems that don't inherit from [containers/storage](https://github.com/containers/storage/).

```shell
podman build --security-opt=label=disable --cap-add=all -t localhost/fedora-bootc:40 .
```

The default uses Fedora 40; to generate e.g. Fedora rawhide content, use

```shell
podman build --from=quay.io/fedora/fedora:rawhide --security-opt=label=disable --cap-add=all -t localhost/fedora-bootc:rawhide .
```

etc.

For more about how the build system came to be, see [README-build-rationale.md](README-build-rationale.md).

## Extending/deriving

The implementation details of this container are *definitely* subject to change.

If you want to make a custom image, one recommendation is to include this project
as a [git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

Then, you could create a copy of the `Containerfile`, and insert the logic you desire
in between the different phases.

Again: all details of this container such as the executable scripts, the location of
`/workdir/rootfs` etc. are subject to change; however, a best effort will be
made to avoid "silent" incompatible changes.  For example, if a script changes
semantics, it will change name.

### Adding some packages

There's an example in the `Containerfile`, but just for reference this is e.g.:

```dockerfile
RUN --mount=type=cache,target=/workdir /src/build/dnf-installroot /workdir/rootfs install -y vim
```

Or feel free to use `install-imagedir` to support installing a full `.spec` file of dependencies.

### Adding arbitrary content, making arbitrary changes

The `/workdir/rootfs` is the target directory.  You can install whatever tools you desire
in the `builder` container, and manipulate the target root.  For example, run e.g.
```
RUN dnf -y install tree && tree /workdir/rootfs
```
to inspect the filesystem (verbosely).  Or run a permissions checker, etc.
