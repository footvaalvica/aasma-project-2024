# This file contains the rules for the Hanabi game agent. The rules are implemented as methods of the Rules class. The Rules class is used by the Policy class to generate policies for the agent.
class Rule:
    # every method should update the obs and mask

    # auxiliary functions
    def _check_certain_card(self):
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
            self._obs_playing_red_vector = obs[175:180]
            self._obs_playing_yellow_vector = obs[180:185]
            self._obs_playing_green_vector = obs[185:190]
            self._obs_playing_blue_vector = obs[190:195]
            self._obs_playing_white_vector = obs[195:200]
            self._obs_player_first_card = obs[308:343]
            self._obs_player_second_card = obs[343:378]
            self._obs_player_third_card = obs[378:413]
            self._obs_player_fourth_card = obs[413:448]
            self._obs_player_fifth_card = obs[448:483]
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
        self._update_all(env, agent, mask, obs)


    # vector enums
    # cards are a 25 bit one hot vector

    # PlaySafeCard

    # OsawaDiscard

    def osawa_discard(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        pass

    # TellPlayableCard

    # TellRandomly
    def tell_random(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        return self._env.action_space(self._agent).sample(self._tell_mask)

    # DiscardRandomly
    def discard_random(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        return self._env.action_space(self._agent).sample(self._discard_mask)

    # TellPlayableCardOuter
    # TellUnknown
    # PlayIfCertain
    def play_if_certain(self, env, agent, mask, obs):
        self._update_all(env, agent, mask, obs)
        # a card is certain when in the first 25 bits of the card info, there is only one bit set to 1
        # this means that the card is known to be a certain color and rank
        # check if the card is certain
        self._check_certain_card()

        # we can return now if the playmask is all 0
        if sum(self._play_mask) == 0:
            return None
        
        # now, we check the red vector for the last card played
        last_played_red = sum(self._obs_playing_red_vector)
        last_played_yellow = sum(self._obs_playing_yellow_vector)
        last_played_green = sum(self._obs_playing_green_vector)
        last_played_blue = sum(self._obs_playing_blue_vector)
        last_played_white = sum(self._obs_playing_white_vector)

        for card in self._cards:
            # analyze the first 5 bits of the card
            if sum(card[0:5]) == 1:
                # the card is a red card
                index = card.index(1)
                # if the card is bigger by 1 than the last played red card, it is safe to play
                if last_played_red + 1 == index:
                    return self._env.action_space(self._agent).sample(self._play_mask)
            elif sum(card[5:10]) == 1:
                # the card is a yellow card
                index = card.index(1)
                if last_played_yellow + 1 == index:
                    return self._env.action_space(self._agent).sample(self._play_mask)
            elif sum(card[10:15]) == 1:
                # the card is a green card
                index = card.index(1)
                if last_played_green + 1 == index:
                    return self._env.action_space(self._agent).sample(self._play_mask)
            elif sum(card[15:20]) == 1:
                # the card is a blue card
                index = card.index(1)
                if last_played_blue + 1 == index:
                    return self._env.action_space(self._agent).sample(self._play_mask)
            elif sum(card[20:25]) == 1:
                # the card is a white card
                index = card.index(1)
                if last_played_white + 1 == index:
                    return self._env.action_space(self._agent).sample(self._play_mask)
            else:
                # the card is not safe to play
                return None


            
    # DiscardOldestFirst
    # IfRule(𝜆) Then (Rule) Else (Rule)
    # PlayProbablySafeCard(𝑇ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 ∈ [0, 1])
    # DiscardProbablyUselessCard(𝑇ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 ∈ [0, 1])
    # TellMostInformation(𝑁𝑒𝑤? ∈ [𝑇𝑟𝑢𝑒, 𝐹𝑎𝑙𝑠𝑒])
    # TellDispensable