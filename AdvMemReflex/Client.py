import socket
import random
import ClientBase

# IP address and port
TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024

# Agent
POKER_CLIENT_NAME = 'AdvMemReflex'
CURRENT_HAND = []


class pokerGames(object):
    def __init__(self):
        self.PlayerName = POKER_CLIENT_NAME
        self.Chips = 0
        self.CurrentHand = []
        self.Ante = 0
        self.playersCurrentBet = 0
        # Tracking dictionary for each opponent
        self.opponents = {}
        self.current_round_actions = {}  # Track actions within current round

    def track_action(self, name, action, value=0):
        """Track opponent actions for memory-based decision making"""
        if name == self.PlayerName:
            return

        if name not in self.opponents:
            # Initialize stats for a new opponent
            self.opponents[name] = {
                'total_actions': 0,
                'opens': 0,
                'raises': 0,
                'folds': 0,
                'checks': 0,
                'calls': 0,
                'all_ins': 0,
                'cards_swapped_total': 0,
                'cards_swapped_count': 0,
                'total_bet_amount': 0,
                'rounds_played': 0,
                'aggressive_actions': 0,  # opens + raises
                'passive_actions': 0,  # checks + calls
            }

        self.opponents[name]['total_actions'] += 1

        if action == 'open':
            self.opponents[name]['opens'] += 1
            self.opponents[name]['aggressive_actions'] += 1
            self.opponents[name]['total_bet_amount'] += value
        elif action == 'raise':
            self.opponents[name]['raises'] += 1
            self.opponents[name]['aggressive_actions'] += 1
            self.opponents[name]['total_bet_amount'] += value
        elif action == 'fold':
            self.opponents[name]['folds'] += 1
        elif action == 'check':
            self.opponents[name]['checks'] += 1
            self.opponents[name]['passive_actions'] += 1
        elif action == 'call':
            self.opponents[name]['calls'] += 1
            self.opponents[name]['passive_actions'] += 1
        elif action == 'all_in':
            self.opponents[name]['all_ins'] += 1
            self.opponents[name]['aggressive_actions'] += 1
        elif action == 'cards_swapped':
            self.opponents[name]['cards_swapped_total'] += value
            self.opponents[name]['cards_swapped_count'] += 1

    def get_opponent_aggression(self, name):
        """Calculate aggression ratio for an opponent (0-1 scale)"""
        if name not in self.opponents:
            return 0.5  # Default to neutral

        stats = self.opponents[name]
        total = stats['aggressive_actions'] + stats['passive_actions']

        if total == 0:
            return 0.5

        return stats['aggressive_actions'] / total

    def get_opponent_fold_rate(self, name):
        """Calculate how often an opponent folds"""
        if name not in self.opponents:
            return 0.3  # Default assumption

        stats = self.opponents[name]
        total = stats['total_actions']

        if total == 0:
            return 0.3

        return stats['folds'] / total

    def get_avg_cards_swapped(self, name):
        """Get average number of cards opponent swaps"""
        if name not in self.opponents or name not in self.opponents:
            return 2.0  # Default assumption

        stats = self.opponents[name]

        if stats['cards_swapped_count'] == 0:
            return 2.0

        return stats['cards_swapped_total'] / stats['cards_swapped_count']

    def analyze_opponents(self):
        """Get overall opponent profile"""
        if not self.opponents:
            return {'avg_aggression': 0.5, 'most_aggressive': None}

        total_aggression = sum(self.get_opponent_aggression(name) for name in self.opponents)
        avg_aggression = total_aggression / len(self.opponents)

        most_aggressive = max(self.opponents.keys(),
                              key=lambda n: self.get_opponent_aggression(n),
                              default=None)

        return {
            'avg_aggression': avg_aggression,
            'most_aggressive': most_aggressive,
            'opponent_count': len(self.opponents)
        }


def ranking(hand):
    """Evaluate hand strength (0-9, higher is better)"""
    if not hand or len(hand) != 5:
        return 0

    # Parse cards
    ranks = []
    suits = []
    for card in hand:
        if len(card) < 2:
            continue
        rank_char = card[0]
        suit_char = card[1]

        # Convert rank to number
        rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                    '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        ranks.append(rank_map.get(rank_char, 0))
        suits.append(suit_char)

    if len(ranks) != 5:
        return 0

    ranks.sort(reverse=True)
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1

    counts = sorted(rank_counts.values(), reverse=True)
    unique_suits = len(set(suits))

    # Check for straight
    is_straight = False
    if ranks[0] - ranks[4] == 4 and len(set(ranks)) == 5:
        is_straight = True
    # Check for A-2-3-4-5 straight
    if ranks == [14, 5, 4, 3, 2]:
        is_straight = True

    # Check for flush
    is_flush = (unique_suits == 1)

    # Evaluate hand
    if is_straight and is_flush:
        return 9  # Straight flush
    elif counts == [4, 1]:
        return 8  # Four of a kind
    elif counts == [3, 2]:
        return 7  # Full house
    elif is_flush:
        return 6  # Flush
    elif is_straight:
        return 5  # Straight
    elif counts == [3, 1, 1]:
        return 4  # Three of a kind
    elif counts == [2, 2, 1]:
        return 3  # Two pair
    elif counts == [2, 1, 1, 1]:
        return 2  # One pair
    else:
        return 1  # High card


def queryPlayerName(_name):
    """Gets the name of the player"""
    if _name is None:
        _name = POKER_CLIENT_NAME
    return _name


def queryOpenAction(_minimumPotAfterOpen, _playersCurrentBet, _playersRemainingChips):
    """Decide opening action based on hand strength and opponent memory"""
    print("Player requested to choose an opening action.")
    print("Current hand:", agent.CurrentHand)

    hand_strength = ranking(agent.CurrentHand)
    opponent_analysis = agent.analyze_opponents()
    avg_aggression = opponent_analysis['avg_aggression']

    # Calculate available betting range with safety margin
    bet_potential = _playersCurrentBet + _playersRemainingChips - _minimumPotAfterOpen

    # Strong hands (Two pair or better) - Open aggressively
    if hand_strength >= 3:  # Two pair or better
        if _playersCurrentBet + _playersRemainingChips > _minimumPotAfterOpen:
            # Adjust aggression based on opponent behavior
            if avg_aggression > 0.65:
                # Against aggressive opponents, be more measured
                safe_bet_max = bet_potential - 30 if bet_potential > 30 else (
                    bet_potential - 10 if bet_potential > 10 else 0)
            else:
                # Against passive opponents, bet more
                safe_bet_max = bet_potential - 20 if bet_potential > 20 else (
                    bet_potential - 10 if bet_potential > 10 else 0)

            if safe_bet_max > 0:
                amount_to_bet = random.randint(0, safe_bet_max)
                return ClientBase.BettingAnswer.ACTION_OPEN, (_minimumPotAfterOpen + amount_to_bet)
            else:
                return ClientBase.BettingAnswer.ACTION_OPEN, _minimumPotAfterOpen
        else:
            return ClientBase.BettingAnswer.ACTION_CHECK

    # Weak to moderate hands (High card or one pair)
    else:
        # Weighted choice: check more often than open
        # Adjust weights based on opponent aggression
        if avg_aggression > 0.6:
            # More cautious against aggressive players
            check_weight = 0.8
            open_weight = 0.2
        else:
            # More willing to open against passive players
            check_weight = 0.7
            open_weight = 0.3

        action_choice = random.choices(
            [ClientBase.BettingAnswer.ACTION_CHECK, ClientBase.BettingAnswer.ACTION_OPEN],
            weights=[check_weight, open_weight],
            k=1
        )[0]

        if action_choice == ClientBase.BettingAnswer.ACTION_OPEN:
            if _playersCurrentBet + _playersRemainingChips > _minimumPotAfterOpen:
                # Small bet with weak hand - keep safety margin
                safe_bet_max = bet_potential - 40 if bet_potential > 40 else (
                    bet_potential - 10 if bet_potential > 10 else 0)

                if safe_bet_max > 0:
                    amount_to_bet = random.randint(0, safe_bet_max)
                    return ClientBase.BettingAnswer.ACTION_OPEN, (_minimumPotAfterOpen + amount_to_bet)
                else:
                    return ClientBase.BettingAnswer.ACTION_CHECK
            else:
                return ClientBase.BettingAnswer.ACTION_CHECK

        return ClientBase.BettingAnswer.ACTION_CHECK


def queryCallRaiseAction(_maximumBet, _minimumAmountToRaiseTo, _playersCurrentBet, _playersRemainingChips):
    """Decide call/raise action based on hand strength and opponent behavior"""
    print("Player requested to choose a call/raise action.")
    print("Current hand:", agent.CurrentHand)

    hand_strength = ranking(agent.CurrentHand)
    opponent_analysis = agent.analyze_opponents()
    avg_aggression = opponent_analysis['avg_aggression']

    print(f"Hand strength: {hand_strength}/9")

    # Calculate raise potential with safety margin
    amount_that_can_be_raised = _playersCurrentBet + _playersRemainingChips - _minimumAmountToRaiseTo
    at_least_raise = 10 if amount_that_can_be_raised > 10 else 0
    safe_raise = amount_that_can_be_raised - 40 if amount_that_can_be_raised > 40 else at_least_raise

    # STRAIGHT OR BETTER -> Go all-in
    if hand_strength >= 5:  # Straight or better
        return ClientBase.BettingAnswer.ACTION_ALLIN

    # TWO PAIR OR BETTER (but below straight) -> Raise or Call
    elif hand_strength >= 3:  # Two pair, three of a kind, full house, four of a kind
        if _playersCurrentBet + _playersRemainingChips > _minimumAmountToRaiseTo:
            # Can afford to raise
            if at_least_raise == 0:
                return ClientBase.BettingAnswer.ACTION_CALL

            # Adjust weights based on opponent aggression
            if avg_aggression > 0.65:
                # Against aggressive opponents, be more cautious
                raise_weight = 0.5
                call_weight = 0.5
            else:
                # Against passive opponents, raise more
                raise_weight = 0.6
                call_weight = 0.4

            action_choice = random.choices(
                [ClientBase.BettingAnswer.ACTION_RAISE, ClientBase.BettingAnswer.ACTION_CALL],
                weights=[raise_weight, call_weight],
                k=1
            )[0]

            if action_choice == ClientBase.BettingAnswer.ACTION_RAISE:
                raise_amount = random.randint(0, safe_raise) + _minimumAmountToRaiseTo
                return ClientBase.BettingAnswer.ACTION_RAISE, raise_amount
            return ClientBase.BettingAnswer.ACTION_CALL
        else:
            # Can't afford to raise - fold or all-in
            action_choice = random.choices(
                [ClientBase.BettingAnswer.ACTION_FOLD, ClientBase.BettingAnswer.ACTION_ALLIN],
                weights=[0.8, 0.2],
                k=1
            )[0]
            return action_choice

    # PAIR OR WORSE -> Mostly fold, sometimes bluff
    else:
        if _playersCurrentBet + _playersRemainingChips > _minimumAmountToRaiseTo:
            # Can afford to raise - consider multiple options

            # Adjust weights based on opponent behavior
            if avg_aggression > 0.7:
                # Against very aggressive opponents, fold more often
                weights = [0.75, 0.15, 0.05, 0.05]  # fold, call, raise, all-in
            else:
                # Against passive opponents, can bluff more
                weights = [0.6, 0.2, 0.1, 0.1]

            action_choice = random.choices(
                [ClientBase.BettingAnswer.ACTION_FOLD, ClientBase.BettingAnswer.ACTION_CALL,
                 ClientBase.BettingAnswer.ACTION_RAISE, ClientBase.BettingAnswer.ACTION_ALLIN],
                weights=weights,
                k=1
            )[0]

            if action_choice == ClientBase.BettingAnswer.ACTION_RAISE:
                if at_least_raise == 0:
                    return ClientBase.BettingAnswer.ACTION_CALL
                raise_amount = random.randint(0, safe_raise) + _minimumAmountToRaiseTo
                return ClientBase.BettingAnswer.ACTION_RAISE, raise_amount
            elif action_choice == ClientBase.BettingAnswer.ACTION_CALL:
                return ClientBase.BettingAnswer.ACTION_CALL
            elif action_choice == ClientBase.BettingAnswer.ACTION_FOLD:
                return ClientBase.BettingAnswer.ACTION_FOLD
            else:
                return ClientBase.BettingAnswer.ACTION_ALLIN
        else:
            # Can't afford to raise - fold or all-in (mostly fold)
            action_choice = random.choices(
                [ClientBase.BettingAnswer.ACTION_FOLD, ClientBase.BettingAnswer.ACTION_ALLIN],
                weights=[0.8, 0.2],
                k=1
            )[0]

            if action_choice == ClientBase.BettingAnswer.ACTION_FOLD:
                return ClientBase.BettingAnswer.ACTION_FOLD
            return ClientBase.BettingAnswer.ACTION_ALLIN


def queryCardsToThrow(_hand):
    """Decide which cards to discard based on hand strength"""
    print("Requested information about what cards to throw")

    hand_strength = ranking(_hand)

    # Don't throw any cards if we have a strong hand
    if hand_strength >= 5:  # Straight or better
        return ''

    # Parse cards
    cards = []
    for card in _hand:
        if len(card) >= 2:
            rank_char = card[0]
            suit_char = card[1]
            rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                        '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
            cards.append({'card': card, 'rank': rank_map.get(rank_char, 0), 'suit': suit_char})

    if len(cards) != 5:
        return ''

    # Count ranks
    rank_counts = {}
    for c in cards:
        rank_counts[c['rank']] = rank_counts.get(c['rank'], 0) + 1

    # Strategy: Keep pairs and better, discard others
    if hand_strength >= 2:  # We have at least a pair
        # Keep the paired/tripled cards, discard others
        discard = ''
        for c in cards:
            if rank_counts[c['rank']] == 1:  # Single card
                discard += c['card'] + ' '
        return discard.strip() + ' ' if discard else ''

    else:  # High card - keep highest cards
        # Sort by rank
        cards.sort(key=lambda x: x['rank'], reverse=True)

        # Keep top 2-3 cards, discard rest
        num_to_keep = 2
        discard = ''
        for i in range(num_to_keep, 5):
            discard += cards[i]['card'] + ' '

        return discard.strip() + ' ' if discard else ''


# Info Functions
def infoNewRound(_round):
    """Called when a new round begins"""
    print('Starting Round: ' + _round)


def infoGameOver():
    """Called when the game is over"""
    print('The game is over.')


def infoPlayerChips(_playerName, _chips):
    """Called when server informs chip counts"""
    print('The player ' + _playerName + ' has ' + _chips + ' chips')


def infoAnteChanged(_ante):
    """Called when the ante changes"""
    print('The ante is: ' + _ante)


def infoForcedBet(_playerName, _forcedBet):
    """Called when a player makes forced bet"""
    print("Player " + _playerName + " made a forced bet of " + _forcedBet + " chips.")


def infoPlayerOpen(_playerName, _openBet):
    """Called when a player opens"""
    print("Player " + _playerName + " opened, bet " + _openBet + " chips.")
    agent.track_action(_playerName, 'open', int(_openBet))


def infoPlayerCheck(_playerName):
    """Called when a player checks"""
    print("Player " + _playerName + " checked.")
    agent.track_action(_playerName, 'check')


def infoPlayerRise(_playerName, _amountRaisedTo):
    """Called when a player raises"""
    print("Player " + _playerName + " raised to " + _amountRaisedTo + " chips.")
    agent.track_action(_playerName, 'raise', int(_amountRaisedTo))


def infoPlayerCall(_playerName):
    """Called when a player calls"""
    print("Player " + _playerName + " called.")
    agent.track_action(_playerName, 'call')


def infoPlayerFold(_playerName):
    """Called when a player folds"""
    print("Player " + _playerName + " folded.")
    agent.track_action(_playerName, 'fold')


def infoPlayerAllIn(_playerName, _allInChipCount):
    """Called when a player goes all-in"""
    print("Player " + _playerName + " goes all-in with " + _allInChipCount + " chips.")
    agent.track_action(_playerName, 'all_in', int(_allInChipCount))


def infoPlayerDraw(_playerName, _cardCount):
    """Called when a player exchanges cards"""
    print("Player " + _playerName + " exchanged " + _cardCount + " cards.")
    agent.track_action(_playerName, 'cards_swapped', int(_cardCount))


def infoPlayerHand(_playerName, _hand):
    """Called during showdown when hands are revealed"""
    print("Player " + _playerName + " hand " + str(_hand))


def infoRoundUndisputedWin(_playerName, _winAmount):
    """Called when a player wins undisputed"""
    print("Player " + _playerName + " won " + _winAmount + " chips undisputed.")


def infoRoundResult(_playerName, _winAmount):
    """Called when round results are announced"""
    print("Player " + _playerName + " won " + _winAmount + " chips.")


# Initialize agent
agent = pokerGames()