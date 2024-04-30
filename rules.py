# TODO

# vector enums
# cards are a 25 bit one hot vector

# PlaySafeCard
def play_safe_card(env, agent, mask, obs):
    play_mask = mask[5:10]
    # check the obs to see if the card is safe
    obs_playing_red_vector = obs[175:180]
    obs_playing_yellow_vector = obs[180:185]
    obs_playing_green_vector = obs[185:190]
    obs_playing_blue_vector = obs[190:195]
    obs_playing_white_vector = obs[195:200]

    obs_player_first_card = obs[308:343]
    obs_player_second_card = obs[343:378]
    obs_player_third_card = obs[378:413]
    obs_player_fourth_card = obs[413:448]
    obs_player_fifth_card = obs[448:483]
    cards = [obs_player_first_card, obs_player_second_card, obs_player_third_card, obs_player_fourth_card, obs_player_fifth_card]

    # a card is safe when in the first 25 bits of the card info, there is only one bit set to 1
    # this means that the card is known to be a certain color and rank

    # check if the first card is not safe, if not, remove it from the mask
    if sum(obs_player_first_card) != 1:
        play_mask[0] = 0
    if sum(obs_player_second_card) != 1:
        play_mask[1] = 0
    if sum(obs_player_third_card) != 1:
        play_mask[2] = 0
    if sum(obs_player_fourth_card) != 1:
        play_mask[3] = 0
    if sum(obs_player_fifth_card) != 1:
        play_mask[4] = 0
    
    # now, we check the red vector for the last card played
    last_played_red = sum(obs_playing_red_vector)
    last_played_yellow = sum(obs_playing_yellow_vector)
    last_played_green = sum(obs_playing_green_vector)
    last_played_blue = sum(obs_playing_blue_vector)
    last_played_white = sum(obs_playing_white_vector)

    for card in cards:
        # analyze the first 5 bits of the card
        if sum(card[0:5]) == 1:
            # the card is a red card
            index = card.index(1)
            # if the card is bigger by 1 than the last played red card, it is safe to play
            if last_played_red + 1 == index:
                return env.action_space(agent).sample(play_mask)
        elif sum(card[5:10]) == 1:
            # the card is a yellow card
            index = card.index(1)
            if last_played_yellow + 1 == index:
                return env.action_space(agent).sample(play_mask)
        elif sum(card[10:15]) == 1:
            # the card is a green card
            index = card.index(1)
            if last_played_green + 1 == index:
                return env.action_space(agent).sample(play_mask)
        elif sum(card[15:20]) == 1:
            # the card is a blue card
            index = card.index(1)
            if last_played_blue + 1 == index:
                return env.action_space(agent).sample(play_mask)
        elif sum(card[20:25]) == 1:
            # the card is a white card
            index = card.index(1)
            if last_played_white + 1 == index:
                return env.action_space(agent).sample(play_mask)
        else:
            # the card is not safe to play
            return None
# OsawaDiscard

def osawa_discard(env, agent, mask, obs):
    discard_mask = mask[0:5]

    obs_playing_red_vector = obs[175:180]
    obs_playing_yellow_vector = obs[180:185]
    obs_playing_green_vector = obs[185:190]
    obs_playing_blue_vector = obs[190:195]
    obs_playing_white_vector = obs[195:200]

    obs_player_cards = obs[308:483]
    obs_player_first_card = obs[308:343]
    obs_player_second_card = obs[343:378]
    obs_player_third_card = obs[378:413]
    obs_player_fourth_card = obs[413:448]
    obs_player_fifth_card = obs[448:483]

    pass

# TellPlayableCard

# TellRandomly
def tell_random(env, agent, mask, obs):
    tell_mask = mask[10:20]
    return env.action_space(agent).sample(tell_mask)

# DiscardRandomly
def discard_random(env, agent, mask, obs):
    discard_mask = mask[0:5]
    return env.action_space(agent).sample(discard_mask)

# TellPlayableCardOuter
# TellUnknown
# PlayIfCertain
# DiscardOldestFirst
# IfRule(𝜆) Then (Rule) Else (Rule)
# PlayProbablySafeCard(𝑇ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 ∈ [0, 1])
# DiscardProbablyUselessCard(𝑇ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 ∈ [0, 1])
# TellMostInformation(𝑁𝑒𝑤? ∈ [𝑇𝑟𝑢𝑒, 𝐹𝑎𝑙𝑠𝑒])
# TellDispensable