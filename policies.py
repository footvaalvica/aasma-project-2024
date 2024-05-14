# Description: This file contains the Policy class which is responsible for generating the policies for the agent.

from rules import *
from Math import log
from copy import deepcopy
import time

class Policy:
    def __init__(self, env, agent, mask, obs):
        self.rule = Rule(env, agent, mask, obs)

# TODO #6 MCTS Policy
class MCTS(Policy):
    def __init__(self, env, agent, mask, obs, depth, policy, timelimit):
        super().__init__(env, agent, mask, obs)
        self.depth = depth
        self.policy = policy
        self.timelimit = timelimit
    
    class Node:
        def __init__(self, action, state, parent=None):
            self.state = state # TODO use this when choosing a move
            self.action = action
            self.parent = parent
            self.children = []
            self.ni = 0 # number of simulations done for this node
            self.vi = 0 # mean value of this node

        def is_leaf(self):
            return len(self.children) == 0

    def upper_confidence_bound(n, ni, c, vi):
        MAX = float('inf')
        return MAX if ni == 0 else vi + c * log(n/ni)

    def run(self):
        # Get all nodes (possible actions from current state)
        actions = self.rule.env.action_space(self.rule.agent)
        # Map a node to each (copy/deepcopy of the state first)
        nodes = [self.Node(action, self.rule.env.copy().step(action)) for action in actions]

        # Create a temporary board for main loop
        restoreEnv = deepcopy(self.rule.env)
        # Repeat this until time runs out
        timeout = time.time() + self.timelimit
        while time.time() < timeout: 
            # 1. Selection
            # Apply UCB to nodes (possible actions) and randomly select one of the ones with highest value
            def selection(node):
                return max(node, key=lambda x: self.upper_confidence_bound(
                    x.parent.ni if x.parent not None else 0, x.ni, c, x.vi))
                # return selection(max(node.children, key=lambda child: child.value + upper_confidence_bound(node.n, child.n, 2)))
            chosen_node = selection(nodes)

            # 2. Expansion
            # Expand the tree (choose that move) for self
            def expansion(node):
                self.rule.env.step(action)
                nodes += [self.Node(action, self.rule.env.copy().step(action), node) for action in actions] # save new child nodes of selected node
                return restoreEnv
            restoreEnv = expansion(chosen_leaf)

            # TODO Are self.rule.env and self.policy.env the same?
            # TODO How can I make a play for the opponent (in the simulation phase)?

            # 3. Simulation
            # Simulate the game until depth level runs out
            def simulation(node, depth):
                # Create a temporary board for simulation loop
                restoreEnvSimu = deepcopy(self.rule.env)
                cur_depth = depth
                while True:
                    # If the game is over, return the value of the game
                    if self.rule.env.is_done():
                        return self.rule.env.value(self.rule.agent)
                    # If the game is not over, apply the policy to get the next move
                    # and continue the simulation
                    if cur_depth == 0:
                        return self.rule.env.value(self.rule.agent) # TODO return the value of the game, even if not won (EDIT: triple check pls)
                    if node.is_leaf():
                        self.policy.run()
                    else:
                        node = selection(node)
                        cur_depth -= 1
                # Restore pre-simulation environment
                self.rule.env = restoreEnvSimu
                self.policy.env = restoreEnvSimu
            simulation_result = simulation(chosen_leaf, self.depth)

            # 4. Backpropagate value
            # Update the value of the ancestor nodes
            def backpropagation(node, value):
                while node is not None:
                    node.ni += 1
                    node.vi += value
                    node = node.parent
            backpropagation(chosen_node, simulation_result)

        # Restore starting environment
        self.rule.env = restoreEnv
        self.policy.env = restoreEnv
        # Choose the node with highest mean value
        return max(nodes, key=lambda x: x.vi)

class MCTS_LegalRandom(MCTS):
    def __init__(self, env, agent, mask, obs):
        depth = 1
        policy = LegalRandom(env, agent, mask, obs)
        timelimit = 60 # seconds
        super().__init__(env, agent, mask, obs, depth, policy, timelimit)

    def run(self):
        # call the super class run method
        super().run()

# TODO #9 Flawed
class Flawed(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        pass  # Implement the flawed policy here

class LegalRandom(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        return self.rule._env.action_space(self.rule._agent).sample(self.rule._mask)

# TODO #8 Piers 
class Piers(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        pass  # Implement Piers policy here

# TODO #7 IGGI
class IGGI(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        pass  # Implement IGGI policy here

# TODO #5 PredictorIS-MCTS Policy is missing
class PredictorISMCTS:
    pass
