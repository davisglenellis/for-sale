import random

# Properties players bid on
class Property:
    def __init__(self, value):
        self.value = value

# Checks players sell properties for
class Check:
    def __init__(self, value):
        self.value = value

# Generic player class
class Player:
    def __init__(self, name):
        self.name = name
        self.money = 14
        self.properties = []
        self.checks = []

    def make_bid(self, current_bid, available_properties, previous_bid):
        # For now, let's make a simple random bid or stick with the previous bid
        if self.money > current_bid:
            if random.choice([True, False]):  # 50% chance to raise bid
                return current_bid + 1
            else:
                return previous_bid
        return previous_bid  # Can't raise, so stick with previous bid
    
    def choose_property_to_sell(self, available_checks):
        # Simple AI: Choose the property that best matches the relative position of the best available check
        if not self.properties:
            raise ValueError(f"{self.name} has no properties to sell!")
        
        best_check_value = max(check.value for check in available_checks)
        worst_check_value = min(check.value for check in available_checks)
        check_range = best_check_value - worst_check_value

        best_property_value = max(prop.value for prop in self.properties)
        worst_property_value = min(prop.value for prop in self.properties)
        property_range = best_property_value - worst_property_value

        if property_range == 0:  # All properties have the same value
            return self.properties[0]

        target_value = worst_property_value + (property_range * (best_check_value - worst_check_value) / check_range)
        
        return min(self.properties, key=lambda p: abs(p.value - target_value))
    
class GameState:
    def __init__(self, available_properties, player_bids, passed_players, players):
        self.available_properties = available_properties
        self.player_bids = player_bids
        self.passed_players = passed_players
        self.players = players

# Initialize game state
class ForSaleGame:
    def __init__(self, num_players, get_back_half_rounded_up):
        self.players = [Player(f"Player {i+1}") for i in range(num_players)]
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
            # self.print_game_state(round_num)
            
            # Reveal properties
            available_properties = [self.property_deck.pop() for _ in range(len(self.players))]
            available_properties.sort(key=lambda x: x.value)

            # Initialize auction
            highest_bidder = None
            current_bid = 0
            passed_players = []
            player_bids = {player: 0 for player in self.players}

            while len(passed_players) < len(self.players) - 1:
                # Debugging step
                # self.print_game_state(round_num)
                player = self.players[self.current_player]
                if player not in passed_players:
                    # Copy current game state
                    game_state = GameState(
                        available_properties.copy(),
                        player_bids.copy(),
                        passed_players.copy(),
                        self.players
                    )

                    # Get player's bid - passing should use previous bid from same player
                    player_bid = player.make_bid(current_bid, game_state, player_bids[player])

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


def run_game(num_players, get_back_half_rounded_up):
    game = ForSaleGame(num_players, get_back_half_rounded_up=get_back_half_rounded_up)
    
    print("Starting the game!")
    print(f"Number of players: {num_players}")
    print(f"Get back half rounded up: {get_back_half_rounded_up}")
    
    game.buying_phase()
    game.selling_phase()
    game.print_game_state()
    print("Winner: " + str(game.winner().name))
    
    print("\nGame Over!")

def main():
    random.seed(42)  # Set a seed for reproducibility
    num_games = 1
    num_players = 5
    get_back_half_rounded_up = False

    for i in range(num_games):
        print(f"\n==================")
        print(f"Running game {i+1}/{num_games}")
        print(f"==================")
        run_game(num_players, get_back_half_rounded_up)

if __name__ == "__main__":
    main()
