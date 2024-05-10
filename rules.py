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

    def _update_card_age(self, action: int):
        self._card_age = [0, 0, 0, 0, 0]

        # increment all elements by 1
        self._card_age = [x + 1 for x in self._card_age]

        if action < 5:
            # it's a discard action
            # they map from 0 to 4 to the cards from left to right
            self._card_age[action] = 0
        elif 5 < action < 10:
            # it's a play action
            # they map from 5 to 9 to the cards from left to right
            self._card_age[action - 5] = 0
        else:
            # we can ignore tell actions
            pass
        
    def _update_all(self, env, agent, mask, obs):
        def _update_obs(obs):
            # Vector of Card X in other player’s hand
            self._obs_hand_other_ones = obs[0:25]
            self._obs_hand_other_twos = obs[25:50]
            self._obs_hand_other_threes = obs[50:75]
            self._obs_hand_other_fours = obs[75:100]
            self._obs_hand_other_fives = obs[100:125]
            # Unary encoding of remaning deck size
            self._obs_unary_remaining_deck = obs[125:175]
            # Vector of <Color> Firework
            self._obs_playing_red_vector = obs[175:180]
            self._obs_playing_yellow_vector = obs[180:185]
            self._obs_playing_green_vector = obs[185:190]
            self._obs_playing_white_vector = obs[190:195]
            self._obs_playing_blue_vector = obs[195:200]
            self._firework_info = [self._obs_playing_red_vector, self._obs_playing_yellow_vector, self._obs_playing_green_vector,
                         self._obs_playing_white_vector, self._obs_playing_blue_vector]
            
            self._obs_remaining_info_tokens = obs[200:208]
            self._obs_remaining_life_tokens = obs[208:211]
            self._obs_discard_thermometer_encoding = obs[211:261]
            # Revealed Info of This Player’s Xth Card
            self._obs_previous_player_id = obs[261:263]
            self._obs_previous_player_action_type = obs[263:267]
            self._obs_previous_action_target = obs[267:269]
            self._obs_previous_action_color_revealed = obs[269:274]
            self._obs_previous_action_rank_revealed = obs[274:279]
            self._obs_which_card_revealed = obs[279:281]
            self._obs_position_played_card = obs[281:283]
            self._obs_last_played_card = obs[283:308]
            self._obs_player_first_card = obs[308:343]
            self._obs_player_second_card = obs[343:378]
            self._obs_player_third_card = obs[378:413]
            self._obs_player_fourth_card = obs[413:448]
            self._obs_player_fifth_card = obs[448:483]
            self._cards = [self._obs_player_first_card, self._obs_player_second_card, self._obs_player_third_card, 
                           self._obs_player_fourth_card, self._obs_player_fifth_card]
            # Revealed Info of Other Player’s Xth Card
            self._obs_other_first_card = obs[483:518]
            self._obs_other_second_card = obs[518:553]
            self._obs_other_third_card = obs[553:588]
            self._obs_other_fourth_card = obs[588:623]
            self._obs_other_fifth_card = obs[663:657]
            

        def _update_mask(mask):
            self._discard_mask = mask[0:5]
            self._play_mask = mask[5:10]
            self._tell_mask = mask[10:20]

        def _update_agent(env, agent):
            self._agent = agent
            self._env = env

        _update_obs(obs)
        _update_mask(mask)
        _update_agent(env, agent)
    
    # constructor
    def __init__(self, env, agent, mask, obs):
        self.card_age = [0, 0, 0, 0, 0]
        self._update_all(env, agent, mask, obs)

    # TODO #1 PlaySafeCard
    def play_safe_card(self, env, agent, mask, obs):
        # go read down below, probably somethings are already done in PlayIfCertain
        self._update_all(env, agent, mask, obs)

        # besides looking at possible cards on hand, it should also look at cards that have been discarded in only to narrow down options
        pass

    # TODO #2 OsawaDiscard
    def osawa_discard(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)

        for card, index in zip(self._cards, [0,1,2,3,4]):
            color_info = card[25:30]
            rank_info = card[30:35]
            max_rank = len(rank_info) - rank_info[::-1].index(1) - 1 # gets highest 1 from the rank_info list

            # let's use the color and rank info first because it's more efficient if it has any info useful for discarding
            discard = True # flag to know whether to discard or not
            for color, firework in zip(color_info, self._firework_info):
                if color == 0:
                    continue
                max_firework_rank = firework.index(0) - 1
                if max_rank > max_firework_rank:
                    # can't discard if max rank is higher than the current firework rank
                    discard = False
                    break
                    
            if discard == True:
                if self._discard_mask[index] == 1:
                        return index
            
            # now let's use the information gathered from the first 25 bits of each card info
            # not sure if using both infos is a redundancy
            discard = True
            card_infos = [card[0:5], card[5:10], card[10:15], card[15:20], card[20:25]]
            for card_info, firework in zip(card_infos, self._firework_info):
                if 1 not in card_info:
                    continue
                max_rank = len(card_info) - card_info[::-1].index(1) - 1
                max_firework_rank = firework.index(0) - 1
                if max_rank > max_firework_rank:
                    # discard that card
                    discard = False
                    break
                    
            if discard == True:
                if self._discard_mask[index] == 1:
                        return index

        # if it passes to this stage, then we can't discard any card
        return -1

    # TellRandomly
    def tell_random(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        return self._env.action_space(self._agent).sample(self._tell_mask)

    # DiscardRandomly
    def discard_random(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        action = self._env.action_space(self._agent).sample(self._discard_mask)
        self._update_card_age(action)
        return action
    
    # PlayIfCertain
    def play_if_certain(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        # a card is certain when in the first 25 bits of the card info, there is only one bit set to 1
        # this means that the card is known to be a certain color and rank
        # check if the card is certain
        self._check_certain_cards()

        # we can return now if the playmask is all 0
        if sum(self._play_mask) == 0:
            return None

        # TODO The code below can probably be reused for PlaySafeCard

        last_played_red = sum(self._obs_playing_red_vector)
        last_played_yellow = sum(self._obs_playing_yellow_vector)
        last_played_green = sum(self._obs_playing_green_vector)
        last_played_blue = sum(self._obs_playing_blue_vector)
        last_played_white = sum(self._obs_playing_white_vector)
        last_played = [last_played_red, last_played_yellow, last_played_green, last_played_white, last_played_blue]

        # remove all cards from the mask
        self._play_mask = [0, 0, 0, 0, 0]

        for i in self._cards:
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
        self._update_card_age(action)
        return action

    def discard_oldest_first(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)

        # get the oldest card
        oldest_card = self._card_age.index(max(self._card_age))

        # change the discard mask to only discard the oldest card
        self._discard_mask = [0, 0, 0, 0, 0]
        self._discard_mask[oldest_card] = 1

        action = self._env.action_space(self._agent).sample(self._discard_mask)
        self._update_card_age(action)
        return action

    # TODO #3 PlayProbablySafeCard(𝑇ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 ∈ [0, 1])
    def play_probably_safe_card(self, env, agent, mask, obs, threshold):
        self._update_all(env, agent, mask, obs)
        pass

    # TODO #4 TellAnyoneAboutUsefulCard
    def tell_anyone_about_useful_card(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        pass