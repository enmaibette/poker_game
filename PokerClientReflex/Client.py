import socket
import random
import ClientBase
from enum import Enum

# IP address and port
TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024

class TypeOfHand(Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

# Agent
POKER_CLIENT_NAME = 'ReflexAgent'
CURRENT_HAND = []

class pokerGames(object):
    def __init__(self):
        self.PlayerName = POKER_CLIENT_NAME
        self.Chips = 0
        self.CurrentHand = []
        self.Ante = 0
        self.playersCurrentBet = 0

'''
* Gets the name of the player.
* @return  The name of the player as a single word without space. <code>null</code> is not a valid answer.
'''
def queryPlayerName(_name):
    if _name is None:
        _name = POKER_CLIENT_NAME
    return _name

'''
* Modify queryOpenAction() and add your strategy here
* Called during the betting phases of the game when the player needs to decide what open
* action to choose.
* @param minimumPotAfterOpen   the total minimum amount of chips to put into the pot if the answer action is
*                              {@link BettingAnswer#ACTION_OPEN}.
* @param playersCurrentBet     the amount of chips the player has already put into the pot (dure to the forced bet).
* @param playersRemainingChips the number of chips the player has not yet put into the pot.
* @return                      An answer to the open query. The answer action must be one of
*                              {@link BettingAnswer#ACTION_OPEN}, {@link BettingAnswer#ACTION_ALLIN} or
*                              {@link BettingAnswer#ACTION_CHECK }. If the action is open, the answers
*                              amount of chips in the anser must be between <code>minimumPotAfterOpen</code>
*                              and the players total amount of chips (the amount of chips alrady put into
*                              pot plus the remaining amount of chips).
'''
def queryOpenAction(_minimumPotAfterOpen, _playersCurrentBet, _playersRemainingChips):
    print("Player requested to choose an opening action.")

    type_of_hand = identify_hand(CURRENT_HAND)
    
    if type_of_hand.value >= TypeOfHand.TWO_PAIR.value:
        if _playersCurrentBet + _playersRemainingChips > _minimumPotAfterOpen:
            bet_p = _playersCurrentBet + _playersRemainingChips - _minimumPotAfterOpen
            safe_bet_max = bet_p - 30 if _playersCurrentBet + _playersRemainingChips - _minimumPotAfterOpen > 30 else (bet_p - 10 if bet_p > 10 else 0)
            amount_that_can_be_bet = random.randint(0, safe_bet_max)
            return ClientBase.BettingAnswer.ACTION_OPEN, (random.randint(0, amount_that_can_be_bet) + _minimumPotAfterOpen)
    else:
        action_choice = random.choices([ClientBase.BettingAnswer.ACTION_CHECK, ClientBase.BettingAnswer.ACTION_OPEN], weights=[0.7, 0.3], k=1)[0]
        if action_choice == ClientBase.BettingAnswer.ACTION_OPEN:
            if _playersCurrentBet + _playersRemainingChips > _minimumPotAfterOpen:
                bet_p = _playersCurrentBet + _playersRemainingChips - _minimumPotAfterOpen
                safe_bet_max = bet_p - 40 if bet_p > 40 else (bet_p - 10 if bet_p > 10 else 0)
                amount_that_can_be_bet = random.randint(0, safe_bet_max)
                return ClientBase.BettingAnswer.ACTION_OPEN, (random.randint(0, amount_that_can_be_bet) + _minimumPotAfterOpen)
    
    return ClientBase.BettingAnswer.ACTION_CHECK

'''
* Modify queryCallRaiseAction() and add your strategy here
* Called during the betting phases of the game when the player needs to decide what call/raise
* action to choose.
* @param maximumBet                the maximum number of chips one player has already put into the pot.
* @param minimumAmountToRaiseTo    the minimum amount of chips to bet if the returned answer is {@link BettingAnswer#ACTION_RAISE}.
* @param playersCurrentBet         the number of chips the player has already put into the pot.
* @param playersRemainingChips     the number of chips the player has not yet put into the pot.
* @return                          An answer to the call or raise query. The answer action must be one of
*                                  {@link BettingAnswer#ACTION_FOLD}, {@link BettingAnswer#ACTION_CALL},
*                                  {@link BettingAnswer#ACTION_RAISE} or {@link BettingAnswer#ACTION_ALLIN }.
*                                  If the players number of remaining chips is less than the maximum bet and
*                                  the players current bet, the call action is not available. If the players
*                                  number of remaining chips plus the players current bet is less than the minimum
*                                  amount of chips to raise to, the raise action is not available. If the action
*                                  is raise, the answers amount of chips is the total amount of chips the player
*                                  puts into the pot and must be between <code>minimumAmountToRaiseTo</code> and
*                                  <code>playersCurrentBet+playersRemainingChips</code>.
'''
def queryCallRaiseAction(_maximumBet, _minimumAmountToRaiseTo, _playersCurrentBet, _playersRemainingChips):
    print("Player requested to choose a call/raise action.")

    # handcards > straight -> all in 
    # handcards >= 2 pair -> raise or call (randomness)
    # handcards <= pair -> fold or call, raise, all in (randomness)
    type_of_hand = identify_hand(CURRENT_HAND)

    if type_of_hand.value >= TypeOfHand.STRAIGHT.value:
        return ClientBase.BettingAnswer.ACTION_ALLIN
    elif type_of_hand.value >= TypeOfHand.TWO_PAIR.value:
        action_choice = random.choices([ClientBase.BettingAnswer.ACTION_RAISE, ClientBase.BettingAnswer.ACTION_CALL], weights=[0.6, 0.4], k=1)[0]
        if _playersCurrentBet + _playersRemainingChips > _minimumAmountToRaiseTo:
            amount_that_can_be_raised = _playersCurrentBet + _playersRemainingChips - _minimumAmountToRaiseTo
            at_least_raise = 10 if amount_that_can_be_raised > 10 else 0
            if at_least_raise == 0:
                return ClientBase.BettingAnswer.ACTION_CALL
            safe_raise = amount_that_can_be_raised - 40 if amount_that_can_be_raised > 40 else at_least_raise
            if action_choice == ClientBase.BettingAnswer.ACTION_RAISE:
                return ClientBase.BettingAnswer.ACTION_RAISE, (random.randint(0, safe_raise) + _minimumAmountToRaiseTo)
            return ClientBase.BettingAnswer.ACTION_CALL
        else: 
            action_choice = random.choices([ClientBase.BettingAnswer.ACTION_FOLD, ClientBase.BettingAnswer.ACTION_ALLIN], weights=[0.8, 0.2], k=1)[0]
            return action_choice
    else:
        action_choice = random.choices([ClientBase.BettingAnswer.ACTION_FOLD, ClientBase.BettingAnswer.ACTION_ALLIN], weights=[0.8, 0.2], k=1)[0]
        if _playersCurrentBet + _playersRemainingChips > _minimumAmountToRaiseTo:
            action_choice = random.choices([ClientBase.BettingAnswer.ACTION_FOLD, ClientBase.BettingAnswer.ACTION_CALL, ClientBase.BettingAnswer.ACTION_RAISE, ClientBase.BettingAnswer.ACTION_ALLIN], weights=[0.6, 0.2, 0.1, 0.1], k=1)[0]
            amount_that_can_be_raised = _playersCurrentBet + _playersRemainingChips - _minimumAmountToRaiseTo
            at_least_raise = 10 if amount_that_can_be_raised > 10 else 0
            if at_least_raise == 0:
                return ClientBase.BettingAnswer.ACTION_CALL
            safe_raise = amount_that_can_be_raised - 40 if amount_that_can_be_raised > 40 else at_least_raise
            if action_choice == ClientBase.BettingAnswer.ACTION_RAISE:
                return ClientBase.BettingAnswer.ACTION_RAISE, (random.randint(0, safe_raise) + _minimumAmountToRaiseTo)
            elif action_choice == ClientBase.BettingAnswer.ACTION_CALL:
                return ClientBase.BettingAnswer.ACTION_CALL
        if action_choice == ClientBase.BettingAnswer.ACTION_FOLD:
            return ClientBase.BettingAnswer.ACTION_FOLD
    return ClientBase.BettingAnswer.ACTION_ALLIN


def card_value(rank):
    if rank.isdigit():
        return int(rank)
    else:
        if rank == 'T':
            return 10
        elif rank == 'J':
            return 11
        elif rank == 'Q':
            return 12
        elif rank == 'K':
            return 13
        elif rank == 'A':
            return 14


           
    ''' HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10
    '''
def identify_cards_in_hand(hand: list[str]):
    ranks = [card[0] for card in hand]
    suits = [card[-1] for card in hand]
    value_ranks = [card_value(rank) for rank in ranks]
    value_ranks.sort()
    return ranks, suits, value_ranks
# identify hand category using IF-THEN rule
def identify_hand(hand):
    type_of_hand = None
    ranks, suits, value_ranks = identify_cards_in_hand(hand)
    if suits.count(suits[0]) == 5:
        if ranks == ['10', 'J', 'Q', 'K', 'A']:
            type_of_hand = TypeOfHand.ROYAL_FLUSH
    elif suits.count(suits[0]) == 5:
        new_ranks_ace_low = [1 if rank == 14 else rank for rank in value_ranks]
        new_ranks_ace_low.sort()
        if value_ranks == [value_ranks[0], value_ranks[0]+1, value_ranks[0]+2, value_ranks[0]+3, value_ranks[0]+4]:
            type_of_hand = TypeOfHand.STRAIGHT_FLUSH
        elif new_ranks_ace_low == [new_ranks_ace_low[0], new_ranks_ace_low[0]+1, new_ranks_ace_low[0]+2, new_ranks_ace_low[0]+3, new_ranks_ace_low[0]+4]:
            type_of_hand = TypeOfHand.STRAIGHT_FLUSH
    elif value_ranks.count(value_ranks[0]) == 4 or value_ranks.count(value_ranks[1]) == 4:
        type_of_hand = TypeOfHand.FOUR_OF_A_KIND
    elif (value_ranks.count(value_ranks[0]) == 3 and value_ranks.count(value_ranks[3]) == 2) or (value_ranks.count(value_ranks[0]) == 2 and value_ranks.count(value_ranks[3]) == 3):
        type_of_hand = TypeOfHand.FULL_HOUSE
    elif suits.count(suits[0]) == 5:
        type_of_hand = TypeOfHand.FLUSH
    elif value_ranks == [value_ranks[0], value_ranks[0]+1, value_ranks[0]+2, value_ranks[0]+3, value_ranks[0]+4]:
        type_of_hand = TypeOfHand.STRAIGHT
    elif value_ranks.count(value_ranks[0]) == 3 or value_ranks.count(value_ranks[1]) == 3 or value_ranks.count(value_ranks[2]) == 3:
        type_of_hand = TypeOfHand.THREE_OF_A_KIND
    elif (value_ranks.count(value_ranks[0]) == 2 and value_ranks.count(value_ranks[2]) == 2) or (value_ranks.count(value_ranks[0]) == 2 and value_ranks.count(value_ranks[4]) == 2) or (value_ranks.count(value_ranks[2]) == 2 and value_ranks.count(value_ranks[4]) == 2):
        type_of_hand = TypeOfHand.TWO_PAIR
    elif (value_ranks.count(value_ranks[0]) == 2 or value_ranks.count(value_ranks[2]) == 2 or value_ranks.count(value_ranks[3]) == 2):
        type_of_hand = TypeOfHand.ONE_PAIR
    else:
        type_of_hand = TypeOfHand.HIGH_CARD
          

    return type_of_hand

'''
* Modify queryCardsToThrow() and add your strategy to throw cards
* Called during the draw phase of the game when the player is offered to throw away some
* (possibly all) of the cards on hand in exchange for new.
* @return  An array of the cards on hand that should be thrown away in exchange for new,
*          or <code>null</code> or an empty array to keep all cards.
* @see     #infoCardsInHand(ca.ualberta.cs.poker.Hand)
'''

def cards_to_keep_random(hand_remove_cards_to_keep, cards_to_keep, at_least=1):
    random_count_to_keep = random.randint(at_least, len(hand_remove_cards_to_keep))
    for _ in range(random_count_to_keep):
        cards_to_keep.append(hand_remove_cards_to_keep[random.randint(0, len(hand_remove_cards_to_keep)-1)])
        hand_remove_cards_to_keep = [card for card in hand_remove_cards_to_keep if card not in cards_to_keep]
    return cards_to_keep

def cards_to_throw_calc(cards_to_keep, hand):
    cards_to_throw = []
    for card in hand:
        if card not in cards_to_keep:
            cards_to_throw.append(card)
    return cards_to_throw

def queryCardsToThrow(_hand):
    print("Requested information about what cards to throw")
    type_of_hand = identify_hand(_hand)
    cards_to_keep = []
    ranks, suits, value_ranks = identify_cards_in_hand(_hand)

    if type_of_hand in [TypeOfHand.ROYAL_FLUSH, TypeOfHand.STRAIGHT_FLUSH, TypeOfHand.FULL_HOUSE, TypeOfHand.FLUSH, TypeOfHand.STRAIGHT]:
        # Keep all cards
        return ''
    if type_of_hand == TypeOfHand.ONE_PAIR:
        # Keep the pair, throw others            
        if value_ranks.count(value_ranks[0]) == 2:
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[0]]
        elif value_ranks.count(value_ranks[2]) == 2:
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[2]]
        elif value_ranks.count(value_ranks[4]) == 2:
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[4]]

        hand_remove_cards_to_keep = [card for card in _hand if card not in cards_to_keep]
        cards_to_keep = cards_to_keep_random(hand_remove_cards_to_keep, cards_to_keep, at_least=1)

    elif type_of_hand == TypeOfHand.TWO_PAIR:
        if (value_ranks.count(value_ranks[0]) == 2 and value_ranks.count(value_ranks[2]) == 2):
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[0] or card_value(card[0]) == value_ranks[2]]
        elif (value_ranks.count(value_ranks[0]) == 2 and value_ranks.count(value_ranks[4]) == 2):
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[0] or card_value(card[0]) == value_ranks[4]]
        elif (value_ranks.count(value_ranks[2]) == 2 and value_ranks.count(value_ranks[4]) == 2):
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[2] or card_value(card[0]) == value_ranks[4]]
        
        hand_remove_cards_to_keep = [card for card in _hand if card not in cards_to_keep]
        cards_to_keep = cards_to_keep_random(hand_remove_cards_to_keep, cards_to_keep, at_least=0)

    elif type_of_hand == TypeOfHand.THREE_OF_A_KIND:
        if value_ranks.count(value_ranks[0]) == 3:
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[0]]
        elif value_ranks.count(value_ranks[1]) == 3:
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[1]]
        elif value_ranks.count(value_ranks[2]) == 3:
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[2]]
    elif type_of_hand == TypeOfHand.FOUR_OF_A_KIND:
        if value_ranks.count(value_ranks[0]) == 4:
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[0]]
        elif value_ranks.count(value_ranks[1]) == 4:
            cards_to_keep = [card for card in _hand if card_value(card[0]) == value_ranks[1]]
        hand_remove_cards_to_keep = [card for card in _hand if card not in cards_to_keep]
        cards_to_keep = cards_to_keep_random(hand_remove_cards_to_keep, cards_to_keep, at_least=0)
    elif type_of_hand == TypeOfHand.HIGH_CARD:
        # Keep the highest card
        highest_value = max(value_ranks)
        cards_to_keep = [card for card in _hand if card_value(card[0]) == highest_value]
        hand_remove_cards_to_keep = [card for card in _hand if card not in cards_to_keep]
        cards_to_keep = cards_to_keep_random(hand_remove_cards_to_keep, cards_to_keep, at_least=2)
        


    cards_to_throw = cards_to_throw_calc(cards_to_keep, _hand)

    return ' '.join(cards_to_throw)
# InfoFunction:

'''
* Called when a new round begins.
* @param round the round number (increased for each new round).
'''
def infoNewRound(_round):
    #_nrTimeRaised = 0
    print('Starting Round: ' + _round )

'''
* Called when the poker server informs that the game is completed.
'''
def infoGameOver():
    print('The game is over.')

'''
* Called when the server informs the players how many chips a player has.
* @param playerName    the name of a player.
* @param chips         the amount of chips the player has.
'''
def infoPlayerChips(_playerName, _chips):
    print('The player ' + _playerName + ' has ' + _chips + 'chips')

'''
* Called when the ante has changed.
* @param ante  the new value of the ante.
'''
def infoAnteChanged(_ante):
    print('The ante is: ' + _ante)

'''
* Called when a player had to do a forced bet (putting the ante in the pot).
* @param playerName    the name of the player forced to do the bet.
* @param forcedBet     the number of chips forced to bet.
'''
def infoForcedBet(_playerName, _forcedBet):
    print("Player "+ _playerName +" made a forced bet of "+ _forcedBet + " chips.")


'''
* Called when a player opens a betting round.
* @param playerName        the name of the player that opens.
* @param openBet           the amount of chips the player has put into the pot.
'''
def infoPlayerOpen(_playerName, _openBet):
    print("Player "+ _playerName + " opened, has put "+ _openBet +" chips into the pot.")

'''
* Called when a player checks.
* @param playerName        the name of the player that checks.
'''
def infoPlayerCheck(_playerName):
    print("Player "+ _playerName +" checked.")

'''
* Called when a player raises.
* @param playerName        the name of the player that raises.
* @param amountRaisedTo    the amount of chips the player raised to.
'''
def infoPlayerRise(_playerName, _amountRaisedTo):
    print("Player "+_playerName +" raised to "+ _amountRaisedTo+ " chips.")

'''
* Called when a player calls.
* @param playerName        the name of the player that calls.
'''
def infoPlayerCall(_playerName):
    print("Player "+_playerName +" called.")

'''
* Called when a player folds.
* @param playerName        the name of the player that folds.
'''
def infoPlayerFold(_playerName):
    print("Player "+ _playerName +" folded.")

'''
* Called when a player goes all-in.
* @param playerName        the name of the player that goes all-in.
* @param allInChipCount    the amount of chips the player has in the pot and goes all-in with.
'''
def infoPlayerAllIn(_playerName, _allInChipCount):
    print("Player "+_playerName +" goes all-in with a pot of "+_allInChipCount+" chips.")

'''
* Called when a player has exchanged (thrown away and drawn new) cards.
* @param playerName        the name of the player that has exchanged cards.
* @param cardCount         the number of cards exchanged.
'''
def infoPlayerDraw(_playerName, _cardCount):
    print("Player "+ _playerName + " exchanged "+ _cardCount +" cards.")

'''
* Called during the showdown when a player shows his hand.
* @param playerName        the name of the player whose hand is shown.
* @param hand              the players hand.
'''
def infoPlayerHand(_playerName, _hand):
    print("Player "+ _playerName +" hand " + str(_hand))

    # Store current hand to use during decision making
    CURRENT_HAND.clear()
    for card in _hand:
        if card != '':
            CURRENT_HAND.append(card)

'''
* Called during the showdown when a players undisputed win is reported.
* @param playerName    the name of the player whose undisputed win is anounced.
* @param winAmount     the amount of chips the player won.
'''
def infoRoundUndisputedWin(_playerName, _winAmount):
    print("Player "+ _playerName +" won "+ _winAmount +" chips undisputed.")

'''
* Called during the showdown when a players win is reported. If a player does not win anything,
* this method is not called. 
* @param playerName    the name of the player whose win is anounced.
* @param winAmount     the amount of chips the player won.
'''
def infoRoundResult(_playerName, _winAmount):
    print("Player "+ _playerName +" won " + _winAmount + " chips.")

