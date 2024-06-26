from random import randint
import sys, inspect
from policies import *
import csv
import os
import sys
import multiprocessing

# delete the results file if it exists
try:
    os.remove("results.csv")
except:
    pass

# write the first line of the csv that will contain the headers
with open('results.csv', mode='w') as results_file:
    results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    results_writer.writerow(["Policy 1", "Policy 2", "Score", "Errors Policy 1", "Errors Policy 2", "Number of actions taken", "Remaining information tokens"])

# If you want to replay a match, you can copy the action history from the console and paste it here
history = []

# Policies' whitelist and blacklist 
whitelist = []
blacklist = ['MCTS', 'PlayerInput', 'Policy'] # Policies NOT to run!!

HARDSEEDS = [13, 87, 95, 10, 42]
seeds = []

# Generate x amount of seeds like so, python tests.py 10 -> generates 10 seeds
if len(sys.argv) > 1:
    length_in = int(sys.argv[1])
    new_seeds = []
    for i in range(length_in):
        seeds.append(randint(0, 1000))
else: # otherwise use hardcoded seeds
    seeds = HARDSEEDS

# Get all policies under "policies" module
def find_subclasses(module, clazz, blacklist=[]):
    return [
        cls
            for name, cls in inspect.getmembers(module)
                if inspect.isclass(cls) and name not in blacklist
                and issubclass(cls, clazz)
    ]
policy_classes = find_subclasses(sys.modules['policies'], Policy, blacklist)

# Function to run a match between two policies given a seed
def run_match(policy1, policy2, seed):
    print(f"Running match between {policy1.__name__} and {policy2.__name__} with seed {seed}")

    # Run the game
    env = EnvWrapper(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode='human')
    env.reset(seed=seed)
    env.render()
    cards_age = {}
    for i in range(env.num_agents):
        cards_age_key = f"player_{i}"
        cards_age[cards_age_key] = [0, 0, 0, 0, 0]
    
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        card_age = cards_age[agent]
        if termination or truncation:
            action = None
            if agent == "player_0":
                print("Game over")
                print_random_ascii_art()
                print("The action history is:")
                print(env.action_history)
                # write the score to another row in the csv file
                # # policy.update(env,agent,mask,obs,card_age)
                with open('results.csv', mode='a') as results_file:
                    results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    results_writer.writerow([policy1.__name__, policy2.__name__,policy.calculate_score(), env.errors["player_0"], env.errors["player_1"], len(env.action_history), int(policy.get_information_tokens())])
        else:
            mask = observation["action_mask"]
            obs = observation["observation"]
            if agent == "player_0":
                policy = policy1(env, agent, mask, obs, card_age) 
                # get policy name and print it
                print(f"Policy {policy1.__name__} is playing against {policy2.__name__}")
            else:
                policy = policy2(env, agent, mask, obs, card_age)
                print(f"Policy {policy2.__name__} is playing against {policy1.__name__}")
            action = policy.run()
            print(f"Agent {agent} chose action {action}")
            env.action_history.append(action)
            cards_age[agent] = update_card_age(card_age, action)

            if agent == "player_0":
                player_cards = env.observe("player_1")["observation"][0:125]
            else:
                player_cards = env.observe("player_0")["observation"][0:125]
            fireworks = obs[167:192]
            env.errors[agent] += update_errors(player_cards, fireworks, action)

            # print the hanabi score
            print(f"Hanabi score: {policy.calculate_score()}")

        env.step(action)

# Function to replay a match given an action history
def replay_match(action_history, seed=42):
    env = EnvWrapper(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8, max_life_tokens=3, observation_type='card_knowledge', render_mode='human')
    env.reset(seed=seed)
    env.render()
    cards_age = {}
    for i in range(env.num_agents):
        cards_age_key = f"player_{i}"
        cards_age[cards_age_key] = [0, 0, 0, 0, 0]

    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        card_age = cards_age[agent]
        if termination or truncation:
            action = None
            print("Game over")
        else:
            mask = observation["action_mask"]
            obs = observation["observation"]

            action = action_history.pop(0)
            print(f"Agent {agent} chose action {action}")
            env.action_history.append(action)
            cards_age[agent] = update_card_age(card_age, action)

            if agent == "player_0":
                player_cards = env.observe("player_1")["observation"][0:125]
            else:
                player_cards = env.observe("player_0")["observation"][0:125]
            fireworks = obs[167:192]
            env.errors[agent] += update_errors(player_cards, fireworks, action)

        env.step(action)

# replay_match(history, seed=12)

def run_match_wrapper(args):
    policy1, policy2, seed = args
    run_match(policy1, policy2, seed)

if __name__ == '__main__':
    pool = multiprocessing.Pool()
    pool.map(run_match_wrapper, [(policy1, policy2, seed) for policy1 in policy_classes for policy2 in policy_classes for seed in seeds])
    pool.close()
    pool.join()
        # # run_match(policy1, policy2, seeds[0])
