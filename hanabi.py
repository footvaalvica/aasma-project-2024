# import policies.py
from policies import *
from utils import *
from random import randint
import sys, inspect

# If you want to replay a match, you can copy the action history from the console and paste it here
history = []

# Policies' whitelist and blacklist 
whitelist = []
blacklist = ['MCTS', 'Policy'] # Policies NOT to run!!

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


# replay_match(history, seed=12)

if __name__ == '__main__':
    print("Welcome to the Hanabi game!")
    print("Available policies:")
    for policy_class in policy_classes:
        print(f"- {policy_class.__name__}")
    print("")
    print("Enter the name of the first policy:")
    policy1_name = input()
    print("Enter the name of the second policy:")
    policy2_name = input()
    print("Enter the number of matches:")
    num_matches = int(input())
    seed = int(randint(0, 100000))
    policy1 = None
    policy2 = None
    for policy_class in policy_classes:
        if policy_class.__name__ == policy1_name:
            policy1 = policy_class
        if policy_class.__name__ == policy2_name:
            policy2 = policy_class
    if policy1 is None or policy2 is None:
        print("Invalid policy name")
        exit(1)
    print(f"Running {num_matches} matches between {policy1.__name__} and {policy2.__name__} with seed {seed}")
    for _ in range(num_matches):
        run_match(policy1, policy2, seed)
    print("Done!")