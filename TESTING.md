# Building and Testing the AirCast ESPHome Add-on

## Prerequisites

- Docker installed on your machine
- Home Assistant OS or Supervised installation
- At least one ESPHome device with media_player component
- iOS device or Mac for AirPlay testing

---

## Method 1: Local Docker Build (Fastest for Development)

### 1. Build the Docker Image

```bash
cd /home/srinivas/aircast/addon-aircast/aircast

# Build for your architecture
docker build --build-arg BUILD_ARCH=amd64 -t local/aircast-test:latest .

# Or for ARM64 (Raspberry Pi 4, etc.)
docker build --build-arg BUILD_ARCH=aarch64 -t local/aircast-test:latest .
```

**Build time**: ~15-30 minutes (Shairport-Sync compilation takes time)

### 2. Test the Image Locally

```bash
# Run the container with host network access
docker run -it --rm \
  --network host \
  --privileged \
  -e SUPERVISOR_TOKEN="your_ha_long_lived_access_token" \
  -v /tmp/aircast-config:/data \
  local/aircast-test:latest

# To get a shell inside the container for debugging:
docker run -it --rm \
  --network host \
  --privileged \
  -e SUPERVISOR_TOKEN="your_token" \
  --entrypoint /bin/bash \
  local/aircast-test:latest
```

### 3. Verify Components

Inside the container or in logs, check:

```bash
# Check Shairport-Sync is installed
shairport-sync --version

# Check FFmpeg is available
ffmpeg -version

# Check Python scripts are executable
ls -l /usr/bin/shairport-*.py /usr/bin/esphome-*.py

# Test ESPHome discovery (needs HA API access)
python3 /usr/bin/esphome-discovery.py

# Check Avahi daemon
avahi-daemon --check
```

---

## Method 2: Local Add-on Development (Recommended for HA Testing)

### 1. Set Up Local Add-on Repository

```bash
# On your Home Assistant host, create a local add-ons folder
mkdir -p /addons/aircast-esphome
cp -r /home/srinivas/aircast/addon-aircast/aircast/* /addons/aircast-esphome/

# Or use a bind mount in development
# (path may vary based on your HA installation)
```

### 2. Add Local Repository to Home Assistant

1. Open Home Assistant
2. Go to **Settings** → **Add-ons** → **Add-on Store**
3. Click the **⋮** (three dots) menu → **Repositories**
4. Add: `file:///addons` or your local path
5. The add-on should appear in the store

### 3. Install and Configure

1. Click on **AirCast** add-on
2. Click **Install** (this will build the Docker image)
3. Go to **Configuration** tab
4. Set your configuration:
   ```yaml
   esphome_enabled: true
   log_level: debug
   ```
5. Click **Save**

### 4. Start the Add-on

1. Go to **Info** tab
2. Click **Start**
3. Enable **"Start on boot"** and **"Watchdog"**
4. Click **Logs** tab to watch output

---

## Method 3: GitHub Actions CI/CD (For Production)

### 1. Set Up GitHub Secrets

In your repository settings, add:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`

### 2. Create Build Workflow

```yaml
# .github/workflows/build.yml
name: Build Add-on

on:
  push:
    branches: [ ESPHome, main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        arch: [amd64, aarch64]
    steps:
      - uses: actions/checkout@v3
      
      - name: Build add-on
        uses: home-assistant/builder@master
        with:
          args: |
            --${{ matrix.arch }} \
            --target aircast \
            --docker-hub-check
```

### 3. Push and Monitor

```bash
git push origin ESPHome
# Watch the build in GitHub Actions tab
```

---

## Testing Checklist

### Phase 1: Container Health

- [ ] Docker image builds successfully
- [ ] No errors in build logs
- [ ] Image size is reasonable (<500MB)
- [ ] All binaries are present (shairport-sync, ffmpeg)
- [ ] Python scripts are executable
- [ ] S6-overlay services start correctly

```bash
# Check image size
docker images | grep aircast

# Inspect image layers
docker history local/aircast-test:latest

# Check running processes inside container
docker exec <container_id> ps aux
```

### Phase 2: ESPHome Discovery

- [ ] Add-on connects to Home Assistant API
- [ ] ESPHome devices are discovered
- [ ] Device names are correct
- [ ] Logs show device list

**Check logs for:**
```
Found X ESPHome media player(s):
  • Kitchen Speaker (media_player.kitchen_speaker)
  • Bedroom Speaker (media_player.bedroom_speaker)
```

### Phase 3: Shairport-Sync Initialization

- [ ] Avahi daemon starts successfully
- [ ] Shairport-Sync instances are created
- [ ] Configuration files generated in /tmp/shairport-configs/
- [ ] Named pipes created in /tmp/
- [ ] No port conflicts

**Check logs for:**
```
Starting Avahi daemon...
Starting Shairport-Sync for Kitchen Speaker
✓ Started AirPlay receiver for Kitchen Speaker
All AirPlay receivers are now running!
```

**Verify in container:**
```bash
# Check Shairport-Sync processes
ps aux | grep shairport-sync

# Check configuration files
ls -l /tmp/shairport-configs/

# Check named pipes
ls -l /tmp/shairport_*.pipe

# Check listening ports
netstat -tulpn | grep shairport
```

### Phase 4: AirPlay Discovery (iOS/Mac)

- [ ] Open Control Center on iPhone/iPad
- [ ] Tap AirPlay icon
- [ ] ESPHome device names appear in list
- [ ] Devices show "AirPlay" icon (not just Bluetooth)
- [ ] Can select individual devices

**Troubleshooting if devices don't appear:**
```bash
# Check mDNS advertisements
avahi-browse -a -t

# Should show entries like:
# + eth0 IPv4 Kitchen Speaker _raop._tcp local

# Check Avahi daemon status
avahi-daemon --check

# Restart Avahi if needed
avahi-daemon --kill
avahi-daemon --daemonize
```

### Phase 5: Audio Playback

Test each ESPHome device:

- [ ] Select device from iOS AirPlay menu
- [ ] Play music from Apple Music/Spotify/etc
- [ ] Audio starts playing (may have 2-3 second delay)
- [ ] Volume control works
- [ ] Pause/resume works
- [ ] Changing tracks works
- [ ] Stopping playback stops ESPHome device

**Monitor during playback:**

```bash
# Watch add-on logs in real-time
docker logs -f <container_id>

# Should see:
# Playback starting for media_player.kitchen_speaker
# Starting FFmpeg: ...
# Starting HTTP server on port 7000
# ✓ Started playback on media_player.kitchen_speaker

# Check FFmpeg processes
ps aux | grep ffmpeg

# Check HTTP servers
netstat -tulpn | grep python

# Check ESPHome device state in HA
# Should show: state: playing
```

### Phase 6: Multiple Devices

- [ ] Play to first device
- [ ] Play to second device simultaneously
- [ ] Both devices play independently
- [ ] No audio interference
- [ ] Both can be controlled separately
- [ ] CPU/memory usage is acceptable

```bash
# Monitor resource usage
docker stats <container_id>

# Check number of active streams
ps aux | grep ffmpeg | wc -l
```

### Phase 7: Error Handling

Test failure scenarios:

- [ ] Stop ESPHome device - add-on handles gracefully
- [ ] Disconnect network - reconnects automatically
- [ ] Kill Shairport-Sync process - auto-restarts
- [ ] Restart Home Assistant - add-on recovers
- [ ] Remove ESPHome device - add-on adapts

### Phase 8: Performance Testing

Monitor for at least 30 minutes of playback:

- [ ] No memory leaks (use `docker stats`)
- [ ] CPU usage stabilizes
- [ ] No pipe/socket leaks (`lsof` or `ls /proc/<pid>/fd`)
- [ ] Temporary files cleaned up
- [ ] Logs don't grow indefinitely

```bash
# Memory usage over time
while true; do
  docker stats --no-stream <container_id> | tail -n 1
  sleep 60
done

# Check for file descriptor leaks
docker exec <container_id> ls -l /proc/$(pgrep shairport)/fd | wc -l

# Monitor temp directory size
docker exec <container_id> du -sh /tmp/
```

---

## Common Issues and Solutions

### Issue 1: Build Fails - Missing Dependencies

**Error:**
```
E: Unable to locate package libsoxr-dev
```

**Solution:**
Check package versions in Dockerfile match your Debian base version:
```bash
# Find available versions
apt-cache policy libsoxr-dev
```

### Issue 2: Shairport-Sync Doesn't Start

**Error:**
```
shairport-sync: error while loading shared libraries
```

**Solution:**
```bash
# Check linked libraries
ldd /usr/local/bin/shairport-sync

# Ensure runtime libraries are kept in Dockerfile
# (not removed in apt-get purge)
```

### Issue 3: AirPlay Devices Don't Appear

**Checklist:**
1. Is Avahi daemon running? `avahi-daemon --check`
2. Are ports 5000+ available? `netstat -tulpn | grep 5000`
3. Is mDNS traffic allowed? Check firewall
4. Is host_network mode enabled? Check add-on config
5. Are you on the same network as HA?

**Debug:**
```bash
# Check mDNS advertisements
avahi-browse -a

# Check Shairport-Sync is advertising
avahi-browse _raop._tcp

# Test from iOS: Settings → Privacy → Local Network
# Ensure Home Assistant app has permission
```

### Issue 4: Audio Doesn't Play on ESPHome

**Check:**
1. ESPHome device supports HTTP URLs
2. Add-on can reach ESPHome device IP
3. HTTP server is running on correct port
4. WAV file is being created

**Debug:**
```bash
# Check if WAV file exists and is growing
watch -n 1 ls -lh /tmp/stream_*.wav

# Test HTTP server directly
curl -I http://localhost:7000/stream_media_player_kitchen.wav

# Check HA API response
# (check add-on logs for API call results)
```

### Issue 5: High CPU Usage

**Causes:**
- FFmpeg transcoding (expected: 15-25% per stream)
- Multiple simultaneous streams
- Inefficient audio format

**Solutions:**
```bash
# Check FFmpeg processes
ps aux | grep ffmpeg

# Optimize FFmpeg settings in shairport-play-handler.py:
# - Lower sample rate if ESPHome supports it
# - Use hardware acceleration if available
# - Reduce buffer sizes
```

### Issue 6: Audio Quality Issues

**Symptoms:**
- Stuttering, dropouts, crackling

**Solutions:**
1. Check network bandwidth
2. Increase buffer sizes in Shairport-Sync config
3. Verify ESPHome device isn't CPU-limited
4. Test with different audio formats

---

## Debug Mode

Enable detailed logging:

```yaml
# Add-on configuration
log_level: debug
```

Then check logs for:
- All API calls to Home Assistant
- Shairport-Sync verbose output
- FFmpeg transcoding details
- HTTP server requests
- Process lifecycle events

---

## Quick Test Script

Save this as `test-addon.sh`:

```bash
#!/bin/bash
set -e

echo "🔨 Building Docker image..."
docker build --build-arg BUILD_ARCH=amd64 -t local/aircast-test:latest ./aircast

echo "✅ Build successful!"
echo ""
echo "📋 Image info:"
docker images local/aircast-test:latest

echo ""
echo "🔍 Checking binaries..."
docker run --rm local/aircast-test:latest shairport-sync --version
docker run --rm local/aircast-test:latest ffmpeg -version 2>&1 | head -n 1
docker run --rm local/aircast-test:latest python3 --version

echo ""
echo "✅ All checks passed!"
echo ""
echo "To run the container:"
echo "docker run -it --rm --network host --privileged \\"
echo "  -e SUPERVISOR_TOKEN='your_token' \\"
echo "  local/aircast-test:latest"
```

Run with:
```bash
chmod +x test-addon.sh
./test-addon.sh
```

---

## Next Steps After Successful Testing

1. **Optimize Dockerfile** - Reduce image size if needed
2. **Add Health Checks** - Monitor component status
3. **Create User Documentation** - Screenshots and setup guide
4. **Set Up CI/CD** - Automated builds for releases
5. **Submit to Community** - Share in HA community add-ons
6. **Gather Feedback** - Test with various ESPHome devices
7. **Performance Tuning** - Optimize based on real-world usage

---

## Support and Debugging

If you encounter issues:

1. **Check add-on logs** - Most issues show up here
2. **Enable debug logging** - Get detailed information
3. **Test components individually** - Isolate the problem
4. **Check Home Assistant logs** - For API-related issues
5. **Verify ESPHome device** - Ensure it's working correctly
6. **Network connectivity** - Test all connections

**Collect debug info:**
```bash
# Add-on logs
docker logs <container_id> > addon-logs.txt

# Container inspect
docker inspect <container_id> > container-info.json

# Process list
docker exec <container_id> ps aux > processes.txt

# Network connections
docker exec <container_id> netstat -tulpn > network.txt

# Running services
docker exec <container_id> s6-rc -a list > services.txt
```

---

## Success Criteria

The add-on is ready for release when:

✅ Builds successfully on amd64 and aarch64
✅ All ESPHome devices discovered correctly
✅ AirPlay receivers appear on iOS within 30 seconds
✅ Audio plays with acceptable quality and latency
✅ Multiple devices work simultaneously
✅ CPU usage < 30% per active stream
✅ Memory usage < 200MB per active stream
✅ No crashes during 24-hour test
✅ Graceful handling of edge cases
✅ Clear logs and error messages

**Happy testing! 🎵**
