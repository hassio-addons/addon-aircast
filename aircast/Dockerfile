ARG BUILD_FROM=ghcr.io/hassio-addons/debian-base:9.1.0
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy root filesystem
COPY rootfs /

# Setup base
ARG BUILD_ARCH=amd64
ARG AIRCAST_VERSION="1.9.3"
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        unzip=6.0-29 \
        python3=3.13.1-1 \
        python3-pip=24.3.1+dfsg-1 \
        python3-requests=2.32.3+dfsg-1 \
        ffmpeg=7:7.1-3 \
        build-essential=12.10 \
        git=1:2.47.1-1 \
        autoconf=2.72-3 \
        automake=1:1.16.5-1.3 \
        libtool=2.4.7-8 \
        libpopt-dev=1.19+dfsg-1+b1 \
        libconfig-dev=1.5-0.4 \
        libasound2-dev=1.2.12-1+b1 \
        avahi-daemon=0.8-13+b2 \
        libavahi-client-dev=0.8-13+b2 \
        libssl-dev=3.3.2-2 \
        libsoxr-dev=0.1.3-4+b3 \
        libplist-dev=2.6.0-3 \
        libsodium-dev=1.0.20-1 \
        libavahi-compat-libdnssd-dev=0.8-13+b2 \
        libavformat-dev=7:7.1-3 \
        libasound2-plugins=1.2.12-2 \
        xxd=2:9.1.0861-1 \
    \
    && curl -J -L -o /tmp/airconnect.zip \
      "https://github.com/philippe44/AirConnect/releases/download/${AIRCAST_VERSION}/AirConnect-${AIRCAST_VERSION}.zip" \
    && unzip -d /tmp /tmp/airconnect.zip \
    \
    && if [ "${BUILD_ARCH}" = "aarch64" ]; then AIRCONNECT_ARCH="aarch64"; \
    elif [ "${BUILD_ARCH}" = "amd64" ]; then AIRCONNECT_ARCH="x86_64"; fi \
    \
    && cp "/tmp/aircast-linux-${AIRCONNECT_ARCH}-static" /usr/bin/aircast \
    && chmod a+x /usr/bin/aircast \
    \
    && git clone https://github.com/mikebrady/shairport-sync.git /tmp/shairport-sync \
    && cd /tmp/shairport-sync \
    && autoreconf -fi \
    && ./configure \
        --with-alsa \
        --with-avahi \
        --with-ssl=openssl \
        --with-soxr \
        --with-metadata \
        --with-stdout \
        --with-pipe \
        --sysconfdir=/etc \
    && make -j$(nproc) \
    && make install \
    \
    && chmod a+x /usr/bin/esphome-discovery.py \
    && chmod a+x /usr/bin/esphome-airplay-bridge.py \
    && chmod a+x /usr/bin/shairport-manager.py \
    && chmod a+x /usr/bin/shairport-play-handler.py \
    \
    && apt-get purge -y --auto-remove \
        unzip \
        build-essential \
        git \
        autoconf \
        automake \
        libtool \
        libpopt-dev \
        libconfig-dev \
        libasound2-dev \
        libavahi-client-dev \
        libssl-dev \
        libsoxr-dev \
        libplist-dev \
        libsodium-dev \
        libavahi-compat-libdnssd-dev \
        libavformat-dev \
    && apt-mark manual \
        ffmpeg \
        avahi-daemon \
        libasound2-plugins \
        python3 \
        python3-requests \
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
