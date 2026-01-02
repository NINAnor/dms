FROM busybox:stable

COPY --from=minio/mc:latest /usr/bin/mc /usr/bin/mc

COPY ./setup.sh /usr/bin/setup-rustfs

CMD ["/usr/bin/setup-rustfs"]
