#!/usr/bin/env python3
"""
Shairport-Sync Play Handler
Handles audio streaming from Shairport-Sync to ESPHome via Home Assistant
Called by Shairport-Sync when playback starts/stops
"""
import os
import sys
import json
import asyncio
import threading
from pathlib import Path
import requests
from typing import Optional
import subprocess

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
HA_API_URL = 'http://supervisor/core/api'

class AudioStreamHandler:
    """Handles streaming audio from pipe to ESPHome device"""
    
    def __init__(self, entity_id: str, pipe_path: str, port: int):
        self.entity_id = entity_id
        self.pipe_path = pipe_path
        self.port = port
        self.stream_url = f"http://localhost:{7000 + port}/stream.wav"
        self.ffmpeg_process: Optional[subprocess.Popen] = None
        self.http_server_process: Optional[subprocess.Popen] = None
        
    def get_local_ip(self) -> str:
        """Get the local IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def start_http_server(self):
        """Start simple HTTP server to serve the audio stream"""
        port = 7000 + self.port
        wav_file = f"/tmp/stream_{self.entity_id.replace('.', '_')}.wav"
        
        # Start FFmpeg to read from pipe and write to WAV file
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 's16le',           # Input format: signed 16-bit little-endian PCM
            '-ar', '44100',          # Sample rate: 44.1 kHz
            '-ac', '2',              # Channels: stereo
            '-i', self.pipe_path,    # Input: named pipe
            '-f', 'wav',             # Output format: WAV
            '-y',                    # Overwrite output
            wav_file                 # Output file
        ]
        
        print(f"Starting FFmpeg: {' '.join(ffmpeg_cmd)}", file=sys.stderr)
        
        self.ffmpeg_process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Start simple HTTP server using Python
        http_cmd = [
            'python3', '-m', 'http.server',
            str(port),
            '--directory', '/tmp',
            '--bind', '0.0.0.0'
        ]
        
        print(f"Starting HTTP server on port {port}", file=sys.stderr)
        
        self.http_server_process = subprocess.Popen(
            http_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give servers time to start
        import time
        time.sleep(1)
    
    def stop_servers(self):
        """Stop FFmpeg and HTTP server"""
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except:
                self.ffmpeg_process.kill()
        
        if self.http_server_process:
            try:
                self.http_server_process.terminate()
                self.http_server_process.wait(timeout=5)
            except:
                self.http_server_process.kill()
    
    def play_on_esphome(self):
        """Send play_media command to ESPHome device via HA API"""
        local_ip = self.get_local_ip()
        stream_url = f"http://{local_ip}:{7000 + self.port}/stream_{self.entity_id.replace('.', '_')}.wav"
        
        print(f"Sending play command to {self.entity_id} with URL: {stream_url}", file=sys.stderr)
        
        try:
            payload = {
                'entity_id': self.entity_id,
                'media_content_id': stream_url,
                'media_content_type': 'music',
                'extra': {
                    'bypass_proxy': True  # Tell ESPHome to skip its proxy
                }
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
            print(f"✓ Started playback on {self.entity_id}", file=sys.stderr)
            return True
            
        except Exception as e:
            print(f"✗ Error playing on {self.entity_id}: {e}", file=sys.stderr)
            return False
    
    def stop_on_esphome(self):
        """Send stop command to ESPHome device via HA API"""
        try:
            payload = {'entity_id': self.entity_id}
            
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
            print(f"✓ Stopped playback on {self.entity_id}", file=sys.stderr)
            return True
            
        except Exception as e:
            print(f"✗ Error stopping {self.entity_id}: {e}", file=sys.stderr)
            return False

def handle_start(entity_id: str, pipe_path: str, port: int):
    """Handle playback start"""
    print(f"Playback starting for {entity_id}", file=sys.stderr)
    
    handler = AudioStreamHandler(entity_id, pipe_path, int(port))
    
    # Start servers and begin playback
    handler.start_http_server()
    handler.play_on_esphome()
    
    # Store handler info for stop command
    state_file = f"/tmp/shairport_state_{entity_id.replace('.', '_')}.json"
    with open(state_file, 'w') as f:
        json.dump({
            'entity_id': entity_id,
            'pipe_path': pipe_path,
            'port': port,
            'ffmpeg_pid': handler.ffmpeg_process.pid if handler.ffmpeg_process else None,
            'http_pid': handler.http_server_process.pid if handler.http_server_process else None
        }, f)

def handle_stop(entity_id: str):
    """Handle playback stop"""
    print(f"Playback stopping for {entity_id}", file=sys.stderr)
    
    # Read state file
    state_file = f"/tmp/shairport_state_{entity_id.replace('.', '_')}.json"
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Stop ESPHome playback
        handler = AudioStreamHandler(entity_id, state['pipe_path'], int(state['port']))
        handler.ffmpeg_process = subprocess.Popen(['true'])  # Dummy
        handler.ffmpeg_process.pid = state.get('ffmpeg_pid')
        handler.http_server_process = subprocess.Popen(['true'])  # Dummy
        handler.http_server_process.pid = state.get('http_pid')
        
        handler.stop_on_esphome()
        handler.stop_servers()
        
        # Clean up state file
        os.remove(state_file)
        
    except Exception as e:
        print(f"✗ Error in stop handler: {e}", file=sys.stderr)

def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: shairport-play-handler.py <start|stop> <entity_id> [pipe_path] [port]", file=sys.stderr)
        sys.exit(1)
    
    command = sys.argv[1]
    entity_id = sys.argv[2]
    
    if command == 'start':
        if len(sys.argv) < 5:
            print("start command requires pipe_path and port", file=sys.stderr)
            sys.exit(1)
        pipe_path = sys.argv[3]
        port = sys.argv[4]
        handle_start(entity_id, pipe_path, port)
    elif command == 'stop':
        handle_stop(entity_id)
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
