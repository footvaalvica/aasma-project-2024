# This file contains the rules for the Hanabi game agent. The rules are implemented as methods of the Rules class. The Rules class is used by the Policy class to generate policies for the agent.
class Rule:
    # every method should update the obs and mask

    # auxiliary functions
    # TODO maybe refacotr this into a static method
    def _check_certain_cards(self):
        if sum(self._obs_player_first_card[0:25]) != 1:
            self._play_mask[0] = 0
        if sum(self._obs_player_second_card[0:25]) != 1:
            self._play_mask[1] = 0
        if sum(self._obs_player_third_card[0:25]) != 1:
            self._play_mask[2] = 0
        if sum(self._obs_player_fourth_card[0:25]) != 1:    
            self._play_mask[3] = 0
        if sum(self._obs_player_fifth_card[0:25]) != 1:
            self._play_mask[4] = 0
        
    def _update_all(self, env, agent, mask, obs):
        def _update_obs(obs):
            it = 0
            self._obs_other_players_hands = {}
            for i in range(env.num_agents - 1):
                # Vector of Card X in other player’s hand
                card1 = obs[it : it+25]
                card2 = obs[it+25 : it+50]
                card3 = obs[it+50 : it+75]
                card4 = obs[it+75 : it+100]
                card5 = obs[it+100 : it+125]
                cards = [card1, card2, card3, card4, card5]
                self._obs_other_players_hands[f"next_player_{i}"] = cards
                it = it + 125

            # Unary encoding of remaning deck size
            self._obs_unary_remaining_deck = obs[it : it+50]
            it = it + 50

            # Vector of <Color> Firework
            red_vector = obs[it : it+5]
            yellow_vector = obs[it+5 : it+10]
            green_vector = obs[it+10 : it+15]
            white_vector = obs[it+15 : it+20]
            blue_vector = obs[it+20 : it+25]
            self._obs_firework_info = [red_vector, yellow_vector, green_vector, white_vector, blue_vector]
            it = it + 25
            
            # Info regarding remaining tokens
            self._obs_remaining_info_tokens = obs[it : it+8]
            self._obs_remaining_life_tokens = obs[it+8 : it+11]
            it = it + 11

            # Info regarding already discarded cards
            discarded_reds = obs[it : it+10]
            discarded_yellows = obs[it+10 : it+20]
            discarded_greens = obs[it+20 : it+30]
            discarded_whites = obs[it+30 : it+40]
            discarded_blues = obs[it+40 : it+50]
            self._obs_discarded_cards = [discarded_reds, discarded_yellows, discarded_greens, discarded_whites, discarded_blues]
            it = it + 50
            
            # Miscellaneous information about game
            self._obs_previous_player_id = obs[it : it+2]
            self._obs_previous_player_action_type = obs[it+2 : it+6]
            self._obs_previous_action_target = obs[it+6 : it+8]
            self._obs_previous_action_color_revealed = obs[it+8 : it+13]
            self._obs_previous_action_rank_revealed = obs[it+13 : it+18]
            self._obs_which_card_revealed = obs[it+18 : it+20]
            self._obs_position_played_card = obs[it+20 : it+22]
            self._obs_last_played_card = obs[it+22 : it+47]
            it = it + 47

            # Revealed info about players cards
            first_card = obs[it : it+35]
            second_card = obs[it+35 : it+70]
            third_card = obs[it+70 : it+105]
            fourth_card = obs[it+105 : it+140]
            fifth_card = obs[it+140 : it+175]
            self._cards_info = [first_card, second_card, third_card, fourth_card, fifth_card]
            it = it + 175

            # Revealed Info of Other Player’s Xth Card
            self._obs_other_players_cards_info = {}
            for i in range(env.num_agents - 1):
                card1_info = obs[it : it+35]
                card2_info = obs[it+35 : it+70]
                card3_info = obs[it+70 : it+105]
                card4_info = obs[it+105 : it+140]
                card5_info = obs[it+140 : it+175]
                cards_info = [card1_info, card2_info, card3_info, card4_info, card5_info]
                self._obs_other_players_cards_info[f"next_player_{i}"] = cards_info
                it = it + 175

        def _update_mask(mask):
            self._mask = mask
            self._discard_mask = mask[0:5]
            self._play_mask = mask[5:10]
            # tell mask may have multiple other players
            self._tell_mask = []
            it = 0
            for i in range(env.num_agents - 1):
                self._tell_mask.append(mask[it : it+10])
                it = it + 10

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
                probabilities[index] = safe_plays / (safe_plays + unsafe_plays)

        highest_prob = max(probabilities)

        if highest_prob >= threshold:
            for prob, prob_index in zip(probabilities, [0,1,2,3,4]):
                if prob == highest_prob:
                    return prob_index + 5 # the action_space index for the play action
        else:
            return None # no probability is higher than the threshold

    # TODO #1 PlaySafeCard
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
        # check if the card is certain
        self._check_certain_cards()

        # we can return now if the playmask is all 0
        if sum(self._play_mask) == 0:
            return None

        # TODO The code below can probably be reused for PlaySafeCard

        last_played_red = sum(self._obs_firework_info[0])
        last_played_yellow = sum(self._obs_firework_info[1])
        last_played_green = sum(self._obs_firework_info[2])
        last_played_blue = sum(self._obs_firework_info[3])
        last_played_white = sum(self._obs_firework_info[4])
        last_played = [last_played_red, last_played_yellow, last_played_green, last_played_white, last_played_blue]

        # remove all cards from the mask
        self._play_mask = [0, 0, 0, 0, 0]

        for i in self._cards_info:
            red_vector = i[0:5]
            yellow_vector = i[5:10]
            green_vector = i[10:15]
            white_vector = i[15:20]
            blue_vector = i[20:25]
            vectors = [red_vector, yellow_vector, green_vector, white_vector, blue_vector]

            for i, vector in enumerate(vectors):
                # get the index of the first bit set to one in the vector
                index = vector.index(1)
                current_last_played = last_played[i]

                if index == current_last_played:
                    # the card is the next card in the firework
                    # we can play it
                    self._play_mask[i] = 1
        
        action = self._env.action_space(self._agent).sample(self._play_mask)
        return action

    def discard_oldest_first(self):
        # get the oldest card
        oldest_card = self._card_age.index(max(self._card_age))

        return oldest_card

    # goes through every oponents card and checks if it can be played
    def tell_anyone_about_useful_card(self):
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
                    color_info = other_card_info[25:30]
                    rank_info = other_card_info[30:35]
                    if color_info.count(1) > 1:
                        if self._mask[indexes[0] + 10 + counter*10] == 1:
                            return indexes[0] + 10 + counter*10
                    elif rank_info.count(1) > 1:
                        if self._mask[indexes[1] + 15 + counter*10] == 1:
                            return indexes[1] + 15 + counter*10
                        
            counter = counter + 1

        return None

    
    def tell_dispensable(self):
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

                    color_info = other_cards_info[discarded_card][25:30]
                    rank_info = other_cards_info[discarded_card][30:35]
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
            rank_1_infos = discarded_cards[0:3]
            rank_2_infos = discarded_cards[3:5]
            rank_3_infos = discarded_cards[5:7]
            rank_4_infos = discarded_cards[7:9]
            rank_5_infos = discarded_cards[9]
            discard_rank_infos = [rank_1_infos, rank_2_infos, rank_3_infos,
                                    rank_4_infos, rank_5_infos]
            max_possible_rank = len(color_info) - color_info[::-1].index(1) - 1 # gets highest 1 from the color_info list

            discard = False
            for i in range(max_possible_rank, 6):
                if 1 in discard_rank_infos[i]:
                    discard = True
                    break

            if discard == True:
                if rule._discard_mask[index] == 1:
                    possible_discards.append(index)
                    break

    # if there are no discarded cards return None
    if len(discarded_cards) > 0:
        return discarded_cards
    return None
    
    
