# import policies.py
from policies import *
from utils import *
from random import randint
import sys

if len(sys.argv) > 1:
    seed = int(sys.argv[1])
else:
    seed = randint(0, 1000)
env = EnvWrapper(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode='human')
env.reset(seed=seed)

env.render()

# need to have card_age for all players, useful in some rules
cards_age = {}
for i in range(env.num_agents):
    cards_age_key = f"player_{i}"
    cards_age[cards_age_key] = [0, 0, 0, 0, 0]

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    card_age = cards_age[agent]
    if termination or truncation:
        action = None
    else:
        mask = observation["action_mask"]
        obs = observation["observation"]

        # this is where you would insert your policy
        if agent == "player_0":
            policy = PlayerInput(env, agent, mask, obs, card_age)
        else:
            policy = IGGI(env, agent, mask, obs, card_age)
        action = policy.run()
        print(f"action being played is {action}")
        env.action_history.append(action)

        # check if action results in an error
        if agent == "player_0":
            player_cards = env.observe("player_1")["observation"][0:125]
        else:
            player_cards = env.observe("player_0")["observation"][0:125]
        fireworks = obs[167:192]
        env.errors[agent] += update_errors(player_cards, fireworks, action)

        print(f"errors are {env.errors[agent]}")
        # need to update cards after every play
        cards_age[agent] = update_card_age(card_age, action)

    env.step(action)
env.close()
