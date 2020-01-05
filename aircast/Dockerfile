ARG BUILD_FROM=hassioaddons/ubuntu-base:4.0.3
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Setup base system
RUN \
    apt-get update \
    \
    && apt-get install -y --no-install-recommends \
        libssl1.0.0=1.0.2n-1ubuntu5.3 \
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
    org.label-schema.description="AirPlay capabilities for your Chromecast devices" \
    org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.name="AirCast" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.url="https://community.home-assistant.io/t/community-hass-io-add-on-aircast/36742?u=frenck" \
    org.label-schema.usage="https://github.com/hassio-addons/addon-aircast/tree/master/README.md" \
    org.label-schema.vcs-ref=${BUILD_REF} \
    org.label-schema.vcs-url="https://github.com/hassio-addons/addon-aircast" \
    org.label-schema.vendor="Community Hass.io Add-ons"
