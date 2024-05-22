# Description: This file contains the Policy class which is responsible for generating the policies for the agent.

# from pettingzoo.utils import wrappers, agent_selector
from utils import *
from rules import *
from math import sqrt
from copy import deepcopy, copy
import time

def copy_env(env):
    hist = env.action_history
    new_env = EnvWrapper(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode=None)
    new_env.reset(env.seed)
    actionCount = 0
    for agent in new_env.agent_iter():
        new_env.step(hist[actionCount])
        actionCount += 1
        if actionCount >= len(hist):
            break
    new_env.action_history = copy(hist)
    return new_env

class Policy:
    def __init__(self, env, agent, mask, obs, card_age):
        self.rule = Rule(env, agent, mask, obs, card_age)
    
    def update(self, env, agent, mask, obs, card_age): # no env
        self.rule.card_age = card_age
        self.rule._update_all(env, agent, mask, obs)

    # calculate the score based on the firework info
    def calculate_score(self):
        score = 1+
        for firework in self.rule._obs_firework_info:
            score += sum(firework)
        return score

class MCTS(Policy):
    def __init__(self, env, agent, mask, obs, card_age, depth, policy, timelimit):
        super().__init__(env, agent, mask, obs, card_age)
        self.depth = depth
        self.policy = policy
        self.timelimit = timelimit
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
        restoreCardAge = deepcopy(self.rule.card_age)

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
                self.policy.rule._env = copy_env(node.state)
                self.policy.rule._env.step(node.action)
                self.policy.rule._env.action_history.append(node.action)
                # --------------------------------------------
                observation, reward, termination, truncation, info = self.policy.rule._env.last()
                mask = observation["action_mask"]
                obs = observation["observation"]
                newCard_age = update_card_age(self.policy.rule.card_age, node.action)
                self.policy.update(self.policy.rule._env, self.policy.rule._env.agent_selection, mask, obs, newCard_age) # keep env
                
                # If leaf node, create children nodes that can later be selected from (explored)
                if node.is_leaf():
                    node.children = [self.Node(action, self.policy.rule._env, node) for action in range(self.policy.rule._env.action_space(self.policy.rule._env.agent_selection).n) if mask[action]]
                    self.policy.rule._env = copy_env(self.policy.rule._env) # Don't mess with children states during simulation
                
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
                            newCard_age = update_card_age(self.policy.rule.card_age, node.action)
                            self.policy.update(self.policy.rule._env, agent, mask, obs, newCard_age) # keep the environment

                            action = self.policy.run()
                            self.policy.rule._env.step(action)
                            # Don't need to alter action history as this wont ever be copied
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

            # Restore starting environment
            self.policy.update(restoreEnv, restoreAgent, restoreMask, restoreObs, restoreCardAge)

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
    def __init__(self, env, agent, mask, obs, card_age):
        depth = 1
        timelimit = 1 # seconds
        policy = LegalRandom(env, agent, mask, obs, card_age)
        super().__init__(env, agent, mask, obs, card_age, depth, policy, timelimit)

    def run(self):
        # call the super class run method
        return super().run()

class Flawed(Policy):
    def __init__(self, env, agent, mask, obs, card_age):
        super().__init__(env, agent, mask, obs, card_age)

    def run(self):
        # it first tries PlaySafeCard, PlayProbablySafeCard(0.25), TellRandomly, OsawaDiscard, then DiscardOldestFirst, then DiscardRandomly
        if self.rule.play_safe_card() is not None:
            print("I am playing safe card")
            return self.rule.play_safe_card()
        elif self.rule.play_probably_safe_card(0.25) is not None:
            print("I am playing probably safe card with a probability of 0.25")
            return self.rule.play_probably_safe_card(0.25)
        elif self.rule.tell_random() is not None:
            print("I am telling randomly")
            return self.rule.tell_random()
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
    def __init__(self, env, agent, mask, obs, card_age):
        super().__init__(env, agent, mask, obs, card_age)

    def run(self):
        # print the legal action mask of the agent
        print(self.rule._mask)
        print("please go check the documentation to see what it means")
        return int(input("Enter your move: "))

class LegalRandom(Policy):
    def __init__(self, env, agent, mask, obs, card_age):
        super().__init__(env, agent, mask, obs, card_age)

    def run(self):
        return self.rule._env.action_space(self.rule._agent).sample(self.rule._mask)

# TODO #8 Piers 
class Piers(Policy):
    def __init__(self, env, agent, mask, obs, card_age):
        super().__init__(env, agent, mask, obs, card_age)

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
    def __init__(self, env, agent, mask, obs, card_age):
        super().__init__(env, agent, mask, obs, card_age)

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
        elif self.rule.discard_oldest_first() is not None:
            print("I am discarding oldest first")
            return self.rule.discard_oldest_first()
        else:
            # tells randomly
            print("I am telling randomly")
            return self.rule.tell_random()
        
       
# TODO more
