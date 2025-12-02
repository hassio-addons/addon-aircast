#!/usr/bin/env python3
"""
ESPHome Media Player Discovery Script
Queries Home Assistant API for ESPHome media players
"""
import os
import sys
import json
import requests
from typing import List, Dict

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
HA_API_URL = 'http://supervisor/core/api'

def get_headers():
    """Get authorization headers for HA API"""
    return {
        'Authorization': f'Bearer {SUPERVISOR_TOKEN}',
        'Content-Type': 'application/json',
    }

def discover_esphome_players() -> List[Dict]:
    """
    Discover ESPHome media players via Home Assistant API
    Returns list of media player entities
    """
    try:
        # Get all states
        response = requests.get(
            f'{HA_API_URL}/states',
            headers=get_headers(),
            timeout=10
        )
        response.raise_for_status()
        states = response.json()
        
        # Filter for ESPHome media players
        esphome_players = []
        for entity in states:
            entity_id = entity.get('entity_id', '')
            attributes = entity.get('attributes', {})
            
            # Check if it's a media player from ESPHome
            if (entity_id.startswith('media_player.') and
                attributes.get('attribution') == 'ESPHome'):
                
                esphome_players.append({
                    'entity_id': entity_id,
                    'friendly_name': attributes.get('friendly_name', entity_id),
                    'state': entity.get('state'),
                    'supported_features': attributes.get('supported_features', 0)
                })
        
        return esphome_players
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Home Assistant API: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error discovering ESPHome players: {e}", file=sys.stderr)
        return []

def main():
    """Main function"""
    players = discover_esphome_players()
    
    if not players:
        print("No ESPHome media players found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(players)} ESPHome media player(s):")
    for player in players:
        print(f"  - {player['friendly_name']} ({player['entity_id']})")
    
    # Output as JSON for consumption by other scripts
    print(json.dumps(players, indent=2))

if __name__ == '__main__':
    main()
