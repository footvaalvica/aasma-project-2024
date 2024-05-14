from pettingzoo.classic import hanabi_v5

# import policies.py
from policies import *

env = hanabi_v5.env(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode = 'human')
env.reset(seed=42)

for agent in env.agent_iter():

    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    else:
        mask = observation["action_mask"]

        print("action mas", mask)
        obs = observation["observation"]
        # this is where you would insert your policy

        print("obs size", len(obs))

        print("thermometer dsicard pile", obs[211:260])

        print("this players first card info", obs[308:333])
        
        print("revealed color", obs[333:338])

        print("revealed rank", obs[338:343])

        policy = LegalRandom(env, agent, mask, obs)
        action = policy.run()

    env.step(action)
env.close()