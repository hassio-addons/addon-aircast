# Home Assistant Community Add-on: AirCast (with ESPHome Support)

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
[![License][license-shield]](LICENSE.md)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

[![Github Actions][github-actions-shield]][github-actions]
![Project Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

AirPlay capabilities for your Chromecast and ESPHome media players.

## About

This add-on extends the original AirCast add-on to support **ESPHome media players** in addition to Chromecast devices.

### Chromecast Support (Original Feature)

Apple devices use AirPlay to send audio to other devices, but this is not
compatible with Google's Chromecast. This add-on solves this
compatibility gap.

It detects Chromecast players in your network and creates virtual AirPlay
devices for each of them. It acts as a bridge between the AirPlay client
and the real Chromecast player.

### ESPHome Support (New!)

Now you can also stream AirPlay audio to your **ESPHome media players**! 

When enabled, the add-on:
- Discovers ESPHome media players via Home Assistant
- Creates virtual AirPlay receivers for each device using Shairport-Sync
- Streams audio through Home Assistant's API
- Works alongside Chromecast support

**Features:**
- 🎵 Full AirPlay support via Shairport-Sync
- 🔍 Automatic device discovery
- 📱 Works with iPhone, iPad, Mac, and iTunes
- 🎛️ Individual device control
- ⚡ Low latency streaming
- 🔄 Independent from Chromecast functionality

## Installation

### Adding the Repository

1. Navigate to the **Add-on Store** in Home Assistant
2. Click the **⋮** (three dots) menu and select **Repositories**
3. Add this repository URL:
   ```
   https://github.com/DeveshwarH1996/addon-aircastESP
   ```
4. Click **Add**

### Installing the Add-on

1. Find **AirCast** in the add-on store
2. Click on it and press **Install**
3. Wait for installation to complete (first build may take 20-30 minutes)
4. Configure the add-on (see below)
5. Start the add-on

## Configuration

**Minimal configuration for ESPHome support:**

```yaml
esphome_enabled: true
```

**Full configuration example:**

```yaml
log_level: info
address: 192.168.1.234
latency_rtp: 5000
latency_http: 0
drift: true
esphome_enabled: true
```

### Option: `esphome_enabled`

Set to `true` to enable ESPHome media player support. When enabled:
- The add-on discovers your ESPHome media players
- Creates AirPlay receivers with your device names
- Streams audio via Home Assistant API

Default: `false`

### Other Options

See [full documentation](aircast/DOCS.md) for details on:
- `log_level` - Control verbosity
- `address` - Bind to specific network interface
- `latency_rtp` / `latency_http` - Audio buffering
- `drift` - Timing reference drift mode

## Usage

### For ESPHome Devices:

1. Enable `esphome_enabled: true` in configuration
2. Start the add-on
3. Check logs to verify your devices were discovered
4. On your iPhone/iPad/Mac, open Control Center
5. Tap the AirPlay icon
6. Your ESPHome devices will appear in the list
7. Select a device and play audio!

### For Chromecast Devices:

Works automatically - no special configuration needed!
Just select the Chromecast from AirPlay on your iOS device.

## Requirements

### For ESPHome Support:

- ESPHome devices with `media_player` component configured
- Devices must support HTTP audio streaming
- Network connectivity between add-on and ESPHome devices

### Network:

- `host_network: true` (automatically configured)
- mDNS/Avahi for AirPlay discovery
- No firewall blocking between devices

## How It Works

### ESPHome Audio Pipeline:

```
iPhone/Mac (AirPlay)
    ↓
Shairport-Sync (receives AirPlay stream)
    ↓
FFmpeg (transcodes to WAV)
    ↓
HTTP Server (streams audio)
    ↓
Home Assistant API (play_media service)
    ↓
ESPHome Device (plays audio)
```

## Documentation

- [Full Documentation](aircast/DOCS.md)
- [Implementation Notes](IMPLEMENTATION_NOTES.md)
- [Testing Guide](TESTING.md)
- [Summary](SUMMARY.md)

## Support

Got questions?

You could [open an issue here][issue] on GitHub.

Original AirCast support:
- The [Home Assistant Community Add-ons Discord chat server][discord] for add-on
  support and feature requests.
- The Home Assistant [Community Forum][forum].

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

## Authors & contributors

ESPHome support added by [DeveshwarH1996][deveshwar].

Original AirCast add-on by [Franck Nijhof][frenck].

The AirCast add-on is based on the excellent [AirConnect][airconnect] project.
ESPHome support uses [Shairport-Sync][shairport-sync].

## License

MIT License

Copyright (c) 2017-2025 Franck Nijhof
Copyright (c) 2025 DeveshwarH1996 (ESPHome support)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[airconnect]: https://github.com/philippe44/AirConnect
[shairport-sync]: https://github.com/mikebrady/shairport-sync
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/DeveshwarH1996/addon-aircastESP.svg
[commits]: https://github.com/DeveshwarH1996/addon-aircastESP/commits/ESPHome
[discord-shield]: https://img.shields.io/discord/478094546522079232.svg
[discord]: https://discord.me/hassioaddons
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg
[forum]: https://community.home-assistant.io/t/home-assistant-community-add-on-aircast/36742?u=frenck
[frenck]: https://github.com/frenck
[deveshwar]: https://github.com/DeveshwarH1996
[github-actions-shield]: https://github.com/DeveshwarH1996/addon-aircastESP/workflows/CI/badge.svg
[github-actions]: https://github.com/DeveshwarH1996/addon-aircastESP/actions
[issue]: https://github.com/DeveshwarH1996/addon-aircastESP/issues
[license-shield]: https://img.shields.io/github/license/DeveshwarH1996/addon-aircastESP.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[releases-shield]: https://img.shields.io/github/release/DeveshwarH1996/addon-aircastESP.svg
[releases]: https://github.com/DeveshwarH1996/addon-aircastESP/releases

## Support

Got questions?

You have several options to get them answered:

- The [Home Assistant Community Add-ons Discord chat server][discord] for add-on
  support and feature requests.
- The [Home Assistant Discord chat server][discord-ha] for general Home
  Assistant discussions and questions.
- The Home Assistant [Community Forum][forum].
- Join the [Reddit subreddit][reddit] in [/r/homeassistant][reddit]

You could also [open an issue here][issue] GitHub.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](.github/CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this repository is by [Franck Nijhof][frenck].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## We have got some Home Assistant add-ons for you

Want some more functionality to your Home Assistant instance?

We have created multiple add-ons for Home Assistant. For a full list, check out
our [GitHub Repository][repository].

## License

MIT License

Copyright (c) 2017-2025 Franck Nijhof

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[airconnect]: https://github.com/philippe44/AirConnect
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/hassio-addons/addon-aircast.svg
[commits]: https://github.com/hassio-addons/addon-aircast/commits/main
[contributors]: https://github.com/hassio-addons/addon-aircast/graphs/contributors
[discord-ha]: https://discord.gg/c5DvZ4e
[discord-shield]: https://img.shields.io/discord/478094546522079232.svg
[discord]: https://discord.me/hassioaddons
[docs]: https://github.com/hassio-addons/addon-aircast/blob/main/aircast/DOCS.md
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg
[forum]: https://community.home-assistant.io/t/home-assistant-community-add-on-aircast/36742?u=frenck
[frenck]: https://github.com/frenck
[github-actions-shield]: https://github.com/hassio-addons/addon-aircast/workflows/CI/badge.svg
[github-actions]: https://github.com/hassio-addons/addon-aircast/actions
[github-sponsors-shield]: https://frenck.dev/wp-content/uploads/2019/12/github_sponsor.png
[github-sponsors]: https://github.com/sponsors/frenck
[issue]: https://github.com/hassio-addons/addon-aircast/issues
[license-shield]: https://img.shields.io/github/license/hassio-addons/addon-aircast.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[patreon-shield]: https://frenck.dev/wp-content/uploads/2019/12/patreon.png
[patreon]: https://www.patreon.com/frenck
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[reddit]: https://reddit.com/r/homeassistant
[releases-shield]: https://img.shields.io/github/release/hassio-addons/addon-aircast.svg
[releases]: https://github.com/hassio-addons/addon-aircast/releases
[repository]: https://github.com/hassio-addons/repository
