#!/usr/bin/with-contenv bash
# ==============================================================================
# Community Hass.io Add-ons: AirCast
# Checks latency settings before starting the AirCast server
# ==============================================================================
# shellcheck disable=SC1091
source /usr/lib/hassio-addons/base.sh

declare latency

latency=$(hass.config.get 'latency_rtp')

if [[ "${latency}" -lt 500 && "${latency}" -ne 0 ]]; then
    hass.log.warning \
        'Setting the RTP latency of AirPlay audio below 500ms is not recommended!'
fi
