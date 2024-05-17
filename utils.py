from pettingzoo.classic import hanabi_v5
from pettingzoo.utils import wrappers

class EnvWrapper(hanabi_v5.raw_env):
    def __init__(self, action_history=[], **kwargs):
        self.action_history = action_history
        super().__init__(**kwargs)

def make_env(action_history=[], **kwargs):
    render_mode = kwargs.get("render_mode")
    if render_mode == "ansi":
        kwargs["render_mode"] = "human"
        env = EnvWrapper(**kwargs)
        env = wrappers.CaptureStdoutWrapper(env)
    else:
        env = EnvWrapper(**kwargs)

    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env
