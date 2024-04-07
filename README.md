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
