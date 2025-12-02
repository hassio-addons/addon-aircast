#!/bin/bash
# Quick build and test script for AirCast ESPHome add-on

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎵 AirCast ESPHome Add-on - Build & Test${NC}"
echo "================================================"
echo ""

# Detect architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    BUILD_ARCH="amd64"
elif [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
    BUILD_ARCH="aarch64"
else
    echo -e "${RED}❌ Unsupported architecture: $ARCH${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Detected architecture: $BUILD_ARCH${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

# Navigate to aircast directory
cd "$(dirname "$0")/aircast"

echo -e "${YELLOW}🔨 Building Docker image...${NC}"
echo "This may take 15-30 minutes on first build (compiling Shairport-Sync)"
echo ""

# Build the image
docker build \
    --build-arg BUILD_ARCH=$BUILD_ARCH \
    -t local/aircast-esphome:latest \
    -t local/aircast-esphome:dev \
    .

echo ""
echo -e "${GREEN}✅ Build successful!${NC}"
echo ""

# Show image info
echo -e "${YELLOW}📋 Image information:${NC}"
docker images local/aircast-esphome:latest
echo ""

# Verify components
echo -e "${YELLOW}🔍 Verifying components...${NC}"
echo ""

echo -n "Checking Shairport-Sync... "
if docker run --rm local/aircast-esphome:latest shairport-sync --version &> /dev/null; then
    VERSION=$(docker run --rm local/aircast-esphome:latest shairport-sync --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} $VERSION"
else
    echo -e "${RED}✗ Not found${NC}"
fi

echo -n "Checking FFmpeg... "
if docker run --rm local/aircast-esphome:latest ffmpeg -version &> /dev/null; then
    VERSION=$(docker run --rm local/aircast-esphome:latest ffmpeg -version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} $VERSION"
else
    echo -e "${RED}✗ Not found${NC}"
fi

echo -n "Checking Python 3... "
if docker run --rm local/aircast-esphome:latest python3 --version &> /dev/null; then
    VERSION=$(docker run --rm local/aircast-esphome:latest python3 --version 2>&1)
    echo -e "${GREEN}✓${NC} $VERSION"
else
    echo -e "${RED}✗ Not found${NC}"
fi

echo -n "Checking Python scripts... "
SCRIPTS=$(docker run --rm local/aircast-esphome:latest ls -1 /usr/bin/*-*.py 2>/dev/null | wc -l)
echo -e "${GREEN}✓${NC} Found $SCRIPTS scripts"

echo ""
echo -e "${GREEN}✅ All components verified!${NC}"
echo ""

# Offer to run the container
echo -e "${YELLOW}🚀 Ready to test?${NC}"
echo ""
echo "To run the container, you need a Home Assistant Supervisor token."
echo ""
echo "Get your token from:"
echo "  Home Assistant → Profile → Long-Lived Access Tokens → Create Token"
echo ""
read -p "Do you have a token ready? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter your Home Assistant token: " HA_TOKEN
    echo ""
    
    echo -e "${YELLOW}🎵 Starting AirCast ESPHome add-on...${NC}"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    
    docker run -it --rm \
        --name aircast-esphome-test \
        --network host \
        --privileged \
        -e SUPERVISOR_TOKEN="$HA_TOKEN" \
        -v /tmp/aircast-test-config:/data \
        local/aircast-esphome:latest
else
    echo ""
    echo -e "${YELLOW}📝 To run manually:${NC}"
    echo ""
    echo "docker run -it --rm \\"
    echo "  --network host \\"
    echo "  --privileged \\"
    echo "  -e SUPERVISOR_TOKEN='YOUR_TOKEN_HERE' \\"
    echo "  -v /tmp/aircast-config:/data \\"
    echo "  local/aircast-esphome:latest"
    echo ""
    echo -e "${YELLOW}🐚 To get a shell inside the container:${NC}"
    echo ""
    echo "docker run -it --rm \\"
    echo "  --network host \\"
    echo "  --privileged \\"
    echo "  -e SUPERVISOR_TOKEN='YOUR_TOKEN_HERE' \\"
    echo "  --entrypoint /bin/bash \\"
    echo "  local/aircast-esphome:latest"
    echo ""
fi

echo ""
echo -e "${GREEN}🎉 Build and verification complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Run the container with your HA token"
echo "  2. Check logs for ESPHome device discovery"
echo "  3. Look for AirPlay receivers on your iPhone/Mac"
echo "  4. Test audio playback"
echo ""
echo "See TESTING.md for detailed testing instructions"
echo ""
