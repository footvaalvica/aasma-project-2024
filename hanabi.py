from pettingzoo.classic import hanabi_v5

# import policies.py
from policies import *

env = hanabi_v5.env(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode='human')
env.reset()

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
            policy = LegalRandom(env, agent, mask, obs)
        action = policy.run()

    env.step(action)
env.close()


env = hanabi_v5.env(render_mode="human")
env.reset(seed=42)

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    else:
        mask = observation["action_mask"]
        # this is where you would insert your policy
        action = env.action_space(agent).sample(mask)

    env.step(action)
env.close()