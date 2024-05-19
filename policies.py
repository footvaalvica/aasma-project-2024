# Description: This file contains the Policy class which is responsible for generating the policies for the agent.

# from pettingzoo.utils import wrappers, agent_selector
from utils import *
from pettingzoo.classic import hanabi_v5
from rules import *
from math import sqrt
from copy import deepcopy, copy
import time

def copy_env(seed, env):
    # print("     Copying environment")
    hist = env.action_history
    new_env = make_env(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode=None, action_history=copy(hist))
    new_env.reset(seed)
    actionCount = 0
    for agent in new_env.agent_iter():
        new_env.step(hist[actionCount])
        actionCount += 1
        if actionCount >= len(hist):
            break
    return new_env

class Policy:
    def __init__(self, env, agent, mask, obs):
        self.rule = Rule(env, agent, mask, obs)
    
    def update(self, env, agent, mask, obs): # no env
        self.rule._update_all(env, agent, mask, obs)

class MCTS(Policy):
    def __init__(self, env, agent, mask, obs, depth, policy, timelimit, seed):
        super().__init__(env, agent, mask, obs)
        self.depth = depth
        self.policy = policy
        self.timelimit = timelimit
        self.seed = seed
        self.MAX_SIMULATIONS = 600
    
    class Node:
        def __init__(self, action, state, parent=None):
            self.action = action
            self.state = state
            self.parent = parent
            self.children = []
            self.ni = 0 # number of simulations done for this node
            self.vi = 0 # value of this node

        def is_leaf(self):
            return len(self.children) == 0 or self.ni == 0 # the (or self.ni == 0) is only needed because i add the children immediately after expanding the node

    def upper_confidence_bound(self, n, ni, c, vi):
        MAX = float('inf')
        return MAX if ni == 0 else vi/ni + c*sqrt(n)/ni

    def run(self):
        print("Running MCTS for a maximum of", self.timelimit, "seconds,", self.MAX_SIMULATIONS, "simulations and depth", self.depth, ".")
        # Create a root node
        rootNode = self.Node(None, self.rule._env)
        # Get all children nodes (possible actions from current state)
        mask = self.rule.get_mask() # self.rule._env.action_space(self.rule._agent).n
        # Map a node to each (copy/deepcopy of the state first)
        rootNode.children = [self.Node(action, self.rule._env, rootNode) for action in range(self.rule._env.action_space(self.rule._agent).n) if mask[action]]

        # Create a temporary board for main loop
        observation, _, _, _, _ = self.policy.rule._env.last()
        restoreEnv = self.rule._env
        restoreMask = deepcopy(self.rule.get_mask())
        restoreAgent = deepcopy(self.rule._agent)
        restoreObs = deepcopy(observation["observation"])

        # Repeat this until time runs out
        timeout = time.time() + self.timelimit
        while time.time() < timeout: 
            # 1. Selection
            # Apply UCB to nodes (possible actions) and randomly select one of the ones with highest value
            # print("Do selection")
            def _selection(node):
                choice = max(node.children, key=lambda x: self.upper_confidence_bound(
                    (x.parent.ni if x.parent is not None else 0), x.ni, sqrt(2), x.vi))
                if choice.is_leaf():
                    return choice
                return _selection(choice)
            chosen_node = _selection(rootNode)

            # 2. Expansion
            # Expand the tree (choose that move) for self
            # print("Do expansion")
            def _expansion(node):
                # Set the environment to the state of the node
                # print("     Expanding for action", node.action, " with history of length", len(node.state.action_history), " for agent", node.state.agent_selection)
                self.policy.rule._env = copy_env(self.seed, node.state)
                self.policy.rule._env.step(node.action)
                self.policy.rule._env.action_history.append(node.action)
                # --------------------------------------------
                observation, reward, termination, truncation, info = self.policy.rule._env.last()
                mask = observation["action_mask"]
                obs = observation["observation"]
                self.policy.update(self.policy.rule._env, self.policy.rule._env.agent_selection, mask, obs) # keep env
                
                # If leaf node, create children nodes that can later be selected from (explored)
                if node.is_leaf():
                    node.children = [self.Node(action, self.policy.rule._env, node) for action in range(self.policy.rule._env.action_space(self.policy.rule._env.agent_selection).n) if mask[action]]
                
                # DEBUG check if any children will commit illegal action
                # print("CHECK CHILDREN")
                #for node in node.children:
                #    # check if any children will commit illegal action
                #    state = copy_env(self.seed, node.state)
                #    observa, reward, termination, truncation, info = state.last()
                #    mask = observa["action_mask"]
                #    if mask[node.action] == 0:
                #        print("Illegal action detected, child with action", node.action, "on mask", mask, "for agent", state.agent_selection)
                #        print("action history of this child", state.action_history)
                #        exit(0)
            _expansion(chosen_node)
            # print("Finish Expansion")

            # 3. Simulation
            # Simulate the game until depth level runs out or time expires
            # print("Do simulation")
            def _simulation(node, depth, timeout):
                cur_depth = depth
                while time.time() < timeout: 
                    for agent in self.policy.rule._env.agent_iter():
                        observation, reward, termination, truncation, info = self.policy.rule._env.last()
                        # If the game is over, return the value of the game
                        if termination or truncation: # what the fuck is truncation
                            # print("Game is over")
                            return self.policy.rule._env._cumulative_rewards[restoreAgent]
                        # If the game is not over, apply the policy to get the next move
                        # and continue the simulation
                        elif node.is_leaf():
                            mask = observation["action_mask"]
                            obs = observation["observation"]
                            self.policy.update(self.policy.rule._env, agent, mask, obs) # keep the environment

                            action = self.policy.run()
                            self.policy.rule._env.step(action)
                            cur_depth -= 1
                        else:
                            # print("Unexpected non-leaf node during simulation, \
                            #      investigate situation")
                            cur_depth -= 1
                            exit(0)
                        if cur_depth == 0:
                            # print("Depth is 0")
                            # return the value of the agent at the end of the simulation (depth ran out, get rewards)
                            return self.policy.rule._env._cumulative_rewards[restoreAgent]
                # if time.time() >= timeout:
                    # print("Time is up")
                # return the value of the agent at the end of the simulation (time ran out, get rewards)
                return self.policy.rule._env._cumulative_rewards[restoreAgent]
            simulation_result = _simulation(chosen_node, self.depth, timeout)
            # Restore starting environment
            self.policy.rule._env = restoreEnv
            # print("Finished simulation.", simulation_result)

            # 4. Backpropagate value
            # Update the value of the ancestor nodes
            # print("Backpropagation")
            def _backpropagation(node, value):
                while node is not None:
                    node.ni += 1
                    node.vi += value
                    node = node.parent
            _backpropagation(chosen_node, simulation_result)
            # print("Backpropagation is done.")
            self.policy.update(restoreEnv, restoreAgent, restoreMask, restoreObs)
            # Prematurely end the loop if n total simulations have been done
            if rootNode.ni >= self.MAX_SIMULATIONS:
                # print("Reached the arbitrary maximum number of simulations")
                break

        # Choose the node with highest mean value
        best = max(rootNode.children, key=lambda x: x.vi)
        print("Finished running MCTS. Result action is", best.action, "with value",
                best.vi, "and", best.ni, "simulations out of", rootNode.ni, "total.")
        return best.action

class MCS_LegalRandom(MCTS):
    def __init__(self, env, agent, mask, obs, seed):
        depth = 1
        timelimit = 1 # seconds
        policy = LegalRandom(env, agent, mask, obs)
        super().__init__(env, agent, mask, obs, depth, policy, timelimit, seed)

    def run(self):
        # call the super class run method
        return super().run()

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
        if sum(self.rule._obs_remaining_life_tokens) > 1 and sum(self.rule._obs_unary_remaining_deck)\
        and self.rule.play_probably_safe_card(0.0) is not None:
            print("I am playing probabuly safe card (0.0)")
            return self.rule.play_probably_safe_card(0.0)
        elif self.rule.play_safe_card() is not None:
            print("I am playing safe card")
            return self.rule.play_safe_card()
        elif sum(self.rule._obs_remaining_life_tokens) > 1 and self.rule.play_probably_safe_card(0.6) is not None:
            print("I am playing probabuly safe card (0.6)")
            return self.rule.play_probably_safe_card(0.6)
        elif self.rule.tell_anyone_about_useful_card() is not None:
            print("I am telling anyone about useful card")
            return self.rule.tell_anyone_about_useful_card()
        elif sum(self.rule._obs_remaining_info_tokens) < 4  and self.rule.tell_dispensable() is not None:
            print("I am telling next player about dispensable card")
            return self.rule.tell_dispensable()
        elif self.rule.osawa_discard() is not None:
            print("I am osawa discarding")
            return self.rule.osawa_discard()
        elif self.rule.discard_oldest_first() is not None:
            print("I am discarding older first")
            return self.rule.discard_oldest_first()
        elif self.rule.tell_random() is not None:
            print("I am telling randomly")
            return self.rule.tell_random()
        else:
            print("I am discarding randomly")
            return self.rule.discard_random()

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
    
