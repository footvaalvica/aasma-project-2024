# import policies.py
from policies import *
from utils import *
from random import randint

SEED = randint(0, 1000)
env = EnvWrapper(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode='human')
env.reset(seed=SEED)

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
        print("action being played is")
        print(action)
        env.action_history.append(action)

        # need to update cards after every play
        cards_age[agent] = update_card_age(card_age, action)

    env.step(action)
env.close()
