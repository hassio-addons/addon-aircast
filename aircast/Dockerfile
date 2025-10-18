ARG BUILD_FROM=ghcr.io/hassio-addons/debian-base:7.8.3
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy root filesystem
COPY rootfs /

# Setup base
ARG BUILD_ARCH=amd64
ARG AIRCAST_VERSION="1.9.1"
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        unzip=6.0-28 \
    \
    && curl -J -L -o /tmp/airconnect.zip \
      "https://github.com/philippe44/AirConnect/releases/download/${AIRCAST_VERSION}/AirConnect-${AIRCAST_VERSION}.zip" \
    && unzip -d /tmp /tmp/airconnect.zip \
    \
    && if [ "${BUILD_ARCH}" = "aarch64" ]; then AIRCONNECT_ARCH="aarch64"; \
    elif [ "${BUILD_ARCH}" = "amd64" ]; then AIRCONNECT_ARCH="x86_64"; \
    elif [ "${BUILD_ARCH}" = "armv7" ]; then AIRCONNECT_ARCH="arm"; fi \
    \
    && cp "/tmp/aircast-linux-${AIRCONNECT_ARCH}-static" /usr/bin/aircast \
    && chmod a+x /usr/bin/aircast \
    \
    && apt-get purge -y --auto-remove \
        unzip \
    && rm -fr \
        /tmp/* \
        /var/{cache,log}/* \
        /var/lib/apt/lists/*

# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Franck Nijhof <frenck@addons.community>" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Home Assistant Community Add-ons" \
    org.opencontainers.image.authors="Franck Nijhof <frenck@addons.community>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://addons.community" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
