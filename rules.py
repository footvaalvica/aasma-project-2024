import numpy as np

# This file contains the rules for the Hanabi game agent. The rules are implemented as methods of the Rules class. The Rules class is used by the Policy class to generate policies for the agent.
class Rule:
    
    # methods to update the game variables
    def _update_all(self, env, agent, mask, obs):
        def _update_obs(obs):
            it = 0
            self._obs_other_players_hands = {}
            for i in range(env.num_agents - 1):
                # Vector of Card X in other player’s hand
                card1 = obs[it : it+25]
                # # print(f"card1 (player {i}): {card1}")
                card2 = obs[it+25 : it+50]
                # # print(f"card2 (player {i}): {card2}")
                card3 = obs[it+50 : it+75]
                # # print(f"card3 (player {i}): {card3}")
                card4 = obs[it+75 : it+100]
                # # print(f"card4 (player {i}): {card4}")
                card5 = obs[it+100 : it+125]
                # # print(f"card5 (player {i}): {card5}")
                cards = [card1, card2, card3, card4, card5]
                self._obs_other_players_hands[f"next_player_{i}"] = cards
                it = it + 125

            # Unary encoding of remaining deck size
            self._obs_unary_remaining_deck = obs[it : it+50]
            # # print(f"self._obs_unary_remaining_deck: {self._obs_unary_remaining_deck}")
            it = it + 50 - 8 # for some reason, have to go back 8

            # Vector of <Color> Firework
            red_vector = obs[it : it+5]
            # # print(f"red_vector: {red_vector}")
            yellow_vector = obs[it+5 : it+10]
            # # print(f"yellow_vector: {yellow_vector}")
            green_vector = obs[it+10 : it+15]
            # # print(f"green_vector: {green_vector}")
            white_vector = obs[it+15 : it+20]
            # # print(f"white_vector: {white_vector}")
            blue_vector = obs[it+20 : it+25]
            # # print(f"blue_vector: {blue_vector}")
            self._obs_firework_info = [red_vector, yellow_vector, green_vector, white_vector, blue_vector]
            it = it + 25

            # Info regarding remaining tokens
            self._obs_remaining_info_tokens = obs[it : it+8]
            # # print(f"self._obs_remaining_info_tokens: {self._obs_remaining_info_tokens}")
            self._obs_remaining_life_tokens = obs[it+8 : it+11]
            # # print(f"self._obs_remaining_life_tokens: {self._obs_remaining_life_tokens}")
            it = it + 11

            # Info regarding already discarded cards
            discarded_reds = obs[it : it+10]
            # # print(f"discarded_reds: {discarded_reds}")
            discarded_yellows = obs[it+10 : it+20]
            # # print(f"discarded_yellows: {discarded_yellows}")
            discarded_greens = obs[it+20 : it+30]
            # # print(f"discarded_greens: {discarded_greens}")
            discarded_whites = obs[it+30 : it+40]
            # # print(f"discarded_whites: {discarded_whites}")
            discarded_blues = obs[it+40 : it+50]
            # # print(f"discarded_blues: {discarded_blues}")
            self._obs_discarded_cards = [discarded_reds, discarded_yellows, discarded_greens, discarded_whites, discarded_blues]
            it = it + 50

            # Miscellaneous information about game (might not be 100% certain)
            self._obs_previous_player_id = obs[it : it+2]
            self._obs_previous_player_action_type = obs[it+2 : it+6]
            self._obs_previous_action_target = obs[it+6 : it+8]
            self._obs_previous_action_color_revealed = obs[it+8 : it+13]
            self._obs_previous_action_rank_revealed = obs[it+13 : it+18]
            self._obs_which_card_revealed = obs[it+18 : it+20]
            self._obs_position_played_card = obs[it+20 : it+22]
            self._obs_last_played_card = obs[it+22 : it+47]
            it = it + 47 + 8

            # Revealed info about player's cards
            first_card = obs[it : it+35]
            # # print(f"first_card: {first_card}")
            second_card = obs[it+35 : it+70]
            # # print(f"second_card: {second_card}")
            third_card = obs[it+70 : it+105]
            # # print(f"third_card: {third_card}")
            fourth_card = obs[it+105 : it+140]
            # # print(f"fourth_card: {fourth_card}")
            fifth_card = obs[it+140 : it+175]
            # # print(f"fifth_card: {fifth_card}")
            self._cards_info = [first_card, second_card, third_card, fourth_card, fifth_card]
            it = it + 175

            # Revealed Info of Other Player’s Xth Card
            self._obs_other_players_cards_info = {}
            for i in range(env.num_agents - 1):
                card1_info = obs[it : it+35]
                # # print(f"card1_info (player {i}): {card1_info}")
                card2_info = obs[it+35 : it+70]
                # # print(f"card2_info (player {i}): {card2_info}")
                card3_info = obs[it+70 : it+105]
                # # print(f"card3_info (player {i}): {card3_info}")
                card4_info = obs[it+105 : it+140]
                # # print(f"card4_info (player {i}): {card4_info}")
                card5_info = obs[it+140 : it+175]
                # print(f"card5_info (player {i}): {card5_info}")
                cards_info = [card1_info, card2_info, card3_info, card4_info, card5_info]
                self._obs_other_players_cards_info[f"next_player_{i}"] = cards_info
                it = it + 175

        def _update_mask(mask):
            # only fit for 2 player games
            self._mask = mask
            self._discard_mask = mask.copy()
            self._discard_mask[5:] = 0
            self._play_mask = mask.copy()
            self._play_mask[0:5] = 0
            self._play_mask[10:] = 0
            self._tell_mask = mask.copy()
            self._tell_mask[0:10] = 0

        def _update_agent(env, agent):
            self._agent = agent
            self._env = env

        _update_obs(obs)
        _update_mask(mask)
        _update_agent(env, agent)
    
    # constructor
    def __init__(self, env, agent, mask, obs, card_age):
        self.card_age = card_age
        self._update_all(env, agent, mask, obs)
    
    def get_mask(self):
        return self._mask

    # PlayProbablySafeCard(𝑇ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 ∈ [0, 1]) - goes through every possible action and defines a ration 
    # (safe actions/safe + unsafe actions), if the ration is above the threshold for any card, plays that card
    def play_probably_safe_card(self, threshold):
        probabilities = [0.0, 0.0, 0.0, 0.0, 0.0]
        
        for card, index in zip(self._cards_info, [0,1,2,3,4]):
            safe_plays = 0
            unsafe_plays = 0
            color_infos = [card[0:5], card[5:10], card[10:15], card[15:20], card[20:25]]
            for color_info, firework in zip(color_infos, self._obs_firework_info):
                firework = firework.tolist()
                max_firework_rank = firework.index(0) - 1
                # next, searches every possible play and evaluates if it is safe or unsafe
                # it's only safe if the index of the play equals the max_firework_rank + 1 (next card in line)
                for play, play_index in zip(color_info, [0,1,2,3,4]):
                    if play == 0:
                        continue
                    if play_index <= max_firework_rank or play_index > max_firework_rank + 1:
                        unsafe_plays += 1
                    else:
                        safe_plays += 1
                if safe_plays + unsafe_plays == 0:
                    continue
                probabilities[index] = safe_plays / (safe_plays + unsafe_plays)

        highest_prob = max(probabilities)

        if highest_prob >= threshold:
            for prob, prob_index in zip(probabilities, [0,1,2,3,4]):
                if prob == highest_prob:
                    return prob_index + 5 # the action_space index for the play action
        else:
            return None # no probability is higher than the threshold

    def play_safe_card(self):
        # go read down below, probably somethings are already done in PlayIfCertain
        return self.play_probably_safe_card(1)

        # besides looking at possible cards on hand, it should also look at cards that have been discarded in only to narrow down options

    # OsawaDiscard - if a card is safe to discard (meaning that in no way can that card be played in the future), discards that card
    def osawa_discard(self):
        discarded_cards = check_discard(self, self._cards_info)

        if discarded_cards is None:
            return None
        else:
            return discarded_cards[0]

    # TellRandomly
    def tell_random(self):
        return self._env.action_space(self._agent).sample(self._tell_mask)

    # DiscardRandomly
    def discard_random(self):
        action = self._env.action_space(self._agent).sample(self._discard_mask)
        return action
    
    # PlayIfCertain
    def play_if_certain(self):
        # a card is certain when in the first 25 bits of the card info, there is only one bit set to 1
        # this means that the card is known to be a certain color and rank
        for index, card in zip([0,1,2,3,4], self._cards_info):
            card = card.tolist()
            # if we're not certain of which card it is, move on
            if sum(card) > 1:
                continue
            color_infos = [card[0:5], card[5:10], card[10:15], card[15:20], card[20:25]]
            # now let's check each info individually
            for color_info, firework in zip(color_infos, self._obs_firework_info):
                firework = firework.tolist()
                if 1 not in color_info:
                    continue
                info_rank = color_info.index(1)
                current_rank = sum(firework)
                # if rank of info is the same as sum of firework, then card is playable
                if info_rank == current_rank:
                    if self._mask[index + 5] == 1:
                        return index + 5
            
        return None
    
    def discard_oldest_first(self):
        # get the oldest card
        card_ages = self.card_age
        oldest_card = card_ages.index(max(card_ages))

        # if has 8 info tokens, can't tell
        if sum(self._obs_remaining_info_tokens) == 8:
            return None

        return oldest_card

    # goes through every oponents card and checks if it can be played
    def tell_anyone_about_useful_card(self):
        # can't tell if there are no more info tokens
        if 1 not in self._obs_remaining_life_tokens:
            return None
        
        counter = 0
        for other_cards_key, other_cards_info_key in zip(self._obs_other_players_hands, self._obs_other_players_cards_info):
            other_cards = self._obs_other_players_hands[other_cards_key]
            other_cards_info = self._obs_other_players_cards_info[other_cards_info_key]
            # need to go through each card at a time
            for other_card, other_card_info in zip(other_cards, other_cards_info):
                for color in range(5):
                    for rank in range(5):
                        if other_card[color*5 + rank] == 1:
                            indexes = [color, rank]
                # if the card being analyzed is the next in line for its color, it's useful
                if sum(self._obs_firework_info[indexes[0]]) == indexes[1]:
                    color_info = other_card_info[25:30].tolist()
                    rank_info = other_card_info[30:35].tolist()
                    if color_info.count(1) > 1 or color_info.count(1) == 0:
                        if self._mask[indexes[0] + 10 + counter*10] == 1:
                            return indexes[0] + 10 + counter*10
                    elif rank_info.count(1) > 1 or rank_info.count(1) == 0:
                        if self._mask[indexes[1] + 15 + counter*10] == 1:
                            return indexes[1] + 15 + counter*10
                        
            counter = counter + 1

        return None

    
    def tell_dispensable(self):
        # can't tell if there are no more info tokens
        if 1 not in self._obs_remaining_life_tokens:
            return None
        
        counter = 0
        for other_cards_key, other_cards_info_key in zip(self._obs_other_players_hands, self._obs_other_players_cards_info):
            other_cards = self._obs_other_players_hands[other_cards_key]
            other_cards_info = self._obs_other_players_cards_info[other_cards_info_key]

            discarded_cards = check_discard(self, other_cards)
            indexes = []

            if discarded_cards is None:
                continue
            else:
                for discarded_card in discarded_cards:
                    other_card = other_cards[discarded_card]
                    for color in range(5):
                        for rank in range(5):
                            if other_card[color*5 + rank] == 1:
                                indexes = [color, rank]

                    color_info = other_cards_info[discarded_card][25:30].tolist()
                    rank_info = other_cards_info[discarded_card][30:35].tolist()
                    if color_info.count(1) == 1 and rank_info.count(1) != 1:
                        if self._mask[indexes[1] + 15 + counter*10] == 1:
                            return indexes[1] + 15 + counter*10
                    if color_info.count(1) != 1 and rank_info.count(1) == 1:
                        if self._mask[indexes[0] + 10 + counter*10] == 1:
                            return indexes[0] + 10 + counter*10
            counter = counter + 1
                        
        return None
                
# auxiliary functions not inside class Rule

# go through a set of cards and checks if any of them can be discarded, returns the ones that can

def check_discard(rule, cards):

    possible_discards = []

    for card, index in zip(cards, [0,1,2,3,4]):
        # let's use the information gathered from the first 25 bits of each card info
        discard = True
        color_infos = [card[0:5], card[5:10], card[10:15], card[15:20], card[20:25]]
        for color_info, firework in zip(color_infos, rule._obs_firework_info):
            color_info = color_info.tolist()
            firework = firework.tolist()
            if 1 not in color_info:
                continue
            max_rank = len(color_info) - color_info[::-1].index(1) - 1
            max_firework_rank = firework.index(0) - 1
            if max_rank > max_firework_rank:
                # can't discard if max rank is higher than the current firework rank
                discard = False
                break
                
        if discard == True:
            if rule._discard_mask[index] == 1:
                possible_discards.append(index)
                break

        # also needs to look at the thermometer encoded pile of cards discarded
        
        for color_info, discarded_cards in zip(color_infos, rule._obs_discarded_cards):
            color_info = color_info.tolist()
            rank_1_infos = discarded_cards[0:3]
            rank_2_infos = discarded_cards[3:5]
            rank_3_infos = discarded_cards[5:7]
            rank_4_infos = discarded_cards[7:9]
            rank_5_infos = discarded_cards[9]
            discard_rank_infos = [rank_1_infos, rank_2_infos, rank_3_infos,
                                    rank_4_infos, np.array(rank_5_infos)]
            if 1 not in color_info:
                continue
            max_possible_rank = len(color_info) - color_info[::-1].index(1) - 1 # gets highest 1 from the color_info list

            discard = False
            for i in range(max_possible_rank, 5):
                if 1 in discard_rank_infos[i]:
                    discard = True
                    break

            if discard == True:
                if rule._discard_mask[index] == 1:
                    possible_discards.append(index)
                    break

    # if there are no discarded cards return None
    if len(possible_discards) > 0:
        return possible_discards
    return None
    
    
