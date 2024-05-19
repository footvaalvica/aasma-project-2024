from pettingzoo.classic import hanabi_v5

# import policies.py
from policies import *
from utils import *
from random import randint

SEED = randint(0, 1000)
env = EnvWrapper(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode='human')
env.reset(seed=SEED)

env.render()

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    if termination or truncation:
        action = None
    else:
        mask = observation["action_mask"]
        obs = observation["observation"]
        # this is where you would insert your policy
        if agent == "player_0":
            policy = PlayerInput(env, agent, mask, obs)
        else:
            policy = MCS_LegalRandom(env, agent, mask, obs)
        action = policy.run()
        env.action_history.append(action)

    env.step(action)
env.close()
