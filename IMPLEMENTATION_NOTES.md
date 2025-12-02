# ESPHome AirPlay Bridge Implementation Notes

## How Music Assistant Does It

Music Assistant uses a sophisticated multi-layered architecture for ESPHome streaming:

### 1. **Player Detection & Configuration**
- Detects ESPHome media players via Home Assistant API
- Queries ESPHome diagnostics to get supported audio formats:
  ```python
  # From HA API: /api/diagnostics/config_entry/{conf_entry_id}
  {
    "format": "flac",      # or wav, mp3
    "sample_rate": 48000,  # supported sample rate
    "num_channels": 2,     # 1 for announcements, 2 for media
    "purpose": 0,          # 0 for media, 1 for announcements
    "sample_bytes": 2      # 2 for 16-bit audio
  }
  ```

### 2. **Stream Management**
- Music Assistant hosts its own HTTP streaming server
- Creates optimized streams based on ESPHome's capabilities
- Uses `StreamsController` to serve audio at: `http://mass-server/api/stream/{format}`

### 3. **Playback Flow**
```python
# When play_media is called on ESPHome player:
async def play_media(self, media: PlayerMedia) -> None:
    # 1. Stop current playback if any
    if self.playback_state == PlaybackState.PLAYING:
        await self.stop()
    
    # 2. Call HA's media_player.play_media service
    await self.hass.call_service(
        domain="media_player",
        service="play_media",
        target={"entity_id": self.player_id},
        service_data={
            "media_content_id": media.uri,  # HTTP stream URL from MA
            "media_content_type": "music",
            "enqueue": "replace",
            "extra": {
                "bypass_proxy": True,  # Tell ESPHome to skip its proxy
                "metadata": {...}       # Pass track metadata
            }
        }
    )
```

### 4. **Audio Pipeline**
```
Music Source → MA Server → HTTP Stream → HA API → ESPHome Device → Audio Output
              (transcode)  (optimized)   (play_media service)
```

### Key Features:
- **Format Optimization**: Queries supported formats and sends optimal stream
- **Bypass Proxy**: Tells ESPHome's media proxy to skip transcoding (MA already optimized it)
- **Flow Mode**: Can use "flow mode" for gapless playback (stitches songs together)
- **Metadata Support**: Passes track info through HA API
- **Dynamic Configuration**: Adjusts sample rate/bit depth based on device capabilities

---

## Our Current Implementation

### What We've Built So Far:

```
AirPlay Client → [aircast binary] → Chromecast Devices
                       ↓
              [esphome-bridge.py] → HTTP Stream → HA API → ESPHome Devices
```

### 1. **Discovery** (`esphome-discovery.py`)
- Queries HA API for media players with attribution "ESPHome"
- Returns entity IDs and friendly names
- Similar to Music Assistant's approach

### 2. **Bridge Service** (`esphome-airplay-bridge.py`)
- Creates HTTP streaming servers (one per ESPHome device)
- Attempts to buffer and serve audio
- Sends `play_media` commands via HA API

### 3. **What's Missing:**

#### A. **No AirPlay Receiver**
The biggest gap: we create infrastructure but don't actually receive AirPlay audio yet.

**Need to add:**
- **Shairport-Sync** integration, OR
- Custom AirPlay receiver using a library like `pyairplay`

#### B. **Audio Pipeline Not Connected**
Our HTTP servers are created but:
- No audio data is being captured from AirPlay
- No transcoding/buffering logic
- No connection between AirPlay input → HTTP output

#### C. **Format Detection Missing**
We should query ESPHome's supported formats like Music Assistant does:
```python
# Query HA diagnostics endpoint
formats = await get_esphome_supported_audio_formats(entity_config_id)
# Then optimize stream format accordingly
```

---

## Recommended Next Steps

### Option 1: Integrate Shairport-Sync (Recommended)
```dockerfile
# Add to Dockerfile
RUN apt-get install -y shairport-sync

# Configure shairport-sync to:
# 1. Create AirPlay receiver per ESPHome device
# 2. Pipe audio to our Python bridge
# 3. Bridge transcodes and serves via HTTP
# 4. Send play_media command to ESPHome via HA API
```

**Architecture:**
```
iPhone → AirPlay → Shairport-Sync → STDOUT (PCM) → Python Bridge
                   (per device)                           ↓
                                                    Transcode to FLAC/WAV
                                                           ↓
                                                    HTTP Stream Server
                                                           ↓
                                                    HA API play_media
                                                           ↓
                                                    ESPHome Device
```

### Option 2: Create Custom AirPlay Receiver
Use a Python library to implement AirPlay RAOP (Remote Audio Output Protocol):
```python
# Pseudo-code
from pyairplay import AirPlayReceiver

receiver = AirPlayReceiver(name="ESPHome Device Name")
@receiver.on_audio
async def handle_audio(audio_data):
    # Transcode audio_data
    # Push to HTTP stream
    # Trigger HA API play_media
```

### Option 3: Hybrid Approach (What Music Assistant Does)
- Keep `aircast` for Chromecast devices
- Add separate service for ESPHome that:
  - Receives AirPlay via Shairport-Sync or custom receiver
  - Manages audio buffering and format conversion
  - Serves optimized HTTP streams
  - Controls ESPHome via HA API

---

## Critical Differences

| Aspect | Music Assistant | Our Implementation |
|--------|----------------|-------------------|
| **Primary Purpose** | Full music server with library management | AirPlay bridge only |
| **Audio Source** | Internal library, streaming services | AirPlay streams only |
| **Stream Hosting** | Built-in web server with queue management | Need to add per-device HTTP servers |
| **Format Detection** | Queries ESPHome diagnostics | Not yet implemented |
| **Buffering** | Sophisticated queue & flow mode | Need to implement |
| **Transcoding** | FFmpeg with per-player DSP | Need to implement |
| **Device Control** | Full HA integration | Basic play_media service |

---

## What Works vs What Doesn't

### ✅ What Currently Works:
1. Discovery of ESPHome devices via HA API
2. S6-overlay service infrastructure
3. Configuration schema for enabling ESPHome support
4. Basic HTTP server framework

### ❌ What Doesn't Work Yet:
1. **No AirPlay reception** - can't receive audio from iOS devices
2. **No audio pipeline** - no data flows through the HTTP servers
3. **No format optimization** - not querying ESPHome capabilities
4. **No transcoding** - no conversion of audio formats
5. **No buffering** - no queue or stream management
6. **No virtual AirPlay devices created** - iOS won't see any new receivers

---

## Immediate Action Items

To make this functional, we need to:

1. **Add AirPlay Receiver**
   - Install and configure Shairport-Sync
   - Create one instance per ESPHome device
   - Pipe audio output to Python bridge

2. **Build Audio Pipeline**
   - Capture PCM audio from Shairport-Sync
   - Buffer audio data
   - Serve via HTTP streaming

3. **Add Transcoding**
   - Install FFmpeg
   - Convert audio to ESPHome-compatible format
   - Optimize based on device capabilities

4. **Query ESPHome Capabilities**
   - Fetch supported formats from HA diagnostics
   - Configure streams accordingly

5. **Implement Proper play_media**
   - Add metadata support
   - Include "bypass_proxy" flag
   - Handle state management

---

## Docker/Home Assistant Add-on Architecture (IMPLEMENTED)

### **Decision: Using Shairport-Sync ✓**

We've chosen Shairport-Sync over custom RAOP implementation because:
- ✅ Production-ready and battle-tested
- ✅ Full AirPlay 1 & 2 support
- ✅ Easy Docker integration
- ✅ Professional audio quality
- ✅ Minimal maintenance overhead

### **Complete System Architecture**

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Home Assistant Add-on Container                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │  aircast binary  │         │ shairport-manager│                 │
│  │  (for Chromecast)│         │    .py           │                 │
│  └──────────────────┘         └────────┬─────────┘                 │
│                                         │                            │
│                              ┌──────────▼─────────────┐             │
│                              │  Shairport-Sync        │             │
│                              │  (per ESPHome device)  │             │
│                              │  - Creates AirPlay     │             │
│                              │    receivers           │             │
│                              │  - Outputs to pipe     │             │
│                              └──────────┬─────────────┘             │
│                                         │                            │
│                              ┌──────────▼─────────────┐             │
│                              │ shairport-play-handler │             │
│                              │       .py              │             │
│                              │  - Reads from pipe     │             │
│                              │  - Transcodes (FFmpeg) │             │
│                              │  - Serves via HTTP     │             │
│                              │  - Calls HA API        │             │
│                              └──────────┬─────────────┘             │
│                                         │                            │
└─────────────────────────────────────────┼────────────────────────────┘
                                          │
                    HTTP Stream URL + HA API play_media
                                          │
                                          ▼
                              ┌────────────────────┐
                              │  Home Assistant    │
                              │  media_player      │
                              │  .play_media()     │
                              └─────────┬──────────┘
                                        │
                                        ▼
                              ┌────────────────────┐
                              │  ESPHome Device    │
                              │  - Fetches HTTP    │
                              │  - Plays audio     │
                              └────────────────────┘
```

### **Component Breakdown**

#### 1. **Shairport-Sync Manager** (`shairport-manager.py`)
- Discovers ESPHome devices via HA API
- Creates Shairport-Sync config file per device
- Spawns one Shairport-Sync process per ESPHome device
- Each creates a unique AirPlay receiver (visible on iOS/Mac)
- Monitors processes and restarts if they crash

#### 2. **Shairport-Sync Instances**
- Native C binary (compiled in Dockerfile)
- Each instance:
  - Listens on unique port (5000, 5001, 5002...)
  - Advertises via Avahi/mDNS with ESPHome device name
  - Outputs raw PCM audio to named pipe
  - Calls play handler on session start/stop

#### 3. **Play Handler** (`shairport-play-handler.py`)
- Called by Shairport-Sync via `sessioncontrol` hooks
- **On Start:**
  - Starts FFmpeg to read pipe and transcode to WAV
  - Starts Python HTTP server to serve WAV file
  - Calls HA API `media_player.play_media` with stream URL
- **On Stop:**
  - Stops FFmpeg and HTTP server
  - Calls HA API `media_player.media_stop`
  - Cleans up temporary files

#### 4. **Audio Flow**
```
iPhone/Mac → AirPlay → Shairport-Sync → Named Pipe (PCM)
                                            ↓
                                        FFmpeg (transcode)
                                            ↓
                                        WAV file in /tmp
                                            ↓
                                    Python HTTP Server
                                            ↓
                                    http://localhost:7000/stream.wav
                                            ↓
                                    HA API play_media
                                            ↓
                                    ESPHome fetches URL
                                            ↓
                                    Audio playback
```

### **Docker Build Process**

1. **Base Image**: Debian-based HA add-on base
2. **Install Build Tools**: gcc, git, autoconf, etc.
3. **Install Runtime Dependencies**:
   - Python 3 + requests
   - FFmpeg (for transcoding)
   - Avahi daemon (for mDNS)
   - ALSA libraries
   - SSL libraries
4. **Build Shairport-Sync from source**:
   - Clone from GitHub
   - Configure with pipe, stdout, metadata support
   - Compile and install
5. **Copy Python scripts**:
   - `shairport-manager.py`
   - `shairport-play-handler.py`
   - `esphome-discovery.py`
6. **Clean up build dependencies** to reduce image size

### **S6-Overlay Services**

Two independent services run in parallel:

#### `aircast` service:
- Runs for Chromecast devices
- Traditional AirConnect functionality
- Enabled by default

#### `esphome-bridge` service:
- Runs if `esphome_enabled: true`
- Starts Avahi daemon
- Executes `shairport-manager.py`
- Manages all ESPHome AirPlay receivers

### **Configuration Options**

```yaml
esphome_enabled: true   # Enable ESPHome support
# ... existing aircast options ...
```

### **Home Assistant Integration**

The add-on uses the Supervisor API to:
1. Query HA states: `http://supervisor/core/api/states`
2. Call services: `http://supervisor/core/api/services/media_player/play_media`
3. Uses `SUPERVISOR_TOKEN` environment variable for auth

### **Network Requirements**

- **mDNS/Avahi**: For AirPlay discovery (port 5353 UDP)
- **AirPlay ports**: 5000+ TCP (one per device)
- **HTTP streaming**: 7000+ TCP (one per device)
- **HA API**: Internal supervisor network
- **host_network: true** required for:
  - Chromecast discovery
  - AirPlay mDNS broadcasting
  - Low-latency audio streaming

### **Advantages of This Architecture**

1. **Isolation**: Each ESPHome device gets its own AirPlay receiver
2. **Scalability**: Can handle multiple devices simultaneously
3. **Reliability**: Process monitoring and auto-restart
4. **Compatibility**: Works with any ESPHome media player
5. **Independence**: Doesn't interfere with Chromecast functionality
6. **Standard Protocols**: Uses well-established AirPlay and HTTP

### **Limitations & Considerations**

1. **Latency**: Small delay due to transcoding and HTTP transfer (~1-2 seconds)
2. **Network Bandwidth**: Each stream consumes ~1.4 Mbps for CD-quality audio
3. **CPU Usage**: FFmpeg transcoding per active stream
4. **No Synchronization**: Each device plays independently (no multi-room sync)
5. **HTTP Streaming**: ESPHome must support fetching HTTP URLs

### **Testing & Deployment**

**Build the Docker image:**
```bash
docker build -t aircast-esphome:latest ./aircast
```

**Install in Home Assistant:**
1. Add add-on repository to HA
2. Install "AirCast" add-on
3. Enable `esphome_enabled: true`
4. Start the add-on
5. Check logs for discovered devices
6. Look for AirPlay receivers on iOS

**Troubleshooting:**
- Check add-on logs for errors
- Verify ESPHome devices are discovered
- Ensure Avahi daemon is running
- Test HTTP stream URLs directly
- Confirm HA API connectivity

---

## Status: Ready for Testing ✓

The implementation is now complete with Shairport-Sync integration. Next steps:
1. Build and test the Docker image
2. Verify AirPlay receivers appear on iOS
3. Test audio playback quality
4. Monitor CPU/memory usage
5. Fine-tune buffering and quality settings
