# Legal random

from rules import *

def legal_random(env, agent, mask, obs):
    return env.action_space(agent).sample(mask)

# MCS - Monte Carlo Search (MCTS with depth limit of 1) using "Legal Random" policy for the rollout phase


# Flawed
def flawed(env, agent, mask, obs):
    return env.action_space(agent).sample(mask)