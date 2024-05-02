# Description: This file contains the Policy class which is responsible for generating the policies for the agent.

from rules import *
class Policy:
    def __init__(self, env, agent, mask, obs):
        self.rule = Rule(env, agent, mask, obs)

    def legal_random(self):
        return self.rule.env.action_space(self.rule.agent).sample(self.rule.mask)

    def flawed(self):
        pass  # Implement the flawed policy here