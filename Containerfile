# This container build uses some special features of podman that allow
# a process executing as part of a container build to generate a new container
# image "from scratch".
#
# This container build uses nested containerization, so you must build with e.g.
# podman build --security-opt=label=disable --cap-add=all <...>
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
# Install tools we will use to build
RUN --mount=type=cache,target=/var/cache/dnf,z dnf -y install golang rpm-ostree selinux-policy-targeted jq dnf-utils rsync
# Copy in the source
COPY . /src
ARG VARIANT=full
RUN /src/build/check-environment
# Populate the initial rootfs directory; the /workdir is a temporary volume defined to not be on overlayfs
# so that we can e.g. set SELinux labels and file capabilities
RUN --mount=type=cache,target=/var/cache/dnf,z --mount=type=cache,target=/workdir rm -rf /workdir/rootfs && /src/build/install-imagedir /src/bootc-${VARIANT} /workdir/rootfs

# Insert arbitrary other code here, if desired.  If convenient, you can use the /src/build/install-imagedir entrypoint.
# RUN --mount=type=cache,target=/workdir <your code here>

# Significant postprocessing, such as generating the initramfs, fixing up SELinux
# location.
RUN --mount=type=cache,target=/workdir /src/build/postprocess-rootfs /workdir/rootfs

# Final place to execute arbitrary code on the target root before we commit it as a container
# RUN --mount=type=cache,target=/workdir <your code here>

# Finally, generate an OCI archive from this.  This uses rpm-ostree to generate a
# "chunked" image with SELinux labels set up, timestamps squashed to zero, etc.
RUN --mount=type=cache,target=/workdir --mount=type=bind,rw=true,src=.,dst=/buildcontext,bind-propagation=shared /src/build/generate-oci /workdir /workdir/rootfs /buildcontext/out.ociarchive

# This magical bit extends the oci-archive (tar) file generated in the build stage.
FROM oci-archive:./out.ociarchive
# Need to reference builder here to force ordering. But since we have to run
# something anyway, we might as well cleanup after ourselves.
RUN --mount=type=bind,from=builder,src=.,target=/var/tmp --mount=type=bind,rw=true,src=.,dst=/buildcontext,bind-propagation=shared rm /buildcontext/out.ociarchive
# And configure metadata
LABEL containers.bootc=1
LABEL redhat.id=fedora
STOPSIGNAL SIGRTMIN+3
CMD /sbin/init
