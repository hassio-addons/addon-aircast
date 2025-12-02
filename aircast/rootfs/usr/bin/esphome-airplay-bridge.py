#!/usr/bin/env python3
"""
ESPHome AirPlay Bridge
Creates virtual AirPlay receivers for ESPHome media players
Streams audio via HTTP to ESPHome devices through Home Assistant API
"""
import os
import sys
import json
import time
import socket
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, List, Optional
import subprocess
import signal

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
HA_API_URL = 'http://supervisor/core/api'
BRIDGE_PORT_BASE = 8090
STREAM_PORT_BASE = 7000

class AudioStreamHandler(BaseHTTPRequestHandler):
    """HTTP handler for audio streaming"""
    
    audio_buffer = bytearray()
    buffer_lock = threading.Lock()
    
    def do_GET(self):
        """Handle GET requests for audio stream"""
        if self.path.startswith('/stream'):
            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header('Transfer-Encoding', 'chunked')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            # Stream audio chunks
            try:
                while True:
                    with self.buffer_lock:
                        if len(self.audio_buffer) > 0:
                            chunk = bytes(self.audio_buffer[:4096])
                            self.audio_buffer = self.audio_buffer[4096:]
                        else:
                            chunk = b''
                    
                    if chunk:
                        self.wfile.write(f'{len(chunk):X}\r\n'.encode())
                        self.wfile.write(chunk)
                        self.wfile.write(b'\r\n')
                        self.wfile.flush()
                    else:
                        time.sleep(0.01)
                        
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class ESPHomeAirPlayBridge:
    """Bridge between AirPlay and ESPHome media players"""
    
    def __init__(self, esphome_players: List[Dict], config: Dict):
        self.esphome_players = esphome_players
        self.config = config
        self.servers = []
        self.active_streams = {}
        
    def get_local_ip(self) -> str:
        """Get the local IP address"""
        try:
            # Connect to external host to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def start_stream_server(self, port: int) -> Optional[HTTPServer]:
        """Start HTTP server for audio streaming"""
        try:
            server = HTTPServer(('', port), AudioStreamHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            return server
        except Exception as e:
            print(f"Error starting stream server on port {port}: {e}", file=sys.stderr)
            return None
    
    def play_on_esphome(self, entity_id: str, stream_url: str):
        """Send play_media command to ESPHome device via HA API"""
        try:
            payload = {
                'entity_id': entity_id,
                'media_content_id': stream_url,
                'media_content_type': 'music'
            }
            
            response = requests.post(
                f'{HA_API_URL}/services/media_player/play_media',
                headers={
                    'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"Started playback on {entity_id}")
            return True
            
        except Exception as e:
            print(f"Error playing on {entity_id}: {e}", file=sys.stderr)
            return False
    
    def stop_on_esphome(self, entity_id: str):
        """Send stop command to ESPHome device via HA API"""
        try:
            payload = {'entity_id': entity_id}
            
            response = requests.post(
                f'{HA_API_URL}/services/media_player/media_stop',
                headers={
                    'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
                    'Content-Type': 'application/json',
                },
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"Stopped playback on {entity_id}")
            return True
            
        except Exception as e:
            print(f"Error stopping {entity_id}: {e}", file=sys.stderr)
            return False
    
    def create_virtual_airplay_device(self, player: Dict, index: int):
        """
        Create a virtual AirPlay receiver for an ESPHome player
        This would use shairport-sync or similar to create the AirPlay endpoint
        """
        # This is a placeholder - would need shairport-sync configured
        # to pipe audio and trigger playback on ESPHome
        pass
    
    def run(self):
        """Start the bridge"""
        print(f"Starting ESPHome AirPlay Bridge for {len(self.esphome_players)} device(s)")
        
        local_ip = self.get_local_ip()
        print(f"Local IP: {local_ip}")
        
        # Start stream servers for each ESPHome player
        for idx, player in enumerate(self.esphome_players):
            port = STREAM_PORT_BASE + idx
            server = self.start_stream_server(port)
            if server:
                self.servers.append(server)
                stream_url = f"http://{local_ip}:{port}/stream"
                print(f"Stream server started for {player['friendly_name']} at {stream_url}")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            for server in self.servers:
                server.shutdown()

def load_config():
    """Load add-on configuration"""
    config_file = '/data/options.json'
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except:
        return {}

def main():
    """Main function"""
    config = load_config()
    
    # Check if ESPHome support is enabled
    if not config.get('esphome_enabled', False):
        print("ESPHome support is disabled in configuration")
        sys.exit(0)
    
    # Discover ESPHome players
    try:
        result = subprocess.run(
            ['/usr/bin/esphome-discovery.py'],
            capture_output=True,
            text=True,
            check=True
        )
        players = json.loads(result.stdout.split('\n')[-1])
    except Exception as e:
        print(f"Error discovering ESPHome players: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not players:
        print("No ESPHome media players found")
        sys.exit(1)
    
    # Start bridge
    bridge = ESPHomeAirPlayBridge(players, config)
    bridge.run()

if __name__ == '__main__':
    main()
