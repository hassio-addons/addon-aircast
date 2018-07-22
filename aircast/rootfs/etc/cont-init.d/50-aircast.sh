#!/usr/bin/with-contenv bash
# ==============================================================================
# Community Hass.io Add-ons: AirCast
# Checks latency settings before starting the AirCast server
# ==============================================================================
# shellcheck disable=SC1091
source /usr/lib/hassio-addons/base.sh

declare latency

# Create a configuration file, if it does not exist yet
if ! hass.file_exists '/config/aircast.xml'; then
    cp /etc/aircast.xml /config/aircast.xml
fi

# Warn if latency is below 500ms
latency=$(hass.config.get 'latency_rtp')
if [[ "${latency}" -lt 500 && "${latency}" -ne 0 ]]; then
    hass.log.warning \
        'Setting the RTP latency of AirPlay audio below 500ms is not recommended!'
fi
