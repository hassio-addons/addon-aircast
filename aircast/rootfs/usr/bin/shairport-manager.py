#!/usr/bin/env python3
"""
Shairport-Sync Manager for ESPHome Devices
Creates and manages Shairport-Sync instances for ESPHome media players
"""
import os
import sys
import json
import time
import subprocess
import signal
import tempfile
from pathlib import Path
from typing import Dict, List
import requests

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
HA_API_URL = 'http://supervisor/core/api'
SHAIRPORT_CONFIG_DIR = '/tmp/shairport-configs'
STREAM_PORT_BASE = 7000

class ShairportSyncManager:
    """Manages Shairport-Sync instances for ESPHome devices"""
    
    def __init__(self, esphome_players: List[Dict], config: Dict):
        self.esphome_players = esphome_players
        self.config = config
        self.processes = {}
        self.stream_pipes = {}
        Path(SHAIRPORT_CONFIG_DIR).mkdir(exist_ok=True)
        
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
    
    def create_shairport_config(self, player: Dict, port: int) -> str:
        """Create Shairport-Sync configuration file for a player"""
        player_name = player['friendly_name']
        config_path = f"{SHAIRPORT_CONFIG_DIR}/{player['entity_id'].replace('.', '_')}.conf"
        pipe_path = f"/tmp/shairport_{player['entity_id'].replace('.', '_')}.pipe"
        
        # Create named pipe for audio output
        if os.path.exists(pipe_path):
            os.remove(pipe_path)
        os.mkfifo(pipe_path)
        self.stream_pipes[player['entity_id']] = pipe_path
        
        config_content = f"""
general = {{
    name = "{player_name}";
    output_backend = "pipe";
    mdns_backend = "avahi";
    port = {5000 + port};
    interpolation = "soxr";
}};

sessioncontrol = {{
    session_timeout = 20;
    allow_session_interruption = "yes";
    run_this_before_play_begins = "/usr/bin/python3 /usr/bin/shairport-play-handler.py start {player['entity_id']} {pipe_path} {port}";
    run_this_after_play_ends = "/usr/bin/python3 /usr/bin/shairport-play-handler.py stop {player['entity_id']}";
    wait_for_completion = "no";
}};

alsa = {{
}};

pipe = {{
    name = "{pipe_path}";
}};

metadata = {{
    enabled = "yes";
    include_cover_art = "no";
}};
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        return config_path
    
    def start_shairport_instance(self, player: Dict, port: int) -> subprocess.Popen:
        """Start a Shairport-Sync instance for a player"""
        config_path = self.create_shairport_config(player, port)
        
        cmd = [
            'shairport-sync',
            '-c', config_path,
            '-v',  # verbose mode for debugging
        ]
        
        print(f"Starting Shairport-Sync for {player['friendly_name']}")
        print(f"Command: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
    
    def start_all(self):
        """Start Shairport-Sync instances for all ESPHome players"""
        for idx, player in enumerate(self.esphome_players):
            try:
                process = self.start_shairport_instance(player, idx)
                self.processes[player['entity_id']] = process
                print(f"✓ Started AirPlay receiver for {player['friendly_name']}")
            except Exception as e:
                print(f"✗ Failed to start Shairport-Sync for {player['friendly_name']}: {e}")
    
    def stop_all(self):
        """Stop all Shairport-Sync instances"""
        print("\nStopping all Shairport-Sync instances...")
        for entity_id, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✓ Stopped {entity_id}")
            except Exception as e:
                print(f"✗ Error stopping {entity_id}: {e}")
                try:
                    process.kill()
                except:
                    pass
        
        # Clean up pipes
        for pipe_path in self.stream_pipes.values():
            try:
                if os.path.exists(pipe_path):
                    os.remove(pipe_path)
            except:
                pass
    
    def monitor(self):
        """Monitor running processes and restart if needed"""
        while True:
            for entity_id, process in list(self.processes.items()):
                if process.poll() is not None:
                    print(f"⚠ Shairport-Sync for {entity_id} died, restarting...")
                    # Find the player
                    player = next(p for p in self.esphome_players if p['entity_id'] == entity_id)
                    idx = self.esphome_players.index(player)
                    try:
                        new_process = self.start_shairport_instance(player, idx)
                        self.processes[entity_id] = new_process
                    except Exception as e:
                        print(f"✗ Failed to restart: {e}")
            
            time.sleep(5)

def discover_esphome_players() -> List[Dict]:
    """Discover ESPHome media players via Home Assistant API"""
    try:
        result = subprocess.run(
            ['/usr/bin/esphome-discovery.py'],
            capture_output=True,
            text=True,
            check=True
        )
        # The script prints info and then JSON on the last line
        lines = result.stdout.strip().split('\n')
        json_line = lines[-1]
        return json.loads(json_line)
    except Exception as e:
        print(f"Error discovering ESPHome players: {e}", file=sys.stderr)
        return []

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
    players = discover_esphome_players()
    
    if not players:
        print("No ESPHome media players found")
        sys.exit(1)
    
    print(f"\nFound {len(players)} ESPHome media player(s)")
    for player in players:
        print(f"  • {player['friendly_name']} ({player['entity_id']})")
    
    # Create and start manager
    manager = ShairportSyncManager(players, config)
    
    # Handle shutdown gracefully
    def signal_handler(signum, frame):
        print("\nReceived shutdown signal")
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start all Shairport-Sync instances
    manager.start_all()
    
    print(f"\n{'='*60}")
    print("All AirPlay receivers are now running!")
    print("You should see them appear on your iOS/Mac devices")
    print(f"{'='*60}\n")
    
    # Monitor processes
    try:
        manager.monitor()
    except KeyboardInterrupt:
        manager.stop_all()

if __name__ == '__main__':
    main()
