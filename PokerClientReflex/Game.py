import json
class Game:
    def __init__(self):
        self.current_round = 0
        self.players = []
        self.player_rounds = {}
        print("Initialized new Game instance.")

    def add_player(self, player_name):
        if player_name not in self.players:
            print("Adding player to game:", player_name)
            self.players.append(player_name)


    def start_new_round(self):
        print("Starting new round:", self.current_round + 1)
        self.current_round = self.current_round + 1
        for player in self.players:
            if player not in self.player_rounds:
                self.player_rounds[player] = {}
            self.player_rounds[player][self.current_round] = {'actions': [], 'bid': 0, 'card_replaced': 0, 'won': False}

    def save_player_action(self, player_name, action):
        if player_name in self.players:
            round_info = self.player_rounds[player_name][self.current_round]
            round_info['actions'].append(action)

    def save_player_bid(self, player_name, bid):
        if player_name in self.players:
            if player_name not in self.player_rounds:
                self.player_rounds[player_name] = {}
            if self.current_round not in self.player_rounds[player_name]:
                self.player_rounds[player_name][self.current_round] = {'actions': [], 'bid': 0, 'card_replaced': 0, 'won': False}
            round_info = self.player_rounds[player_name][self.current_round]
            round_info['bid'] += bid
    
    def save_player_card_replaced(self, player_name, number_of_cards):
        if player_name in self.players:
            round_info = self.player_rounds[player_name][self.current_round]
            round_info['card_replaced'] = number_of_cards
    
    def save_player_won(self, player_name):
        if player_name in self.players:
            round_info = self.player_rounds[player_name][self.current_round]
            round_info['won'] = True

    def __str__(self):
        return f"Game(current_round={self.current_round}, players={self.players}, player_rounds={self.player_rounds})"
    
    def save_to_json(self, filename='game_data.json'):
        with open(filename, 'w') as f:
            json.dump({
                'players': self.players,
                'player_rounds': self.player_rounds
            }, f, indent=4)
