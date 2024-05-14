# Description: This file contains the Policy class which is responsible for generating the policies for the agent.

from pettingzoo.classic import hanabi_v5
from rules import *
from math import log, sqrt
from copy import deepcopy
import time

def copy_env(env):
    new_env = hanabi_v5.env(colors=5, ranks=5, players=2, hand_size=5,
                            max_information_tokens=8, max_life_tokens=3,
                            observation_type='card_knowledge', render_mode = 'human')
    new_env.reset()
    new_env.possible_agents = deepcopy(env.possible_agents)
    new_env.agents = deepcopy(env.agents)
    new_env._cumulative_rewards = deepcopy(env._cumulative_rewards)
    # new_env._agent_selector = deepcopy(env._agent_selector)
    new_env.state = deepcopy(env.state) 
    return new_env

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
            self.vi = 0 # value of this node

        def is_leaf(self):
            return len(self.children) == 0

    def upper_confidence_bound(self, n, ni, c, vi):
        MAX = float('inf')
        return MAX if ni == 0 else vi/ni + c*sqrt(n)/ni

    def run(self):
        # Get all nodes (possible actions from current state)
        mask = self.rule.get_mask() # self.rule._env.action_space(self.rule._agent).n
        # Map a node to each (copy/deepcopy of the state first)
        nodes = [self.Node(action, copy_env(self.rule._env)) for action in range(self.rule._env.action_space(self.rule._agent).n) if mask[action-1]]

        # Create a temporary board for main loop
        restoreEnv = copy_env(self.rule._env)
        self.policy.rule._env = restoreEnv # unnecessary?
        # Repeat this until time runs out
        timeout = time.time() + self.timelimit
        while time.time() < timeout: 
            # 1. Selection
            # Apply UCB to nodes (possible actions) and randomly select one of the ones with highest value
            def _selection(nodes):
                return max(nodes, key=lambda x: self.upper_confidence_bound(
                    (x.parent.ni if x.parent is not None else 0), x.ni, sqrt(2), x.vi))
                # return selection(max(node.children, key=lambda child: child.value + upper_confidence_bound(node.n, child.n, 2)))
            chosen_node = _selection(nodes)

            # 2. Expansion
            # Expand the tree (choose that move) for self
            def _expansion(node, nodes):
                self.policy.rule._env = copy_env(node.state)
                self.policy.rule._env.step(node.action)
                curr_mask = self.policy.rule.get_mask()

                # observation, reward, termination, truncation, info = self.policy.rule._env.last() # ??? TODO
                if node.is_leaf():
                    nodes += [self.Node(action, copy_env(self.policy.rule._env), node) for action in range(self.rule._env.action_space(self.rule._agent).n) if mask[action-1]] # save new child nodes of selected node
            _expansion(chosen_node, nodes)

            # Are self.rule.env and self.policy.env the same? YES, self is a policy too
            # TODO How can I make a play for the opponent (in the simulation phase)?

            # 3. Simulation
            # Simulate the game until depth level runs out or time expires
            def _simulation(node, depth, timeout):
                # Create temporary board for simulation (don't wanna tamper node state)
                cur_depth = depth
                while time.time() < timeout: 
                    for agent in self.policy.rule._env.agent_iter():
                        observation, reward, termination, truncation, info = self.policy.rule._env.last() # ??? TODO
                        # If the game is over, return the value of the game
                        if termination or truncation: # what the fuck is truncation
                            print("Game is over")
                            return self.policy.rule._env._cumulative_rewards[self.policy.rule._agent]
                        # If the game is not over, apply the policy to get the next move
                        # and continue the simulation
                        if cur_depth == 0:
                            print("Depth is 0")
                            # return the value of the agent at the end of the simulation (depth ran out, get rewards)
                            return self.policy.rule._env.value(self.policy.rule._agent)
                        if node.is_leaf():
                            action = self.policy.run()
                            self.policy.rule._env.step(action)
                        else:
                            node = _selection(node)
                            cur_depth -= 1
                # return the value of the agent at the end of the simulation (time ran out, get rewards)
                return self.policy.rule._env.value(self.policy.rule._agent)
            simulation_result = _simulation(chosen_node, self.depth, timeout)
            # Restore starting environment
            self.policy.rule._env = restoreEnv
            print("Finished simulation.")

            # 4. Backpropagate value
            # Update the value of the ancestor nodes
            def _backpropagation(node, value):
                while node is not None:
                    node.ni += 1
                    node.vi += value
                    node = node.parent
            _backpropagation(chosen_node, simulation_result)
            print("Backpropagation is done.")

        # Choose the node with highest mean value
        print("Finished running MCTS. Choosing the best (root) node.")
        best = max(nodes, key=lambda x: x.vi)
        while best.parent is not None:
            best = best.parent
        print("Best (root) node is chosen.")
        return best.action

class MCS_LegalRandom(MCTS):
    def __init__(self, env, agent, mask, obs):
        depth = 1
        timelimit = 60 # seconds
        policy = LegalRandom(env, agent, mask, obs)
        super().__init__(env, agent, mask, obs, depth, policy, timelimit)

    def run(self):
        # call the super class run method
        super().run()

class Flawed(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        # it first tries PlaySafeCard, PlayProbablySafeCard(0.25), TellRandomly, OsawaDiscard, then DiscardOldestFirst, then DiscardRandomly
        if self.rule.play_safe_card() is not None:
            print("I am playing safe card")
            return self.rule.play_safe_card()
        elif self.rule.play_probably_safe_card(0.25) is not None:
            print("I am playing probably safe card with a probability of 0.25")
            return self.rule.play_probably_safe_card(0.25)
        elif self.rule.tell_randomly() is not None:
            print("I am telling randomly")
            return self.rule.tell_randomly()
        elif self.rule.osawa_discard() is not None:
            print("I am osawa discarding")
            return self.rule.osawa_discard()
        elif self.rule.discard_oldest_first() is not None:
            print("I am discarding oldest first")
            return self.rule.discard_oldest_first()
        else:
            print("I am discarding randomly")
            return self.rule.discard_randomly()

class PlayerInput(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        # print the legal action mask of the agent
        print(self.rule._mask)
        print("please go check the documentation to see what it means")
        return int(input("Enter your move: "))

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
        pass

# TODO #7 IGGI
class IGGI(Policy):
    def __init__(self, env, agent, mask, obs):
        super().__init__(env, agent, mask, obs)

    def run(self):
        # it first tries PlayIfCertain, then PlaySafeCard, then TellAnyoneAboutUsefulCard, then OsawaDiscard, then DiscardOldestFirst
        if self.rule.play_if_certain() is not None:
            print("I am playing if certain")
            return self.rule.play_if_certain()
        elif self.rule.play_safe_card() is not None:
            print("I am playing safe card")
            return self.rule.play_safe_card()
        elif self.rule.tell_anyone_about_useful_card() is not None:
            print("I am telling anyone about useful card")
            return self.rule.tell_anyone_about_useful_card()
        elif self.rule.osawa_discard() is not None:
            print("I am osawa discarding")
            return self.rule.osawa_discard()
        else:
            print("I am discarding oldest first")
            return self.rule.discard_oldest_first()
       

# TODO #5 PredictorIS-MCTS Policy is missing
class PredictorISMCTS:
    pass
