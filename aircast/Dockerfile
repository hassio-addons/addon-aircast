ARG BUILD_FROM=hassioaddons/ubuntu-base:5.2.2
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Setup base system
RUN \
    apt-get update \
    \
    && apt-get install -y --no-install-recommends \
        libssl1.0.0=1.0.2n-1ubuntu5.4 \
    \
    && rm -fr \
        /tmp/* \
        /var/{cache,log}/* \
        /var/lib/apt/lists/*

# Copy root filesystem
COPY rootfs /

# Add aircast binary
ARG BUILD_ARCH=amd64
COPY bin/aircast-${BUILD_ARCH} /usr/bin/aircast

# Build arguments
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="AirCast" \
    io.hass.description="AirPlay capabilities for your Chromecast devices" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Franck Nijhof <frenck@addons.community>" \
    org.opencontainers.image.title="AirCast" \
    org.opencontainers.image.description="AirPlay capabilities for your Chromecast devices" \
    org.opencontainers.image.vendor="Home Assistant Community Add-ons" \
    org.opencontainers.image.authors="Franck Nijhof <frenck@addons.community>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://addons.community" \
    org.opencontainers.image.source="https://github.com/hassio-addons/addon-aircast" \
    org.opencontainers.image.documentation="https://github.com/hassio-addons/addon-aircast/blob/master/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
