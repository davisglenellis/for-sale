import random
import subprocess
import json
from agent_interface import call_agent, PropertyEncoder

# Properties players bid on
class Property:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"value": self.value}

# Checks players sell properties for
class Check:
    def __init__(self, value):
        self.value = value

    def to_dict(self):
        return {"value": self.value}

# Generic player class
class Player:
    def __init__(self, name, agent_script):
        self.name = name
        self.money = 14
        self.properties = []
        self.checks = []
        self.agent_script = agent_script

    def to_dict(self):
        return {
            "name": self.name,
            "money": self.money,
            "properties": [prop.to_dict() for prop in self.properties],
            "checks": [check.to_dict() for check in self.checks]
        }

    def make_bid(self, current_bid, game_state, previous_bid):
        result = call_agent(self.agent_script, "bid", game_state, self, current_bid, previous_bid)
        return result["bid"]

    def choose_property_to_sell(self, available_checks):
        if not self.properties:
            print(f"Warning: {self.name} has no properties to sell!")
            return None

        temp_game_state = GameState(available_checks, {}, [], [self])
        try:
            result = call_agent(self.agent_script, "sell", temp_game_state, self)
            property_value = result["property_to_sell"]
            chosen_property = next((p for p in self.properties if p.value == property_value), None)
            if chosen_property is None:
                print(f"Warning: {self.name} chose an invalid property to sell. Choosing randomly.")
                chosen_property = random.choice(self.properties)
            return chosen_property
        except Exception as e:
            print(f"Error in choose_property_to_sell for {self.name}: {e}")
            # Fallback: return a random property
            return random.choice(self.properties) if self.properties else None
    
class GameState:
    def __init__(self, available_properties, player_bids, passed_players, players):
        self.available_properties = available_properties
        self.player_bids = player_bids
        self.passed_players = passed_players
        self.players = players

    def to_dict(self):
        return {
            "available_properties": [prop.to_dict() for prop in self.available_properties],
            "player_bids": {player.name: bid for player, bid in self.player_bids.items()},
            "passed_players": [player.name for player in self.passed_players],
            "players": [player.to_dict() for player in self.players]
        }

# Initialize game state
class ForSaleGame:
    def __init__(self, players, get_back_half_rounded_up):
        self.players = players
        self.get_back_half_rounded_up = get_back_half_rounded_up
        self.current_player = 0

        # Property values 1 - 30
        self.property_deck = [Property(value) for value in range(1, 31)]

        # Check values 0 - 15, excluding 1, 2 of every number
        self.check_deck = [Check(value) for value in range(16) if value != 1 for _ in range(2)]

        # Shuffle decks
        random.shuffle(self.property_deck)
        random.shuffle(self.check_deck)

    # Players buy properties
    def buying_phase(self):
        round_num = 1
        
        while len(self.property_deck) >= len(self.players):

            # Debugging step
            self.print_game_state()
            
            # Reveal properties
            available_properties = [self.property_deck.pop() for _ in range(len(self.players))]
            available_properties.sort(key=lambda x: x.value)


            highest_bidder = self.players[(self.current_player - 1) % len(self.players)]
            current_bid = 0
            passed_players = []
            player_bids = {player: 0 for player in self.players}

            while len(passed_players) < len(self.players) - 1:
                player = self.players[self.current_player]
                if player not in passed_players:
                    game_state = GameState(
                        available_properties.copy(),
                        player_bids,
                        passed_players.copy(),
                        self.players
                    )
                    try:
                        player_bid = player.make_bid(current_bid, game_state, player_bids[player])
                    except Exception as e:
                        print("Error in make_bid:")
                        print(json.dumps(game_state.__dict__, cls=PropertyEncoder, indent=2))
                        raise e

                    if player_bid > current_bid:
                        current_bid = player_bid
                        highest_bidder = player
                        player_bids[player] = player_bid
                    else:
                        # Player passes
                        passed_players.append(player)
                        money_back = self.calculate_money_back(player_bid)
                        player.money -= (player_bid - money_back)
                        player.properties.append(available_properties.pop(0))

                # This also makes sure highest bidder is first bidder in next round
                self.current_player = (self.current_player + 1) % len(self.players)

            # Highest bidder gets the final property
            highest_bidder.money -= current_bid
            highest_bidder.properties.append(available_properties.pop())
        
    # Money back rounded up or down
    def calculate_money_back(self, bid):
        if self.get_back_half_rounded_up:
            return (bid + 1) // 2
        else:
            return bid // 2
        
    def selling_phase(self):
        rounds = len(self.players[0].properties)  # All players should have the same number of properties
        
        for round in range(rounds):
            # Reveal checks
            available_checks = [self.check_deck.pop() for _ in range(len(self.players))]
            available_checks.sort(key=lambda x: x.value, reverse=True)

            # Players choose properties to sell
            offers = []
            for player in self.players:
                property_to_sell = player.choose_property_to_sell(available_checks)
                offers.append((player, property_to_sell))
                player.properties.remove(property_to_sell)
            
            # Sort offers by property value, highest first
            offers.sort(key=lambda x: x[1].value, reverse=True)

            # Distribute checks
            for (player, property), check in zip(offers, available_checks):
                player.checks.append(check)

    def winner(self):
        return max(self.players, key=lambda p: sum(check.value for check in p.checks) + p.money)

    def print_game_state(self):
        for player in self.players:
            print(f"{player.name}: ${player.money}, Properties: {[p.value for p in player.properties]}")
            print(f"Checks: {[p.value for p in player.checks]}")


def run_game(player_agents, get_back_half_rounded_up):
    players = [Player(f"Player {i+1}", agent) for i, agent in enumerate(player_agents)]
    game = ForSaleGame(players, get_back_half_rounded_up=get_back_half_rounded_up)

    print("Starting the game!")
    print(f"Number of players: {len(player_agents)}")
    print(f"Get back half rounded up: {get_back_half_rounded_up}")
    
    game.buying_phase()
    game.selling_phase()
    game.print_game_state()
    print("Winner: " + str(game.winner().name))
    
    print("\nGame Over!")

def main():
    random.seed(42)  # Set a seed for reproducibility
    num_games = 5
    
    player_agents = [
        "./random_ai.py",
        "./random_ai.py",
        "./random_ai.py",
        "./random_ai.py",
        "./random_ai.py",
    ]

    get_back_half_rounded_up = False

    for i in range(num_games):
        print(f"\n==================")
        print(f"Running game {i+1}/{num_games}")
        print(f"==================")
        run_game(player_agents, get_back_half_rounded_up)

if __name__ == "__main__":
    main()
