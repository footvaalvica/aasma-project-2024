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
