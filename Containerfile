# This container build uses some special features of podman that allow
# a process executing as part of a container build to generate a new container
# image "from scratch".
#
# This container build uses nested containerization, so you must build with e.g.
# podman build --security-opt=label=disable --cap-add=all --device /dev/fuse <...>
#
# # Why are we doing this?
#
# Today this base image build process uses rpm-ostree.  There is a lot of things that
# rpm-ostree does when generating a container image...but important parts include:
#
# - auto-updating labels in the container metadata
# - Generating "chunked" content-addressed reproducible image layers (notice
#   how there are ~60 layers in the generated image)
#
# The latter bit in particular is currently impossible to do from Containerfile.
# A future goal is adding some support for this in a way that can be honored by
# buildah (xref https://github.com/containers/podman/discussions/12605)
#
# # Why does this build process require additional privileges?
#
# Because it's generating a base image and uses containerization features itself.
# In the future some of this can be lifted.

FROM quay.io/fedora/fedora:40 as builder
RUN --mount=type=cache,target=/var/cache/dnf,z dnf -y install rpm-ostree selinux-policy-targeted && dnf clean all
COPY . /src
WORKDIR /src
# Copy in repos, and a brutal hack to extract the $releasever, because rpm-ostree always wants to try
# to do cross builds and have the value initialized statically.
RUN cp /etc/yum.repos.d/*.repo . && \
    releasever=$(rpm -q --provides fedora-release-container | grep -Ee 'system-release\(' | sed -e 's/.*(\([0-9]\+\)).*/\1/'); \
    echo "releasever: ${releasever}" >> releasever.yaml
ARG VARIANT=full
RUN --mount=type=cache,target=/workdir --mount=type=bind,rw=true,src=.,dst=/buildcontext,bind-propagation=shared \
    rpm-ostree compose image --cachedir=/workdir --format=ociarchive --initialize fedora-bootc-${VARIANT}.yaml /buildcontext/out.ociarchive

FROM oci-archive:./out.ociarchive
# Need to reference builder here to force ordering. But since we have to run
# something anyway, we might as well cleanup after ourselves.
RUN --mount=type=bind,from=builder,src=.,target=/var/tmp --mount=type=bind,rw=true,src=.,dst=/buildcontext,bind-propagation=shared rm /buildcontext/out.ociarchive
