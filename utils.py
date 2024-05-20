from pettingzoo.classic import hanabi_v5
from pettingzoo.utils import wrappers

class EnvWrapper(hanabi_v5.raw_env):
    def __init__(self, **kwargs):
        self.action_history = []
        self.seed = None
        super().__init__(**kwargs)
    
    def reset(self, seed=None, options=None):
        self.action_history = []
        self.seed = seed
        return super().reset(seed, options)

    def step(self, action):
        # self.action_history.append(action) # for performance sake,
        # update action history manually where needed
        return super().step(action)


#################### HELPER FUNCTIONS ############################

def update_card_age(card_age, action: int):
    # increment all elements by 1
    card_age = [x + 1 for x in card_age]

    if action < 5:
        # it's a discard action
        # they map from 0 to 4 to the cards from left to right
        card_age[action] = 0
    elif 5 < action < 10:
        # it's a play action
        # they map from 5 to 9 to the cards from left to right
        card_age[action - 5] = 0
    else:
        # we can ignore tell actions
        pass

    return card_age