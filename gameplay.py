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

    def print_game_state(self, round_num):
        print(f"\n--- Round {round_num} ---")
        for player in self.players:
            print(f"{player.name}: ${player.money}, Properties: {[p.value for p in player.properties]}")
        print(f"Properties left: {len(self.property_deck)}")  


def run_game(num_players, get_back_half_rounded_up):
    game = ForSaleGame(num_players, get_back_half_rounded_up=get_back_half_rounded_up)
    
    print("Starting the game!")
    print(f"Number of players: {num_players}")
    print(f"Get back half rounded up: {get_back_half_rounded_up}")
    
    game.buying_phase()
    
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
