#Playing a card game created by Lectuer

from collections import defaultdict as dd
from itertools import combinations as comb

def phazed_play(player_id, table, turn_history, phase_status, hand, discard):
    
    needed_phase = phase_status[player_id] + 1
    phase_complete = bool(table[player_id][1])       
    valuecount = dd(int)
    suitcount = dd(int)
    hand_count = 0  # total value of cards in hand
    card_draw = False
    group1 = []
    group2 = []
    
    if turn_history:  # if a play has been made
        if not(turn_history[-1][0] == player_id):
            card_draw = False
        else:  # my play is most recent in turn_history
            card_draw = True
            recent_move = turn_history[-1][1][-1]
        
    # setup the value and suit count for use in phases
    for card in hand:
        valuecount[card[:-1]] += 1
        suitcount[card[1]] += 1
        
    if not(card_draw):  # if it is the first move 
        if discard is None:
            return (1, None)
        
        elif not(phase_complete): 
            if needed_phase == 3 or needed_phase == 6: 
                # check for any new accumulations with discard
                if not(playing_phase(hand, needed_phase)[0]):
                    if playing_phase(hand + [discard], needed_phase)[0]:                        
                        return (2, discard)
      
                # if no accumulation just decide using total hand value
                # if hand value (count) is higher than 68, try get lower value
                # card, otherwise less than 68, try get higher value card
                hand = card_to_number(hand, 3)
                discard_num = card_to_number([discard], 3)[0]
                for card in hand:
                    hand_count += int(card[:-1])
                if hand_count + int(discard_num[:-1]) < 68: 
                    if int(discard_num[:-1]) < 7: 
                        # pray that deck card will give you higher value card
                        return (1, None) 
                    else:                      
                        return(2, discard)
                    
                else:  # if adding discard will cause hand total to go over 68
                    if int(discard_num[:-1]) > 7:
                        return(1, None)  # hope deck card is lower than 7
                    else:
                        return(2, discard)
            
            # if not in accumulation phase, pick up Ace from discard
            # if possible
            elif discard[0] == 'A':                 
                return (2, discard)
            
            elif needed_phase == 1 or needed_phase == 4:  # same value cards
                
                # if a combination of any 2 cards from hand + discard can
                # make a set of 3 or 4 cards of same value
                cardno = 3
                if needed_phase == 4:
                    cardno = 4
               
                if not(playing_phase(hand, needed_phase, cardno)[0]): 
                    if (playing_phase(hand + [discard], needed_phase, 
                                      cardno)[0]):
                        
                        return (2, discard)
                
                # does discard make a triple (for phase 4) or pair (phase 2)
                if valuecount[discard[:-1]] + 1 > cardno - 2:
                    return (2, discard)
                
                return (1, None)

            
            elif needed_phase == 2:
                # if discard pickup makes it the most occuring suit, do discard
                top_suit = [suit for suit in suitcount if suitcount[suit] == 
                            max(suitcount.values())]
                        
                if suitcount[discard[1]] + 1 > suitcount[top_suit[0]]:
                    return (2, discard)
                else:
                    return (1, None)
                                    
            elif needed_phase == 5: 
                        
                if discard in hand: 
                    return (1, None)  # don't want duplicates in run
                        
                # if adding discard makes a run, pickup discard    
                if not(playing_phase(hand, needed_phase, 8)[0]):                
                    if playing_phase(hand + [discard], needed_phase, 
                                     8)[0]:
                        
                        return (2, discard)
                        
                return (1, None)      
                                
                                   
            elif needed_phase == 7:        
                # check for group 1 of phase 7, by separating hand by the 
                # colour of discard suit
                
                if discard[1] in ['C', 'S']:  # discard is black
                        colour_hand = [card for card in hand if card[1] == 'C' 
                                       or card[1] == 'S']
                else:  # discard is red
                        colour_hand = [card for card in hand if card[1] == 'D' 
                                       or card[1] == 'H']
                        

                # check if adding discard will help create group 1 of phase 7
                if not(playing_phase(colour_hand, 7.1, 4)[0]):
                        if playing_phase(colour_hand + [discard], 7.1)[0]:
                            return (2, discard)
                        
                # check if adding discard will help create group 2                      
                if not(playing_phase(hand, 4, 4)[0]): 
                        if playing_phase(hand + [discard], 4, 4)[0]:
                            return (2, discard)

                return (1, None)
                
        else:  # phase complete
            # check if the discard creates a valid play to any other phase
            if adding_to_phase(discard, player_id, table, turn_history, 
                               phase_status, hand, discard): 

                return (2, discard)
            
            elif discard[0] in ['2', '3', '4', '5', '6']:  # low score
                return (2, discard)
            return (1, None)

    elif 1 in recent_move or 2 in recent_move:  # recent move was draw
        
        if not(phase_complete): 
            
            if needed_phase == 1 or needed_phase == 4:                
                cardno = 3
                if needed_phase == 4:
                    cardno = 4
                group1 = playing_phase(hand, needed_phase, cardno)[0]
                group2 = playing_phase(hand, needed_phase, cardno)[1]
                
                play = (3, (needed_phase, [group1, group2]))
                
            elif needed_phase == 2:
                group1 = playing_phase(hand, 2, 7)[0]
                play = (3, (2, [group1]))
                
            elif needed_phase == 3 or needed_phase == 6:                
                group1 = playing_phase(hand, needed_phase)[0]
                group2 = playing_phase(hand, needed_phase)[1]  
                play = (3, (needed_phase, [group1, group2]))
                
              
            elif needed_phase == 5:                
                group1 = playing_phase(hand, needed_phase, 8)[0]     
                play = (3, (5, [group1]))
                    
            elif needed_phase == 7:                          
                red_hand = [card for card in hand if card[-1] == 'D' or 
                            card[-1] == 'H']
                black_hand = [card for card in hand if card[-1] == 'C' or
                              card[-1] == 'S']
                
                if playing_phase(red_hand, 7.1, 4)[0]:                   
                    group1 = playing_phase(red_hand, 7.1, 4)[0]
                elif playing_phase(black_hand, 7.1, 4)[0]:
                    group1 = playing_phase(black_hand, 7.1, 4)[0]
                    
                # phase 7 group 2 can be run under same conditions as phase 4
                group2 = playing_phase(hand, 4, 4)[0]                 
                play = (3, (7, [group1, group2]))
           
                
            # creating a copy as phazed_is_valid_play changes play variable            
            if phazed_is_valid_play(play, player_id, table, turn_history, 
                                    phase_status, hand, discard):
                # when running play through phazed_is_valid_play, sometimes 
                # the cards in play gets changed to only have values 
                # e.g. Q -> 12, so number_to_card()
                
                play[1][1][0] = number_to_card(group1)
                if group2:
                    play[1][1][1] = number_to_card(group2)
                return play
                  
    elif 4 in recent_move:  # if recent_move was adding onto phase
        # player of the phase the last card was added onto     
        player_added = recent_move[1][1][0]  
        phase = phase_status[player_added]
        
        if phase == 3 or phase == 6: 
            # check to finish accumulation
            needed_total = [55, 68, 76, 81, 84, 86, 87, 88]
            group = recent_move[1][1][1] 
            accumulation_count = 0
            accumulation = table[player_added][1][group]
            accumulation = card_to_number(accumulation, 3)
            for card in accumulation:
                accumulation_count += int(card[:-1])
             
            # accumulation not finished
            if not(accumulation_count in needed_total):
                return adding_to_accumulation(hand, player_added, group, table)
        
  

    if phase_complete and card_draw:  # add to phase section    
        for card in hand:  # check if any card can be added to a phase
            if adding_to_phase(card, player_id, table, turn_history, 
                               phase_status, hand, discard):

                return adding_to_phase(card, player_id, table, 
                                       turn_history, phase_status, 
                                       hand, discard)
    

    # if none of these can be done, discard

    hand = number_to_card(hand) 
 
    if len(hand) == 1:      
        return (5, hand[0])
    
    if group1:
        for card in group1:  # if group1 of a phase has been made don't discard
            if card in hand:  
                hand.remove(card)
    
    if len(turn_history) > 55:  # reaching turn_limit, try to reduce score
        for card in hand:
            if card[0] == 'A':
                return (5, card)
            
    if not(phase_complete):  # set of discard guidelines for phases
        card_to_discard = ''
        value_count2 = dd(int)
        suit_count2 = dd(int)
        for card in hand:
            if card[0] == 'A':
                continue
            value_count2[card[:-1]] += 1
            suit_count2[card[-1]] += 1
            
        if needed_phase == 1 or needed_phase == 4: 
            # discard least occuring card based on value
            value_to_discard = min(value_count2.items(), 
                                   key=lambda value: value[1])[0]
            for card in hand:                
                if card[:-1] == value_to_discard:
                    card_to_discard = card
                    break
                    
            return (5, card_to_discard)
        
        elif needed_phase == 2:
            # discard least occuring card based on suit
            suit_to_discard = min(suit_count2.items(), 
                                  key=lambda suit: suit[1])[0]
            for card in hand:
                if card[-1] == suit_to_discard:
                    card_to_discard = card
                    break
                
        elif needed_phase == 3 or needed_phase == 6:          
            hand = card_to_number(hand, 3)
            card_values = [int(value[:-1]) for value in hand]
            for card in hand:
                hand_count += int(card[:-1])
                if int(card[:-1]) == 1:  # discard aces if any                
                    card = number_to_card([card])[0]
                    return (5, card) 
                
            needed_cardvalue = 68  # two accumulations
            if group1: 
                needed_cardvalue = 34
                

            if hand_count < needed_cardvalue:  # remove low value card                   
                for card in hand:
                    if int(card[:-1]) == min(card_values):
                        card_to_discard = card
                        break
            elif hand_count > needed_cardvalue: 
                # if removing a card and hand_count still > 
                # needed_cardvalue, remove that card

                for card in hand: 
                    if hand_count - int(card[:-1]) > needed_cardvalue:
                        card_to_discard = card
                        break           
            
        elif needed_phase == 5:
            value_to_discard = max(value_count2.items(), 
                                   key=lambda value: value[1])[0]
            for card in hand:
                if card[:-1] == value_to_discard:
                    card_to_discard = card
                        
    
        elif needed_phase == 7:     
            if not(group1):  # no run of 4 same colour cards
                if group2: 
                    # discard most common card                
                    value_to_discard = max(value_count2.items(), 
                                           key=lambda value: value[1])[0]
                    for card in hand:
                        if card[:-1] == value_to_discard and (
                            card not in group2):

                            card_to_discard = card
                            
            elif not(group2): 
                if group1:
                    # discard least occuring card by value
                    value_to_discard = min(value_count2.items(), 
                                           key=lambda value: value[1])[0]
                    for card in hand:
                        if card[:-1] == value_to_discard:
                            card_to_discard = card
        
        if card_to_discard:  # if any of the above found a card to discard
            card_to_discard = number_to_card([card_to_discard])[0]            
            return (5, card_to_discard)
                    
       
        hand = card_to_number(hand, 3)
        # make sure hand doesnt have an abundance of aces
        ace_control = {1: 2,
                       2: 3,
                       3: 0,
                       4: 3,
                       5: 3,
                       6: 0,
                       7: 3}
        acecount = 0

        for card in hand:    
            if card[:-1] == 1:
                acecount += 1
        if acecount <= ace_control[needed_phase]:  # low amount of aces
            for card in hand:
                if card[0] == 1:
                    # remove it from hand so it can't be discarded
                    hand.remove(card) 
                    
        elif acecount > ace_control[needed_phase]:  # too many aces                                   
            for card in hand:
                if card[0] == 1:
                    card = number_to_card([card])[0]
                    return (5, card)
    
    # otherwise remove highest value card
    hand = card_to_number(hand, 3) 
    highestcardvalue = 0
    for card in hand:
        if card[:-1] == 1:
            card_to_discard = card
            break

        if int(card[:-1]) > highestcardvalue:
            card_to_discard = card
            highestcardvalue = int(card[:-1])

    card_to_discard = number_to_card([card_to_discard])[0]  
    hand = number_to_card(hand)
    return (5, card_to_discard)
        
def playing_phase(hand, phase, cardno=0):
    """ Attempt to play a phase with a given hand. cardno is the length of
    the group in the phase, e.g. a run of 8 cards would have cardno = 8. Is 
    also used to determine whether the discard is useful"""

    group1 = []
    group2 = []
    hand_copy = list(hand)  # any changes onto hand_copy don't happen to hand
    
    if phase == 1 or phase == 4:        
        # try create same value sets of length cardno, and if any are found
        # save them to group1
        for group in comb(hand_copy, cardno):          
            if phase ==1:
      
                if 1 in phazed_group_type(list(group)):
                    group1 = list(group)
                    break
            else:
                if 3 in phazed_group_type(list(group)):                    
                    group1 = list(group)
                    break
                    
        # if 1 group was found, repeat the process after removing the first
        # group's card from hand_copy
        if group1:         
            for card in group1:
                hand_copy.remove(card)
            for group in comb(hand_copy, cardno):          
                if phase == 1:                   
                    if 1 in phazed_group_type(list(group)):                       
                        group2 = list(group)
                        break
                else:
                    if 3 in phazed_group_type(list(group)):                        
                        group2 = list(group)
                        break
       
    elif phase == 2:
        # find a combination of 7 cards that have same suit
        for group in comb(hand_copy, cardno):
            if 2 in phazed_phase_type([list(group)]):
                group1 = list(group)
                break
                
        
        
    elif phase == 3 or phase == 6:
        hand_copy = card_to_number(hand_copy, 3)      
        # create combinations of card with length i. i starts at 3 as that
        # is the min number of cards for an accumulation
        for i in range(3, len(hand_copy) + 1):  
            if group1:
                break
            for group in comb(hand_copy, i):
                if accumulation_check(list(group)) == 'coloraccumulation':
                    group1 = list(group)
                    break

                elif accumulation_check(list(group)) == (
                    'accumulation') and phase == 3:
                    
                    group1 = list(group)
                    break 
        # repeat process removing group 1 from hand_copy
        if group1:
           
            for card in group1:
                hand_copy.remove(card)
            for i in range(3, len(hand_copy) + 1):
                if group2: 
                    break
                    
                for group in comb(hand_copy, i):
                    if accumulation_check(list(group)) == 'coloraccumulation':
                        group2 = list(group)
                        break

                    elif (accumulation_check(list(group)) == ('accumulation') 
                          and phase == 3):

                        group2 = list(group)
                        break
   
    elif phase == 5 or phase == 7.1: 
        # change hand to just have value of card, or if Ace, save card as 'A'
        # in the case of phase 7, group1 (7.1) the hands given are already 
        # separated into different colors
        
        hand_copy = card_to_number(hand_copy, 5) 
        
        for i in range(len(hand_copy)):  
            if hand_copy[i][0] == 'A':
                hand_copy[i] = 'A'
            else:
                hand_copy[i] = int(hand_copy[i][:-1])
        
        aces_inhand = hand_copy.count('A')
        
        while 'A' in hand_copy:
            hand_copy.remove('A') 
        
        
      
        # remove duplicates to get a unique list
        hand_copy = list(set(hand_copy))
        
        if len(hand_copy) < cardno:
            return [group1, group2]  # just return empty lists if no run
        
        # Try find runs starting with lowest possible card, and continue trying
        # if there are enough cards in hand to create a run
        
        for i in range(0, len(hand_copy)): 
            ace_count = aces_inhand
            
            if phase == 7.1 and ace_count > 2: 
                ace_count = 2  # phase 7 group 1 needs 2 non-wild cards
                    
            elif phase == 5 and ace_count > 6:
                ace_count = 6

            card_value = hand_copy[i]          
            
            run = [card_value]  # keep track of the values that make a run
            
            for h in range(i + 1, i + cardno):  
                if card_value + 1 in hand_copy: 
                    run.append(card_value + 1)
                    card_value = card_value + 1
                
                elif card_value == 13:
                    
                    if 2 in hand_copy:
                        run.append(2)
                        card_value = 2
                    
                else:  # check if there is ace to fill a missing card
                    if ace_count == 0: 
                        # can't continue run
 
                        break
                        
                    ace_count -= 1 
                    card_value = card_value + 1
                    run.append('A')
            
            if len(run) == cardno:  # a run has been found
                break
        
        # if run is found, replace values and aces with actual card 
        # (e.g. add suit)
        ace_list = [ace for ace in hand if ace[0] == 'A']         
        hand = card_to_number(hand, 5)
        if len(run) == cardno:
            # for each value of run, go through cards in hand and
            # if they card and value match, append that card to group1
            for value in run:         
                for card in hand:
                       
                    if value != 'A' and card[:-1] != 'A':
                        if int(card[:-1]) == value: 
                            group1.append(card)
                            break
                    elif value == 'A':
                        
                        group1.append(ace_list[0])
                        ace_list.pop(0) 
                        break
   
    # make sure group 1 and 2 are sent back in proper format
    group1 = number_to_card(group1) 
    group2 = number_to_card(group2)
    
    return [group1, group2]       
                      
def number_to_card(group):
    """ Convert number values back to letters. Takes in a list of cards"""
    cardletters = {'1': 'A',
                   '10': '0',
                   '11': 'J',
                   '12': 'Q',
                   '13': 'K'}
   
    for i in range(len(group)):
        card = group[i]
       
        if str(card)[:-1] in cardletters:
            group[i] = cardletters[card[:-1]] + card[-1]
    return group
    
def adding_to_phase(card, player_id, table, turn_history, phase_status, 
                   hand, discard):
    """ Checks if the given card can be added to a phase on the table. 
        Also requires other game details as arguments in order to call
        phazed_is_valid_play()"""
    
    for player in range(4):
        if table[player][1]:  # if the player has a played phase
            index = len(table[player][1][0])  # num of cards in first group 
    
            if table[player][0] == 5:  # if adding to run
                # try add to start
                if phazed_is_valid_play((4, (card, (player, 0, 0))), 
                   player_id, table, turn_history, phase_status, 
                   hand, discard):
                    
                    card = number_to_card([card])[0] 
                    return (4, (card, (player, 0, 0)))
                # try add to end
                elif phazed_is_valid_play((4, (card, (player, 0, 
                     index))), player_id, table, turn_history, 
                     phase_status, hand, discard):
                    
                    card = number_to_card([card])[0] 
                        
                    return (4, (card, (player, 0, index)))

           
            elif table[player][0] == 3 or table[player][0] == 6:  
                # try find a card to the accumulation (both groups) 
                
                if adding_to_accumulation(hand, player, 0, table):
                    return adding_to_accumulation(hand, player, 0, table)
                elif adding_to_accumulation(hand, player, 1, table):
                    return adding_to_accumulation(hand, player, 1, table)
       
            else: 
                # just check if adding to phase is valid play, if phase has
                # two groups, try second group as well
                
                group = len(table[player][1])
              
                if phazed_is_valid_play((4, (card, (player, 0, index))), 
                   player_id, table, turn_history, phase_status, 
                   hand, discard):
                    card = number_to_card([card])[0] 
                    return (4, (card, (player, 0, index)))

                if group == 2:
                    index = len(table[player][1][1])  # num of cards in group2        
                    if phazed_is_valid_play((4, (card, 
                       (player, 1, index))), player_id, table, 
                       turn_history, phase_status, hand, discard):
                        card = number_to_card([card])[0] 
                        return (4, (card, (player, 1, index)))
    return False

def adding_to_accumulation(hand, player, phase_group, table):
    """ Finds a combination of cards that complete an accumulation,
    and returns back the first card of that combination in play format"""
    
    phase = table[player][0]
    hand_copy = card_to_number(hand, 3)
    needed_total = [55, 68, 76, 81, 84, 86, 87, 88] 
    accumulation = table[player][1][phase_group]  # list of cards 
    accumulation = card_to_number(accumulation, 3)
    index = len(accumulation)
    accumulation_value = 0 

    
    # find the total value of accumulation and determine what the next 
    # limit is. E.g. if 34, then next limit is 55
    for card in accumulation:
        accumulation_value += int(card[:-1])
    for num in needed_total:
        if accumulation_value < num:
            next_accumulation = num
            break
    
    needed_cardtotal = next_accumulation - accumulation_value
    
    for i in range(1, len(hand_copy) + 1):     
        # create combinations of increasing i length
        for group in comb(hand_copy, i): 
            group_value = 0
            
            for card in group:
                group_value += int(card[:-1])
                
                if phase == 6:
                    # if card not same colour as played accumulation
                    # go to next group
                    if not(colour_check(card, accumulation)):
                        group_value = 0
                        break
                    
            if group_value == needed_cardtotal:
                # if combination found, return a play using the first card
                # of combination
                card = group[0]
                card = number_to_card([card])[0] 
                return (4, (card, (player, phase_group, index)))   
            
    return False

def phazed_is_valid_play(play, player_id, table, turn_history, phase_status, 
                         hand, discard):
    """
    Determines if a play is valid. Play can range from card pickup,
    phase play, adding onto phase and discard, and is in the form of a tuple.
    Also requires other arguments of game condition.
    """
    
    hand = list(hand) 
    needed_total = [55, 68, 76, 81, 84, 86, 87, 88]  # fibonacci
    card_draw = False
    recent_draw = False
    own_phaseplayed = bool(table[player_id][1])  
    recent_move = []


    if turn_history:
        if not(turn_history[-1][0] == player_id):
            card_draw = False
        else:  # my play is most recent in turn_history
            card_draw = True
            recent_move = turn_history[-1][1][-1]
    
    
    if 1 in recent_move or 2 in recent_move:
        recent_draw = True  # if player's recent move was drawing a card  
        
    if play[0] == 1 or play[0] == 2: 
        if not(card_draw):  # if player has not made any moves yet
            if play[0] == 2 and play[1] == discard:  # pickup matches discard
                return True
            
            elif play[0] == 1:
                return True
            
        return False
        
    if play[0] == 3:  # playing to phase
        
        
        if not(recent_draw):  # phase play has to occur after card draw
            return False
        # check phase has not been played and cards are in hand
        if not(own_phaseplayed):            
            playingcards = play[1][1][0]
            if len(play[1][1]) == 2:  # if two groups for phase                
                playingcards = play[1][1][0] + play[1][1][1]
        
            # check if user has the needed cards
            hand = number_to_card(hand) 
            for card in playingcards:
                if card not in hand:
                    return False
                hand.remove(card)
            # if stated phase play matches the phase player needs to play
            if play[1][0] == phase_status[player_id] + 1:
                # if list of cards are a phase type and if intended phase
                # play matches that
                if play[1][0] in phazed_phase_type(play[1][1]):
                    return True

    elif play[0] == 4:  # add onto phase      
        other_playerid = play[1][1][0]                   
        addon_phase = phase_status[other_playerid] 
        next_fibonacci = 0
        playing_card = play[1][0]
        group = play[1][1][1]  
        # the group that user wants to play to
        phase_cards = table[other_playerid][1][group] 
        
        if not(table[other_playerid][0]):  # if player doesn't have a phase
            return False
        
        if not(card_draw) and not(own_phaseplayed): 
            return False

        if playing_card in hand:                    
            # convert letters to value for playing_card and phase_cards
            phase_cards = card_to_number(phase_cards, addon_phase)
            playing_card = card_to_number([playing_card], addon_phase)[0]

            if addon_phase == 3 or addon_phase == 6:                
                value_count = 0
                for card in phase_cards:
                    value_count += int(card[:-1]) 

                    for num in needed_total:
                        if value_count < num:
                            next_fibonacci = num
                            break

                if len(hand) == 1:  # check final card completes sequence
                    if int(playing_card[:-1]) + value_count == next_fibonacci:
                        if addon_phase == 6:
                            return colour_check(playing_card, phase_cards)
                        return True
                # if not final card, as long as card does not cause 
                # value_count to go over next_fibonacci
                else: 
                    if int(playing_card[:-1]) + value_count <= next_fibonacci:
                        if addon_phase == 6:                          
                            return colour_check(playing_card, phase_cards)
                        return True

            # ace can be added to anything besides accumulation
            elif playing_card[0] ==  'A': 
                    return True

            elif addon_phase == 1 or addon_phase == 4 or (addon_phase == 7 
                                                          and group == 1): 
                # find if playing_card is same value as other cards in group
                for card in phase_cards:
                    if card[0] != 'A':
                        comparison_card = card
                        break
                        
                if playing_card[:-1] == comparison_card[:-1]: 
                    return True
                
            elif addon_phase == 2: 
                # same process as above except comparing suits
                for card in phase_cards:
                    if card[0] != 'A':
                        comparison_card = card
                        break
                        
                if playing_card[-1] == comparison_card[-1]:
                    return True

            elif addon_phase == 5 or (addon_phase == 7 and group == 0):
                
                no_cards = len(phase_cards)
                if no_cards == 12:  # run has a full rotation
                    return False 
                  
                card_place = play[1][1][2]
                
                if card_place == no_cards:
                    # add card to end of group and see if it is a valid run
                    phase_cards = phase_cards + [playing_card]                
                    if run_check(phase_cards):
                        if addon_phase == 7:
                            return colour_check(playing_card, phase_cards)
                        return True
                            
                elif card_place == 0: 
                    # add card to start of group and see if valid run
                    phase_cards = [playing_card] + phase_cards
                    
                    if run_check(phase_cards):
                        if addon_phase == 7:
                            return colour_check(playing_card, phase_cards)
                        return True

    elif play[0] == 5:  # discard
        accumulation_attempt = False
        playing_card = play[1]
        value_count = 0

        if not(playing_card in hand) or not(card_draw):
            return False
        
        # check if before discarding, an accumulation was added to
        
        if recent_move[0] == 4:
            other_player = recent_move[1][1][0]
            group = recent_move[1][1][1]
            if phase_status[other_player] == 3 or (phase_status
               [other_player] == 6):
                accumulation_attempt = True
                added_card = recent_move[1][0]
                phase_cards = table[other_player][1][group]                        
                

        if accumulation_attempt:
            phase_cards = card_to_number(phase_cards, 3)
            added_card = card_to_number([added_card], 3)[0] 
            for card in phase_cards:
                value_count += int(card[:-1])

            if value_count + int(added_card[:-1]) in needed_total:
                return True  # if accumulation completed
            else:
                return False
            
        else:  # no accumulation add on
            return True
        
    return False

def colour_check(playing_card, phase_cards):
    """ only to check colour between a single card and a list of cards"""
    # if card has black suit, phase_cards cannot have red suit and vice-versa, 
    # phase_cards are all same colour so just compare playing_card with 1
    
    if playing_card[-1] in ['H', 'D']:
        if phase_cards[0][-1] in ['H', 'D']:
            return True
    elif playing_card[-1] in ['S', 'C']:
        if phase_cards[0][-1] in ['S', 'C']:
            return True
    return False 

def card_to_number(phase_cards, addon_phase):
    """Convert letter cards and 10 to actual value. Additionally change Ace
    to 1 if addon_phase == 3. Takes in a list of cards and a phase id"""
    cardnumber = {'0': 10,
                  'J': 11,
                  'Q': 12,
                  'K': 13}    
    
    for i in range(len(phase_cards)):
        card = phase_cards[i]
        if card[0] in cardnumber:
            # replace phase_cards[i] with actual integer and suit
            phase_cards[i] = str(cardnumber[card[0]]) + card[-1] 
        if addon_phase == 3:  # only change ace when looking at accumulation          
            if card[0] == 'A':
                phase_cards[i] = '1' + card[-1]
    return phase_cards

def phazed_phase_type(phase):
    """Determines whether a list of list of cards fits phase conditions.  
    Uses phazed_group_type to determine group. Returns any phase that the cards
    are suitable for."""
    
    group_play = []
    phase_play = []
   
    for group in phase:         
        # add group_type to group_play for all groups in the phase
        group_play.append(phazed_group_type(group)) 
    
    # phase 1 check
    if group_play.count([1]) >= 2:
        phase_play.append(1)
    # phase 2 check    
    if [2] in group_play:

        phase_play.append(2)
    
    # phase 3 check, can be a mix of both accumulations and coloraccumulations
    if (group_play.count([6]) + group_play.count([6, 7])) >= 2:       
        phase_play.append(3)
    
    # phase 4 check
    
    if group_play.count([3]) >= 2:
        phase_play.append(4)
    
    # phase 5 check
    if [4] in group_play:
        phase_play.append(5)
    
    # phase 6 check
    if group_play.count([6, 7]) >= 2:
        phase_play.append(6)
  
    # phase 7 check
    if [5] in group_play and [3] in group_play:
        phase_play.append(7)
    
    return sorted(phase_play)

def phazed_group_type(group):
    """Determine whether a list of cards meet a group condition and returns
    any group id that is met"""
    values = dd(int)
    cardvalue = ''
    cardsuit = ''
    suits = dd(int)
    available_play = []
    group = list(group)   
    group = card_to_number(group, 0)  # replace letter cards with numbers 
      
    # check 1
    if len(group) == 3:
        # get the occurences of values in group and store in values dict
        # Aces just store as 'A' as they are a wild card
        for card in group:
            values[card[:-1]] += 1
                
            if card[0] != 'A':
                cardvalue = card[:-1] 
   
        if values['A'] > 1:  # need at least two non-wild cards          
            return []
       
        if values[cardvalue] == 3 or (values['A'] == 1 and 
                                      values[cardvalue] == 2):                          
            return [1]
        
        elif accumulation_check(group) == 'coloraccumulation':
            return [6, 7]
        elif accumulation_check(group) == 'accumulation':
            return [6]
        
    # check 2
    elif len(group) == 7:
        # similar method as above but this time use suits as condition
        for card in group:           
            if card[0] != 'A':
                suits[card[-1]] += 1
                cardsuit = card[-1]
            else:
                suits[card[0]] += 1
        
        if suits['A'] > 5: 
            return []
        
        if suits[cardsuit] + suits['A'] == 7:         
            available_play.append(2)


            
    # check 3 and 5
    elif len(group) == 4:
        
        for card in group:
            values[card[:-1]] += 1
            
            if card[0] != 'A':
                cardvalue = card[:-1] 
                suits[card[-1]] += 1
                cardsuit = card[-1]
            else:
                suits[card[0]] += 1
        if values['A'] > 2:
            return[0]
        
        # if theres a set of 4 same value cards with or without aces
        if values[cardvalue] + values['A'] == 4: 
            return [3]
        
        # if run with less than 3 aces
        if run_check(group) and values['A'] <= 2: 
            # check cards are the same colour using the suits dict
            if 'H' in suits or 'D' in suits:
                if 'S' not in suits and 'C' not in suits:
                    available_play.append(5)
            elif 'S' in suits or 'C' in suits:             
                if 'H' not in suits and 'D' not in suits:
                    available_play.append(5)

    # check 4
    elif len(group) == 8:
        aces_count = 0
        for card in group:
            if card[0] == 'A':
                aces_count += 1
        # if group is a run with at least 2 non-wild cards
        if run_check(group) and aces_count <= 6:
            available_play.append(4)

    if accumulation_check(group) == 'coloraccumulation':
        available_play.extend([6, 7])
    elif accumulation_check(group) == 'accumulation':
        available_play.append(6)
    
    
    return sorted(available_play)

def run_check(group):
    """Takes a list of cards and determines if it is a run. Returns True or 
    False depending on if run"""
    
    only_aces = False
    run = True
    for i in range(len(group)):      
        card = group[i]
        if i == 0:
            if card[0] == 'A':  # starting card is ace
                only_aces = True 
        else:
            if card[0] == 'A':
                run = True  # if ace appears, continue run
                if group[i - 1][0] != 'A': 
                    # replace ace with previous card + 1 to value
                    group[i] = str(int(group[i - 1][:-1]) + 1) + group[i][1]

            elif card[0] != 'A':
                if only_aces:  # if first non-ace card in group
                    run = True
                
                # check card is 1 value bigger than previous card
                elif int(card[:-1]) == int(group[i - 1][:-1]) + 1:
                    run = True
                # going from King to 2
                elif int(card[:-1]) == 2 and int(group[i - 1][:-1]) == 13:                    
                        run = True    
                else:
                    run = False                   
                only_aces = False
                
        if not run:
            return False
    
    return True

def accumulation_check(group):
    """Checks if the total sum of a given list of cards adds to 34"""
    count = 0
    suits = dd(int)
    # change all Aces to 1
    group = list(group)
    group = card_to_number(group, 3)  # change letters and 10 to numbers
  
    for card in group:    
        count += int(card[:-1])
        suits[card[-1]] += 1
        
    if count == 34:
        if 'H' in suits or 'D' in suits:
            if 'S' not in suits and 'C' not in suits:
                return 'coloraccumulation'
                
        elif 'S' in suits or 'C' in suits:
            if 'H' not in suits and 'D' not in suits:
                return 'coloraccumulation'
            
        return 'accumulation'
    return False
