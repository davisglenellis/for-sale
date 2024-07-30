import subprocess
import json

class PropertyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'value'):
            return obj.value
        if hasattr(obj, 'name'):
            return obj.name
        return super().default(obj)

def serialize_game_state(game_state):
    return {
        "available_properties": game_state.available_properties,
        "player_bids": {player.name if hasattr(player, 'name') else str(player): bid 
                        for player, bid in game_state.player_bids.items()},
        "passed_players": game_state.passed_players,
        "players": game_state.players
    }

def call_agent(agent_script, action, game_state, player, current_bid=None, previous_bid=None):
    serialized_state = serialize_game_state(game_state)
    player_data = {
        "money": player.money,
        "properties": player.properties,
    }
    
    input_data = {
        "action": action,
        "game_state": serialized_state,
        "player_data": player_data,
        "current_bid": current_bid,
        "previous_bid": previous_bid
    }
    
    input_json = json.dumps(input_data, cls=PropertyEncoder)
    
    result = subprocess.run(
        [agent_script],
        input=input_json,
        capture_output=True,
        text=True
    )
    
    return json.loads(result.stdout)
