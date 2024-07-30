#!/usr/bin/env python3
import sys
import json
import random

def make_bid(player_data, game_state, current_bid, previous_bid):
    if player_data["money"] > current_bid:
        if random.choice([True, False]):  # 50% chance to raise bid
            return random.randint(max(current_bid + 1, previous_bid + 1), player_data["money"])
        else:
            return previous_bid
    return previous_bid

def choose_property_to_sell(player_data, game_state):
    properties = player_data["properties"]
    available_checks = game_state["available_properties"]
    
    best_check_value = max(available_checks)
    worst_check_value = min(available_checks)
    check_range = best_check_value - worst_check_value

    best_property_value = max(properties)
    worst_property_value = min(properties)
    property_range = best_property_value - worst_property_value

    if property_range == 0:  # All properties have the same value
        return properties[0]

    target_value = worst_property_value + (property_range * (best_check_value - worst_check_value) / check_range)
    
    return min(properties, key=lambda p: abs(p - target_value))

if __name__ == "__main__":
    try:
        input_data = json.loads(sys.stdin.read())
        action = input_data["action"]
        game_state = input_data["game_state"]
        player_data = input_data["player_data"]
        
        if action == "bid":
            current_bid = input_data["current_bid"]
            previous_bid = input_data["previous_bid"]
            result = {"bid": make_bid(player_data, game_state, current_bid, previous_bid)}
        elif action == "sell":
            result = {"property_to_sell": choose_property_to_sell(player_data, game_state)}
        else:
            result = {"error": "Invalid action"}
        
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
