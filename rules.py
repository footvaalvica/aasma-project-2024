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
            self._obs_playing_blue_vector = obs[190:195]
            self._obs_playing_white_vector = obs[195:200]
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
            # Revealed Info of Other Player’s Xth Card
            self._obs_other_first_card = obs[483:518]
            self._obs_other_second_card = obs[518:553]
            self._obs_other_third_card = obs[553:588]
            self._obs_other_fourth_card = obs[588:623]
            self._obs_other_fifth_card = obs[663:657]
            self._cards = [self._obs_player_first_card, self._obs_player_second_card, self._obs_player_third_card, self._obs_player_fourth_card, self._obs_player_fifth_card]

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

    # TODO PlaySafeCard
    def play_safe_card(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        pass

    # TODO OsawaDiscard
    def osawa_discard(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        pass

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
        
        # this code checks if the card is safe to play if we are certain about it
        # TODO @tiago pls check not sure if correct

        last_played_red = sum(self._obs_playing_red_vector)
        last_played_yellow = sum(self._obs_playing_yellow_vector)
        last_played_green = sum(self._obs_playing_green_vector)
        last_played_blue = sum(self._obs_playing_blue_vector)
        last_played_white = sum(self._obs_playing_white_vector)

        # if the card is certain, we can check if it is safe to play
        # a card is safe to play
        return None

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

    # TODO PlayProbablySafeCard(𝑇ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 ∈ [0, 1]) @Tiago
    def play_probably_safe_card(self, env, agent, mask, obs, threshold):
        self._update_all(env, agent, mask, obs)
        pass

    # TODO TellAnyoneAboutUsefulCard
    def tell_anyone_about_useful_card(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        pass