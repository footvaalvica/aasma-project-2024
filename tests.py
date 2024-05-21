from random import randint
import sys, inspect
from policies import *

# Generate x amount of seeds for each configuration
HARDSEEDS = [13, 87, 95, 10, 42]
seeds = []

if len(sys.argv) > 1:
    len = int(sys.argv[1])
    new_seeds = []
    for i in range(len):
        seeds.append(randint(0, 1000))
else:
    seeds = HARDSEEDS

# Get all policies under "policies" module
def find_subclasses(module, clazz, blacklist=[]):
    return [
        cls
            for name, cls in inspect.getmembers(module)
                if inspect.isclass(cls) and name not in blacklist
                and issubclass(cls, clazz)
    ]
    
blacklist = ['MCTS', 'PlayerInput', 'Policy'] # Policies NOT to run!!
policy_classes = find_subclasses(sys.modules['policies'], Policy, blacklist)

# Get each pair combination of agents (policies)
for i in range(len(policy_classes)):
    for j in range(i+1, len(policy_classes)):
        for seed in seeds:
            print(f"python hanabi.py {policy_classes[i].__name__} {policy_classes[j].__name__} {seed}")

# Run each pair combination of agents with the same configurations

