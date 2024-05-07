# Description: This file contains the Policy class which is responsible for generating the policies for the agent.

from rules import *
from Math import log
import time

class Policy:
    def __init__(self, env, agent, mask, obs):
        self.rule = Rule(env, agent, mask, obs)

class MCTS(Policy):
    def __init__(self, env, agent, mask, obs, depth, policy):
        super().__init__(env, agent, mask, obs)
        self.depth = depth
        self.policy = policy

    def upper_confidence_bound(n, ni, c, vi):
        MAX = float('inf')
        return MAX if ni == 0 else vi + c * log(n/ni)
    
    def run(self):
        # Get all nodes (possible actions from current state)
        nodes = self.rule.env.action_space(self.rule.agent)
        (self.rule.mask) # TODO copilot code, make sure it makes sense
        # Repeate this until time runs out
        timeout = time.time() + 60
        while time.time() < timeout:
            # 1. Selection
            # Apply UCB to nodes (possible actions) and randomly select one of the ones with highest value
            def selection(node):
                # TODO idk if htis is needed and if so how to implement it
                # if node.is_leaf():
                #    return node
                # else:
                ##### 
                # return selection(max(node.children, key=lambda child: child.value + upper_confidence_bound(node.n, child.n, 2)))
                return max(node, key=lambda x: self.upper_confidence_bound(x.n, x.ni, c, x.vi))
            # 2. Expansion
            # Expand the tree (choose that move) for self
            def expansion(node):
                return self.policy.run()
            # 3. Simulation
            # Simulate the game until depth level runs out
            def simulation(node):
                return self.rule.env.action_space(self.rule.agent).sample(self.rule.mask)
            # 4. Backpropagate value
            # Update the value of the node selected and its ancestors
            def backpropagation(node, value):
                pass
        
class MCTS_LegalRandom(MCTS):
    def __init__(self, env, agent, mask, obs):
        depth = 1
        policy = LegalRandom(env, agent, mask, obs)
        super().__init__(env, agent, mask, obs, depth, policy)

    def run(self):
        # call the super class run method
        super().run()

# TODO
class Flawed(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        pass  # Implement the flawed policy here

class LegalRandom(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        return self.rule.env.action_space(self.rule.agent).sample(self.rule.mask)

# TODO
class Piers(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        pass  # Implement Piers policy here

# TODO
class IGGI(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        pass  # Implement IGGI policy here

# TODO
class PredictorISMCTS:
    pass