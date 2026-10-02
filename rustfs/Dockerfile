# RustFS with the `rc` CLI baked in, so a single container can create its
# own bucket and set a public-read policy at startup — no init container,
# no sidecar, no manual post-boot step.
#
# See docs/adr/ (if present) for why RustFS was chosen over Garage/MinIO.
FROM rustfs/rustfs:1.0.0

# The base image already sets USER rustfs (non-root); switch back to root
# for the install steps below. We deliberately stay root for the server
# process too (like the old minio service effectively did) so the
# entrypoint's `mkdir -p "$DATA_DIR"` can always write to a bind-mounted
# host volume regardless of that host directory's ownership.
USER root

ARG RC_VERSION=v0.1.30
ARG TARGETARCH=amd64

# rustfs/rustfs ships only the `rustfs` server binary. `rc` is a separate
# project (github.com/rustfs/cli) distributed as release tarballs.
ADD https://github.com/rustfs/cli/releases/download/${RC_VERSION}/rustfs-cli-linux-${TARGETARCH}-${RC_VERSION}.tar.gz /tmp/rc.tar.gz
RUN tar -xzf /tmp/rc.tar.gz -C /tmp \
    && mv /tmp/rc /usr/local/bin/rc \
    && chmod +x /usr/local/bin/rc \
    && rm -rf /tmp/rc.tar.gz

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
