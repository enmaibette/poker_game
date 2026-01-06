import socket
import random
import ClientBase
import time

from Client import *
from Game import Game

iMsg = 0
SIGNAL_ALIVE = ''#'==================ALIVE======================'
SIGNAL_START = '\n================== Round Start =============='
SIGNAL_END = '******************* Round End ****************\n'

# Agent Name
CURRENT_HAND = []

current_gamme = None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

infoAgent = pokerGames()
MsgFractions = []

GAME_ON = True
game = Game()

while GAME_ON:


    try:
        # Get data
        data = s.recv(BUFFER_SIZE)
        # split string into fraction
        message = data.split()

        for fraction in message:
            MsgFractions.append(fraction)

        # Iterate through messages
        while len(MsgFractions):

            # Check if message is empty.
            if len(MsgFractions) == 0:
                continue
            #else:
            #    print(MsgFractions)


            # No. of Msg
            iMsg = iMsg + 1
            # print('MsgFractions', data)

            # Get Request type. Pop first element.
            RequestType = MsgFractions.pop(0).decode('ascii')
            #print('CMD', RequestType, MsgFractions)

            # "Name?"
            # /** Sent from server to clients before the game starts. */
            if RequestType == 'Name?':  # if Server request for name
                s.send(('Name ' + queryPlayerName(POKER_CLIENT_NAME) + "\n").encode())

            # "Chips"
            # /** Sent from server to clients when the server informs the players how many chips a player has.
            # * Append space, the players name, space and the amount of chips after this string. Separate the words by space. */
            elif RequestType == 'Chips':  # if Server remind player chips cumber
                name = MsgFractions.pop(0).decode('ascii')
                if name == POKER_CLIENT_NAME:
                    chips = MsgFractions.pop(0).decode('ascii')
                    infoAgent.Chips = int(chips)
                    # SMART start
                    infoPlayerChips(name, chips)
                    # SMART end
                else:
                    infoPlayerChips(name, MsgFractions.pop(0).decode('ascii'))
               
               # Add player to game in the first round
                if game.current_round <= 1: 
                    game.add_player(name)

            # "Ante_Changed"
            # /** Sent from server to clients when the server informs the players that the ante has changed.
            # * Append space and the value of the ante after this string. */
            elif RequestType == 'Ante_Changed':  # if ante is changed
                ante = MsgFractions.pop(0).decode('ascii')
                infoAgent.Ante = int(ante)
                infoAnteChanged(ante)

            # "Forced_Bet"
            # /** Sent from server to clients when the server informs the players that a player has made a forced bet (the ante).
            # * Append the players name and the bet value after this string. Separate the words by space. */
            elif RequestType == 'Forced_Bet':  # Notice force bet
                name = MsgFractions.pop(0).decode('ascii')
                bet = MsgFractions.pop(0).decode('ascii')
                if name == POKER_CLIENT_NAME:
                    print(SIGNAL_START)
                    infoAgent.playersCurrentBet = infoAgent.playersCurrentBet + int(bet)
                    game.start_new_round()
                    game.save_player_bid(name, int(infoAgent.playersCurrentBet))
                else:
                    infoForcedBet(name, bet)
                    game.save_player_bid(name, int(bet))
            # "Open?"
            # /** Sent from server to clients as information when a player opens.
            # * Append the players name and the total amount of chips the player has put into into the pot after this string.
            # * Separate the words by space. */
            elif RequestType == 'Open?':
                minimumPotAfterOpen = int(MsgFractions.pop(0).decode('ascii'))
                playersCurrentBet = int(MsgFractions.pop(0).decode('ascii'))
                playerRemainingChips = int(MsgFractions.pop(0).decode('ascii'))
                tmp = queryOpenAction(minimumPotAfterOpen, playersCurrentBet, playerRemainingChips)
                if isinstance(tmp, str):  # For check and All-in
                    s.send((tmp + "\n").encode())
                elif len(tmp) == 2:  # For open
                    s.send((tmp[0] + ' ' + str(tmp[1]) + " \n").encode())
                print(SIGNAL_ALIVE)
                print(POKER_CLIENT_NAME + 'Action>', tmp)
                game.save_player_action(POKER_CLIENT_NAME, tmp)

            elif RequestType == 'Call/Raise?':
                maximumBet = int(MsgFractions.pop(0).decode('ascii'))
                minimumAmountToRaiseTo = int(MsgFractions.pop(0).decode('ascii'))
                playersCurrentBet = int(MsgFractions.pop(0).decode('ascii'))
                playersRemainingChips = int(MsgFractions.pop(0).decode('ascii'))
                tmp = queryCallRaiseAction(maximumBet, minimumAmountToRaiseTo, playersCurrentBet, playersRemainingChips)
                if isinstance(tmp, str):  # For fold, all-in, call
                    s.send((tmp + "\n").encode())
                elif len(tmp) == 2:  # For raise
                    s.send((tmp[0] + ' ' + str(tmp[1]) + " \n").encode())
                print(SIGNAL_ALIVE)
                print(POKER_CLIENT_NAME + 'Action>', tmp)

            elif RequestType == 'Cards':  # Get Cards
                # infoCardsInHand(MsgFractions) # show info for hands
                infoAgent.CurrentHand = []
                for ielem in range(1, 6):  # 1 based indexing is required...
                    infoAgent.CurrentHand.append(MsgFractions.pop(0).decode('ascii'))
                infoPlayerHand(POKER_CLIENT_NAME, infoAgent.CurrentHand)
                # print('CurrentHand>', infoAgent.CurrentHand)
            elif RequestType == 'Draw?':
                discardCards = queryCardsToThrow(infoAgent.CurrentHand)
                s.send(('Throws ' + discardCards + "\n").encode())
                print(POKER_CLIENT_NAME + ' Action>' + 'Throws ' + discardCards)

            # "Round"
            # /** Sent from server to clients when a new round begins.
            # * Append space and the round number after this string. */
            elif RequestType == 'Round':
                infoNewRound(MsgFractions.pop(0).decode('ascii'))
            # "Game_Over"
            # /** Sent from server to clients when the game is completed. */
            elif RequestType == 'Game_Over':
                infoGameOver()
                game.save_to_json()
                GAME_ON = False


            # "Player_Open"
            # /** Sent from server to clients as information when a player opens.
            # * Append the players name and the total amount of chips the player has put into into the pot after this string.
            # * Separate the words by space. */
            elif RequestType == 'Player_Open':
                player_name = MsgFractions.pop(0).decode('ascii')
                amount_opened = MsgFractions.pop(0).decode('ascii')
                infoPlayerOpen(player_name, amount_opened)
                game.save_player_action(player_name, 'Open')
                game.save_player_bid(player_name, int(amount_opened))

            # "Player_Check"
            # /** Sent from server to clients as information when a player checks.
            # * Append the players name after this string. Separate the words by space. */
            elif RequestType == 'Player_Check':
                player_name = MsgFractions.pop(0).decode('ascii')
                game.save_player_action(player_name, 'Check')
                infoPlayerCheck(player_name)

            # "Player_Raise"
            # /** Sent from server to clients when a player raises the bet.
            # * Append the name and the raised amount of chips after this string. Separate the words by space. */
            elif RequestType == 'Player_Raise':
                player_name = MsgFractions.pop(0).decode('ascii')
                player_bid = MsgFractions.pop(0).decode('ascii')
                game.save_player_action(player_name, 'Raise')
                game.save_player_bid(player_name, int(player_bid))
                infoPlayerRise(player_name, player_bid)

            # "Player_Call"
            # /** Sent from server to clients as information when a player calls.
            # * Append the players name after this string. Separate the words by space. */
            elif RequestType == 'Player_Call':
                player_name = MsgFractions.pop(0).decode('ascii')
                game.save_player_action(player_name, 'Call')
                infoPlayerCall(player_name)

            # "Player_Fold"
            # /** Sent from server to clients as information when a player folds.
            # * Append the players name after this string. Separate the words by space. */
            elif RequestType == 'Player_Fold':
                player_name = MsgFractions.pop(0).decode('ascii')
                game.save_player_action(player_name, 'Fold')
                infoPlayerFold(player_name)

            # "Player_All-in"
            # /** Sent from server to clients as information when a player goes all-in.
            # * Append the players name after this string. Separate the words by space. */
            elif RequestType == 'Player_All-in':
                player_name = MsgFractions.pop(0).decode('ascii')
                game.save_player_action(player_name, 'All-in')
                infoPlayerAllIn(player_name, MsgFractions.pop(0).decode('ascii'))

            # "Player_Draw"
            # /** Sent from server to client as information when a player throws away old and draws new cards.
            # * Append the players name and the number of cards exchanged after this string. Separate the words by space. */
            elif RequestType == 'Player_Draw':
                player_name = MsgFractions.pop(0).decode('ascii')
                number_of_cards = MsgFractions.pop(0).decode('ascii')
                game.save_player_action(player_name, 'Draw')
                game.save_player_card_replaced(player_name, int(number_of_cards))
                infoPlayerDraw(player_name, number_of_cards)

            # "Round_Win_Undisputed"
            # /** Sent from server to clients when the server informs the players that a player won a round undisputed.
            # * Append the players name and the amount of chips the player won after the string. Separate the words by space. */
            elif RequestType == 'Round_Win_Undisputed':
                print(SIGNAL_END)
                player_name = MsgFractions.pop(0).decode('ascii')
                amount_won = MsgFractions.pop(0).decode('ascii')
                game.save_player_won(player_name)
                infoRoundUndisputedWin(player_name, amount_won)

            # "Round_result"
            # /** Sent from server to clients when the server informs the players the result of a round for a player.
            # * Append the players name and the amount of chips the player won after the string. Separate the words by space. */
            elif RequestType == 'Round_result':
                print(SIGNAL_END)
                player_name = MsgFractions.pop(0).decode('ascii')
                amount_won = MsgFractions.pop(0).decode('ascii')
                game.save_player_won(player_name)
                infoRoundResult(player_name, amount_won)

            # "Player_Hand"
            # /** Sent from server to clients when the server informs the players what hand a player holds.
            # * Append the players name and the cards of the players hand after this string. Separate the words by space.*/
            elif RequestType == 'Player_Hand':
                player_name = MsgFractions.pop(0).decode('ascii')
                player_hand = [MsgFractions.pop(0).decode('ascii'), MsgFractions.pop(0).decode('ascii'), MsgFractions.pop(0).decode('ascii'), MsgFractions.pop(0).decode('ascii'),
                               MsgFractions.pop(0).decode('ascii')]
                infoPlayerHand(player_name, player_hand)

    except socket.timeout:
        break

s.close()









